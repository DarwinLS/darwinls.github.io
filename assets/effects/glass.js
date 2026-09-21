/* ============================================================
   Glass runtime (progressive; the CSS glass is complete without it).

   Refraction, Chromium only (backdrop-filter accepts an SVG filter
   reference there). The glass never follows the pointer: it answers
   only to what is behind it, so the bend changes as scenery scrolls
   underneath. Each clear-glass element gets a displacement map built
   from its own size and corner radius: zero across the face, rising
   through a bevel band at the edge, pointing inward, so the scenery
   bends at the rim the way it does through a thick slab and text over
   the middle stays sharp. Maps are cached per size bucket and rebuilt
   on resize. Other browsers, coarse pointers, software GPU, reduced
   transparency and calm-capped devices keep the non-refracting glass.
   ============================================================ */
(function () {
    "use strict";
    var root = document.documentElement;
    var fine = matchMedia("(hover: hover) and (pointer: fine)");
    var reduceTransparency = matchMedia("(prefers-reduced-transparency: reduce)");

    /* ---------- Refraction ---------- */
    var REFRACT = ".glass:not(.no-refract)";
    var SVGNS = "http://www.w3.org/2000/svg";
    var defs = null, filters = {}, observed = new Map(), ro = null, count = 0;

    function chromium() {
        var ua = navigator.userAgentData;
        return !!(ua && ua.brands && ua.brands.some(function (b) { return /Chromium/.test(b.brand); }));
    }
    function allowed() {
        return chromium() && fine.matches && !reduceTransparency.matches &&
            root.dataset.gpu !== "soft" && root.dataset.intensity !== undefined &&
            !(root.dataset.intensity === "calm" && root.dataset.pref !== "calm");
    }

    function ensureDefs() {
        if (defs) return defs;
        var svg = document.createElementNS(SVGNS, "svg");
        svg.setAttribute("aria-hidden", "true");
        svg.setAttribute("width", "0");
        svg.setAttribute("height", "0");
        svg.style.cssText = "position:absolute;width:0;height:0;overflow:hidden;pointer-events:none";
        defs = document.createElementNS(SVGNS, "defs");
        svg.appendChild(defs);
        document.body.appendChild(svg);
        return defs;
    }

    /* Signed distance to a rounded rectangle centred at the origin */
    function sdf(px, py, hw, hh, r) {
        var qx = Math.abs(px) - (hw - r), qy = Math.abs(py) - (hh - r);
        var ox = Math.max(qx, 0), oy = Math.max(qy, 0);
        return Math.hypot(ox, oy) + Math.min(Math.max(qx, qy), 0) - r;
    }

    function buildMap(w, h, radius, bevel) {
        var S = 0.5;                                    // map resolution (bilinear upscale)
        var cw = Math.max(2, Math.round(w * S)), ch = Math.max(2, Math.round(h * S));
        var cv = document.createElement("canvas");
        cv.width = cw; cv.height = ch;
        var ctx = cv.getContext("2d");
        var img = ctx.createImageData(cw, ch), d = img.data;
        var hw = w / 2, hh = h / 2, r = Math.min(radius, hw, hh);
        var e = 0.75;
        for (var j = 0; j < ch; j++) {
            for (var i = 0; i < cw; i++) {
                var px = (i + 0.5) / S - hw, py = (j + 0.5) / S - hh;
                var dist = -sdf(px, py, hw, hh, r);            // positive inside
                var o = (j * cw + i) * 4;
                var rx = 0.5, gy = 0.5;
                if (dist < bevel) {
                    var t = 1 - Math.max(dist, 0) / bevel;
                    var mag = t * t * (3 - 2 * t);             // smooth ramp toward the rim
                    // outward normal from the SDF gradient
                    var nx = sdf(px + e, py, hw, hh, r) - sdf(px - e, py, hw, hh, r);
                    var ny = sdf(px, py + e, hw, hh, r) - sdf(px, py - e, hw, hh, r);
                    var nl = Math.hypot(nx, ny) || 1;
                    nx /= nl; ny /= nl;
                    // sample inward: the rim shows scenery pulled from inside the pane
                    rx = 0.5 - nx * mag * 0.5;
                    gy = 0.5 - ny * mag * 0.5;
                }
                d[o] = Math.round(rx * 255);
                d[o + 1] = Math.round(gy * 255);
                d[o + 2] = Math.round((dist < bevel ? edgeMask(dist, bevel) : 0) * 255);
                d[o + 3] = 255;
            }
        }
        ctx.putImageData(img, 0, 0);
        return cv.toDataURL("image/png");
    }

    /* How much of the sharp, bent rim shows over the frost: full at the
       lip, fading out by the inner edge of the bevel band */
    function edgeMask(dist, bevel) {
        var t = 1 - Math.max(dist, 0) / bevel;
        return Math.min(1, t * 1.6);
    }

    function node(tag, attrs) {
        var n = document.createElementNS(SVGNS, tag);
        for (var k in attrs) n.setAttribute(k, String(attrs[k]));
        return n;
    }

    /* The filter replaces the CSS blur in this tier:
         frost  = the backdrop, blurred (the pane's face)
         bent   = the backdrop, barely softened, displaced by the map
         rim    = bent, kept only inside the bevel band (map blue channel)
         result = rim over frost
       so the lip shows crisp scenery bending around the edge while the
       face stays frosted behind text. */
    function filterFor(w, h, radius, blur, k) {
        var bw = Math.round(w / 4) * 4, bh = Math.round(h / 4) * 4, br = Math.round(radius);
        var key = bw + "x" + bh + "r" + br + "b" + blur + "k" + k;
        if (filters[key]) return filters[key];
        var small = Math.min(bw, bh);
        var bevel = Math.max(6, Math.min(34, small * 0.3));
        var scale = bevel * 1.25 * k;          // k=1 stays under the fold limit (1.33x): text passing under the lip bends but never mirrors
        var id = "glass-refract-" + (++count);
        var f = node("filter", {
            id: id, x: 0, y: 0, width: bw, height: bh,
            filterUnits: "userSpaceOnUse", primitiveUnits: "userSpaceOnUse",
            "color-interpolation-filters": "sRGB"
        });
        f.appendChild(node("feImage", {
            href: buildMap(bw, bh, br, bevel), x: 0, y: 0, width: bw, height: bh,
            preserveAspectRatio: "none", result: "map"
        }));
        f.appendChild(node("feGaussianBlur", { "in": "SourceGraphic", stdDeviation: blur, edgeMode: "duplicate", result: "frost" }));
        f.appendChild(node("feGaussianBlur", { "in": "SourceGraphic", stdDeviation: 0.6, edgeMode: "duplicate", result: "soft" }));
        f.appendChild(node("feDisplacementMap", {
            "in": "soft", in2: "map", scale: scale,
            xChannelSelector: "R", yChannelSelector: "G", result: "bent"
        }));
        f.appendChild(node("feColorMatrix", {
            "in": "map", type: "matrix",
            values: "0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 1 0 0", result: "mask"
        }));
        f.appendChild(node("feComposite", { "in": "bent", in2: "mask", operator: "in", result: "rim" }));
        f.appendChild(node("feComposite", { "in": "rim", in2: "frost", operator: "over" }));
        ensureDefs().appendChild(f);
        filters[key] = "url(#" + id + ")";
        return filters[key];
    }

    /* Large panes: displacement only, applied AFTER the compositor's own
       blur. The full rim filter runs its blurs in SVG, which measured at
       ~2x the frame cost on page-sized panes; this keeps a softer bend
       at the edge for a fraction of the cost. */
    function bendFor(w, h, radius, k) {
        var bw = Math.round(w / 8) * 8, bh = Math.round(h / 8) * 8, br = Math.round(radius);
        var key = "bend" + bw + "x" + bh + "r" + br + "k" + k;
        if (filters[key]) return filters[key];
        var bevel = Math.max(10, Math.min(40, Math.min(bw, bh) * 0.2));
        var id = "glass-bend-" + (++count);
        var f = node("filter", {
            id: id, x: 0, y: 0, width: bw, height: bh,
            filterUnits: "userSpaceOnUse", primitiveUnits: "userSpaceOnUse",
            "color-interpolation-filters": "sRGB"
        });
        f.appendChild(node("feImage", {
            href: buildMap(bw, bh, br, bevel), x: 0, y: 0, width: bw, height: bh,
            preserveAspectRatio: "none", result: "map"
        }));
        f.appendChild(node("feDisplacementMap", {
            "in": "SourceGraphic", in2: "map", scale: bevel * 1.25 * k,
            xChannelSelector: "R", yChannelSelector: "G"
        }));
        ensureDefs().appendChild(f);
        filters[key] = "url(#" + id + ")";
        return filters[key];
    }

    var FULL_AREA = 140000;   // px²: header bar, buttons, small cards get the crisp rim

    function apply(el) {
        var r = el.getBoundingClientRect();
        if (r.width < 8 || r.height < 8) return;
        var cs = getComputedStyle(el);
        var rad = parseFloat(cs.borderTopLeftRadius) || 0;
        /* --refract-strength: 0 off, 1 default; above ~1.1 the lip starts
           to fold scenery into a mirrored band */
        var k = parseFloat(cs.getPropertyValue("--refract-strength"));
        if (isNaN(k)) k = 1;
        if (k <= 0) {
            el.style.removeProperty("--refract");
            el.style.removeProperty("--refract-post");
            return;
        }
        if (r.width * r.height <= FULL_AREA) {
            var blur = parseFloat(cs.getPropertyValue("--glass-blur")) || 16;
            el.style.removeProperty("--refract-post");
            el.style.setProperty("--refract", filterFor(r.width, r.height, rad, blur, k));
        } else {
            el.style.removeProperty("--refract");
            el.style.setProperty("--refract-post", bendFor(r.width, r.height, rad, k));
        }
    }

    function enableRefraction() {
        if (ro) return;
        root.dataset.glass = "refract";
        ro = new ResizeObserver(function (entries) {
            entries.forEach(function (en) { apply(en.target); });
        });
        document.querySelectorAll(REFRACT).forEach(function (el) {
            observed.set(el, true);
            ro.observe(el);
        });
    }
    function disableRefraction() {
        if (!ro) return;
        ro.disconnect();
        ro = null;
        observed.forEach(function (_, el) { el.style.removeProperty("--refract"); el.style.removeProperty("--refract-post"); });
        observed.clear();
        delete root.dataset.glass;
    }
    function syncRefraction() {
        if (allowed()) enableRefraction(); else disableRefraction();
    }

    function boot() {
        syncRefraction();
        [fine, reduceTransparency].forEach(function (m) {
            var on = syncRefraction;
            if (m.addEventListener) m.addEventListener("change", on);
        });
        new MutationObserver(syncRefraction).observe(root, {
            attributes: true, attributeFilter: ["data-gpu", "data-intensity"]
        });
    }
    if (document.prerendering) {
        document.addEventListener("prerenderingchange", boot, { once: true });
    } else if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot, { once: true });
    } else {
        boot();
    }
})();
