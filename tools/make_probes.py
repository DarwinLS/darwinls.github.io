"""Dev-only: build _probe_*.html copies of the real pages with injected
theme/intensity/scroll/pointer overrides for headless-Edge screenshots.
Probe files are gitignored (_*.html). Not part of the site build."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONFIGS = [
    # (out name, source, theme, intensity, margin_top_px, coarse)
    ("_p_home_hero_light.html", "index.html", "light", "balanced", 0, False),
    ("_p_home_hero_dark.html", "index.html", "dark", "balanced", 0, False),
    ("_p_home_mid_light.html", "index.html", "light", "balanced", 1600, False),
    ("_p_home_bot_light.html", "index.html", "light", "balanced", 3094, False),
    ("_p_home_bot_dark.html", "index.html", "dark", "balanced", 3094, False),
    ("_p_home_coarse.html", "index.html", "light", "balanced", 0, True),
    ("_p_home_calm.html", "index.html", "light", "calm", 0, False),
    ("_p_about_light.html", "about.html", "light", "balanced", 0, False),
    ("_p_projects_light.html", "projects.html", "light", "balanced", 0, False),
    ("_p_contact_light.html", "contact.html", "light", "balanced", 0, False),
    ("_p_veraflux_light.html", "veraflux.html", "light", "balanced", 0, False),
    ("_p_projects_bot_light.html", "projects.html", "light", "balanced", 1971, False),
    # mobile-width poses (headless floors the window at ~474px)
    ("_p_m_home_mid.html", "index.html", "light", "balanced", 1000, False),
    ("_p_m_home_low.html", "index.html", "light", "balanced", 2100, False),
    ("_p_m_home_bot.html", "index.html", "light", "balanced", 2906, False),
    ("_p_m_about_mid.html", "about.html", "light", "balanced", 700, False),
]

COARSE_JS = """
<script>
(function () {
    var native = window.matchMedia.bind(window);
    window.matchMedia = function (q) {
        if (q.indexOf("pointer: coarse") !== -1) {
            return { matches: true, media: q, addEventListener: function(){}, removeEventListener: function(){}, addListener: function(){}, removeListener: function(){} };
        }
        if (q.indexOf("pointer: fine") !== -1) {
            return { matches: false, media: q, addEventListener: function(){}, removeEventListener: function(){}, addListener: function(){}, removeListener: function(){} };
        }
        return native(q);
    };
})();
</script>
"""

PROBE_JS = """
<script>
window.addEventListener("load", function () {
    setTimeout(function () {
        var scene = document.querySelector(".scene-descent, .vista");
        var track = document.querySelector(".scene-track");
        console.log("[probe] scrollWidth=" + document.documentElement.scrollWidth
            + " innerWidth=" + window.innerWidth
            + " scrollHeight=" + document.documentElement.scrollHeight
            + " rainSheets=" + document.querySelectorAll(".fx-rain-move").length
            + " slantWrappers=" + document.querySelectorAll(".fx-rain-slant").length
            + " fxHidden=" + document.querySelectorAll(".fx-hidden").length
            + " trackAnim=" + (track ? getComputedStyle(track).animationName : "none")
            + " sceneH=" + (scene ? Math.round(scene.getBoundingClientRect().height) : -1)
            + " innerHeight=" + window.innerHeight);
    }, 400);
});
</script>
"""


def build(out, src, theme, intensity, margin, coarse):
    html = (ROOT / src).read_text(encoding="utf-8")
    inject = f'<script>localStorage.setItem("theme","{theme}");localStorage.setItem("intensity","{intensity}");</script>'
    if coarse:
        inject += COARSE_JS
    if margin:
        # fake a scrolled pose: content shifts up, fixed layers stay put
        inject += f"<style>body{{margin-top:-{margin}px}}</style>"
    inject += PROBE_JS
    html = html.replace("<head>", "<head>" + inject, 1)
    (ROOT / out).write_text(html, encoding="utf-8")
    print("wrote", out)


for cfg in CONFIGS:
    build(*cfg)
