/* ============================================================
   Immersive WebGL2 volumetric rain (Phase 6).

   A desktop-only, feature-detected upgrade over the 2D canvas rain.
   Renders layered depth streaks + a faint volumetric wash in a single
   fullscreen fragment pass. Own GLSL (no license strings attached).

   ambient.js dynamically import()s this ONLY when: intensity=immersive,
   fine pointer, motion allowed, and WebGL2 is present. Any failure here
   (no context, compile error, context loss) returns null so the caller
   falls back to the proven 2D canvas rain.
   ============================================================ */

const VERT = `#version 300 es
in vec2 p;
void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;

const FRAG = `#version 300 es
precision highp float;
out vec4 o;
uniform vec2 uRes;
uniform float uTime;
uniform float uDark;
uniform vec3 uColor;

float hash(float n){ return fract(sin(n) * 43758.5453123); }

// One depth layer of falling streaks.
float rainLayer(vec2 uv, float t, float cols, float speed, float thick){
    uv.x *= cols;
    float id = floor(uv.x);
    float fx = fract(uv.x) - 0.5;
    if (hash(id * 1.7) < 0.4) return 0.0;                 // gaps between columns
    float sp  = speed * (0.7 + 0.6 * hash(id + 2.3));
    float off = hash(id * 4.1) * 9.0;
    float fy  = fract(uv.y * (cols * 0.16) + t * sp + off);
    float dash = smoothstep(0.0, 0.015, fy) * smoothstep(0.26, 0.02, fy); // falling dash
    float line = smoothstep(thick, 0.0, abs(fx));         // thin vertical
    float jitter = 0.85 + 0.15 * hash(id + 11.0);
    return dash * line * jitter;
}

void main(){
    vec2 uv = gl_FragCoord.xy / uRes.xy;
    uv.y = 1.0 - uv.y;                                    // top = 0
    float t = uTime;
    float acc = 0.0;
    acc += rainLayer(uv, t, 34.0, 0.85, 0.030) * 0.45;   // far
    acc += rainLayer(uv, t, 22.0, 1.30, 0.026) * 0.75;   // mid
    acc += rainLayer(uv, t, 14.0, 1.95, 0.022) * 1.00;   // near
    acc = clamp(acc, 0.0, 1.0);
    acc *= smoothstep(0.0, 0.12, uv.y + 0.05);           // ease in from the top
    float alpha = acc * (uDark > 0.5 ? 0.55 : 0.46);
    o = vec4(uColor * alpha, alpha);                     // premultiplied
}`;

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
    const scene = !!opts.scene;
    const canvas = document.createElement("canvas");
    canvas.className = "fx-rain" + (scene ? "" : " is-fixed");
    canvas.setAttribute("aria-hidden", "true");

    const gl = canvas.getContext("webgl2", { alpha: true, premultipliedAlpha: true, antialias: false, depth: false });
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
    const uRes = gl.getUniformLocation(prog, "uRes");
    const uTime = gl.getUniformLocation(prog, "uTime");
    const uDark = gl.getUniformLocation(prog, "uDark");
    const uColor = gl.getUniformLocation(prog, "uColor");

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);   // premultiplied

    const root = document.documentElement;
    const dprCap = 1.75;
    let W = 0, H = 0;

    function readColor() {
        const v = getComputedStyle(root).getPropertyValue("--rain-color").trim() || "180 200 220";
        return v.split(/\s+/).map((n) => parseFloat(n) / 255);
    }
    let color = readColor();
    let dark = root.dataset.theme === "dark" ? 1 : (matchMedia("(prefers-color-scheme: dark)").matches && root.dataset.theme !== "light" ? 1 : 0);

    function resize() {
        const r = host.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, dprCap);
        W = Math.max(1, Math.round((r.width || window.innerWidth) * dpr));
        H = Math.max(1, Math.round((scene ? r.height : window.innerHeight) * dpr));
        canvas.width = W; canvas.height = H;
        canvas.style.width = (scene ? r.width : window.innerWidth) + "px";
        canvas.style.height = (scene ? r.height : window.innerHeight) + "px";
        gl.viewport(0, 0, W, H);
    }

    let raf = 0, running = false, visible = true, t0 = performance.now();
    function frame(now) {
        if (!running) return;
        gl.useProgram(prog);
        gl.uniform2f(uRes, W, H);
        gl.uniform1f(uTime, (now - t0) / 1000);
        gl.uniform1f(uDark, dark);
        gl.uniform3f(uColor, color[0], color[1], color[2]);
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        raf = requestAnimationFrame(frame);
    }
    function start() { if (!running) { running = true; raf = requestAnimationFrame(frame); } }
    function stop() { running = false; cancelAnimationFrame(raf); }

    let io;
    if (scene && "IntersectionObserver" in window) {
        io = new IntersectionObserver((e) => { visible = e[0].isIntersecting; (visible && !document.hidden) ? start() : stop(); }, { threshold: 0 });
        io.observe(host);
    }
    const onVis = () => { (document.hidden || !visible) ? stop() : start(); };
    const onResize = () => resize();
    const themeObs = new MutationObserver(() => {
        color = readColor();
        dark = root.dataset.theme === "dark" ? 1 : (root.dataset.theme === "light" ? 0 : dark);
    });
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
            io && io.disconnect();
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
