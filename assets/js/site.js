/* Phase 1 UI: theme toggle + mobile drawer.
   The no-FOUC theme is set by a tiny inline <head> script before paint;
   this file only wires the interactive controls. */
(function () {
    "use strict";
    var root = document.documentElement;

    /* --- Theme toggle (light <-> dark, persisted) --- */
    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
        toggle.addEventListener("click", function () {
            var next = root.dataset.theme === "dark" ? "light" : "dark";
            root.dataset.theme = next;
            try { localStorage.setItem("theme", next); } catch (e) {}
            toggle.setAttribute(
                "aria-label",
                next === "dark" ? "Switch to light theme" : "Switch to dark theme"
            );
        });
    }

    /* --- Ambience dial (Calm / Fog / Rain) ---
       The user picks a weather mode; the device caps how far it can go
       (low-end / reduced-motion clamps to Calm). This scaffold sets
       [data-intensity] (effective) + [data-pref] (chosen) on <html> so
       effects can gate on the mode.
       Pairs with the no-FOUC inline script that sets both before paint. */
    (function () {
        var LEVELS = ["calm", "fog", "rain"];
        var LABELS = { calm: "Calm", fog: "Fog", rain: "Rain" };

        // Highest level this device should ever run (independent of choice).
        function ceiling() {
            var conn = navigator.connection || {};
            var cores = navigator.hardwareConcurrency || 8;
            var mem = navigator.deviceMemory || 8;
            if (matchMedia("(prefers-reduced-motion: reduce)").matches ||
                conn.saveData || cores <= 2 || mem <= 2) return "calm";
            // CPU compositing: fog still works (static banks, drift and
            // rain stay off), so the dial keeps doing something visible.
            if (root.dataset.gpu === "soft") return "fog";
            return "rain";
        }
        function clamp(pref) {
            return LEVELS[Math.min(LEVELS.indexOf(pref), LEVELS.indexOf(ceiling()))];
        }
        function readPref() {
            var p = root.dataset.pref;
            if (LEVELS.indexOf(p) < 0) { try { p = localStorage.getItem("intensity"); } catch (e) {} }
            // Stored values from the old Calm/Balanced/Immersive dial.
            if (p === "balanced") p = "fog";
            else if (p === "immersive") p = "rain";
            return LEVELS.indexOf(p) < 0 ? "rain" : p;
        }

        var btn = document.getElementById("intensity-toggle");

        function apply(pref) {
            var eff = clamp(pref);
            root.dataset.pref = pref;
            root.dataset.intensity = eff;
            if (btn) {
                var msg = "Ambience: " + LABELS[pref];
                if (eff !== pref) msg += " (limited to " + LABELS[eff] + " on this device)";
                btn.setAttribute("aria-label", msg + ". Click to change.");
                btn.setAttribute("title", msg);
            }
        }

        apply(readPref());

        if (btn) {
            btn.addEventListener("click", function () {
                var next = LEVELS[(LEVELS.indexOf(readPref()) + 1) % LEVELS.length];
                try { localStorage.setItem("intensity", next); } catch (e) {}
                apply(next);
            });
        }

        // Re-clamp live when the environment changes (OS reduced-motion)
        // so an accessibility toggle applies without a reload.
        ["(prefers-reduced-motion: reduce)"].forEach(function (q) {
            var m = matchMedia(q);
            var on = function () { apply(readPref()); };
            if (m.addEventListener) m.addEventListener("change", on);
            else if (m.addListener) m.addListener(on);
        });

        // Software-GPU sniff. When the browser composites on the CPU
        // (e.g. Chrome with "hardware acceleration unavailable", which
        // reports a SwiftShader WebGL renderer), backdrop blur and rain
        // rasterize per frame on the main processor and everything
        // lags. Probing a GL context costs ~10ms, so it runs after
        // first paint; the verdict persists (localStorage "gpusoft")
        // so the no-FOUC script clamps instantly on later visits, and
        // re-probing every load self-heals after a driver/settings fix.
        setTimeout(function () {
            var soft = false;
            try {
                var cv = document.createElement("canvas");
                var gl = cv.getContext("webgl") || cv.getContext("experimental-webgl");
                if (gl) {
                    var info = gl.getExtension("WEBGL_debug_renderer_info");
                    var rend = info ? String(gl.getParameter(info.UNMASKED_RENDERER_WEBGL)) : "";
                    soft = /swiftshader|llvmpipe|software/i.test(rend);
                    var lose = gl.getExtension("WEBGL_lose_context");
                    if (lose) lose.loseContext();
                }
            } catch (e) {}
            try {
                if (soft) localStorage.setItem("gpusoft", "1");
                else localStorage.removeItem("gpusoft");
            } catch (e) {}
            var was = root.dataset.gpu === "soft";
            if (soft !== was) {
                if (soft) root.dataset.gpu = "soft";
                else delete root.dataset.gpu;
                apply(readPref());
            }
        }, 0);
    })();

    /* --- Graceful scroll cue ---
       Eased rAF tween instead of the native jump. The anchor href is
       the no-JS fallback; reduced-motion keeps the native behavior. */
    var cue = document.querySelector(".scroll-cue");
    if (cue) {
        cue.addEventListener("click", function (e) {
            if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
            var target = document.querySelector(cue.getAttribute("href"));
            if (!target) return;
            e.preventDefault();
            var navH = parseFloat(getComputedStyle(root).getPropertyValue("--nav-height")) || 0;
            var from = window.scrollY;
            var to = target.getBoundingClientRect().top + from - navH;
            var dur = 900, t0 = performance.now();
            (function step(t) {
                var p = Math.min(1, (t - t0) / dur);
                /* ease-in-out cubic */
                var eased = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
                window.scrollTo(0, from + (to - from) * eased);
                if (p < 1) requestAnimationFrame(step);
            })(t0);
        });
    }

    /* --- Hero pane specular ---
       A pointer-lit highlight inside the glass CTAs. Fine hover
       pointers only, and never under reduced motion; the span is
       injected here so touch devices and no-JS never carry it. The
       pointermove writes two custom props consumed by one gradient,
       so each move is paint-only damage on a small isolated layer. */
    if (matchMedia("(hover: hover) and (pointer: fine)").matches &&
        !matchMedia("(prefers-reduced-motion: reduce)").matches) {
        document.querySelectorAll(".hero .btn").forEach(function (btn) {
            var spec = document.createElement("span");
            spec.className = "btn-spec";
            spec.setAttribute("aria-hidden", "true");
            btn.appendChild(spec);
            var rect = null;
            btn.addEventListener("pointerenter", function () {
                rect = btn.getBoundingClientRect();
            });
            btn.addEventListener("pointermove", function (e) {
                if (!rect) rect = btn.getBoundingClientRect();
                btn.style.setProperty("--mx", (e.clientX - rect.left).toFixed(1) + "px");
                btn.style.setProperty("--my", (e.clientY - rect.top).toFixed(1) + "px");
            }, { passive: true });
        });
    }

    /* --- Mobile hamburger drawer --- */
    var burger = document.getElementById("nav-burger");
    if (burger) {
        var setMenu = function (open) {
            root.dataset.menu = open ? "open" : "";
            burger.setAttribute("aria-expanded", String(open));
            burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        };
        burger.addEventListener("click", function () {
            setMenu(root.dataset.menu !== "open");
        });
        // Close on link tap or Escape
        document.querySelectorAll("#nav-links a").forEach(function (a) {
            a.addEventListener("click", function () { setMenu(false); });
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && root.dataset.menu === "open") setMenu(false);
        });
        // Close on any tap outside the panel (the dim scrim is a header
        // pseudo-element, so scrim taps land here too).
        document.addEventListener("click", function (e) {
            if (root.dataset.menu !== "open") return;
            if (e.target.closest("#nav-links") || e.target.closest("#nav-burger")) return;
            setMenu(false);
        });
        // Auto-close when the viewport grows past the drawer breakpoint.
        var wide = matchMedia("(min-width: 821px)");
        var onWide = function () { if (wide.matches) setMenu(false); };
        if (wide.addEventListener) wide.addEventListener("change", onWide);
        else if (wide.addListener) wide.addListener(onWide);
    }
})();
