/* ============================================================
   Ambient + choreography controller (JS half).

   Progressive enhancement: this module only ADDS motion. Without it
   the site is fully styled and readable (scenery is static inline
   SVG, content is never hidden by CSS unless this script runs).

   It reads the intensity dial ([data-intensity] on <html>, set by the
   no-FOUC inline script) and mounts effects to match:
     calm       -> no rain, no cursor light, no reveals-hide
                   (atmosphere = static in-scene mist + .fx-haze)
     balanced   -> tiled rain (1 dense sheet), reveals, timeline draw
     immersive  -> tiled rain (2 sheets), cursor dew
   Rain streaks are drawn ONCE into small tiling textures; each depth
   layer is then a repeating background scrolled by a CSS transform
   animation. Zero per-frame JS, zero WebGL: the compositor moves
   three textures, the same cost as scrolling a page. save-data and
   low-memory devices get no rain at all.
   ============================================================ */

const root = document.documentElement;
const reduce = matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = matchMedia("(pointer: fine)");

const level = () => root.dataset.intensity || "balanced";
const motionOK = () => !reduce.matches;

/* ---------- shared engine lifecycle ---------- */
let teardown = [];
let gen = 0;                          // bumped each boot; guards async mounts
function destroyAll() {
    teardown.forEach((fn) => { try { fn(); } catch (e) {} });
    teardown = [];
}

/* ============================================================
   RAIN - compositor-tiled sheets.
   ============================================================ */

/* Dev-only override, set by the perf harness (tools/perf_probe.py)
   before this module loads: { off, sheets, stepsPerSec }. Never set
   in production pages. */
const rainDebug = () => window.__rainDebug || null;

/* null = no rain at all (calm, reduced motion, save-data, low-end) */
function rainLevel() {
    const dbg = rainDebug();
    if (dbg && dbg.off) return null;
    const lvl = level();
    if (lvl === "calm" || !motionOK()) return null;
    const conn = navigator.connection;
    if (conn && conn.saveData) return null;
    if (navigator.deviceMemory && navigator.deviceMemory <= 2) return null;
    return lvl;
}

/* Depth sheets, far -> near. Each becomes one small tiling texture
   drawn once, then scrolled forever by the compositor. The slant is
   BAKED into the streaks (no rotated wrapper: the old rotate needed a
   -14%/-10% oversize, and on DPR-3 phones those oversized sheets blew
   the compositor's texture budget - other layers got evicted and the
   page visibly flashed while scrolling). dur is seconds per 1024px. */
const TILE_W = 512;
const SHEETS = [
    { count: 170, len: 30, w: 1.0, a: 0.20, dur: 2.6, slant: 3 },
    { count: 100, len: 48, w: 1.4, a: 0.30, dur: 1.7, slant: 5 },
    { count: 44,  len: 80, w: 2.0, a: 0.40, dur: 1.05, slant: 7 },
];

function rainRGB() {
    return (getComputedStyle(root).getPropertyValue("--rain-color").trim() || "120 135 150")
        .replace(/\s+/g, ",");
}

/* One tile: slanted streaks with a bright falling head fading up,
   drawn around both seams (3x3 offsets) so the loop is seamless. */
function makeRainTile(rgb, sheet, densityMul, tileH) {
    const c = document.createElement("canvas");
    c.width = TILE_W;
    c.height = tileH;
    const ctx = c.getContext("2d");
    ctx.lineCap = "round";
    const slope = Math.tan((sheet.slant * Math.PI) / 180);
    const n = Math.round(sheet.count * densityMul * (tileH / 1024));
    for (let i = 0; i < n; i++) {
        const x = Math.random() * TILE_W;
        const y = Math.random() * tileH;
        const len = sheet.len * (0.55 + 0.9 * Math.random());
        const a = sheet.a * (0.55 + 0.9 * Math.random());
        const dx = slope * len;
        ctx.lineWidth = sheet.w * (0.75 + 0.5 * Math.random());
        for (const ox of [-TILE_W, 0, TILE_W]) {
            for (const oy of [-tileH, 0, tileH]) {
                const g = ctx.createLinearGradient(x + ox - dx, y + oy - len, x + ox, y + oy);
                g.addColorStop(0, `rgba(${rgb},0)`);
                g.addColorStop(1, `rgba(${rgb},${a})`);
                ctx.strokeStyle = g;
                ctx.beginPath();
                ctx.moveTo(x + ox - dx, y + oy - len);
                ctx.lineTo(x + ox, y + oy);
                ctx.stroke();
            }
        }
    }
    return c.toDataURL();
}

function mountRain() {
    const lvl = rainLevel();
    if (!lvl) return;
    const dbg = rainDebug();
    const coarse = !finePointer.matches;
    /* Measured (tools/perf_probe.py, 144Hz Iris Xe): ONE sheet on a
       512 tile scrolls at a tight single-vsync cadence (p95 7.1ms);
       every extra sheet adds regular double-vsync spills. So balanced
       and phones run one denser mid sheet; immersive opts into two.
       Small tiles also halve each sheet's GPU memory (phone eviction). */
    let sheets = lvl === "immersive" && !coarse
        ? [SHEETS[1], SHEETS[2]]
        : [SHEETS[1]];
    if (dbg && dbg.sheets) sheets = SHEETS.slice(0, dbg.sheets);
    const tileH = (dbg && dbg.tileH) || 512;
    const densityMul = coarse ? 0.8 : lvl === "immersive" ? 1 : 1.25;

    const host = document.createElement("div");
    host.className = "fx-rain is-fixed";
    host.setAttribute("aria-hidden", "true");
    const movers = [];
    for (const sheet of sheets) {
        const move = document.createElement("div");
        move.className = "fx-rain-move";
        const dur = (sheet.dur * tileH) / 1024;
        move.style.setProperty("--dur", dur + "s");
        move.style.setProperty("--tile-h", tileH + "px");
        /* Quantized fall: with steps() the transform only changes N
           times per second, so the frames in between carry no damage
           and the compositor skips them entirely. A linear fall damages
           EVERY vsync: on a 144Hz+ panel that keeps the GPU compositing
           the whole page stack nonstop even while idle (fan spin-up).
           32/s reads as smooth motion at rain speeds. */
        const sps = dbg && dbg.linear ? 0 : (dbg && dbg.stepsPerSec) || 32;
        if (sps) {
            move.style.animationTimingFunction =
                `steps(${Math.max(2, Math.round(dur * sps))})`;
        }
        move.style.backgroundImage = `url(${makeRainTile(rainRGB(), sheet, densityMul, tileH)})`;
        host.appendChild(move);
        movers.push({ move, sheet });
    }
    document.body.appendChild(host);

    /* re-tint on theme flip (regenerating the small tiles is cheap) */
    const themeObs = new MutationObserver(() => {
        const rgb = rainRGB();
        for (const m of movers) {
            m.move.style.backgroundImage = `url(${makeRainTile(rgb, m.sheet, densityMul, tileH)})`;
        }
    });
    themeObs.observe(root, { attributes: true, attributeFilter: ["data-theme"] });

    teardown.push(() => {
        themeObs.disconnect();
        host.remove();
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
    try { mountRain(); } catch (e) {}
    try { mountCursor(); } catch (e) {}
    try { mountReveals(); } catch (e) {}
}

/* Speculation Rules prerender pages in the background; never run the
   rain (or any rAF work) inside a prerendered page - boot on reveal. */
if (document.prerendering) {
    document.addEventListener("prerenderingchange", boot, { once: true });
} else {
    boot();
}

// Re-mount when the intensity dial changes (nav toggle / device re-clamp).
let remountTimer = 0;
new MutationObserver(() => {
    clearTimeout(remountTimer);
    remountTimer = setTimeout(boot, 60);
}).observe(root, { attributes: true, attributeFilter: ["data-intensity"] });

// Re-evaluate rain/cursor/reveal gating if the OS reduced-motion pref flips.
reduce.addEventListener?.("change", boot);
