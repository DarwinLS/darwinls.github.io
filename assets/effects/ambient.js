/* ============================================================
   Ambient + choreography controller (JS half).

   Progressive enhancement: this module only ADDS motion. Without it
   the site is fully styled and readable (scenery is static inline
   SVG, content is never hidden by CSS unless this script runs).

   It reads the intensity dial ([data-intensity] on <html>, set by the
   no-FOUC inline script) and mounts effects to match:
     calm       -> no rain, no cursor light, no reveals-hide
                   (atmosphere = static in-scene mist + .fx-haze)
     balanced   -> WebGL rain (2 layers), reveals, timeline draw
     immersive  -> WebGL rain (3 layers + splashes), cursor dew
   Rain is WebGL-first on every capable device; a frame-time watchdog
   demotes to a batched 2D canvas at half density if the page cannot
   hold ~45fps, and remembers that for the session. save-data and
   low-memory devices get no rain at all.
   ============================================================ */

const root = document.documentElement;
const reduce = matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = matchMedia("(pointer: fine)");

const level = () => root.dataset.intensity || "balanced";
const motionOK = () => !reduce.matches;

const GL_BLOCKED_KEY = "fx-gl-blocked";

/* ---------- shared engine lifecycle ---------- */
let teardown = [];
let gen = 0;                          // bumped each boot; guards async mounts
function destroyAll() {
    teardown.forEach((fn) => { try { fn(); } catch (e) {} });
    teardown = [];
}
function hasWebGL2() {
    try { return !!document.createElement("canvas").getContext("webgl2"); }
    catch (e) { return false; }
}
function glBlocked() {
    try { return sessionStorage.getItem(GL_BLOCKED_KEY) === "1"; }
    catch (e) { return false; }
}
function blockGL() {
    try { sessionStorage.setItem(GL_BLOCKED_KEY, "1"); } catch (e) {}
}

/* ============================================================
   RAIN - WebGL2 shader first (rain-gl.js), batched 2D fallback.
   ============================================================ */

/* null = no rain at all (calm, reduced motion, save-data, low-end) */
function rainLevel() {
    const lvl = level();
    if (lvl === "calm" || !motionOK()) return null;
    const conn = navigator.connection;
    if (conn && conn.saveData) return null;
    if (navigator.deviceMemory && navigator.deviceMemory <= 2) return null;
    return lvl;
}

async function mountRain() {
    const lvl = rainLevel();
    if (!lvl) return;
    const myGen = gen;
    const coarse = !finePointer.matches;

    if (!glBlocked() && hasWebGL2()) {
        try {
            const mod = await import("./rain-gl.js");
            if (myGen !== gen) return;                       // superseded during import
            const inst = mod.createRainGL(document.body, { level: lvl, coarse });
            if (inst && inst.ok) {
                if (myGen !== gen) { inst.destroy(); return; }
                teardown.push(inst.destroy);
                watchdog(inst, lvl, coarse, myGen);
                return;
            }
        } catch (e) { /* fall through to 2D */ }
    }
    mount2DRain(lvl, coarse, glBlocked() ? 0.5 : 1);
}

/* Frame-time watchdog: sample ~90 frames after the GL mount; if the
   trimmed mean exceeds 22ms the device cannot hold the shader, so
   demote to the 2D canvas at half density for the rest of the session. */
function watchdog(inst, lvl, coarse, myGen) {
    const samples = [];
    let n = 0, last = performance.now(), raf = 0;
    function tick(t) {
        if (myGen !== gen) return;
        const d = t - last; last = t;
        if (d > 0 && d < 500) samples.push(d);
        if (++n < 90) { raf = requestAnimationFrame(tick); return; }
        samples.sort((a, b) => a - b);
        const trimmed = samples.slice(4, -4);
        const avg = trimmed.reduce((s, v) => s + v, 0) / (trimmed.length || 1);
        if (avg > 22) {
            blockGL();
            try { inst.destroy(); } catch (e) {}
            mount2DRain(lvl, coarse, 0.5);
        }
    }
    raf = requestAnimationFrame(tick);
    teardown.push(() => cancelAnimationFrame(raf));
}

/* Batched 2D fallback: three depth buckets, ONE path + ONE stroke per
   bucket per frame (no per-drop style strings or beginPath churn). */
function mount2DRain(lvl, coarse, densityMul) {
    const canvas = document.createElement("canvas");
    canvas.className = "fx-rain is-fixed";
    canvas.setAttribute("aria-hidden", "true");
    document.body.appendChild(canvas);

    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) { canvas.remove(); return; }

    const dprCap = coarse ? 1.25 : 1.5;
    let W = 0, H = 0;
    const wind = lvl === "immersive" ? 1.1 : 0.6;
    const speedMul = lvl === "immersive" ? 1.2 : 1;

    /* depth buckets: [alpha, lineWidth, speed, length] far -> near */
    const BUCKETS = [
        { a: 0.14, w: 0.8, v: 2.6, len: 9 },
        { a: 0.24, w: 1.1, v: 4.2, len: 14 },
        { a: 0.38, w: 1.5, v: 6.0, len: 20 },
    ];
    let colors = [];
    function readColors() {
        const rgb = (getComputedStyle(root).getPropertyValue("--rain-color").trim() || "120 135 150")
            .replace(/\s+/g, ",");
        colors = BUCKETS.map((b) => `rgba(${rgb},${b.a})`);
    }
    readColors();

    let drops = [[], [], []];
    function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, dprCap);
        W = window.innerWidth; H = window.innerHeight;
        canvas.width = Math.round(W * dpr);
        canvas.height = Math.round(H * dpr);
        canvas.style.width = W + "px";
        canvas.style.height = H + "px";
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const base = (lvl === "immersive" ? 1.5 : 0.8) * (coarse ? 0.5 : 1) * densityMul;
        const total = Math.round((W * H / 10000) * base);
        drops = BUCKETS.map((b, i) => {
            const share = [0.45, 0.33, 0.22][i];
            return Array.from({ length: Math.max(1, Math.round(total * share)) }, () => ({
                x: Math.random() * (W + 120) - 60,
                y: Math.random() * H,
            }));
        });
    }

    let raf = 0, last = 0, running = false;
    function frame(t) {
        if (!running) return;
        const dt = Math.min(2.5, (t - last) / 16.67 || 1);
        last = t;
        ctx.clearRect(0, 0, W, H);
        ctx.lineCap = "round";
        for (let i = 0; i < BUCKETS.length; i++) {
            const b = BUCKETS[i];
            const v = b.v * speedMul;
            ctx.strokeStyle = colors[i];
            ctx.lineWidth = b.w;
            ctx.beginPath();
            for (const d of drops[i]) {
                d.y += v * dt;
                d.x += wind * (v / 6) * dt;
                if (d.y - b.len > H) { d.y = -b.len; d.x = Math.random() * (W + 120) - 60; }
                ctx.moveTo(d.x, d.y);
                ctx.lineTo(d.x - wind * 2.2, d.y - b.len);
            }
            ctx.stroke();
        }
        raf = requestAnimationFrame(frame);
    }
    function start() { if (!running) { running = true; last = performance.now(); raf = requestAnimationFrame(frame); } }
    function stop() { running = false; cancelAnimationFrame(raf); }

    const onVis = () => { document.hidden ? stop() : start(); };
    document.addEventListener("visibilitychange", onVis);
    const onResize = () => resize();
    window.addEventListener("resize", onResize, { passive: true });
    const themeObs = new MutationObserver(readColors);
    themeObs.observe(root, { attributes: true, attributeFilter: ["data-theme"] });

    resize();
    start();

    teardown.push(() => {
        stop();
        themeObs.disconnect();
        document.removeEventListener("visibilitychange", onVis);
        window.removeEventListener("resize", onResize);
        canvas.remove();
    });
}

/* ============================================================
   CURSOR DEW - immersive + fine pointer only. A soft light that
   follows the pointer (plain alpha radial, no blend mode).
   ============================================================ */
function mountCursor() {
    if (level() !== "immersive" || !finePointer.matches || !motionOK()) return;
    const dew = document.createElement("div");
    dew.className = "fx-dew";
    dew.setAttribute("aria-hidden", "true");
    document.body.appendChild(dew);
    let tx = innerWidth / 2, ty = innerHeight / 2, x = tx, y = ty, raf = 0;
    const move = (e) => { tx = e.clientX; ty = e.clientY; };
    function loop() {
        x += (tx - x) * 0.12; y += (ty - y) * 0.12;
        dew.style.transform = `translate3d(${x}px,${y}px,0) translate(-50%,-50%)`;
        raf = requestAnimationFrame(loop);
    }
    window.addEventListener("pointermove", move, { passive: true });
    raf = requestAnimationFrame(loop);
    teardown.push(() => { cancelAnimationFrame(raf); window.removeEventListener("pointermove", move); dew.remove(); });
}

/* ============================================================
   REVEALS / STAGGER / COUNT-UP / TIMELINE DRAW.
   Auto-tags a curated set of elements so no per-page HTML edits
   are needed. Nothing is hidden unless motion is allowed.
   ============================================================ */
const REVEAL = [
    ".what .section-inner > *", ".featured-inner", ".work-peek .peek-head",
    ".peek-card", ".about-teaser .teaser-inner > *", ".pull-quote",
    ".section-block > .block-heading", ".tl-node", ".skill-group",
    ".cs-section", ".cs-demo", ".project-card", ".foliage-divider",
    ".contact-layout > *",
];
const STAGGER = [".pillars", ".tech-stack", ".feature-points", ".peek-grid"];

function mountReveals() {
    if (!motionOK() || level() === "calm" || !("IntersectionObserver" in window)) return;
    root.classList.add("fx-ready");

    const els = new Set();
    REVEAL.forEach((s) => document.querySelectorAll(s).forEach((el) => els.add(el)));
    STAGGER.forEach((s) => document.querySelectorAll(s).forEach((c) => {
        els.delete(c);                         // stagger the children, not the block
        [...c.children].forEach((ch, i) => {
            ch.style.setProperty("--i", i);
            ch.classList.add("fx-staggered");
            els.add(ch);
        });
    }));

    const vh = window.innerHeight;
    const io = new IntersectionObserver((entries, obs) => {
        entries.forEach((e) => {
            if (!e.isIntersecting) return;
            const el = e.target;
            el.classList.remove("fx-hidden");
            el.classList.add("fx-in");
            if (el.classList.contains("tl-node")) el.style.setProperty("--draw", "1");
            countUp(el);
            obs.unobserve(el);
        });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });

    els.forEach((el) => {
        el.classList.add("reveal");
        const top = el.getBoundingClientRect().top;
        if (top > vh * 0.92) el.classList.add("fx-hidden");   // only hide below-the-fold (no flash)
        io.observe(el);
    });

    // Failsafe: never leave anything hidden.
    const failsafe = setTimeout(() => {
        document.querySelectorAll(".reveal.fx-hidden").forEach((el) => {
            el.classList.remove("fx-hidden"); el.classList.add("fx-in");
        });
    }, 3000);

    teardown.push(() => { io.disconnect(); clearTimeout(failsafe); root.classList.remove("fx-ready"); });
}

function countUp(scope) {
    scope.querySelectorAll("[data-count]").forEach((el) => {
        if (el.dataset.counted) return;
        el.dataset.counted = "1";
        const to = parseFloat(el.dataset.count);
        const suffix = el.dataset.countSuffix || "";
        const prefix = el.dataset.countPrefix || "";
        if (!motionOK() || level() === "calm") { el.textContent = prefix + to + suffix; return; }
        const dur = 1100, t0 = performance.now();
        (function tick(t) {
            const p = Math.min(1, (t - t0) / dur);
            const eased = 1 - Math.pow(1 - p, 3);
            el.textContent = prefix + Math.round(to * eased) + suffix;
            if (p < 1) requestAnimationFrame(tick);
        })(t0);
    });
}

/* ============================================================
   BOOT + re-mount on intensity change
   ============================================================ */
function boot() {
    gen++;
    destroyAll();
    mountRain().catch(() => {});
    try { mountCursor(); } catch (e) {}
    try { mountReveals(); } catch (e) {}
}

boot();

// Re-mount when the intensity dial changes (nav toggle / device re-clamp).
let remountTimer = 0;
new MutationObserver(() => {
    clearTimeout(remountTimer);
    remountTimer = setTimeout(boot, 60);
}).observe(root, { attributes: true, attributeFilter: ["data-intensity"] });

// Re-evaluate rain/cursor/reveal gating if the OS reduced-motion pref flips.
reduce.addEventListener?.("change", boot);
