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
