"""Design audit harness (dev only; nothing here ships).

Needs the site served locally (python -m http.server 8765 from the repo root)
and Playwright with chromium, webkit and firefox installed.

    python tools/design_audit.py shots    LABEL   viewport-stepped captures + contrast
    python tools/design_audit.py states   LABEL   rest/hover/focus/active strips per component
    python tools/design_audit.py checks   LABEL   census, focus order, headings, images,
                                                  overflow, alignment, targets, head, axe
    python tools/design_audit.py coverage LABEL   CSS rules no page state ever matched
    python tools/design_audit.py all      LABEL

Output goes to _private/audit/LABEL/ (gitignored). Captures step through the
page one viewport at a time instead of full-page screenshots: the scenery is
position:fixed, and a full-page capture paints it once at the top.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("AUDIT_BASE", "http://127.0.0.1:8765")
PAGES = {
    "home": "/",
    "veraflux": "/veraflux/",
    "design": "/design/",
    "evidence": "/design/evidence/",
    "scan": "/design/scan/",
    "writing": "/design/writing/",
    "about": "/about/",
}
WIDTHS = {390: 844, 768: 1024, 1024: 768, 1440: 900, 1920: 1080}
AXE = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"
GPU_ARGS = ["--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist"]


def out_dir(label, *parts):
    d = ROOT / "_private" / "audit" / label
    for p in parts:
        d = d / p
    d.mkdir(parents=True, exist_ok=True)
    return d


def new_context(browser, width, theme, intensity="calm", mobile=None, scheme="light", reduced=None):
    mobile = width <= 430 if mobile is None else mobile
    ctx = browser.new_context(
        viewport={"width": width, "height": WIDTHS.get(width, 900)},
        device_scale_factor=2 if mobile else 1,
        is_mobile=mobile if browser.browser_type.name != "firefox" else False,
        has_touch=mobile,
        color_scheme=scheme,
        reduced_motion=reduced or "no-preference",
    )
    script = f"try{{localStorage.setItem('intensity','{intensity}');"
    if theme in ("light", "dark"):
        script += f"localStorage.setItem('theme','{theme}');"
    else:
        script += "localStorage.removeItem('theme');"
    script += "}catch(e){}"
    ctx.add_init_script(script)
    return ctx


def load(page, path):
    page.goto(BASE + path, wait_until="load")
    page.evaluate("document.fonts.ready")
    # walk the page once so lazy images decode before any capture
    page.evaluate("""async () => {
        const H = document.documentElement.scrollHeight;
        for (let y = 0; y < H; y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
        scrollTo(0, 0);
    }""")
    page.wait_for_timeout(400)


# ---------------------------------------------------------------- contrast

TEXT_RECTS_JS = r"""() => {
  const out = [];
  const W = innerWidth, H = innerHeight;
  const sig = e => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  // fixed chrome (the header) covers content; never sample text under it
  const covers = [...document.querySelectorAll('.site-header .navbar')].map(e => e.getBoundingClientRect());
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const byEl = new Map();
  let n;
  while ((n = walker.nextNode())) {
    if (!n.nodeValue.trim()) continue;
    const el = n.parentElement;
    if (!el || el.closest('svg, script, style, noscript, [aria-hidden="true"], .visually-hidden')) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    for (const r of range.getClientRects()) {
      if (r.width < 2 || r.height < 2) continue;
      const e = byEl.get(el) || { x0: 1e9, y0: 1e9, x1: -1e9, y1: -1e9, text: '' };
      e.x0 = Math.min(e.x0, r.left); e.y0 = Math.min(e.y0, r.top); e.x1 = Math.max(e.x1, r.right); e.y1 = Math.max(e.y1, r.bottom);
      e.text += n.nodeValue.trim() + ' ';
      byEl.set(el, e);
    }
  }
  for (const [el, b] of byEl) {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    if (b.y0 < 0 || b.y1 > H || b.x0 < 0 || b.x1 > W + 1) continue;
    if (covers.some(c => b.y0 < c.bottom + 4 && b.y1 > c.top && b.x0 < c.right && b.x1 > c.left)) continue;
    const hit = document.elementFromPoint((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2);
    if (!hit || !(el.contains(hit) || hit.contains(el))) continue;
    let op = 1; for (let a = el; a; a = a.parentElement) op *= +getComputedStyle(a).opacity;
    out.push({ sig: sig(el), parent: el.parentElement ? sig(el.parentElement) : '', text: b.text.trim().slice(0, 60),
      x0: b.x0, y0: b.y0, x1: b.x1, y1: b.y1, color: cs.color, op, size: parseFloat(cs.fontSize), weight: +cs.fontWeight,
      spec: !!el.closest('.spec-plate, .notice, .phone') });
  }
  return out;
}"""

HIDE_TEXT_CSS = ("*,*::before,*::after{color:transparent!important;-webkit-text-fill-color:transparent!important;"
                 "text-shadow:none!important;text-decoration-color:transparent!important}")


def parse_rgba(s):
    # rgb()/rgba() in 0-255, or color(srgb r g b / a) in 0-1 (color-mix output)
    srgb = s.startswith("color(")
    body = s[s.index("(") + 1:s.rindex(")")].replace("srgb", "").replace("/", ",")
    parts = [p for p in body.replace(" ", ",").split(",") if p.strip()]
    r, g, b = (float(parts[i]) * (255 if srgb else 1) for i in range(3))
    a = float(parts[3]) if len(parts) > 3 else 1.0
    return r, g, b, a


def lum(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def contrast_for_step(page, dpr, rects):
    from io import BytesIO
    from PIL import Image
    tag = page.add_style_tag(content=HIDE_TEXT_CSS)
    page.wait_for_timeout(60)
    img = Image.open(BytesIO(page.screenshot())).convert("RGB")
    page.evaluate("t => t.remove()", tag)
    fails = []
    for r in rects:
        if r["spec"]:
            continue
        box = tuple(int(v * dpr) for v in (max(r["x0"], 0), max(r["y0"], 0), r["x1"], r["y1"]))
        if box[2] > img.width or box[3] > img.height or box[2] <= box[0] or box[3] <= box[1]:
            continue   # outside the captured pixels (mobile viewport vs screenshot height)
        crop = img.crop(box)
        px = list(crop.getdata())
        if not px:
            continue
        px.sort(key=lum)
        lo, hi = px[int(len(px) * 0.08)], px[int(len(px) * 0.92)]
        mid = px[len(px) // 2]
        cr, cg, cb, ca = parse_rgba(r["color"])
        a = ca * r["op"]
        fg = tuple(c * a + m * (1 - a) for c, m in zip((cr, cg, cb), mid))
        worst = min(ratio(fg, lo), ratio(fg, hi))
        large = r["size"] >= 24 or (r["size"] >= 18.66 and r["weight"] >= 700)
        need = 3.0 if large else 4.5
        if worst < need:
            fails.append({**{k: r[k] for k in ("sig", "parent", "text", "size", "weight", "color")},
                          "ratio": round(worst, 2), "need": need, "bg_lo": lo, "bg_hi": hi})
    return fails


# ---------------------------------------------------------------- shots

def shots(label, combos=None):
    root = out_dir(label, "shots")
    fails_all = []
    combos = combos or (
        [("chromium", w, t, "calm") for w in WIDTHS for t in ("light", "dark")]
        + [("chromium", 1440, "os-dark", "calm"), ("chromium", 1440, "dark", "rain"), ("chromium", 390, "light", "rain")]
        + [(b, 1440, t, "calm") for b in ("webkit", "firefox") for t in ("light", "dark")]
    )
    with sync_playwright() as p:
        browsers = {}
        for bname, width, theme, inten in combos:
            if bname not in browsers:
                bt = getattr(p, bname)
                browsers[bname] = bt.launch(args=GPU_ARGS) if bname == "chromium" else bt.launch()
            scheme = "dark" if theme == "os-dark" else "light"
            ctx = new_context(browsers[bname], width, theme, inten, scheme=scheme)
            page = ctx.new_page()
            dpr = 2 if width <= 430 else 1
            for name, path in PAGES.items():
                load(page, path)
                H = page.evaluate("document.documentElement.scrollHeight")
                vh = WIDTHS[width]
                step = int(vh * 0.85)
                ys = list(range(0, max(H - vh, 0) + 1, step))
                if ys[-1] < H - vh:
                    ys.append(H - vh)
                d = root / f"{bname}-{width}-{theme}-{inten}" / name
                d.mkdir(parents=True, exist_ok=True)
                for i, y in enumerate(ys):
                    page.evaluate(f"scrollTo(0,{y})")
                    page.wait_for_timeout(180 if inten == "calm" else 450)
                    page.screenshot(path=str(d / f"{i:02d}.png"))
                    if bname == "chromium" and inten == "calm":
                        rects = page.evaluate(TEXT_RECTS_JS)
                        for f in contrast_for_step(page, dpr, rects):
                            fails_all.append({"page": name, "width": width, "theme": theme, "y": y, **f})
                print(bname, width, theme, inten, name, len(ys), "steps", flush=True)
            ctx.close()
        for b in browsers.values():
            b.close()
    # dedupe contrast failures by (page, sig, text, theme)
    uniq = {}
    for f in fails_all:
        k = (f["page"], f["theme"], f["sig"], f["text"])
        if k not in uniq or f["ratio"] < uniq[k]["ratio"]:
            uniq[k] = {**f, "widths": sorted({g["width"] for g in fails_all
                                              if (g["page"], g["theme"], g["sig"], g["text"]) == k})}
    rows = sorted(uniq.values(), key=lambda f: f["ratio"])
    (out_dir(label) / "contrast.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("contrast failures:", len(rows))


# ---------------------------------------------------------------- states

FOCUSABLES_JS = r"""() => {
  const sig = e => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).sort().join('.') : '')
      + ' in ' + (e.parentElement ? e.parentElement.tagName.toLowerCase() + '.' + (e.parentElement.className || '').toString().trim().split(/\s+/)[0] : '');
  const seen = new Map();
  document.querySelectorAll('a[href], button, [tabindex]:not([tabindex="-1"])').forEach((e, i) => {
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height || getComputedStyle(e).visibility === 'hidden') return;
    const s = sig(e);
    if (!seen.has(s)) { e.setAttribute('data-audit-id', String(i)); seen.set(s, i); }
  });
  return [...seen.entries()].map(([s, i]) => ({ sig: s, id: i }));
}"""


def states(label):
    from io import BytesIO
    from PIL import Image, ImageDraw
    root = out_dir(label, "states")
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU_ARGS)
        for theme in ("light", "dark"):
            ctx = new_context(b, 1440, theme, "calm")
            ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=BASE)
            page = ctx.new_page()
            done = set()
            for name, path in PAGES.items():
                load(page, path)
                # pressing for :active must never follow the link
                page.evaluate("document.addEventListener('click', e => e.preventDefault(), true)")
                for item in page.evaluate(FOCUSABLES_JS):
                    if item["sig"] in done:
                        continue
                    done.add(item["sig"])
                    sel = f'[data-audit-id="{item["id"]}"]'
                    el = page.locator(sel).first
                    try:
                        el.scroll_into_view_if_needed(timeout=2000)
                    except Exception:
                        continue
                    page.wait_for_timeout(120)
                    frames = []
                    toggles = ("theme-toggle" in item["sig"] or "intensity-toggle" in item["sig"])
                    for st in (("rest", "hover", "focus") if toggles else ("rest", "hover", "focus", "active")):
                        page.mouse.move(2, 400)
                        page.evaluate("document.activeElement && document.activeElement.blur()")
                        page.wait_for_timeout(60)
                        bb = el.bounding_box()
                        if not bb:
                            break
                        if st == "hover":
                            page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
                        elif st == "focus":
                            page.keyboard.press("Shift")
                            page.evaluate(f"document.querySelector('{sel}').focus()")
                        elif st == "active":
                            page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
                            page.mouse.down()
                        page.wait_for_timeout(420)
                        pad = 18
                        clip = {"x": max(bb["x"] - pad, 0), "y": max(bb["y"] - pad, 0),
                                "width": min(bb["width"] + 2 * pad, 1440 - max(bb["x"] - pad, 0)),
                                "height": min(bb["height"] + 2 * pad, 900)}
                        if clip["y"] + clip["height"] > 900:
                            clip["height"] = 900 - clip["y"]
                        try:
                            frames.append((st, Image.open(BytesIO(page.screenshot(clip=clip)))))
                        except Exception:
                            pass
                        if st == "active":
                            page.mouse.up()
                    if not frames:
                        continue
                    w = sum(f.width for _, f in frames) + 12 * len(frames)
                    h = max(f.height for _, f in frames) + 22
                    strip = Image.new("RGB", (w, h), (120, 120, 120))
                    x = 0
                    dr = ImageDraw.Draw(strip)
                    for st, f in frames:
                        dr.text((x + 4, 4), st, fill=(255, 255, 255))
                        strip.paste(f, (x, 22))
                        x += f.width + 12
                    fn = "".join(c if c.isalnum() else "_" for c in item["sig"])[:90]
                    strip.save(root / f"{theme}-{name}-{fn}.png")
                print("states", theme, name, flush=True)
            ctx.close()
        # mobile drawer open + copy button copied
        for theme in ("light", "dark"):
            ctx = new_context(b, 390, theme, "calm")
            page = ctx.new_page()
            load(page, "/")
            page.click("#nav-burger")
            page.wait_for_timeout(600)
            page.screenshot(path=str(root / f"{theme}-drawer-open.png"))
            ctx.close()
        b.close()


# ---------------------------------------------------------------- checks

CENSUS_JS = r"""() => {
  const sig = e => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  const rows = [];
  for (const e of document.querySelectorAll('header *, main *, footer *')) {
    if (e.closest('svg, .spec, .spec-plate, .phone, .notice')) continue;
    const cs = getComputedStyle(e);
    if (cs.display === 'none') continue;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const hasText = [...e.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
    const row = { sig: sig(e) };
    if (hasText) {
      row.font = `${cs.fontFamily.split(',')[0].replace(/"/g,'')} ${cs.fontSize} / ${cs.fontWeight} / lh ${cs.lineHeight} / ls ${cs.letterSpacing}${cs.textTransform === 'uppercase' ? ' / UPPER' : ''}`;
      row.fontSize = cs.fontSize; row.color = cs.color;
    }
    if (cs.borderTopLeftRadius !== '0px' || cs.borderBottomRightRadius !== '0px') row.radius = [cs.borderTopLeftRadius, cs.borderTopRightRadius, cs.borderBottomRightRadius, cs.borderBottomLeftRadius].join(' ');
    for (const side of ['Top','Right','Bottom','Left']) {
      const w = cs['border' + side + 'Width'];
      if (w !== '0px' && cs['border' + side + 'Style'] !== 'none' && !cs['border' + side + 'Color'].endsWith(', 0)')) (row.borders ||= []).push(`${side} ${w} ${cs['border' + side + 'Style']} ${cs['border' + side + 'Color']}`);
    }
    if (cs.boxShadow !== 'none') row.shadow = cs.boxShadow;
    if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)') row.bg = cs.backgroundColor;
    if (cs.backdropFilter && cs.backdropFilter !== 'none') row.backdrop = cs.backdropFilter;
    if (cs.transitionDuration !== '0s') row.transition = `${cs.transitionProperty} ${cs.transitionDuration} ${cs.transitionTimingFunction}`;
    rows.push(row);
  }
  return rows;
}"""

FOCUS_WALK_JS = r"""() => {
  const a = document.activeElement;
  if (!a || a === document.body) return null;
  const cs = getComputedStyle(a), r = a.getBoundingClientRect();
  const sig = a.tagName.toLowerCase() + (typeof a.className === 'string' && a.className.trim() ? '.' + a.className.trim().split(/\s+/).join('.') : '');
  const onscreen = r.width > 0 && r.height > 0 && r.right > 0 && r.left < innerWidth && r.bottom > 0 && r.top < innerHeight;
  let hidden = false;
  for (let e = a; e; e = e.parentElement) { const s = getComputedStyle(e); if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity === 0 || e.inert) hidden = true; }
  return { sig, text: (a.textContent || a.getAttribute('aria-label') || '').trim().slice(0, 40), onscreen, hidden,
    outline: cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0 ? `${cs.outlineWidth} ${cs.outlineStyle} ${cs.outlineColor} off ${cs.outlineOffset}` : '',
    shadow: cs.boxShadow !== 'none' ? 'yes' : '', radius: cs.borderTopLeftRadius };
}"""

MISC_JS = r"""() => {
  const W = document.documentElement.clientWidth;
  const sig = e => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => ({ level: +h.tagName[1], text: h.textContent.trim().slice(0, 50), sig: sig(h) }));
  const skips = [];
  headings.reduce((prev, h) => { if (h.level > prev + 1) skips.push(`h${prev} -> h${h.level}: ${h.text}`); return h.level; }, 0);
  const images = [...document.querySelectorAll('img')].map(i => {
    const r = i.getBoundingClientRect(), vis = getComputedStyle(i).display !== 'none' && r.width > 0;
    return { src: i.getAttribute('src'), vis, alt: i.getAttribute('alt'), w: Math.round(r.width), nw: i.naturalWidth,
      attrs: `${i.hasAttribute('width') ? 'w' : '-'}${i.hasAttribute('height') ? 'h' : '-'} loading=${i.loading} decoding=${i.decoding} fetchpriority=${i.fetchPriority}` };
  }).filter(i => i.vis);
  const overflow = [...document.querySelectorAll('body *')].filter(e => {
    const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.right > W + 1 && s.position !== 'fixed' && !e.closest('.table-wrap, .fx-rain, .scene-descent, .vista, .sky-backdrop, .fx-haze, .nav-links, svg');
  }).slice(0, 8).map(e => sig(e) + ' right=' + Math.round(e.getBoundingClientRect().right));
  const blocks = {};
  for (const e of document.querySelectorAll('main > * , main > * > *, main .page-section > .section-inner, .content-page > *')) {
    const r = e.getBoundingClientRect(); if (!r.width || getComputedStyle(e).position === 'absolute') continue;
    if (r.width < W * 0.5) continue;
    const k = Math.round(r.left) + '+' + Math.round(r.width); (blocks[k] ||= []).push(sig(e).slice(0, 60));
  }
  const targets = [...document.querySelectorAll('a[href], button')].filter(e => {
    const r = e.getBoundingClientRect(); if (!r.width) return false;
    if (getComputedStyle(e).display === 'inline' && e.closest('p, li') && !e.closest('nav, .socials')) return false;
    return r.width < 24 || r.height < 24 || ((e.tagName === 'BUTTON' || e.classList.contains('btn')) && (r.height < 44));
  }).map(e => `${sig(e)} "${(e.textContent||'').trim().slice(0,25)}" ${Math.round(e.getBoundingClientRect().width)}x${Math.round(e.getBoundingClientRect().height)}`);
  const head = {
    icon: [...document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]')].map(l => l.getAttribute('href')),
    themeColor: [...document.querySelectorAll('meta[name="theme-color"]')].map(m => m.content + ' ' + (m.media || '')),
    colorScheme: getComputedStyle(document.documentElement).colorScheme,
    ogImage: document.querySelector('meta[property="og:image"]')?.content || '',
    twitter: document.querySelector('meta[name="twitter:card"]')?.content || '',
    skipLink: !!document.querySelector('a[href="#main"], a.skip-link'),
    preloads: [...document.querySelectorAll('link[rel="preload"]')].map(l => l.getAttribute('href')),
    newTab: [...document.querySelectorAll('a[target="_blank"]')].map(a => a.textContent.trim().slice(0, 30) + ' -> ' + a.getAttribute('href')),
  };
  return { headings, skips, images, overflow, blocks, targets, head, docW: W, scrollW: document.documentElement.scrollWidth };
}"""


def checks(label):
    root = out_dir(label)
    report = defaultdict(dict)
    census = defaultdict(lambda: defaultdict(Counter))
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU_ARGS)
        for width in (390, 1440):
            for theme in ("light", "dark"):
                ctx = new_context(b, width, theme, "calm")
                page = ctx.new_page()
                for name, path in PAGES.items():
                    load(page, path)
                    key = f"{name}@{width}-{theme}"
                    report[key]["misc"] = page.evaluate(MISC_JS)
                    for row in page.evaluate(CENSUS_JS):
                        for prop in ("font", "fontSize", "radius", "borders", "shadow", "bg", "color", "backdrop", "transition"):
                            if prop in row:
                                vals = row[prop] if isinstance(row[prop], list) else [row[prop]]
                                for v in vals:
                                    census[f"{theme}"][prop][v] += 1
                                    census[f"{theme}-where"][prop + "|" + v][row["sig"][:60]] += 1
                    # keyboard walk
                    page.evaluate("scrollTo(0,0)")
                    page.evaluate("document.activeElement && document.activeElement.blur()")
                    walk, first = [], None
                    for _ in range(160):
                        page.keyboard.press("Tab")
                        page.wait_for_timeout(35)
                        f = page.evaluate(FOCUS_WALK_JS)
                        if not f:
                            break
                        k = (f["sig"], f["text"])
                        if first is None:
                            first = k
                        elif k == first:
                            break
                        walk.append(f)
                    report[key]["focus"] = walk
                    if theme == "light":
                        try:
                            page.add_script_tag(url=AXE)
                            res = page.evaluate("axe.run(document, {resultTypes:['violations']})")
                            report[key]["axe"] = [{"id": v["id"], "impact": v["impact"], "help": v["help"],
                                                   "nodes": [n["target"][0] for n in v["nodes"][:6]]}
                                                  for v in res["violations"]]
                        except Exception as e:  # offline
                            report[key]["axe"] = [{"id": "axe-unavailable", "impact": "", "help": str(e)[:80], "nodes": []}]
                    print("checks", key, flush=True)
                ctx.close()
        b.close()
    (root / "checks.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    flat = {t: {prop: dict(c.most_common()) for prop, c in props.items()} for t, props in census.items()}
    (root / "census.json").write_text(json.dumps(flat, indent=1), encoding="utf-8")
    summarize(label, report, census)


def summarize(label, report, census):
    L = [f"# Audit checks: {label}", ""]
    for prop in ("fontSize", "font", "radius", "borders", "shadow", "backdrop", "transition", "bg", "color"):
        c = census["light"][prop]
        L.append(f"## {prop}: {len(c)} distinct values (light)")
        for v, n in c.most_common():
            where = census["light-where"][prop + "|" + v]
            L.append(f"- `{v}` x{n}  e.g. {', '.join(s for s, _ in where.most_common(3))}")
        L.append("")
    L.append("## Per page")
    for key, r in report.items():
        m = r["misc"]
        L.append(f"### {key}")
        if m["scrollW"] > m["docW"]:
            L.append(f"- OVERFLOW scrollWidth {m['scrollW']} > {m['docW']}: {m['overflow']}")
        if m["skips"]:
            L.append(f"- heading skips: {m['skips']}")
        L.append(f"- block columns: {{{', '.join(f'{k}: {len(v)}' for k, v in m['blocks'].items())}}}")
        for img in m["images"]:
            flags = []
            if not img["alt"]:
                flags.append("EMPTY ALT (visible)")
            if img["nw"] and img["w"] and img["nw"] > img["w"] * 2.6:
                flags.append(f"oversized {img['nw']}px for {img['w']}px")
            if not img["attrs"].startswith("wh"):
                flags.append("no width/height")
            if flags:
                L.append(f"- img {img['src']}: {'; '.join(flags)} ({img['attrs']})")
        if m["targets"]:
            L.append(f"- small targets: {m['targets']}")
        bad_focus = [f for f in r["focus"] if f["hidden"] or not f["onscreen"] or not (f["outline"] or f["shadow"])]
        for f in bad_focus:
            L.append(f"- focus problem: {f['sig']} '{f['text']}' hidden={f['hidden']} onscreen={f['onscreen']} outline='{f['outline']}' shadow={f['shadow']}")
        L.append(f"- focus stops: {len(r['focus'])}")
        for v in r.get("axe", []):
            L.append(f"- axe {v['impact']}: {v['id']} ({v['help']}) {v['nodes']}")
        L.append(f"- head: {json.dumps(m['head'])}")
        L.append("")
    (out_dir(label) / "checks.md").write_text("\n".join(L), encoding="utf-8")
    print("wrote", out_dir(label) / "checks.md")


# ---------------------------------------------------------------- coverage

def coverage(label):
    used = defaultdict(set)       # url -> set of (start,end) used
    all_rules = {}                # url -> {(start,end)}
    texts = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU_ARGS)
        for width in (390, 1440):
            for theme in ("light", "dark"):
                for inten in ("calm", "rain"):
                    ctx = new_context(b, width, theme, inten)
                    page = ctx.new_page()
                    cdp = ctx.new_cdp_session(page)
                    sheets = {}
                    cdp.on("CSS.styleSheetAdded", lambda e: sheets.__setitem__(e["header"]["styleSheetId"], e["header"]["sourceURL"]))
                    cdp.send("DOM.enable")
                    cdp.send("CSS.enable")
                    cdp.send("CSS.startRuleUsageTracking")
                    for name, path in PAGES.items():
                        load(page, path)
                        if width <= 430:
                            try:
                                page.click("#nav-burger", timeout=1500)
                                page.wait_for_timeout(300)
                                page.click("#nav-burger", timeout=1500)
                            except Exception:
                                pass
                    res = cdp.send("CSS.stopRuleUsageTracking")
                    for sid, url in sheets.items():
                        if url.endswith(".css") and url not in texts:
                            from urllib.request import urlopen
                            texts[url] = urlopen(url).read().decode("utf-8")
                    for u in res["ruleUsage"]:
                        url = sheets.get(u["styleSheetId"], "")
                        if not url.endswith(".css"):
                            continue
                        span = (int(u["startOffset"]), int(u["endOffset"]))
                        all_rules.setdefault(url, set()).add(span)
                        if u["used"]:
                            used[url].add(span)
                    ctx.close()
                    print("coverage", width, theme, inten, flush=True)
        b.close()
    L = ["# Rules never matched (any page, 390/1440, light/dark, calm/rain)",
         "State-only selectors (:hover, :focus, :active, :checked) are listed separately; they need a state to match.", ""]
    for url, spans in all_rules.items():
        text = texts.get(url, "")
        unused = sorted(spans - used[url])
        stateful, plain = [], []
        for s, e in unused:
            body = text[s:e]
            # walk back to the selector
            k = text.rfind("}", 0, s)
            k2 = text.rfind(";", 0, s)
            sel = text[max(k, k2) + 1:s].strip().split("{")[0].strip()
            sel = " ".join(sel.split())
            line = text.count("\n", 0, s) + 1
            (stateful if any(x in sel for x in (":hover", ":focus", ":active", ":checked", ":disabled")) else plain).append(f"- L{line}: `{sel[:140]}`")
        L.append(f"## {url.replace(BASE, '')}: {len(plain)} plain, {len(stateful)} state-only")
        L += plain
        L.append("")
        L.append("<details><summary>state-only</summary>")
        L.append("")
        L += stateful
        L.append("</details>")
        L.append("")
    (out_dir(label) / "coverage.md").write_text("\n".join(L), encoding="utf-8")
    print("wrote coverage.md")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    lab = sys.argv[2] if len(sys.argv) > 2 else "latest"
    if cmd in ("shots", "all"):
        shots(lab)
    if cmd in ("states", "all"):
        states(lab)
    if cmd in ("checks", "all"):
        checks(lab)
    if cmd in ("coverage", "all"):
        coverage(lab)
