"""Scene generator (dev-time only, stdlib only, nothing ships).

Produces the inline-SVG scenery for the site: layered ink-wash ridges
with conifer serration, interleaved mist bands, the valley-floor footer
treelines, and botanical divider line-art.

Usage:
    python tools/scene_gen.py            write partials to assets/scenes/
    python tools/scene_gen.py --inject   also rewrite the HTML files
                                         between <!-- scene:NAME --> markers

Deterministic: seeds live in the SCENES config below, so output is
reproducible and diffable. Colors are never baked in: paths reference
gradient stops / fill classes defined in styles.css (gs-*, ft-*,
firefly), which is what makes the scenes adapt to light / dark /
per-biome themes.
"""

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "scenes"
INJECT = "--inject" in sys.argv

# ---------------- scene definitions ----------------
# Shared frame: ridge/mist layers compose in a 1440x900 reference
# viewBox. baseline = mean crest height (higher = lower on screen).
# amp = crest amplitude above baseline. freq = big undulations across
# the width. ramp = which .gs-N gradient ramp colors the layer
# (1 = farthest / dissolved into sky, 7 = nearest / most ink).
# serr = conifer serration (step, h, w) in frame px, None = smooth.
# env(x) optionally scales amplitude across the width (x in 0..1).

FRAME = (1440, 900)

SCENES = {
    # HOME: the descent composition (7 ridges + 3 mist bands)
    "home-descent": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "sd",
        "grad_ns": "home",
        "layers": [
            {"type": "ridge", "name": "sd-1", "seed": 101, "baseline": 330, "amp": 88,  "freq": 2.3, "sharp": 1.25, "skew": 0.18, "ramp": 1, "serr": None, "ridged": True},
            {"type": "mist",  "name": "sd-m1", "seed": 151, "yc": 468, "thick": 210, "opacity": 0.85},
            {"type": "ridge", "name": "sd-2", "seed": 102, "baseline": 400, "amp": 108, "freq": 2.7, "sharp": 1.20, "skew": 0.20, "ramp": 2, "serr": None, "ridged": True},
            {"type": "mist",  "name": "sd-m2", "seed": 152, "yc": 615, "thick": 150, "opacity": 0.7},
            {"type": "ridge", "name": "sd-3", "seed": 103, "baseline": 470, "amp": 110, "freq": 3.0, "sharp": 1.35, "skew": 0.22, "ramp": 3, "serr": (32, 10, 7)},
            {"type": "ridge", "name": "sd-4", "seed": 104, "baseline": 550, "amp": 120, "freq": 2.8, "sharp": 1.25, "skew": 0.25, "ramp": 4, "serr": (26, 14, 8)},
            {"type": "mist",  "name": "sd-m3", "seed": 153, "yc": 800, "thick": 180, "opacity": 0.7},
            {"type": "ridge", "name": "sd-5", "seed": 105, "baseline": 640, "amp": 120, "freq": 3.4, "sharp": 1.20, "skew": 0.28, "ramp": 5, "serr": (20, 22, 11)},
            {"type": "ridge", "name": "sd-6", "seed": 106, "baseline": 730, "amp": 110, "freq": 4.0, "sharp": 1.15, "skew": 0.30, "ramp": 6, "serr": (16, 30, 13)},
            {"type": "ridge", "name": "sd-7", "seed": 107, "baseline": 830, "amp": 80,  "freq": 4.6, "sharp": 1.10, "skew": 0.30, "ramp": 7, "serr": (13, 40, 15)},
        ],
    },
    # PROJECTS: rain-veiled closer forest
    "vista-projects": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "vl",
        "grad_ns": "proj",
        "layers": [
            {"type": "ridge", "name": "vl-1", "seed": 201, "baseline": 620, "amp": 100, "freq": 2.6, "sharp": 1.35, "skew": 0.22, "ramp": 3, "serr": (24, 16, 11)},
            {"type": "mist",  "name": "vl-m1", "seed": 251, "yc": 700, "thick": 135, "opacity": 0.65},
            {"type": "ridge", "name": "vl-2", "seed": 202, "baseline": 720, "amp": 110, "freq": 3.2, "sharp": 1.20, "skew": 0.26, "ramp": 5, "serr": (18, 26, 14)},
            {"type": "ridge", "name": "vl-3", "seed": 203, "baseline": 810, "amp": 90,  "freq": 3.8, "sharp": 1.12, "skew": 0.30, "ramp": 6, "serr": (14, 34, 17)},
        ],
    },
    # ABOUT: dusk valley, ridges frame the timeline column
    "vista-about": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "vl",
        "grad_ns": "abt",
        "env": lambda x: 0.55 + 0.95 * abs(x - 0.5) * 2,
        "layers": [
            {"type": "ridge", "name": "vl-1", "seed": 301, "baseline": 600, "amp": 95,  "freq": 2.2, "sharp": 1.45, "skew": 0.20, "ramp": 2, "serr": None},
            {"type": "ridge", "name": "vl-2", "seed": 302, "baseline": 680, "amp": 105, "freq": 2.7, "sharp": 1.30, "skew": 0.24, "ramp": 3, "serr": (26, 10, 9)},
            {"type": "mist",  "name": "vl-m1", "seed": 351, "yc": 760, "thick": 130, "opacity": 0.6},
            {"type": "ridge", "name": "vl-3", "seed": 303, "baseline": 760, "amp": 100, "freq": 3.2, "sharp": 1.18, "skew": 0.28, "ramp": 5, "serr": (20, 20, 12)},
            {"type": "ridge", "name": "vl-4", "seed": 304, "baseline": 845, "amp": 80,  "freq": 3.7, "sharp": 1.12, "skew": 0.30, "ramp": 6, "serr": (15, 28, 15)},
        ],
    },
    # CONTACT: golden-hour clearing, soft far ridges + horizon glow
    "vista-contact": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "vl",
        "grad_ns": "con",
        "layers": [
            {"type": "glow",  "name": "vl-glow", "cx": 730, "cy": 815, "rx": 560, "ry": 175},
            {"type": "ridge", "name": "vl-1", "seed": 401, "baseline": 700, "amp": 60, "freq": 1.8, "sharp": 1.55, "skew": 0.16, "ramp": 1, "serr": None},
            {"type": "mist",  "name": "vl-m1", "seed": 451, "yc": 805, "thick": 150, "opacity": 0.6},
            {"type": "ridge", "name": "vl-2", "seed": 402, "baseline": 790, "amp": 70, "freq": 2.2, "sharp": 1.45, "skew": 0.18, "ramp": 2, "serr": None},
        ],
    },
    # VERAFLUX: reading sanctuary, one distant ridge
    "vista-veraflux": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "vl",
        "grad_ns": "vera",
        "layers": [
            {"type": "ridge", "name": "vl-1", "seed": 501, "baseline": 812, "amp": 60, "freq": 1.6, "sharp": 1.55, "skew": 0.15, "ramp": 1, "serr": None},
        ],
    },
    # FOOTER: valley-floor treelines, all pages, in-flow svg
    "footer-valley": {
        "kind": "footer",
        "frame": (1440, 180),
        "grad_ns": "foot",
        "layers": [
            {"type": "treeline", "name": "ft-1", "seed": 601, "baseline": 106, "amp": 26, "freq": 2.6, "sharp": 1.15, "skew": 0.25, "serr": (17, 34, 13), "skip": 0.3},
            {"type": "treeline", "name": "ft-2", "seed": 602, "baseline": 130, "amp": 26, "freq": 3.2, "sharp": 1.10, "skew": 0.28, "serr": (15, 44, 15), "skip": 0.26},
            {"type": "mist",     "name": "ft-m1", "seed": 651, "yc": 140, "thick": 75, "opacity": 0.32},
            {"type": "treeline", "name": "ft-3", "seed": 603, "baseline": 154, "amp": 20, "freq": 3.8, "sharp": 1.05, "skew": 0.30, "serr": (13, 54, 18), "skip": 0.24},
        ],
        "fireflies": {"seed": 691, "count": 9, "x": (70, 1380), "y": (72, 148), "r": (1.5, 2.5)},
    },
    # DIVIDERS: botanical line-art (fern fronds + a sprig)
    "divider-fern-1":      {"kind": "fern",  "seed": 701, "w": 190, "h": 36},
    "divider-fern-2":      {"kind": "fern",  "seed": 702, "w": 190, "h": 36},
    "divider-fern-home":   {"kind": "fern",  "seed": 703, "w": 190, "h": 36},
    "divider-sprig-about": {"kind": "sprig", "seed": 704, "w": 170, "h": 36},
}

# Where each scene's generated block gets injected
# (between <!-- scene:NAME --> ... <!-- /scene:NAME --> markers).
TARGETS = {
    "home-descent":        ["index.html"],
    "vista-projects":      ["projects.html"],
    "vista-about":         ["about.html"],
    "vista-contact":       ["contact.html"],
    "vista-veraflux":      ["veraflux.html"],
    "footer-valley":       ["index.html", "projects.html", "about.html", "contact.html", "veraflux.html"],
    "divider-fern-1":      ["projects.html"],
    "divider-fern-2":      ["projects.html"],
    "divider-fern-home":   ["index.html"],
    "divider-sprig-about": ["about.html"],
}

# ---------------- deterministic randomness ----------------

MASK = 0xFFFFFFFF


def mulberry32(seed):
    state = {"a": seed & MASK}

    def rnd():
        state["a"] = (state["a"] + 0x6D2B79F5) & MASK
        t = state["a"]
        t = ((t ^ (t >> 15)) * (t | 1)) & MASK
        t = (t + (((t ^ (t >> 7)) * (t | 61)) & MASK)) ^ t
        t &= MASK
        return ((t ^ (t >> 14)) & MASK) / 4294967296

    return rnd


def fbm(seed, base_freq, octaves=4, gain=0.5, lac=2.0, fold=False):
    """1D fractal value noise: f(x) for x in 0..1, output ~0..1.
    fold=True folds each octave (ridged multifractal): sharp crests,
    V valleys, summit heights that vary instead of plateauing."""
    rng = mulberry32(seed)
    lattices = []
    freq = base_freq
    for _ in range(octaves):
        n = math.ceil(freq) + 3
        lattices.append(([rng() for _ in range(n)], freq))
        freq *= lac

    def f(x):
        v, a, tot = 0.0, 1.0, 0.0
        xc = min(max(x, 0.0), 1.0)
        for vals, fr in lattices:
            p = xc * fr
            i = int(p)
            frac = p - i
            s = frac * frac * (3 - 2 * frac)
            o = vals[i] * (1 - s) + vals[i + 1] * s
            if fold:
                o = 1 - abs(2 * o - 1)
                o = o * o * (0.6 + 0.4 * o)
            v += a * o
            tot += a
            a *= gain
        return v / tot

    return f


def r1(v):
    n = round(v * 10) / 10
    if n == int(n):
        return str(int(n))
    return f"{n:.1f}"


# ---------------- ridge profile ----------------

def ridge_profile(layer, w, env):
    """y(x) in frame px: asymmetric-skewed, sharpened, normalized fbm.
    ridged layers use folded (ridged-multifractal) noise for sharp
    alpine crests, the young-orogeny look of the far Central Range."""
    f = fbm(layer["seed"], layer["freq"], fold=bool(layer.get("ridged")))

    def raw(x01):
        return f(x01 + layer["skew"] * 0.22 * (f(x01) - 0.5))

    n = 480
    samples = [raw(i / n) for i in range(n + 1)]
    lo, hi = min(samples), max(samples)
    span = (hi - lo) or 1.0

    def y(x):
        x01 = min(max(x / w, 0.0), 1.0)
        idx = x01 * n
        i = int(idx)
        frac = idx - i
        v = samples[i] * (1 - frac) + samples[min(i + 1, n)] * frac
        nv = ((v - lo) / span) ** layer["sharp"]
        if env:
            nv = min(nv * env(x01), 1.2)
        return layer["baseline"] - layer["amp"] * nv

    return y


def smooth_ridge_path(layer, w, h, env, bleed=20, drop=0):
    """Smooth ink-wash ridge: quadratic bezier chain through midpoints.
    bleed/drop extend the fill past the viewBox so scroll-driven
    translate animations never reveal a gap (svg overflow: visible,
    clipped by the scene container). Ridged layers render as a fine
    polyline (bezier smoothing would round off the sharp crests);
    soft layers keep the quadratic ink-wash chain."""
    y = ridge_profile(layer, w, env)
    if layer.get("ridged"):
        n = 110
        d = f"M{r1(-bleed)},{r1(y(-bleed))}"
        for i in range(1, n + 1):
            x = -bleed + (w + bleed * 2) * (i / n)
            d += f"L{r1(x)},{r1(y(x))}"
        d += f"L{w + bleed},{h + drop}L{-bleed},{h + drop}Z"
        return d
    n = 48
    pts = []
    for i in range(n + 1):
        x = -bleed + (w + bleed * 2) * (i / n)
        pts.append((x, y(x)))
    d = f"M{r1(pts[0][0])},{r1(pts[0][1])}"
    for i in range(1, n):
        mx = (pts[i][0] + pts[i + 1][0]) / 2
        my = (pts[i][1] + pts[i + 1][1]) / 2
        d += f"Q{r1(pts[i][0])},{r1(pts[i][1])} {r1(mx)},{r1(my)}"
    d += f"L{r1(pts[n][0])},{r1(pts[n][1])}"
    d += f"L{w + bleed},{h + drop}L{-bleed},{h + drop}Z"
    return d


def tree_points(xc, yb, th, hw, lean):
    """Conifer spire: base, shoulder, branch-tier notch, leaning tip,
    mirrored down. Reads as cryptomeria / hinoki at silhouette scale."""
    return [
        (xc - hw, yb),
        (xc - hw * 0.30 + lean * 0.45, yb - th * 0.52),
        (xc - hw * 0.44 + lean * 0.45, yb - th * 0.58),
        (xc + lean, yb - th),
        (xc + hw * 0.44 + lean * 0.45, yb - th * 0.58),
        (xc + hw * 0.30 + lean * 0.45, yb - th * 0.52),
        (xc + hw, yb),
    ]


def serrated_ridge_path(layer, w, h, env, bleed=20, drop=0):
    """Forest ridge: the base curve carries irregular tree spires; ~20%
    of steps are skipped for canopy gaps, and a slow height-multiplier
    noise makes tree heights swell in grove waves."""
    y = ridge_profile(layer, w, env)
    rng = mulberry32(layer["seed"] * 7 + 13)
    grove = fbm(layer["seed"] * 3 + 5, 5)
    step, th_base, tw = layer["serr"]
    skip = layer.get("skip", 0.2)
    pts = [(float(-bleed), y(-bleed))]
    x = -bleed + step * 0.5
    while x < w + bleed:
        if rng() < skip:
            pts.append((x, y(x)))
        else:
            h_mul = 0.55 + 0.9 * grove(x / w)
            th = th_base * h_mul * (0.45 + 0.9 * rng())
            thw = (tw * (0.7 + 0.6 * rng())) / 2
            lean = -1.5 + 5 * rng()
            pts.extend(tree_points(x, y(x), th, thw, lean))
        x += step * (0.75 + 0.5 * rng())
    pts.append((w + bleed, y(w + bleed)))
    d = f"M{r1(pts[0][0])},{r1(pts[0][1])}"
    for px, py in pts[1:]:
        d += f"L{r1(px)},{r1(py)}"
    d += f"L{w + bleed},{h + drop}L{-bleed},{h + drop}Z"
    return d


def mist_band(layer, w, grad_id, bleed=20):
    """Mist band: undulating top and bottom edges, feathered entirely by
    its own vertical gradient (transparent -> veil -> transparent).
    Zero blur, zero blend mode."""
    yc, thick = layer["yc"], layer["thick"]
    top = fbm(layer["seed"], 2.4, 3)
    bot = fbm(layer["seed"] + 17, 1.8, 3)
    n = 36
    top_pts, bot_pts = [], []
    for i in range(n + 1):
        x = -bleed + (w + bleed * 2) * (i / n)
        top_pts.append((x, yc - thick / 2 + (top(i / n) - 0.5) * thick * 0.7))
        bot_pts.append((x, yc + thick / 2 + (bot(i / n) - 0.5) * thick * 0.5))

    def chain(pts):
        d = ""
        for i in range(1, len(pts) - 1):
            mx = (pts[i][0] + pts[i + 1][0]) / 2
            my = (pts[i][1] + pts[i + 1][1]) / 2
            d += f"Q{r1(pts[i][0])},{r1(pts[i][1])} {r1(mx)},{r1(my)}"
        return d + f"L{r1(pts[-1][0])},{r1(pts[-1][1])}"

    d = f"M{r1(top_pts[0][0])},{r1(top_pts[0][1])}" + chain(top_pts)
    rev = list(reversed(bot_pts))
    d += f"L{r1(rev[0][0])},{r1(rev[0][1])}" + chain(rev) + "Z"

    y1 = yc - thick / 2 - thick * 0.35
    y2 = yc + thick / 2 + thick * 0.25
    grad = (
        f'<linearGradient id="{grad_id}" gradientUnits="userSpaceOnUse" x1="0" y1="{r1(y1)}" x2="0" y2="{r1(y2)}">'
        '<stop offset="0" class="gs-mist" stop-opacity="0"/>'
        '<stop offset="0.45" class="gs-mist"/>'
        '<stop offset="1" class="gs-mist" stop-opacity="0"/>'
        "</linearGradient>"
    )
    return d, grad


# ---------------- scene assemblers ----------------

def ridge_svg(layer, scene, w, h):
    gid = f"g-{scene['grad_ns']}-{layer['name']}"
    env = scene.get("env")
    y = ridge_profile(layer, w, env)
    min_y = min(y(x) for x in range(0, w + 1, 8))
    if layer["serr"]:
        min_y -= layer["serr"][1] * 1.3
    y2 = min(h, layer["baseline"] + 190)
    grad = (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{r1(min_y)}" x2="0" y2="{r1(y2)}">'
        f'<stop offset="0" class="gs-{layer["ramp"]}a"/>'
        f'<stop offset="1" class="gs-{layer["ramp"]}b"/>'
        "</linearGradient>"
    )
    d = (
        serrated_ridge_path(layer, w, h, env, bleed=60, drop=220)
        if layer["serr"]
        else smooth_ridge_path(layer, w, h, env, bleed=60, drop=220)
    )
    return (
        f'<svg class="{scene["prefix"]} {layer["name"]}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false">'
        f'<defs>{grad}</defs><path fill="url(#{gid})" d="{d}"/></svg>'
    )


def mist_svg(layer, scene, w, h):
    gid = f"g-{scene['grad_ns']}-{layer['name']}"
    d, grad = mist_band(layer, w, gid, bleed=60)
    return (
        f'<svg class="{scene["prefix"]} {layer["name"]} mist" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false" style="opacity:{layer["opacity"]}">'
        f'<defs>{grad}</defs><path fill="url(#{gid})" d="{d}"/></svg>'
    )


def glow_svg(layer, scene, w, h):
    gid = f"g-{scene['grad_ns']}-{layer['name']}"
    grad = (
        f'<radialGradient id="{gid}">'
        '<stop offset="0" class="gs-glow"/>'
        '<stop offset="1" class="gs-glow" stop-opacity="0"/>'
        "</radialGradient>"
    )
    return (
        f'<svg class="{scene["prefix"]} {layer["name"]} glow" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false">'
        f'<defs>{grad}</defs>'
        f'<ellipse cx="{layer["cx"]}" cy="{layer["cy"]}" rx="{layer["rx"]}" ry="{layer["ry"]}" fill="url(#{gid})"/></svg>'
    )


def layers_scene(scene):
    w, h = scene["frame"]
    out = []
    for layer in scene["layers"]:
        if layer["type"] == "mist":
            out.append(mist_svg(layer, scene, w, h))
        elif layer["type"] == "glow":
            out.append(glow_svg(layer, scene, w, h))
        else:
            out.append(ridge_svg(layer, scene, w, h))
    return "\n".join(out)


def footer_scene(scene):
    """One in-flow svg. Treelines use flat fill classes (ft-*), fireflies
    are class-driven circles (lit by CSS in dark mode)."""
    w, h = scene["frame"]
    parts, defs = [], []
    for layer in scene["layers"]:
        if layer["type"] == "mist":
            gid = f"g-{scene['grad_ns']}-{layer['name']}"
            d, grad = mist_band(layer, w, gid)
            defs.append(grad)
            parts.append(f'<path fill="url(#{gid})" opacity="{layer["opacity"]}" d="{d}"/>')
        else:
            parts.append(f'<path class="{layer["name"]}" d="{serrated_ridge_path(layer, w, h, None)}"/>')
    ff = scene.get("fireflies")
    if ff:
        rng = mulberry32(ff["seed"])
        for _ in range(ff["count"]):
            cx = r1(ff["x"][0] + rng() * (ff["x"][1] - ff["x"][0]))
            cy = r1(ff["y"][0] + rng() * (ff["y"][1] - ff["y"][0]))
            rr = r1(ff["r"][0] + rng() * (ff["r"][1] - ff["r"][0]))
            fd = r1(rng() * 5.5)
            parts.append(f'<circle class="firefly" cx="{cx}" cy="{cy}" r="{rr}" style="--fd:{fd}"/>')
    return (
        '<div class="footer-scene" aria-hidden="true">'
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false">'
        f'<defs>{"".join(defs)}</defs>{"".join(parts)}</svg></div>'
    )


# ---------------- botanical dividers ----------------

def q_point(p0, p1, p2, t):
    """Point + tangent on a quadratic bezier."""
    u = 1 - t
    return (
        u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
        2 * u * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0]),
        2 * u * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1]),
    )


def fern_scene(scene):
    w, h = scene["w"], scene["h"]
    rng = mulberry32(scene["seed"])
    p0, p1, p2 = (10, h - 6), (w * 0.42, h * 0.72), (w - 10, 7)
    paths = [
        f'<path pathLength="1" d="M{r1(p0[0])},{r1(p0[1])} Q{r1(p1[0])},{r1(p1[1])} {r1(p2[0])},{r1(p2[1])}"/>'
    ]
    n = 22
    for i in range(1, n + 1):
        t = 0.05 + 0.88 * (i / n)
        side = 1 if i % 2 == 0 else -1
        x, yv, dx, dy = q_point(p0, p1, p2, t)
        ln = math.hypot(dx, dy) or 1
        tx, ty = dx / ln, dy / ln
        px, py = -ty * side, tx * side
        L = (((1 - t) ** 1.25) * 13 + 2.5) * (0.85 + 0.3 * rng())
        sweep = 0.45 + 0.2 * rng()
        ex = x + (px + tx * sweep) * L * 0.82
        ey = yv + (py + ty * sweep) * L * 0.82
        cx = x + px * L * 0.55 + tx * L * 0.1
        cy = yv + py * L * 0.55 + ty * L * 0.1
        paths.append(f'<path pathLength="1" d="M{r1(x)},{r1(yv)} Q{r1(cx)},{r1(cy)} {r1(ex)},{r1(ey)}"/>')
    return divider_wrap(scene, paths)


def sprig_scene(scene):
    w, h = scene["w"], scene["h"]
    rng = mulberry32(scene["seed"])
    p0, p1, p2 = (8, h - 8), (w * 0.5, h * 0.55), (w - 8, 9)
    paths = [
        f'<path pathLength="1" d="M{r1(p0[0])},{r1(p0[1])} Q{r1(p1[0])},{r1(p1[1])} {r1(p2[0])},{r1(p2[1])}"/>'
    ]
    n = 11
    for i in range(1, n + 1):
        t = 0.08 + 0.84 * (i / n)
        side = 1 if i % 2 == 0 else -1
        x, yv, dx, dy = q_point(p0, p1, p2, t)
        ln = math.hypot(dx, dy) or 1
        tx, ty = dx / ln, dy / ln
        L = (((1 - t) ** 0.9) * 10 + 4) * (0.85 + 0.3 * rng())
        # branchlet sweeps forward and up, cypress-like
        ex = x + tx * L * 0.9 + -ty * side * L * 0.7
        ey = yv + ty * L * 0.9 + tx * side * L * 0.7
        cx = x + tx * L * 0.25 + -ty * side * L * 0.55
        cy = yv + ty * L * 0.25 + tx * side * L * 0.55
        paths.append(f'<path pathLength="1" d="M{r1(x)},{r1(yv)} Q{r1(cx)},{r1(cy)} {r1(ex)},{r1(ey)}"/>')
    return divider_wrap(scene, paths)


def divider_wrap(scene, paths):
    joined = "\n    ".join(paths)
    return (
        '<div class="foliage-divider" aria-hidden="true">'
        f'<svg viewBox="0 0 {scene["w"]} {scene["h"]}" width="{scene["w"]}" height="{scene["h"]}" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round">'
        f"\n    {joined}\n</svg></div>"
    )


# ---------------- build + write + inject ----------------

def build_scene(name):
    scene = SCENES[name]
    kind = scene["kind"]
    if kind == "layers":
        return layers_scene(scene)
    if kind == "footer":
        return footer_scene(scene)
    if kind == "fern":
        return fern_scene(scene)
    if kind == "sprig":
        return sprig_scene(scene)
    raise ValueError(f"unknown scene kind for {name}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    built = {}
    for name in SCENES:
        built[name] = build_scene(name)
        (OUT / f"{name}.html").write_text(built[name] + "\n", encoding="utf-8")
        print(f"{name}: {len(built[name]) / 1024:.1f} KB")

    if INJECT:
        files = {}
        for name, target_files in TARGETS.items():
            for file in target_files:
                if file not in files:
                    files[file] = (ROOT / file).read_text(encoding="utf-8")
                pattern = re.compile(
                    r"([ \t]*)<!-- scene:" + re.escape(name) + r" -->.*?<!-- /scene:" + re.escape(name) + r" -->",
                    re.DOTALL,
                )
                if not pattern.search(files[file]):
                    print(f"!! marker scene:{name} not found in {file}")
                    continue

                def repl(m, _name=name):
                    indent = m.group(1)
                    body = "\n".join(indent + line for line in built[_name].split("\n"))
                    return f"{indent}<!-- scene:{_name} -->\n{body}\n{indent}<!-- /scene:{_name} -->"

                files[file] = pattern.sub(repl, files[file], count=1)
        for file, content in files.items():
            (ROOT / file).write_text(content, encoding="utf-8", newline="\n")
            print(f"injected -> {file}")


if __name__ == "__main__":
    main()
