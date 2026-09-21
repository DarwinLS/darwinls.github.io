/* Phase 1 UI: theme toggle + mobile drawer.
   The no-FOUC theme is set by a tiny inline <head> script before paint;
   this file only wires the interactive controls. */
(function () {
    "use strict";
    var root = document.documentElement;

    /* --- Theme toggle (light <-> dark, persisted) ---
       First visits follow the OS (no data-theme, CSS light-dark()). A
       click pins the opposite of what is showing and remembers it.
       A same-document View Transition softly dissolves the page while
       a faint golden-hour bloom (.fx-dusk) rises and fades. Reduced
       motion, soft GPU, and browsers without the API swap instantly. */
    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
        var dusk = document.querySelector(".fx-dusk");
        var osDark = matchMedia("(prefers-color-scheme: dark)");
        var isDark = function () {
            var t = root.dataset.theme;
            return t ? t === "dark" : osDark.matches;
        };
        /* The browser-chrome tint follows the theme actually showing: pin
           both media variants of theme-color once a choice is stored. */
        var chrome = document.querySelectorAll('meta[name="theme-color"]');
        var label = function () {
            var dark = isDark();
            toggle.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
            /* the icon shows the current theme, so the tip names the switch */
            toggle.dataset.tip = dark ? "Switch to light" : "Switch to dark";
            if (root.dataset.theme) {
                chrome.forEach(function (m) { m.setAttribute("content", dark ? "#0e1512" : "#edf0ec"); });
            }
        };
        label();
        if (osDark.addEventListener) osDark.addEventListener("change", label);

        var swapTheme = function (next) {
            root.dataset.theme = next;
            try { localStorage.setItem("theme", next); } catch (e) {}
            label();
        };

        toggle.addEventListener("click", function () {
            var next = isDark() ? "light" : "dark";
            var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
            var soft = root.dataset.gpu === "soft";

            if (!document.startViewTransition || reduce || soft) {
                swapTheme(next);
                return;
            }

            root.dataset.vtTheme = "1";
            var vt = document.startViewTransition(function () {
                swapTheme(next);
                if (dusk) dusk.style.opacity = "1";
            });
            vt.ready.then(function () {
                if (dusk) {
                    dusk.style.opacity = "";
                    root.animate(
                        { opacity: [0, 0.9, 0] },
                        { duration: 600, easing: "ease-in-out",
                          pseudoElement: "::view-transition-new(vt-dusk)" }
                    );
                }
            });
            vt.finished.finally(function () { delete root.dataset.vtTheme; });
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
        var LABELS = { calm: "Calm, off", fog: "Fog", rain: "Rain" };

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
        var said = null;
        if (btn) {
            said = document.createElement("span");
            said.className = "visually-hidden";
            said.setAttribute("aria-live", "polite");
            btn.after(said);
        }

        function apply(pref, announce) {
            var eff = clamp(pref);
            root.dataset.pref = pref;
            root.dataset.intensity = eff;
            if (btn) {
                var msg = "Weather effects: " + LABELS[pref];
                if (eff !== pref) msg += " (limited to " + LABELS[eff] + " on this device)";
                btn.setAttribute("aria-label", msg);
                btn.dataset.tip = msg;
                if (announce && said) said.textContent = msg;
            }
        }

        apply(readPref());

        if (btn) {
            btn.addEventListener("click", function () {
                var next = LEVELS[(LEVELS.indexOf(readPref()) + 1) % LEVELS.length];
                try { localStorage.setItem("intensity", next); } catch (e) {}
                apply(next, true);
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
            var navH = parseFloat(getComputedStyle(document.body).scrollPaddingTop) || parseFloat(getComputedStyle(root).scrollPaddingTop) || 0;
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

    /* --- Copy-to-clipboard buttons ([data-copy]) ---
       The mailto link beside each button stays the no-JS path. The
       button's label span confirms, and a polite live region says it. */
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
        var text = btn.querySelector(".copy-label") || btn;
        var label = text.textContent;
        var timer = 0;
        var live = document.createElement("span");
        live.className = "visually-hidden";
        live.setAttribute("aria-live", "polite");
        btn.after(live);
        btn.addEventListener("click", function () {
            var done = function (ok) {
                text.textContent = ok ? "Copied" : "Copy failed";
                live.textContent = ok ? "Email address copied" : "Could not copy the email address";
                btn.dataset.state = ok ? "copied" : "failed";
                clearTimeout(timer);
                timer = setTimeout(function () {
                    text.textContent = label;
                    live.textContent = "";
                    delete btn.dataset.state;
                }, 2000);
            };
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(btn.getAttribute("data-copy")).then(function () { done(true); }, function () { done(false); });
            } else {
                done(false);
            }
        });
    });

    /* --- Mobile hamburger drawer --- */
    var burger = document.getElementById("nav-burger");
    if (burger) {
        /* The closed sheet is visibility:hidden (styles.css), so its links
           leave the tab order. Opening moves focus to the first link;
           tabbing out of the sheet, Escape, or a tap outside closes it. */
        var menu = document.getElementById("nav-links");
        var setMenu = function (open, focusFirst) {
            root.dataset.menu = open ? "open" : "";
            burger.setAttribute("aria-expanded", String(open));
            if (open && focusFirst && menu) {
                var first = menu.querySelector("a");
                if (first) setTimeout(function () { first.focus(); }, 30);
            }
        };
        burger.setAttribute("aria-label", "Menu");
        burger.addEventListener("click", function (e) {
            setMenu(root.dataset.menu !== "open", true);
        });
        if (menu) {
            menu.addEventListener("focusout", function (e) {
                if (root.dataset.menu !== "open") return;
                var to = e.relatedTarget;
                if (to && (menu.contains(to) || to === burger)) return;
                setMenu(false);
            });
        }
        // Close on link tap or Escape
        document.querySelectorAll("#nav-links a").forEach(function (a) {
            a.addEventListener("click", function () { setMenu(false); });
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && root.dataset.menu === "open") {
                setMenu(false);
                burger.focus();
            }
        });
        // Close on any tap outside the panel (the dim scrim is a header
        // pseudo-element, so scrim taps land here too).
        document.addEventListener("click", function (e) {
            if (root.dataset.menu !== "open") return;
            if (e.target.closest("#nav-links") || e.target.closest("#nav-burger")) return;
            setMenu(false);
        });
        // Auto-close when the viewport grows past the drawer breakpoint.
        var wide = matchMedia("(min-width: 721px)");
        var onWide = function () { if (wide.matches) setMenu(false); };
        if (wide.addEventListener) wide.addEventListener("change", onWide);
        else if (wide.addListener) wide.addListener(onWide);
    }

    /* --- Resume menu --- */
    /* The markup is a <details>, so opening, closing, the keyboard and the
       no-script case are already handled. This adds only what a menu is
       expected to do beyond a disclosure: Escape, a click outside, focus
       leaving, and closing with the drawer that contains it. */
    var resumeMenu = document.querySelector(".nav-menu > details");
    if (resumeMenu) {
        var closeResume = function (refocus) {
            if (!resumeMenu.open) return;
            resumeMenu.open = false;
            if (refocus) {
                var s = resumeMenu.querySelector("summary");
                if (s) s.focus();
            }
        };
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") closeResume(true);
        });
        document.addEventListener("click", function (e) {
            if (!resumeMenu.contains(e.target)) closeResume(false);
        });
        resumeMenu.addEventListener("focusout", function (e) {
            if (!resumeMenu.contains(e.relatedTarget)) closeResume(false);
        });
        if (burger) burger.addEventListener("click", function () { closeResume(false); });
    }
})();
