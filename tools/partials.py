"""Shared page chrome (dev-time only, stdlib only, nothing ships).

Every page carries the same head boot scripts, header, scenery
backdrop, footer and script tags. Hand-copying those across ten
files drifts, so this tool owns them: each page keeps its own
content, and the blocks between marker comments are rewritten from
the PAGES registry below.

    <!-- partial:head -->      ... <!-- /partial:head -->
    <!-- partial:header -->    ... <!-- /partial:header -->
    <!-- partial:backdrop -->  ... <!-- /partial:backdrop -->
    <!-- partial:footer -->    ... <!-- /partial:footer -->
    <!-- partial:scripts -->   ... <!-- /partial:scripts -->

Usage:
    python tools/scene_gen.py     regenerate assets/scenes/*.html (if scenes changed)
    python tools/partials.py      rewrite the marker blocks in every page
                                  and write the redirect stubs

Scenery is read from assets/scenes/, so run scene_gen.py first when a
scene changes. Paths are root-absolute (/styles.css) because pages
live in subdirectories; preview with `python -m http.server` from the
repo root rather than file://.
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENES = ROOT / "assets" / "scenes"
SITE = "https://darwinls.github.io"

EMAIL = "darwinllss321@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/darwin-smith/"
GITHUB = "https://github.com/DarwinLS"
# In-site links go straight to the PDFs; /resume/ and /resume/design/
# stay as short shareable redirects (REDIRECTS below).
RESUME_SE = "/assets/resume/Darwin_Smith_Software_Engineer.pdf"
RESUME_PD = "/assets/resume/Darwin_Smith_Product_Designer.pdf"
ICON_CHEV = ('<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
             ' stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
             ' aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>')
NEW_TAB = '<span class="visually-hidden"> (opens in a new tab)</span>'
PDF_TAB = '<span class="visually-hidden"> (PDF, opens in a new tab)</span>'
OG_IMAGE = "/assets/og/og-default.png"

# ---------------- registry ----------------
# file: path relative to repo root. url: canonical path.
# biome: sky tint + scene family (styles.css [data-biome]).
# scene: generated scene name in assets/scenes/, and its wrapper kind.
# nav: which nav item is current. resume: which resume "Resume" opens.
# order: view-transition direction (lower = further "up" the site).

PAGES = [
    {
        "file": "index.html", "url": "/", "order": 0,
        "title": "Darwin Smith | Software Engineer & Product Designer",
        "desc": "Darwin Smith, software engineer and product designer. Designed and built Veraflux, a product that turns PubMed studies into cited supplement reports.",
        "biome": "home", "scene": ("descent", "home-descent"),
        "nav": "home", "resume": "se",
        "cards_h": "h3", "footer": "slim",
    },
    {
        "file": "veraflux/index.html", "url": "/veraflux/", "order": 1,
        "title": "How Veraflux is built | Darwin Smith",
        "desc": "The engineering behind Veraflux: a retrieval-augmented LLM pipeline over PubMed, request deadlines and load shedding, deploy incidents, and billing correctness.",
        "biome": "veraflux", "scene": ("vista", "vista-veraflux"),
        "nav": "engineering", "resume": "se",
    },
    {
        "file": "design/index.html", "url": "/design/", "order": 2,
        "title": "Design case studies | Darwin Smith",
        "desc": "Product design case studies from Veraflux, a health-research product: color, accessibility and typography, interaction design, and content design.",
        "biome": "projects", "scene": ("vista", "vista-projects"),
        "nav": "design", "resume": "pd",
        "cards_h": "h2", "cards_lazy": False,
    },
    {
        "file": "design/evidence/index.html", "url": "/design/evidence/", "order": 3,
        "css": ["/specimens.css"],
        "fonts": ["/assets/fonts/specimens/source-sans-3-var.woff2"],
        "title": "Evidence you can trust, typeset honestly · Design case study | Darwin Smith",
        "desc": "A design case study: color, accessibility, statistic emphasis, and typeface choices for AI-generated health reports.",
        "biome": "veraflux", "scene": ("vista", "vista-veraflux"),
        "nav": "design", "resume": "pd",
    },
    {
        "file": "design/writing/index.html", "url": "/design/writing/", "order": 3,
        "css": ["/specimens.css"],
        "title": "Error and pricing copy that tells the truth · Design case study | Darwin Smith",
        "desc": "A content design case study: error messages, plan copy, and a price line for a pre-launch health product.",
        "biome": "veraflux", "scene": ("vista", "vista-veraflux"),
        "nav": "design", "resume": "pd",
    },
    {
        "file": "design/scan/index.html", "url": "/design/scan/", "order": 3,
        "css": ["/specimens.css"],
        "title": "A scan flow built around the wait · Design case study | Darwin Smith",
        "desc": "A design case study: a photo-to-results flow for a slow AI backend that shows real elapsed time instead of simulated progress.",
        "biome": "veraflux", "scene": ("vista", "vista-veraflux"),
        "nav": "design", "resume": "pd",
    },
    {
        "file": "about/index.html", "url": "/about/", "order": 4,
        "title": "About | Darwin Smith",
        "desc": "About Darwin Smith: software engineer and product designer, UC San Diego Mathematics and Computer Science.",
        "biome": "about", "scene": ("vista", "vista-about"),
        "nav": "about", "resume": "se", "footer": "slim",
    },
]

# Old URLs and resume shortcuts. Stubs are noindex and carry a visible link.
REDIRECTS = [
    ("veraflux.html", "/veraflux/", "How Veraflux is built"),
    ("projects.html", "/#projects", "Projects"),
    ("about.html", "/about/", "About"),
    ("contact.html", "/#contact", "Contact"),
    ("resume/index.html", "/assets/resume/Darwin_Smith_Software_Engineer.pdf", "Software engineering resume (PDF)"),
    ("resume/design/index.html", "/assets/resume/Darwin_Smith_Product_Designer.pdf", "Product design resume (PDF)"),
]

# Case studies, in reading order. Cards on the home page and the design
# index come from here, and so does each study's previous/next footer.
CASE_STUDIES = [
    {
        "url": "/design/evidence/", "tag": "Color, accessibility, typography",
        "title": "Evidence you can trust, typeset honestly",
        "blurb": "A rating badge that made thin evidence look like a safety warning, a brand color that failed as text, and type choices made for a report full of statistics.",
        "img": "report-collapsed", "w": 1308, "h": 1190,
        "alt": "Collapsed sections of a Veraflux report, each with a numbered heading, a one-sentence preview, and a study count",
    },
    {
        "url": "/design/scan/", "tag": "Interaction design",
        "title": "A scan flow built around the wait",
        "blurb": "Photograph a supplement label and wait minutes for research on every ingredient, with the list staying on screen and a clock instead of a fake progress bar.",
        "img": "thumb-scan", "w": 1200, "h": 750,
        "alt": "Three versions of the same ingredient list: review, analyzing with an elapsed clock, and results with study counts",
    },
    {
        "url": "/design/writing/", "tag": "Content design",
        "title": "Error and pricing copy that tells the truth",
        "blurb": "Error messages that said what happened, a free plan that undersold the product, and a price line that told subscribers their bill would rise.",
        "img": "thumb-writing", "w": 1200, "h": 750,
        "alt": "A phone-width error notice before and after: a raw exception message beside a plain explanation with a retry button",
    },
]

NAV = [
    ("engineering", "Engineering", "/veraflux/"),
    ("design", "Design", "/design/"),
    ("about", "About", "/about/"),
]

# ---------------- blocks ----------------

THEME_BOOT = """<script>
      (function(){var r=document.documentElement;r.classList.add('js');try{var t=localStorage.getItem('theme');if(t==='light'||t==='dark'){r.dataset.theme=t;document.querySelectorAll('meta[name="theme-color"]').forEach(function(m){m.content=t==='dark'?'#0e1512':'#edf0ec';});}}catch(e){}try{var L=['calm','fog','rain'],p=localStorage.getItem('intensity');if(p==='balanced')p='fog';else if(p==='immersive')p='rain';if(L.indexOf(p)<0)p='rain';var gs=localStorage.getItem('gpusoft');if(gs==='1')r.dataset.gpu='soft';var c=navigator.connection||{},co=navigator.hardwareConcurrency||8,me=navigator.deviceMemory||8,mm=function(q){return window.matchMedia&&matchMedia(q).matches;},cl;if(mm('(prefers-reduced-motion: reduce)')||c.saveData||co<=2||me<=2){cl='calm';}else if(gs==='1'){cl='fog';}else{cl='rain';}r.dataset.pref=p;r.dataset.intensity=L[Math.min(L.indexOf(p),L.indexOf(cl))];}catch(e){r.dataset.pref='rain';r.dataset.intensity='rain';}})();
    </script>"""


def transitions_boot():
    # Longest matching prefix wins, so /design/scan/ sorts after /design/.
    order = {p["url"]: p["order"] for p in PAGES}
    return """<script>
      /* Cross-document View Transitions: tag navigation direction so pages
         slide the right way descending vs ascending the site (Chromium;
         ignored elsewhere). Inline so it registers before pagereveal fires.
         Generated by tools/partials.py. */
      (function(){var O=%s;function p(u){try{var n=new URL(u,location.href).pathname.replace(/index\\.html$/,'');if(n in O)return O[n];var b=-1,v=0;for(var k in O){if(n.indexOf(k)===0&&k.length>b){b=k.length;v=O[k];}}return v;}catch(e){return 0;}}function d(f,t){var a=p(f),b=p(t);return b>a?'forward':b<a?'backward':'reload';}addEventListener('pageswap',function(e){if(e.viewTransition&&e.activation&&e.activation.entry){e.viewTransition.types.add(d(location.href,e.activation.entry.url));}});addEventListener('pagereveal',function(e){if(!e.viewTransition)return;var a=(self.navigation&&navigation.activation)||null;var f=a&&a.from?a.from.url:null;e.viewTransition.types.add(f?d(f,location.href):'forward');});})();
    </script>""" % json.dumps(order, separators=(",", ":"))


SPECULATION = """<script type="speculationrules">
      {"prerender":[{"where":{"and":[{"href_matches":"/*"},{"not":{"href_matches":"/resume/*"}},{"not":{"href_matches":"/assets/*"}},{"not":{"href_matches":"/*.html"}}]},"eagerness":"moderate"}]}
    </script>"""


def head_block(page):
    esc = lambda s: html.escape(s, quote=True)
    url = SITE + page["url"]
    lines = [
        # theme-color precedes the boot script so a stored theme can pin it before paint
        '<meta name="theme-color" content="#edf0ec" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#0e1512" media="(prefers-color-scheme: dark)">',
        THEME_BOOT,
        transitions_boot(),
        SPECULATION,
        f'<title>{esc(page["title"])}</title>',
        f'<meta name="description" content="{esc(page["desc"])}">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Darwin Smith">',
        f'<meta property="og:title" content="{esc(page["title"])}">',
        f'<meta property="og:description" content="{esc(page["desc"])}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{SITE}{page.get("image", OG_IMAGE)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(page.get("image_alt", "Darwin Smith, Software Engineer and Product Designer, over a misty forest ridge"))}">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="color-scheme" content="light dark">',
        # ICO first, SVG after: among equally appropriate icons the spec says
        # the LAST declared wins, so the vector is preferred wherever it is
        # supported (which is now Safari 26 as well). The ICO is declared at
        # 48x48, a size it really contains, which also keeps Chrome from
        # choosing it over the SVG for a 16 or 32px tab. It sits at the
        # document root for the agents that never parse this head at all:
        # feed readers, link unfurlers and crawlers ask for /favicon.ico and
        # nothing else. The 32px PNG it replaces was no use to any of them.
        '<link rel="icon" href="/favicon.ico" sizes="48x48">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="stylesheet" href="/styles.css">',
        '<link rel="stylesheet" href="/transitions.css">',
        '<link rel="stylesheet" href="/effects.css">',
        '<link rel="preload" href="/assets/fonts/fraunces-var.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>',
    ]
    lines += [f'<link rel="stylesheet" href="{href}">' for href in page.get("css", [])]
    lines += [f'<link rel="preload" href="{href}" as="font" type="font/woff2" crossorigin>' for href in page.get("fonts", [])]
    return "\n".join(lines)


ICON_CALM = '<svg class="i-calm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>'
ICON_FOG = '<svg class="i-fog" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 17H7"/><path d="M17 21H9"/></svg>'
ICON_RAIN = '<svg class="i-rain" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="m9.2 22 3-7"/><path d="m9 13-3 7"/><path d="m17 13-3 7"/></svg>'
ICON_MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'
ICON_SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>'
ICON_BURGER = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18"/><path d="M3 12h18"/><path d="M3 18h18"/></svg>'


# The nav mark is the SAME artwork as the favicon, generated by
# tools/make_icons.py so the two can never drift. Edit it there.
#
# The page takes the REDUCED register: the ridges alone in currentColor,
# planes separated by opacity, no tile and no sky. The icon slots take
# the filled tile. That is one mark in two registers, the way a crest
# has a solid hinata form and a reduced form, not two marks.
#
# The tile was tried here first and read as an app icon pasted into a
# nav where everything else is monochrome type and line work. A single
# FLAT silhouette was rejected before that, correctly, because it is a
# blob; the mistake was concluding that bare could not work. Layered by
# opacity it keeps the depth that is the whole identity, and it themes
# itself, which a fixed-colour tile cannot.
#
# It crops to its own ink via BARE_VIEW. With the sky gone the ridges
# fill only the lower part of the 32 box, so a square element left the
# mass sitting 4.07px low and the mark read as dropped below the
# wordmark even though its box was perfectly centred.
from make_icons import BARE_VIEW, mark_svg  # noqa: E402

LOGO_MARK = mark_svg(
    "lm", bare=True,
    open_tag=f'<svg class="logo-mark" viewBox="{BARE_VIEW}" aria-hidden="true">')


def header_block(page):
    items = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if page["nav"] == key else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    # Resume opens a two-item menu rather than guessing a track. It is a
    # <details>, so it opens, closes and takes the keyboard with no script;
    # site.js only adds the dismissals a menu is expected to have. The
    # track this page is about is listed first.
    tracks = [("Software engineering", RESUME_SE), ("Product design", RESUME_PD)]
    if page["resume"] == "pd":
        tracks.reverse()
    choices = "\n".join(
        f'                        <li><a class="ext" href="{href}" target="_blank"'
        f' rel="noopener">{label}{PDF_TAB}</a></li>'
        for label, href in tracks)
    items.append(
        '<li class="nav-menu">\n'
        '                <details>\n'
        f'                    <summary>Resume{ICON_CHEV}</summary>\n'
        '                    <ul class="nav-menu-list">\n'
        f'{choices}\n'
        '                    </ul>\n'
        '                </details>\n'
        '            </li>')
    home_cur = ' aria-current="page"' if page["nav"] == "home" else ""
    links = "\n".join("            " + i for i in items)
    return f"""<a class="skip-link btn btn--primary btn--sm" href="#main">Skip to content</a>
<header class="site-header">
    <nav class="navbar" aria-label="Main">
        <span class="navbar-glass glass no-refract" aria-hidden="true"></span>
        <a class="logo" href="/"{home_cur}>{LOGO_MARK}<span class="logo-word">Darwin Smith</span></a>
        <ul class="nav-links glass" id="nav-links">
{links}
        </ul>
        <div class="nav-tools">
            <button class="icon-btn intensity-toggle" id="intensity-toggle" type="button" aria-label="Ambience" data-tip="Ambience">{ICON_CALM}{ICON_FOG}{ICON_RAIN}</button>
            <button class="icon-btn theme-toggle" id="theme-toggle" type="button" aria-label="Switch theme" data-tip="Theme">{ICON_MOON}{ICON_SUN}</button>
            <button class="icon-btn nav-burger" id="nav-burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav-links">{ICON_BURGER}</button>
        </div>
    </nav>
</header>"""


def scene_markup(name):
    path = SCENES / f"{name}.html"
    if not path.exists():
        raise SystemExit(f"missing {path}; run python tools/scene_gen.py first")
    return path.read_text(encoding="utf-8").rstrip("\n")


def indent(text, pad):
    return "\n".join((pad + line) if line else line for line in text.split("\n"))


def backdrop_block(page):
    kind, name = page["scene"]
    scene = indent(scene_markup(name), "        ")
    top = """<div class="sky-backdrop" aria-hidden="true"></div>
<div class="fx-haze" aria-hidden="true"></div>
<div class="fx-dusk" aria-hidden="true"></div>
"""
    if kind == "descent":
        return top + f"""<div class="scene-descent" aria-hidden="true">
    <div class="scene-track">
{scene}
    </div>
    <div class="sd sd-dusk"></div>
</div>"""
    short = name.replace("vista-", "")
    return top + f"""<div class="vista vista-{short}" aria-hidden="true">
    <div class="scene-track">
{scene}
    </div>
</div>"""


ICON_MAIL = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>'


def footer_block(page):
    resume = RESUME_PD if page["resume"] == "pd" else RESUME_SE
    scene = indent(scene_markup("footer-valley"), "    ")
    if page.get("footer") == "slim":
        # the page already ends with a full contact card
        return f"""<footer class="site-footer site-footer--slim">
{scene}
    <p class="copyright">&copy; 2026 Darwin Smith</p>
</footer>"""
    return f"""<footer class="site-footer">
{scene}
    <address class="footer-contact">
        <a class="footer-email" href="mailto:{EMAIL}">{ICON_MAIL}<span>{EMAIL}</span></a>
        <span class="footer-links">
            <a class="ext brand brand--li" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn{NEW_TAB}</a>
            <a class="ext brand brand--gh" href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub{NEW_TAB}</a>
            <a class="ext brand brand--doc" href="{resume}" target="_blank" rel="noopener">Resume{PDF_TAB}</a>
        </span>
    </address>
    <p class="copyright">&copy; 2026 Darwin Smith</p>
</footer>"""


def scripts_block(page):
    return """<script src="/assets/js/site.js" defer></script>
<script src="/assets/effects/glass.js" defer></script>
<script type="module" src="/assets/effects/ambient.js"></script>"""


def shot_img(name, w, h, alt, lazy=True, priority=False, sizes="(min-width: 1180px) 360px, (min-width: 900px) 30vw, 94vw", themed=True):
    """Both theme variants carry the alt text: CSS removes the hidden one
    from the accessibility tree with display:none. Each variant offers an
    800px source so phones and card slots never pull the full capture.
    A single-theme capture (no -dark file) renders one image."""
    base = "/assets/images/veraflux/"
    a = html.escape(alt, quote=True)
    first = ' fetchpriority="high"' if priority else (' loading="lazy"' if lazy else "")

    def srcset(theme):
        return f'{base}{name}-{theme}-800.webp 800w, {base}{name}-{theme}.webp {w}w'

    dark = themed and (ROOT / "assets" / "images" / "veraflux" / f"{name}-dark.webp").exists()
    light_img = (f'<img class="{"shot-light" if dark else "shot-any"}" src="{base}{name}-light.webp" srcset="{srcset("light")}" sizes="{sizes}" '
                 f'width="{w}" height="{h}" alt="{a}" decoding="async"{first}>')
    if not dark:
        return light_img
    return (light_img + "\n" +
            f'<img class="shot-dark" src="{base}{name}-dark.webp" srcset="{srcset("dark")}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{a}" decoding="async" loading="lazy">')


def design_cards_block(page):
    h = page.get("cards_h", "h3")
    lazy = page.get("cards_lazy", True)
    cards = []
    for cs in CASE_STUDIES:
        # decorative inside the link: the heading already names the card
        # one image in both themes, so a row of thumbnails never mixes light and dark
        img = indent(shot_img(cs["img"], cs["w"], cs["h"], "", lazy=lazy, themed=False), "        ")
        cid = "card-" + cs["url"].strip("/").split("/")[-1]
        cards.append(f"""    <a class="card" href="{cs['url']}" aria-labelledby="{cid}">
        <div class="card-media">
{img}
        </div>
        <div class="card-body">
            <span class="eyebrow">{html.escape(cs['tag'])}</span>
            <{h} id="{cid}">{html.escape(cs['title'])}</{h}>
            <p>{html.escape(cs['blurb'])}</p>
        </div>
    </a>""")
    return '<div class="grid-3">\n' + "\n".join(cards) + "\n</div>"


def case_nav_block(page):
    def card(href, label, title, new_tab=False):
        attrs = ' target="_blank" rel="noopener"' if new_tab else ""
        tail = NEW_TAB if new_tab else ""
        return f'    <a class="nav-card glass" href="{href}"{attrs}><span class="meta-label">{label}<span class="visually-hidden">:</span></span> <span class="nav-card-title">{html.escape(title)}</span>{tail}</a>'

    urls = [cs["url"] for cs in CASE_STUDIES]
    links = []
    if page["url"] == "/design/":
        links.append(card("/veraflux/", "The engineering side", "How Veraflux is built"))
        links.append(card(CASE_STUDIES[0]["url"], "Start here", CASE_STUDIES[0]["title"]))
        links.append(card(RESUME_PD, "Resume", "Product design resume (PDF)", new_tab=True))
        label = "More work"
    elif page["url"] not in urls:
        # the engineering page: hand off to the design work
        links.append(card("/design/", "Design", "All case studies"))
        links.append(card(CASE_STUDIES[0]["url"], "First case study", CASE_STUDIES[0]["title"]))
        links.append(card(RESUME_SE, "Resume", "Software engineering resume (PDF)", new_tab=True))
        label = "More work"
    else:
        i = urls.index(page["url"])
        prev_cs = CASE_STUDIES[i - 1] if i > 0 else None
        next_cs = CASE_STUDIES[i + 1] if i + 1 < len(CASE_STUDIES) else None
        links.append(card(prev_cs["url"], "Previous case study", prev_cs["title"]) if prev_cs
                     else card("/design/", "Back to", "All case studies"))
        links.append(card(next_cs["url"], "Next case study", next_cs["title"]) if next_cs
                     else card("/veraflux/", "The engineering side", "How Veraflux is built"))
        links.append(card(RESUME_PD, "Resume", "Product design resume (PDF)", new_tab=True))
        label = "More case studies"
    return f'<nav class="nav-cards" aria-label="{label}">\n' + "\n".join(links) + "\n</nav>"


BLOCKS = {
    "head": head_block,
    "header": header_block,
    "backdrop": backdrop_block,
    "footer": footer_block,
    "scripts": scripts_block,
}

# Only written where a page carries the marker.
OPTIONAL_BLOCKS = {
    "design-cards": design_cards_block,
    "case-nav": case_nav_block,
}


def redirect_stub(target, label):
    t = html.escape(target, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex">
    <title>{html.escape(label)} | Darwin Smith</title>
    <meta http-equiv="refresh" content="0; url={t}">
    <script>location.replace({json.dumps(target)});</script>
</head>
<body>
    <p><a href="{t}">{html.escape(label)}</a></p>
</body>
</html>
<!-- Generated by tools/partials.py -->
"""


def main():
    for page in PAGES:
        path = ROOT / page["file"]
        if not path.exists():
            print(f"!! {page['file']} does not exist yet, skipped")
            continue
        text = path.read_text(encoding="utf-8")
        for name, build in {**BLOCKS, **OPTIONAL_BLOCKS}.items():
            pattern = re.compile(
                r"([ \t]*)<!-- partial:" + re.escape(name) + r" -->.*?<!-- /partial:" + re.escape(name) + r" -->",
                re.DOTALL,
            )
            m = pattern.search(text)
            if not m:
                if name in BLOCKS:
                    print(f"!! marker partial:{name} not found in {page['file']}")
                continue
            pad = m.group(1)
            body = indent(build(page), pad)
            text = text[:m.start()] + f"{pad}<!-- partial:{name} -->\n{body}\n{pad}<!-- /partial:{name} -->" + text[m.end():]
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"chrome -> {page['file']}")

    for file, target, label in REDIRECTS:
        path = ROOT / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(redirect_stub(target, label), encoding="utf-8", newline="\n")
        print(f"redirect {file} -> {target}")


if __name__ == "__main__":
    main()
