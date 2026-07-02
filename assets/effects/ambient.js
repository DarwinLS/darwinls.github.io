/* ============================================================
   Ambient + choreography controller (Phase 4-5, JS half).

   Progressive enhancement: this module only ADDS motion. Without it
   the site is fully styled and readable (content is never hidden by
   CSS unless this script is present and motion is allowed).

   It reads the intensity dial ([data-intensity] on <html>, set by the
   no-FOUC inline script) and mounts effects to match:
     calm       -> static rain frame, no drift, no reveals-hide
     balanced   -> gentle rain, fog drift (CSS), reveals, timeline draw
     immersive  -> denser rain, cursor dew, everything on
   Effects pause when the tab is hidden or the canvas is offscreen,
   cap DPR, use rAF delta timing, and animate only transform/opacity.
   ============================================================ */

const root = document.documentElement;
const reduce = matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = matchMedia("(pointer: fine)");

const level = () => root.dataset.intensity || "balanced";
const motionOK = () => !reduce.matches;

/* ---------- shared, throttled visibility of the whole engine ---------- */
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

/* ============================================================
   RAIN — pooled 2D canvas, depth layers, wind, DPR-capped.
   Mounts into .hero-scene on the home page (above the ridgelines,
   below the text) or as a fixed layer behind content elsewhere.
   ============================================================ */
async function mountRain() {
    const lvl = level();
    const scene = document.querySelector(".hero-scene");
    const host = scene || document.body;
    const myGen = gen;

    // Immersive + desktop: try the WebGL volumetric upgrade; canvas otherwise.
    if (lvl === "immersive" && finePointer.matches && motionOK() && hasWebGL2()) {
        try {
            const mod = await import("./rain-gl.js");
            if (myGen !== gen) return;                       // superseded during import
            const inst = mod.createRainGL(host, { scene: !!scene });
            if (inst && inst.ok) {
                if (myGen !== gen) { inst.destroy(); return; }
                teardown.push(inst.destroy);
                return;
            }
        } catch (e) { /* fall through to 2D canvas */ }
    }

    const canvas = document.createElement("canvas");
    canvas.className = "fx-rain" + (scene ? "" : " is-fixed");
    canvas.setAttribute("aria-hidden", "true");
    host.appendChild(canvas);

    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) { canvas.remove(); return; }

    const coarse = !finePointer.matches;
    const dprCap = coarse ? 1.5 : 2;
    let dpr = Math.min(window.devicePixelRatio || 1, dprCap);
    let W = 0, H = 0, drops = [];
    let rainColor = readRain();

    function readRain() {
        const v = getComputedStyle(root).getPropertyValue("--rain-color").trim() || "120 135 150";
        return v.replace(/\s+/g, ",");
    }
    function densityFactor() {
        // drops per 10k px^2, scaled by intensity and device
        const base = lvl === "immersive" ? 2.6 : lvl === "calm" ? 0.5 : 1.3;
        return coarse ? base * 0.5 : base;
    }
    function makeDrop(seed) {
        const depth = Math.random();            // 0 far (slow, faint) -> 1 near
        return {
            x: Math.random() * (W + 120) - 60,
            y: seed ? Math.random() * H : -20 - Math.random() * H,
            len: 7 + depth * 15,
            v: (2.2 + depth * 4.5) * (lvl === "immersive" ? 1.25 : 1),
            a: 0.10 + depth * 0.28,
            w: 0.6 + depth * 0.9,
        };
    }
    function resize() {
        const r = host.getBoundingClientRect();
        W = Math.max(1, Math.round(r.width));
        H = Math.max(1, Math.round(scene ? r.height : window.innerHeight));
        dpr = Math.min(window.devicePixelRatio || 1, dprCap);
        canvas.width = Math.round(W * dpr);
        canvas.height = Math.round(H * dpr);
        canvas.style.width = W + "px";
        canvas.style.height = H + "px";
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const target = Math.round((W * H / 10000) * densityFactor());
        drops = [];
        for (let i = 0; i < target; i++) drops.push(makeDrop(true));
    }

    const wind = lvl === "immersive" ? 1.1 : 0.6;
    let raf = 0, last = 0, running = false, visible = true;

    function frame(t) {
        if (!running) return;
        const dt = Math.min(2.5, (t - last) / 16.67 || 1);
        last = t;
        ctx.clearRect(0, 0, W, H);
        ctx.lineCap = "round";
        for (const d of drops) {
            d.y += d.v * dt;
            d.x += wind * (d.v / 6) * dt;
            if (d.y - d.len > H) { Object.assign(d, makeDrop(false)); d.y = -d.len; }
            ctx.strokeStyle = `rgba(${rainColor},${d.a})`;
            ctx.lineWidth = d.w;
            ctx.beginPath();
            ctx.moveTo(d.x, d.y);
            ctx.lineTo(d.x - wind * 2.2, d.y - d.len);
            ctx.stroke();
        }
        // Calm: draw one static frame then stop.
        if (lvl === "calm" || !motionOK()) { running = false; return; }
        raf = requestAnimationFrame(frame);
    }
    function start() {
        if (running) return;
        running = true; last = performance.now();
        raf = requestAnimationFrame(frame);
    }
    function stop() { running = false; cancelAnimationFrame(raf); }

    // Pause offscreen (hero canvas) + when tab hidden.
    let io;
    if (scene && "IntersectionObserver" in window) {
        io = new IntersectionObserver((es) => {
            visible = es[0].isIntersecting;
            if (visible && !document.hidden) start(); else stop();
        }, { threshold: 0 });
        io.observe(scene);
    }
    const onVis = () => { if (document.hidden || !visible) stop(); else start(); };
    document.addEventListener("visibilitychange", onVis);

    const onResize = () => { resize(); if (lvl === "calm") { start(); } };
    window.addEventListener("resize", onResize, { passive: true });

    // Re-read rain colour when the theme flips.
    const themeObs = new MutationObserver(() => { rainColor = readRain(); if (lvl === "calm") start(); });
    themeObs.observe(root, { attributes: true, attributeFilter: ["data-theme"] });

    resize();
    start();

    teardown.push(() => {
        stop();
        io && io.disconnect();
        themeObs.disconnect();
        document.removeEventListener("visibilitychange", onVis);
        window.removeEventListener("resize", onResize);
        canvas.remove();
    });
}

/* ============================================================
   FOG — inject the element; CSS owns the drift (gated by intensity).
   ============================================================ */
function mountFog() {
    if (document.querySelector(".fx-fog")) return;
    const fog = document.createElement("div");
    fog.className = "fx-fog";
    fog.setAttribute("aria-hidden", "true");
    fog.innerHTML = "<i></i><i></i>";
    document.body.appendChild(fog);
    teardown.push(() => fog.remove());
}

/* ============================================================
   CURSOR DEW — immersive + fine pointer only. A soft light that
   follows the pointer and lifts the fog around it.
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
   REVEALS / STAGGER / COUNT-UP / TIMELINE DRAW (Phase 5).
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
    try { mountFog(); } catch (e) {}
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

// Re-evaluate cursor/reveal gating if the OS reduced-motion pref flips.
reduce.addEventListener?.("change", boot);
