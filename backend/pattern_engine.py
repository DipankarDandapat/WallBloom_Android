"""
Pattern generation engine for WallBloom
Generates procedural wallpapers with deterministic output based on seed
"""

import random
import math
from PIL import Image, ImageDraw
from enum import Enum
from io import BytesIO

class PatternType(str, Enum):
    HILLS = "hills"
    WAVES = "waves"
    DUNES = "dunes"
    MOUNTAINS = "mountains"
    ARCS = "arcs"
    SCRIBBLE = "scribble"
    GEOMETRIC = "geometric"
    NOISE = "noise"
    GRADIENT = "gradient"
    CELLULAR = "cellular"
    SPIRAL = "spiral"
    HEXAGON = "hexagon"
    AURORA = "aurora"
    MANDALA = "mandala"
    VORTEX = "vortex"
    LIGHTNING = "lightning"
    BUBBLES = "bubbles"
    DIAMOND = "diamond"
    LAVA = "lava"
    CIRCUIT = "circuit"
    GALAXY = "galaxy"
    RIPPLE = "ripple"
    MOSAIC = "mosaic"
    TERRACES = "terraces"
    TIDES = "tides"
    SANDSTORM = "sandstorm"
    PEAKS = "peaks"
    RINGS = "rings"
    BRUSHSTROKE = "brushstroke"
    CONTOUR = "contour"
    PLAID = "plaid"
    STARBURST = "starburst"
    WEAVE = "weave"
    PEBBLES = "pebbles"
    CHEVRON = "chevron"
    FRACTAL = "fractal"
    COBWEB = "cobweb"
    ORIGAMI = "origami"
    NOODLES = "noodles"
    CRYSTALS = "crystals"
    SMOKE = "smoke"
    LABYRINTH = "labyrinth"
    POLKA = "polka"
    FEATHERS = "feathers"
    SCALES = "scales"
    CROSSHATCH = "crosshatch"
    DNA = "dna"
    BINARY_RAIN = "binary_rain"
    RADAR = "radar"
    TOPOGRAPHIC = "topographic"
    WAVEFORM = "waveform"
    SATELLITE = "satellite"
    SONAR = "sonar"
    DATASTREAM = "datastream"
    FIBER_OPTIC = "fiber_optic"
    NEURAL = "neural"
    CORAL = "coral"
    SNOWFLAKES = "snowflakes"
    RAINDROPS = "raindrops"
    VINES = "vines"
    CLOUDS = "clouds"
    BAMBOO = "bamboo"
    CRACKS = "cracks"
    ROOTS = "roots"
    VORONOI = "voronoi"
    KALEIDOSCOPE = "kaleidoscope"
    TRIANGULAR_MESH = "triangular_mesh"
    PINWHEEL = "pinwheel"
    PRISM = "prism"
    HYPNOTIC = "hypnotic"
    PLASMA = "plasma"
    INTERFERENCE = "interference"
    TURBULENCE = "turbulence"
    INK_BLOT = "ink_blot"
    WATERCOLOR = "watercolor"
    POINTILLISM = "pointillism"
    MAZE = "maze"
    CONSTELLATION = "constellation"
    LACE = "lace"
    GLITCH = "glitch"
    STAINED_GLASS = "stained_glass"
    TOPSOIL = "topsoil"
    FISH_NET = "fish_net"
    HONEYCOMB_FLOW = "honeycomb_flow"
    PIXEL_SORT = "pixel_sort"
    SAND_RIPPLE = "sand_ripple"
    TREE_RINGS = "tree_rings"
    LIGHTNING_FIELD = "lightning_field"
    SOAP_BUBBLE = "soap_bubble"
    CELTIC_KNOT = "celtic_knot"
    METEOR_SHOWER = "meteor_shower"
    LENTICULAR = "lenticular"
    BRUSH_GRID = "brush_grid"
    NEON_GRID = "neon_grid"
    PATCHWORK = "patchwork"
    SUNBURST = "sunburst"
    DROPLETS = "droplets"
    WIRE_FRAME = "wire_frame"

# Color palettes
PRESET_PALETTES = [
    {
        "name": "Charcoal",
        "colors": ["#1a1a1a", "#4a4a4a", "#8a8a8a", "#d0d0d0"]
    },
    {
        "name": "Stone",
        "colors": ["#2c2c2c", "#5a5a5a", "#9a9a9a", "#e0e0e0"]
    },
    {
        "name": "Ocean Blue",
        "colors": ["#001f3f", "#0074d9", "#7fdbca", "#b3e5fc"]
    },
    {
        "name": "Sunrise",
        "colors": ["#ff6b35", "#f7931e", "#fdb833", "#fff4e6"]
    },
    {
        "name": "Fire",
        "colors": ["#8b0000", "#ff4500", "#ffa500", "#ffe4b5"]
    },
    {
        "name": "Purple",
        "colors": ["#2d1b4e", "#6a0572", "#ab47bc", "#e1bee7"]
    },
    {
        "name": "Neon",
        "colors": ["#0a0e27", "#ff006e", "#00f5ff", "#ffbe0b"]
    },
    {
        "name": "Arctic",
        "colors": ["#0c1821", "#1a535c", "#4ecdc4", "#f7fff7"]
    },
    {
        "name": "Forest",
        "colors": ["#0b3d2c", "#1e5631", "#40916c", "#d8f3dc"]
    },
    {
        "name": "Sunset",
        "colors": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"]
    },
    {
        "name": "Deep Space",
        "colors": ["#0a0a0a", "#1a1a2e", "#16213e", "#0f3460"]
    },
    {
        "name": "Tropical",
        "colors": ["#06d6a0", "#118ab2", "#073b4c", "#ef476f"]
    },
    {
        "name": "Cherry Blossom",
        "colors": ["#fff0f3", "#ffb3c1", "#ff4d6d", "#c9184a"]
    },
    {
        "name": "Midnight Gold",
        "colors": ["#0d0d0d", "#1a1a2e", "#c9a84c", "#f5d76e"]
    },
    {
        "name": "Cyberpunk",
        "colors": ["#0d0221", "#ff2079", "#00fff5", "#7b2fff"]
    },
    {
        "name": "Autumn",
        "colors": ["#3d1c02", "#a0522d", "#d2691e", "#f4a460"]
    },
    {
        "name": "Mint",
        "colors": ["#004d40", "#00796b", "#80cbc4", "#e0f2f1"]
    },
    {
        "name": "Rose Gold",
        "colors": ["#3b1219", "#8b3a52", "#d4a0a7", "#f9e4e8"]
    },
    {
        "name": "Lava",
        "colors": ["#1a0000", "#7f0000", "#e63900", "#ff9933"]
    },
    {
        "name": "Ice",
        "colors": ["#e8f4f8", "#a8d8ea", "#4a90d9", "#1a3a5c"]
    },
    {
        "name": "Galaxy",
        "colors": ["#0b0c2a", "#3d1a78", "#8e44ad", "#e056fd"]
    },
    {
        "name": "Emerald",
        "colors": ["#022c22", "#065f46", "#34d399", "#d1fae5"]
    },
    {
        "name": "Candy",
        "colors": ["#ff6eb4", "#ff9de2", "#c3f0ca", "#fffacd"]
    },
    {
        "name": "Rust",
        "colors": ["#1c0a00", "#6e2c00", "#b85c00", "#e8a87c"]
    },
    {
        "name": "Neon Jungle",
        "colors": ["#0a1a0a", "#00ff41", "#ff00ff", "#ffff00"]
    },
    {
        "name": "Dusk",
        "colors": ["#1a1035", "#4a2060", "#c0608a", "#f4a96a"]
    },
    {
        "name": "Steel",
        "colors": ["#1c2833", "#2e4057", "#607d8b", "#cfd8dc"]
    },
    {
        "name": "Bioluminescence",
        "colors": ["#000d1a", "#003366", "#00ccff", "#99ffee"]
    },
    {
        "name": "Volcanic Ash",
        "colors": ["#1a0a00", "#4a3728", "#9e7b5a", "#e8d5b7"]
    },
    {
        "name": "Peacock",
        "colors": ["#003333", "#006666", "#33cccc", "#99ffcc"]
    },
    {
        "name": "Blood Moon",
        "colors": ["#0d0000", "#4d0000", "#cc2200", "#ff6633"]
    },
    {
        "name": "Ultraviolet",
        "colors": ["#0a0014", "#2d0057", "#7700cc", "#cc66ff"]
    },
    {
        "name": "Matcha",
        "colors": ["#1a2e1a", "#3d6b35", "#86b049", "#d4e8a0"]
    },
    {
        "name": "Sandstone",
        "colors": ["#2e1f0e", "#7a5c3a", "#c4a882", "#f5e6cc"]
    },
    {
        "name": "Northern Lights",
        "colors": ["#020b18", "#0d4f3c", "#1aff9c", "#b3fff0"]
    },
    {
        "name": "Coral Reef",
        "colors": ["#003049", "#d62828", "#f77f00", "#fcbf49"]
    },
    {
        "name": "Lavender",
        "colors": ["#1a0533", "#6b2d8b", "#b57bee", "#e8d5f5"]
    },
    {
        "name": "Copper",
        "colors": ["#1a0a00", "#7c3a1e", "#b87333", "#f0c080"]
    },
    {
        "name": "Teal Storm",
        "colors": ["#001a1a", "#004d4d", "#009999", "#66ffff"]
    },
    {
        "name": "Sakura Night",
        "colors": ["#0d0010", "#3d0030", "#cc3399", "#ffccee"]
    },
    {
        "name": "Amber",
        "colors": ["#1a0d00", "#7a3b00", "#e08000", "#ffd580"]
    },
    {
        "name": "Slate Blue",
        "colors": ["#0a0f1e", "#1e3a5f", "#4a7fc1", "#a8c8f0"]
    },
    {
        "name": "Jade",
        "colors": ["#001a0d", "#004d26", "#00a86b", "#80ffc0"]
    },
    {
        "name": "Crimson",
        "colors": ["#0d0000", "#4d0011", "#cc0033", "#ff6680"]
    },
    {
        "name": "Moonlight",
        "colors": ["#05050f", "#1a1a3e", "#9999cc", "#e8e8ff"]
    },
    {
        "name": "Tangerine",
        "colors": ["#1a0500", "#7a2600", "#e05c00", "#ffb380"]
    },
    {
        "name": "Seafoam",
        "colors": ["#001a14", "#00664d", "#33cc99", "#b3ffe6"]
    },
    {
        "name": "Obsidian",
        "colors": ["#000000", "#0d0d0d", "#1a1a1a", "#4d4d4d"]
    },
    {
        "name": "Bubblegum",
        "colors": ["#ff80bf", "#ff99cc", "#ffccee", "#fff0f8"]
    },
    {
        "name": "Toxic",
        "colors": ["#0a1a00", "#1a4d00", "#66cc00", "#ccff33"]
    }
]

class SeededRandom:
    """Seeded random number generator for reproducible patterns"""
    
    def __init__(self, seed):
        self.rng = random.Random(seed)
    
    def random(self):
        return self.rng.random()
    
    def randint(self, a, b):
        return self.rng.randint(a, b)
    
    def choice(self, seq):
        return self.rng.choice(seq)
    
    def uniform(self, a, b):
        return self.rng.uniform(a, b)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def invert_color(hex_color):
    """Invert a hex color"""
    r, g, b = hex_to_rgb(hex_color)
    return f"#{255-r:02x}{255-g:02x}{255-b:02x}"

def get_palette_colors(palette_index, inverted=False):
    """Get colors from palette"""
    palette_index = palette_index % len(PRESET_PALETTES)
    palette = PRESET_PALETTES[palette_index]
    colors = palette["colors"]
    
    if inverted:
        return [invert_color(c) for c in colors]
    return colors

def generate_hills(draw, width, height, colors, rng):
    """Generate hills pattern"""
    num_hills = rng.randint(3, 6)
    
    for i in range(num_hills):
        x_offset = rng.randint(-width // 2, width)
        amplitude = rng.randint(height // 4, height // 2)
        frequency = rng.uniform(0.001, 0.01)
        
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        
        points = []
        for x in range(width):
            y = int(height / 2 + math.sin((x + x_offset) * frequency) * amplitude)
            points.append((x, y))
        
        # Draw filled polygon
        for j in range(len(points) - 1):
            x1, y1 = points[j]
            x2, y2 = points[j + 1]
            draw.line([(x1, y1), (x2, y2)], fill=rgb, width=2)

def generate_waves(draw, width, height, colors, rng):
    """Generate waves pattern"""
    num_waves = rng.randint(4, 8)
    wave_height = height // (num_waves + 1)
    
    for i in range(num_waves):
        y = (i + 1) * wave_height
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        
        points = []
        for x in range(width):
            offset = math.sin(x * 0.01) * 20
            points.append((x, int(y + offset)))
        
        draw.polygon(points + [(width, height), (0, height)], fill=rgb)

def generate_mountains(draw, width, height, colors, rng):
    """Generate mountains pattern"""
    num_peaks = rng.randint(3, 5)
    peaks = []
    
    for _ in range(num_peaks):
        peaks.append({
            'x': rng.randint(0, width),
            'height': rng.randint(height // 3, height),
            'width': rng.randint(width // 4, width // 2)
        })
    
    for i, peak in enumerate(peaks):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        
        points = []
        for x in range(width):
            dist = abs(x - peak['x'])
            if dist < peak['width']:
                y = height - int(peak['height'] * (1 - dist / peak['width']))
            else:
                y = height
            points.append((x, y))
        
        draw.polygon(points, fill=rgb)

def generate_geometric(draw, width, height, colors, rng):
    """Generate geometric pattern"""
    num_shapes = rng.randint(20, 40)
    
    for i in range(num_shapes):
        shape_type = rng.choice(['circle', 'rect', 'triangle'])
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        size = rng.randint(20, 100)
        
        if shape_type == 'circle':
            draw.ellipse([x, y, x + size, y + size], fill=rgb)
        elif shape_type == 'rect':
            draw.rectangle([x, y, x + size, y + size], fill=rgb)
        else:
            draw.polygon([(x, y), (x + size, y), (x + size // 2, y + size)], fill=rgb)

def generate_gradient(draw, width, height, colors, rng):
    """Generate gradient pattern"""
    color1 = hex_to_rgb(colors[0])
    color2 = hex_to_rgb(colors[-1])
    
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def generate_noise(draw, width, height, colors, rng):
    """Generate noise pattern"""
    for x in range(0, width, 5):
        for y in range(0, height, 5):
            color = colors[rng.randint(0, len(colors) - 1)]
            rgb = hex_to_rgb(color)
            draw.rectangle([x, y, x + 5, y + 5], fill=rgb)

def generate_dunes(draw, width, height, colors, rng):
    """Generate sand dunes pattern"""
    num_dunes = rng.randint(4, 8)
    
    for i in range(num_dunes):
        y = int(height * (i + 1) / (num_dunes + 1))
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        
        amplitude = rng.randint(10, 30)
        frequency = rng.uniform(0.005, 0.015)
        
        points = []
        for x in range(width):
            offset = math.sin(x * frequency) * amplitude
            points.append((x, int(y + offset)))
        
        draw.polygon(points + [(width, height), (0, height)], fill=rgb)

def generate_arcs(draw, width, height, colors, rng):
    """Generate arcs pattern"""
    num_arcs = rng.randint(5, 10)
    
    for i in range(num_arcs):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        radius = rng.randint(50, 200)
        
        draw.arc([x - radius, y - radius, x + radius, y + radius], 0, 360, fill=rgb, width=3)

def generate_scribble(draw, width, height, colors, rng):
    """Generate scribble pattern"""
    num_lines = rng.randint(20, 50)
    
    for i in range(num_lines):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        
        x1 = rng.randint(0, width)
        y1 = rng.randint(0, height)
        x2 = x1 + rng.randint(-100, 100)
        y2 = y1 + rng.randint(-100, 100)
        
        draw.line([(x1, y1), (x2, y2)], fill=rgb, width=2)

def generate_spiral(draw, width, height, colors, rng):
    """Generate spiral pattern"""
    cx, cy = width // 2, height // 2
    num_spirals = rng.randint(2, 5)
    max_radius = math.sqrt(cx**2 + cy**2)

    for s in range(num_spirals):
        color = colors[s % len(colors)]
        rgb = hex_to_rgb(color)
        angle_offset = rng.uniform(0, 2 * math.pi)
        tightness = rng.uniform(0.08, 0.2)
        points = []
        for i in range(1200):
            angle = i * 0.05 + angle_offset
            r = tightness * angle * (max_radius / (tightness * 1200 * 0.05))
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle))
            if 0 <= x < width and 0 <= y < height:
                points.append((x, y))
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=rgb, width=3)


def generate_hexagon(draw, width, height, colors, rng):
    """Generate hexagonal grid pattern"""
    size = rng.randint(30, 70)
    hex_w = size * 2
    hex_h = math.sqrt(3) * size
    col_idx = 0

    x = 0
    while x < width + hex_w:
        row_idx = 0
        y_offset = (hex_h / 2) if (col_idx % 2) else 0
        y = -hex_h + y_offset
        while y < height + hex_h:
            color = colors[(col_idx + row_idx) % len(colors)]
            rgb = hex_to_rgb(color)
            pts = [
                (x + size * math.cos(math.radians(60 * i)), y + size * math.sin(math.radians(60 * i)))
                for i in range(6)
            ]
            draw.polygon(pts, fill=rgb, outline=(0, 0, 0))
            y += hex_h
            row_idx += 1
        x += hex_w * 0.75
        col_idx += 1


def generate_aurora(draw, width, height, colors, rng):
    """Generate aurora borealis curtain pattern"""
    num_bands = rng.randint(4, 8)
    for i in range(num_bands):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        base_y = int(height * rng.uniform(0.1, 0.7))
        band_height = rng.randint(height // 8, height // 3)
        freq = rng.uniform(0.003, 0.008)
        phase = rng.uniform(0, 2 * math.pi)

        for dy in range(band_height):
            alpha = int(180 * (1 - dy / band_height))
            blended = tuple(int(c * alpha / 255) for c in rgb)
            points = []
            for x in range(width):
                y = base_y + dy + int(20 * math.sin(x * freq + phase))
                if 0 <= y < height:
                    points.append((x, y))
            for p in points:
                draw.point(p, fill=blended)


def generate_mandala(draw, width, height, colors, rng):
    """Generate mandala / radial symmetry pattern"""
    cx, cy = width // 2, height // 2
    num_rings = rng.randint(4, 8)
    petals = rng.randint(6, 12)

    for ring in range(num_rings, 0, -1):
        radius = int((ring / num_rings) * min(cx, cy))
        color = colors[ring % len(colors)]
        rgb = hex_to_rgb(color)
        for p in range(petals):
            angle = (2 * math.pi / petals) * p
            next_angle = (2 * math.pi / petals) * (p + 1)
            pts = [
                (cx, cy),
                (cx + radius * math.cos(angle), cy + radius * math.sin(angle)),
                (cx + radius * math.cos((angle + next_angle) / 2) * 1.15, cy + radius * math.sin((angle + next_angle) / 2) * 1.15),
                (cx + radius * math.cos(next_angle), cy + radius * math.sin(next_angle)),
            ]
            draw.polygon(pts, fill=rgb)


def generate_vortex(draw, width, height, colors, rng):
    """Generate vortex / twisted concentric rings pattern"""
    cx, cy = width // 2, height // 2
    num_rings = rng.randint(20, 40)
    twist = rng.uniform(0.05, 0.2)
    max_r = int(math.sqrt(cx**2 + cy**2))

    for i in range(num_rings, 0, -1):
        r = int((i / num_rings) * max_r)
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        pts = []
        steps = max(60, r)
        for s in range(steps + 1):
            angle = (2 * math.pi / steps) * s + twist * i
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        if len(pts) >= 2:
            draw.line(pts, fill=rgb, width=max(1, r // 10))


def generate_lightning(draw, width, height, colors, rng):
    """Generate lightning bolt branching pattern"""
    num_bolts = rng.randint(3, 7)
    for b in range(num_bolts):
        color = colors[b % len(colors)]
        rgb = hex_to_rgb(color)
        x = rng.randint(width // 4, 3 * width // 4)
        y = 0
        segments = rng.randint(8, 16)
        seg_h = height // segments
        for _ in range(segments):
            nx = x + rng.randint(-80, 80)
            ny = y + seg_h
            draw.line([(x, y), (nx, ny)], fill=rgb, width=rng.randint(1, 4))
            # branch
            if rng.random() > 0.6:
                bx = nx + rng.randint(-60, 60)
                by = ny + rng.randint(20, 60)
                draw.line([(nx, ny), (bx, by)], fill=rgb, width=1)
            x, y = nx, ny


def generate_bubbles(draw, width, height, colors, rng):
    """Generate floating bubbles pattern"""
    num_bubbles = rng.randint(30, 80)
    for i in range(num_bubbles):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        r = rng.randint(10, 80)
        draw.ellipse([x - r, y - r, x + r, y + r], outline=rgb, width=2)
        # inner highlight
        hr = max(2, r // 4)
        draw.ellipse([x - hr, y - hr - r // 3, x + hr, y + hr - r // 3], fill=rgb)


def generate_diamond(draw, width, height, colors, rng):
    """Generate diamond / rhombus grid pattern"""
    size = rng.randint(40, 90)
    rows = height // size + 2
    cols = width // size + 2
    for row in range(rows):
        for col in range(cols):
            cx = col * size + (size // 2 if row % 2 else 0)
            cy = row * size
            color = colors[(row + col) % len(colors)]
            rgb = hex_to_rgb(color)
            pts = [
                (cx, cy - size // 2),
                (cx + size // 2, cy),
                (cx, cy + size // 2),
                (cx - size // 2, cy),
            ]
            draw.polygon(pts, fill=rgb, outline=(0, 0, 0))


def generate_lava(draw, width, height, colors, rng):
    """Generate lava lamp blob pattern"""
    num_blobs = rng.randint(6, 14)
    # background gradient
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1 % len(colors)])
    for y in range(height):
        t = y / height
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    for i in range(num_blobs):
        color = colors[(i + 2) % len(colors)]
        rgb = hex_to_rgb(color)
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        rx = rng.randint(30, 120)
        ry = rng.randint(40, 160)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rgb)


def generate_circuit(draw, width, height, colors, rng):
    """Generate circuit board trace pattern"""
    grid = 40
    color_bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=color_bg)
    num_traces = rng.randint(30, 60)
    for i in range(num_traces):
        color = colors[(i % (len(colors) - 1)) + 1]
        rgb = hex_to_rgb(color)
        x = rng.randint(0, width // grid) * grid
        y = rng.randint(0, height // grid) * grid
        length = rng.randint(3, 10)
        direction = rng.choice(['h', 'v'])
        for _ in range(length):
            nx = x + (grid if direction == 'h' else 0)
            ny = y + (grid if direction == 'v' else 0)
            if 0 <= nx <= width and 0 <= ny <= height:
                draw.line([(x, y), (nx, ny)], fill=rgb, width=2)
                # node dot
                draw.ellipse([nx - 4, ny - 4, nx + 4, ny + 4], fill=rgb)
            x, y = nx, ny
            if rng.random() > 0.7:
                direction = rng.choice(['h', 'v'])


def generate_galaxy(draw, width, height, colors, rng):
    """Generate galaxy star field with spiral arms"""
    # dark background
    draw.rectangle([0, 0, width, height], fill=hex_to_rgb(colors[0]))
    cx, cy = width // 2, height // 2
    # stars
    for _ in range(800):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        r = rng.randint(0, 2)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
    # spiral arms
    arms = rng.randint(2, 4)
    for arm in range(arms):
        color = colors[(arm + 1) % len(colors)]
        rgb = hex_to_rgb(color)
        offset = (2 * math.pi / arms) * arm
        for i in range(600):
            t = i / 600
            angle = t * 4 * math.pi + offset
            r = t * min(cx, cy) * 0.9
            spread = rng.randint(-8, 8)
            x = int(cx + (r + spread) * math.cos(angle))
            y = int(cy + (r + spread) * math.sin(angle))
            if 0 <= x < width and 0 <= y < height:
                draw.point((x, y), fill=rgb)


def generate_ripple(draw, width, height, colors, rng):
    """Generate concentric ripple / water drop pattern"""
    num_centers = rng.randint(2, 5)
    centers = [(rng.randint(0, width), rng.randint(0, height)) for _ in range(num_centers)]
    max_r = int(math.sqrt(width**2 + height**2))
    ring_gap = rng.randint(20, 50)
    for idx, (cx, cy) in enumerate(centers):
        color = colors[idx % len(colors)]
        rgb = hex_to_rgb(color)
        for r in range(ring_gap, max_r, ring_gap * 2):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgb, width=2)


def generate_mosaic(draw, width, height, colors, rng):
    """Generate stained-glass mosaic pattern"""
    tile_w = rng.randint(30, 70)
    tile_h = rng.randint(30, 70)
    for y in range(0, height, tile_h):
        for x in range(0, width, tile_w):
            color = colors[rng.randint(0, len(colors) - 1)]
            rgb = hex_to_rgb(color)
            # slight random offset for organic feel
            ox = rng.randint(-5, 5)
            oy = rng.randint(-5, 5)
            pts = [
                (x + ox, y + oy),
                (x + tile_w + ox, y + oy),
                (x + tile_w + ox, y + tile_h + oy),
                (x + ox, y + tile_h + oy),
            ]
            draw.polygon(pts, fill=rgb, outline=(30, 30, 30))


def generate_terraces(draw, width, height, colors, rng):
    """Stepped layered terraces — like rice field terraces"""
    num_layers = rng.randint(5, 10)
    for i in range(num_layers):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        base_y = int(height * (i + 1) / (num_layers + 1))
        step_h = rng.randint(8, 20)
        freq = rng.uniform(0.004, 0.012)
        phase = rng.uniform(0, math.pi)
        pts = []
        for x in range(width):
            # quantize to steps for terrace effect
            raw = base_y + math.sin(x * freq + phase) * rng.uniform(20, 50)
            y = int(raw // step_h) * step_h
            pts.append((x, y))
        draw.polygon(pts + [(width, height), (0, height)], fill=rgb)


def generate_tides(draw, width, height, colors, rng):
    """Double-frequency overlapping tide waves"""
    num_layers = rng.randint(4, 7)
    for i in range(num_layers):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        base_y = int(height * (i + 1) / (num_layers + 1))
        f1 = rng.uniform(0.006, 0.014)
        f2 = rng.uniform(0.002, 0.006)
        a1 = rng.randint(10, 25)
        a2 = rng.randint(15, 35)
        pts = []
        for x in range(width):
            y = base_y + int(math.sin(x * f1) * a1 + math.sin(x * f2 + 1.2) * a2)
            pts.append((x, y))
        draw.polygon(pts + [(width, height), (0, height)], fill=rgb)


def generate_sandstorm(draw, width, height, colors, rng):
    """Diagonal wind-blown sand streak lines"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_streaks = rng.randint(60, 140)
    for i in range(num_streaks):
        color = colors[(i % (len(colors) - 1)) + 1]
        rgb = hex_to_rgb(color)
        x1 = rng.randint(-width // 2, width)
        y1 = rng.randint(0, height)
        length = rng.randint(80, 300)
        angle = rng.uniform(-0.3, 0.3)  # mostly horizontal
        x2 = int(x1 + length * math.cos(angle))
        y2 = int(y1 + length * math.sin(angle))
        w = rng.randint(1, 3)
        draw.line([(x1, y1), (x2, y2)], fill=rgb, width=w)


def generate_peaks(draw, width, height, colors, rng):
    """Sharp jagged mountain peaks — more angular than mountains"""
    num_peaks = rng.randint(6, 14)
    # draw back-to-front layers
    for layer in range(3, 0, -1):
        color = colors[(layer - 1) % len(colors)]
        rgb = hex_to_rgb(color)
        horizon = int(height * (0.3 + layer * 0.15))
        pts = [(0, height)]
        x = 0
        while x < width:
            peak_x = x + rng.randint(width // (num_peaks + 1) - 20, width // (num_peaks + 1) + 20)
            peak_y = rng.randint(int(horizon * 0.4), horizon)
            pts.append((peak_x, peak_y))
            valley_x = peak_x + rng.randint(20, 60)
            pts.append((valley_x, horizon))
            x = valley_x
        pts.append((width, height))
        draw.polygon(pts, fill=rgb)


def generate_rings(draw, width, height, colors, rng):
    """Concentric arcs radiating from corners and edges"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    origins = [
        (0, 0), (width, 0), (0, height), (width, height),
        (width // 2, 0), (0, height // 2),
    ]
    chosen = [origins[rng.randint(0, len(origins) - 1)] for _ in range(rng.randint(2, 4))]
    max_r = int(math.sqrt(width ** 2 + height ** 2))
    gap = rng.randint(25, 55)
    for oi, (ox, oy) in enumerate(chosen):
        color = colors[(oi + 1) % len(colors)]
        rgb = hex_to_rgb(color)
        for r in range(gap, max_r, gap * 2):
            draw.arc([ox - r, oy - r, ox + r, oy + r], 0, 360, fill=rgb, width=rng.randint(2, 5))


def generate_brushstroke(draw, width, height, colors, rng):
    """Flowing thick paint brushstroke bands"""
    num_strokes = rng.randint(5, 10)
    for i in range(num_strokes):
        color = colors[i % len(colors)]
        rgb = hex_to_rgb(color)
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        stroke_w = rng.randint(40, 120)
        freq = rng.uniform(0.003, 0.009)
        phase = rng.uniform(0, 2 * math.pi)
        pts_top, pts_bot = [], []
        for x in range(width):
            mid_y = cy + int(math.sin(x * freq + phase) * rng.uniform(20, 60))
            half = stroke_w // 2 + int(math.sin(x * freq * 2) * stroke_w * 0.15)
            pts_top.append((x, mid_y - half))
            pts_bot.append((x, mid_y + half))
        draw.polygon(pts_top + list(reversed(pts_bot)), fill=rgb)


def generate_contour(draw, width, height, colors, rng):
    """Topographic contour map lines"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_centers = rng.randint(2, 4)
    centers = [(rng.randint(width // 4, 3 * width // 4),
                 rng.randint(height // 4, 3 * height // 4)) for _ in range(num_centers)]
    num_lines = rng.randint(12, 22)
    for li in range(num_lines):
        color = colors[(li % (len(colors) - 1)) + 1]
        rgb = hex_to_rgb(color)
        threshold = (li + 1) / (num_lines + 1)
        pts = []
        for x in range(0, width, 3):
            # sum of gaussian hills
            val = sum(
                math.exp(-((x - cx) ** 2 + (0 - cy) ** 2) / (2 * (width * 0.25) ** 2))
                for cx, cy in centers
            )
            for y in range(0, height, 3):
                v = sum(
                    math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * (width * 0.25) ** 2))
                    for cx, cy in centers
                )
                if abs(v - threshold) < 0.015:
                    pts.append((x, y))
        for p in pts:
            draw.point(p, fill=rgb)


def generate_plaid(draw, width, height, colors, rng):
    """Woven plaid / tartan crossing stripe pattern"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_stripes = rng.randint(4, 8)
    stripe_w = rng.randint(20, 50)
    gap = rng.randint(40, 90)
    # horizontal stripes
    for i in range(num_stripes):
        color = colors[(i % (len(colors) - 1)) + 1]
        rgb = hex_to_rgb(color)
        y = rng.randint(0, height)
        draw.rectangle([0, y, width, y + stripe_w], fill=(*rgb, 160))
    # vertical stripes
    for i in range(num_stripes):
        color = colors[((i + 2) % (len(colors) - 1)) + 1]
        rgb = hex_to_rgb(color)
        x = rng.randint(0, width)
        # draw semi-transparent by blending manually
        for px in range(x, min(x + stripe_w, width)):
            for py in range(height):
                try:
                    existing = draw._image.getpixel((px, py))
                    blended = tuple(int(existing[c] * 0.5 + rgb[c] * 0.5) for c in range(3))
                    draw.point((px, py), fill=blended)
                except Exception:
                    pass


def generate_starburst(draw, width, height, colors, rng):
    """Radiating spikes from multiple centers"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_centers = rng.randint(2, 5)
    for ci in range(num_centers):
        cx = rng.randint(width // 4, 3 * width // 4)
        cy = rng.randint(height // 4, 3 * height // 4)
        num_spikes = rng.randint(12, 24)
        max_len = rng.randint(int(min(width, height) * 0.2), int(min(width, height) * 0.5))
        color = colors[(ci + 1) % len(colors)]
        rgb = hex_to_rgb(color)
        for s in range(num_spikes):
            angle = (2 * math.pi / num_spikes) * s
            length = max_len * rng.uniform(0.6, 1.0)
            ex = int(cx + length * math.cos(angle))
            ey = int(cy + length * math.sin(angle))
            draw.line([(cx, cy), (ex, ey)], fill=rgb, width=rng.randint(1, 4))


def generate_weave(draw, width, height, colors, rng):
    """Interlocking over-under basket weave"""
    stripe = rng.randint(20, 45)
    for row, y in enumerate(range(0, height, stripe)):
        rgb = hex_to_rgb(colors[row % len(colors)])
        draw.rectangle([0, y, width, y + stripe - 1], fill=rgb)
    for col, x in enumerate(range(0, width, stripe)):
        rgb = hex_to_rgb(colors[(col + 2) % len(colors)])
        for row, y in enumerate(range(0, height, stripe)):
            if (row + col) % 2 == 0:
                draw.rectangle([x, y, x + stripe - 1, y + stripe - 1], fill=rgb)


def generate_pebbles(draw, width, height, colors, rng):
    """Randomly packed oval pebble shapes"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for i in range(rng.randint(40, 100)):
        rgb = hex_to_rgb(colors[(i % (len(colors) - 1)) + 1])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        rx = rng.randint(15, 55)
        ry = rng.randint(10, 35)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rgb, outline=bg)


def generate_chevron(draw, width, height, colors, rng):
    """Repeating V-shaped chevron zigzag rows"""
    band_h = rng.randint(30, 70)
    for row, base_y in enumerate(range(-band_h, height + band_h, band_h)):
        rgb = hex_to_rgb(colors[row % len(colors)])
        pts = []
        for x in range(0, width + 2, 2):
            phase = x % (band_h * 2)
            y_off = phase if phase < band_h else (band_h * 2 - phase)
            pts.append((x, base_y + y_off))
        pts += [(width, height + band_h), (0, height + band_h)]
        draw.polygon(pts, fill=rgb)


def generate_fractal(draw, width, height, colors, rng):
    """Iterative Sierpinski-inspired triangle subdivision"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    margin = 20
    depth = rng.randint(3, 5)
    stack = [([(width//2, margin), (width-margin, height-margin), (margin, height-margin)], depth, 1)]
    while stack:
        pts, d, ci = stack.pop()
        if d == 0:
            draw.polygon(pts, fill=hex_to_rgb(colors[ci % len(colors)]))
            continue
        ax, ay = pts[0]; bx, by = pts[1]; cx2, cy2 = pts[2]
        m1 = ((ax+bx)/2, (ay+by)/2)
        m2 = ((bx+cx2)/2, (by+cy2)/2)
        m3 = ((ax+cx2)/2, (ay+cy2)/2)
        stack.append(([pts[0], m1, m3], d-1, ci))
        stack.append(([m1, pts[1], m2], d-1, ci+1))
        stack.append(([m3, m2, pts[2]], d-1, ci+2))


def generate_cobweb(draw, width, height, colors, rng):
    """Spider web with radial spokes and concentric polygon rings"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cx, cy = width // 2, height // 2
    spokes = rng.randint(8, 16)
    rings = rng.randint(6, 12)
    max_r = int(min(width, height) * 0.48)
    spoke_rgb = hex_to_rgb(colors[1 % len(colors)])
    for s in range(spokes):
        angle = (2 * math.pi / spokes) * s
        draw.line([(cx, cy), (int(cx + max_r * math.cos(angle)), int(cy + max_r * math.sin(angle)))],
                  fill=spoke_rgb, width=1)
    for ri in range(1, rings + 1):
        r = int(max_r * ri / rings)
        rgb = hex_to_rgb(colors[(ri + 1) % len(colors)])
        pts = [(int(cx + r * math.cos((2 * math.pi / spokes) * s)),
                int(cy + r * math.sin((2 * math.pi / spokes) * s))) for s in range(spokes)]
        draw.polygon(pts, outline=rgb)


def generate_origami(draw, width, height, colors, rng):
    """Flat-fold origami triangular facets"""
    cols_n = rng.randint(6, 12)
    rows_n = rng.randint(4, 8)
    cw = width // cols_n
    rh = height // rows_n
    for row in range(rows_n + 1):
        for col in range(cols_n + 1):
            x, y = col * cw, row * rh
            r1 = hex_to_rgb(colors[(row + col) % len(colors)])
            r2 = hex_to_rgb(colors[(row + col + 1) % len(colors)])
            draw.polygon([(x, y), (x + cw, y), (x, y + rh)], fill=r1)
            draw.polygon([(x + cw, y), (x + cw, y + rh), (x, y + rh)], fill=r2)


def generate_noodles(draw, width, height, colors, rng):
    """Long curvy flowing noodle ribbon lines"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for i in range(rng.randint(15, 35)):
        rgb = hex_to_rgb(colors[(i % (len(colors) - 1)) + 1])
        x, y = rng.randint(0, width), rng.randint(0, height)
        pts = [(x, y)]
        for _ in range(rng.randint(8, 20)):
            x += rng.randint(-60, 60)
            y += rng.randint(-40, 40)
            pts.append((x, y))
        if len(pts) >= 2:
            draw.line(pts, fill=rgb, width=rng.randint(3, 10))


def generate_crystals(draw, width, height, colors, rng):
    """Angular crystal gem facet polygons"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for i in range(rng.randint(15, 35)):
        rgb = hex_to_rgb(colors[(i % (len(colors) - 1)) + 1])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        sides = rng.randint(4, 7)
        rx = rng.randint(20, 80)
        ry = rng.randint(30, 100)
        rot = rng.uniform(0, math.pi)
        pts = [(cx + rx * math.cos(rot + 2 * math.pi * s / sides),
                cy + ry * math.sin(rot + 2 * math.pi * s / sides)) for s in range(sides)]
        draw.polygon(pts, fill=rgb, outline=bg)


def generate_smoke(draw, width, height, colors, rng):
    """Soft drifting smoke plume columns"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for pi in range(rng.randint(3, 7)):
        rgb = hex_to_rgb(colors[(pi % (len(colors) - 1)) + 1])
        base_x = rng.randint(width // 6, 5 * width // 6)
        for y in range(height, -1, -4):
            t = 1 - y / height
            radius = int(10 + t * rng.uniform(40, 90))
            drift = int(math.sin(y * 0.03 + pi) * 30 * t)
            cx = base_x + drift
            af = t * 0.6
            blended = tuple(int(bg[c] * (1 - af) + rgb[c] * af) for c in range(3))
            draw.ellipse([cx - radius, y - radius // 2, cx + radius, y + radius // 2], fill=blended)


def generate_labyrinth(draw, width, height, colors, rng):
    """Rectangular maze-like corridor grid"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cell = rng.randint(30, 60)
    wall_rgb = hex_to_rgb(colors[1 % len(colors)])
    for row in range(height // cell + 1):
        for col in range(width // cell + 1):
            x, y = col * cell, row * cell
            if col < width // cell and rng.random() > 0.35:
                draw.line([(x, y), (x + cell, y)], fill=wall_rgb, width=2)
            if row < height // cell and rng.random() > 0.35:
                draw.line([(x, y), (x, y + cell)], fill=wall_rgb, width=2)


def generate_polka(draw, width, height, colors, rng):
    """Regular polka dot grid with offset rows"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    spacing = rng.randint(40, 80)
    base_r = rng.randint(8, 20)
    dot_idx = 0
    for row, y in enumerate(range(spacing // 2, height + spacing, spacing)):
        offset = (spacing // 2) if (row % 2) else 0
        for x in range(spacing // 2 + offset, width + spacing, spacing):
            rgb = hex_to_rgb(colors[(dot_idx % (len(colors) - 1)) + 1])
            r = base_r + rng.randint(-4, 4)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=rgb)
            dot_idx += 1


def generate_feathers(draw, width, height, colors, rng):
    """Overlapping feather teardrop leaf shapes"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for i in range(rng.randint(20, 45)):
        rgb = hex_to_rgb(colors[(i % (len(colors) - 1)) + 1])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        length = rng.randint(40, 120)
        fw = rng.randint(15, 40)
        angle = rng.uniform(0, 2 * math.pi)
        tip = (cx + int(length * math.cos(angle)), cy + int(length * math.sin(angle)))
        perp = angle + math.pi / 2
        bl = (cx - int(fw * math.cos(perp)), cy - int(fw * math.sin(perp)))
        br = (cx + int(fw * math.cos(perp)), cy + int(fw * math.sin(perp)))
        draw.polygon([bl, tip, br], fill=rgb)
        draw.line([(cx, cy), tip], fill=hex_to_rgb(colors[0]), width=1)


def generate_scales(draw, width, height, colors, rng):
    """Fish scale overlapping arc tiles"""
    sw = rng.randint(40, 80)
    sh = rng.randint(30, 60)
    for row, y in enumerate(range(0, height + sh, sh)):
        offset = (sw // 2) if (row % 2) else 0
        for col, x in enumerate(range(-sw + offset, width + sw, sw)):
            rgb = hex_to_rgb(colors[(row + col) % len(colors)])
            draw.ellipse([x, y, x + sw, y + sh * 2], fill=rgb,
                         outline=hex_to_rgb(colors[0]))


def generate_crosshatch(draw, width, height, colors, rng):
    """Dense diagonal crosshatch line grid"""
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    spacing = rng.randint(15, 35)
    lw = rng.randint(1, 2)
    c1 = hex_to_rgb(colors[1 % len(colors)])
    c2 = hex_to_rgb(colors[2 % len(colors)])
    for start in range(-height, width + height, spacing):
        draw.line([(start, 0), (start + height, height)], fill=c1, width=lw)
    for start in range(0, width + height + height, spacing):
        draw.line([(start, 0), (start - height, height)], fill=c2, width=lw)


def generate_dna(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    strands = rng.randint(3, 7)
    for s in range(strands):
        cx = int(width * (s + 1) / (strands + 1))
        rgb1 = hex_to_rgb(colors[(s + 1) % len(colors)])
        rgb2 = hex_to_rgb(colors[(s + 2) % len(colors)])
        for y in range(0, height, 6):
            t = y / height
            angle = t * 6 * math.pi
            x1 = cx + int(30 * math.cos(angle))
            x2 = cx + int(30 * math.cos(angle + math.pi))
            draw.ellipse([x1-5, y-5, x1+5, y+5], fill=rgb1)
            draw.ellipse([x2-5, y-5, x2+5, y+5], fill=rgb2)
            if y % 30 == 0:
                draw.line([(x1, y), (x2, y)], fill=rgb1, width=2)

def generate_binary_rain(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    col_w = rng.randint(18, 30)
    for x in range(0, width, col_w):
        rgb = hex_to_rgb(colors[(x // col_w) % len(colors)])
        length = rng.randint(height // 4, height)
        start_y = rng.randint(0, height)
        for i in range(length // 14):
            y = (start_y + i * 14) % height
            bit = rng.choice(['0', '1'])
            alpha = int(255 * (1 - i / (length // 14)))
            c = tuple(int(v * alpha / 255) for v in rgb)
            draw.text((x, y), bit, fill=c) if hasattr(draw, 'text') else draw.rectangle([x, y, x+8, y+10], fill=c)

def generate_radar(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cx, cy = width // 2, height // 2
    max_r = min(cx, cy)
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    for r in range(max_r, 0, -max_r // 6):
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rgb1, width=1)
    for i in range(8):
        angle = i * math.pi / 4
        draw.line([(cx, cy), (int(cx + max_r * math.cos(angle)), int(cy + max_r * math.sin(angle)))], fill=rgb1, width=1)
    sweep = rng.uniform(0, 2 * math.pi)
    for i in range(60):
        a = sweep - i * 0.05
        fade = int(200 * (1 - i / 60))
        fc = tuple(int(v * fade / 255) for v in rgb2)
        draw.line([(cx, cy), (int(cx + max_r * math.cos(a)), int(cy + max_r * math.sin(a)))], fill=fc, width=2)
    blip_count = rng.randint(3, 8)
    for _ in range(blip_count):
        bx = cx + rng.randint(-max_r, max_r)
        by = cy + rng.randint(-max_r, max_r)
        draw.ellipse([bx-4, by-4, bx+4, by+4], fill=rgb2)

def generate_topographic(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    centers = [(rng.randint(width//4, 3*width//4), rng.randint(height//4, 3*height//4)) for _ in range(rng.randint(2, 4))]
    levels = rng.randint(8, 14)
    step = 4  # coarser sampling for performance
    sigma2 = 2 * (width * 0.3) ** 2
    n = len(centers)
    for li in range(levels):
        rgb = hex_to_rgb(colors[(li % (len(colors)-1)) + 1])
        threshold = (li + 1) / (levels + 1)
        for x in range(0, width, step):
            for y in range(0, height, step):
                v = sum(math.exp(-((x-cx)**2+(y-cy)**2)/sigma2) for cx,cy in centers) / n
                if abs(v - threshold) < 0.025:
                    draw.rectangle([x, y, x+step-1, y+step-1], fill=rgb)

def generate_waveform(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_waves = rng.randint(3, 6)
    for i in range(num_waves):
        rgb = hex_to_rgb(colors[(i+1) % len(colors)])
        cy = int(height * (i+1) / (num_waves+1))
        freqs = [rng.uniform(0.005, 0.03) for _ in range(3)]
        amps = [rng.randint(10, 40) for _ in range(3)]
        pts = []
        for x in range(width):
            y = cy + sum(int(amps[j]*math.sin(x*freqs[j])) for j in range(3))
            pts.append((x, y))
        for j in range(len(pts)-1):
            draw.line([pts[j], pts[j+1]], fill=rgb, width=2)

def generate_satellite(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    grid = rng.randint(60, 100)
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    for y in range(0, height, grid):
        for x in range(0, width, grid):
            draw.rectangle([x, y, x+grid, y+grid], outline=rgb1, width=1)
            cx, cy = x + grid//2, y + grid//2
            draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill=rgb2)
            if rng.random() > 0.5:
                draw.line([(cx-grid//3, cy), (cx+grid//3, cy)], fill=rgb1, width=1)
                draw.line([(cx, cy-grid//3), (cx, cy+grid//3)], fill=rgb1, width=1)

def generate_sonar(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_sources = rng.randint(2, 4)
    for si in range(num_sources):
        cx = rng.randint(width//4, 3*width//4)
        cy = rng.randint(height//4, 3*height//4)
        rgb = hex_to_rgb(colors[(si+1) % len(colors)])
        max_r = int(math.sqrt(width**2+height**2))
        gap = rng.randint(30, 60)
        for r in range(gap, max_r, gap*2):
            fade = int(200 * (1 - r/max_r))
            fc = tuple(int(v*fade//200) for v in rgb)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=fc, width=1)

def generate_datastream(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_streams = rng.randint(8, 16)
    for i in range(num_streams):
        rgb = hex_to_rgb(colors[(i % (len(colors)-1))+1])
        x = rng.randint(0, width)
        y = 0
        while y < height:
            seg = rng.randint(10, 40)
            draw.line([(x, y), (x, y+seg)], fill=rgb, width=rng.randint(1, 3))
            y += seg + rng.randint(5, 20)
            x += rng.randint(-20, 20)
            x = max(0, min(width, x))

def generate_fiber_optic(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for i in range(rng.randint(20, 40)):
        rgb = hex_to_rgb(colors[(i % (len(colors)-1))+1])
        x, y = rng.randint(0, width), rng.randint(0, height)
        pts = [(x, y)]
        for _ in range(rng.randint(10, 25)):
            x += rng.randint(-30, 30)
            y += rng.randint(-15, 15)
            pts.append((x, y))
        for j in range(len(pts)-1):
            draw.line([pts[j], pts[j+1]], fill=rgb, width=1)
        ex, ey = pts[-1]
        draw.ellipse([ex-3, ey-3, ex+3, ey+3], fill=rgb)

def generate_neural(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    nodes = [(rng.randint(0, width), rng.randint(0, height)) for _ in range(rng.randint(20, 40))]
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i < j and math.sqrt((x2-x1)**2+(y2-y1)**2) < width//4:
                draw.line([(x1,y1),(x2,y2)], fill=rgb1, width=1)
    for (nx, ny) in nodes:
        r = rng.randint(4, 10)
        draw.ellipse([nx-r, ny-r, nx+r, ny+r], fill=rgb2)

def generate_coral(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(4, 8)):
        stack = [(rng.randint(0,width), height, math.pi/2, rng.randint(40,80), rng.randint(4,6), 1)]
        while stack:
            x, y, angle, length, depth, ci = stack.pop()
            if depth == 0 or length < 3: continue
            rgb = hex_to_rgb(colors[ci % len(colors)])
            ex = int(x + length * math.cos(angle))
            ey = int(y - length * math.sin(angle))
            draw.line([(x,y),(ex,ey)], fill=rgb, width=max(1, depth))
            stack.append((ex, ey, angle+rng.uniform(0.3,0.7), length*0.7, depth-1, ci+1))
            stack.append((ex, ey, angle-rng.uniform(0.3,0.7), length*0.7, depth-1, ci+2))

def generate_snowflakes(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(10, 25)):
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        r = rng.randint(20, 60)
        rgb = hex_to_rgb(colors[rng.randint(1, len(colors)-1)])
        arms = 6
        for a in range(arms):
            angle = a * math.pi / 3
            ex = int(cx + r * math.cos(angle))
            ey = int(cy + r * math.sin(angle))
            draw.line([(cx,cy),(ex,ey)], fill=rgb, width=2)
            for b in [0.4, 0.7]:
                bx = int(cx + r*b*math.cos(angle))
                by = int(cy + r*b*math.sin(angle))
                for sign in [1, -1]:
                    bbx = int(bx + r*0.25*math.cos(angle+sign*math.pi/3))
                    bby = int(by + r*0.25*math.sin(angle+sign*math.pi/3))
                    draw.line([(bx,by),(bbx,bby)], fill=rgb, width=1)

def generate_raindrops(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for i in range(rng.randint(30, 70)):
        rgb = hex_to_rgb(colors[(i % (len(colors)-1))+1])
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        l = rng.randint(10, 30)
        draw.line([(x,y),(x+rng.randint(-3,3),y+l)], fill=rgb, width=1)
        r = rng.randint(3, 8)
        draw.ellipse([x-r, y-r*2, x+r, y], outline=rgb, width=1)

def generate_vines(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(5, 12)):
        rgb = hex_to_rgb(colors[rng.randint(1, len(colors)-1)])
        x, y = rng.randint(0, width), height
        pts = [(x, y)]
        for _ in range(rng.randint(15, 30)):
            x += rng.randint(-20, 20)
            y -= rng.randint(10, 30)
            pts.append((x, y))
        for j in range(len(pts)-1):
            draw.line([pts[j], pts[j+1]], fill=rgb, width=2)
        for j in range(0, len(pts), 3):
            lx, ly = pts[j]
            lw = rng.randint(8, 18)
            lh = rng.randint(5, 12)
            draw.ellipse([lx-lw, ly-lh, lx+lw, ly+lh], fill=rgb)

def generate_clouds(draw, width, height, colors, rng):
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1 % len(colors)])
    for y in range(height):
        t = y / height
        draw.line([(0,y),(width,y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    for _ in range(rng.randint(6, 14)):
        rgb = hex_to_rgb(colors[rng.randint(2, len(colors)-1)])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height//2)
        for _ in range(rng.randint(4, 8)):
            ox = rng.randint(-40, 40)
            oy = rng.randint(-20, 20)
            r = rng.randint(20, 60)
            draw.ellipse([cx+ox-r, cy+oy-r, cx+ox+r, cy+oy+r], fill=rgb)

def generate_bamboo(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(8, 18)):
        rgb = hex_to_rgb(colors[rng.randint(1, len(colors)-1)])
        x = rng.randint(0, width)
        seg_h = rng.randint(30, 60)
        w = rng.randint(6, 16)
        for y in range(0, height, seg_h):
            draw.rectangle([x-w//2, y, x+w//2, y+seg_h-4], fill=rgb)
            draw.line([(x-w//2-4, y+seg_h-4),(x+w//2+4, y+seg_h-4)], fill=bg, width=3)

def generate_cracks(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    rgb = hex_to_rgb(colors[1 % len(colors)])
    for _ in range(rng.randint(3, 7)):
        stack = [(rng.randint(0,width), rng.randint(0,height), rng.uniform(0,2*math.pi), rng.randint(40,100), 5)]
        while stack:
            x, y, angle, length, depth = stack.pop()
            if depth == 0 or length < 5: continue
            ex = int(x + length * math.cos(angle))
            ey = int(y + length * math.sin(angle))
            draw.line([(x,y),(ex,ey)], fill=rgb, width=max(1, depth//2))
            if rng.random() > 0.4:
                stack.append((ex, ey, angle+rng.uniform(0.2,0.8), length*rng.uniform(0.5,0.8), depth-1))
            if rng.random() > 0.5:
                stack.append((ex, ey, angle-rng.uniform(0.2,0.8), length*rng.uniform(0.4,0.7), depth-1))

def generate_roots(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(3, 6)):
        stack = [(rng.randint(0,width), rng.randint(0,height//2), math.pi/2+rng.uniform(-0.5,0.5), rng.randint(50,100), 6, 1)]
        while stack:
            x, y, angle, length, depth, ci = stack.pop()
            if depth == 0 or length < 4: continue
            rgb = hex_to_rgb(colors[ci % len(colors)])
            ex = int(x + length * math.cos(angle))
            ey = int(y + length * math.sin(angle))
            draw.line([(x,y),(ex,ey)], fill=rgb, width=max(1,depth//2))
            stack.append((ex, ey, angle+rng.uniform(0.2,0.6), length*0.75, depth-1, ci+1))
            if rng.random() > 0.4:
                stack.append((ex, ey, angle-rng.uniform(0.2,0.6), length*0.65, depth-1, ci+2))

def generate_voronoi(draw, width, height, colors, rng):
    n = rng.randint(20, 50)
    pts = [(rng.randint(0,width), rng.randint(0,height)) for _ in range(n)]
    step = 4
    for y in range(0, height, step):
        for x in range(0, width, step):
            nearest = min(range(n), key=lambda i: (pts[i][0]-x)**2+(pts[i][1]-y)**2)
            rgb = hex_to_rgb(colors[nearest % len(colors)])
            draw.rectangle([x, y, x+step, y+step], fill=rgb)
    for (px, py) in pts:
        draw.ellipse([px-3, py-3, px+3, py+3], fill=hex_to_rgb(colors[0]))

def generate_kaleidoscope(draw, width, height, colors, rng):
    cx, cy = width//2, height//2
    segments = rng.randint(6, 12)
    for i in range(rng.randint(30, 60)):
        rgb = hex_to_rgb(colors[i % len(colors)])
        r1 = rng.randint(10, min(cx,cy))
        r2 = rng.randint(r1, min(cx,cy))
        a1 = rng.uniform(0, 2*math.pi/segments)
        a2 = a1 + rng.uniform(0.05, 0.3)
        for s in range(segments):
            base = s * 2 * math.pi / segments
            pts = [
                (cx + r1*math.cos(base+a1), cy + r1*math.sin(base+a1)),
                (cx + r2*math.cos(base+a1), cy + r2*math.sin(base+a1)),
                (cx + r2*math.cos(base+a2), cy + r2*math.sin(base+a2)),
                (cx + r1*math.cos(base+a2), cy + r1*math.sin(base+a2)),
            ]
            draw.polygon(pts, fill=rgb)

def generate_triangular_mesh(draw, width, height, colors, rng):
    cols = rng.randint(8, 16)
    rows = rng.randint(6, 12)
    cw, rh = width//cols, height//rows
    for row in range(rows+1):
        for col in range(cols+1):
            x, y = col*cw, row*rh
            jx = rng.randint(-cw//4, cw//4)
            jy = rng.randint(-rh//4, rh//4)
            r1 = hex_to_rgb(colors[(row+col) % len(colors)])
            r2 = hex_to_rgb(colors[(row+col+1) % len(colors)])
            draw.polygon([(x+jx,y+jy),(x+cw,y),(x,y+rh)], fill=r1)
            draw.polygon([(x+cw,y),(x+cw,y+rh),(x,y+rh)], fill=r2)

def generate_pinwheel(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cx, cy = width//2, height//2
    blades = rng.randint(4, 8)
    max_r = min(cx, cy)
    for b in range(blades):
        rgb = hex_to_rgb(colors[(b+1) % len(colors)])
        base_angle = b * 2*math.pi/blades
        twist = rng.uniform(0.3, 0.7)
        pts = [(cx, cy)]
        for i in range(30):
            t = i/29
            r = t * max_r
            a = base_angle + t*twist*math.pi
            pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
        draw.polygon(pts, fill=rgb)

def generate_prism(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_prisms = rng.randint(5, 12)
    for i in range(num_prisms):
        rgb = hex_to_rgb(colors[(i+1) % len(colors)])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        h = rng.randint(40, 120)
        w = rng.randint(20, 60)
        angle = rng.uniform(0, math.pi)
        pts = [
            (cx, cy-h),
            (cx+int(w*math.cos(angle)), cy+int(w*math.sin(angle))),
            (cx-int(w*math.cos(angle)), cy+int(w*math.sin(angle))),
        ]
        draw.polygon(pts, fill=rgb)
        side = hex_to_rgb(colors[(i+2) % len(colors)])
        draw.polygon([(cx,cy-h),(cx+int(w*math.cos(angle)),cy+int(w*math.sin(angle))),(cx+int(w*math.cos(angle))+5,cy+int(w*math.sin(angle))+5),(cx+5,cy-h+5)], fill=side)

def generate_hypnotic(draw, width, height, colors, rng):
    cx, cy = width//2, height//2
    rings = rng.randint(15, 30)
    max_r = int(math.sqrt(cx**2+cy**2))
    for i in range(rings):
        r = int(max_r * i / rings)
        rgb = hex_to_rgb(colors[i % len(colors)])
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rgb, width=max(1, (rings-i)//5))
    spokes = rng.randint(8, 16)
    for s in range(spokes):
        angle = s * 2*math.pi/spokes
        rgb = hex_to_rgb(colors[(s+1) % len(colors)])
        draw.line([(cx,cy),(int(cx+max_r*math.cos(angle)),int(cy+max_r*math.sin(angle)))], fill=rgb, width=1)

def generate_plasma(draw, width, height, colors, rng):
    step = 6
    f1 = rng.uniform(0.01, 0.03)
    f2 = rng.uniform(0.01, 0.03)
    f3 = rng.uniform(0.005, 0.015)
    for y in range(0, height, step):
        for x in range(0, width, step):
            v = math.sin(x*f1) + math.sin(y*f2) + math.sin((x+y)*f3)
            v = (v + 3) / 6
            idx = int(v * (len(colors)-1))
            rgb = hex_to_rgb(colors[idx % len(colors)])
            draw.rectangle([x, y, x+step, y+step], fill=rgb)

def generate_interference(draw, width, height, colors, rng):
    step = 5
    cx1, cy1 = rng.randint(0,width), rng.randint(0,height)
    cx2, cy2 = rng.randint(0,width), rng.randint(0,height)
    freq = rng.uniform(0.05, 0.15)
    for y in range(0, height, step):
        for x in range(0, width, step):
            d1 = math.sqrt((x-cx1)**2+(y-cy1)**2)
            d2 = math.sqrt((x-cx2)**2+(y-cy2)**2)
            v = (math.sin(d1*freq) + math.sin(d2*freq) + 2) / 4
            idx = int(v * (len(colors)-1))
            draw.rectangle([x,y,x+step,y+step], fill=hex_to_rgb(colors[idx % len(colors)]))

def generate_turbulence(draw, width, height, colors, rng):
    step = 5
    octaves = 4
    for y in range(0, height, step):
        for x in range(0, width, step):
            v = 0
            for o in range(octaves):
                f = 0.005 * (2**o)
                v += math.sin(x*f + rng.uniform(-0.1,0.1)) * math.cos(y*f) / (2**o)
            v = (v + 2) / 4
            idx = int(max(0, min(len(colors)-1, v*(len(colors)-1))))
            draw.rectangle([x,y,x+step,y+step], fill=hex_to_rgb(colors[idx]))

def generate_ink_blot(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cx, cy = width//2, height//2
    for i in range(rng.randint(5, 12)):
        rgb = hex_to_rgb(colors[(i+1) % len(colors)])
        pts = []
        n = rng.randint(8, 16)
        base_r = rng.randint(30, 120)
        for j in range(n):
            angle = 2*math.pi*j/n
            r = base_r + rng.randint(-base_r//3, base_r//3)
            ox = rng.randint(-width//4, width//4)
            oy = rng.randint(-height//4, height//4)
            pts.append((cx+ox+r*math.cos(angle), cy+oy+r*math.sin(angle)))
        draw.polygon(pts, fill=rgb)

def generate_watercolor(draw, width, height, colors, rng):
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[-1])
    for y in range(height):
        t = y/height
        base = tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))
        draw.line([(0,y),(width,y)], fill=base)
    for _ in range(rng.randint(8, 18)):
        rgb = hex_to_rgb(colors[rng.randint(0, len(colors)-1)])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        for _ in range(rng.randint(5, 12)):
            r = rng.randint(20, 80)
            ox, oy = rng.randint(-30,30), rng.randint(-30,30)
            af = rng.uniform(0.2, 0.5)
            blended = tuple(int(rgb[c]*af) for c in range(3))
            draw.ellipse([cx+ox-r, cy+oy-r, cx+ox+r, cy+oy+r], fill=blended)

def generate_pointillism(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(800, 2000)):
        rgb = hex_to_rgb(colors[rng.randint(0, len(colors)-1)])
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        r = rng.randint(2, 8)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=rgb)

def generate_maze(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cell = rng.randint(25, 50)
    wall = hex_to_rgb(colors[1 % len(colors)])
    cols_n = width // cell
    rows_n = height // cell
    visited = [[False]*cols_n for _ in range(rows_n)]
    walls_h = [[True]*cols_n for _ in range(rows_n+1)]
    walls_v = [[True]*(cols_n+1) for _ in range(rows_n)]
    # Iterative DFS maze carving
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        r, c = stack[-1]
        dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        rng.rng.shuffle(dirs)
        moved = False
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows_n and 0<=nc<cols_n and not visited[nr][nc]:
                if dr==0: walls_v[r][max(c,nc)] = False
                else: walls_h[max(r,nr)][c] = False
                visited[nr][nc] = True
                stack.append((nr, nc))
                moved = True
                break
        if not moved:
            stack.pop()
    for r in range(rows_n):
        for c in range(cols_n):
            x, y = c*cell, r*cell
            if walls_h[r][c]: draw.line([(x,y),(x+cell,y)], fill=wall, width=2)
            if walls_v[r][c]: draw.line([(x,y),(x,y+cell)], fill=wall, width=2)
    draw.line([(0,rows_n*cell),(cols_n*cell,rows_n*cell)], fill=wall, width=2)
    draw.line([(cols_n*cell,0),(cols_n*cell,rows_n*cell)], fill=wall, width=2)

def generate_constellation(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    stars = [(rng.randint(0,width), rng.randint(0,height)) for _ in range(rng.randint(40, 80))]
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    for i, (x1,y1) in enumerate(stars):
        for j, (x2,y2) in enumerate(stars):
            if i < j and math.sqrt((x2-x1)**2+(y2-y1)**2) < width//5:
                draw.line([(x1,y1),(x2,y2)], fill=rgb1, width=1)
    for (sx, sy) in stars:
        r = rng.randint(2, 5)
        draw.ellipse([sx-r, sy-r, sx+r, sy+r], fill=rgb2)

def generate_lace(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    rgb = hex_to_rgb(colors[1 % len(colors)])
    spacing = rng.randint(30, 60)
    for y in range(0, height, spacing):
        for x in range(0, width, spacing):
            r = spacing // 2
            draw.ellipse([x, y, x+r, y+r], outline=rgb, width=1)
            draw.ellipse([x+r//2, y+r//2, x+r+r//2, y+r+r//2], outline=rgb, width=1)
            draw.line([(x,y),(x+spacing,y+spacing)], fill=rgb, width=1)
            draw.line([(x+spacing,y),(x,y+spacing)], fill=rgb, width=1)

def generate_glitch(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(20, 50)):
        rgb = hex_to_rgb(colors[rng.randint(1, len(colors)-1)])
        y = rng.randint(0, height)
        h = rng.randint(2, 20)
        shift = rng.randint(-80, 80)
        x1 = rng.randint(0, width//2)
        x2 = rng.randint(width//2, width)
        draw.rectangle([x1+shift, y, x2+shift, y+h], fill=rgb)
    for _ in range(rng.randint(5, 15)):
        rgb = hex_to_rgb(colors[rng.randint(0, len(colors)-1)])
        x = rng.randint(0, width)
        draw.line([(x,0),(x+rng.randint(-30,30),height)], fill=rgb, width=rng.randint(1,3))

def generate_stained_glass(draw, width, height, colors, rng):
    n = rng.randint(30, 60)
    pts = [(rng.randint(0, width), rng.randint(0, height)) for _ in range(n)]
    pts += [(0,0),(width,0),(0,height),(width,height)]
    step = 5
    for y in range(0, height, step):
        for x in range(0, width, step):
            nearest = min(range(len(pts)), key=lambda i: (pts[i][0]-x)**2+(pts[i][1]-y)**2)
            rgb = hex_to_rgb(colors[nearest % len(colors)])
            draw.rectangle([x, y, x+step, y+step], fill=rgb)
    for i, (px, py) in enumerate(pts[:n]):
        for j, (qx, qy) in enumerate(pts[:n]):
            if i < j and math.sqrt((qx-px)**2+(qy-py)**2) < width//5:
                draw.line([(px,py),(qx,qy)], fill=(0,0,0), width=2)

def generate_topsoil(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(200, 500)):
        rgb = hex_to_rgb(colors[rng.randint(0, len(colors)-1)])
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        w = rng.randint(4, 20)
        h = rng.randint(2, 8)
        angle = rng.uniform(0, math.pi)
        cx2, cy2 = x + int(w*math.cos(angle)), y + int(w*math.sin(angle))
        draw.line([(x,y),(cx2,cy2)], fill=rgb, width=h)

def generate_fish_net(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    spacing = rng.randint(25, 55)
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    wave_amp = rng.randint(5, 15)
    wave_freq = rng.uniform(0.02, 0.06)
    for i, start in enumerate(range(-height, width+height, spacing)):
        for x in range(width):
            y = start + x + int(wave_amp * math.sin(x * wave_freq))
            if 0 <= y < height:
                draw.point((x, y), fill=rgb1)
    for i, start in enumerate(range(width+height, -height, -spacing)):
        for x in range(width):
            y = start - x + int(wave_amp * math.sin(x * wave_freq))
            if 0 <= y < height:
                draw.point((x, y), fill=rgb2)

def generate_honeycomb_flow(draw, width, height, colors, rng):
    size = rng.randint(25, 55)
    hex_w = size * 2
    hex_h = math.sqrt(3) * size
    flow_freq = rng.uniform(0.003, 0.008)
    col_idx = 0
    x = 0
    while x < width + hex_w:
        row_idx = 0
        y_offset = (hex_h / 2) if (col_idx % 2) else 0
        y = -hex_h + y_offset
        while y < height + hex_h:
            cx2, cy2 = x, y
            flow = math.sin(cx2 * flow_freq + cy2 * flow_freq * 0.7)
            ci = int((flow + 1) / 2 * (len(colors) - 1))
            rgb = hex_to_rgb(colors[ci % len(colors)])
            pts = [(cx2 + size*math.cos(math.radians(60*i)), cy2 + size*math.sin(math.radians(60*i))) for i in range(6)]
            draw.polygon(pts, fill=rgb, outline=(0,0,0))
            y += hex_h
            row_idx += 1
        x += hex_w * 0.75
        col_idx += 1

def generate_pixel_sort(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    stripe_h = rng.randint(3, 10)
    for y in range(0, height, stripe_h):
        num_segs = rng.randint(3, 8)
        xs = sorted([rng.randint(0, width) for _ in range(num_segs)])
        xs = [0] + xs + [width]
        for i in range(len(xs)-1):
            rgb = hex_to_rgb(colors[i % len(colors)])
            shift = rng.randint(-30, 30)
            x1, x2 = xs[i]+shift, xs[i+1]+shift
            draw.rectangle([x1, y, x2, y+stripe_h], fill=rgb)

def generate_sand_ripple(draw, width, height, colors, rng):
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1 % len(colors)])
    for y in range(height):
        t = y / height
        draw.line([(0,y),(width,y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    rgb = hex_to_rgb(colors[2 % len(colors)])
    num_ripples = rng.randint(8, 18)
    for i in range(num_ripples):
        base_y = int(height * (i+1) / (num_ripples+1))
        f1 = rng.uniform(0.008, 0.02)
        f2 = rng.uniform(0.003, 0.008)
        amp = rng.randint(3, 12)
        pts = []
        for x in range(width):
            y = base_y + int(math.sin(x*f1)*amp + math.sin(x*f2+1)*amp*0.5)
            pts.append((x, y))
        for j in range(len(pts)-1):
            draw.line([pts[j], pts[j+1]], fill=rgb, width=1)

def generate_tree_rings(draw, width, height, colors, rng):
    cx, cy = width//2 + rng.randint(-width//6, width//6), height//2 + rng.randint(-height//6, height//6)
    max_r = int(math.sqrt((max(cx, width-cx))**2 + (max(cy, height-cy))**2))
    num_rings = rng.randint(20, 45)
    gap = max_r // num_rings
    for i in range(num_rings, 0, -1):
        r = i * gap
        rgb = hex_to_rgb(colors[i % len(colors)])
        wobble = rng.randint(2, 8)
        pts = []
        steps = max(60, r // 2)
        for s in range(steps+1):
            angle = 2*math.pi*s/steps
            wr = r + int(wobble * math.sin(angle * rng.randint(3,7)))
            pts.append((cx + wr*math.cos(angle), cy + wr*math.sin(angle)))
        if len(pts) >= 3:
            draw.polygon(pts, fill=rgb)

def generate_lightning_field(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for b in range(rng.randint(8, 18)):
        rgb = hex_to_rgb(colors[(b % (len(colors)-1))+1])
        x = rng.randint(0, width)
        y = rng.randint(0, height//3)
        stack = [(x, y, rng.uniform(math.pi*0.3, math.pi*0.7), rng.randint(30, 80), 4)]
        while stack:
            sx, sy, angle, length, depth = stack.pop()
            if depth == 0 or length < 5: continue
            ex = int(sx + length * math.cos(angle))
            ey = int(sy + length * math.sin(angle))
            draw.line([(sx,sy),(ex,ey)], fill=rgb, width=max(1, depth-1))
            stack.append((ex, ey, angle+rng.uniform(0.2,0.6), length*0.7, depth-1))
            if rng.random() > 0.45:
                stack.append((ex, ey, angle-rng.uniform(0.2,0.6), length*0.6, depth-1))

def generate_soap_bubble(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for i in range(rng.randint(15, 35)):
        cx2 = rng.randint(0, width)
        cy2 = rng.randint(0, height)
        r = rng.randint(20, 100)
        rgb = hex_to_rgb(colors[(i+1) % len(colors)])
        for ring in range(3):
            rr = r - ring*2
            if rr > 0:
                draw.ellipse([cx2-rr, cy2-rr, cx2+rr, cy2+rr], outline=rgb, width=1)
        hr = max(2, r//5)
        hx = cx2 - r//3
        hy = cy2 - r//3
        draw.ellipse([hx-hr, hy-hr//2, hx+hr, hy+hr//2], fill=hex_to_rgb(colors[-1]))

def generate_celtic_knot(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    grid = rng.randint(60, 100)
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    for gy in range(0, height, grid):
        for gx in range(0, width, grid):
            cx2, cy2 = gx + grid//2, gy + grid//2
            r = grid // 2 - 4
            draw.ellipse([cx2-r, cy2-r, cx2+r, cy2+r], outline=rgb1, width=3)
            inner = r - 8
            if inner > 4:
                draw.ellipse([cx2-inner, cy2-inner, cx2+inner, cy2+inner], outline=rgb2, width=2)
            draw.line([(gx, cy2),(gx+grid, cy2)], fill=rgb1, width=2)
            draw.line([(cx2, gy),(cx2, gy+grid)], fill=rgb2, width=2)

def generate_meteor_shower(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    for _ in range(rng.randint(30, 70)):
        rgb = hex_to_rgb(colors[rng.randint(1, len(colors)-1)])
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        length = rng.randint(20, 80)
        angle = rng.uniform(math.pi*0.55, math.pi*0.75)
        ex = int(x + length * math.cos(angle))
        ey = int(y + length * math.sin(angle))
        draw.line([(x,y),(ex,ey)], fill=rgb, width=rng.randint(1,2))
        r = rng.randint(1, 3)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=rgb)

def generate_lenticular(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    num_bands = rng.randint(6, 14)
    band_h = height // num_bands
    for i in range(num_bands):
        rgb = hex_to_rgb(colors[(i+1) % len(colors)])
        y = i * band_h
        freq = rng.uniform(0.005, 0.015)
        amp = rng.randint(band_h//4, band_h//2)
        pts_top, pts_bot = [], []
        for x in range(width):
            mid = y + band_h//2 + int(math.sin(x*freq)*amp)
            pts_top.append((x, mid - band_h//3))
            pts_bot.append((x, mid + band_h//3))
        draw.polygon(pts_top + list(reversed(pts_bot)), fill=rgb)

def generate_brush_grid(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cell = rng.randint(40, 80)
    for gy in range(0, height, cell):
        for gx in range(0, width, cell):
            rgb = hex_to_rgb(colors[rng.randint(0, len(colors)-1)])
            num_strokes = rng.randint(3, 8)
            for _ in range(num_strokes):
                x1 = gx + rng.randint(0, cell)
                y1 = gy + rng.randint(0, cell)
                x2 = gx + rng.randint(0, cell)
                y2 = gy + rng.randint(0, cell)
                draw.line([(x1,y1),(x2,y2)], fill=rgb, width=rng.randint(1,4))

def generate_neon_grid(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    spacing = rng.randint(40, 80)
    perspective = rng.uniform(0.3, 0.7)
    horizon = int(height * perspective)
    vp_x = width // 2
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    for x in range(0, width+spacing, spacing):
        draw.line([(x, height),(vp_x + int((x-vp_x)*0.1), horizon)], fill=rgb1, width=1)
    num_h = rng.randint(6, 14)
    for i in range(num_h):
        t = i / num_h
        y = int(horizon + (height - horizon) * t)
        fade = int(200 * t)
        fc = tuple(min(255, int(v * fade / 200)) for v in rgb2)
        draw.line([(0, y),(width, y)], fill=fc, width=1)

def generate_patchwork(draw, width, height, colors, rng):
    min_size = rng.randint(40, 80)
    regions = [(0, 0, width, height)]
    for _ in range(rng.randint(20, 40)):
        if not regions: break
        idx = rng.randint(0, len(regions)-1)
        x1, y1, x2, y2 = regions.pop(idx)
        if x2-x1 < min_size*2 and y2-y1 < min_size*2: continue
        if (x2-x1) > (y2-y1):
            split = rng.randint(x1+min_size, x2-min_size)
            regions += [(x1,y1,split,y2),(split,y1,x2,y2)]
        else:
            split = rng.randint(y1+min_size, y2-min_size)
            regions += [(x1,y1,x2,split),(x1,split,x2,y2)]
    for i, (x1,y1,x2,y2) in enumerate(regions):
        rgb = hex_to_rgb(colors[i % len(colors)])
        draw.rectangle([x1+1,y1+1,x2-1,y2-1], fill=rgb)
        draw.rectangle([x1,y1,x2,y2], outline=hex_to_rgb(colors[0]), width=2)

def generate_sunburst(draw, width, height, colors, rng):
    cx, cy = width//2, height//2
    max_r = int(math.sqrt(cx**2 + cy**2))
    num_rays = rng.randint(12, 30)
    ray_w = rng.uniform(0.05, 0.15)
    for i in range(num_rays):
        rgb = hex_to_rgb(colors[(i+1) % len(colors)])
        base_angle = i * 2*math.pi / num_rays
        pts = [
            (cx, cy),
            (cx + max_r*math.cos(base_angle - ray_w), cy + max_r*math.sin(base_angle - ray_w)),
            (cx + max_r*math.cos(base_angle + ray_w), cy + max_r*math.sin(base_angle + ray_w)),
        ]
        draw.polygon(pts, fill=rgb)
    for ri in range(5, 0, -1):
        r = int(max_r * ri / 6)
        rgb = hex_to_rgb(colors[ri % len(colors)])
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rgb, width=2)

def generate_droplets(draw, width, height, colors, rng):
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1 % len(colors)])
    for y in range(height):
        t = y/height
        draw.line([(0,y),(width,y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    for i in range(rng.randint(20, 50)):
        rgb = hex_to_rgb(colors[(i % (len(colors)-1))+1])
        cx2 = rng.randint(0, width)
        cy2 = rng.randint(0, height)
        r = rng.randint(8, 30)
        tail = rng.randint(r, r*3)
        draw.ellipse([cx2-r, cy2-r, cx2+r, cy2+r], fill=rgb)
        pts = [(cx2-r//2, cy2+r//2), (cx2, cy2+r+tail), (cx2+r//2, cy2+r//2)]
        draw.polygon(pts, fill=rgb)
        gap = rng.randint(15, 40)
        for ri in range(1, 4):
            rr = ri * gap
            fade = int(180 * (1 - ri/4))
            fc = tuple(int(v*fade//180) for v in rgb)
            draw.ellipse([cx2-rr, cy2-rr, cx2+rr, cy2+rr], outline=fc, width=1)

def generate_wire_frame(draw, width, height, colors, rng):
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)
    cols_n = rng.randint(6, 12)
    rows_n = rng.randint(4, 8)
    cw, rh = width // cols_n, height // rows_n
    pts = {}
    for r in range(rows_n+1):
        for c in range(cols_n+1):
            jx = rng.randint(-cw//4, cw//4)
            jy = rng.randint(-rh//4, rh//4)
            pts[(r,c)] = (c*cw + jx, r*rh + jy)
    rgb1 = hex_to_rgb(colors[1 % len(colors)])
    rgb2 = hex_to_rgb(colors[2 % len(colors)])
    for r in range(rows_n):
        for c in range(cols_n):
            p1, p2 = pts[(r,c)], pts[(r,c+1)]
            p3, p4 = pts[(r+1,c)], pts[(r+1,c+1)]
            ci = (r+c) % len(colors)
            draw.polygon([p1,p2,p4,p3], fill=hex_to_rgb(colors[ci]), outline=rgb1)
            draw.line([p1,p4], fill=rgb2, width=1)

def generate_cellular(draw, width, height, colors, rng):
    """Generate cellular pattern"""
    cell_size = rng.randint(20, 50)
    
    for y in range(0, height, cell_size):
        for x in range(0, width, cell_size):
            color = colors[rng.randint(0, len(colors) - 1)]
            rgb = hex_to_rgb(color)
            draw.rectangle([x, y, x + cell_size, y + cell_size], fill=rgb, outline=(100, 100, 100))

def generate_pattern(width, height, pattern_type, palette_index, seed, inverted=False):
    """
    Generate a wallpaper pattern
    
    Args:
        width: Image width
        height: Image height
        pattern_type: Pattern type (from PatternType enum)
        palette_index: Index of color palette
        seed: Random seed for reproducibility
        inverted: Whether to invert colors
    
    Returns:
        PIL Image object
    """
    # Initialize seeded random
    rng = SeededRandom(seed)
    
    # Get colors
    colors = get_palette_colors(palette_index, inverted)
    
    # Create image with background color
    bg_color = hex_to_rgb(colors[0])
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Generate pattern based on type
    if pattern_type == PatternType.HILLS:
        generate_hills(draw, width, height, colors, rng)
    elif pattern_type == PatternType.WAVES:
        generate_waves(draw, width, height, colors, rng)
    elif pattern_type == PatternType.DUNES:
        generate_dunes(draw, width, height, colors, rng)
    elif pattern_type == PatternType.MOUNTAINS:
        generate_mountains(draw, width, height, colors, rng)
    elif pattern_type == PatternType.ARCS:
        generate_arcs(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SCRIBBLE:
        generate_scribble(draw, width, height, colors, rng)
    elif pattern_type == PatternType.GEOMETRIC:
        generate_geometric(draw, width, height, colors, rng)
    elif pattern_type == PatternType.NOISE:
        generate_noise(draw, width, height, colors, rng)
    elif pattern_type == PatternType.GRADIENT:
        generate_gradient(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CELLULAR:
        generate_cellular(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SPIRAL:
        generate_spiral(draw, width, height, colors, rng)
    elif pattern_type == PatternType.HEXAGON:
        generate_hexagon(draw, width, height, colors, rng)
    elif pattern_type == PatternType.AURORA:
        generate_aurora(draw, width, height, colors, rng)
    elif pattern_type == PatternType.MANDALA:
        generate_mandala(draw, width, height, colors, rng)
    elif pattern_type == PatternType.VORTEX:
        generate_vortex(draw, width, height, colors, rng)
    elif pattern_type == PatternType.LIGHTNING:
        generate_lightning(draw, width, height, colors, rng)
    elif pattern_type == PatternType.BUBBLES:
        generate_bubbles(draw, width, height, colors, rng)
    elif pattern_type == PatternType.DIAMOND:
        generate_diamond(draw, width, height, colors, rng)
    elif pattern_type == PatternType.LAVA:
        generate_lava(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CIRCUIT:
        generate_circuit(draw, width, height, colors, rng)
    elif pattern_type == PatternType.GALAXY:
        generate_galaxy(draw, width, height, colors, rng)
    elif pattern_type == PatternType.RIPPLE:
        generate_ripple(draw, width, height, colors, rng)
    elif pattern_type == PatternType.MOSAIC:
        generate_mosaic(draw, width, height, colors, rng)
    elif pattern_type == PatternType.TERRACES:
        generate_terraces(draw, width, height, colors, rng)
    elif pattern_type == PatternType.TIDES:
        generate_tides(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SANDSTORM:
        generate_sandstorm(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PEAKS:
        generate_peaks(draw, width, height, colors, rng)
    elif pattern_type == PatternType.RINGS:
        generate_rings(draw, width, height, colors, rng)
    elif pattern_type == PatternType.BRUSHSTROKE:
        generate_brushstroke(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CONTOUR:
        generate_contour(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PLAID:
        generate_plaid(draw, width, height, colors, rng)
    elif pattern_type == PatternType.STARBURST:
        generate_starburst(draw, width, height, colors, rng)
    elif pattern_type == PatternType.WEAVE:
        generate_weave(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PEBBLES:
        generate_pebbles(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CHEVRON:
        generate_chevron(draw, width, height, colors, rng)
    elif pattern_type == PatternType.FRACTAL:
        generate_fractal(draw, width, height, colors, rng)
    elif pattern_type == PatternType.COBWEB:
        generate_cobweb(draw, width, height, colors, rng)
    elif pattern_type == PatternType.ORIGAMI:
        generate_origami(draw, width, height, colors, rng)
    elif pattern_type == PatternType.NOODLES:
        generate_noodles(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CRYSTALS:
        generate_crystals(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SMOKE:
        generate_smoke(draw, width, height, colors, rng)
    elif pattern_type == PatternType.LABYRINTH:
        generate_labyrinth(draw, width, height, colors, rng)
    elif pattern_type == PatternType.POLKA:
        generate_polka(draw, width, height, colors, rng)
    elif pattern_type == PatternType.FEATHERS:
        generate_feathers(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SCALES:
        generate_scales(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CROSSHATCH:
        generate_crosshatch(draw, width, height, colors, rng)
    elif pattern_type == PatternType.DNA:
        generate_dna(draw, width, height, colors, rng)
    elif pattern_type == PatternType.BINARY_RAIN:
        generate_binary_rain(draw, width, height, colors, rng)
    elif pattern_type == PatternType.RADAR:
        generate_radar(draw, width, height, colors, rng)
    elif pattern_type == PatternType.TOPOGRAPHIC:
        generate_topographic(draw, width, height, colors, rng)
    elif pattern_type == PatternType.WAVEFORM:
        generate_waveform(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SATELLITE:
        generate_satellite(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SONAR:
        generate_sonar(draw, width, height, colors, rng)
    elif pattern_type == PatternType.DATASTREAM:
        generate_datastream(draw, width, height, colors, rng)
    elif pattern_type == PatternType.FIBER_OPTIC:
        generate_fiber_optic(draw, width, height, colors, rng)
    elif pattern_type == PatternType.NEURAL:
        generate_neural(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CORAL:
        generate_coral(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SNOWFLAKES:
        generate_snowflakes(draw, width, height, colors, rng)
    elif pattern_type == PatternType.RAINDROPS:
        generate_raindrops(draw, width, height, colors, rng)
    elif pattern_type == PatternType.VINES:
        generate_vines(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CLOUDS:
        generate_clouds(draw, width, height, colors, rng)
    elif pattern_type == PatternType.BAMBOO:
        generate_bamboo(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CRACKS:
        generate_cracks(draw, width, height, colors, rng)
    elif pattern_type == PatternType.ROOTS:
        generate_roots(draw, width, height, colors, rng)
    elif pattern_type == PatternType.VORONOI:
        generate_voronoi(draw, width, height, colors, rng)
    elif pattern_type == PatternType.KALEIDOSCOPE:
        generate_kaleidoscope(draw, width, height, colors, rng)
    elif pattern_type == PatternType.TRIANGULAR_MESH:
        generate_triangular_mesh(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PINWHEEL:
        generate_pinwheel(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PRISM:
        generate_prism(draw, width, height, colors, rng)
    elif pattern_type == PatternType.HYPNOTIC:
        generate_hypnotic(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PLASMA:
        generate_plasma(draw, width, height, colors, rng)
    elif pattern_type == PatternType.INTERFERENCE:
        generate_interference(draw, width, height, colors, rng)
    elif pattern_type == PatternType.TURBULENCE:
        generate_turbulence(draw, width, height, colors, rng)
    elif pattern_type == PatternType.INK_BLOT:
        generate_ink_blot(draw, width, height, colors, rng)
    elif pattern_type == PatternType.WATERCOLOR:
        generate_watercolor(draw, width, height, colors, rng)
    elif pattern_type == PatternType.POINTILLISM:
        generate_pointillism(draw, width, height, colors, rng)
    elif pattern_type == PatternType.MAZE:
        generate_maze(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CONSTELLATION:
        generate_constellation(draw, width, height, colors, rng)
    elif pattern_type == PatternType.LACE:
        generate_lace(draw, width, height, colors, rng)
    elif pattern_type == PatternType.GLITCH:
        generate_glitch(draw, width, height, colors, rng)
    elif pattern_type == PatternType.STAINED_GLASS:
        generate_stained_glass(draw, width, height, colors, rng)
    elif pattern_type == PatternType.TOPSOIL:
        generate_topsoil(draw, width, height, colors, rng)
    elif pattern_type == PatternType.FISH_NET:
        generate_fish_net(draw, width, height, colors, rng)
    elif pattern_type == PatternType.HONEYCOMB_FLOW:
        generate_honeycomb_flow(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PIXEL_SORT:
        generate_pixel_sort(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SAND_RIPPLE:
        generate_sand_ripple(draw, width, height, colors, rng)
    elif pattern_type == PatternType.TREE_RINGS:
        generate_tree_rings(draw, width, height, colors, rng)
    elif pattern_type == PatternType.LIGHTNING_FIELD:
        generate_lightning_field(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SOAP_BUBBLE:
        generate_soap_bubble(draw, width, height, colors, rng)
    elif pattern_type == PatternType.CELTIC_KNOT:
        generate_celtic_knot(draw, width, height, colors, rng)
    elif pattern_type == PatternType.METEOR_SHOWER:
        generate_meteor_shower(draw, width, height, colors, rng)
    elif pattern_type == PatternType.LENTICULAR:
        generate_lenticular(draw, width, height, colors, rng)
    elif pattern_type == PatternType.BRUSH_GRID:
        generate_brush_grid(draw, width, height, colors, rng)
    elif pattern_type == PatternType.NEON_GRID:
        generate_neon_grid(draw, width, height, colors, rng)
    elif pattern_type == PatternType.PATCHWORK:
        generate_patchwork(draw, width, height, colors, rng)
    elif pattern_type == PatternType.SUNBURST:
        generate_sunburst(draw, width, height, colors, rng)
    elif pattern_type == PatternType.DROPLETS:
        generate_droplets(draw, width, height, colors, rng)
    elif pattern_type == PatternType.WIRE_FRAME:
        generate_wire_frame(draw, width, height, colors, rng)

    return image

def blend_patterns(width, height, pattern_type_1, pattern_type_2, palette_index, seed, inverted=False, blend_ratio=0.5):
    """Blend two patterns together using alpha blending"""
    img1 = generate_pattern(width, height, pattern_type_1, palette_index, seed, inverted)
    img2 = generate_pattern(width, height, pattern_type_2, palette_index, seed, inverted)
    return Image.blend(img1, img2, alpha=blend_ratio)

def export_to_bytes(image):
    """Export PIL image to PNG bytes"""
    buffer = BytesIO()
    image.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)
    return buffer.getvalue()
