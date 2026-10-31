"""
Premium generators for WallBloom.

These complement the flat vector generators in pattern_engine/scene_engine with
soft gradients, atmospheric depth, blur and film grain. Every generator is
deterministic for a given (width, height, colors, seed) and returns a PIL image.

Heavy, low-frequency work (blurred blobs, colour fields) is computed on a
downscaled canvas and upscaled, which keeps 4K renders well under a second.
"""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# ----------------------------------------------------------------------------
# Colour helpers
# ----------------------------------------------------------------------------

def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _luma(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _sorted_by_luma(colors):
    """Palette colours ordered dark -> light."""
    return sorted((_rgb(c) for c in colors), key=_luma)


def _mix(a, b, t):
    return a * (1 - t) + b * t


def _tuple(c):
    return tuple(int(max(0, min(255, round(v)))) for v in c)


def _ramp(stops, t):
    """Sample a multi-stop colour ramp. t is an ndarray in [0, 1]."""
    stops = np.asarray(stops, dtype=np.float64)
    n = len(stops) - 1
    t = np.clip(t, 0, 1) * n
    i = np.clip(np.floor(t).astype(int), 0, n - 1)
    f = (t - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f


def _np_rng(rng):
    return np.random.default_rng(rng.randint(0, 2 ** 31 - 1))


def _vertical_gradient(width, height, stops, curve=1.0):
    t = np.linspace(0, 1, height) ** curve
    col = _ramp(stops, t)
    return np.repeat(col[:, None, :], width, axis=1)


def _to_image(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def _grain(img, rng, amount=6.0):
    """Subtle monochrome film grain; avoids banding on large gradients."""
    arr = np.asarray(img, dtype=np.float32)
    noise = _np_rng(rng).normal(0, amount, size=arr.shape[:2]).astype(np.float32)
    return _to_image(arr + noise[..., None])


def _blur(img, radius):
    return img.filter(ImageFilter.GaussianBlur(radius)) if radius > 0 else img


def _soft_layer(width, height, scale, draw_fn, blur_px):
    """Draw RGBA shapes on a downscaled canvas, blur, and upscale smoothly."""
    sw, sh = max(8, int(width * scale)), max(8, int(height * scale))
    layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), sw, sh)
    layer = _blur(layer, blur_px * scale)
    return layer.resize((width, height), Image.BICUBIC)


def _ridge(width, rng, base, amp, octaves=5, roughness=0.5, smooth=False):
    """1-D fractal ridgeline as a sum of seeded sines; returns y per x."""
    x = np.arange(width, dtype=np.float64) / width
    y = np.full(width, float(base))
    a, f = amp, rng.uniform(0.8, 1.6)
    for k in range(octaves):
        phase = rng.uniform(0, 2 * math.pi)
        wave = np.sin(x * f * 2 * math.pi + phase)
        if not smooth and k < 2:
            wave = 1 - np.abs(wave) * 2  # sharper, mountain-like crests
        y += a * wave
        a *= roughness
        f *= rng.uniform(1.8, 2.3)
    return y


def _fill_below(arr, ys, color, alpha=1.0):
    """Fill everything below a ridgeline (in-place on a float RGB array)."""
    h = arr.shape[0]
    rows = np.arange(h)[:, None]
    mask = rows >= ys[None, :]
    if alpha >= 1.0:
        arr[mask] = color
    else:
        arr[mask] = arr[mask] * (1 - alpha) + np.asarray(color) * alpha


def _stars(draw, width, height, rng, count, max_y, color=(255, 255, 255), size=1.0):
    unit = max(1, int(min(width, height) / 900 * size))
    for _ in range(count):
        x, y = rng.randint(0, width), rng.randint(0, int(max_y))
        r = unit * rng.choice([1, 1, 1, 2])
        b = rng.uniform(0.35, 1.0)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=_tuple(np.asarray(color) * b))


def _glow(width, height, cx, cy, radius, color, strength=1.0):
    """Additive radial glow as a float array."""
    yy, xx = np.ogrid[:height, :width]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(radius, 1)
    g = np.exp(-d ** 2 * 2.2) * strength
    return g[..., None] * np.asarray(color, dtype=np.float64)


def _small_glow(width, height, cx, cy, radius, color, strength=1.0, scale=0.25):
    """Glow computed at reduced resolution (it is smooth) then upscaled."""
    sw, sh = max(8, int(width * scale)), max(8, int(height * scale))
    g = _glow(sw, sh, cx * scale, cy * scale, radius * scale, color, strength)
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), mode="RGB")
    return np.asarray(img.resize((width, height), Image.BICUBIC), dtype=np.float64)


# ----------------------------------------------------------------------------
# Patterns
# ----------------------------------------------------------------------------

def mesh_gradient(width, height, colors, rng):
    """Soft, blurred colour blobs - the modern 'mesh gradient' look."""
    cols = [_rgb(c) for c in colors]
    base = _tuple(_mix(_sorted_by_luma(colors)[0], _sorted_by_luma(colors)[1], 0.5))

    def draw(d, w, h):
        d.rectangle([0, 0, w, h], fill=base + (255,))
        for i in range(rng.randint(5, 8)):
            c = _tuple(cols[(i + 1) % len(cols)])
            r = rng.uniform(0.25, 0.55) * max(w, h)
            x, y = rng.uniform(-0.1, 1.1) * w, rng.uniform(-0.1, 1.1) * h
            d.ellipse([x - r, y - r * rng.uniform(0.6, 1.2), x + r, y + r], fill=c + (rng.randint(200, 255),))

    img = _soft_layer(width, height, 0.12, draw, max(width, height) * 0.07).convert("RGB")
    return _grain(img, rng, 5)


def grain_gradient(width, height, colors, rng):
    """Smooth multi-stop diagonal gradient with film grain."""
    cols = [_rgb(c) for c in colors]
    s = _sorted_by_luma(colors)
    stops = [s[0], cols[rng.randint(1, len(cols) - 1)], s[-1]]
    if rng.random() < 0.5:
        stops.reverse()
    angle = rng.uniform(0, math.pi)
    sw, sh = max(8, width // 8), max(8, height // 8)
    yy, xx = np.mgrid[0:sh, 0:sw]
    t = (xx / sw * math.cos(angle) + yy / sh * math.sin(angle))
    t = (t - t.min()) / max(t.max() - t.min(), 1e-6)
    t = t + 0.08 * np.sin(xx / sw * rng.uniform(2, 5) + rng.uniform(0, 6)) * np.cos(yy / sh * rng.uniform(2, 5))
    small = _to_image(_ramp(stops, t))
    return _grain(small.resize((width, height), Image.BICUBIC), rng, 7)


def layered_peaks(width, height, colors, rng):
    """Atmospheric mountain layers fading into a hazy sky."""
    dark, *_, light = _sorted_by_luma(colors)
    accent = _rgb(colors[rng.randint(1, len(colors) - 1)])
    sky = _vertical_gradient(width, height, [_mix(light, accent, 0.35), light, _mix(light, accent, 0.2)], 1.2)
    sun_x, sun_y = rng.uniform(0.25, 0.75) * width, rng.uniform(0.2, 0.42) * height
    sky += _small_glow(width, height, sun_x, sun_y, min(width, height) * 0.45, _mix(accent, np.array([255, 255, 255.0]), 0.6) * 0.35)
    img = _to_image(sky)
    d = ImageDraw.Draw(img)
    r = min(width, height) * rng.uniform(0.06, 0.1)
    d.ellipse([sun_x - r, sun_y - r, sun_x + r, sun_y + r], fill=_tuple(_mix(light, np.array([255, 250, 240.0]), 0.75)))
    arr = np.asarray(img, dtype=np.float64).copy()
    layers = rng.randint(5, 7)
    for i in range(layers):
        t = (i + 1) / layers
        base = height * (0.42 + 0.5 * t ** 1.1)
        ys = _ridge(width, rng, base, height * 0.07 * (1.2 - t * 0.5), octaves=5, roughness=0.38)
        color = _mix(_mix(light, accent, 0.45), dark, t ** 0.9)
        _fill_below(arr, ys, color)
    return _grain(_to_image(arr), rng, 4)


def silk_waves(width, height, colors, rng):
    """Flowing stacked ribbons with soft shading."""
    cols = _sorted_by_luma(colors)
    arr = _vertical_gradient(width, height, [cols[0], _mix(cols[0], cols[-1], 0.15)])
    n = rng.randint(6, 9)
    x = np.arange(width) / width
    for i in range(n):
        t = i / (n - 1)
        base = height * (0.25 + 0.7 * t)
        amp = height * rng.uniform(0.04, 0.09)
        f1, f2 = rng.uniform(0.6, 1.4), rng.uniform(1.5, 3.0)
        p1, p2 = rng.uniform(0, 6.3), rng.uniform(0, 6.3)
        ys = base + amp * np.sin(x * f1 * 2 * math.pi + p1) + amp * 0.35 * np.sin(x * f2 * 2 * math.pi + p2)
        c = _ramp(cols, np.array([0.25 + 0.75 * ((i * 0.37) % 1.0)]))[0]
        rows = np.arange(height)[:, None]
        depth = np.clip((rows - ys[None, :]) / (height * 0.12), 0, 1)
        shade = (1 - 0.35 * depth)[..., None]
        mask = (rows >= ys[None, :])[..., None]
        arr = np.where(mask, c * shade, arr)
        # Thin highlight along each ribbon crest
        hl = np.exp(-((rows - ys[None, :]) / (height * 0.004)) ** 2)[..., None]
        arr = arr + hl * 40
    return _grain(_to_image(arr), rng, 4)


def bokeh(width, height, colors, rng):
    """Out-of-focus light orbs over a dark gradient."""
    cols = _sorted_by_luma(colors)
    dark = _mix(cols[0], np.zeros(3), 0.55)
    bg = _to_image(_vertical_gradient(width, height, [dark, _mix(dark, cols[1], 0.35), dark]))
    unit = max(width, height)
    for blur_r, count, size in ((0.02, 14, (0.05, 0.12)), (0.008, 26, (0.02, 0.06)), (0.002, 40, (0.006, 0.018))):
        def draw(d, w, h, count=count, size=size):
            for _ in range(count):
                c = _tuple(cols[rng.randint(1, len(cols) - 1)])
                r = rng.uniform(*size) * max(w, h)
                x, y = rng.uniform(0, w), rng.uniform(0, h)
                d.ellipse([x - r, y - r, x + r, y + r], fill=c + (rng.randint(60, 150),))
        layer = _soft_layer(width, height, 0.25, draw, unit * blur_r)
        bg = Image.alpha_composite(bg.convert("RGBA"), layer)
    return _grain(bg.convert("RGB"), rng, 4)


def liquid(width, height, colors, rng):
    """Domain-warped colour field - marbled liquid paint."""
    cols = [_rgb(c) for c in colors]
    sw, sh = max(8, width // 4), max(8, height // 4)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float64)
    u, v = xx / max(sw, sh), yy / max(sw, sh)
    f = rng.uniform(2.0, 3.5)
    for _ in range(3):
        a, b = rng.uniform(0, 6.3), rng.uniform(0, 6.3)
        u, v = u + 0.35 * np.sin(v * f * 2 + a), v + 0.35 * np.cos(u * f * 2 + b)
    t = 0.5 + 0.5 * np.sin((u + v) * f * 1.7 + rng.uniform(0, 6.3))
    stops = cols + [cols[0]]
    small = _to_image(_ramp(stops, t))
    return _grain(small.resize((width, height), Image.BICUBIC), rng, 4)


def flow_lines(width, height, colors, rng):
    """Hundreds of fine strokes tracing a smooth flow field."""
    cols = _sorted_by_luma(colors)
    bg = _mix(cols[0], np.zeros(3), 0.3)
    ss = 2  # supersample for anti-aliased strokes
    W, H = width * ss, height * ss
    img = Image.new("RGB", (W, H), _tuple(bg))
    d = ImageDraw.Draw(img)
    fx, fy, p = rng.uniform(1.5, 3.0), rng.uniform(1.5, 3.0), rng.uniform(0, 6.3)
    unit = max(W, H)
    step = unit * 0.004
    lw = max(1, int(unit / 1400))
    for i in range(rng.randint(420, 620)):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        c = _tuple(cols[1 + (i % (len(cols) - 1))] * rng.uniform(0.55, 1.0))
        pts = [(x, y)]
        for _ in range(rng.randint(40, 110)):
            ang = math.sin(x / unit * fx * 2 * math.pi + p) * 2.2 + math.cos(y / unit * fy * 2 * math.pi) * 2.2
            x += math.cos(ang) * step
            y += math.sin(ang) * step
            pts.append((x, y))
        d.line(pts, fill=c, width=lw)
    return img.resize((width, height), Image.LANCZOS)


def glass_orbs(width, height, colors, rng):
    """Glossy shaded spheres floating on a soft gradient."""
    cols = _sorted_by_luma(colors)
    arr = _vertical_gradient(width, height, [cols[0], _mix(cols[0], cols[1], 0.6)], 0.9)
    unit = min(width, height)
    for _ in range(rng.randint(3, 6)):
        r = unit * rng.uniform(0.12, 0.38)
        cx, cy = rng.uniform(0.1, 0.9) * width, rng.uniform(0.1, 0.9) * height
        base = cols[rng.randint(1, max(1, len(cols) - 2))]
        x0, x1 = int(max(0, cx - r)), int(min(width, cx + r + 1))
        y0, y1 = int(max(0, cy - r)), int(min(height, cy + r + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
        dx, dy = (xx - cx) / r, (yy - cy) / r
        dist = np.sqrt(dx ** 2 + dy ** 2)
        inside = dist <= 1
        nz = np.sqrt(np.clip(1 - dist ** 2, 0, 1))
        light = np.clip(-0.45 * dx - 0.55 * dy + 0.7 * nz, 0, 1)
        spec = np.clip(light, 0, 1) ** 24
        color = base[None, None, :] * (0.3 + 0.6 * light[..., None]) + 255 * spec[..., None] * 0.55
        edge = np.clip((1 - dist) * r / 1.5, 0, 1)[..., None]
        region = arr[y0:y1, x0:x1]
        arr[y0:y1, x0:x1] = np.where(inside[..., None], region * (1 - edge) + color * edge, region)
    return _grain(_to_image(arr), rng, 4)


def halftone(width, height, colors, rng):
    """Graphic halftone dots modulated by a sweeping gradient."""
    cols = _sorted_by_luma(colors)
    img = Image.new("RGB", (width, height), _tuple(cols[0]))
    d = ImageDraw.Draw(img)
    cell = max(6, int(min(width, height) / rng.randint(34, 52)))
    fx, fy, ph = rng.uniform(0.5, 1.5), rng.uniform(0.5, 1.5), rng.uniform(0, 6.3)
    ca, cb = cols[1], cols[-1]
    for gy in range(0, height + cell, cell):
        for gx in range(0, width + cell, cell):
            ox = cell / 2 if (gy // cell) % 2 else 0
            u, v = (gx + ox) / width, gy / height
            t = 0.5 + 0.5 * math.sin(u * fx * 2 * math.pi + v * fy * 2 * math.pi + ph)
            r = cell * 0.48 * t
            if r < 0.6:
                continue
            c = _tuple(_mix(ca, cb, t))
            d.ellipse([gx + ox - r, gy - r, gx + ox + r, gy + r], fill=c)
    return img


PREMIUM_PATTERNS = {
    "mesh_gradient": mesh_gradient,
    "grain_gradient": grain_gradient,
    "layered_peaks": layered_peaks,
    "silk_waves": silk_waves,
    "bokeh": bokeh,
    "liquid": liquid,
    "flow_lines": flow_lines,
    "glass_orbs": glass_orbs,
    "halftone": halftone,
}


# ----------------------------------------------------------------------------
# Minimal scenes
# ----------------------------------------------------------------------------

def _scene_palette(colors):
    """Normalise any palette (4 or 6 colours) to named roles."""
    s = _sorted_by_luma(colors)
    return {"night": s[0], "deep": s[1], "mid": s[len(s) // 2], "soft": s[-2], "light": s[-1]}


def minimal_mountains(width, height, colors, rng):
    return layered_peaks(width, height, colors, rng)


def misty_forest(width, height, colors, rng):
    p = _scene_palette(colors)
    fog = _mix(p["light"], p["soft"], 0.4)
    arr = _vertical_gradient(width, height, [p["light"], fog, _mix(fog, p["mid"], 0.4)], 1.1)
    img = _to_image(arr)
    layers = 5
    for i in range(layers):
        t = (i + 1) / layers
        color = _tuple(_mix(fog, p["night"], t ** 1.2))
        d = ImageDraw.Draw(img)
        ground = height * (0.55 + 0.4 * t)
        d.rectangle([0, ground, width, height], fill=color)
        tree_w = width * (0.035 + 0.05 * t)
        x = -tree_w
        while x < width + tree_w:
            h = height * rng.uniform(0.12, 0.26) * (0.6 + t)
            top = ground - h
            tiers = 6
            for k in range(tiers):
                ty = top + h * k / tiers
                half = tree_w * (0.25 + 0.75 * (k + 1) / tiers)
                d.polygon([(x, ty), (x - half, ty + h / tiers * 1.8), (x + half, ty + h / tiers * 1.8)], fill=color)
            d.rectangle([x - tree_w * 0.06, ground - h * 0.1, x + tree_w * 0.06, ground], fill=color)
            x += tree_w * rng.uniform(0.7, 1.4)
        # Mist band between layers
        mist = _soft_layer(width, height, 0.15, lambda dd, w, h2, g=ground: dd.rectangle(
            [0, g / height * h2 - h2 * 0.05, w, g / height * h2 + h2 * 0.03], fill=_tuple(fog) + (120,)), height * 0.05)
        img = Image.alpha_composite(img.convert("RGBA"), mist).convert("RGB")
    return _grain(img, rng, 4)


def ocean_sunset(width, height, colors, rng):
    p = _scene_palette(colors)
    horizon = height * rng.uniform(0.55, 0.65)
    sky = _vertical_gradient(width, int(horizon), [p["deep"], p["mid"], p["soft"], p["light"]], 1.0)
    sea = _vertical_gradient(width, height - int(horizon), [_mix(p["mid"], p["deep"], 0.5), p["night"]], 0.8)
    arr = np.concatenate([sky, sea], axis=0)
    sun_x = width * rng.uniform(0.35, 0.65)
    sun_r = min(width, height) * rng.uniform(0.12, 0.18)
    arr += _small_glow(width, height, sun_x, horizon - sun_r * 0.3, sun_r * 3, p["light"] * 0.45)
    img = _to_image(arr)
    d = ImageDraw.Draw(img)
    sun_c = _tuple(_mix(p["light"], np.array([255, 245, 225.0]), 0.6))
    d.pieslice([sun_x - sun_r, horizon - sun_r * 1.3, sun_x + sun_r, horizon + sun_r * 0.7], 180, 360, fill=sun_c)
    # Shimmering reflection: stacked thin strokes narrowing toward the viewer
    rows = int((height - horizon) / max(3, height / 260))
    for k in range(rows):
        y = horizon + (k + 1) * (height - horizon) / (rows + 1)
        t = k / max(rows - 1, 1)
        half = sun_r * (0.9 - 0.5 * t) * rng.uniform(0.5, 1.2)
        th = max(1, int(height / 900 * (1 + 2 * t)))
        a = 1 - t * 0.85
        c = _tuple(_mix(np.asarray(img.getpixel((int(sun_x), int(y)))), np.asarray(sun_c, dtype=float), a * 0.8))
        off = rng.uniform(-0.2, 0.2) * sun_r
        d.rectangle([sun_x - half + off, y, sun_x + half + off, y + th], fill=c)
    return _grain(img, rng, 4)


def moonlit_dunes(width, height, colors, rng):
    p = _scene_palette(colors)
    arr = _vertical_gradient(width, height, [p["night"], p["deep"], _mix(p["deep"], p["mid"], 0.5)], 1.3)
    mx, my = width * rng.uniform(0.25, 0.75), height * rng.uniform(0.15, 0.3)
    mr = min(width, height) * 0.08
    arr += _small_glow(width, height, mx, my, mr * 5, p["soft"] * 0.35)
    img = _to_image(arr)
    d = ImageDraw.Draw(img)
    _stars(d, width, height, rng, int(width * height / 9000), height * 0.6, _mix(p["light"], np.array([255, 255, 255.0]), 0.6))
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=_tuple(_mix(p["light"], np.array([255, 255, 250.0]), 0.7)))
    arr = np.asarray(img, dtype=np.float64).copy()
    for i in range(5):
        t = (i + 1) / 5
        ys = _ridge(width, rng, height * (0.58 + 0.36 * t), height * 0.035, octaves=2, roughness=0.35, smooth=True)
        lit = _mix(p["mid"], p["soft"], 0.5 * (1 - t))
        shadow = _mix(p["deep"], p["night"], 0.3 + 0.7 * t)
        rows = np.arange(height)[:, None]
        depth = np.clip((rows - ys[None, :]) / (height * 0.09), 0, 1)[..., None]
        body = lit * (1 - depth) + shadow * depth
        mask = (rows >= ys[None, :])[..., None]
        arr = np.where(mask, body, arr)
    return _grain(_to_image(arr), rng, 5)


def ringed_planet(width, height, colors, rng):
    p = _scene_palette(colors)
    arr = _vertical_gradient(width, height, [p["night"], _mix(p["night"], p["deep"], 0.6), p["night"]])
    arr += _small_glow(width, height, width * rng.uniform(0.2, 0.8), height * rng.uniform(0.2, 0.8),
                       max(width, height) * 0.5, p["mid"] * 0.25)
    img = _to_image(arr)
    d = ImageDraw.Draw(img)
    _stars(d, width, height, rng, int(width * height / 6000), height)
    unit = min(width, height)
    cx, cy, r = width * rng.uniform(0.35, 0.65), height * rng.uniform(0.38, 0.58), unit * rng.uniform(0.22, 0.3)
    tilt = rng.uniform(-0.35, 0.35)
    ring_c = _mix(p["soft"], p["light"], 0.5)

    def ring(back):
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for k in range(14):
            rr = r * (1.35 + k * 0.06)
            c = _tuple(ring_c * (0.55 + 0.45 * ((k * 7) % 5) / 4)) + (200 - k * 6,)
            ld.ellipse([cx - rr, cy - rr * 0.22, cx + rr, cy + rr * 0.22], outline=c, width=max(1, int(unit / 260)))
        if back:
            ld.rectangle([0, cy, width, height], fill=(0, 0, 0, 0))
        else:
            ld.rectangle([0, 0, width, cy], fill=(0, 0, 0, 0))
        return layer.rotate(math.degrees(tilt), center=(cx, cy), resample=Image.BICUBIC)

    img = Image.alpha_composite(img.convert("RGBA"), ring(True))
    arr = np.asarray(img.convert("RGB"), dtype=np.float64).copy()
    yy, xx = np.ogrid[:height, :width]
    dx, dy = (xx - cx) / r, (yy - cy) / r
    dist = np.sqrt(dx ** 2 + dy ** 2)
    inside = dist <= 1
    nz = np.sqrt(np.clip(1 - dist ** 2, 0, 1))
    light = np.clip(-0.6 * dx - 0.4 * dy + 0.5 * nz, 0, 1)
    bands = 0.5 + 0.5 * np.sin((dy * math.cos(tilt) - dx * math.sin(tilt)) * 14 + rng.uniform(0, 6))
    surf = _ramp([p["deep"], p["mid"], p["soft"]], bands * 0.7 + 0.15)
    shaded = surf * (0.15 + 0.95 * light[..., None])
    edge = np.clip((1 - dist) * r / 2, 0, 1)[..., None]
    arr = np.where(inside[..., None], arr * (1 - edge) + shaded * edge, arr)
    img = Image.alpha_composite(_to_image(arr).convert("RGBA"), ring(False))
    return _grain(img.convert("RGB"), rng, 4)


def aurora_lake(width, height, colors, rng):
    p = _scene_palette(colors)
    horizon = int(height * rng.uniform(0.6, 0.68))
    sky = _vertical_gradient(width, horizon, [p["night"], _mix(p["night"], p["deep"], 0.7)])
    img = _to_image(sky)
    d = ImageDraw.Draw(img)
    _stars(d, width, horizon, rng, int(width * horizon / 7000), horizon)

    def curtains(dd, w, h):
        for k in range(rng.randint(3, 5)):
            c = _tuple(_mix(p["soft"], p["light"], rng.uniform(0, 1)))
            base = h * rng.uniform(0.25, 0.5)
            amp, f, ph = h * 0.06, rng.uniform(1, 2.5), rng.uniform(0, 6.3)
            f2, ph2 = rng.uniform(4, 9), rng.uniform(0, 6.3)
            for x in range(0, w, 2):
                y = base + amp * math.sin(x / w * f * 2 * math.pi + ph)
                length = h * (0.1 + 0.14 * (0.5 + 0.5 * math.sin(x / w * f2 * math.pi + ph2)))
                dd.line([(x, y - length), (x, y - length * 0.4)], fill=c + (60,), width=2)
                dd.line([(x, y - length * 0.4), (x, y)], fill=c + (170,), width=2)

    aur = _soft_layer(width, horizon, 0.25, curtains, height * 0.006)
    img = Image.alpha_composite(img.convert("RGBA"), aur).convert("RGB")
    arr = np.asarray(img, dtype=np.float64).copy()
    ys = _ridge(width, rng, horizon * 0.86, horizon * 0.08, octaves=5, roughness=0.5)
    _fill_below(arr, ys, p["night"] * 0.6)
    # Reflection: mirrored, darkened, slightly rippled
    src_rows = np.clip(horizon - 1 - np.arange(height - horizon), 0, horizon - 1)
    refl = arr[src_rows]
    ripple = (np.sin(np.arange(refl.shape[0]) * 0.9) * max(1, width / 500)).astype(int)
    refl = np.stack([np.roll(refl[i], ripple[i], axis=0) for i in range(refl.shape[0])])
    water = refl * 0.55 + _mix(p["night"], p["deep"], 0.3) * 0.25
    out = np.concatenate([arr[:horizon], water], axis=0)
    return _grain(_to_image(out), rng, 4)


def lone_tree(width, height, colors, rng):
    p = _scene_palette(colors)
    arr = _vertical_gradient(width, height, [p["mid"], p["soft"], p["light"]], 1.4)
    sun_x, sun_y = width * rng.uniform(0.3, 0.7), height * rng.uniform(0.45, 0.58)
    arr += _small_glow(width, height, sun_x, sun_y, min(width, height) * 0.6, p["light"] * 0.4)
    img = _to_image(arr)
    d = ImageDraw.Draw(img)
    sr = min(width, height) * 0.13
    d.ellipse([sun_x - sr, sun_y - sr, sun_x + sr, sun_y + sr], fill=_tuple(_mix(p["light"], np.array([255, 248, 235.0]), 0.6)))
    arr = np.asarray(img, dtype=np.float64).copy()
    hill_y = _ridge(width, rng, height * 0.72, height * 0.04, octaves=2, roughness=0.3, smooth=True)
    _fill_below(arr, hill_y + height * 0.06, _mix(p["deep"], p["mid"], 0.5))
    _fill_below(arr, hill_y, p["night"])
    img = _to_image(arr)
    d = ImageDraw.Draw(img)
    tx = int(width * rng.uniform(0.3, 0.7))
    base_y = hill_y[min(tx, width - 1)]
    unit = min(width, height)
    trunk_h = unit * 0.32
    color = _tuple(p["night"])

    def branch(x, y, ang, length, w, depth):
        if depth == 0 or length < unit * 0.01:
            d.ellipse([x - w * 4, y - w * 3, x + w * 4, y + w * 3], fill=color)
            return
        x2, y2 = x + math.cos(ang) * length, y - math.sin(ang) * length
        d.line([(x, y), (x2, y2)], fill=color, width=max(1, int(w)))
        for spread in (-1, 1):
            branch(x2, y2, ang + spread * rng.uniform(0.3, 0.6), length * rng.uniform(0.62, 0.78), w * 0.68, depth - 1)

    branch(tx, base_y, math.pi / 2, trunk_h, unit * 0.025, 8)
    return _grain(img, rng, 4)


def paper_hills(width, height, colors, rng):
    p = _scene_palette(colors)
    stops = [p["light"], p["soft"], p["mid"], p["deep"], p["night"]]
    img = _to_image(_vertical_gradient(width, height, [p["light"], _mix(p["light"], p["soft"], 0.5)]))
    layers = 6
    for i in range(layers):
        t = (i + 1) / layers
        ys = _ridge(width, rng, height * (0.3 + 0.62 * t), height * 0.06, octaves=2, roughness=0.35, smooth=True)
        color = _tuple(_ramp(stops, np.array([0.15 + 0.85 * t]))[0])
        poly = [(0, height)] + [(x, ys[x]) for x in range(0, width, max(1, width // 400))] + [(width, ys[-1]), (width, height)]
        # Paper-cut drop shadow
        shadow = _soft_layer(width, height, 0.25, lambda dd, w, h, pts=poly: dd.polygon(
            [(x * w / width, (y - height * 0.008) * h / height) for x, y in pts], fill=(0, 0, 0, 70)), height * 0.012)
        img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
        ImageDraw.Draw(img).polygon(poly, fill=color)
    return _grain(img, rng, 3)


def city_dusk(width, height, colors, rng):
    p = _scene_palette(colors)
    arr = _vertical_gradient(width, height, [p["deep"], p["mid"], p["soft"]], 0.9)
    arr += _small_glow(width, height, width * 0.5, height * 0.62, max(width, height) * 0.45, p["light"] * 0.3)
    img = _to_image(arr)
    d = ImageDraw.Draw(img)
    _stars(d, width, height, rng, int(width * height / 20000), height * 0.35)
    unit = min(width, height)
    win = _tuple(_mix(p["light"], np.array([255, 230, 170.0]), 0.5))
    for layer in range(3):
        t = (layer + 1) / 3
        color = _tuple(_mix(_mix(p["mid"], p["deep"], 0.5), p["night"], t))
        x = -unit * 0.05
        while x < width:
            bw = unit * rng.uniform(0.07, 0.16) * (0.7 + 0.5 * t)
            bh = height * rng.uniform(0.12, 0.42) * (1.1 - 0.35 * t)
            top = height * (0.78 + 0.08 * t) - bh
            d.rectangle([x, top, x + bw, height], fill=color)
            if layer == 2:
                cw = max(2, int(bw / 9))
                for wy in np.arange(top + cw * 2, height - cw, cw * 2.2):
                    for wx in np.arange(x + cw, x + bw - cw, cw * 2):
                        if rng.random() < 0.28:
                            d.rectangle([wx, wy, wx + cw * 0.9, wy + cw * 1.1], fill=win)
            x += bw + unit * rng.uniform(0.0, 0.02)
    return _grain(img, rng, 4)


PREMIUM_SCENES = {
    "minimal_mountains": minimal_mountains,
    "misty_forest": misty_forest,
    "ocean_sunset": ocean_sunset,
    "moonlit_dunes": moonlit_dunes,
    "ringed_planet": ringed_planet,
    "aurora_lake": aurora_lake,
    "lone_tree": lone_tree,
    "paper_hills": paper_hills,
    "city_dusk": city_dusk,
}

PREMIUM_SCENE_DEFINITIONS = {
    "minimal_mountains": {"name": "Alpine Haze", "emoji": "🏔️", "default_palette": ["#1d2b44", "#3c5a7a", "#7f9cb5", "#c9d6e2", "#f2c6a0", "#f7efe6"]},
    "misty_forest": {"name": "Misty Pines", "emoji": "🌲", "default_palette": ["#0f1f1c", "#1f3b34", "#4d6b61", "#93ada3", "#cfdcd5", "#eef3ef"]},
    "ocean_sunset": {"name": "Ocean Sunset", "emoji": "🌅", "default_palette": ["#120d26", "#3b1f4f", "#a4416b", "#f07f5a", "#f9c784", "#fff1d6"]},
    "moonlit_dunes": {"name": "Moonlit Dunes", "emoji": "🌙", "default_palette": ["#070b1d", "#16224a", "#3d4a85", "#8a8fc4", "#d8c9e8", "#f6f1ff"]},
    "ringed_planet": {"name": "Ringed Planet", "emoji": "🪐", "default_palette": ["#05060f", "#1b1640", "#5b3f8c", "#c47fb4", "#f2c7a5", "#fff4e8"]},
    "aurora_lake": {"name": "Aurora Lake", "emoji": "🌌", "default_palette": ["#030914", "#0b2238", "#0f5257", "#1fbf8f", "#9ff2c8", "#e6fff4"]},
    "lone_tree": {"name": "Lone Tree", "emoji": "🌳", "default_palette": ["#1a0f1e", "#43233b", "#a2465b", "#ec8a5e", "#f8c77a", "#fff0cf"]},
    "paper_hills": {"name": "Paper Hills", "emoji": "🏞️", "default_palette": ["#22313f", "#3e6372", "#6fa3a0", "#b9d8c2", "#f3e3c3", "#fff8ec"]},
    "city_dusk": {"name": "City at Dusk", "emoji": "🌆", "default_palette": ["#0b0b1e", "#262055", "#6a3f84", "#d0708f", "#f7b98b", "#ffe9c9"]},
}
