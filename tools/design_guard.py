#!/usr/bin/env python3
"""Static guards for the visual system described in DESIGN_SYSTEM.md.

No browser, no network, no private files: everything here reads the
committed tree, so it runs the same on a laptop and in CI.

The rules come in two shapes.

  Absolute rules are things that must never be true. A raw font stack
  outside the token block, an em dash in prose, the private research
  folder in git history. These fail on the first offence.

  Ratchets are counts that are allowed to be non-zero today because the
  code already carries that much debt, and are pinned so the number can
  only fall. Each ceiling below is a measurement of the tree on
  2026-09-22, not a guess, and every one of them is annotated with why
  the remainder is there. Lowering a ceiling is a normal part of paying
  the debt down; raising one needs a reason in the commit message.

Run:  python tools/design_guard.py
      python tools/design_guard.py --verbose    (list every offence)
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# The stylesheets that answer to the token system. specimens.css does not
# appear here on purpose: it reproduces the Veraflux product UI pixel for
# pixel, so it must carry the product's own colours and radii, not the
# portfolio's. See DESIGN_SYSTEM.md, "The one exemption".
SYSTEM_CSS = ["styles.css", "effects.css", "transitions.css"]

# Every page a reader can land on. The root-level .html files are
# redirect stubs for old URLs and carry no prose of their own.
PAGES = [
    "index.html",
    "about/index.html",
    "veraflux/index.html",
    "design/index.html",
    "design/evidence/index.html",
    "design/scan/index.html",
    "design/writing/index.html",
]

SCENES = ["assets/scenes/%s.html" % n for n in
          ("footer-valley", "home-descent", "vista-about",
           "vista-projects", "vista-veraflux")]

JS = ["assets/js/site.js", "assets/effects/ambient.js",
      "assets/effects/glass.js", "assets/effects/precip.js"]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


# --------------------------------------------------------------------------
# 1. Files that must never enter the public repository
# --------------------------------------------------------------------------

# _private/ holds the token sources, the audit log and the career fact
# file. The infrastructure resume is deliberately not published. A .tex
# source would leak the same content the PDFs are curated from.
FORBIDDEN = [
    (re.compile(r"^_private/"), "private research and token sources"),
    (re.compile(r"Infrastructure_Engineer"), "unpublished infrastructure resume"),
    (re.compile(r"\.tex$"), "resume source"),
    (re.compile(r"^_.*\.html$"), "scratch page"),
]


def check_tracked_files():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ["git ls-files unavailable, cannot verify the publish boundary"]
    bad = []
    for path in out.splitlines():
        for pattern, why in FORBIDDEN:
            if pattern.search(path):
                bad.append(f"{path} is tracked but is {why}")
    return bad


# --------------------------------------------------------------------------
# 2. Token hygiene
# --------------------------------------------------------------------------

# A declaration, allowing for the inline style="--x: 1" form used by the
# generated scenes.
DEF_RE = re.compile(r"""(?:^|[{;"'])\s*(--[A-Za-z0-9_-]+)\s*:""", re.M)
USE_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)")

# Properties read through var() that are never declared in a stylesheet,
# because something else supplies them. Each is a per-element knob with a
# var() fallback, so the page renders correctly when nothing sets it.
RUNTIME_SET = {
    # glass.js writes these two when the refraction tier is available.
    # It also reads --refract-strength with getPropertyValue rather than
    # var(), so that one never reaches this census.
    "--refract", "--refract-post",
    # per-element glass overrides, all with fallbacks in the .glass recipe
    "--g-back-inset", "--g-back-o", "--g-edge", "--g-grain",
    "--g-rim-o", "--g-rim-w", "--g-sheen", "--g-shadow",
    # precip.js and the rain layer
    "--rain-T",
    # ambient.js writes these on the marquee and the drawn timeline
    "--tile-dx", "--tile-h", "--draw",
    # per-instance stagger index and duration, set on the element in JS
    # (--d, --fd and --c are declared inline in the markup instead, so
    # they are ordinary declarations and do not belong here)
    "--i", "--dur",
}

# Declared and currently unused. This set may shrink, never grow: a new
# entry means a token was added and never wired up, or a rule that used
# one was deleted without the token following it.
KNOWN_UNUSED = {
    # palette entries kept for completeness of the named nature colours
    "--bark", "--fern", "--raised", "--sunken",
    # from the glass plan; the final recipe uses fringes instead of a
    # separate bevel pair, and the sheen instead of a specular pair
    "--bevel-cool", "--bevel-warm", "--spec-hi", "--spec-mid",
    # a type step and a space step the built pages never reached for
    "--fs-statement", "--space-20",
    # tint variants the current materials do not call
    "--glass-tint-hi", "--quiet-edge", "--rain-color",
}


def token_census():
    defs, uses = {}, {}
    for rel in SYSTEM_CSS + ["specimens.css"] + PAGES + SCENES + JS:
        text = read(rel)
        for m in DEF_RE.finditer(text):
            defs.setdefault(m.group(1), set()).add(rel)
        for m in USE_RE.finditer(text):
            uses.setdefault(m.group(1), set()).add(rel)
    return defs, uses


def check_tokens():
    defs, uses = token_census()
    bad = []
    for name in sorted(set(uses) - set(defs) - RUNTIME_SET):
        where = ", ".join(sorted(uses[name]))
        bad.append(f"var({name}) is used in {where} but never declared, "
                   f"and is not a documented runtime property")
    for name in sorted((set(defs) - set(uses)) - KNOWN_UNUSED):
        where = ", ".join(sorted(defs[name]))
        bad.append(f"{name} is declared in {where} and never used")
    # Both allowlists are pinned in the other direction too, so they
    # cannot quietly accumulate entries for things that no longer exist.
    stale = sorted(KNOWN_UNUSED - (set(defs) - set(uses)))
    if stale:
        bad.append("KNOWN_UNUSED lists tokens that are now used or gone: "
                   + ", ".join(stale) + " (remove them from the list)")
    stale = sorted(RUNTIME_SET - (set(uses) - set(defs)))
    if stale:
        bad.append("RUNTIME_SET lists properties nothing reads any more: "
                   + ", ".join(stale) + " (remove them from the list)")
    return bad


# --------------------------------------------------------------------------
# 3. Shape comes from the radius scale
# --------------------------------------------------------------------------

# Two literals in styles.css are deliberate and are matched exactly, so a
# third one cannot slip in beside them.
RADIUS_EXCEPTIONS = {
    # .link: the focus ring hugs the text, and a 2px hug reads as square
    # at every font size the links appear at
    "2px",
    # .pebble: an organic blob, which is a shape and not a corner
    "55% 45% 52% 48% / 48% 55% 45% 52%",
}
RADIUS_OK = {"inherit", "50%", "0", "999px"}


def check_radius():
    bad = []
    for rel in SYSTEM_CSS:
        text = read(rel)
        for m in re.finditer(r"border-radius:\s*([^;{}]+)", text):
            value = " ".join(m.group(1).split())
            if "var(" in value or value in RADIUS_OK:
                continue
            if value in RADIUS_EXCEPTIONS:
                continue
            bad.append(f"{rel}:{line_of(text, m.start())} literal radius "
                       f"{value!r}, use a --r-* token")
    return bad


# --------------------------------------------------------------------------
# 4. Colour lives in the token layer (ratchet)
# --------------------------------------------------------------------------

# Hex values that are stencils rather than colours: a mask gradient needs
# an opaque and a transparent end, and which colour it is has no meaning.
STENCIL = {"#000", "#fff", "#000000", "#ffffff", "#0000"}

# Measured 2026-09-22. The whole remainder is the footer and the scene
# ink: the footer sits on the painted valley rather than on --paper, so
# its text colours are picked against artwork and have no token yet.
# See DESIGN_SYSTEM.md, "Known debt".
RAW_COLOUR_CEILING = {"styles.css": 25, "effects.css": 0, "transitions.css": 0}


def raw_colour_hits(rel):
    text = read(rel)
    hits = []
    for m in re.finditer(
            r"(?:^|[{;])\s*(-?[a-z-]+)\s*:\s*([^;{}]*#[0-9a-fA-F]{3,8}[^;{}]*)",
            text, re.M):
        prop, value = m.group(1), m.group(2)
        if prop.startswith("--"):
            continue
        found = re.findall(r"#[0-9a-fA-F]{3,8}\b", value)
        if all(h.lower() in STENCIL for h in found):
            continue
        hits.append((line_of(text, m.start()), prop,
                     " ".join(value.split())[:70]))
    return hits


def check_raw_colour():
    bad = []
    for rel, ceiling in RAW_COLOUR_CEILING.items():
        hits = raw_colour_hits(rel)
        if len(hits) > ceiling:
            bad.append(f"{rel} has {len(hits)} raw colour declarations "
                       f"outside the token layer, ceiling is {ceiling}")
            for ln, prop, value in hits[ceiling:]:
                bad.append(f"    {rel}:{ln} {prop}: {value}")
        elif len(hits) < ceiling:
            bad.append(f"{rel} is down to {len(hits)} raw colour "
                       f"declarations, lower RAW_COLOUR_CEILING to match")
    return bad


# --------------------------------------------------------------------------
# 5. Specificity escape hatches (ratchet)
# --------------------------------------------------------------------------

# Measured 2026-09-22. styles.css: five, all in the reduced-motion and
# forced-colors blocks, where the rule has to beat an inline style or an
# animation. effects.css: three, same reason. transitions.css: two.
IMPORTANT_CEILING = {"styles.css": 5, "effects.css": 3, "transitions.css": 2}


def check_important():
    bad = []
    for rel, ceiling in IMPORTANT_CEILING.items():
        n = read(rel).count("!important")
        if n > ceiling:
            bad.append(f"{rel} has {n} uses of !important, ceiling is {ceiling}")
        elif n < ceiling:
            bad.append(f"{rel} is down to {n} uses of !important, "
                       f"lower IMPORTANT_CEILING to match")
    return bad


# --------------------------------------------------------------------------
# 6. Breakpoints (ratchet)
# --------------------------------------------------------------------------

# Measured 2026-09-22: 15 distinct width thresholds across the system
# stylesheets, which is drift, not a scale. Pinned so it stops growing
# while it gets consolidated. See DESIGN_SYSTEM.md, "Known debt".
BREAKPOINT_CEILING = 15


def breakpoints():
    found = set()
    for rel in SYSTEM_CSS:
        for m in re.finditer(r"\((?:min|max)-width:\s*([0-9.]+)px\)", read(rel)):
            found.add(float(m.group(1)))
    return found


def check_breakpoints():
    found = breakpoints()
    if len(found) > BREAKPOINT_CEILING:
        listing = ", ".join(f"{v:g}" for v in sorted(found))
        return [f"{len(found)} distinct width breakpoints, ceiling is "
                f"{BREAKPOINT_CEILING}: {listing}"]
    if len(found) < BREAKPOINT_CEILING:
        return [f"down to {len(found)} width breakpoints, lower "
                f"BREAKPOINT_CEILING to match"]
    return []


# --------------------------------------------------------------------------
# 7. Prose rules
# --------------------------------------------------------------------------

STRIP = re.compile(r"(?is)<(script|style|svg)\b.*?</\1>")
IDENTITY = "Software Engineer &amp; Product Designer"


def prose_of(rel):
    return STRIP.sub(" ", read(rel))


# The dash rule is a writing rule, so it covers the repository's own
# prose as well as the pages.
PROSE_FILES = PAGES + ["README.md", "DESIGN_SYSTEM.md"]


def check_prose():
    bad = []
    for rel in PROSE_FILES:
        text = prose_of(rel)
        for ch, name in (("—", "em dash"), ("–", "en dash")):
            if ch in text:
                bad.append(f"{rel} contains {text.count(ch)} {name}(s); "
                           f"this site writes without them")
    # The identity is a fixed title-case string wherever it is set as a
    # label: the page title, the Open Graph title, the hero tagline. A
    # symbol joins the two halves, and that symbol is an escaped
    # ampersand, in that order. Running prose is free to spell out "and"
    # (the meta description and the og:image alt text both do), so only
    # the symbol forms are policed here.
    variants = re.compile(
        r"(?:Software Engineer|Product Designer)\s*(?:&amp;|&(?!amp;)|/|\+)\s*"
        r"(?:Software Engineer|Product Designer)")
    for rel in PAGES:
        text = prose_of(rel)
        for m in variants.finditer(text):
            if m.group(0) != IDENTITY:
                bad.append(f"{rel}:{line_of(text, m.start())} identity reads "
                           f"{m.group(0)!r}, must be {IDENTITY!r}")
    return bad


# --------------------------------------------------------------------------
# 8. Every page carries the same head
# --------------------------------------------------------------------------

REQUIRED_HEAD = [
    ('lang="en"', "a language"),
    ('name="description"', "a description"),
    ('rel="canonical"', "a canonical URL"),
    ('name="theme-color"', "a theme colour"),
    ("favicon.svg", "the SVG favicon"),
    ("apple-touch-icon", "the touch icon"),
    ('property="og:title"', "an Open Graph title"),
    ('property="og:image"', "an Open Graph image"),
    ("twitter:card", "a Twitter card"),
    ("skip", "a skip link"),
]


def check_head():
    bad = []
    for rel in PAGES:
        text = read(rel)
        for needle, what in REQUIRED_HEAD:
            if needle not in text:
                bad.append(f"{rel} is missing {what} ({needle})")
    return bad


# --------------------------------------------------------------------------
# 9. Referenced assets exist
# --------------------------------------------------------------------------

ASSET_RE = re.compile(r'(?:href|src|content)="(/assets/[^"?#]+)"')


def check_assets():
    bad = []
    for rel in PAGES:
        for m in set(ASSET_RE.findall(read(rel))):
            if not (ROOT / m.lstrip("/")).exists():
                bad.append(f"{rel} references {m}, which is not in the tree")
    return bad


# --------------------------------------------------------------------------

CHECKS = [
    ("publish boundary", check_tracked_files),
    ("token hygiene", check_tokens),
    ("radius scale", check_radius),
    ("colour in the token layer", check_raw_colour),
    ("specificity hatches", check_important),
    ("breakpoint drift", check_breakpoints),
    ("prose rules", check_prose),
    ("page head", check_head),
    ("asset references", check_assets),
]


def main(argv):
    verbose = "--verbose" in argv
    failures = 0
    for name, fn in CHECKS:
        problems = fn()
        if problems:
            failures += len(problems)
            print(f"FAIL  {name}")
            shown = problems if verbose else problems[:12]
            for p in shown:
                print(f"        {p}")
            if len(problems) > len(shown):
                print(f"        ... and {len(problems) - len(shown)} more "
                      f"(run with --verbose)")
        else:
            print(f"ok    {name}")
    print()
    if failures:
        print(f"{failures} problem(s). See DESIGN_SYSTEM.md for the rules.")
        return 1
    print(f"{len(CHECKS)} guards pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
