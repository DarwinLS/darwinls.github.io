"""Scene generator (dev-time only, stdlib only, nothing ships).

Produces the inline-SVG scenery for the site: layered canopy-forest
ridges (billowing clump masses with emergent cryptomeria giants),
interleaved mist bands, Alishan cloud-sea fog banks (fog dial mode),
the valley-floor footer, and botanical divider line-art.

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
# canopy = billowing forest mass riding the ridge: r = clump radius
# range, inner = y-offset of a deeper interior canopy row. No canopy
# = bare smooth ridge. fog = feathered radial mist pocket (diegetic
# readability surface). env(x) optionally scales amplitude.

FRAME = (1440, 900)

SCENES = {
    # HOME: the descent composition (7 ridges + 3 mist bands)
    "home-descent": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "sd",
        "grad_ns": "home",
        "layers": [
            {"type": "ridge", "name": "sd-1", "seed": 101, "baseline": 330, "amp": 88,  "freq": 2.3, "sharp": 1.25, "skew": 0.18, "ramp": 1, "ridged": True},
            {"type": "mist",  "name": "sd-m1", "seed": 151, "yc": 468, "thick": 210, "opacity": 0.85},
            {"type": "ridge", "name": "sd-2", "seed": 102, "baseline": 400, "amp": 108, "freq": 2.7, "sharp": 1.20, "skew": 0.20, "ramp": 2, "ridged": True},
            {"type": "fogbank", "name": "sd-f1", "seed": 161, "yc": 470, "thick": 130, "opacity": 0.9,  "r": (26, 48)},
            {"type": "mist",  "name": "sd-m2", "seed": 152, "yc": 615, "thick": 150, "opacity": 0.7},
            {"type": "ridge", "name": "sd-3", "seed": 103, "baseline": 470, "amp": 110, "freq": 3.0, "sharp": 1.35, "skew": 0.22, "ramp": 3, "canopy": {"r": (7, 13)}},
            {"type": "ridge", "name": "sd-4", "seed": 104, "baseline": 550, "amp": 120, "freq": 2.8, "sharp": 1.25, "skew": 0.25, "ramp": 4, "canopy": {"r": (9, 16)}},
            {"type": "fogbank", "name": "sd-f2", "seed": 162, "yc": 610, "thick": 170, "opacity": 0.95, "r": (32, 60)},
            {"type": "mist",  "name": "sd-m3", "seed": 153, "yc": 800, "thick": 180, "opacity": 0.7},
            {"type": "ridge", "name": "sd-5", "seed": 105, "baseline": 640, "amp": 120, "freq": 3.4, "sharp": 1.20, "skew": 0.28, "ramp": 5, "canopy": {"r": (10, 17), "inner": 24}},
            {"type": "ridge", "name": "sd-6", "seed": 106, "baseline": 730, "amp": 110, "freq": 4.0, "sharp": 1.15, "skew": 0.30, "ramp": 6, "canopy": {"r": (12, 21), "inner": 30}},
            {"type": "shrine", "name": "sd-shrine", "on": "sd-7", "x": 855, "dy": 6, "s": 1.1},
            {"type": "ridge", "name": "sd-7", "seed": 107, "baseline": 830, "amp": 80,  "freq": 4.6, "sharp": 1.10, "skew": 0.30, "ramp": 7, "canopy": {"r": (15, 26), "inner": 38}},
            # The descent needs somewhere to arrive. The track travels 46vh
            # (+22 to -24) but sd-7 was the last ridgeline, at 830 of a 900
            # frame, so the bottom 280px of every screen at the end of the
            # scroll was bleed fill: measured, 31% of the viewport, flat.
            #
            # sd-f3 is folded in HERE rather than painted last. Every fog
            # bank in the stack tucks behind the ridge in front of it,
            # which is what stops it reading as a cloud with an edge; the
            # one at the bottom had nothing in front of it, so it lay over
            # the near forest and over the shrine and looked pasted on.
            # Folded, the cloud sits behind the near canopy and the shrine
            # comes back out of it. The drift moved with the job: whichever
            # bank is topmost carries it, and that is sd-f4 now.
            {"type": "fogbank", "name": "sd-f3", "seed": 163, "yc": 775, "thick": 150, "opacity": 0.9, "r": (36, 68)},
            # The valley floor. Nearer, so bigger and darker rather than
            # more of the same, and the near layer carries emergents: the
            # first attempt put a plain large-clump canopy here and it read
            # as an unidentifiable dark stripe, because a run of same-sized
            # bumps is texture, and this close the eye wants trees.
            {"type": "ridge", "name": "sd-8", "seed": 108, "baseline": 915, "amp": 66, "freq": 5.2, "sharp": 1.10, "skew": 0.30, "ramp": 8, "canopy": {"r": (19, 32), "inner": 46}},
            {"type": "mist",  "name": "sd-m4", "seed": 154, "yc": 1005, "thick": 120, "opacity": 0.5},
            {"type": "ridge", "name": "sd-9", "seed": 109, "baseline": 1055, "amp": 44, "freq": 5.2, "sharp": 1.05, "skew": 0.30, "ramp": 9, "canopy": {"r": (30, 52), "inner": 62, "emergent": (0.30, 0.95, 0.42, 2)}},
            # topmost, so this is the one that drifts
            {"type": "fogbank", "name": "sd-f4", "seed": 164, "yc": 1035, "thick": 120, "opacity": 0.85, "r": (44, 80)},
        ],
    },
    # PROJECTS: rain-veiled closer forest under a far range
    "vista-projects": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "vl",
        "grad_ns": "proj",
        "layers": [
            {"type": "ridge", "name": "vl-1", "seed": 204, "baseline": 520, "amp": 80, "freq": 1.9, "sharp": 1.5, "skew": 0.16, "ramp": 1, "ridged": True},
            {"type": "ridge", "name": "vl-2", "seed": 201, "baseline": 620, "amp": 100, "freq": 2.6, "sharp": 1.35, "skew": 0.22, "ramp": 3, "canopy": {"r": (8, 14)}},
            {"type": "fogbank", "name": "vl-f1", "seed": 261, "yc": 690, "thick": 130, "opacity": 0.9, "r": (28, 52)},
            {"type": "mist",  "name": "vl-m1", "seed": 251, "yc": 700, "thick": 135, "opacity": 0.65},
            {"type": "ridge", "name": "vl-3", "seed": 202, "baseline": 720, "amp": 110, "freq": 3.2, "sharp": 1.20, "skew": 0.26, "ramp": 5, "canopy": {"r": (12, 22), "inner": 28}},
            {"type": "ridge", "name": "vl-4", "seed": 203, "baseline": 810, "amp": 90,  "freq": 3.8, "sharp": 1.12, "skew": 0.30, "ramp": 6, "canopy": {"r": (16, 28), "inner": 38}},
            # Same runout, smaller: the vista track travels 10vh, so the
            # viewport bottom reaches frame 990 while the last ridgeline
            # sat at 810. One nearer, larger-crowned layer covers it.
            {"type": "ridge", "name": "vl-5", "seed": 205, "baseline": 975, "amp": 52, "freq": 4.6, "sharp": 1.06, "skew": 0.30, "ramp": 8, "canopy": {"r": (24, 40), "inner": 54, "emergent": (0.26, 0.90, 0.44, 2)}},
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
            {"type": "ridge", "name": "vl-1", "seed": 301, "baseline": 600, "amp": 95,  "freq": 2.2, "sharp": 1.45, "skew": 0.20, "ramp": 2},
            {"type": "ridge", "name": "vl-2", "seed": 302, "baseline": 680, "amp": 105, "freq": 2.7, "sharp": 1.30, "skew": 0.24, "ramp": 3, "canopy": {"r": (8, 14)}},
            {"type": "fogbank", "name": "vl-f1", "seed": 361, "yc": 735, "thick": 130, "opacity": 0.9, "r": (28, 52)},
            {"type": "mist",  "name": "vl-m1", "seed": 351, "yc": 760, "thick": 130, "opacity": 0.6},
            {"type": "ridge", "name": "vl-3", "seed": 303, "baseline": 760, "amp": 100, "freq": 3.2, "sharp": 1.18, "skew": 0.28, "ramp": 5, "canopy": {"r": (12, 22), "inner": 28}},
            {"type": "ridge", "name": "vl-4", "seed": 304, "baseline": 845, "amp": 80,  "freq": 3.7, "sharp": 1.12, "skew": 0.30, "ramp": 6, "canopy": {"r": (15, 26), "inner": 36}},
            # Same runout, smaller: the vista track travels 10vh, so the
            # viewport bottom reaches frame 990 while the last ridgeline
            # sat at 845. One nearer, larger-crowned layer covers it.
            {"type": "ridge", "name": "vl-5", "seed": 305, "baseline": 990, "amp": 48, "freq": 4.5, "sharp": 1.06, "skew": 0.30, "ramp": 8, "canopy": {"r": (24, 40), "inner": 54, "emergent": (0.26, 0.90, 0.44, 2)}},
        ],
    },
    # VERAFLUX: highland lake at first light. A far range and a lake
    # mist band sit high enough that the reading panes always have
    # ridgelines behind them to refract; the near forest stays low.
    "vista-veraflux": {
        "kind": "layers",
        "frame": FRAME,
        "prefix": "vl",
        "grad_ns": "vera",
        "layers": [
            {"type": "ridge", "name": "vl-1", "seed": 511, "baseline": 540, "amp": 75, "freq": 1.7, "sharp": 1.55, "skew": 0.15, "ramp": 1, "ridged": True},
            {"type": "mist",  "name": "vl-m1", "seed": 551, "yc": 620, "thick": 150, "opacity": 0.75},
            {"type": "ridge", "name": "vl-2", "seed": 512, "baseline": 650, "amp": 90, "freq": 2.3, "sharp": 1.35, "skew": 0.2, "ramp": 2},
            {"type": "ridge", "name": "vl-3", "seed": 513, "baseline": 770, "amp": 85, "freq": 3.1, "sharp": 1.22, "skew": 0.26, "ramp": 4, "canopy": {"r": (9, 16)}},
            {"type": "fogbank", "name": "vl-f1", "seed": 561, "yc": 800, "thick": 110, "opacity": 0.85, "r": (24, 44)},
            {"type": "ridge", "name": "vl-4", "seed": 514, "baseline": 862, "amp": 58, "freq": 3.9, "sharp": 1.12, "skew": 0.3, "ramp": 6, "canopy": {"r": (14, 24), "inner": 30}},
            # Same runout, smaller: the vista track travels 10vh, so the
            # viewport bottom reaches frame 990 while the last ridgeline
            # sat at 862. One nearer, larger-crowned layer covers it.
            {"type": "ridge", "name": "vl-5", "seed": 515, "baseline": 1000, "amp": 44, "freq": 4.4, "sharp": 1.06, "skew": 0.30, "ramp": 8, "canopy": {"r": (22, 38), "inner": 50, "emergent": (0.26, 0.90, 0.44, 2)}},
        ],
    },
    # FOOTER: valley floor, all pages, in-flow svg. One canopy line in
    # the same billowing language as the page scenes, over a smooth
    # treeless ridge and pooled mist.
    # FOOTER: the valley floor, all pages, in-flow svg. The floor is still
    # water: it gives the page somewhere to end, it is the one shape in the
    # whole scene that is an unbroken horizontal, and it is what the rain
    # already falling in this world lands on.
    "footer-valley": {
        "kind": "footer",
        # 260, not 180. The trees and the shore keep their old positions, so
        # the composition is unchanged; the frame simply continues far
        # enough down to cover the whole footer. It used to stop at 180
        # while the footer is 274 tall, so the nearest 94px of water - the
        # part with the copyright sitting on it - was flat colour with no
        # banding, no reflection and no ripples. Water that is nearer to
        # you shows MORE detail, not less, so that was backwards.
        "frame": (1440, 260),
        "grad_ns": "foot",
        # No layers. There used to be a treeline, a mist band and a bank
        # running the full width, and that band was opaque, as was the
        # footer's own background above the waterline. Between them they
        # hid the fixed rain layer, so the rain stopped before it reached
        # the surface it was falling on, which is the one thing the footer
        # exists to show. Land is discrete now and rain falls through every
        # gap between the pieces. Something blocking SOME of it is right.
        "layers": [],
        "land": [
            {"cx": 70, "half": 340, "rise": 72, "seed": 71},
            {"cx": 620, "half": 85, "rise": 32, "seed": 77},
            {"cx": 1375, "half": 300, "rise": 64, "seed": 83},
        ],
        # `arc` turns the waterline down at each end, uncovering the bank
        # behind it, which is what closes an expanse of water into a pond
        # instead of an ocean. Different figures per side, because a
        # symmetric parabola reads as a drawn curve; `bay` lets the line
        # wander. `pond` puts rocks and reeds along the shore, which is the
        # other half of the job: with nothing standing in water there is no
        # way to tell whether it is six metres across or six kilometres.
        "water": {"shore": 126, "wave": 3.0, "freq": 1.4, "phase": 0.7,
                  "arc": (52, 34), "bay": 6.0, "bay_fine": 2.2,
                  "bay_seed": 29, "deep": 150,
                  "reflect": 0, "band_seed": 41,
                  "veil": {"up": 20, "down": 36, "a": 0.18},
                  # `pow` crowds the rows towards the far shore; `broad` is
                  # the near field, which the perspective law would
                  # otherwise leave empty.
                  "surf": {"rows": 16, "pow": 1.6, "th": 0.32, "amp": 1.5,
                           "hi": 0.55, "a": (0.09, 0.24),
                           "seg": (0.12, 0.42), "gap": (0.03, 0.14),
                           "broad": {"rows": 7, "from": 0.26,
                                     "th": (9.0, 26.0), "a": (0.07, 0.15),
                                     "seg": (0.22, 0.62), "gap": (0.02, 0.16)}},
                  # `mid` fills the band the text sits above: reach 22
                  # holds those features at or above y=152, and the
                  # earliest text line measures y=162 at every width.
                  # leaves in the near field. The perspective law puts
                  # most of the surface banding far away, so the
                  # foreground needs something of its own for scale.
                  "lily": {"seed": 515, "drifts": 8, "from": 40,
                           "spread": 130, "r": (7.0, 19.0)},
                  "pond": {"seed": 901, "clear": (420, 1020), "rocks": 20,
                           "reach": 44, "rw": (19, 56), "moss": 0.85,
                           "reed_h": (22, 52), "reed_clumps": 9,
                           "mid": {"gap": (70, 150), "reach": 22,
                                   "rw": (11, 27), "bare": 0.40}}},
        # Rain on water is not four drops a cycle. Four drops on a surface
        # under a downpour reads as a still pond next to a rainstorm, which
        # is the incoherence being fixed here. Real rain on water is a
        # continuous stipple with the occasional larger event, so that is
        # what this draws: a dense field of small short-lived dimples for
        # the texture, and a few hero drops that arrive as a visible streak
        # and throw three rings. Drawn streaks were tried and cut: a line
        # sitting above a ripple does not read as its cause, and the only
        # thing that would is the real rain sheet synchronised to the
        # ripples, which is not worth the complexity. The rain reaching
        # the water at all is what closes the gap.
        "rain": {"cycle": 5.2, "seed": 733, "hero": 6, "stipple": 20,
                 "slant": 7.0, "x": (40, 1400)},
        "fireflies": {"seed": 691, "count": 9, "x": (70, 1380), "y": (44, 104), "r": (1.5, 2.5)},
    },
    # DIVIDERS: botanical line-art (fern fronds + a sprig)
}

# Where each scene's generated block gets injected
# (between <!-- scene:NAME --> ... <!-- /scene:NAME --> markers).
# Page backdrops (vistas, the home descent) and the footer valley are
# placed by tools/partials.py, which reads them from assets/scenes/.
TARGETS = {}

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


# Canopy clump tuning. Measured across all 14 canopy layers, the shipped
# values gave an apex-to-width ratio with a median of 0.27 and a tail to 0.43;
# reference photographs of a forested ridge at this distance sit nearer 0.05
# to 0.25, and the regularity read as styled. These are smaller and more
# frequent clumps at a lower rise: median 0.21, tail 0.36, 36% more clumps.
CLUMP = 0.80            # clump radius, as a fraction of the layer's r
ADVANCE = (1.40, 0.58)  # how far each clump advances, in radii
RISE = (0.22, 0.18)     # apex height, as a fraction of the clump's own span


def canopy_edge_d(layer, w, env, bleed, y_off=0.0, seed_off=0, r_scale=1.0):
    """Scalloped canopy top edge: overlapping clump bumps (one Q arc
    each) riding the ridge profile - a continuous billowing forest
    MASS rather than individual trees. A slow grove wave swells and
    shrinks clump size across the width. Returns a path fragment
    from M at x=-bleed to x>=w+bleed (integer coords)."""
    base = ridge_profile(layer, w, env)
    y = lambda x: base(x) + y_off
    cfg = layer["canopy"]
    r_lo, r_hi = cfg["r"]
    rng = mulberry32(layer["seed"] * 11 + 3 + seed_off)
    grove = fbm(layer["seed"] * 5 + 9, 4)
    F = lambda v: str(int(round(v)))
    em = cfg.get("emergent")   # (chance, rise, half-width, min gap) or None
    x = float(-bleed)
    d = f"M{F(x)},{F(y(x))}"
    since = 0
    while x < w + bleed:
        r = (r_lo + (r_hi - r_lo) * rng()) * r_scale * CLUMP
        r *= 0.7 + 0.7 * grove(min(max(x / w, 0.0), 1.0))
        r = max(r, 3.0)
        x2 = x + r * (ADVANCE[0] + ADVANCE[1] * rng())
        span = x2 - x
        since += 1
        if em and since >= em[3] and rng() < em[0]:
            # An emergent: one crown standing clear of the canopy around
            # it. The file has promised "emergent cryptomeria giants" since
            # it was written and never drew one, and their absence is what
            # made the NEAREST layer fail: a run of same-sized bumps reads
            # as texture at distance, which is correct, but in the
            # foreground the eye expects to resolve individual trees and
            # instead got an unidentifiable dark stripe.
            #
            # It is one clump in the same chain, not a shape laid on top:
            # narrower footprint, much greater rise, and a rounded head. A
            # separate path would read as a sticker.
            since = 0
            hw = span * em[2] * (0.8 + 0.4 * rng())
            rise = span * em[1] * (0.55 + 0.95 * rng())
            cx = x + hw
            x2 = x + hw * 2
            top = y(cx) - rise
            d += (f"Q{F(x + hw * 0.22)},{F(y(cx) - rise * 0.52)} "
                  f"{F(x + hw * 0.62)},{F(top + rise * 0.10)}"
                  f"Q{F(cx)},{F(top - rise * 0.10)} "
                  f"{F(x + hw * 1.38)},{F(top + rise * 0.10)}"
                  f"Q{F(x + hw * 1.78)},{F(y(cx) - rise * 0.52)} "
                  f"{F(x2)},{F(y(x2) + 1 + 2.0 * rng())}")
        else:
            # asymmetric clump: apex off-center, height varies widely
            # (centered same-height arcs read as bubble wrap, not canopy).
            # The rise comes from the span actually chosen, not from the
            # radius: drawn independently the two extremes can combine, and
            # the tail of that distribution is what reads as a spike.
            xm = x + span * (0.32 + 0.36 * rng())
            bump = span * (RISE[0] + RISE[1] * rng())
            d += f"Q{F(xm)},{F(y(xm) - bump)} {F(x2)},{F(y(x2) + 1 + 2.0 * rng())}"
        x = x2
    return d


def bank_edge_d(layer, w, bleed=20):
    """A wooded bank seen across water.

    Deliberately NOT the canopy generator. The page scenes are distant
    ranges, the footer is a near shoreline, and sharing the clump-arc chain
    is what made the same texture appear at the bottom of every page. Here
    the unit is a whole stand of trees, not a crown: wide soft lobes at
    irregular spacing, an order of magnitude bigger than a clump.
    """
    cfg = layer["bank"]
    lo_s, hi_s = cfg["span"]
    rise = cfg["rise"]
    y = ridge_profile(layer, w, None)
    rng = mulberry32(layer["seed"] * 17 + 5)
    F = lambda v: f"{v:.1f}"
    x = float(-bleed)
    d = f"M{F(x)},{F(y(x))}"
    while x < w + bleed:
        span = lo_s + (hi_s - lo_s) * rng()
        top = rise * (0.35 + 0.65 * rng())
        ax = x + span * (0.35 + 0.30 * rng())
        x2 = x + span
        d += f"Q{F(ax)},{F(y(ax) - top * 1.9)} {F(x2)},{F(y(x2))}"
        x = x2 - span * (0.05 + 0.20 * rng())
    return d


def canopy_ridge_path(layer, w, h, env, bleed=60, drop=380,
                      y_off=0.0, seed_off=0, r_scale=1.0):
    """Closed canopy-forest ridge fill (scalloped edge + body)."""
    d = canopy_edge_d(layer, w, env, bleed, y_off, seed_off, r_scale)
    return d + f"L{w + bleed},{h + drop}L{-bleed},{h + drop}Z"


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
    cnp = layer.get("canopy")
    if cnp:
        min_y -= cnp["r"][1] * 1.3
        if cnp.get("emergent"):
            min_y -= cnp["r"][1] * cnp["emergent"][1] * 2.2
    y2 = min(h, layer["baseline"] + 190)
    grad = (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{r1(min_y)}" x2="0" y2="{r1(y2)}">'
        f'<stop offset="0" class="gs-{layer["ramp"]}a"/>'
        f'<stop offset="1" class="gs-{layer["ramp"]}b"/>'
        "</linearGradient>"
    )
    if cnp:
        d = canopy_ridge_path(layer, w, h, env, bleed=60, drop=380)
    else:
        d = smooth_ridge_path(layer, w, h, env, bleed=60, drop=380)
    paths = f'<path fill="url(#{gid})" d="{d}"/>'
    # Interior canopy row: a second, larger-clump scallop line offset
    # below the crest, one ramp step deeper - depth INSIDE the forest
    # so near ridges read as a full canopy, not a flat fill.
    if cnp and cnp.get("inner"):
        inner_ramp = min(8, layer["ramp"] + 1)
        d2 = canopy_ridge_path(layer, w, h, env, bleed=60, drop=380,
                               y_off=cnp["inner"], seed_off=7, r_scale=1.25)
        paths += f'<path style="fill:var(--gs-{inner_ramp}a)" d="{d2}"/>'
    return (
        f'<div class="{scene["prefix"]} {layer["name"]}">'
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false">'
        f'<defs>{grad}</defs>{paths}</svg></div>'
    )


def mist_svg(layer, scene, w, h):
    gid = f"g-{scene['grad_ns']}-{layer['name']}"
    d, grad = mist_band(layer, w, gid, bleed=60)
    # Base opacity rides the inner svg so wrapper-level opacity
    # animations (choreography) multiply with it instead of fighting.
    return (
        f'<div class="{scene["prefix"]} {layer["name"]} mist">'
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false" style="opacity:{layer["opacity"]}">'
        f'<defs>{grad}</defs><path fill="url(#{gid})" d="{d}"/></svg></div>'
    )


def fogbank_svg(layer, scene, w, h):
    """Alishan cloud-sea bank: a dense fog mass pooling in a valley
    between ridge layers, so nearer peaks pierce through it.

    Cloud has no outline. The earlier version drew crowns at close to
    canopy rhythm and then revealed them with a gradient that was already
    55% opaque at the crown tips, so the sea read as white forest - the
    exact failure the old comment here warned about. Two things separate
    fog from foliage now: scale, with billows far wider and flatter than
    any clump, and edge, with the gradient starting fully transparent
    above the highest crown so the top of the bank dissolves instead of
    ending. Still zero blur and zero blend mode. Hidden by default; the
    fog dial mode fades the .fogbank wrapper in (styles.css)."""
    gid = f"g-{scene['grad_ns']}-{layer['name']}"
    yc, thick = layer["yc"], layer["thick"]
    r_lo, r_hi = layer["r"]
    bleed = 60
    rng = mulberry32(layer["seed"] * 13 + 5)
    swell = fbm(layer["seed"], 1.6, 3)
    top_y = lambda x: (yc - thick / 2
                       + (swell(min(max(x / w, 0.0), 1.0)) - 0.5) * thick * 0.5)
    F = lambda v: str(int(round(v)))
    x = float(-bleed)
    d = f"M{F(x)},{F(top_y(x))}"
    rise_max = 0.0
    while x < w + bleed:
        r = (r_lo + (r_hi - r_lo) * rng()) * 1.7
        # cloud crowns advance much wider and rise much shallower than
        # canopy clumps, so scale alone separates the two languages
        x2 = x + r * (2.0 + 1.1 * rng())
        xm = x + (x2 - x) * (0.38 + 0.24 * rng())
        bump = r * (0.30 + 0.30 * rng())
        rise_max = max(rise_max, bump)
        d += f"Q{F(xm)},{F(top_y(xm) - bump)} {F(x2)},{F(top_y(x2) + 1 + 2 * rng())}"
        x = x2
    # The bottom edge is pushed well below where the gradient dies, because
    # the gradient has to reach zero BEFORE the path ends. It did not: the
    # feather bottomed out at yc + 0.75 * thick while the path stopped as
    # high as yc + 0.3 * thick, so every bank ended on its own boundary at
    # up to 0.87 opacity. A ridge painted afterwards hides that, which is
    # why it was only ever visible on the lowest bank in the stack, where
    # it read as a cloud sliced off along a line.
    bot = fbm(layer["seed"] + 17, 1.8, 3)
    n = 36
    pts = []
    for i in range(n + 1):
        px = -bleed + (w + bleed * 2) * (i / n)
        pts.append((px, yc + thick / 2 + thick * 0.35
                    + (bot(i / n) - 0.5) * thick * 0.4))
    bottom_hi = min(y for _, y in pts)
    rev = list(reversed(pts))
    d += f"L{r1(rev[0][0])},{r1(rev[0][1])}"
    for i in range(1, len(rev) - 1):
        mx = (rev[i][0] + rev[i + 1][0]) / 2
        my = (rev[i][1] + rev[i + 1][1]) / 2
        d += f"Q{r1(rev[i][0])},{r1(rev[i][1])} {r1(mx)},{r1(my)}"
    d += f"L{r1(rev[-1][0])},{r1(rev[-1][1])}Z"
    # the feather starts above the highest crown and at zero, so no crown
    # ever shows an edge against the sky
    y1 = yc - thick / 2 - rise_max * 1.15
    # zero at the HIGHEST point of the bottom edge, so no part of that edge
    # is ever drawn and the bank can only dissolve
    y2 = bottom_hi
    grad = (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{r1(y1)}" x2="0" y2="{r1(y2)}">'
        '<stop offset="0" class="gs-mist" stop-opacity="0"/>'
        '<stop offset="0.30" class="gs-mist" stop-opacity="0.35"/>'
        '<stop offset="0.55" class="gs-mist" stop-opacity="0.92"/>'
        '<stop offset="0.78" class="gs-mist" stop-opacity="0.85"/>'
        '<stop offset="1" class="gs-mist" stop-opacity="0"/>'
        "</linearGradient>"
    )
    return (
        f'<div class="{scene["prefix"]} {layer["name"]} mist fogbank">'
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false" style="opacity:{layer["opacity"]}">'
        f'<defs>{grad}</defs><path fill="url(#{gid})" d="{d}"/></svg></div>'
    )


def fog_svg(layer, scene, w, h):
    """Feathered radial fog pocket in the scene's mist color: valley
    fog pooling among the canopy. Currently unused - kept for the
    future landmark/diegetic-elements round (fog placed intentionally
    as scenery; hero readability now comes from a hero-anchored wash
    in styles.css, not a scene layer)."""
    gid = f"g-{scene['grad_ns']}-{layer['name']}"
    grad = (
        f'<radialGradient id="{gid}">'
        '<stop offset="0" class="gs-mist"/>'
        '<stop offset="0.55" class="gs-mist" stop-opacity="0.6"/>'
        '<stop offset="1" class="gs-mist" stop-opacity="0"/>'
        "</radialGradient>"
    )
    return (
        f'<div class="{scene["prefix"]} {layer["name"]} mist">'
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false" style="opacity:{layer["opacity"]}">'
        f'<defs>{grad}</defs>'
        f'<ellipse cx="{layer["cx"]}" cy="{layer["cy"]}" rx="{layer["rx"]}" ry="{layer["ry"]}" fill="url(#{gid})"/></svg></div>'
    )


def shrine_svg(layer, scene, w, h):
    """Mountain shrine landmark: a small Japanese hall EMERGING from
    behind the canopy of the ridge named by cfg["on"] (that ridge
    paints after this layer, so its treetops occlude the stone base:
    the shrine rises out of the forest instead of floating). Gabled
    sori roof: steep at the ridge, concave sweep flattening toward
    deep eaves, tips kicked upward at the corners. Warm light in the
    door and windows via baked radial gradients riding the amber
    tokens (gs-glow halo + gs-shrineglow apertures), so light and dark
    retune it like the rest of the scene. y comes from the host
    ridge's profile at x, so the seat survives seed changes. Static:
    nothing here animates (animating a child would re-raster the whole
    fixed scene layer)."""
    host = next(l for l in scene["layers"] if l["name"] == layer["on"])
    env = scene.get("env")
    x = layer["x"]
    y = ridge_profile(host, w, env)(x) + layer.get("dy", 0)
    s = layer.get("s", 1.0)
    gid = f"g-{scene['grad_ns']}-{layer['name']}"
    halo = (
        f'<radialGradient id="{gid}-halo">'
        '<stop offset="0" class="gs-glow"/>'
        '<stop offset="1" class="gs-glow" stop-opacity="0"/>'
        "</radialGradient>"
    )
    warm = (
        f'<radialGradient id="{gid}-warm">'
        '<stop offset="0" class="gs-shrineglow"/>'
        '<stop offset="1" class="gs-shrineglow" stop-opacity="0"/>'
        "</radialGradient>"
    )
    # Local coords: origin at the crest ground line, y negative = up.
    # Tall stone base on purpose: it is the part the host ridge's
    # canopy is allowed to swallow, keeping the lit apertures clear.
    silhouette = (
        "M-46,0h92v-7h-92Z"                       # stone platform
        "M-38,-7h76v-6h-76Z"                      # plinth
        "M-46,-7h6v-32h-6Z"                       # left veranda post
        "M40,-7h6v-32h-6Z"                        # right veranda post
        "M-30,-13h60v-32h-60Z"                    # hall body (to -45)
        # Roof as ONE closed shape: sori sweeps + kicked tips on top, a
        # straight tip-to-tip fascia underneath (at -36 it overlaps the
        # wall top at -45, so the roof can never float off the body).
        # Traced LEFT first so its winding matches the h/v rectangles:
        # opposite windings cancel under the nonzero fill rule and every
        # overlap turns into a see-through hole (the old roof gap bug).
        "M0,-70Q-16,-52 -54,-42Q-59,-41 -62,-46"  # left sweep + tip kick
        "L-58,-36L58,-36"                         # straight fascia underside
        "L62,-46Q59,-41 54,-42Q16,-52 0,-70Z"     # right tip kick + sweep
        "M-2,-70h4v-7h-4Z"                        # gable finial
    )
    apertures = (
        "M-5,-13V-28Q0,-34 5,-28V-13Z"            # arched door
        "M-24,-22h6v-8h-6Z"                       # left window
        "M18,-22h6v-8h-6Z"                        # right window
    )
    return (
        f'<div class="{scene["prefix"]} {layer["name"]} glow shrine">'
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false">'
        f'<defs>{halo}{warm}</defs>'
        f'<g transform="translate({r1(x)},{r1(y)}) scale({s})">'
        f'<ellipse cx="0" cy="-30" rx="100" ry="52" fill="url(#{gid}-halo)"/>'
        # translucent under-eave shadow: the openings beside the hall
        # (any real overhang exposes background) read as shaded veranda
        # depth instead of glowing sky
        f'<path style="fill:var(--gs-8a);opacity:0.55" d="M-46,-7h92v-32h-92Z"/>'
        f'<path style="fill:var(--gs-8a)" d="{silhouette}"/>'
        f'<path style="fill:var(--amber-soft)" d="{apertures}"/>'
        f'<ellipse cx="0" cy="-24" rx="12" ry="11" fill="url(#{gid}-warm)"/>'
        f'<ellipse cx="-21" cy="-26" rx="9" ry="8" fill="url(#{gid}-warm)"/>'
        f'<ellipse cx="21" cy="-26" rx="9" ry="8" fill="url(#{gid}-warm)"/>'
        "</g></svg></div>"
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
        f'<div class="{scene["prefix"]} {layer["name"]} glow">'
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" focusable="false">'
        f'<defs>{grad}</defs>'
        f'<ellipse cx="{layer["cx"]}" cy="{layer["cy"]}" rx="{layer["rx"]}" ry="{layer["ry"]}" fill="url(#{gid})"/></svg></div>'
    )


def layers_scene(scene):
    w, h = scene["frame"]
    out = []
    for layer in scene["layers"]:
        if layer["type"] == "mist":
            out.append(mist_svg(layer, scene, w, h))
        elif layer["type"] == "fogbank":
            out.append(fogbank_svg(layer, scene, w, h))
        elif layer["type"] == "fog":
            out.append(fog_svg(layer, scene, w, h))
        elif layer["type"] == "glow":
            out.append(glow_svg(layer, scene, w, h))
        elif layer["type"] == "shrine":
            out.append(shrine_svg(layer, scene, w, h))
        else:
            out.append(ridge_svg(layer, scene, w, h))
    return "\n".join(out)




def land_parts(cfg, shore_y, lobes=(70, 170)):
    """One discrete chunk of land standing in the water, and the knots
    its top runs through.

    The footer used to carry a treeline and a bank right across its width.
    That band was opaque, and so was the footer's own background above the
    waterline, so between them they hid the fixed rain layer and the rain
    visibly stopped before it reached the surface it was falling on.
    Something blocking SOME of the rain is right, and more truthful than
    nothing blocking it; a band blocking all of it is not.

    So land is discrete. Same wide soft lobes as the old bank, so it is
    obviously the same material; it simply ends, and rain falls through
    every gap. Its base follows the waterline, so it sits IN the water
    rather than floating over it.

    The knots come back with it because the scrub along the top has to
    walk the same line. Guessing at that line puts the scrub through the
    silhouette.
    """
    cx, half, rise = cfg["cx"], cfg["half"], cfg["rise"]
    rng = mulberry32(cfg["seed"])
    x0, x1 = cx - half, cx + half
    pts, x = [], x0
    while x < x1:
        t = (x - x0) / (2 * half)
        # tapers to nothing at both ends, so it meets water rather than air
        env = (4.0 * t * (1.0 - t)) ** 0.75
        pts.append((x, shore_y(x) - rise * env * (0.62 + 0.55 * rng())))
        x += lobes[0] + (lobes[1] - lobes[0]) * rng()
    pts.append((x1, shore_y(x1)))
    d = f"M{r1(x0)},{r1(shore_y(x0))}"
    prev = (x0, shore_y(x0))
    for px, py in pts:
        mx = (prev[0] + px) / 2
        my = min(prev[1], py) - rise * 0.18
        d += f"Q{r1(mx)},{r1(my)} {r1(px)},{r1(py)}"
        prev = (px, py)
    n = 10
    for i in range(n + 1):
        bx = x1 - (x1 - x0) * (i / n)
        d += f"L{r1(bx)},{r1(shore_y(bx) + 5)}"
    return d + "Z", [(x0, shore_y(x0))] + pts


def land_mass_d(cfg, shore_y, lobes=(70, 170)):
    return land_parts(cfg, shore_y, lobes)[0]


def bank_moss_d(knots, shore_y, seed, rise=(2.5, 9.0)):
    """A ragged lip of moss along the waterline of a land mass.

    This is the answer to the shoreline reading as a drawn curve. A wavier
    line does not fix it: in every one of the pond references the water's
    edge is unfollowable because things sit on it, and moss at the edge is
    the most characteristic of those things.

    The first attempt made discrete mounds and they read as a row of round
    shrubs, because a mound built from two or three circles is a bush. In
    the photographs the moss is a continuous low lip that follows the bank
    and varies in thickness, breaking off and starting again. So this is a
    ribbon: a wandering top edge, a bottom edge dipped just into the
    water, drawn in runs with gaps between them, and tapered at both ends
    of every run as well as by the land's own envelope.
    """
    rng = mulberry32(seed)
    x0, x1 = knots[0][0], knots[-1][0]
    out = []
    x = x0 + rng() * 30
    while x < x1:
        x2 = min(x + 40 + rng() * 150, x1)
        if x2 - x > 26:
            n = max(4, int((x2 - x) / 11))
            top, bot = [], []
            for i in range(n + 1):
                px = x + (x2 - x) * i / n
                t = min(max((px - x0) / max(1e-6, x1 - x0), 0.0), 1.0)
                env = (4.0 * t * (1.0 - t)) ** 0.7
                # each run tapers to nothing at its own ends too, so a run
                # never stops on a vertical edge
                e2 = math.sin(math.pi * i / n) ** 0.55
                r = (rise[0] + (rise[1] - rise[0]) * rng()) * env * e2
                top.append((px, shore_y(px) - r))
                bot.append((px, shore_y(px) + r * 0.42 + 0.5))
            d = f"M{r1(top[0][0])},{r1(top[0][1])}"
            for i in range(1, n):
                mx = (top[i][0] + top[i + 1][0]) / 2
                my = (top[i][1] + top[i + 1][1]) / 2
                d += f"Q{r1(top[i][0])},{r1(top[i][1])} {r1(mx)},{r1(my)}"
            d += f"L{r1(top[n][0])},{r1(top[n][1])}"
            for px, py in reversed(bot):
                d += f"L{r1(px)},{r1(py)}"
            out.append(f'<path d="{d}Z"/>')
        x = x2 + 18 + rng() * 90
    return "".join(out)


def scrub_d(knots, shore_y, seed, bump=13.0, drop=3.0):
    """Clumped scrub along the top of a land mass.

    The canopy overhead is built from asymmetric clumps and the footer
    land was a bare curve, so at the same distance the two read as
    different materials: one drawn, one cut out. This walks the line the
    land runs along and emits the same kind of clump, one size smaller.

    The taper matters as much as the clumps. Without it the last bump at
    each end rises off a silhouette that has already reached the
    waterline, and stands in open water as a thin dark spike.
    """
    rng = mulberry32(seed)

    def top(x):
        for i in range(len(knots) - 1):
            a, b = knots[i], knots[i + 1]
            if a[0] <= x <= b[0]:
                u = (x - a[0]) / max(1e-6, b[0] - a[0])
                return a[1] + (b[1] - a[1]) * u + drop
        return knots[-1][1] + drop

    x0, x1 = knots[0][0], knots[-1][0]

    def env(x):
        t = min(max((x - x0) / max(1e-6, x1 - x0), 0.0), 1.0)
        return (4.0 * t * (1.0 - t)) ** 0.9

    x = x0
    d = f"M{r1(x)},{r1(shore_y(x) + 6)}L{r1(x)},{r1(top(x))}"
    while x < x1:
        r = bump * (0.55 + 1.1 * rng())
        x2 = min(x + r * (1.5 + 1.1 * rng()), x1)
        xm = x + (x2 - x) * (0.3 + 0.4 * rng())
        d += (f"Q{r1(xm)},{r1(top(xm) - r * (0.7 + 0.9 * rng()) * env(xm))} "
              f"{r1(x2)},{r1(top(x2))}")
        x = x2
    return d + f"L{r1(x1)},{r1(shore_y(x1) + 6)}Z"


def rock_d(cx, cy, rw, rh, rng, tilt=0.0, amp=2.2, tilt_k=0.55):
    """A boulder as a smooth closed lump standing on a flat base.

    The radius is a sum of three low harmonics rather than an independent
    draw per point. Per-point noise puts a kink in the contour wherever
    two consecutive draws land on opposite sides, and at 4x those kinks
    read as facets on a crystal; harmonics wander without ever cornering.
    The harmonic is faded out by sin(a) so both ends land exactly on the
    base, which also removes a short horizontal ledge that used to show at
    the waterline where the contour met the closing line.

    A negative `rh` turns the lump downwards, which is how the submerged
    half is drawn from the same function.
    """
    # sin(2a) is the lopsided term: it lifts one side and drops the
    # other, and at the old weight it could swing 0.29 of the radius,
    # which is how one rock came out shaped like a boot. The lumpy terms
    # carry the texture instead.
    ph = [rng() * math.tau for _ in range(3)]
    am = (amp * (0.035 + 0.030 * rng()), amp * (0.055 + 0.050 * rng()),
          amp * (0.030 + 0.040 * rng()))
    n = 16
    pts = []
    for i in range(n + 1):
        a = math.pi * (i / n)
        k = 1.0 + math.sin(a) * (am[0] * math.sin(a * 2 + ph[0])
                                 + am[1] * math.sin(a * 3 + ph[1])
                                 + am[2] * math.sin(a * 5 + ph[2]))
        x = cx - math.cos(a) * rw * k
        y = cy - math.sin(a) * rh * k
        pts.append((x + tilt * (1 - math.sin(a)) * rw * tilt_k, y))
    # quadratic chain through the midpoints: every knot is a control point
    # and every join lands on a midpoint, so the curve is smooth
    d = f"M{r1(pts[0][0])},{r1(pts[0][1])}"
    for i in range(1, n):
        mx = (pts[i][0] + pts[i + 1][0]) / 2
        my = (pts[i][1] + pts[i + 1][1]) / 2
        d += f"Q{r1(pts[i][0])},{r1(pts[i][1])} {r1(mx)},{r1(my)}"
    d += f"L{r1(pts[n][0])},{r1(pts[n][1])}"
    return d + f"L{r1(cx + rw)},{r1(cy)}L{r1(cx - rw)},{r1(cy)}Z"


def moss_d(cx, cy, rw, rh, rng):
    """Moss as a cushion of overlapping lobes on part of the crown.

    Reference: japanesegardenpond1 and pond1 in
    `_private/research/sample-nature/`. Moss sits on the upper surface
    and spills over one shoulder in fingers. It does not run from one
    side of a rock to the other, and its lower edge is scalloped by the
    lobes rather than drawn as a line.

    The version this replaces filled everything above a wandering line.
    That always produces a continuous edge across the whole rock, which
    the owner read as a cap and, on the bigger rocks, as a head of hair.
    Lobes leave bare stone between them and at both ends of the arc.

    Every lobe is clipped to the rock, so pushing them outward is safe
    and is what makes the moss follow the silhouette instead of floating
    inside it.
    """
    # the arc of crown it covers. Never the whole crown, and biased to
    # one side, because moss grows where the light and the damp are.
    a0 = 0.08 + 0.44 * rng()
    span = 0.22 + 0.30 * rng()
    n = 4 + int(rng() * 4)
    # lobes are sized off the SMALLER axis, or a flat rock gets lobes
    # taller than itself and the clip turns them back into a cap
    base = min(rw * 0.30, max(rh * 0.52, 2.2))
    out = []
    for i in range(n):
        t = (i + 0.5) / n
        a = math.pi * (a0 + span * t)
        rr = 0.60 + 0.46 * rng()
        px = cx - math.cos(a) * rw * rr
        py = cy - math.sin(a) * rh * rr
        lr = base * (0.62 + 0.80 * rng())
        out.append(f'<ellipse cx="{r1(px)}" cy="{r1(py)}" rx="{r1(lr)}" '
                   f'ry="{r1(lr * (0.66 + 0.46 * rng()))}"/>')
    # one finger down a flank, which is what stops the patch reading as a
    # sticker laid flat on the top
    if rng() < 0.7:
        a = math.pi * (a0 + span * (0.12 if rng() < 0.5 else 0.88))
        px = cx - math.cos(a) * rw * 1.02
        py = cy - math.sin(a) * rh * 0.34
        lr = base * (0.40 + 0.34 * rng())
        out.append(f'<ellipse cx="{r1(px)}" cy="{r1(py)}" rx="{r1(lr * 0.72)}" '
                   f'ry="{r1(lr * 1.5)}"/>')
    return "".join(out)


def rock_group(uid, cx, cy, rw, rh, rng, tilt, moss_a, ns="foot"):
    """A rock in two flat tones: body, and a moss patch on the crown.

    An earlier version gave it a large specular highlight and a dark wet
    band at the foot and came out a pale plate with a green beret, because
    everything else in this scene is a single-tone silhouette and a rock
    with modelled shading is more finished than the land behind it. Flat
    is the house style here, not a limitation, so the rock carries only
    the tones that mean something.

    The moss is clipped to the outline, so no amount of tuning can push it
    past the silhouette.
    """
    d = rock_d(cx, cy, rw, rh, rng, tilt)
    cid = f"cr{uid}"
    # A stone standing in water is darker for a hand's width above the
    # line. An earlier version drew that as a flat rect and the rock came
    # out a three-layer sandwich, because the rect's top edge is a
    # straight line across the silhouette. This is the same idea with no
    # edge at all: a gradient that is strongest at the waterline and gone
    # by a third of the way up.
    wet = (f'<rect class="pd-wet" fill="url(#g-{ns}-wet)" '
           f'x="{r1(cx - rw * 1.2)}" y="{r1(cy - rh * 0.62)}" '
           f'width="{r1(rw * 2.4)}" height="{r1(rh * 0.62 + 2)}"/>')
    if moss_a <= 0 or rw < 16 or rng() > 0.82:
        return (f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
                f'<path class="pd-rock" d="{d}"/>'
                f'<g clip-path="url(#{cid})">{wet}</g>')
    # The outline is written out twice, to draw and to clip. Storing it
    # once in <defs> and referencing it with <use> was tried and reverted:
    # <use> inside <clipPath> does clip correctly in all three engines,
    # but Firefox antialiases a <use> instance differently from the same
    # path drawn directly, so the rock edges moved by up to 9/255 in that
    # engine alone. gzip had already reduced the duplication to about
    # 0.1 KB, which is not worth a cross-engine difference.
    return (f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
            f'<path class="pd-rock" d="{d}"/>'
            f'<g clip-path="url(#{cid})">'
            f'<g class="pd-moss" opacity="{moss_a}">'
            + moss_d(cx, cy, rw, rh, rng) + f"</g>{wet}</g>")


def rock_sub_d(cx, cy, rw, rh, seed, tilt, depth):
    """The part of the rock that is under the water.

    This replaces both the wet band and the reflection, and it is what
    actually says a rock is standing IN something. An object drawn whole
    with a shape beneath it is an object on a floor; an object whose own
    mass continues past a line, in a colour the water has taken over, is
    an object in water. It also gives the waterline something to cut,
    which is the only unambiguous way to show where the surface is.

    It takes the rock's OWN seed, not one derived from it, and takes the
    depth as an argument rather than drawing it. Both matter: `rock_d`
    spends its first six draws on the three harmonic phases and their
    three amplitudes, so the same seed gives the same contour and the
    mass below is the mass above, mirrored. A different seed, or one
    extra draw taken before the call, gives a different lump pattern
    under every rock, which is what the owner saw as misalignment. The
    tilt is passed through unchanged for the same reason: a vertical
    mirror preserves x.
    """
    return rock_d(cx, cy, rw, -rh * depth, mulberry32(seed), tilt)


def blade_d(x0, base_y, h, lean, wx, head=0.0):
    cxx, cyy = x0 + lean * 0.35, base_y - h * 0.55
    tip = (x0 + lean, base_y - h)
    d = (f"M{r1(x0 - wx)},{r1(base_y)}"
         f"Q{r1(cxx - wx * 0.5)},{r1(cyy)} {r1(tip[0])},{r1(tip[1])}"
         f"Q{r1(cxx + wx * 0.5)},{r1(cyy)} {r1(x0 + wx)},{r1(base_y)}Z")
    if head > 0:
        # a seed head. Three or four of these in the scene is the whole
        # difference between grass and reeds, and reeds are what say pond.
        hw = max(1.1, wx * 1.9)
        d += (f"M{r1(tip[0] - hw)},{r1(tip[1] + head)}"
              f"Q{r1(tip[0] - hw)},{r1(tip[1] - head * 0.35)} "
              f"{r1(tip[0])},{r1(tip[1] - head * 0.45)}"
              f"Q{r1(tip[0] + hw)},{r1(tip[1] - head * 0.35)} "
              f"{r1(tip[0] + hw)},{r1(tip[1] + head)}"
              f"Q{r1(tip[0])},{r1(tip[1] + head * 0.7)} "
              f"{r1(tip[0] - hw)},{r1(tip[1] + head)}Z")
    return d


def reed_clump(cx, base_y, count, h_lo, h_hi, spread, rng, heads=0.18):
    """A clump of reeds, as (back, front, reflection).

    Vertical marks are the other half of the job: rocks give the surface
    scale, reeds stop it reading as a set of horizontal stripes. Back
    blades are shorter, thinner and a lighter green, and that one split is
    the difference between a silhouette comb and a thicket.
    """
    back, front, refl = [], [], []
    for i in range(count):
        t = (i + 0.5) / count
        x0 = cx + (t - 0.5) * spread * (0.6 + 0.8 * rng())
        h = h_lo + (h_hi - h_lo) * rng()
        lean = (t - 0.5) * 2.0 * (0.5 + 0.9 * rng()) * h * 0.32
        if rng() < 0.42:
            h *= 0.78
            back.append(blade_d(x0, base_y - 1.0, h, lean * 1.15,
                                max(0.5, h * 0.026)))
            continue
        wx = max(0.55, h * 0.032)
        front.append(blade_d(x0, base_y, h, lean, wx,
                             h * 0.11 if rng() < heads else 0.0))
        refl.append(blade_d(x0, base_y, -h * 0.30, lean * 0.5, wx * 1.25))
    return " ".join(back), " ".join(front), " ".join(refl)


def lily_d(cx, cy, rx, ry, rot):
    """One floating leaf, seen almost edge on.

    Reference: pond1 in `_private/research/sample-nature/`. The near half
    of that pond is read entirely from the leaves lying on it: they are
    what gives the surface a scale and stops the foreground being a plane
    of colour, which is exactly the weakness left in this footer.

    The notch is the whole silhouette. Without it a lily pad is an
    ellipse, and an ellipse on water is a stone.
    """
    if rot is None:
        # the notch is facing away from the viewer, so it is not in view
        return (f"M{r1(cx - rx)},{r1(cy)}A{r1(rx)},{r1(ry)} 0 1 1 "
                f"{r1(cx + rx)},{r1(cy)}A{r1(rx)},{r1(ry)} 0 1 1 "
                f"{r1(cx - rx)},{r1(cy)}Z")
    # A notch cut to the centre is a spike on a shape this squashed: the
    # pad is five or six times wider than it is tall, so anything radial
    # comes out as a dart. It is a shallow bite instead, and only ever on
    # the near edge, which is the only edge whose notch you could see.
    g = 0.46
    x1, y1 = cx + rx * math.cos(rot - g), cy + ry * math.sin(rot - g)
    x2, y2 = cx + rx * math.cos(rot + g), cy + ry * math.sin(rot + g)
    ax, ay = cx + rx * math.cos(rot) * 0.42, cy + ry * math.sin(rot) * 0.42
    return (f"M{r1(x1)},{r1(y1)}A{r1(rx)},{r1(ry)} 0 1 1 {r1(x2)},{r1(y2)}"
            f"L{r1(ax)},{r1(ay)}Z")


def lilies(cfg, w, floor, shore, clear):
    """Leaves in the near field, kept out of the band the text sits in.

    They flatten and widen towards the viewer, because the surface is
    being seen at a shallower and shallower angle, and they come in drifts
    rather than evenly, because one evenly spaced row of them reads as a
    pattern rather than as plants.
    """
    rng = mulberry32(cfg["seed"])
    lo, hi = clear
    out = []
    for _ in range(cfg["drifts"]):
        # a drift centre, always outside the text band
        dx = (30 + rng() * (lo - 110)) if rng() < 0.5 else (hi + 60 + rng() * (w - hi - 110))
        dy = shore + cfg["from"] + rng() * (floor - shore - cfg["from"] - 8)
        for _ in range(2 + int(rng() * 3.4)):
            cx = dx + (rng() - 0.5) * cfg["spread"]
            cy = dy + (rng() - 0.5) * cfg["spread"] * 0.32
            if lo - 30 < cx < hi + 30 or not (0 < cx < w):
                continue
            t = (cy - shore) / max(1e-6, floor - shore)     # 0 far, 1 near
            rx = cfg["r"][0] + (cfg["r"][1] - cfg["r"][0]) * (0.35 + 0.65 * t) * (0.7 + 0.6 * rng())
            # about half have their notch turned away and read as whole
            rot = (math.pi * (0.24 + 0.52 * rng())) if rng() < 0.55 else None
            ry = rx * (0.16 + 0.13 * (1 - t))
            out.append(f'<path d="{lily_d(cx, cy, rx, ry, rot)}"/>')
    return f'<g class="pd-lily">{"".join(out)}</g>' if out else ""


def shallow_d(cx, cy, rx, ry, ns):
    """A soft patch of shallower water under something standing in it.

    An object and the surface it stands in have to share something or the
    object is a sticker. This is what they share, and it is also what
    makes a free-standing reed clump plausible, since a reed can only grow
    where it can reach the bottom. Rocks do not get one: under a rock it
    reads as a dark halo, and under a land mass it stacks with that mass's
    own reflection into a blotch.
    """
    return (f'<ellipse cx="{r1(cx)}" cy="{r1(cy)}" rx="{r1(rx)}" '
            f'ry="{r1(ry)}" fill="url(#g-{ns}-shal)"/>')


def pond_features(cfg, shore_y, w, h, ns):
    """Rocks and reeds along the shore, returned as (under, over).

    `under` belongs inside the water clip and before the surface banding,
    so the bands cross the submerged shapes: surface texture passing over
    a reflection is what fixes the reflection to the surface rather than
    floating it above one. `over` belongs after the clip closes.

    The footer read as an ocean: an unbroken horizontal plane, edge to
    edge, with a near-straight shoreline and nothing standing in it. The
    waterline's own `arc` answers the first two. This answers the third,
    which is scale: with nothing in the water there is no way to tell
    whether it is six metres across or six kilometres.
    """
    rng = mulberry32(cfg.get("seed", 901))
    lo, hi = cfg["clear"]
    left, right = [], []
    for side, start, stop, bag in ((1, 30.0, lo - 40, left),
                                   (-1, w - 30.0, hi + 40, right)):
        x = start
        while (x - stop) * side < 0:
            # rocks come in groups, but the step has to clear the widest
            # radius or a group silhouettes into a single lump. The bound
            # is checked inside the group too: without it a group starting
            # near the end of a walk carried rocks hundreds of px past it,
            # into the band the footer text sits in.
            for _ in range(1 + int(rng() * 2.6)):
                if (x - stop) * side >= 0:
                    break
                bag.append(x)
                x += side * (34 + rng() * 46)
            x += side * (70 + rng() * 130)
    # interleaved, so the count cap cannot spend itself on one shore
    spots = []
    for i in range(max(len(left), len(right))):
        if i < len(left):
            spots.append(left[i])
        if i < len(right):
            spots.append(right[i])
    spots = spots[:cfg["rocks"]]

    # The middle. `clear` kept everything out of it so nothing would sit
    # behind the footer text, which was right as far as it went and had
    # two costs: at 390px the svg is xMidYMax slice at scale 0.5, so the
    # viewport sees scene x 330..1110 and the whole pond is off-screen;
    # and even at 1440 the two shores face each other across a 600px gap.
    # Measured in scene units at 390/768/1024/1440/1920, the earliest
    # footer text starts at y=162 and the waterline is at y=126, so a
    # feature held above about y=156 is clear of text at every width.
    mid, mc = [], cfg.get("mid")
    if mc:
        x = lo + 10 + rng() * 60
        while x < hi - 10:
            mid.append(x)
            x += mc["gap"][0] + rng() * (mc["gap"][1] - mc["gap"][0])
    midset = set(mid)

    rocks, reeds = [], []
    for cx in spots + mid:
        far = cx in midset
        u = rng()
        cy = shore_y(cx) + (mc["reach"] if far else cfg["reach"]) * (u ** 1.4) + 2
        # most rocks small and a few large, which is what a shoreline
        # looks like; a flat pick made them all the same mid size
        rwr = mc["rw"] if far else cfg["rw"]
        rw = rwr[0] + (rwr[1] - rwr[0]) * (rng() ** 1.15)
        # height is capped twice: as a fraction of the width, because a
        # rock 0.69 of its own width tall reads as a boulder rather than
        # as a stone at a pond edge, and absolutely, because a big rw and
        # a high draw together put one rock above the land behind it
        rh = min(rw * (0.42 + 0.52 * rng()), 32.0) * (1.0 - 0.38 * u)
        if far and rng() < mc["bare"]:
            # part of the middle band is grass only, or it reads as a line
            # of stepping stones laid across the pond
            reeds.append((cx, cy + 1, 3 + int(rng() * 4), 10 + rng() * 14, False))
            continue
        rocks.append((cx, cy, rw, rh, (rng() - 0.5) * 0.8,
                      0.5 + 0.25 * rng()))
        if rng() < (0.45 if far else 0.6):
            reeds.append((cx + rw * (1.1 + rng() * 0.9), cy + 1,
                          4 + int(rng() * 5), 14 + rng() * 16, True))
    for _ in range(cfg["reed_clumps"]):
        cx = 30 + rng() * (w - 60)
        if lo - 40 < cx < hi + 40:
            continue
        reeds.append((cx, shore_y(cx) + 2 + rng() * cfg["reach"] * 0.45,
                      4 + int(rng() * 6), 12 + rng() * 18, False))

    under, back, front = [], [], []
    for cx, by, n, spread, anchored in reeds:
        if not anchored:
            under.append(shallow_d(cx, by + 2, spread * 2.6, spread * 0.62, ns))
    sub = []
    for cx, cy, rw, rh, tilt, depth in rocks:
        if cy > shore_y(cx) + 1.5:
            sub.append('<path d="%s"/>' % rock_sub_d(
                cx, cy, rw, rh, int(cx) * 13 + 1, tilt, depth))
    if sub:
        under.append(f'<g fill="url(#g-{ns}-sub)">' + "".join(sub) + "</g>")
    rrefl = []
    for cx, by, n, spread, anchored in reeds:
        b, f, rf = reed_clump(cx, by, n, cfg["reed_h"][0], cfg["reed_h"][1],
                              spread, mulberry32(int(cx) * 7 + 3))
        back.append(b)
        front.append(f)
        rrefl.append(rf)
    if any(rrefl):
        under.append(f'<g fill="url(#g-{ns}-rrefl)">'
                     + "".join(f'<path d="{d}"/>' for d in rrefl if d) + "</g>")

    # back blades first, so the stone occludes some of the grass. With
    # every blade in front of every rock the two read as two overlays;
    # interleaved they read as one bank.
    over = ['<g class="pd-reed-back">'
            + "".join(f'<path d="{d}"/>' for d in back if d) + "</g>"]
    for i, (cx, cy, rw, rh, tilt, depth) in enumerate(rocks):
        over.append(rock_group(f"{ns}{i}", cx, cy, rw, rh,
                               mulberry32(int(cx) * 13 + 1), tilt,
                               cfg.get("moss", 0.85), ns))
    over.append('<g class="pd-reed">'
                + "".join(f'<path d="{d}"/>' for d in front if d) + "</g>")
    return "".join(under), "".join(over)


def lens_d(x0, x1, y, th):
    """A streak that tapers to nothing at both ends.

    The shape matters more than the fill. A rectangle ends on a vertical
    edge, and that edge is what makes a band read as a ruled line; a lens
    has no end to see. With a vertical fade as well it has no hard
    boundary anywhere, which is the only way a mark this size can sit on
    water without becoming a stripe.
    """
    xm = (x0 + x1) / 2
    return (f"M{r1(x0)},{r1(y)}Q{r1(xm)},{r1(y - th)} {r1(x1)},{r1(y)}"
            f"Q{r1(xm)},{r1(y + th)} {r1(x0)},{r1(y)}Z")


def surface_bands(cfg, shore, floor, w, seed, ns):
    """Reflected sky on a still surface, in perspective.

    Rows are placed on t**pow, so they crowd towards the far shore and
    open out towards the viewer. That one curve is what turns a flat fill
    into a plane you are looking across; evenly spaced rows read as a
    wall. Thickness follows the local row spacing for the same reason, and
    no row runs the full width, because an unbroken horizontal line across
    1440px is the strongest ocean cue there is.
    """
    rng = mulberry32(seed)
    span = floor - shore
    n, p = cfg["rows"], cfg["pow"]
    # Emitted in generation order, one paint per path, on purpose.
    # Grouping them by tone to hoist the shared `fill` off 73 paths was
    # tried and reverted: a group collects paths that were not adjacent,
    # which reorders semi-transparent overlapping shapes, and with
    # source-over compositing order changes the result. Measured against a
    # deterministic capture it moved the water by up to 9/255, in the band
    # the footer text sits in, and gzip had already reduced the repeated
    # attribute to about 0.1 KB. Not a trade worth making.
    out = []

    def add(g, a, d):
        out.append(f'<path fill="url(#g-{ns}-{g})" fill-opacity="{a:.3f}" '
                   f'd="{d}"/>')

    for i in range(n):
        t = (i + 0.6) / n
        y0 = shore + span * (t ** p)
        ds = span * p * (t ** (p - 1)) / n          # local row spacing
        th = max(0.9, ds * cfg["th"] * (0.55 + 0.9 * rng()))
        amp = cfg["amp"] * (0.4 + 1.2 * rng())
        freq = 0.8 + 1.4 * rng()
        phase = rng() * math.tau
        g = "bhi" if rng() < cfg["hi"] else "blo"
        a = cfg["a"][0] + (cfg["a"][1] - cfg["a"][0]) * rng()
        x = -30 + rng() * 140
        while x < w + 10:
            seg = w * (cfg["seg"][0] + (cfg["seg"][1] - cfg["seg"][0]) * rng())
            x2 = min(x + seg, w + 30)
            if x2 - x > 60:
                y = y0 + amp * math.sin(x / w * math.tau * freq + phase)
                add(g, a, lens_d(x, x2, y, th))
            x = x2 + w * (cfg["gap"][0] + (cfg["gap"][1] - cfg["gap"][0]) * rng())

    # The near field, in a separate much lazier pass. Replacing ruled
    # lines with perspective streaks fixed the stripes and took the near
    # field's structure with it, because the perspective law puts most of
    # the marks far away. Near water is not emptier than far water, it is
    # lazier: the shapes are much bigger and much fainter.
    bd = cfg.get("broad")
    if bd:
        for i in range(bd["rows"]):
            t = bd["from"] + (1.02 - bd["from"]) * ((i + 0.5) / bd["rows"])
            y0 = shore + span * t
            th = bd["th"][0] + (bd["th"][1] - bd["th"][0]) * rng()
            g = "bhi" if rng() < cfg["hi"] else "blo"
            a = bd["a"][0] + (bd["a"][1] - bd["a"][0]) * rng()
            x = -w * (0.1 + 0.3 * rng())
            while x < w + 10:
                seg = w * (bd["seg"][0] + (bd["seg"][1] - bd["seg"][0]) * rng())
                x2 = min(x + seg, w + 60)
                if x2 - x > 120:
                    yy = y0 + (rng() - 0.5) * th * 0.8
                    add(g, a, lens_d(x, x2, yy, th))
                x = x2 + w * (bd["gap"][0] + (bd["gap"][1] - bd["gap"][0]) * rng())
    return "".join(out)


def shore_fn(wat, w):
    """The waterline.

    `arc` turns it down at each end, uncovering the bank behind it, which
    is what closes an expanse of water into a pond instead of an ocean. It
    needs no new shape, so nothing new can be clipped by the bottom of the
    svg, which is how two earlier attempts failed. A squared falloff
    reached too far in and thickened the bank across most of the width; the
    fourth power keeps the middle open. The two sides differ because a
    symmetric parabola reads as a drawn curve rather than as a shore.

    The land masses have to stand on exactly the line the water is drawn
    to, so both read it from here.
    """
    shore, wave = wat["shore"], wat["wave"]
    arc_l, arc_r = wat.get("arc", (0.0, 0.0))
    bay = fbm(wat.get("bay_seed", 29), 2.6, 3)
    bay_a = wat.get("bay", 0.0)
    # a second, finer octave. One low fbm at this amplitude over 1440px is
    # very nearly a straight line, which is half of why the edge read as
    # drawn; the other half is answered by what sits on it.
    fine = fbm(wat.get("bay_seed", 29) + 7, 8.5, 2)
    fine_a = wat.get("bay_fine", 0.0)

    def sy(x):
        u = min(max(x / w, 0.0), 1.0)
        v = (arc_l * max(0.0, 1.0 - 2.0 * u) ** 4
             + arc_r * max(0.0, 2.0 * u - 1.0) ** 4)
        return (shore - wave * math.sin(x / w * math.tau * wat["freq"] + wat["phase"])
                + v + bay_a * (bay(u) - 0.5) * 2.0
                + fine_a * (fine(u) - 0.5) * 2.0)
    return sy


def water_paths(wat, w, h, ns, bleed=20, cls_water="ft-water",
                cls_refl="ft-refl", rain=None):
    """A still water surface: the plane, what stands in it, its banding,
    and any rain sites landing on it.

    Water reads from the banding first: a still surface is never one flat
    tone, and low contrast streaks of reflected sky are what make it a
    surface even between drops. But a streak with a hard edge, or one that
    runs the full width, or a row of them at even spacing, stops being
    water: it becomes a ruled line on a wall. `surface_bands` answers all
    three.
    """
    defs, parts = [], []
    shore = wat["shore"]
    sy = shore_fn(wat, w)

    n = 40
    pts = [(-bleed + (w + bleed * 2) * i / n, 0.0) for i in range(n + 1)]
    pts = [(px, sy(px)) for px, _ in pts]

    def chain(to_y):
        d = f"M{r1(pts[0][0])},{r1(pts[0][1])}"
        for i in range(1, len(pts) - 1):
            mx = (pts[i][0] + pts[i + 1][0]) / 2
            my = (pts[i][1] + pts[i + 1][1]) / 2
            d += f"Q{r1(pts[i][0])},{r1(pts[i][1])} {r1(mx)},{r1(my)}"
        return (d + f"L{r1(pts[-1][0])},{r1(pts[-1][1])}"
                f"L{w + bleed},{r1(to_y)}L{-bleed},{r1(to_y)}Z")

    wg, rg = f"g-{ns}-water", f"g-{ns}-refl"
    defs.append(
        f'<linearGradient id="{wg}" gradientUnits="userSpaceOnUse" x1="0" '
        f'y1="{r1(shore - 8)}" x2="0" y2="{r1(wat.get("deep", h))}">'
        '<stop offset="0" class="gs-water-a"/><stop offset="1" class="gs-water-b"/>'
        "</linearGradient>"
        f'<linearGradient id="{rg}" gradientUnits="userSpaceOnUse" x1="0" '
        f'y1="{r1(shore)}" x2="0" y2="{r1(shore + wat["reflect"])}">'
        f'<stop offset="0" class="gs-water-r" stop-opacity="{wat.get("refl_a", 0.34)}"/>'
        f'<stop offset="0.45" class="gs-water-r" stop-opacity="{wat.get("refl_a", 0.34) * 0.45:.2f}"/>'
        '<stop offset="1" class="gs-water-r" stop-opacity="0"/>'
        "</linearGradient>"
        # objectBoundingBox units, so ONE def per tone fades every lens
        # whatever its size, and one more fades every submerged mass.
        # A hard bottom edge on either is what reads as a ruled line or a
        # saucer.
        + "".join(
            f'<linearGradient id="g-{ns}-{k}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" class="gs-{k}" stop-opacity="0"/>'
            f'<stop offset="0.5" class="gs-{k}" stop-opacity="1"/>'
            f'<stop offset="1" class="gs-{k}" stop-opacity="0"/>'
            "</linearGradient>" for k in ("bhi", "blo"))
        + "".join(
            f'<linearGradient id="g-{ns}-{k}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" class="gs-{k}" stop-opacity="{a0}"/>'
            f'<stop offset="0.55" class="gs-{k}" stop-opacity="{a1}"/>'
            f'<stop offset="1" class="gs-{k}" stop-opacity="0"/>'
            "</linearGradient>"
            for k, a0, a1 in (("sub", 0.95, 0.45), ("rrefl", 0.30, 0.12)))
        + f'<linearGradient id="g-{ns}-wet" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" class="gs-wet" stop-opacity="0"/>'
        '<stop offset="0.55" class="gs-wet" stop-opacity="0.34"/>'
        '<stop offset="1" class="gs-wet" stop-opacity="0.72"/>'
        "</linearGradient>"
        + f'<radialGradient id="g-{ns}-shal">'
        '<stop offset="0" class="gs-shal" stop-opacity="0.40"/>'
        '<stop offset="0.55" class="gs-shal" stop-opacity="0.18"/>'
        '<stop offset="1" class="gs-shal" stop-opacity="0"/>'
        "</radialGradient>")
    # Everything that lives ON the surface has to be clipped to it. The
    # bands, the shoreline veil and the bank's reflection are all drawn as
    # full-width horizontal shapes, which was fine while the waterline ran
    # level; now that it turns down at the ends they ran straight across
    # the land there, and a lake's banding over a bank reads as a mistake
    # rather than as a surface.
    water_d = chain(wat.get("floor", h))
    clip = f"c-{ns}-water"
    defs.append(f'<clipPath id="{clip}"><path d="{water_d}"/></clipPath>')
    parts.append(f'<path class="{cls_water}" fill="url(#{wg})" d="{water_d}"/>')
    parts.append(f'<g clip-path="url(#{clip})">')

    # What stands in the water goes in first, so the banding crosses it.
    under, over = "", ""
    if wat.get("pond"):
        under, over = pond_features(wat["pond"], sy, w, h, ns)
    parts.append(under)

    lil = wat.get("lily")
    if lil and wat.get("pond"):
        parts.append(lilies(lil, w, wat.get("floor", h), shore,
                            wat["pond"]["clear"]))

    surf = wat.get("surf")
    if surf:
        parts.append(surface_bands(surf, shore, wat.get("floor", h), w,
                                   wat.get("band_seed", 41), ns))

    # A full-width reflection band reflected a full-width bank. There is no
    # such bank now, and the band was darkening the water exactly where the
    # footer text sits, which cost about a point of contrast. Each land
    # mass and each rock reflects itself instead, which is also what a
    # reflection is.
    if wat.get("reflect"):
        parts.append(f'<path class="{cls_refl}" fill="url(#{rg})" d="{chain(shore + wat["reflect"])}"/>')

    # haze lying on the shoreline. Every other join in this scene is
    # softened by mist; the waterline was the one hard edge, which is what
    # made the bank read as a slab laid on top of a surface instead of a
    # shore running into it.
    veil = wat.get("veil")
    if veil:
        vg = f"g-{ns}-veil"
        defs.append(
            f'<linearGradient id="{vg}" gradientUnits="userSpaceOnUse" x1="0" '
            f'y1="{r1(shore - veil["up"])}" x2="0" y2="{r1(shore + veil["down"])}">'
            '<stop offset="0" class="gs-mist" stop-opacity="0"/>'
            f'<stop offset="0.42" class="gs-mist" stop-opacity="{veil["a"]}"/>'
            '<stop offset="1" class="gs-mist" stop-opacity="0"/>'
            "</linearGradient>")
        parts.append(f'<path fill="url(#{vg})" d="'
                     f'M{-bleed},{r1(shore - veil["up"])}'
                     f'L{w + bleed},{r1(shore - veil["up"])}'
                     f'L{w + bleed},{r1(shore + veil["down"])}'
                     f'L{-bleed},{r1(shore + veil["down"])}Z"/>')
    parts.append("</g>")

    if rain:
        parts += rain_on_water(rain, w, wat.get("floor", h), sy)
    parts.append(wat.get("_bank", ""))
    parts.append(over)
    return defs, parts


def rain_on_water(rain, w, floor, sy):
    """Rain landing on the surface.

    The old version placed four drops on a 5.2s cycle. Under a downpour
    that reads as a still pond beside a rainstorm: the density of the
    impacts has to agree with the density of the rain, or the surface
    looks like it is in different weather from the sky.

    Answering it with four hundred expanding rings would be both noisy and
    expensive, and it is not what rain on water looks like anyway. What it
    looks like is a continuous fine stipple, out of which a few larger
    events resolve. So there are two populations here:

      stipple  many small dimples with one short ring, low contrast,
               scattered over the whole surface and spread evenly through
               the cycle. This is the texture, and it is what makes the
               water look rained-on between events.
      hero     a few full drops: a falling streak slanted to match the
               near sheet of the background rain, then the dimple, then
               three rings. The streak is the part that was missing. The
               footer occludes the background rain, so previously the
               drops had no visible cause - they simply appeared.

    Every timing is derived from one seeded stream, so the field is
    irregular but reproducible.
    """
    rng = mulberry32(rain.get("seed", 733))
    T = rain["cycle"]
    x0, x1 = rain.get("x", (40, w - 40))
    out = []

    def site(cx, cy, delay, cls, rings, k):
        g = [f'<g class="rain-site {cls}" style="--d:{delay:.2f}s" '
             f'transform="translate({r1(cx)},{r1(cy)})">']
        g.append(f'<ellipse class="rain-dimple" rx="{r1(2.6 * k)}" ry="{r1(0.55 * k)}"/>')
        # each ring is a wave with two faces: a lit crest and the shadow
        # behind it. One hairline circle is a diagram of a ripple.
        for i2 in range(1, rings + 1):
            g.append(f'<g class="rain-ring r{i2}">'
                     f'<ellipse class="rr-lo" cy="{r1(0.55 * k)}" rx="{r1(3 * k)}" ry="{r1(0.62 * k)}"/>'
                     f'<ellipse class="rr-hi" rx="{r1(3 * k)}" ry="{r1(0.62 * k)}"/></g>')
        g.append("</g>")
        out.append("".join(g))

    # stipple first, so a hero's rings always draw over the small fry
    n_st = rain.get("stipple", 20)
    for i in range(n_st):
        cx = x0 + (x1 - x0) * rng()
        top = sy(cx) + 4
        # spread over the whole surface. A rng() ** 0.7 weighting was
        # meant to favour the near half and instead pushed almost the
        # whole field into the bottom third, leaving the water by the
        # shore still. Depth is carried by SIZE instead, which is the
        # honest cue: far impacts are small, near ones are large.
        u = rng()
        cy = top + (floor - top - 3) * u
        site(cx, cy, (i + rng()) * T / n_st, "is-stipple", 1,
             0.45 + 0.45 * u)

    n_h = rain.get("hero", 6)
    for i in range(n_h):
        cx = x0 + (x1 - x0) * ((i + 0.15 + 0.7 * rng()) / n_h)
        top = sy(cx) + 8
        u = 0.12 + 0.84 * rng()
        cy = top + (floor - top - 6) * u
        site(cx, cy, (i + 0.3 * rng()) * T / n_h, "is-hero", 3,
             0.85 + 0.5 * u)
    return out


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
            if layer.get("bank"):
                d = bank_edge_d(layer, w) + f"L{w + 20},{h}L{-20},{h}Z"
            elif layer.get("canopy"):
                d = canopy_ridge_path(layer, w, h, None, bleed=20, drop=0)
            else:
                d = smooth_ridge_path(layer, w, h, None)
            parts.append(f'<path class="{layer["name"]}" d="{d}"/>')
    wat = scene.get("water")
    bank = []
    if wat and scene.get("land"):
        # drawn before the water, so the water's own edge closes over the
        # base of each mass and they sit IN it rather than on top of it
        sy0 = shore_fn(wat, w)
        for m in scene["land"]:
            d, knots = land_parts(m, sy0)
            parts.append(f'<path class="ft-land" d="{d}"/>')
            # scrub along the top, so the land is not a bare cut-out under
            # a canopy that is full of clumped crown texture
            parts.append('<path class="ft-scrub" d="%s"/>'
                         % scrub_d(knots, sy0, m["seed"] + 5))
            # and moss on its waterline, handed to water_paths so it is
            # painted after the surface rather than under it
            bank.append(bank_moss_d(knots, sy0, m["seed"] + 11))
        land_refl = "".join(
            f'<path d="{land_mass_d({**m, "rise": -m["rise"] * 0.42}, sy0)}"/>'
            for m in scene["land"])
        parts.append(f'<g class="ft-land-refl">{land_refl}</g>')
    if wat:
        if bank:
            wat = {**wat, "_bank": '<g class="ft-bank-moss">'
                   + "".join(bank) + "</g>"}
        d2, p2 = water_paths(wat, w, h, scene["grad_ns"],
                             rain=scene.get("rain"))
        defs += d2
        parts += p2

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
