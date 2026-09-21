"""Build the site mark: favicon.svg, favicon.ico, apple-touch-icon.png.

THE MARK

A window onto the site's own landscape: warm sky over cool layered
ridges, with the amber arriving as rim light along the near crest. Every
colour is sampled from the running site rather than recomputed, so the
mark and the scenery cannot drift apart.

Why this and not a pictogram. The previous marks failed for reasons that
only showed up at the size they are actually seen:

  - an amber alpine peak on a tile is the generic image-placeholder
    glyph at 16px, and it painted terrain in the colour the site uses
    for ink.
  - a single blade reads as a balloon. One flat silhouette has to be
    recognisable by outline alone, and a leaf is not.

Both were pictograms of a thing in the scenery. This is the scenery. The
site's subject is layered depth read through haze, and a downscale of the
real hero proves that subject survives 16px as a VALUE PROGRESSION
(warm sky, pale haze, saturated green) even after every individual ridge
has dissolved. So the mark keeps the progression and adds one crisp
crest to act as the figure.

The crest carries a secondary shoulder on purpose. A single smooth dome
is any mountain logo; the shoulder makes the silhouette a landmark, and
it is what survives as the picture simplifies.

WHAT THE CREST RESEARCH CHANGED, AND WHAT IT DID NOT

Two canonical Japanese crest families are this exact composition: 遠山
(tooyama, "distant mountains", the named family for receding layered
ridges) and 山に霞 (yama ni kasumi, "mountain over mist"). JAANUS
documents 霞床 (kasumidoko), an alcove whose staggered shelves read as
cloud crossing a Mt. Fuji scroll. So layered ridge plus mist over a
paper ground is an attested composition.

Canonical kasumi is hard-edged with rounded heads and OCCLUDES what sits
behind it. That was prototyped and rejected: in painting those bands lie
across a detailed scene and read as air, but this landscape is already
reduced to three flat planes, so hard bars just add more flat bars and
read as stripes. The site's own mist_band() feathers by gradient, and
internal consistency wins. Recorded as tested, not overlooked.

Kept from the research:
  - one charge plus one enclosure. No pond, no shoji frame, no second
    motif. Combining unrelated charges is the documented failure mode,
    and prototyping had already killed both on sight.
  - NO RAYS behind the ridge, ever. A rayed disc reads as the Rising Sun
    flag, which is a live branding hazard. The amber is rim light on a
    crest, never a source with rays.
  - the mark must survive monochrome and inversion, because colour is
    never load-bearing. Verified: the crest reads as a landform filled
    black on white and white on black.

SIZES

An .ico carries an independent bitmap per size, so 16px is not a
squeezed copy of 32px. It drops the mid plane and the haze and widens
the rim, which measurably separates the two planes at that size.
"""
import pathlib
import struct

# Pillow and Playwright are imported inside the rasterising functions:
# partials.py imports mark_svg() from here for the nav, and building
# markup should not require a browser.

ROOT = pathlib.Path(__file__).resolve().parent.parent

# sampled from the running site (see the ridge ramp --gs-*a and --sky-*)
SKY_HI, SKY_LO = "#c4ccc2", "#f2e0c2"
FAR_FILL, MID_FILL, NEAR_FILL = "#a6bbb5", "#789781", "#133d2a"
AMBER, AMBER_SOFT, PAPER = "#c8772e", "#e29a5b", "#edf0ec"

# far ridge peaks RIGHT so it answers a near crest that peaks LEFT
FAR = ("M-1,16.4 C3,14.8 6,14.2 10,15.2 C14,16.2 18,11 23,9.6 "
       "C27,8.4 30,11 33,13 L33,33 L-1,33Z")
MID = ("M-1,21 C4,19 8,17.6 13,18.6 C17,19.4 20,17 24,16.4 "
       "C28,15.8 30,17.4 33,18.6 L33,33 L-1,33Z")
# main summit left, shoulder descending right
CREST = ("M-1,23 C2,20.2 4.6,15.2 8.2,14.8 C11.4,14.4 13,18.4 15.4,19.2 "
         "C17.6,19.9 19,17.6 21.4,18 C24,18.4 26,21.6 29,23.4 "
         "C30.8,24.5 32,24.9 33,25.1 L33,33 L-1,33Z")

RADIUS = 7          # on a 32 viewBox
HAZE_OP = 0.45
RIM_W = 1.1
RIM_W_SMALL = 1.4   # the 16px cut needs a wider rim to register at all

# The tile's containing edge. Not decoration: the sky is luminance ~204
# and a dark tab strip is ~54, so a rounded corner blending between them
# throws bright specks along the arc. A dark rim makes the corner blend
# dark-to-dark. Measured at 32px on a dark tab, brightest corner pixel
# over the tab: no rim +149, rim +36.
EDGE = "#1f3a2e"
EDGE_W = 1.8
EDGE_W_SMALL = 1.8

# The tile is SQUARE, and that is the fix for the corner specks rather
# than a style choice. A rounded corner pulls the pale sky (L~204) to
# within a pixel of the boundary, so against a dark tab (L~54) the
# pixels just inside the arc read as bright flecks. Hiding them needs a
# rim of about 3.2 units, which at 160px is a 16px mat that eats the
# picture. A square edge has no arc, so a thin rim is enough and the
# failure mode is gone rather than covered up. apple-touch was already
# square, so all three files are now one artwork.
#
# It matters that this lives in favicon.SVG. The head declares the ICO
# first and the SVG second, and among equally appropriate icons the LAST
# declared wins, so browsers render the SVG. A fix applied only to the
# ICO's 16px entry is a fix to a file no browser loads.
TILE_RX = 0

# The page register crops to its own ink. With the sky gone the ridges
# occupy only y 9.30..33 of the 32 box, so in a square element the mass
# sits 4.65 units low, which at 28px is 4.07px: the mark reads as
# dropped below the wordmark even though its BOX is perfectly centred.
# 34 / 24.29 = 1.400 exactly, matching a 28x20 element.
BARE_VIEW = "-1 8.71 34 24.29"
BARE_W, BARE_H = 28, 20


def frame_shape(rx=RADIUS, frame="rect"):
    """The one shape that bounds the mark."""
    if frame == "circle":
        return '<circle cx="16" cy="16" r="16"/>'
    corner = f' rx="{rx}"' if rx else ""
    return f'<rect width="32" height="32"{corner}/>'


def mark_svg(ns="lm", rx=TILE_RX, mid=True, haze=True, rim_w=RIM_W,
             open_tag=None, frame="rect", edge=None, edge_w=1.1, bare=False):
    """The mark. `ns` namespaces the gradient ids so an inlined copy
    cannot collide with the scene gradients already on the page.

    Everything, sky included, lives inside ONE clipped group. Drawing a
    rounded sky rect AND clipping the ridges with an identical rounded
    rect gave two independently antialiased edges over the same corner:
    where the crest's coverage exceeded the sky rect's it painted onto
    bare page, leaving stray mid-tone pixels just outside the corner
    that read as a pale blue fringe against warm surroundings."""
    tag = open_tag or ('<svg xmlns="http://www.w3.org/2000/svg" '
                       'viewBox="0 0 32 32">')
    if bare:
        # The reduced register: the ridges alone in currentColor, planes
        # separated by OPACITY so the mark still carries its depth, with
        # no tile, no sky and no gradients to define. For sitting in a
        # line of type rather than on the page as an icon.
        parts = [tag, f'<path d="{FAR}" fill="currentColor" opacity="0.26"/>']
        if mid:
            parts.append(f'<path d="{MID}" fill="currentColor" opacity="0.55"/>')
        parts.append(f'<path d="{CREST}" fill="currentColor"/></svg>')
        return "".join(parts)
    out = [tag, "<defs>",
           f'<linearGradient id="{ns}-sky" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="{SKY_HI}"/>'
           f'<stop offset="1" stop-color="{SKY_LO}"/></linearGradient>',
           # The light peaks ON the flank and falls away again. Ramping
           # it to full at x=1 put the strongest amber at the lowest,
           # furthest part of the ridge, which thickened into a heavy
           # diagonal in the corner and read as a drawn edge, not light.
           f'<linearGradient id="{ns}-rim" x1="0" y1="0" x2="1" y2="0">'
           f'<stop offset="0.34" stop-color="{AMBER_SOFT}" stop-opacity="0"/>'
           f'<stop offset="0.68" stop-color="{AMBER}" stop-opacity="1"/>'
           f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0.22"/>'
           f'</linearGradient>']
    if haze:
        out.append(
            f'<linearGradient id="{ns}-haze" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{PAPER}" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="{PAPER}" stop-opacity="{HAZE_OP}"/>'
            f'<stop offset="1" stop-color="{PAPER}" stop-opacity="0"/>'
            f'</linearGradient>')
    out.append(f'<clipPath id="{ns}-tile">{frame_shape(rx, frame)}</clipPath>')
    out.append("</defs>")
    # one rounded boundary: the sky is square and clipped with everything else
    out.append(f'<g clip-path="url(#{ns}-tile)">')
    out.append(f'<rect width="32" height="32" fill="url(#{ns}-sky)"/>')
    out.append(f'<path d="{FAR}" fill="{FAR_FILL}"/>')
    if haze:
        out.append(f'<rect x="-1" y="13.5" width="34" height="6" '
                   f'fill="url(#{ns}-haze)"/>')
    if mid:
        out.append(f'<path d="{MID}" fill="{MID_FILL}"/>')
    out.append(f'<path d="{CREST}" fill="{NEAR_FILL}"/>')
    out.append(f'<path d="{CREST}" fill="none" stroke="url(#{ns}-rim)" '
               f'stroke-width="{rim_w}" transform="translate(0,-0.5)"/>')
    if edge:
        # An inner rim, drawn last, inside the clip so half the stroke is
        # cut away and the visible width is edge_w. Its job is optical,
        # not decorative: the sky is L~204 and a dark surround is L~40,
        # so a rounded corner blending between them throws bright specks
        # along the arc. A dark rim makes that blend dark-to-dark.
        out.append(f'<g stroke="{edge}" fill="none" '
                   f'stroke-width="{edge_w * 2}">'
                   + frame_shape(rx, frame).replace("/>", ' fill="none"/>')
                   + "</g>")
    out.append("</g></svg>")
    return "".join(out)


def rasterise(jobs):
    """jobs: list of (svg, px). Rendered at device_scale_factor 1 so what
    lands in the file is the true pixel grid, not a smoothed upscale."""
    import io
    from PIL import Image
    from playwright.sync_api import sync_playwright
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 300, "height": 300},
                        device_scale_factor=1)
        for svg, px in jobs:
            # NO page background: omit_background only yields real
            # transparency if nothing paints behind the mark. Painting
            # white here baked opaque white into the rounded corners,
            # which showed as a white halo on any non-white tab strip.
            pg.set_content(
                "<body style='margin:0;background:transparent'>"
                f"<div style='width:{px}px;height:{px}px'>{svg}</div>")
            buf = pg.screenshot(omit_background=True,
                                clip={"x": 0, "y": 0, "width": px, "height": px})
            shots.append(Image.open(io.BytesIO(buf)).convert("RGBA"))
        b.close()
    return shots


def write_ico(path, images):
    """Hand-rolled so each size can be a DIFFERENT drawing. PIL's writer
    resizes one source image, which would defeat the 16px cut."""
    import io
    payloads = []
    for im in images:
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        payloads.append(buf.getvalue())
    n = len(images)
    out = struct.pack("<HHH", 0, 1, n)
    offset = 6 + 16 * n
    for im, data in zip(images, payloads):
        w = 0 if im.width >= 256 else im.width
        h = 0 if im.height >= 256 else im.height
        out += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    out += b"".join(payloads)
    path.write_bytes(out)


def main():
    from PIL import Image
    full = mark_svg("lm", edge=EDGE, edge_w=EDGE_W)
    # With a square edge the 16px cut needs no special rim weight: there
    # is no corner arc for the sky to leak around.
    cut = mark_svg("lm", mid=False, haze=False, rim_w=RIM_W_SMALL,
                   edge=EDGE, edge_w=EDGE_W_SMALL)
    # apple-touch is full bleed and square: iOS applies its own corner
    # mask, so baking one in would show a halo inside the system radius
    touch = mark_svg("lm", edge=EDGE, edge_w=EDGE_W)

    (ROOT / "favicon.svg").write_text(full + "\n", encoding="utf-8")

    ico16, ico32, ico48, atouch = rasterise(
        [(cut, 16), (full, 32), (full, 48), (touch, 180)])
    write_ico(ROOT / "favicon.ico", [ico16, ico32, ico48])

    # opaque: Apple asks for no alpha channel on the touch icon
    flat = Image.new("RGB", atouch.size, "#ffffff")
    flat.paste(atouch, mask=atouch.split()[3])
    flat.save(ROOT / "apple-touch-icon.png", format="PNG", optimize=True)

    for f in ("favicon.svg", "favicon.ico", "apple-touch-icon.png"):
        print(f"{f:24s} {(ROOT / f).stat().st_size:6d} bytes")


if __name__ == "__main__":
    main()
