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
    }
})();
