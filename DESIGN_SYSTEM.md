# The visual system

This site is a landscape you descend. Every surface is a pane of glass held in
front of that landscape, and everything in this document follows from those two
sentences.

It is written for someone who did not build the site and now has to change it
without breaking it. It says what the rules are, why each one exists, which ones
are deliberately broken, and what checks will catch you if you break one by
accident.

Figures in this document are measurements of the tree on 2026-09-22, and most of
them are re-derived on every run by `tools/design_guard.py`. If a number here
disagrees with the guard, the guard is right.

---

## 1. How the stylesheet is made

`styles.css` (3,230 lines) is **generated, not hand written**. It is assembled
from a reviewed source plus a chain of refinement passes:

```
_private/styleguide/v4.css          the system, authored
  + refine-1.css … refine-5.css     reviewed rounds, applied in order
  → _private/styleguide/finalize.py
  → styles.css
```

Two more generators write into the tree:

| Command | Writes |
|---|---|
| `python _private/styleguide/finalize.py` | `styles.css` |
| `python tools/scene_gen.py` | `assets/scenes/*.html`, the five SVG landscapes |
| `python tools/partials.py` | the shared head, nav, footer and card blocks in every page |
| `python tools/make_icons.py` | `favicon.svg`, `favicon.ico`, `apple-touch-icon.png` |

A full rebuild is those four in that order.

> **Editing `styles.css` by hand is always wrong.** The next `finalize.py` run
> will overwrite it and the change will vanish with no error. Edit `v4.css` or
> the last refine file, then rebuild.

### The honest caveat

`_private/` is gitignored, so **the token source is not published and CI cannot
verify that `styles.css` matches it**. The guard therefore checks the built
artefact, which is the thing that actually ships, rather than the source.

That is a real weakness rather than a design choice. `v4.css` and the refine
chain contain no private information; they live under `_private/` only because
that is where the styleguide lab was built. Moving the CSS sources and
`finalize.py` into a public `styleguide/` directory would let CI rebuild and
diff, turning "do not hand edit" from a convention into something enforced.

---

## 2. Foundations

205 custom properties are declared across the shipped stylesheets, 199 of them in
`styles.css`, with 120 in the root token block. Everything below is one of them.

### Colour

Colour is written **once**, with `light-dark()`. There is no parallel dark theme
to keep in sync; the pair lives in the token itself.

```css
--ink:    light-dark(#19211c, #e7ece4);
--amber:  light-dark(#c8772e, #e0913f);
```

Only the handful of *non-colour* values that genuinely differ after dark get a
second block, under the heading `Night numbers`: glass saturation, glass
contrast, grain opacity, fog strength. Five values, twice (once for the pinned
`[data-theme="dark"]`, once for the OS preference), and nothing else.

The palette is named after the landscape, not after its use:

- **Surfaces and ink**: `--paper`, `--raised`, `--sunken`, `--ink`, `--ink-2`, `--ink-3`
- **Nature**: `--pine`, `--moss`, `--fern`, `--mist`, `--bark`, `--bark-deep`, `--amber`, `--amber-soft`, `--moss-gold`
- **Text roles**: `--accent-ink`, `--eyebrow-ink`, `--pine-ink`, `--on-pine`

**Text roles exist because the landscape colours do not pass contrast as text.**
`--amber` is a fill and a mark, never a word. `--accent-ink` is the amber that
holds 4.5:1 on paper and on every glass tint in both themes, and it is a
noticeably different colour (`#7a3f12` by day) for exactly that reason. Reaching
for `--amber` on a text node is the single easiest way to fail an audit here.

### Type

Two faces, both self-hosted variable woff2: **Fraunces** for display, **Inter**
for body and UI. Ten size steps, fluid where fluidity helps:

| Token | Value |
|---|---|
| `--fs-label` | `0.75rem` |
| `--fs-small` | `0.875rem` |
| `--fs-body` | `1rem` |
| `--fs-prose` | `clamp(1rem, 0.95rem + 0.22vw, 1.0938rem)` |
| `--fs-lead` | `clamp(1.0938rem, 1rem + 0.45vw, 1.3125rem)` |
| `--fs-h3` | `clamp(1.1875rem, 1.1rem + 0.35vw, 1.375rem)` |
| `--fs-h2` | `clamp(1.5rem, 1.2rem + 1.1vw, 2.125rem)` |
| `--fs-statement` | `clamp(1.625rem, 1.2rem + 1.7vw, 2.5rem)` |
| `--fs-h1` | `clamp(2.125rem, 1.5rem + 2.6vw, 3.625rem)` |
| `--fs-display` | `clamp(2.75rem, 1.7rem + 4.4vw, 5rem)` |

Plus four leading tokens (`--lh-tight` 1.12 through `--lh-prose` 1.68) and three
tracking tokens. Headings take `text-wrap: balance`; prose takes `pretty`.

### Space, layout, shape

Space is a single named ramp, `--space-1` (0.25rem) through `--space-20` (5rem),
skipping the steps nothing needed. Layout is six tokens: `--page-max` at
**1120px**, a fluid `--gutter`, a `--band-gap`, the nav height pair `--nav-h` and
`--nav-top`, and `--nav-offset` computed from those two.

Shape is five steps and nothing else:

```css
--r-xs: 6px;  --r-sm: 10px;  --r-md: 16px;  --r-lg: 22px;  --r-pill: 999px;
```

**Nested corners are computed, never picked.** An inner radius is the outer
radius minus the padding between them, written as a `calc()`, so the two arcs
stay concentric when either value moves.

### Elevation

One light source, above and slightly to the left, for the whole site. Three
shadow tints feed three elevation tokens (`--elev-1`, `--elev-2`, `--elev-3`),
each a contact shadow plus an ambient shadow. Nothing composes its own shadow
stack except the glass materials and the keycap buttons, both of which are
documented at their definition.

### Motion

Four easings and four durations. `--ease-settle` for anything arriving,
`--ease-drift` for ambience, `--ease-draw` for stroke reveals, `--ease-exit` for
anything leaving. No raw durations, and no `transition: all`.

### Focus

One ring for the entire site:

```css
:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 3px; }
:where(a, button, [tabindex]):focus-visible { box-shadow: var(--focus-glow); }
```

`outline` follows `border-radius` natively, so the ring takes each element's own
corners with no per-component work. The ring is amber and it is the only amber
that appears on a focused element.

---

## 3. Materials

This is the part of the system that is not generic. Four materials, and a rule
about how they stack.

| Material | Where it goes | What it is |
|---|---|---|
| `.glass` | nav, bands, plates, buttons | a thin tint over a blurred, graded backdrop |
| `.glass-paper` | reading columns, case-study sections | the same edges over a near-opaque frost |
| `.inset` | anything sitting inside glass | a frosted inlay with no backdrop of its own |
| `.well` | specimens, code, diagrams | a recessed version of the inlay |

### The one structural rule: glass is never nested in glass

Two stacked `backdrop-filter` layers blur the already-blurred, which reads as
mud, and each one costs a full-surface GPU pass. Anything that needs to sit
inside a pane uses `.inset` or `.well`, which have the same edge language and no
backdrop. `.inset` exists only to make this rule easy to follow.

### What a pane is made of

A clear pane is six layers, in order from the back:

1. **Backdrop**: `blur` + `saturate` + `contrast` + `brightness`. On Chromium a
   displacement map is prefixed so the edge refracts.
2. **Tint**: `--glass-tint`, a warm frost by day, a lifted warm grey at night so
   panes separate from dark scenery.
3. **Grain**: an inline SVG `feTurbulence` frost, `--frost`.
4. **Sky reflection**: a gradient on the upper face.
5. **Edge work** (`box-shadow`): a lit top lip, a shaded base, a hairline of
   thickness, and two 1.5px dispersion fringes, cool on the lit side and warm on
   the shaded side.
6. **Rims** (`::before` and `::after`, both masked rings): an outer conic rim
   that is brightest where the light enters at 225deg and glints where it
   leaves, and a back-face rim inset 3px, which is the far edge of the slab seen
   through its own thickness.

Text on clear glass takes **one step deeper ink** than it would on paper, because
light frost lets dark scenery through. Panes that carry body text take a denser
tint again (`.glass.panel`), so small text still holds 4.5:1 over the darkest
part of the forest. Frames with no body text, the nav bar and screenshot mounts,
stay light.

`.glass--frame` adds the shoji detail: a quiet timber line set 11px inside the
pane, drawn with `outline-offset: -11px` so it follows the radius.

### Capability tiers

The same pane degrades through four tiers, each defined once:

| Tier | Condition | Treatment |
|---|---|---|
| 1 | Chromium, fine pointer, hardware GPU | refraction; `glass.js` sets `--refract` |
| 2 | other browsers | full optics with blur, no bending |
| 3 | coarse pointer on large panels, software GPU, no `backdrop-filter`, `prefers-reduced-transparency` | tint only, no blur |
| 4 | no `light-dark()` | flat day palette, toggle hidden |

Tier 3 exists for two different reasons that happen to want the same answer:
blurring a full-width panel is expensive on a phone, and some people have asked
their OS not to show transparency.

---

## 4. Components

One of each, used everywhere.

- **`.btn`, a keycap.** A key top standing on a side wall, with variants
  `.btn--primary`, `.btn--secondary`, `.btn--quiet` and a `.btn--sm` size. Depth
  is a single `--b-depth` token: on hover the cap rises by exactly what the
  wall grows, so the foot line never moves. Every state is one shadow list, which is what stops
  a later rule from overriding half of a button.
- **`.eyebrow`** is the only uppercase label. **`.meta-label`** is the only small
  caps-style key in a key/value row.
- **`.link`** underlines at 1px and thickens to 2px on hover, so links are never
  marked by colour alone. **`.link-arrow`** carries an SVG chevron that nudges.
- **`.chip`** is a pill on inset fill, for tech stacks, skills and pillars.
- **`.card`** is an inset inlay. Link cards lift on hover; non-link cards do not,
  which is the site's only signal that a card is or is not clickable.
- **`.section-head`** is the single section header pattern: eyebrow, heading,
  optional action. **`.actions`** is the single call-to-action row.
- **`.list`** is the pebble-bulleted list. **`.mount`** is the single screenshot
  frame. **`.rule-title`** is a heading followed by a hairline that fades out to
  the right, and is the only horizontal rule on the site.
- **`.rail`** is the reading layout: at 960px and up, a section puts its label
  and title in a left column beside the opening paragraph, prose continues at a
  reading measure, and `.rail-wide` figures take a full row in source order.

---

## 5. Themes, biomes and scenery

**Theme resolution**: a stored choice wins; otherwise the OS preference. The head
script sets `data-theme` only when something is stored, so a visitor with no
choice gets `color-scheme: light dark` and the OS decides. There is no
time-of-day default.

**Biomes** retint the sky per section by overriding `--sky-1` and `--sky-2` on
`[data-biome]`. Four values are in use: `home`, which keeps the default valley
sky, and `projects`, `about` and `veraflux`, which each retint it.

**Scenery** is five generated SVG landscapes in `assets/scenes/`, written by
`tools/scene_gen.py` (1,802 lines). They are `position: fixed` behind the page at
`z-index: -2`, which is why the glass has something to show and also why
screenshot diffing a scrolled region of this site does not work: the scene does
not move with the content.

Drawn elements across the scenery share one stroke language. In dark mode a crest
rim (`--crest-stroke`) separates canopy silhouettes that would otherwise merge;
by day it resolves to `transparent`, because the light ramp already separates
them. Footer land, scrub and rocks take the same stroke token, so the footer and
the hero read as one illustration.

---

## 6. Content rules

These are not about pixels, and they are enforced alongside the visual rules
because breaking one is just as visible.

- **No em dashes and no en dashes** in page prose. Currently zero of each.
- **The identity string is fixed**: `Software Engineer &amp; Product Designer`,
  in that order, wherever it is used as a label. Running prose may spell out
  "and", which the meta description and the Open Graph alt text both do.
- **Specimens are product exact.** A screenshot or reproduction of the Veraflux
  UI shows what the product shows, including states that are less flattering. A
  specimen is evidence, and evidence that has been tidied is not evidence.
- **Numbers are measured, never estimated.** Figures that appear on the site are
  traceable to `_private/CAREER_VERIFIED_FACTS.md`.
- **Every page carries the same head**: language, description, canonical, theme
  colour, both icons, Open Graph title and image, Twitter card, skip link.

---

## 7. The one exemption

**`specimens.css` does not answer to this system.** It reproduces the Veraflux
product UI, so it carries the product's colours, radii and type, which are not
this site's. Its 32 raw colour declarations and 9 literal radii, counted the same way the
guard counts them everywhere else, are correct as written, and making them use
portfolio tokens would make the specimens lie.

The guard excludes it from every token rule for that reason. It is the only file
with that status.

---

## 8. How it is checked

### `tools/design_guard.py`

Static, no browser, no network, reads only committed files, so it runs the same
locally and in CI (`.github/workflows/design-guard.yml`, on push and pull
request).

```
python tools/design_guard.py [--verbose]
```

Nine guards:

| Guard | Catches |
|---|---|
| publish boundary | `_private/`, the unpublished infrastructure resume, or a `.tex` source entering git |
| token hygiene | a `var()` nothing declares, a token nothing reads, a stale allowlist entry |
| radius scale | a literal `border-radius` outside the two documented exceptions |
| colour in the token layer | a raw hex used as a value rather than declared as a token |
| specificity hatches | a new `!important` |
| breakpoint drift | a sixteenth distinct width threshold |
| prose rules | an em dash, an en dash, a drifted identity string |
| page head | a page missing any of the ten required head elements |
| asset references | an `/assets/` path with no file behind it |

Some of these are absolute and some are **ratchets**: a count that is allowed to
be non-zero today because the code already carries that much debt, pinned so it
can only fall. Every ceiling in the file is a measurement with a comment saying
what the remainder is and why. Lowering one is ordinary work. Raising one needs a
reason in the commit message.

Each guard has been verified to fail on a matching regression, not just to pass
on the current tree.

### `tools/design_audit.py`

The heavier pass, needing Playwright and a local server. It writes to
`_private/audit/<label>/`.

`checks <label>` walks all 7 pages at 390 and 1440, light and dark. It measures
contrast against the pixels actually rendered behind each text node, which is the
only honest way to measure text on glass; runs axe-core; censuses computed font
sizes, radii, shadows, borders, backdrops and off-token colours; walks the tab
order checking that every stop has a visible ring and nothing hidden is
reachable; and looks for horizontal overflow and block misalignment.

`shots <label>` captures 17 combinations of each page: 5 widths in both themes,
plus OS-dark, plus rain at two widths, plus WebKit and Firefox at 1440 in both
themes, which is how the fallback tiers get looked at.

It is not in CI because it needs a browser and a server. Current state: 0
contrast failures, 0 serious or critical axe violations, 0 horizontal overflow.

The tap-target warnings it prints at 1440 are expected. Targets are sized for the
pointer: `@media (pointer: coarse)` takes buttons, icon buttons, footer links and
the footer email to 2.75rem, and a keyboard user on a fine pointer gets a focus
ring that fits the text instead.

### Where the reasoning lives

`_private/research/design-audit-2026-09-17.md` (1,599 lines) records every round:
what was measured, what the measurement showed, what changed, and which proposed
changes were rejected after the measurement contradicted them. Several entries
are records of being wrong, which are the useful ones.

---

## 9. Known debt

Listed because an undocumented compromise is indistinguishable from a mistake.
Each is pinned by a ratchet, so none of them can grow quietly.

| Debt | Size | Why it is there |
|---|---|---|
| Raw colours in `styles.css` | 25 declarations | The footer and the scene ink sit on painted artwork rather than on `--paper`, so their colours were picked against the illustration and have no token yet. A `--footer-*` ink group would absorb all of them. |
| Width breakpoints | 15 distinct values | Drift, not a scale: 380, 400, 480, 600, 640, 700, 720, 721, 899, 900, 959, 960, 1000, 1100, 1199. Consolidating to four or five named steps is the fix. |
| Declared and unused tokens | 13 | Four nature colours kept for palette completeness, four left from a glass recipe that shipped differently, and five odds. Listed by name in the guard. |
| `!important` | 10 total | All inside `prefers-reduced-motion` and `forced-colors` blocks, where the rule has to beat an inline style or a running animation. This is the legitimate use. |
| Token source unpublished | see §1 | CI cannot verify `styles.css` against `v4.css`. |

---

## 10. Changing something

1. Edit `_private/styleguide/v4.css`, or the last refine file if the change is a
   later round.
2. Rebuild: `finalize.py`, then `scene_gen.py`, then `partials.py`.
3. Run `python tools/design_guard.py`. It is fast and it runs offline.
4. If the change touches colour, contrast or layout, run
   `python tools/design_audit.py checks <label>` against the local server.
5. If you added a value that is not a token, either make it a token or add it to
   the right ratchet with a comment explaining why it is not one. Do not widen a
   guard silently.
