"""Dev-only rain/scenery perf harness. Two modes:

    python tools/perf_probe.py build            write _perf_*.html probe pages
    python tools/perf_probe.py serve [outfile]  serve repo root on :8123 with a
                                                /__log endpoint for results

Each probe page is a copy of index.html that forces one effect config
(via window.__rainDebug and/or injected CSS), then auto-scrolls the page
for ~10s while sampling requestAnimationFrame deltas, and POSTs the
stats to /__log. Run each page in a HEADED browser (real GPU path;
headless uses a different compositing path and lies about this).

Probe files are gitignored (_*.html). Nothing here ships.
"""

import json
import sys
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent

# name -> (rainDebug dict or None, extra CSS or "", [intensity])
# intensity defaults to "rain" when the tuple has two entries.
KILL_CHOREO = (".sd,.vl,.scene-track{animation:none !important;"
               "will-change:auto !important}")
KILL_FIXED = (".fx-haze{display:none !important}"
              "body::after{display:none !important}")
CONFIGS = {
    # atmosphere round: WebGL precip (primary) vs CSS fallback vs off
    "glr":       (None, ""),                                  # WebGL rain, shipped
    "glf":       (None, "", "fog"),                           # WebGL fog, shipped
    "cssr":      ({"forceCSS": True}, ""),                    # CSS fallback: 1 sheet
    "cssr2":     ({"forceCSS": True, "sheets": 2}, ""),       # old 2-sheet baseline
    "noprecip":  ({"off": True}, ""),                         # floor
    "glr_dpr1":  ({"scale": 1}, ""),                          # DPR sensitivity
    "glr_30":    ({"fps": 30}, ""),                           # fps-cap headroom
    "glr_nodew": (None, ".fx-dew{display:none !important}"),  # dew delta
    "off":         ({"off": True}, ""),
    "cur2lin":     (None, ""),                       # shipped default (historic name)
    "s1lin":       ({"sheets": 1}, ""),
    "s2q24":       ({"stepsPerSec": 24}, ""),
    "s2q30":       ({"stepsPerSec": 30}, ""),
    "s3lin":       ({"sheets": 3}, ""),
    "off_nochoreo": ({"off": True}, KILL_CHOREO),    # attributes scene-layer cost
    "off_nofixed": ({"off": True}, KILL_FIXED),      # attributes haze + grain cost
    # round 2: is ONE scroll-driven layer cheap? is rain free sans choreo?
    "trackonly":   ({"off": True},
                    ".sd,.vl{animation:none !important;will-change:auto !important}"),
    "rain2_nochoreo": (None, KILL_CHOREO),
    "parting4":    ({"off": True},
                    ".sd-1,.sd-2,.sd-5,.sd-6,.sd-7,.sd-dusk"
                    "{animation:none !important;will-change:auto !important}"),
    # round 4: rain layer AREA + grain cost (per-layer choreography is
    # already retired, so these run against the shipped track drift)
    "r4_2s1024":   (None, ""),
    "r4_2s512":    ({"tileH": 512}, ""),
    "r4_1s1024":   ({"sheets": 1}, ""),
    "r4_1s512":    ({"sheets": 1, "tileH": 512}, ""),
    "r4_1s512_ng": ({"sheets": 1, "tileH": 512},
                    "body::after{display:none !important}"),
    "r4_off":      ({"off": True}, ""),
    # candidate ship config: track + sd-3/sd-4 parting + m1 fade (4 animated)
    "ship4":       (None,
                    ".sd-1,.sd-2,.sd-5,.sd-6,.sd-7,.sd-dusk,.sd-m2,.sd-m3"
                    "{animation:none !important;will-change:auto !important}"),
    # same but also without the film grain + haze (how much more headroom?)
    "ship4_lean":  (None,
                    ".sd-1,.sd-2,.sd-5,.sd-6,.sd-7,.sd-dusk,.sd-m2,.sd-m3"
                    "{animation:none !important;will-change:auto !important}"
                    + KILL_FIXED),
    # round 3 bisect: count vs kind of animated layer
    "b_track_rain2": (None,
                      ".sd,.vl{animation:none !important;will-change:auto !important}"),
    "b_part3_norain": ({"off": True},
                       ".sd:not(.sd-3):not(.sd-4)"
                       "{animation:none !important;will-change:auto !important}"),
    "b_part3_rain2": (None,
                      ".sd:not(.sd-3):not(.sd-4)"
                      "{animation:none !important;will-change:auto !important}"),
    "b_part_m1_norain": ({"off": True},
                         ".sd:not(.sd-3):not(.sd-4):not(.sd-m1)"
                         "{animation:none !important;will-change:auto !important}"),
    "b_m1only_norain": ({"off": True},
                        ".sd:not(.sd-m1)"
                        "{animation:none !important;will-change:auto !important}"),
}

MEASURE_JS = """
<script>
window.addEventListener("load", function () {
    setTimeout(function () {
        var max = document.documentElement.scrollHeight - innerHeight;
        var t0 = performance.now(), DUR = 10000, deltas = [], last = t0;
        function frame(t) {
            var d = t - last; last = t;
            if (d > 0 && d < 2000) deltas.push(d);
            var p = (t - t0) / DUR;
            if (p >= 1) return report();
            var ph = (p * 2) % 1;   /* two down-up passes */
            var y = (ph < 0.5 ? ph * 2 : 2 - ph * 2) * max;
            scrollTo(0, y);
            requestAnimationFrame(frame);
        }
        function report() {
            deltas.shift();
            var s = deltas.slice().sort(function (a, b) { return a - b; });
            var q = function (p) { return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
            var avg = deltas.reduce(function (a, b) { return a + b; }, 0) / deltas.length;
            var over25 = deltas.filter(function (d) { return d > 25; }).length;
            var over50 = deltas.filter(function (d) { return d > 50; }).length;
            fetch("/__log?name=NAME&hz=" + Math.round(1000 / q(0.5))
                + "&avg=" + avg.toFixed(2) + "&p95=" + q(0.95).toFixed(2)
                + "&max=" + Math.max.apply(null, deltas).toFixed(1)
                + "&over25=" + over25 + "&over50=" + over50
                + "&n=" + deltas.length
            ).then(function () { document.title = "PROBE-DONE"; });
        }
        requestAnimationFrame(frame);
    }, 1800);
});
</script>
"""


def build():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    for name, cfg in CONFIGS.items():
        dbg, css = cfg[0], cfg[1]
        intensity = cfg[2] if len(cfg) > 2 else "rain"
        inject = ('<script>localStorage.setItem("theme","dark");'
                  f'localStorage.setItem("intensity","{intensity}");</script>')
        if dbg is not None:
            inject += f"<script>window.__rainDebug = {json.dumps(dbg)};</script>"
        if css:
            inject += f"<style>{css}</style>"
        inject += MEASURE_JS.replace("NAME", name)
        out = ROOT / f"_perf_{name}.html"
        out.write_text(src.replace("<head>", "<head>" + inject, 1), encoding="utf-8")
        print("wrote", out.name)


def serve(outfile):
    out = Path(outfile)

    class H(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/__log"):
                row = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
                with out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
                self.send_response(204)
                self.end_headers()
                return
            return super().do_GET()

        def log_message(self, *a):
            pass

    HTTPServer(("127.0.0.1", 8123), partial(H, directory=str(ROOT))).serve_forever()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    if mode == "build":
        build()
    else:
        serve(sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "_perf_results.jsonl"))
