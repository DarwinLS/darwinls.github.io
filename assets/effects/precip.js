/* ============================================================
   Precipitation layer (WebGL half).

   ONE fixed canvas at z -1 renders the active weather mode:
     rain -> 3 procedural streak depths with wind slant and a
             bright falling head (per-column speed/phase/length
             variance so it never reads as a repeating tile)
     fog  -> drifting 3-octave value-noise mist, denser toward
             the bottom of the viewport (near fog; the cloud-sea
             banks live in the scenery SVG, not here)

   Raw WebGL1, no library: one fullscreen triangle, one program,
   one draw call per frame. Budget guards:
     - powerPreference "low-power", no AA/depth/stencil
     - DPR cap: coarse 1, fine min(dpr, 1.5); fog renders at an
       extra 0.5 scale (low-frequency content, CSS upscales)
     - frame cap via timestamp accumulator: 60fps rain, 30fps fog
       (a 144Hz panel must never render 144fps weather)
     - rAF cancelled while the tab is hidden

   The host reuses the .fx-rain.is-fixed lvh sizing (see
   effects.css): the canvas backing store is sized ONCE from that
   box and re-sized only when the box genuinely changes, so the
   Android URL bar never resizes or re-rasters it.

   mountPrecip() returns a teardown function, or null on ANY
   failure (no context, compile/link error, context lost at
   creation) - ambient.js then falls back to the CSS tiled rain.

   Measured (tools/perf_probe.py, headed Edge, 144Hz Iris Xe,
   auto-scroll, median hz / avg ms per frame). Forest-pavilion round,
   with the glass surfaces and quiet-ambience rain in place:
     no precip 143 / 8.9   WebGL rain 143 / 8.9   CSS 1-sheet 143 / 9.3
     WebGL fog + drifting near bank 141 / 10.6
   Quiet rain now costs nothing measurable over the no-precip floor.
   Fog pays ~1.7ms for the ONE drifting bank; the bank must be the
   TOPMOST scene layer (mid-stack drift split every layer above it out
   of the track texture and pinned fog to 72Hz). Previous round for
   reference: no precip 145/7.5, loud rain 143/8.6, fog 143/8.3,
   old 2-sheet tiled immersive 143/9.5.
   ============================================================ */

const VERT = "attribute vec2 a_pos;void main(){gl_Position=vec4(a_pos,0.0,1.0);}";

const FRAG = `
precision mediump float;
uniform vec2 u_res;
uniform float u_time;
uniform float u_mode;      /* 0 fog, 1 rain */
uniform vec3 u_rainColor;
uniform vec3 u_fogColor;
uniform float u_wind;
uniform float u_alpha;     /* fog master opacity */
uniform float u_fogMix;    /* fog showing through in rain mode */
uniform float u_far;       /* far rain layer on/off (phones drop it) */

float h1(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}
float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(h1(i), h1(i + vec2(1.0, 0.0)), u.x),
        mix(h1(i + vec2(0.0, 1.0)), h1(i + vec2(1.0, 1.0)), u.x),
        u.y);
}
float fbm3(vec2 p) {
    return (0.5 * vnoise(p) + 0.25 * vnoise(p * 2.03) + 0.125 * vnoise(p * 4.09)) / 0.875;
}
/* One rain depth: hashed columns, per-column speed/phase/length,
   soft-edged streak with a squared falloff toward the tail. */
float streaks(vec2 st, float cols, float stretch, float speed,
              float len, float wid, float keep, float seed) {
    vec2 p = st;
    p.x += (1.0 - st.y) * u_wind * speed * 0.35;   /* nearer = more slant */
    float xc = p.x * cols;
    float col = floor(xc);
    float r = h1(vec2(col, seed));
    float on = step(1.0 - keep, h1(vec2(col, seed + 5.0)));
    float yv = fract(p.y * stretch + u_time * speed * (0.8 + 0.4 * r) + r * 7.0);
    float tail = smoothstep(len * (0.7 + 0.6 * r), 0.0, yv);
    tail *= tail;
    float cx = 0.2 + 0.6 * h1(vec2(col, seed + 9.0));
    float m = smoothstep(wid, wid * 0.35, abs(fract(xc) - cx));
    return on * tail * m;
}
float fogAmt(vec2 st, vec2 uv) {
    float d = 0.65 * fbm3(st * 2.2 + vec2(u_time * 0.015, 0.0))
            + 0.35 * fbm3(st * 4.8 - vec2(u_time * 0.030, u_time * 0.004));
    float m = smoothstep(0.85, 0.15, uv.y);        /* denser near the ground */
    return u_alpha * m * smoothstep(0.35, 0.75, d);
}
void main() {
    vec2 uv = gl_FragCoord.xy / u_res;
    vec2 st = vec2(uv.x * (u_res.x / u_res.y), uv.y);
    float a;
    vec3 col;
    if (u_mode > 0.5) {
        /* Quiet ambience: about half the lit columns of the first cut,
           dimmer heads, slightly slower fall. Rain should read as
           atmosphere BEHIND the content, never something you watch. */
        float r = streaks(st, 90.0, 5.0, 0.8, 0.24, 0.10, 0.30, 11.0) * u_far * 0.10
                + streaks(st, 55.0, 3.4, 1.3, 0.27, 0.12, 0.28, 23.0) * 0.16
                + streaks(st, 30.0, 2.2, 2.0, 0.32, 0.14, 0.25, 37.0) * 0.24;
        float f = 0.0;
        if (u_fogMix > 0.0) f = fogAmt(st, uv) * u_fogMix;
        a = min(1.0, r + f);
        col = u_rainColor;
    } else {
        a = fogAmt(st, uv);
        col = u_fogColor;
    }
    gl_FragColor = vec4(col * a, a);               /* premultiplied */
}
`;

/* Resolve a CSS color expression (incl. color-mix custom properties,
   whose computed custom-property value is NOT resolved) by letting
   the engine compute it on a probe element. */
function cssColor(expr) {
    const probe = document.createElement("div");
    probe.style.color = expr;
    probe.style.position = "absolute";
    probe.style.visibility = "hidden";
    document.body.appendChild(probe);
    const c = getComputedStyle(probe).color;
    probe.remove();
    const m = c.match(/[\d.]+/g);
    return m && m.length >= 3
        ? [+m[0] / 255, +m[1] / 255, +m[2] / 255]
        : [0.5, 0.55, 0.6];
}

function rainColor() {
    const t = getComputedStyle(document.documentElement)
        .getPropertyValue("--rain-color").trim();
    const p = t.split(/\s+/).map(Number);
    return p.length === 3 && p.every((v) => !isNaN(v))
        ? [p[0] / 255, p[1] / 255, p[2] / 255]
        : [0.42, 0.5, 0.57];
}

function buildProgram(gl) {
    function sh(type, src) {
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) return null;
        return s;
    }
    const vs = sh(gl.VERTEX_SHADER, VERT);
    const fs = sh(gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) return null;
    const prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return null;
    return prog;
}

export function mountPrecip({ mode, coarse, dbg, onDegrade }) {
    try {
        return mount(mode, coarse, dbg || null, onDegrade || null);
    } catch (e) {
        return null;
    }
}

function mount(mode, coarse, dbg, onDegrade) {
    const canvas = document.createElement("canvas");
    const attrs = {
        alpha: true, premultipliedAlpha: true, antialias: false,
        depth: false, stencil: false, powerPreference: "low-power",
    };
    const gl = canvas.getContext("webgl", attrs)
        || canvas.getContext("experimental-webgl", attrs);
    if (!gl || gl.isContextLost()) return null;

    /* Software WebGL (SwiftShader / llvmpipe: Chrome falls back to it
       when its GPU blocklist or a policy disables acceleration) turns
       the fullscreen shader into a per-frame CPU hog. Treat it as no
       WebGL at all and let the CSS tiled rain carry the weather. */
    try {
        const info = gl.getExtension("WEBGL_debug_renderer_info");
        const renderer = info
            ? String(gl.getParameter(info.UNMASKED_RENDERER_WEBGL))
            : "";
        if (/swiftshader|llvmpipe|software/i.test(renderer)) {
            const ext = gl.getExtension("WEBGL_lose_context");
            if (ext) ext.loseContext();
            return null;
        }
    } catch (e) {}

    const host = document.createElement("div");
    host.className = "fx-rain is-fixed fx-precip";
    host.setAttribute("aria-hidden", "true");
    host.appendChild(canvas);
    document.body.appendChild(host);

    const isRain = mode === "rain";
    const scale = (dbg && dbg.scale)
        || (coarse ? 1 : Math.min(devicePixelRatio || 1, 1.25)) * (isRain ? 1 : 0.5);
    const frameMs = dbg && dbg.fps ? 1000 / dbg.fps : isRain ? 1000 / 60 : 1000 / 30;

    let prog = null;
    let loc = null;

    function init() {
        prog = buildProgram(gl);
        if (!prog) return false;
        gl.useProgram(prog);
        const buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER,
            new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
        const aPos = gl.getAttribLocation(prog, "a_pos");
        gl.enableVertexAttribArray(aPos);
        gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);
        gl.disable(gl.DEPTH_TEST);
        /* No GL blending: the triangle overwrites every pixel per frame
           (blending here would accumulate frames), and the PAGE blends
           the canvas via its premultiplied alpha. */
        gl.disable(gl.BLEND);
        loc = {};
        for (const u of ["u_res", "u_time", "u_mode", "u_rainColor",
            "u_fogColor", "u_wind", "u_alpha", "u_fogMix", "u_far"]) {
            loc[u] = gl.getUniformLocation(prog, u);
        }
        gl.uniform1f(loc.u_mode, isRain ? 1 : 0);
        gl.uniform1f(loc.u_wind, 0.12);
        gl.uniform1f(loc.u_alpha, 0.28);
        gl.uniform1f(loc.u_fogMix, 0);
        gl.uniform1f(loc.u_far, coarse ? 0 : 1);
        tint();
        return true;
    }

    function tint() {
        gl.uniform3fv(loc.u_rainColor, rainColor());
        gl.uniform3fv(loc.u_fogColor, cssColor("var(--mist-veil)"));
    }

    /* Backing store rides the lvh host box: the Android URL bar never
       changes that box, so bar settles are a no-op here by the guard. */
    let boxW = 0, boxH = 0;
    function size() {
        const r = host.getBoundingClientRect();
        if (Math.abs(r.width - boxW) <= 1 && Math.abs(r.height - boxH) <= 1) return;
        boxW = r.width;
        boxH = r.height;
        canvas.width = Math.max(1, Math.round(r.width * scale));
        canvas.height = Math.max(1, Math.round(r.height * scale));
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.uniform2f(loc.u_res, canvas.width, canvas.height);
    }

    if (!init()) {
        host.remove();
        return null;
    }
    size();

    /* Frame-capped loop: skip rAF ticks until the cap interval has
       passed, keeping the remainder so cadence stays even.
       Watchdog: if the achieved cadence of DRAWN frames runs far
       behind the cap (weak GPU, browser throttling, anything the
       software-renderer check above could not see), self-destruct and
       hand the weather back to the cheap CSS path via onDegrade. */
    let raf = 0;
    let last = 0;
    let wdCount = 0;
    let wdStart = 0;
    let wdDone = false;
    const t0 = performance.now();
    function frame(t) {
        raf = requestAnimationFrame(frame);
        if (t - last < frameMs - 1) return;
        last = t - ((t - last) % frameMs);
        gl.uniform1f(loc.u_time, ((t - t0) / 1000) % 3600);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        if (!wdDone) {
            wdCount++;
            if (wdCount === 20) {
                wdStart = t;             /* skip startup jank */
            } else if (wdCount === 80) {
                wdDone = true;
                if ((t - wdStart) / 60 > frameMs * 1.8) {
                    dispose();
                    if (onDegrade) onDegrade();
                }
            }
        }
    }
    function start() {
        if (!raf) raf = requestAnimationFrame(frame);
    }
    function stop() {
        cancelAnimationFrame(raf);
        raf = 0;
    }
    start();

    const onVis = () => {
        if (document.hidden) {
            stop();
        } else {
            wdCount = 0;                 /* do not count the hidden gap */
            start();
        }
    };
    document.addEventListener("visibilitychange", onVis);

    let resizeTimer = 0;
    const onResize = () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(size, 250);
    };
    window.addEventListener("resize", onResize);

    const onLost = (e) => {
        e.preventDefault();
        stop();
    };
    const onRestored = () => {
        if (init()) {
            boxW = 0;                      /* force a re-size */
            size();
            start();
        }
    };
    canvas.addEventListener("webglcontextlost", onLost);
    canvas.addEventListener("webglcontextrestored", onRestored);

    /* Theme flip = a pair of uniform writes, no re-init (cheaper than
       the tile regeneration the CSS fallback needs). */
    const themeObs = new MutationObserver(tint);
    themeObs.observe(document.documentElement,
        { attributes: true, attributeFilter: ["data-theme"] });

    /* Idempotent: the watchdog can dispose first and ambient.js will
       still call the same teardown later on a dial/theme reboot. */
    let disposed = false;
    function dispose() {
        if (disposed) return;
        disposed = true;
        stop();
        clearTimeout(resizeTimer);
        themeObs.disconnect();
        document.removeEventListener("visibilitychange", onVis);
        window.removeEventListener("resize", onResize);
        canvas.removeEventListener("webglcontextlost", onLost);
        canvas.removeEventListener("webglcontextrestored", onRestored);
        const ext = gl.getExtension("WEBGL_lose_context");
        if (ext) ext.loseContext();
        host.remove();
    }
    return dispose;
}
