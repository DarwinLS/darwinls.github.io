/* ============================================================
   WebGL2 rain - the PRIMARY rain renderer at every intensity
   (ambient.js falls back to a batched 2D canvas only when WebGL2
   is missing or the frame-time watchdog trips).

   One fullscreen fragment pass, own GLSL. Compared to the old
   column-dash draft: per-streak hashed identity (speed, length,
   brightness, thickness, phase), per-layer slant with low-frequency
   wind gusts, bright-head/fading-tail shading, a faint atmospheric
   haze floor so the frame has body between streaks, and sparse
   splash glints along the bottom (immersive, fine pointer).

   createRainGL(host, { level, coarse, splash }) -> { ok, destroy }
   or null on any failure (caller falls back).
   ============================================================ */

const VERT = `#version 300 es
in vec2 p;
void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;

const FRAG = `#version 300 es
precision highp float;
out vec4 o;
uniform vec2  uRes;
uniform float uTime;
uniform vec3  uColor;
uniform float uC1;      /* column counts per depth layer; 0 = layer off */
uniform float uC2;
uniform float uC3;
uniform float uOpacity;
uniform float uSpeed;
uniform float uWind;
uniform float uSplash;

float hash(float n){ return fract(sin(n) * 43758.5453123); }

/* One depth layer of streaks. Every column hashes its own speed,
   dash length, brightness, thickness and phase so the sheet never
   reads as a uniform grid. */
float rainLayer(vec2 uv, float t, float cols, float speed,
                float thick, float gap, float slant, float lenMul, float soft){
    uv.x += (uv.y - 0.5) * slant;                     /* wind shear */
    uv.x *= cols;
    float id = floor(uv.x);
    float fx = fract(uv.x) - 0.5;
    if (hash(id * 1.7 + cols) < gap) return 0.0;      /* canopy gaps */
    float spd = speed * (0.7 + 0.6 * hash(id + 2.3));
    float len = (0.10 + 0.20 * hash(id * 3.3 + 7.0)) * lenMul;
    float bri = 0.6 + 0.4 * hash(id + 11.0);
    float th  = thick * (0.8 + 0.4 * hash(id * 5.1 + 3.0));
    float off = hash(id * 4.1) * 9.0;
    /* MINUS t so the pattern travels DOWN the screen (uv.y grows
       downward): constant-phase points sit at uv.y = (c + t*spd)/k */
    float fy  = fract(uv.y * (cols * 0.14) - t * spd + off);
    /* bright head at the BOTTOM (leading) edge, tail fading upward */
    float tail = smoothstep(0.0, len * 0.8, fy);
    float head = 1.0 - smoothstep(len * 0.97, len, fy);
    float dash = tail * head * step(fy, len);
    float line = smoothstep(th, th * soft, abs(fx));
    return dash * line * bri;
}

void main(){
    vec2 uv = gl_FragCoord.xy / uRes.xy;
    uv.y = 1.0 - uv.y;                                /* top = 0 */
    float t = uTime;
    /* slow wind gusts sway the shear angle of every layer */
    float gust = uWind * (0.6 * sin(t * 0.13) + 0.4 * sin(t * 0.047 + 1.7));
    float acc = 0.0;
    if (uC1 > 0.5) acc += rainLayer(uv, t, uC1, 0.85 * uSpeed, 0.030, 0.55, 0.030 + 0.045 * gust, 0.85, 0.10) * 0.40;
    if (uC2 > 0.5) acc += rainLayer(uv, t, uC2, 1.30 * uSpeed, 0.026, 0.45, 0.055 + 0.075 * gust, 1.00, 0.18) * 0.70;
    if (uC3 > 0.5) acc += rainLayer(uv, t, uC3, 1.95 * uSpeed, 0.024, 0.35, 0.085 + 0.115 * gust, 1.60, 0.38) * 1.45;
    /* sparse splash glints where drops meet the ground line */
    if (uSplash > 0.5 && uv.y > 0.955) {
        float cell = floor(uv.x * 60.0);
        float ph = hash(cell * 9.7);
        float fl = fract(t * (0.45 + 0.5 * hash(cell * 3.1)) + ph);
        float glint = smoothstep(0.05, 0.0, fl);
        float fxs = abs(fract(uv.x * 60.0) - 0.5);
        acc += glint * smoothstep(0.42, 0.08, fxs) * smoothstep(0.955, 0.985, uv.y) * 0.5;
    }
    acc = clamp(acc, 0.0, 1.0);
    acc *= smoothstep(0.0, 0.12, uv.y + 0.05);        /* ease in from the sky */
    /* atmospheric haze floor: wet air, not just lines */
    float haze = smoothstep(0.5, 1.05, uv.y) * 0.05
               + smoothstep(0.25, 0.0, uv.y) * 0.03;
    float alpha = clamp(acc * uOpacity + haze * uOpacity * 0.9, 0.0, 1.0);
    o = vec4(uColor * alpha, alpha);                  /* premultiplied */
}`;

/* Per-intensity render profile. The whole budget is engineered to fit
   an INTEGRATED GPU comfortably: soft streaks hide the low DPR, and
   balanced renders at ~30fps. coarse pointers go lower still; the
   watchdog in ambient.js guards the rest. */
function profile(level, coarse) {
    const p = level === "immersive"
        ? { cols: [34, 22, 14], op: [0.46, 0.55], speed: 1.15, wind: 1.0, dpr: coarse ? 1.0 : 1.25, minFrame: 0 }
        : { cols: [26, 15, 0],  op: [0.34, 0.44], speed: 1.0,  wind: 0.5, dpr: coarse ? 1.0 : 1.25, minFrame: 31 };
    if (coarse) p.cols = p.cols.map((c) => Math.round(c * 0.7));
    return p;
}

function compile(gl, type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
        gl.deleteShader(s);
        return null;
    }
    return s;
}

export function createRainGL(host, opts = {}) {
    const canvas = document.createElement("canvas");
    canvas.className = "fx-rain is-fixed";
    canvas.setAttribute("aria-hidden", "true");

    /* low-power on purpose: ambient rain must never wake the discrete
       GPU (fan spin) on dual-GPU laptops; the budget fits the iGPU */
    const gl = canvas.getContext("webgl2", {
        alpha: true, premultipliedAlpha: true, antialias: false, depth: false,
        powerPreference: "low-power",
    });
    if (!gl) return null;

    const vs = compile(gl, gl.VERTEX_SHADER, VERT);
    const fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) return null;
    const prog = gl.createProgram();
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return null;

    host.appendChild(canvas);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, "p");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    gl.useProgram(prog);
    const U = {};
    for (const n of ["uRes", "uTime", "uColor", "uC1", "uC2", "uC3", "uOpacity", "uSpeed", "uWind", "uSplash"]) {
        U[n] = gl.getUniformLocation(prog, n);
    }

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);   /* premultiplied */

    const root = document.documentElement;
    const prof = profile(opts.level, !!opts.coarse);
    const splash = opts.level === "immersive" && !opts.coarse ? 1 : 0;
    let W = 0, H = 0;

    function isDark() {
        if (root.dataset.theme === "dark") return true;
        if (root.dataset.theme === "light") return false;
        return matchMedia("(prefers-color-scheme: dark)").matches;
    }
    function readColor() {
        const v = getComputedStyle(root).getPropertyValue("--rain-color").trim() || "120 135 150";
        return v.split(/\s+/).map((n) => parseFloat(n) / 255);
    }
    let color = readColor();
    let dark = isDark();

    function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, prof.dpr);
        W = Math.max(1, Math.round(window.innerWidth * dpr));
        H = Math.max(1, Math.round(window.innerHeight * dpr));
        canvas.width = W; canvas.height = H;
        canvas.style.width = window.innerWidth + "px";
        canvas.style.height = window.innerHeight + "px";
        gl.viewport(0, 0, W, H);
    }

    let raf = 0, running = false, t0 = performance.now(), lastDraw = 0;
    function frame(now) {
        if (!running) return;
        /* balanced runs at ~30fps: half the fragment work, invisible
           on soft streaks */
        if (prof.minFrame && now - lastDraw < prof.minFrame) {
            raf = requestAnimationFrame(frame);
            return;
        }
        lastDraw = now;
        gl.useProgram(prog);
        gl.uniform2f(U.uRes, W, H);
        gl.uniform1f(U.uTime, (now - t0) / 1000);
        gl.uniform3f(U.uColor, color[0], color[1], color[2]);
        gl.uniform1f(U.uC1, prof.cols[0]);
        gl.uniform1f(U.uC2, prof.cols[1]);
        gl.uniform1f(U.uC3, prof.cols[2]);
        gl.uniform1f(U.uOpacity, dark ? prof.op[1] : prof.op[0]);
        gl.uniform1f(U.uSpeed, prof.speed);
        gl.uniform1f(U.uWind, prof.wind);
        gl.uniform1f(U.uSplash, splash);
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        raf = requestAnimationFrame(frame);
    }
    function start() { if (!running) { running = true; raf = requestAnimationFrame(frame); } }
    function stop() { running = false; cancelAnimationFrame(raf); }

    const onVis = () => { document.hidden ? stop() : start(); };
    const onResize = () => resize();
    const themeObs = new MutationObserver(() => { color = readColor(); dark = isDark(); });
    let lost = false;
    const onLost = (e) => { e.preventDefault(); lost = true; stop(); };
    canvas.addEventListener("webglcontextlost", onLost);

    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("resize", onResize, { passive: true });
    themeObs.observe(root, { attributes: true, attributeFilter: ["data-theme"] });

    resize();
    start();

    return {
        ok: true,
        destroy() {
            stop();
            themeObs.disconnect();
            document.removeEventListener("visibilitychange", onVis);
            window.removeEventListener("resize", onResize);
            canvas.removeEventListener("webglcontextlost", onLost);
            const ext = gl.getExtension("WEBGL_lose_context");
            ext && !lost && ext.loseContext();
            canvas.remove();
        },
    };
}
