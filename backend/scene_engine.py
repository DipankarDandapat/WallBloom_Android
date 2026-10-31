"""
Scene generation engine for WallBloom
Generates themed scene wallpapers with intelligent color combinations
"""

import random
import math
from PIL import Image, ImageDraw
from enum import Enum
from io import BytesIO

from premium_engine import PREMIUM_SCENES, PREMIUM_SCENE_DEFINITIONS


class SceneTheme(str, Enum):
    LANDMARKS = "landmarks"
    WORLD_SCENES = "world_scenes"
    CELESTIAL = "celestial"
    NATURE_ELEMENTS = "nature_elements"
    URBAN = "urban"
    UNDERWATER = "underwater"
    FANTASY = "fantasy"
    MINIMAL = "minimal"


class SceneType(str, Enum):
    # Landmarks
    EIFFEL_TOWER = "eiffel_tower"
    STATUE_OF_LIBERTY = "statue_of_liberty"
    BIG_BEN = "big_ben"
    TAJ_MAHAL = "taj_mahal"
    CHRIST_REDEEMER = "christ_redeemer"
    COLOSSEUM = "colosseum"
    SYDNEY_OPERA_HOUSE = "sydney_opera_house"

    GREAT_WALL = "great_wall"
    BURJ_KHALIFA = "burj_khalifa"
    SAGRADA_FAMILIA = "sagrada_familia"
    STONEHENGE = "stonehenge"
    MACHU_PICCHU = "machu_picchu"
    LEANING_TOWER_PISA = "leaning_tower_pisa"
    ACROPOLIS = "acropolis"
    MOUNT_FUJI = "mount_fuji"

    # World Scenes
    DESERT = "desert"
    BEACH = "beach"
    MOUNTAIN = "mountain"
    VALLEY = "valley"
    CANYON = "canyon"
    PLATEAU = "plateau"
    SAVANNA = "savanna"
    TUNDRA = "tundra"
    GLACIER = "glacier"
    RAINFOREST = "rainforest"
    FJORD = "fjord"
    WETLANDS = "wetlands"
    STEPPE = "steppe"

    # Celestial
    SUNRISE = "sunrise"
    SUNSET = "sunset"
    STARFIELD = "starfield"
    NORTHERN_LIGHTS = "northern_lights"
    SOLAR_ECLIPSE = "solar_eclipse"
    NEBULA = "nebula"
    GALAXY = "galaxy"
    LUNAR_ECLIPSE = "lunar_eclipse"
    COMET = "comet"
    METEOR_SHOWER = "meteor_shower"
    BINARY_STARS = "binary_stars"
    MOONRISE = "moonrise"

    # Nature Elements
    FOREST = "forest"
    JUNGLE = "jungle"
    OCEAN = "ocean"
    WATERFALL = "waterfall"
    VOLCANO = "volcano"
    STORM = "storm"
    MEADOW = "meadow"

    CAVE = "cave"
    HOT_SPRING = "hot_spring"
    CORAL_REEF = "coral_reef"
    DUNES_NIGHT = "dunes_night"
    MANGROVE = "mangrove"

    # Urban
    MINIMALIST_CITY = "minimalist_city"
    NEON_CITY = "neon_city"
    CLASSIC_SKYLINE = "classic_skyline"
    GEOMETRIC_GRID = "geometric_grid"
    MODERN_ART = "modern_art"
    ROOFTOP_GARDEN = "rooftop_garden"
    SUBWAY = "subway"
    NIGHT_MARKET = "night_market"
    INDUSTRIAL = "industrial"
    RAINY_STREET = "rainy_street"

    # Underwater
    DEEP_OCEAN = "deep_ocean"
    SHIPWRECK = "shipwreck"
    KELP_FOREST = "kelp_forest"
    BIOLUMINESCENT = "bioluminescent"
    SUBMARINE = "submarine"
    TIDE_POOL = "tide_pool"

    # Fantasy
    ENCHANTED_FOREST = "enchanted_forest"
    FLOATING_ISLANDS = "floating_islands"
    CRYSTAL_CAVE = "crystal_cave"
    DRAGON_LAIR = "dragon_lair"
    ANCIENT_RUINS = "ancient_ruins"
    AURORA_CASTLE = "aurora_castle"

    # Minimal
    MINIMAL_MOUNTAINS = "minimal_mountains"
    MISTY_FOREST = "misty_forest"
    OCEAN_SUNSET = "ocean_sunset"
    MOONLIT_DUNES = "moonlit_dunes"
    RINGED_PLANET = "ringed_planet"
    AURORA_LAKE = "aurora_lake"
    LONE_TREE = "lone_tree"
    PAPER_HILLS = "paper_hills"
    CITY_DUSK = "city_dusk"


# Scene definitions with default palettes
SCENE_DEFINITIONS = {
    # Landmarks
    SceneType.EIFFEL_TOWER: {
        "name": "Eiffel Tower",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🗼",
        "default_palette": ["#ff6b35", "#f7931e", "#fdb833", "#fff4e6", "#e67e22", "#d35400"]
    },
    SceneType.STATUE_OF_LIBERTY: {
        "name": "Statue of Liberty",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🗽",
        "default_palette": ["#0074d9", "#7fdbca", "#2ecc71", "#f8f9fa", "#3498db", "#27ae60"]
    },
    SceneType.BIG_BEN: {
        "name": "Big Ben",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🇬🇧",
        "default_palette": ["#2c3e50", "#34495e", "#95a5a6", "#ecf0f1", "#7f8c8d", "#bdc3c7"]
    },
    SceneType.TAJ_MAHAL: {
        "name": "Taj Mahal",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🕌",
        "default_palette": ["#fff5e6", "#ffe4b5", "#d2691e", "#8b4513", "#fa8072", "#ff6347"]
    },
    SceneType.CHRIST_REDEEMER: {
        "name": "Christ the Redeemer",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🗿",
        "default_palette": ["#0074d9", "#7fdbca", "#2ecc71", "#f8f9fa", "#3498db", "#27ae60"]
    },
    SceneType.COLOSSEUM: {
        "name": "Colosseum",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🏛️",
        "default_palette": ["#d2691e", "#8b4513", "#a0522d", "#cd853f", "#deb887", "#f5deb3"]
    },
    SceneType.SYDNEY_OPERA_HOUSE: {
        "name": "Sydney Opera House",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🎭",
        "default_palette": ["#0074d9", "#7fdbca", "#2ecc71", "#f8f9fa", "#3498db", "#27ae60"]
    },

    SceneType.GREAT_WALL: {
        "name": "Great Wall",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🏯",
        "default_palette": ["#87ceeb", "#b0c4de", "#8b7355", "#a0896b", "#556b2f", "#6b8e23"]
    },
    SceneType.BURJ_KHALIFA: {
        "name": "Burj Khalifa",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🏙️",
        "default_palette": ["#0a1628", "#1a3a5c", "#2e6da4", "#5ba3d9", "#c8dff0", "#ffffff"]
    },
    SceneType.SAGRADA_FAMILIA: {
        "name": "Sagrada Familia",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "⛪",
        "default_palette": ["#87ceeb", "#d4a96a", "#c49a4a", "#e8d5a3", "#8b6914", "#f5f0e8"]
    },
    SceneType.STONEHENGE: {
        "name": "Stonehenge",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🗿",
        "default_palette": ["#6b7f9e", "#8a9bb5", "#7a7a7a", "#9a9a9a", "#4a5a3a", "#6a7a5a"]
    },
    SceneType.MACHU_PICCHU: {
        "name": "Machu Picchu",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🏔️",
        "default_palette": ["#4a7c59", "#2d5a3d", "#8b7355", "#a0896b", "#87ceeb", "#c8e6f0"]
    },
    SceneType.LEANING_TOWER_PISA: {
        "name": "Tower of Pisa",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🗼",
        "default_palette": ["#87ceeb", "#add8e6", "#f5f0e8", "#e8dcc8", "#4a7c59", "#2d5a3d"]
    },
    SceneType.ACROPOLIS: {
        "name": "Acropolis",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🏛️",
        "default_palette": ["#87ceeb", "#ffd700", "#e8d5a3", "#c8b87a", "#8b7355", "#ffffff"]
    },
    SceneType.MOUNT_FUJI: {
        "name": "Mount Fuji",
        "theme": SceneTheme.LANDMARKS,
        "emoji": "🗻",
        "default_palette": ["#87ceeb", "#b0d4e8", "#6a8fa8", "#4a6a80", "#ffffff", "#e8f4f8"]
    },

    # World Scenes
    SceneType.DESERT: {
        "name": "Desert",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🏜️",
        "default_palette": ["#f4a460", "#d2691e", "#cd853f", "#deb887", "#f5deb3", "#ffe4c4"]
    },
    SceneType.BEACH: {
        "name": "Beach",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🏖️",
        "default_palette": ["#87ceeb", "#add8e6", "#f0f8ff", "#ffffff", "#00bfff", "#1e90ff"]
    },
    SceneType.MOUNTAIN: {
        "name": "Mountain",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "⛰️",
        "default_palette": ["#708090", "#2f4f4f", "#556b2f", "#8fbc8f", "#696969", "#778899"]
    },
    SceneType.VALLEY: {
        "name": "Valley",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🌾",
        "default_palette": ["#90ee90", "#32cd32", "#228b22", "#f0e68c", "#daa520", "#b8860b"]
    },
    SceneType.CANYON: {
        "name": "Canyon",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🏜️",
        "default_palette": ["#cd5c5c", "#dc143c", "#b22222", "#8b0000", "#a0522d", "#8b4513"]
    },
    SceneType.PLATEAU: {
        "name": "Plateau",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🏔️",
        "default_palette": ["#708090", "#2f4f4f", "#556b2f", "#8fbc8f", "#696969", "#778899"]
    },
    SceneType.SAVANNA: {
        "name": "Savanna",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🦁",
        "default_palette": ["#daa520", "#b8860b", "#f0e68c", "#90ee90", "#32cd32", "#228b22"]
    },
    SceneType.TUNDRA: {
        "name": "Tundra",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "❄️",
        "default_palette": ["#e0ffff", "#f0ffff", "#ffffff", "#f5f5f5", "#d3d3d3", "#c0c0c0"]
    },
    SceneType.GLACIER: {
        "name": "Glacier",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🧊",
        "default_palette": ["#a8d8ea", "#c9e8f5", "#e8f6ff", "#ffffff", "#6baed6", "#2171b5"]
    },
    SceneType.RAINFOREST: {
        "name": "Rainforest",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🌧️",
        "default_palette": ["#1a3a1a", "#2d5a2d", "#4a8c4a", "#6ab06a", "#8fce8f", "#b8e6b8"]
    },
    SceneType.FJORD: {
        "name": "Fjord",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🏔️",
        "default_palette": ["#2c4a6e", "#3d6b9e", "#5a8fc0", "#7ab0d8", "#4a6741", "#6a9460"]
    },
    SceneType.WETLANDS: {
        "name": "Wetlands",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🌿",
        "default_palette": ["#4a6741", "#6a9460", "#8ab87e", "#b8d4a0", "#5a8a6a", "#3a6a50"]
    },
    SceneType.STEPPE: {
        "name": "Steppe",
        "theme": SceneTheme.WORLD_SCENES,
        "emoji": "🌾",
        "default_palette": ["#c8a84b", "#a88a30", "#e8c870", "#f0dca0", "#8a7040", "#6a5030"]
    },

    # Celestial
    SceneType.SUNRISE: {
        "name": "Sunrise",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌅",
        "default_palette": ["#ff6b35", "#f7931e", "#fdb833", "#fff4e6", "#e67e22", "#d35400"]
    },
    SceneType.SUNSET: {
        "name": "Sunset",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌇",
        "default_palette": ["#ff4500", "#ff6347", "#ff7f50", "#ff8c00", "#ffa500", "#ffd700"]
    },
    SceneType.STARFIELD: {
        "name": "Starfield",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌌",
        "default_palette": ["#0a0a0a", "#1a1a2e", "#16213e", "#0f3460", "#ffffff", "#f0f0f0"]
    },
    SceneType.NORTHERN_LIGHTS: {
        "name": "Northern Lights",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌌",
        "default_palette": ["#020b18", "#0d4f3c", "#1aff9c", "#b3fff0", "#00ff7f", "#3cb371"]
    },
    SceneType.SOLAR_ECLIPSE: {
        "name": "Solar Eclipse",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌑",
        "default_palette": ["#000000", "#1a1a1a", "#333333", "#4d4d4d", "#ffd700", "#ffaa00"]
    },
    SceneType.NEBULA: {
        "name": "Nebula",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🪐",
        "default_palette": ["#2d0057", "#7700cc", "#cc66ff", "#ff66ff", "#00ccff", "#00ffff"]
    },
    SceneType.GALAXY: {
        "name": "Galaxy",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "✨",
        "default_palette": ["#0b0c2a", "#3d1a78", "#8e44ad", "#e056fd", "#6a1b9a", "#4a148c"]
    },
    SceneType.LUNAR_ECLIPSE: {
        "name": "Lunar Eclipse",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌕",
        "default_palette": ["#0a0a1a", "#1a0a0a", "#8b1a1a", "#cc3300", "#ff6633", "#ffaa66"]
    },
    SceneType.COMET: {
        "name": "Comet",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "☄️",
        "default_palette": ["#020818", "#0a1a3a", "#1a3a6a", "#4a8ac0", "#c8e8ff", "#ffffff"]
    },
    SceneType.METEOR_SHOWER: {
        "name": "Meteor Shower",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌠",
        "default_palette": ["#050510", "#0d0d2a", "#1a1a4a", "#2a2a6a", "#ffcc44", "#ffffff"]
    },
    SceneType.BINARY_STARS: {
        "name": "Binary Stars",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "⭐",
        "default_palette": ["#020510", "#0a0a20", "#ff8844", "#4488ff", "#ffddcc", "#cce0ff"]
    },
    SceneType.MOONRISE: {
        "name": "Moonrise",
        "theme": SceneTheme.CELESTIAL,
        "emoji": "🌙",
        "default_palette": ["#050a18", "#0d1a30", "#1a2a4a", "#2a3a5a", "#e8e0c8", "#f8f4e8"]
    },

    # Nature Elements
    SceneType.FOREST: {
        "name": "Forest",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🌲",
        "default_palette": ["#0b3d2c", "#1e5631", "#40916c", "#d8f3dc", "#228b22", "#006400"]
    },
    SceneType.JUNGLE: {
        "name": "Jungle",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🌴",
        "default_palette": ["#006400", "#228b22", "#32cd32", "#90ee90", "#008080", "#20b2aa"]
    },
    SceneType.OCEAN: {
        "name": "Ocean",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🌊",
        "default_palette": ["#001f3f", "#0074d9", "#7fdbca", "#b3e5fc", "#00ffff", "#e0ffff"]
    },
    SceneType.WATERFALL: {
        "name": "Waterfall",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "💦",
        "default_palette": ["#1a6b8a", "#0d4f6e", "#4a7c59", "#2d5a3d", "#c8e6f0", "#f0f8ff"]
    },
    SceneType.VOLCANO: {
        "name": "Volcano",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🌋",
        "default_palette": ["#8b0000", "#ff4500", "#ffa500", "#ff6347", "#1a0a00", "#4a0000"]
    },
    SceneType.STORM: {
        "name": "Storm",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "⛈️",
        "default_palette": ["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#3498db", "#2980b9"]
    },
    SceneType.MEADOW: {
        "name": "Meadow",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🌿",
        "default_palette": ["#90ee90", "#32cd32", "#228b22", "#f0e68c", "#daa520", "#b8860b"]
    },
    SceneType.CAVE: {
        "name": "Cave",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🕳️",
        "default_palette": ["#0a0a0a", "#1a1210", "#3a2a20", "#5a4030", "#8a6a50", "#c8a878"]
    },
    SceneType.HOT_SPRING: {
        "name": "Hot Spring",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "♨️",
        "default_palette": ["#1a3a4a", "#0d6e8a", "#20b2c8", "#7fe0e8", "#c8f0f4", "#ffffff"]
    },
    SceneType.CORAL_REEF: {
        "name": "Coral Reef",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🪸",
        "default_palette": ["#003a5a", "#005a8a", "#ff6b35", "#ff9f1c", "#2ec4b6", "#cbf3f0"]
    },
    SceneType.DUNES_NIGHT: {
        "name": "Dunes at Night",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🌙",
        "default_palette": ["#050818", "#0d1530", "#1a2a50", "#8a7a5a", "#c8b888", "#e8d8a8"]
    },
    SceneType.MANGROVE: {
        "name": "Mangrove",
        "theme": SceneTheme.NATURE_ELEMENTS,
        "emoji": "🌳",
        "default_palette": ["#2a4a3a", "#3a6a4a", "#4a8a5a", "#5aaa6a", "#3a5a6a", "#4a7a8a"]
    },

    # Urban
    SceneType.MINIMALIST_CITY: {
        "name": "Minimalist City",
        "theme": SceneTheme.URBAN,
        "emoji": "🏙️",
        "default_palette": ["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#ecf0f1", "#bdc3c7"]
    },
    SceneType.NEON_CITY: {
        "name": "Neon City",
        "theme": SceneTheme.URBAN,
        "emoji": "🌃",
        "default_palette": ["#0d0221", "#ff2079", "#00fff5", "#7b2fff", "#ff00ff", "#ffff00"]
    },
    SceneType.CLASSIC_SKYLINE: {
        "name": "Classic Skyline",
        "theme": SceneTheme.URBAN,
        "emoji": "🏙️",
        "default_palette": ["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#ecf0f1", "#bdc3c7"]
    },
    SceneType.GEOMETRIC_GRID: {
        "name": "Geometric Grid",
        "theme": SceneTheme.URBAN,
        "emoji": "📐",
        "default_palette": ["#000000", "#1a1a1a", "#333333", "#4d4d4d", "#ffffff", "#cccccc"]
    },
    SceneType.MODERN_ART: {
        "name": "Modern Art",
        "theme": SceneTheme.URBAN,
        "emoji": "🎨",
        "default_palette": ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
    },
    SceneType.ROOFTOP_GARDEN: {
        "name": "Rooftop Garden",
        "theme": SceneTheme.URBAN,
        "emoji": "🌿",
        "default_palette": ["#87ceeb", "#b0d4e8", "#4a7c59", "#6aaa70", "#8a8a8a", "#c8c8c8"]
    },
    SceneType.SUBWAY: {
        "name": "Subway",
        "theme": SceneTheme.URBAN,
        "emoji": "🚇",
        "default_palette": ["#1a1a2e", "#16213e", "#0f3460", "#e94560", "#f5a623", "#c8c8c8"]
    },
    SceneType.NIGHT_MARKET: {
        "name": "Night Market",
        "theme": SceneTheme.URBAN,
        "emoji": "🏮",
        "default_palette": ["#1a0a05", "#3a1a08", "#ff6b1a", "#ffaa33", "#ff3366", "#ffe066"]
    },
    SceneType.INDUSTRIAL: {
        "name": "Industrial",
        "theme": SceneTheme.URBAN,
        "emoji": "🏭",
        "default_palette": ["#1a1a1a", "#2a2a2a", "#4a4a4a", "#6a6a6a", "#ff6600", "#ffaa00"]
    },
    SceneType.RAINY_STREET: {
        "name": "Rainy Street",
        "theme": SceneTheme.URBAN,
        "emoji": "🌧️",
        "default_palette": ["#0a0f1a", "#141e2e", "#1e2d42", "#2a3d56", "#ff9933", "#ffcc66"]
    },

    # Underwater
    SceneType.DEEP_OCEAN: {
        "name": "Deep Ocean",
        "theme": SceneTheme.UNDERWATER,
        "emoji": "🌊",
        "default_palette": ["#000814", "#001d3d", "#003566", "#0077b6", "#00b4d8", "#90e0ef"]
    },
    SceneType.SHIPWRECK: {
        "name": "Shipwreck",
        "theme": SceneTheme.UNDERWATER,
        "emoji": "⛵",
        "default_palette": ["#001220", "#002a40", "#004060", "#5a7a6a", "#8aaa8a", "#c8d8c0"]
    },
    SceneType.KELP_FOREST: {
        "name": "Kelp Forest",
        "theme": SceneTheme.UNDERWATER,
        "emoji": "🌿",
        "default_palette": ["#001a10", "#003020", "#005030", "#007040", "#40a060", "#80d090"]
    },
    SceneType.BIOLUMINESCENT: {
        "name": "Bioluminescent",
        "theme": SceneTheme.UNDERWATER,
        "emoji": "✨",
        "default_palette": ["#000510", "#000a20", "#001040", "#0040a0", "#00d4ff", "#80ffee"]
    },
    SceneType.SUBMARINE: {
        "name": "Submarine",
        "theme": SceneTheme.UNDERWATER,
        "emoji": "🪬",
        "default_palette": ["#001828", "#002a40", "#003d5c", "#f5a623", "#e8e8e8", "#00b4d8"]
    },
    SceneType.TIDE_POOL: {
        "name": "Tide Pool",
        "theme": SceneTheme.UNDERWATER,
        "emoji": "🐠",
        "default_palette": ["#87ceeb", "#5a9ab5", "#3a7a95", "#8a7a6a", "#ff7a5a", "#ffaa80"]
    },

    # Fantasy
    SceneType.ENCHANTED_FOREST: {
        "name": "Enchanted Forest",
        "theme": SceneTheme.FANTASY,
        "emoji": "🧚",
        "default_palette": ["#0d0d2b", "#1a1a4a", "#2d1b69", "#7b2fff", "#00ff9f", "#ffe066"]
    },
    SceneType.FLOATING_ISLANDS: {
        "name": "Floating Islands",
        "theme": SceneTheme.FANTASY,
        "emoji": "🏔️",
        "default_palette": ["#87ceeb", "#b0d4f0", "#4a7c59", "#6aaa70", "#c8a878", "#ffffff"]
    },
    SceneType.CRYSTAL_CAVE: {
        "name": "Crystal Cave",
        "theme": SceneTheme.FANTASY,
        "emoji": "💎",
        "default_palette": ["#0a0520", "#1a0a40", "#2a1060", "#8844cc", "#cc88ff", "#ffffff"]
    },
    SceneType.DRAGON_LAIR: {
        "name": "Dragon Lair",
        "theme": SceneTheme.FANTASY,
        "emoji": "🐉",
        "default_palette": ["#1a0500", "#3a0a00", "#6a1500", "#cc3300", "#ff6600", "#ffcc00"]
    },
    SceneType.ANCIENT_RUINS: {
        "name": "Ancient Ruins",
        "theme": SceneTheme.FANTASY,
        "emoji": "🟿",
        "default_palette": ["#1a1a0a", "#3a3a1a", "#6a6a3a", "#9a8a5a", "#c8b878", "#e8d8a8"]
    },
    SceneType.AURORA_CASTLE: {
        "name": "Aurora Castle",
        "theme": SceneTheme.FANTASY,
        "emoji": "🏰",
        "default_palette": ["#020b18", "#0d1a30", "#1aff9c", "#b3fff0", "#cc88ff", "#ffffff"]
    },
}


# Minimal scenes live in premium_engine; register them with the same shape.
for _key, _definition in PREMIUM_SCENE_DEFINITIONS.items():
    SCENE_DEFINITIONS[SceneType(_key)] = {**_definition, "theme": SceneTheme.MINIMAL}


def get_scene_default_palette(scene_type: str) -> list:
    """Get default palette for a scene type"""
    scene_def = SCENE_DEFINITIONS.get(scene_type)
    if not scene_def:
        return ["#000000", "#444444", "#888888", "#cccccc"]

    if scene_def["default_palette"]:
        return scene_def["default_palette"]

    # For random scenes, pick a random palette from the theme
    theme = scene_def["theme"]
    all_palettes = []
    for s, defn in SCENE_DEFINITIONS.items():
        if defn["theme"] == theme and defn["default_palette"]:
            all_palettes.extend(defn["default_palette"])

    if all_palettes:
        # Return a subset of 4 colors
        return all_palettes[:4]
    return ["#000000", "#444444", "#888888", "#cccccc"]


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _sky_gradient(draw, width, height, colors):
    """Shared helper: draw a vertical sky gradient from colors[0] to colors[1]"""
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _wavy_band(draw, width, height, band_y, amplitude, frequency, color):
    """Shared helper: draw a wavy filled band down to the bottom of the image"""
    points = []
    for x in range(width):
        offset = math.sin(x * frequency) * amplitude
        points.append((x, int(band_y + offset)))
    draw.polygon(points + [(width, height), (0, height)], fill=color)


def generate_landmark_eiffel_tower(draw, width, height, colors, rng):
    """Generate Eiffel Tower silhouette"""
    _sky_gradient(draw, width, height, colors)

    # Ground
    ground_y = int(height * 0.85)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    # Eiffel Tower
    tower_x = width // 2
    tower_base = int(height * 0.15)
    tower_top = int(height * 0.45)
    tower_width = int(width * 0.15)

    tower_color = hex_to_rgb(colors[3])

    # Draw tower with tapering
    for y in range(tower_base, tower_top, 5):
        progress = (y - tower_base) / (tower_top - tower_base)
        current_width = tower_width * (1 - progress * 0.8)

        # Draw horizontal bars
        if progress < 0.7:
            draw.rectangle([tower_x - current_width, y, tower_x + current_width, y + 3], fill=tower_color)

        # Draw diagonal legs
        leg_y = int(height * 0.85)
        leg_width = tower_width * 2.5
        draw.line([(tower_x - leg_width, leg_y), (tower_x - current_width, y)], fill=tower_color, width=2)
        draw.line([(tower_x + leg_width, leg_y), (tower_x + current_width, y)], fill=tower_color, width=2)

    # Tower top
    draw.polygon([
        (tower_x, tower_top),
        (tower_x - 5, tower_top - 20),
        (tower_x + 5, tower_top - 20)
    ], fill=tower_color)


def generate_landmark_statue_of_liberty(draw, width, height, colors, rng):
    """Generate Statue of Liberty silhouette"""
    _sky_gradient(draw, width, height, colors)

    # Water
    water_y = int(height * 0.8)
    draw.rectangle([0, water_y, width, height], fill=hex_to_rgb(colors[2]))

    # pedestal
    ped_x = width // 2
    ped_y = water_y
    ped_w = int(width * 0.15)
    ped_h = int(height * 0.1)
    ped_color = hex_to_rgb(colors[3])
    draw.rectangle([ped_x - ped_w, ped_y - ped_h, ped_x + ped_w, ped_y], fill=ped_color)

    # Statue base
    base_y = ped_y - ped_h
    base_w = int(ped_w * 0.8)
    base_h = int(height * 0.05)
    base_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[1])
    draw.rectangle([ped_x - base_w, base_y - base_h, ped_x + base_w, base_y], fill=base_color)

    # Statue body
    body_y = base_y - base_h
    body_w = int(base_w * 0.7)
    body_h = int(height * 0.25)
    body_color = hex_to_rgb(colors[5] if len(colors) > 5 else colors[2])
    draw.rectangle([ped_x - body_w, body_y - body_h, ped_x + body_w, body_y], fill=body_color)

    # Crown/Head
    crown_y = body_y - body_h
    crown_r = int(width * 0.03)
    draw.ellipse([ped_x - crown_r, crown_y - crown_r * 2, ped_x + crown_r, crown_y], fill=body_color)

    # Torch
    torch_y = crown_y - crown_r * 2
    torch_w = int(width * 0.02)
    torch_h = int(height * 0.1)
    torch_color = hex_to_rgb(colors[1])
    draw.rectangle([ped_x - torch_w, torch_y - torch_h, ped_x + torch_w, torch_y], fill=torch_color)


def generate_landmark_sydney(draw, width, height, colors, rng):
    """Generate Sydney Opera House silhouette (stylized sail shells over water)"""
    _sky_gradient(draw, width, height, colors)

    # Water
    water_y = int(height * 0.75)
    draw.rectangle([0, water_y, width, height], fill=hex_to_rgb(colors[2]))

    # Water reflection ripples
    ripple_color = hex_to_rgb(colors[3])
    for i in range(4):
        ry = water_y + int(height * 0.05) + i * int(height * 0.04)
        draw.line([(0, ry), (width, ry)], fill=ripple_color, width=2)

    # Base platform
    base_x = int(width * 0.2)
    base_w = int(width * 0.6)
    base_h = int(height * 0.04)
    base_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[1])
    draw.rectangle([base_x, water_y - base_h, base_x + base_w, water_y], fill=base_color)

    # Opera house "sails" - overlapping curved triangular shells
    shell_color = hex_to_rgb(colors[5]) if len(colors) > 5 else hex_to_rgb(colors[0])
    num_shells = 5
    shell_base_y = water_y - base_h
    for i in range(num_shells):
        shell_x = base_x + int(base_w * (i + 0.5) / num_shells)
        shell_h = int(height * (0.12 + 0.03 * math.sin(i)))
        shell_w = int(width * 0.06)
        draw.polygon([
            (shell_x - shell_w, shell_base_y),
            (shell_x, shell_base_y - shell_h),
            (shell_x + shell_w, shell_base_y),
        ], fill=shell_color)


def generate_landmark_big_ben(draw, width, height, colors, rng):
    """Generate Big Ben clock tower silhouette"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.88)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    cx = width // 2
    tower_w = int(width * 0.14)
    tower_top = int(height * 0.2)
    tower_color = hex_to_rgb(colors[3])

    # Main tower shaft
    draw.rectangle([cx - tower_w, tower_top, cx + tower_w, ground_y], fill=tower_color)

    # Vertical ribbing detail
    rib_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[1])
    for rx in range(cx - tower_w, cx + tower_w, max(6, tower_w // 3)):
        draw.line([(rx, tower_top), (rx, ground_y)], fill=rib_color, width=1)

    # Clock face housing (slightly wider block)
    clock_h = int(height * 0.12)
    clock_y = tower_top + int(height * 0.03)
    clock_w = int(tower_w * 1.15)
    draw.rectangle([cx - clock_w, clock_y, cx + clock_w, clock_y + clock_h], fill=rib_color)

    # Clock face circle
    face_color = hex_to_rgb(colors[5] if len(colors) > 5 else colors[0])
    face_r = int(clock_h * 0.4)
    face_cy = clock_y + clock_h // 2
    draw.ellipse([cx - face_r, face_cy - face_r, cx + face_r, face_cy + face_r], fill=face_color)
    # Clock hands
    draw.line([(cx, face_cy), (cx, face_cy - int(face_r * 0.7))], fill=tower_color, width=2)
    draw.line([(cx, face_cy), (cx + int(face_r * 0.5), face_cy)], fill=tower_color, width=2)

    # Spire / pyramidal roof
    spire_top = tower_top - int(height * 0.12)
    draw.polygon([
        (cx - tower_w, tower_top),
        (cx, spire_top),
        (cx + tower_w, tower_top),
    ], fill=tower_color)


def generate_landmark_taj_mahal(draw, width, height, colors, rng):
    """Generate Taj Mahal silhouette with central dome, minarets, and reflecting pool"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.82)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    # Reflecting pool
    pool_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[1])
    draw.rectangle([int(width * 0.25), int(height * 0.9), int(width * 0.75), height], fill=pool_color)

    body_color = hex_to_rgb(colors[3])
    cx = width // 2

    # Main platform / base
    base_w = int(width * 0.28)
    base_h = int(height * 0.18)
    draw.rectangle([cx - base_w, ground_y - base_h, cx + base_w, ground_y], fill=body_color)

    # Central dome
    dome_r = int(width * 0.16)
    dome_base_y = ground_y - base_h
    draw.ellipse([cx - dome_r, dome_base_y - dome_r * 2, cx + dome_r, dome_base_y], fill=body_color)
    # Dome finial
    draw.line([(cx, dome_base_y - dome_r * 2), (cx, dome_base_y - dome_r * 2 - 15)], fill=body_color, width=3)

    # Four corner minarets
    minaret_color = hex_to_rgb(colors[5] if len(colors) > 5 else colors[0])
    minaret_h = int(height * 0.28)
    minaret_w = int(width * 0.02)
    for side in (-1, 1):
        for spread in (1.0, 1.6):
            mx = cx + side * int(base_w * spread)
            draw.rectangle([mx - minaret_w, ground_y - minaret_h, mx + minaret_w, ground_y], fill=minaret_color)
            # Minaret dome cap
            cap_r = minaret_w + 2
            cap_y = ground_y - minaret_h
            draw.ellipse([mx - cap_r, cap_y - cap_r * 2, mx + cap_r, cap_y], fill=minaret_color)


def generate_landmark_christ_redeemer(draw, width, height, colors, rng):
    """Generate Christ the Redeemer statue silhouette atop a hill"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.85)
    hill_color = hex_to_rgb(colors[2])
    # Hill mound
    draw.ellipse([int(width * 0.1), ground_y - int(height * 0.15), int(width * 0.9), ground_y + int(height * 0.2)],
                 fill=hill_color)

    cx = width // 2
    statue_color = hex_to_rgb(colors[3])

    # Pedestal
    ped_h = int(height * 0.05)
    ped_w = int(width * 0.05)
    ped_y = ground_y - int(height * 0.1)
    draw.rectangle([cx - ped_w, ped_y - ped_h, cx + ped_w, ped_y], fill=statue_color)

    # Body (robe), tapering column
    body_top = ped_y - ped_h - int(height * 0.25)
    body_w = int(width * 0.04)
    draw.polygon([
        (cx - int(body_w * 1.4), ped_y - ped_h),
        (cx - body_w, body_top),
        (cx + body_w, body_top),
        (cx + int(body_w * 1.4), ped_y - ped_h),
    ], fill=statue_color)

    # Outstretched arms
    arm_y = body_top + int(height * 0.05)
    arm_span = int(width * 0.22)
    draw.line([(cx - arm_span, arm_y), (cx + arm_span, arm_y)], fill=statue_color, width=max(4, int(height * 0.012)))

    # Head
    head_r = int(width * 0.02)
    draw.ellipse([cx - head_r, body_top - head_r * 2, cx + head_r, body_top], fill=statue_color)


def generate_landmark_colosseum(draw, width, height, colors, rng):
    """Generate Colosseum silhouette - a tiered elliptical amphitheater with arches"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.85)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    structure_color = hex_to_rgb(colors[3])
    arch_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[0])

    # Three stacked tiers, each a wide rounded band, narrowing as they rise
    num_tiers = 3
    tier_h = int(height * 0.12)
    outer_w = int(width * 0.42)
    for tier in range(num_tiers):
        tier_y0 = ground_y - tier_h * (tier + 1)
        tier_y1 = ground_y - tier_h * tier
        tier_w = int(outer_w * (1 - tier * 0.08))
        cx = width // 2
        draw.rectangle([cx - tier_w, tier_y0, cx + tier_w, tier_y1], fill=structure_color)

        # Arched windows along this tier
        num_arches = 10 - tier * 2
        arch_w = (tier_w * 2) // num_arches
        for a in range(num_arches):
            ax = cx - tier_w + a * arch_w + arch_w // 4
            draw.rectangle([ax, tier_y0 + int(tier_h * 0.2), ax + arch_w // 2, tier_y1 - int(tier_h * 0.1)],
                            fill=arch_color)


def generate_landmark_great_wall(draw, width, height, colors, rng):
    """Great Wall of China snaking over rolling hills"""
    _sky_gradient(draw, width, height, colors)
    ground_y = int(height * 0.72)

    # Rolling hills
    hill_color = hex_to_rgb(colors[4 % len(colors)])
    _wavy_band(draw, width, height, ground_y, 40, 0.004, hill_color)
    draw.rectangle([0, ground_y + 60, width, height], fill=hex_to_rgb(colors[5 % len(colors)]))

    # Wall path follows a sine wave across the image
    wall_color = hex_to_rgb(colors[2])
    wall_h = int(height * 0.06)
    wall_w = int(width * 0.04)
    for x in range(0, width, 3):
        wy = int(ground_y - 10 + math.sin(x * 0.006) * 35)
        draw.rectangle([x, wy - wall_h, x + 3, wy], fill=wall_color)

    # Watchtowers at intervals
    tower_color = hex_to_rgb(colors[3])
    for tx in range(int(width * 0.08), width, int(width * 0.18)):
        wy = int(ground_y - 10 + math.sin(tx * 0.006) * 35)
        draw.rectangle([tx - wall_w, wy - wall_h - int(height * 0.07),
                         tx + wall_w, wy], fill=tower_color)
        # Battlements
        for bx in range(tx - wall_w, tx + wall_w, int(wall_w * 0.6)):
            draw.rectangle([bx, wy - wall_h - int(height * 0.07) - int(height * 0.02),
                             bx + int(wall_w * 0.4), wy - wall_h - int(height * 0.07)], fill=tower_color)


def generate_landmark_burj_khalifa(draw, width, height, colors, rng):
    """Burj Khalifa at night with city lights below"""
    _sky_gradient(draw, width, height, colors)
    cx = width // 2
    ground_y = int(height * 0.88)

    # City glow on horizon
    glow_color = hex_to_rgb(colors[3])
    draw.rectangle([0, ground_y - int(height * 0.04), width, ground_y], fill=glow_color)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[1]))

    # Small background buildings
    bld_color = hex_to_rgb(colors[1])
    for i in range(12):
        bx = int(width * i / 12)
        bh = rng.randint(int(height * 0.08), int(height * 0.22))
        draw.rectangle([bx, ground_y - bh, bx + int(width / 12) - 2, ground_y], fill=bld_color)

    # Main tower — tapered in 4 setback stages
    tower_color = hex_to_rgb(colors[2])
    stages = [(0.09, 0.88), (0.06, 0.65), (0.04, 0.45), (0.025, 0.28), (0.01, 0.12)]
    for w_frac, base_frac in stages:
        tw = int(width * w_frac)
        by = int(height * base_frac)
        draw.rectangle([cx - tw, by, cx + tw, ground_y], fill=tower_color)

    # Spire
    spire_top = int(height * 0.04)
    draw.polygon([(cx - 4, int(height * 0.12)), (cx, spire_top), (cx + 4, int(height * 0.12))],
                 fill=hex_to_rgb(colors[4 % len(colors)]))

    # Window lights
    win_color = hex_to_rgb(colors[4 % len(colors)])
    for wy in range(int(height * 0.15), ground_y, int(height * 0.03)):
        tw = max(4, int(width * 0.09 * (1 - (ground_y - wy) / ground_y * 0.7)))
        for wx in range(cx - tw + 2, cx + tw - 2, 6):
            if rng.random() > 0.35:
                draw.rectangle([wx, wy, wx + 3, wy + int(height * 0.018)], fill=win_color)


def generate_landmark_sagrada_familia(draw, width, height, colors, rng):
    """Sagrada Familia with its distinctive spires"""
    _sky_gradient(draw, width, height, colors)
    cx = width // 2
    ground_y = int(height * 0.86)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[3 % len(colors)]))

    stone_color = hex_to_rgb(colors[1 % len(colors)])
    spire_color = hex_to_rgb(colors[2 % len(colors)])
    detail_color = hex_to_rgb(colors[3 % len(colors)])

    # Main nave body
    nave_w = int(width * 0.28)
    nave_top = int(height * 0.42)
    draw.rectangle([cx - nave_w, nave_top, cx + nave_w, ground_y], fill=stone_color)

    # Central tall spires (3)
    spire_data = [(-int(width * 0.12), int(width * 0.04), int(height * 0.08)),
                  (0, int(width * 0.055), int(height * 0.04)),
                  (int(width * 0.12), int(width * 0.04), int(height * 0.08))]
    for sx_off, sw, stop_y in spire_data:
        sx = cx + sx_off
        draw.rectangle([sx - sw, stop_y, sx + sw, ground_y], fill=spire_color)
        draw.polygon([(sx - sw, stop_y), (sx, stop_y - int(height * 0.08)), (sx + sw, stop_y)],
                     fill=spire_color)
        # Horizontal bands on spire
        for by in range(stop_y, ground_y, int(height * 0.05)):
            draw.line([(sx - sw, by), (sx + sw, by)], fill=detail_color, width=2)

    # Outer flanking towers (2 each side)
    for side, count in [(-1, 2), (1, 2)]:
        for i in range(count):
            ftx = cx + side * int(width * (0.2 + i * 0.1))
            ftw = int(width * 0.025)
            fth = int(height * (0.28 - i * 0.06))
            fty = ground_y - fth
            draw.rectangle([ftx - ftw, fty, ftx + ftw, ground_y], fill=stone_color)
            draw.polygon([(ftx - ftw, fty), (ftx, fty - int(height * 0.06)), (ftx + ftw, fty)],
                         fill=spire_color)

    # Rose window
    draw.ellipse([cx - int(width * 0.06), nave_top + int(height * 0.04),
                  cx + int(width * 0.06), nave_top + int(height * 0.14)], fill=detail_color)


def generate_landmark_stonehenge(draw, width, height, colors, rng):
    """Stonehenge on a misty plain at dusk"""
    _sky_gradient(draw, width, height, colors)
    ground_y = int(height * 0.72)

    # Ground plain
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[3 % len(colors)]))
    # Mist band
    mist_color = hex_to_rgb(colors[1 % len(colors)])
    draw.rectangle([0, ground_y - int(height * 0.04), width, ground_y + int(height * 0.03)], fill=mist_color)

    stone_color = hex_to_rgb(colors[2 % len(colors)])
    cap_color   = hex_to_rgb(colors[3 % len(colors)])
    cx = width // 2
    stone_w = int(width * 0.025)
    stone_h = int(height * 0.18)
    cap_h   = int(height * 0.04)
    cap_w   = int(width * 0.07)

    # Outer ring: 6 upright pairs with lintels
    pairs = [(-0.22, -0.10), (0.10, 0.22), (-0.06, 0.06)]
    for lx, rx in pairs:
        for ox in [lx, rx]:
            sx = cx + int(width * ox)
            draw.rectangle([sx - stone_w, ground_y - stone_h, sx + stone_w, ground_y], fill=stone_color)
        # Lintel across the pair
        mid = cx + int(width * (lx + rx) / 2)
        draw.rectangle([mid - int(cap_w * 0.9), ground_y - stone_h - cap_h,
                         mid + int(cap_w * 0.9), ground_y - stone_h], fill=cap_color)

    # Inner trilithon (taller, center)
    for ox in [-0.04, 0.04]:
        sx = cx + int(width * ox)
        draw.rectangle([sx - stone_w, ground_y - int(stone_h * 1.25),
                         sx + stone_w, ground_y], fill=stone_color)
    draw.rectangle([cx - int(cap_w * 0.55), ground_y - int(stone_h * 1.25) - cap_h,
                     cx + int(cap_w * 0.55), ground_y - int(stone_h * 1.25)], fill=cap_color)

    # Fallen/leaning stones
    for ox, angle in [(-0.15, 0.3), (0.17, -0.25)]:
        sx = cx + int(width * ox)
        pts = [
            (sx - stone_w, ground_y),
            (sx + stone_w, ground_y),
            (sx + stone_w + int(stone_h * math.sin(angle)), ground_y - int(stone_h * math.cos(angle))),
            (sx - stone_w + int(stone_h * math.sin(angle)), ground_y - int(stone_h * math.cos(angle))),
        ]
        draw.polygon(pts, fill=stone_color)


def generate_landmark_machu_picchu(draw, width, height, colors, rng):
    """Machu Picchu terraced ruins on a mountain ridge"""
    _sky_gradient(draw, width, height, colors)

    # Background misty mountains
    for layer in range(3):
        mc = hex_to_rgb(colors[(layer + 1) % len(colors)])
        base_y = int(height * (0.45 + layer * 0.08))
        pts = [(0, height)]
        for x in range(0, width + 1, int(width / 6)):
            ph = rng.randint(int(height * 0.1), int(height * 0.3))
            pts.append((x, base_y - ph))
        pts.append((width, height))
        draw.polygon(pts, fill=mc)

    ground_y = int(height * 0.78)
    ridge_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=ridge_color)

    # Terraced walls
    terrace_color = hex_to_rgb(colors[3])
    num_terraces = 6
    for i in range(num_terraces):
        ty = ground_y - i * int(height * 0.06)
        tw_left  = int(width * (0.1 + i * 0.02))
        tw_right = int(width * (0.9 - i * 0.02))
        draw.rectangle([tw_left, ty - int(height * 0.015), tw_right, ty], fill=terrace_color)

    # Stone buildings on top terrace
    bld_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[0])
    top_y = ground_y - num_terraces * int(height * 0.06)
    for i in range(5):
        bx = int(width * (0.2 + i * 0.13))
        bh = rng.randint(int(height * 0.06), int(height * 0.12))
        bw = int(width * 0.07)
        draw.rectangle([bx, top_y - bh, bx + bw, top_y], fill=bld_color)
        # Doorway
        draw.rectangle([bx + bw // 3, top_y - int(bh * 0.5),
                         bx + bw * 2 // 3, top_y], fill=ridge_color)

    # Tall peak behind (Huayna Picchu)
    peak_color = hex_to_rgb(colors[5] if len(colors) > 5 else colors[1])
    draw.polygon([(int(width * 0.72), ground_y),
                  (int(width * 0.82), int(height * 0.18)),
                  (int(width * 0.92), ground_y)], fill=peak_color)


def generate_landmark_leaning_tower_pisa(draw, width, height, colors, rng):
    """Leaning Tower of Pisa with its characteristic tilt"""
    _sky_gradient(draw, width, height, colors)
    ground_y = int(height * 0.86)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[3 % len(colors)]))

    cx = width // 2 + int(width * 0.05)  # slightly right of center
    lean = int(width * 0.06)             # how far the top leans right
    tower_w = int(width * 0.09)
    tower_h = int(height * 0.58)
    tower_color = hex_to_rgb(colors[2])
    col_color   = hex_to_rgb(colors[3])

    # Tower body as a parallelogram (leaning right)
    top_y = ground_y - tower_h
    draw.polygon([
        (cx - tower_w, ground_y),
        (cx + tower_w, ground_y),
        (cx + tower_w + lean, top_y),
        (cx - tower_w + lean, top_y),
    ], fill=tower_color)

    # Colonnaded gallery floors (6 rings)
    num_floors = 6
    for f in range(num_floors):
        t = f / num_floors
        fy = ground_y - int(tower_h * (f + 1) / (num_floors + 1))
        fx_left  = cx - tower_w + int(lean * t)
        fx_right = cx + tower_w + int(lean * t)
        draw.line([(fx_left, fy), (fx_right, fy)], fill=col_color, width=max(2, int(height * 0.008)))
        # Columns
        num_cols = 8
        for c in range(num_cols + 1):
            col_x = fx_left + int((fx_right - fx_left) * c / num_cols)
            draw.line([(col_x, fy), (col_x, fy + int(tower_h / (num_floors + 1)))],
                      fill=col_color, width=2)

    # Belfry cap
    bx = cx + lean
    draw.polygon([
        (bx - tower_w + int(tower_w * 0.2), top_y),
        (bx, top_y - int(height * 0.06)),
        (bx + tower_w - int(tower_w * 0.2), top_y),
    ], fill=tower_color)

    # Grass patch
    grass_color = hex_to_rgb(colors[5 % len(colors)])
    draw.rectangle([0, ground_y - int(height * 0.02), width, ground_y], fill=grass_color)


def generate_landmark_acropolis(draw, width, height, colors, rng):
    """Acropolis of Athens — Parthenon on a rocky hill"""
    _sky_gradient(draw, width, height, colors)
    ground_y = int(height * 0.88)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[3 % len(colors)]))

    # Rocky hill
    hill_color = hex_to_rgb(colors[2 % len(colors)])
    hill_top_y = int(height * 0.58)
    draw.polygon([
        (0, ground_y),
        (int(width * 0.12), hill_top_y + int(height * 0.06)),
        (int(width * 0.3), hill_top_y),
        (int(width * 0.7), hill_top_y),
        (int(width * 0.88), hill_top_y + int(height * 0.06)),
        (width, ground_y),
    ], fill=hill_color)

    # Stepped platform (stylobate)
    plat_color = hex_to_rgb(colors[3])
    plat_y = hill_top_y
    for step in range(3):
        sw = int(width * (0.42 - step * 0.02))
        sy = plat_y + step * int(height * 0.015)
        draw.rectangle([width // 2 - sw, sy, width // 2 + sw, sy + int(height * 0.015)], fill=plat_color)

    # Parthenon columns
    col_color = hex_to_rgb(colors[5 % len(colors)])
    cx = width // 2
    col_base_y = plat_y + 3 * int(height * 0.015)
    col_top_y  = col_base_y - int(height * 0.22)
    col_w = int(width * 0.018)
    num_cols = 8
    col_span = int(width * 0.38)
    for i in range(num_cols):
        col_x = cx - col_span // 2 + int(col_span * i / (num_cols - 1))
        draw.rectangle([col_x - col_w, col_top_y, col_x + col_w, col_base_y], fill=col_color)

    # Entablature (horizontal beam)
    draw.rectangle([cx - col_span // 2 - col_w, col_top_y - int(height * 0.03),
                     cx + col_span // 2 + col_w, col_top_y], fill=plat_color)

    # Triangular pediment
    draw.polygon([
        (cx - col_span // 2 - col_w, col_top_y - int(height * 0.03)),
        (cx, col_top_y - int(height * 0.03) - int(height * 0.1)),
        (cx + col_span // 2 + col_w, col_top_y - int(height * 0.03)),
    ], fill=plat_color)


def generate_landmark_mount_fuji(draw, width, height, colors, rng):
    """Mount Fuji with cherry blossoms in the foreground"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.82)
    cx = width // 2

    # Lake reflection band
    lake_color = hex_to_rgb(colors[3])
    draw.rectangle([0, ground_y, width, ground_y + int(height * 0.1)], fill=lake_color)

    # Ground
    draw.rectangle([0, ground_y + int(height * 0.1), width, height], fill=hex_to_rgb(colors[2]))

    # Fuji cone — wide gentle slopes
    fuji_color = hex_to_rgb(colors[1])
    peak_y = int(height * 0.12)
    base_w = int(width * 0.55)
    draw.polygon([
        (cx - base_w, ground_y),
        (cx, peak_y),
        (cx + base_w, ground_y),
    ], fill=fuji_color)

    # Snow cap
    snow_color = hex_to_rgb(colors[4 % len(colors)])
    snow_h = int(height * 0.14)
    draw.polygon([
        (cx - int(base_w * 0.28), peak_y + snow_h),
        (cx, peak_y),
        (cx + int(base_w * 0.28), peak_y + snow_h),
    ], fill=snow_color)

    # Fuji reflection in lake (inverted, faded)
    refl_color = hex_to_rgb(colors[3])
    refl_h = int(height * 0.08)
    draw.polygon([
        (cx - int(base_w * 0.5), ground_y),
        (cx, ground_y + refl_h),
        (cx + int(base_w * 0.5), ground_y),
    ], fill=refl_color)

    # Cherry blossom trees in foreground
    blossom_color = hex_to_rgb(colors[5 % len(colors)])
    trunk_color   = hex_to_rgb(colors[2 % len(colors)])
    for i in range(rng.randint(4, 7)):
        tx = rng.randint(int(width * 0.05), int(width * 0.95))
        th = rng.randint(int(height * 0.08), int(height * 0.14))
        draw.line([(tx, ground_y), (tx, ground_y - th)], fill=trunk_color, width=4)
        cr = rng.randint(int(width * 0.04), int(width * 0.07))
        draw.ellipse([tx - cr, ground_y - th - cr, tx + cr, ground_y - th + cr // 2],
                     fill=blossom_color)


def generate_world_desert(draw, width, height, colors, rng):
    """Generate desert scene with dunes"""
    _sky_gradient(draw, width, height, colors)

    # Dunes
    num_dunes = rng.randint(4, 6)
    ground_y = int(height * 0.7)

    for i in range(num_dunes):
        dune_y = ground_y + int(height * 0.05 * i)
        color = hex_to_rgb(colors[(i + 2) % len(colors)])

        amplitude = rng.randint(20, 50)
        frequency = rng.uniform(0.003, 0.008)
        _wavy_band(draw, width, height, dune_y, amplitude, frequency, color)


def generate_world_beach(draw, width, height, colors, rng):
    """Generate beach scene"""
    _sky_gradient(draw, width, height, colors)

    # Ocean
    ocean_y = int(height * 0.6)
    ocean_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ocean_y, width, height], fill=ocean_color)

    # Waves
    for i in range(3):
        wave_y = ocean_y + int(height * 0.03 * i)
        wave_color = hex_to_rgb(colors[3])
        amplitude = rng.randint(5, 15)
        frequency = rng.uniform(0.01, 0.02)
        _wavy_band(draw, width, height, wave_y, amplitude, frequency, wave_color)

    # Sand
    sand_y = int(height * 0.55)
    sand_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[1])
    draw.rectangle([0, sand_y, width, ocean_y], fill=sand_color)


def generate_world_mountain(draw, width, height, colors, rng):
    """Generate mountain range scene with snow caps"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.85)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    # Layered mountain ranges, back to front
    num_layers = 3
    for layer in range(num_layers):
        peak_color = hex_to_rgb(colors[(layer + 2) % len(colors)])
        base_y = int(height * (0.55 + layer * 0.1))
        num_peaks = rng.randint(3, 5)
        points = [(0, height)]
        for p in range(num_peaks + 1):
            x = int(width * p / num_peaks)
            peak_h = rng.randint(int(height * 0.15), int(height * 0.35))
            y = base_y - peak_h if 0 < p < num_peaks else base_y
            points.append((x, y))
        points.append((width, height))
        draw.polygon(points, fill=peak_color)

    # Snow caps on the front layer's tallest peaks
    snow_color = hex_to_rgb(colors[-1])
    num_peaks = 4
    for p in range(num_peaks):
        x = int(width * (p + 0.5) / num_peaks)
        peak_h = int(height * 0.3)
        peak_y = ground_y - peak_h
        draw.polygon([
            (x - 15, peak_y + 25),
            (x, peak_y),
            (x + 15, peak_y + 25),
        ], fill=snow_color)


def generate_world_valley(draw, width, height, colors, rng):
    """Generate rolling valley scene"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.55)
    num_hills = 3
    for i in range(num_hills):
        hill_y = ground_y + int(height * 0.1 * i)
        color = hex_to_rgb(colors[(i + 2) % len(colors)])
        amplitude = rng.randint(25, 60)
        frequency = rng.uniform(0.002, 0.005)
        _wavy_band(draw, width, height, hill_y, amplitude, frequency, color)

    # Scattered wildflower dots
    flower_color = hex_to_rgb(colors[-1])
    for _ in range(rng.randint(20, 40)):
        fx = rng.randint(0, width)
        fy = rng.randint(int(height * 0.75), height)
        r = rng.randint(2, 4)
        draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=flower_color)


def generate_world_canyon(draw, width, height, colors, rng):
    """Generate a deep canyon/gorge scene with horizontal rock strata"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.3)

    # Canyon walls: horizontal layered rock bands narrowing toward a central gorge
    num_layers = 8
    layer_h = int((height - ground_y) / num_layers)
    for i in range(num_layers):
        y0 = ground_y + i * layer_h
        y1 = y0 + layer_h
        color = hex_to_rgb(colors[(i + 2) % len(colors)])
        # Gorge narrows as we go down, walls step inward
        inset = int(width * 0.02 * i)
        draw.rectangle([0, y0, inset + int(width * 0.15), y1], fill=color)
        draw.rectangle([width - inset - int(width * 0.15), y0, width, y1], fill=color)

    # River at the bottom of the gorge
    river_color = hex_to_rgb(colors[-1])
    river_y = int(height * 0.92)
    draw.rectangle([int(width * 0.3), river_y, int(width * 0.7), height], fill=river_color)


def generate_world_plateau(draw, width, height, colors, rng):
    """Generate flat-topped mesa/plateau formations over a desert plain"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.8)
    plain_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=plain_color)

    # Several flat-topped mesas of varying width/height
    num_mesas = rng.randint(3, 5)
    for i in range(num_mesas):
        mesa_color = hex_to_rgb(colors[(i + 3) % len(colors)])
        mx = int(width * (i + 0.5) / num_mesas) + rng.randint(-20, 20)
        mesa_w = rng.randint(int(width * 0.08), int(width * 0.16))
        mesa_h = rng.randint(int(height * 0.15), int(height * 0.35))
        top_y = ground_y - mesa_h
        # Trapezoid: wider base, flat narrower top
        draw.polygon([
            (mx - mesa_w, ground_y),
            (mx - int(mesa_w * 0.7), top_y),
            (mx + int(mesa_w * 0.7), top_y),
            (mx + mesa_w, ground_y),
        ], fill=mesa_color)


def generate_world_meadow(draw, width, height, colors, rng):
    """Generate a flat grassy meadow with scattered flowers and a few trees"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.65)
    grass_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=grass_color)

    # Subtle flat grass texture band (no rolling hills, unlike valley)
    texture_color = hex_to_rgb(colors[(3) % len(colors)])
    for i in range(3):
        strip_y = ground_y + int((height - ground_y) * i / 3)
        draw.line([(0, strip_y), (width, strip_y)], fill=texture_color, width=2)

    # Dense scattered wildflowers across the whole field
    flower_colors = [hex_to_rgb(colors[i % len(colors)]) for i in range(2, len(colors))]
    for _ in range(rng.randint(60, 100)):
        fx = rng.randint(0, width)
        fy = rng.randint(ground_y, height)
        r = rng.randint(2, 5)
        color = rng.choice(flower_colors) if flower_colors else hex_to_rgb(colors[-1])
        draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=color)

    # A couple of solitary trees
    tree_color = hex_to_rgb(colors[-1])
    for _ in range(rng.randint(1, 3)):
        tx = rng.randint(int(width * 0.1), int(width * 0.9))
        trunk_h = rng.randint(int(height * 0.1), int(height * 0.18))
        draw.line([(tx, ground_y), (tx, ground_y - trunk_h)], fill=tree_color, width=4)
        canopy_r = int(width * 0.03)
        draw.ellipse([tx - canopy_r, ground_y - trunk_h - canopy_r, tx + canopy_r, ground_y - trunk_h + canopy_r],
                     fill=tree_color)


def generate_world_glacier(draw, width, height, colors, rng):
    """Glacier scene with crevasses, ice seracs, and a meltwater lake"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.55)
    ice_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=ice_color)

    # Ice surface undulations
    for i in range(4):
        band_y = ground_y + int((height - ground_y) * i / 4)
        color = hex_to_rgb(colors[(i + 3) % len(colors)])
        amplitude = rng.randint(8, 20)
        _wavy_band(draw, width, height, band_y, amplitude, 0.006, color)

    # Crevasses (dark cracks)
    crack_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(5, 9)):
        cx = rng.randint(int(width * 0.05), int(width * 0.95))
        cy = rng.randint(ground_y + int(height * 0.05), int(height * 0.85))
        cw = rng.randint(2, 6)
        ch = rng.randint(int(height * 0.06), int(height * 0.18))
        draw.ellipse([cx - cw, cy, cx + cw, cy + ch], fill=crack_color)

    # Meltwater lake at base
    lake_color = hex_to_rgb(colors[4 % len(colors)])
    draw.ellipse([int(width * 0.25), int(height * 0.82), int(width * 0.75), height], fill=lake_color)

    # Snow specks
    for _ in range(rng.randint(30, 50)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, ground_y)
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=hex_to_rgb(colors[3 % len(colors)]))


def generate_world_rainforest(draw, width, height, colors, rng):
    """Rainforest with dense multi-layer canopy and rain streaks"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.78)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    # 4 canopy layers, progressively darker and lower
    for layer in range(4):
        layer_y = int(height * (0.22 + layer * 0.12))
        color = hex_to_rgb(colors[(layer + 1) % len(colors)])
        amplitude = rng.randint(15, 35)
        frequency = rng.uniform(0.012, 0.025)
        points = []
        for x in range(width):
            offset = math.sin(x * frequency + layer * 1.3) * amplitude
            points.append((x, int(layer_y + offset)))
        draw.polygon(points + [(width, ground_y), (0, ground_y)], fill=color)

    # Tall emergent tree trunks
    trunk_color = hex_to_rgb(colors[0])
    for _ in range(rng.randint(3, 6)):
        tx = rng.randint(int(width * 0.05), int(width * 0.95))
        th = rng.randint(int(height * 0.35), int(height * 0.55))
        draw.line([(tx, ground_y), (tx, ground_y - th)], fill=trunk_color, width=5)

    # Rain streaks
    rain_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(50, 80)):
        rx = rng.randint(0, width)
        ry = rng.randint(0, int(height * 0.6))
        draw.line([(rx, ry), (rx - 4, ry + 14)], fill=rain_color, width=1)


def generate_world_fjord(draw, width, height, colors, rng):
    """Norwegian fjord: steep cliffs flanking a narrow deep-water channel"""
    _sky_gradient(draw, width, height, colors)

    water_y = int(height * 0.52)
    cliff_color = hex_to_rgb(colors[4 % len(colors)])
    water_color = hex_to_rgb(colors[1])
    snow_color  = hex_to_rgb(colors[3])

    # Water channel
    draw.rectangle([0, water_y, width, height], fill=water_color)

    # Left cliff face
    left_pts = [(0, height)]
    for y in range(height, water_y - 1, -int(height * 0.04)):
        jut = rng.randint(int(width * 0.12), int(width * 0.32))
        left_pts.append((jut, y))
    left_pts.append((0, water_y))
    draw.polygon(left_pts, fill=cliff_color)

    # Right cliff face
    right_pts = [(width, height)]
    for y in range(height, water_y - 1, -int(height * 0.04)):
        jut = rng.randint(int(width * 0.68), int(width * 0.88))
        right_pts.append((jut, y))
    right_pts.append((width, water_y))
    draw.polygon(right_pts, fill=cliff_color)

    # Snow caps on cliff tops
    for x in range(0, int(width * 0.28), int(width * 0.04)):
        sy = rng.randint(int(height * 0.1), int(height * 0.25))
        draw.ellipse([x, sy, x + int(width * 0.06), sy + int(height * 0.04)], fill=snow_color)
    for x in range(int(width * 0.72), width, int(width * 0.04)):
        sy = rng.randint(int(height * 0.1), int(height * 0.25))
        draw.ellipse([x, sy, x + int(width * 0.06), sy + int(height * 0.04)], fill=snow_color)

    # Water ripples
    ripple_color = hex_to_rgb(colors[2])
    for i in range(4):
        ry = water_y + int((height - water_y) * (i + 1) / 5)
        _wavy_band(draw, width, height, ry, 5, 0.015, ripple_color)


def generate_world_wetlands(draw, width, height, colors, rng):
    """Wetlands/marsh with reeds, still water patches, and lily pads"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.6)
    mud_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=mud_color)

    # Still water patches
    water_color = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(3, 6)):
        wx = rng.randint(int(width * 0.05), int(width * 0.8))
        wy = rng.randint(ground_y + int(height * 0.05), int(height * 0.85))
        ww = rng.randint(int(width * 0.08), int(width * 0.2))
        wh = int(ww * 0.35)
        draw.ellipse([wx, wy, wx + ww, wy + wh], fill=water_color)

    # Reed clusters
    reed_color = hex_to_rgb(colors[3])
    for _ in range(rng.randint(12, 20)):
        rx = rng.randint(0, width)
        rbase = rng.randint(ground_y + int(height * 0.02), int(height * 0.9))
        rh = rng.randint(int(height * 0.1), int(height * 0.22))
        draw.line([(rx, rbase), (rx, rbase - rh)], fill=reed_color, width=2)
        # Reed head
        draw.ellipse([rx - 3, rbase - rh - 8, rx + 3, rbase - rh], fill=reed_color)

    # Lily pads
    lily_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(6, 12)):
        lx = rng.randint(int(width * 0.05), int(width * 0.9))
        ly = rng.randint(ground_y + int(height * 0.08), int(height * 0.88))
        lr = rng.randint(int(width * 0.015), int(width * 0.03))
        draw.ellipse([lx - lr, ly - lr // 2, lx + lr, ly + lr // 2], fill=lily_color)


def generate_world_steppe(draw, width, height, colors, rng):
    """Vast flat steppe with golden grass, distant low hills, and big sky"""
    # Big sky — 65% of image
    sky_split = int(height * 0.35)
    _sky_gradient(draw, width, height, colors)

    # Distant low hills silhouette
    hill_color = hex_to_rgb(colors[4 % len(colors)])
    hill_pts = [(0, height)]
    for x in range(0, width + 1, int(width / 8)):
        hy = sky_split + rng.randint(int(height * 0.02), int(height * 0.08))
        hill_pts.append((x, hy))
    hill_pts.append((width, height))
    draw.polygon(hill_pts, fill=hill_color)

    # Flat grassland
    grass_color = hex_to_rgb(colors[2])
    ground_y = sky_split + int(height * 0.06)
    draw.rectangle([0, ground_y, width, height], fill=grass_color)

    # Grass texture — short vertical strokes
    stroke_color = hex_to_rgb(colors[3])
    for _ in range(rng.randint(120, 180)):
        gx = rng.randint(0, width)
        gy = rng.randint(ground_y, height)
        gh = rng.randint(4, 12)
        draw.line([(gx, gy), (gx + rng.randint(-2, 2), gy - gh)], fill=stroke_color, width=1)

    # Sparse shrubs
    shrub_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(4, 8)):
        sx = rng.randint(int(width * 0.05), int(width * 0.95))
        sy = rng.randint(ground_y + int(height * 0.02), int(height * 0.8))
        sr = rng.randint(int(width * 0.015), int(width * 0.03))
        draw.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2], fill=shrub_color)


def generate_world_savanna(draw, width, height, colors, rng):
    """Generate savanna scene with acacia trees and golden grass"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.65)
    grass_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=grass_color)

    # Grass texture strokes
    stroke_color = hex_to_rgb(colors[3])
    for _ in range(rng.randint(60, 100)):
        gx = rng.randint(0, width)
        gy = rng.randint(ground_y, height)
        gh = rng.randint(5, 15)
        draw.line([(gx, gy), (gx, gy - gh)], fill=stroke_color, width=1)

    # Acacia-style silhouette trees
    tree_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[0])
    for _ in range(rng.randint(2, 4)):
        tx = rng.randint(int(width * 0.1), int(width * 0.9))
        trunk_h = rng.randint(int(height * 0.1), int(height * 0.18))
        draw.line([(tx, ground_y), (tx, ground_y - trunk_h)], fill=tree_color, width=4)
        canopy_w = int(width * 0.08)
        canopy_h = int(height * 0.03)
        canopy_y = ground_y - trunk_h
        draw.ellipse([tx - canopy_w, canopy_y - canopy_h, tx + canopy_w, canopy_y + canopy_h], fill=tree_color)


def generate_world_tundra(draw, width, height, colors, rng):
    """Generate icy tundra scene"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.75)
    snow_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=snow_color)

    # Gentle snow drifts
    for i in range(3):
        drift_y = ground_y + int(height * 0.04 * i)
        color = hex_to_rgb(colors[(i + 3) % len(colors)])
        amplitude = rng.randint(10, 25)
        frequency = rng.uniform(0.004, 0.008)
        _wavy_band(draw, width, height, drift_y, amplitude, frequency, color)

    # Falling snow specks
    speck_color = hex_to_rgb(colors[-1])
    for _ in range(rng.randint(40, 70)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, ground_y)
        r = rng.randint(1, 3)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=speck_color)


def generate_celestial_sunrise(draw, width, height, colors, rng):
    """Generate sunrise scene"""
    _sky_gradient(draw, width, height, colors)

    # Sun
    sun_y = int(height * 0.7)
    sun_r = int(width * 0.15)
    sun_color = hex_to_rgb(colors[2])
    draw.ellipse([width // 2 - sun_r, sun_y - sun_r, width // 2 + sun_r, sun_y + sun_r], fill=sun_color)

    # Sun rays
    for i in range(12):
        angle = (2 * math.pi / 12) * i
        ray_len = sun_r + int(width * 0.05)
        ray_color = hex_to_rgb(colors[3])
        draw.line([
            (width // 2 + sun_r * math.cos(angle), sun_y + sun_r * math.sin(angle)),
            (width // 2 + ray_len * math.cos(angle), sun_y + ray_len * math.sin(angle))
        ], fill=ray_color, width=2)


def generate_celestial_sunset(draw, width, height, colors, rng):
    """Generate sunset scene with a sun dipping toward a horizon"""
    _sky_gradient(draw, width, height, colors)

    horizon_y = int(height * 0.75)
    horizon_color = hex_to_rgb(colors[2])
    draw.rectangle([0, horizon_y, width, height], fill=horizon_color)

    # Sinking sun, partially below the horizon
    sun_y = horizon_y
    sun_r = int(width * 0.13)
    sun_color = hex_to_rgb(colors[3])
    draw.ellipse([width // 2 - sun_r, sun_y - sun_r, width // 2 + sun_r, sun_y + sun_r], fill=sun_color)
    # Redraw horizon strip over lower half of sun so it appears to set
    draw.rectangle([0, horizon_y, width, height], fill=horizon_color)
    draw.pieslice([width // 2 - sun_r, sun_y - sun_r, width // 2 + sun_r, sun_y + sun_r], 180, 360, fill=sun_color)

    # Warm glow bands above horizon
    glow_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[1])
    for i in range(3):
        band_y = horizon_y - int(height * 0.03 * (i + 1))
        draw.line([(0, band_y), (width, band_y)], fill=glow_color, width=2)


def generate_celestial_starfield(draw, width, height, colors, rng):
    """Generate a starry night sky"""
    _sky_gradient(draw, width, height, colors)

    star_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[-1])
    for _ in range(rng.randint(150, 250)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        r = rng.choice([1, 1, 1, 2, 2, 3])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=star_color)

    # A few brighter stars with a little sparkle cross
    bright_color = hex_to_rgb(colors[-1])
    for _ in range(rng.randint(8, 15)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        draw.line([(sx - 6, sy), (sx + 6, sy)], fill=bright_color, width=1)
        draw.line([(sx, sy - 6), (sx, sy + 6)], fill=bright_color, width=1)


def generate_celestial_eclipse(draw, width, height, colors, rng):
    """Generate a solar eclipse scene with corona"""
    _sky_gradient(draw, width, height, colors)

    cx, cy = width // 2, int(height * 0.45)
    corona_r = int(width * 0.16)
    moon_r = int(width * 0.13)

    corona_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[-1])
    draw.ellipse([cx - corona_r, cy - corona_r, cx + corona_r, cy + corona_r], fill=corona_color)

    # Corona rays
    ray_color = hex_to_rgb(colors[5] if len(colors) > 5 else colors[-1])
    for i in range(16):
        angle = (2 * math.pi / 16) * i
        inner = corona_r
        outer = corona_r + int(width * 0.04)
        draw.line([
            (cx + inner * math.cos(angle), cy + inner * math.sin(angle)),
            (cx + outer * math.cos(angle), cy + outer * math.sin(angle))
        ], fill=ray_color, width=2)

    # Dark moon disc covering the sun
    moon_color = hex_to_rgb(colors[0])
    draw.ellipse([cx - moon_r, cy - moon_r, cx + moon_r, cy + moon_r], fill=moon_color)


def generate_celestial_nebula(draw, width, height, colors, rng):
    """Generate a colorful nebula cloud scene"""
    _sky_gradient(draw, width, height, colors)

    # Layered translucent-looking blobs built from overlapping ellipses
    for i in range(rng.randint(5, 8)):
        color = hex_to_rgb(colors[(i + 2) % len(colors)])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        rx = rng.randint(int(width * 0.1), int(width * 0.3))
        ry = rng.randint(int(height * 0.08), int(height * 0.2))
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)

    # Scatter stars on top
    star_color = hex_to_rgb(colors[-1])
    for _ in range(rng.randint(60, 100)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=star_color)


def generate_celestial_galaxy(draw, width, height, colors, rng):
    """Generate a spiral galaxy scene"""
    _sky_gradient(draw, width, height, colors)

    cx, cy = width // 2, height // 2
    max_r = int(min(width, height) * 0.45)

    # Spiral arms made of dots
    num_arms = 2
    points_per_arm = 250
    for arm in range(num_arms):
        arm_offset = math.pi * arm
        color = hex_to_rgb(colors[(arm + 3) % len(colors)])
        for i in range(points_per_arm):
            t = i / points_per_arm
            angle = t * 6 * math.pi + arm_offset
            r = t * max_r
            x = cx + int(r * math.cos(angle))
            y = cy + int(r * math.sin(angle) * 0.6)
            size = max(1, int(3 * (1 - t)))
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)

    # Bright galactic core
    core_color = hex_to_rgb(colors[-1])
    core_r = int(max_r * 0.12)
    draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=core_color)


def generate_celestial_northern_lights(draw, width, height, colors, rng):
    """Generate northern lights scene"""
    _sky_gradient(draw, width, height, colors)

    # Aurora bands
    num_bands = rng.randint(3, 5)
    for i in range(num_bands):
        band_y = int(height * 0.3) + int(height * 0.1 * i)
        color = hex_to_rgb(colors[(i + 2) % len(colors)])
        alpha = int(150 * (1 - i / num_bands))
        blended = tuple(int(c * alpha / 255) for c in color)

        amplitude = rng.randint(30, 80)
        frequency = rng.uniform(0.002, 0.005)
        _wavy_band(draw, width, height, band_y, amplitude, frequency, blended)


def generate_celestial_lunar_eclipse(draw, width, height, colors, rng):
    """Blood moon lunar eclipse — deep red moon with star field"""
    _sky_gradient(draw, width, height, colors)

    # Stars
    star_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(120, 200)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=star_color)

    cx, cy = width // 2, int(height * 0.42)
    moon_r = int(width * 0.18)

    # Outer penumbra glow
    glow_color = hex_to_rgb(colors[2])
    for i in range(5, 0, -1):
        gr = moon_r + i * int(width * 0.015)
        draw.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=glow_color)

    # Blood moon disc — gradient from dark edge to bright center
    for i in range(moon_r, 0, -1):
        t = i / moon_r
        r = int(hex_to_rgb(colors[2])[0] * t + hex_to_rgb(colors[3])[0] * (1 - t))
        g = int(hex_to_rgb(colors[2])[1] * t + hex_to_rgb(colors[3])[1] * (1 - t))
        b = int(hex_to_rgb(colors[2])[2] * t + hex_to_rgb(colors[3])[2] * (1 - t))
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(r, g, b))

    # Bright limb highlight
    highlight = hex_to_rgb(colors[4 % len(colors)])
    draw.ellipse([cx - int(moon_r * 0.3), cy - int(moon_r * 0.5),
                  cx + int(moon_r * 0.3), cy - int(moon_r * 0.1)], fill=highlight)


def generate_celestial_comet(draw, width, height, colors, rng):
    """Comet streaking across a deep-space sky with a glowing nucleus and ion tail"""
    _sky_gradient(draw, width, height, colors)

    # Background stars
    star_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(100, 160)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=star_color)

    # Comet position — upper-right quadrant heading lower-left
    head_x = int(width * 0.72)
    head_y = int(height * 0.28)
    tail_len = int(width * 0.55)
    tail_angle = math.radians(210)  # pointing lower-left

    # Dust tail — wide, fading bands
    tail_color = hex_to_rgb(colors[3])
    for i in range(8, 0, -1):
        spread = i * int(width * 0.008)
        tx = head_x + int(tail_len * i / 8 * math.cos(tail_angle))
        ty = head_y + int(tail_len * i / 8 * math.sin(tail_angle))
        draw.line([(head_x, head_y), (tx + spread, ty - spread)], fill=tail_color, width=max(1, 8 - i))
        draw.line([(head_x, head_y), (tx - spread, ty + spread)], fill=tail_color, width=max(1, 8 - i))

    # Ion tail — narrow, bright blue streak
    ion_color = hex_to_rgb(colors[2])
    ion_end_x = head_x + int(tail_len * math.cos(tail_angle + math.radians(10)))
    ion_end_y = head_y + int(tail_len * math.sin(tail_angle + math.radians(10)))
    draw.line([(head_x, head_y), (ion_end_x, ion_end_y)], fill=ion_color, width=3)

    # Coma (glowing haze around nucleus)
    coma_color = hex_to_rgb(colors[4 % len(colors)])
    coma_r = int(width * 0.04)
    draw.ellipse([head_x - coma_r, head_y - coma_r, head_x + coma_r, head_y + coma_r], fill=coma_color)

    # Bright nucleus
    nucleus_color = hex_to_rgb(colors[5 % len(colors)])
    nuc_r = int(width * 0.015)
    draw.ellipse([head_x - nuc_r, head_y - nuc_r, head_x + nuc_r, head_y + nuc_r], fill=nucleus_color)


def generate_celestial_meteor_shower(draw, width, height, colors, rng):
    """Radiant meteor shower with many streaks converging from a vanishing point"""
    _sky_gradient(draw, width, height, colors)

    # Stars
    star_color = hex_to_rgb(colors[3])
    for _ in range(rng.randint(100, 160)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=star_color)

    # Radiant point — upper center
    rad_x = int(width * 0.5) + rng.randint(-int(width * 0.1), int(width * 0.1))
    rad_y = int(height * 0.2)

    # Meteors radiating outward
    meteor_color = hex_to_rgb(colors[4 % len(colors)])
    trail_color  = hex_to_rgb(colors[5 % len(colors)])
    num_meteors = rng.randint(18, 28)
    for _ in range(num_meteors):
        angle = rng.uniform(0, 2 * math.pi)
        length = rng.randint(int(width * 0.08), int(width * 0.3))
        start_dist = rng.randint(int(width * 0.02), int(width * 0.12))
        mx0 = rad_x + int(start_dist * math.cos(angle))
        my0 = rad_y + int(start_dist * math.sin(angle))
        mx1 = rad_x + int((start_dist + length) * math.cos(angle))
        my1 = rad_y + int((start_dist + length) * math.sin(angle))
        # Bright head
        draw.line([(mx0, my0), (mx1, my1)], fill=meteor_color, width=2)
        # Fading trail (slightly offset)
        draw.line([(mx0 + 1, my0 + 1), (mx1 + 1, my1 + 1)], fill=trail_color, width=1)

    # Bright radiant glow
    glow_r = int(width * 0.03)
    draw.ellipse([rad_x - glow_r, rad_y - glow_r, rad_x + glow_r, rad_y + glow_r],
                 fill=hex_to_rgb(colors[5 % len(colors)]))


def generate_celestial_binary_stars(draw, width, height, colors, rng):
    """Two orbiting stars — one hot blue, one cool orange — with accretion glow and star field"""
    _sky_gradient(draw, width, height, colors)

    # Star field
    for _ in range(rng.randint(120, 180)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=hex_to_rgb(colors[3]))

    cx, cy = width // 2, height // 2
    sep = int(width * 0.18)  # separation between the two stars

    # Star A — hot blue (left)
    ax, ay = cx - sep, cy
    star_a_color = hex_to_rgb(colors[3])
    for i in range(5, 0, -1):
        gr = int(width * 0.04) * i
        draw.ellipse([ax - gr, ay - gr, ax + gr, ay + gr], fill=star_a_color)
    draw.ellipse([ax - int(width * 0.04), ay - int(width * 0.04),
                  ax + int(width * 0.04), ay + int(width * 0.04)],
                 fill=hex_to_rgb(colors[5 % len(colors)]))

    # Star B — cool orange (right)
    bx, by = cx + sep, cy
    star_b_color = hex_to_rgb(colors[2])
    for i in range(4, 0, -1):
        gr = int(width * 0.035) * i
        draw.ellipse([bx - gr, by - gr, bx + gr, by + gr], fill=star_b_color)
    draw.ellipse([bx - int(width * 0.035), by - int(width * 0.035),
                  bx + int(width * 0.035), by + int(width * 0.035)],
                 fill=hex_to_rgb(colors[4 % len(colors)]))

    # Accretion bridge — faint ellipse connecting the two
    bridge_color = hex_to_rgb(colors[1])
    draw.ellipse([ax, cy - int(height * 0.04), bx, cy + int(height * 0.04)], fill=bridge_color)

    # Orbital ring
    orb_rx = sep + int(width * 0.06)
    orb_ry = int(height * 0.12)
    draw.ellipse([cx - orb_rx, cy - orb_ry, cx + orb_rx, cy + orb_ry],
                 outline=hex_to_rgb(colors[3]), width=1)


def generate_celestial_moonrise(draw, width, height, colors, rng):
    """Full moon rising over a calm dark ocean horizon"""
    _sky_gradient(draw, width, height, colors)

    horizon_y = int(height * 0.62)
    water_color = hex_to_rgb(colors[1])
    draw.rectangle([0, horizon_y, width, height], fill=water_color)

    # Stars in upper sky
    for _ in range(rng.randint(60, 100)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, horizon_y - int(height * 0.1))
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=hex_to_rgb(colors[5 % len(colors)]))

    cx = width // 2
    moon_r = int(width * 0.14)
    moon_y = horizon_y  # moon center sits on the horizon

    # Moon glow halo
    glow_color = hex_to_rgb(colors[3])
    for i in range(6, 0, -1):
        gr = moon_r + i * int(width * 0.012)
        draw.ellipse([cx - gr, moon_y - gr, cx + gr, moon_y + gr], fill=glow_color)

    # Moon disc
    moon_color = hex_to_rgb(colors[4 % len(colors)])
    draw.ellipse([cx - moon_r, moon_y - moon_r, cx + moon_r, moon_y + moon_r], fill=moon_color)

    # Subtle mare (dark patches) on moon
    mare_color = hex_to_rgb(colors[3])
    for _ in range(rng.randint(3, 5)):
        mx = cx + rng.randint(-int(moon_r * 0.5), int(moon_r * 0.5))
        my = moon_y + rng.randint(-int(moon_r * 0.5), int(moon_r * 0.5))
        mr = rng.randint(int(moon_r * 0.1), int(moon_r * 0.25))
        draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=mare_color)

    # Moon reflection on water — vertical shimmer column
    refl_color = hex_to_rgb(colors[4 % len(colors)])
    refl_w = int(moon_r * 0.5)
    for ry in range(horizon_y, height, 4):
        t = (ry - horizon_y) / (height - horizon_y)
        rw = int(refl_w * (1 + t * 1.5))
        draw.line([(cx - rw, ry), (cx + rw, ry)], fill=refl_color, width=2)

    # Gentle water waves
    wave_color = hex_to_rgb(colors[2])
    for i in range(3):
        wy = horizon_y + int((height - horizon_y) * (i + 1) / 4)
        _wavy_band(draw, width, height, wy, 4, 0.018, wave_color)


def generate_nature_forest(draw, width, height, colors, rng):
    """Generate forest scene"""
    _sky_gradient(draw, width, height, colors)

    # Ground
    ground_y = int(height * 0.7)
    ground_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=ground_color)

    # Trees
    num_trees = rng.randint(8, 15)
    for _ in range(num_trees):
        tree_x = rng.randint(0, width)
        tree_h = rng.randint(int(height * 0.2), int(height * 0.4))
        tree_color = hex_to_rgb(colors[3 % len(colors)])

        # Trunk
        trunk_w = int(width * 0.01)
        draw.rectangle([tree_x - trunk_w, ground_y - tree_h, tree_x + trunk_w, ground_y], fill=tree_color)

        # Leaves
        leaf_y = ground_y - tree_h
        leaf_r = int(width * 0.05)
        leaf_color = hex_to_rgb(colors[4 % len(colors)])
        draw.ellipse([tree_x - leaf_r, leaf_y - leaf_r * 2, tree_x + leaf_r, leaf_y], fill=leaf_color)


def generate_nature_jungle(draw, width, height, colors, rng):
    """Generate dense jungle scene with layered canopy"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.75)
    ground_color = hex_to_rgb(colors[2])
    draw.rectangle([0, ground_y, width, height], fill=ground_color)

    # Layered canopy silhouettes, denser than forest
    for layer in range(3):
        layer_y = int(height * (0.3 + layer * 0.1))
        color = hex_to_rgb(colors[(layer + 2) % len(colors)])
        amplitude = rng.randint(20, 40)
        frequency = rng.uniform(0.01, 0.02)
        points = []
        for x in range(width):
            offset = math.sin(x * frequency + layer) * amplitude
            points.append((x, int(layer_y + offset)))
        draw.polygon(points + [(width, ground_y), (0, ground_y)], fill=color)

    # Large leaf silhouettes in foreground
    leaf_color = hex_to_rgb(colors[3])
    for _ in range(rng.randint(6, 10)):
        lx = rng.randint(0, width)
        ly = rng.randint(int(ground_y * 0.9), ground_y)
        lw = rng.randint(int(width * 0.04), int(width * 0.08))
        lh = int(lw * 0.4)
        draw.ellipse([lx - lw, ly - lh, lx + lw, ly + lh], fill=leaf_color)


def generate_nature_ocean(draw, width, height, colors, rng):
    """Generate open ocean scene with layered waves"""
    _sky_gradient(draw, width, height, colors)

    horizon_y = int(height * 0.45)
    for i in range(6):
        wave_y = horizon_y + int((height - horizon_y) * i / 6)
        color = hex_to_rgb(colors[(i + 1) % len(colors)])
        amplitude = rng.randint(6, 18)
        frequency = rng.uniform(0.008, 0.02)
        _wavy_band(draw, width, height, wave_y, amplitude, frequency, color)


def generate_nature_waterfall(draw, width, height, colors, rng):
    """Generate a realistic waterfall scene: sky, rocky cliffs, narrow falling water, mist pool, greenery"""
    # Sky
    _sky_gradient(draw, width, height, colors)

    cx = width // 2
    fall_w = int(width * 0.12)          # narrow waterfall column
    cliff_top_y = int(height * 0.18)    # top of the cliff / waterfall origin
    fall_bottom_y = int(height * 0.72)  # where water hits the pool
    ground_y = int(height * 0.85)

    rock_color   = hex_to_rgb(colors[2])
    water_color  = hex_to_rgb(colors[0])
    foam_color   = hex_to_rgb(colors[5] if len(colors) > 5 else colors[-1])
    green_color  = hex_to_rgb(colors[3])
    pool_color   = hex_to_rgb(colors[1])
    mist_color   = hex_to_rgb(colors[4] if len(colors) > 4 else colors[-1])

    # ── Rocky cliff plateau (top ledge spanning full width) ──
    draw.rectangle([0, cliff_top_y, width, cliff_top_y + int(height * 0.08)], fill=rock_color)

    # ── Left cliff wall (rocky face, slightly irregular) ──
    left_wall_x = cx - fall_w // 2
    for i in range(6):
        seg_y = cliff_top_y + int(height * 0.08) + i * int((fall_bottom_y - cliff_top_y - int(height * 0.08)) / 6)
        seg_h = int((fall_bottom_y - cliff_top_y - int(height * 0.08)) / 6) + 2
        jut = rng.randint(-int(width * 0.015), int(width * 0.01))
        draw.rectangle([0, seg_y, left_wall_x + jut, seg_y + seg_h], fill=rock_color)

    # ── Right cliff wall ──
    right_wall_x = cx + fall_w // 2
    for i in range(6):
        seg_y = cliff_top_y + int(height * 0.08) + i * int((fall_bottom_y - cliff_top_y - int(height * 0.08)) / 6)
        seg_h = int((fall_bottom_y - cliff_top_y - int(height * 0.08)) / 6) + 2
        jut = rng.randint(-int(width * 0.01), int(width * 0.015))
        draw.rectangle([right_wall_x + jut, seg_y, width, seg_y + seg_h], fill=rock_color)

    # ── Ground below cliff ──
    draw.rectangle([0, ground_y, width, height], fill=rock_color)

    # ── Greenery on cliff edges ──
    for side in [0, 1]:
        base_x = 0 if side == 0 else right_wall_x
        end_x  = left_wall_x if side == 0 else width
        for _ in range(rng.randint(8, 14)):
            gx = rng.randint(base_x, end_x)
            gy = rng.randint(cliff_top_y - int(height * 0.06), cliff_top_y + int(height * 0.04))
            gr = rng.randint(int(width * 0.02), int(width * 0.05))
            draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr // 2], fill=green_color)

    # ── Waterfall column — gradient from top (lighter) to bottom (darker) ──
    for y in range(cliff_top_y + int(height * 0.08), fall_bottom_y):
        t = (y - cliff_top_y) / (fall_bottom_y - cliff_top_y)
        r = int(water_color[0] * (1 - t * 0.3))
        g = int(water_color[1] * (1 - t * 0.3))
        b = int(water_color[2] * (1 - t * 0.3))
        draw.line([(cx - fall_w // 2, y), (cx + fall_w // 2, y)], fill=(r, g, b))

    # ── Vertical foam streaks inside the fall ──
    for _ in range(rng.randint(18, 30)):
        sx = rng.randint(cx - fall_w // 2 + 2, cx + fall_w // 2 - 2)
        sy = rng.randint(cliff_top_y + int(height * 0.08), fall_bottom_y - int(height * 0.05))
        sh = rng.randint(int(height * 0.04), int(height * 0.12))
        draw.line([(sx, sy), (sx, sy + sh)], fill=foam_color, width=rng.randint(1, 3))

    # ── Mist / spray cloud at base ──
    mist_cx = cx
    mist_cy = fall_bottom_y + int(height * 0.03)
    for _ in range(rng.randint(20, 35)):
        mx = rng.randint(mist_cx - int(width * 0.12), mist_cx + int(width * 0.12))
        my = rng.randint(fall_bottom_y - int(height * 0.02), fall_bottom_y + int(height * 0.06))
        mr = rng.randint(int(width * 0.015), int(width * 0.04))
        draw.ellipse([mx - mr, my - mr // 2, mx + mr, my + mr // 2], fill=mist_color)

    # ── Pool at base ──
    pool_x0 = cx - int(width * 0.18)
    pool_x1 = cx + int(width * 0.18)
    pool_y0 = fall_bottom_y + int(height * 0.02)
    pool_y1 = ground_y
    draw.ellipse([pool_x0, pool_y0, pool_x1, pool_y1], fill=pool_color)

    # ── Pool ripple rings ──
    for i in range(1, 4):
        rx = int(width * 0.04 * i)
        ry = int(height * 0.01 * i)
        ric_y = pool_y0 + (pool_y1 - pool_y0) // 2
        draw.ellipse([cx - rx, ric_y - ry, cx + rx, ric_y + ry], outline=foam_color, width=1)

    # ── Foam cap at top of fall (where water spills over ledge) ──
    foam_top_y = cliff_top_y + int(height * 0.07)
    draw.ellipse([cx - fall_w, foam_top_y - int(height * 0.015),
                  cx + fall_w, foam_top_y + int(height * 0.015)], fill=foam_color)


def generate_nature_volcano(draw, width, height, colors, rng):
    """Generate erupting volcano scene"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.85)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[4] if len(colors) > 4 else colors[0]))

    # Volcano cone
    cx = width // 2
    cone_color = hex_to_rgb(colors[0])
    peak_y = int(height * 0.35)
    draw.polygon([
        (cx - int(width * 0.3), ground_y),
        (cx, peak_y),
        (cx + int(width * 0.3), ground_y),
    ], fill=cone_color)

    # Lava streaks down the cone
    lava_color = hex_to_rgb(colors[1])
    for _ in range(rng.randint(3, 5)):
        offset = rng.randint(-int(width * 0.15), int(width * 0.15))
        draw.line([(cx + offset * 0.2, peak_y + 20), (cx + offset, ground_y)], fill=lava_color, width=4)

    # Eruption plume and glow
    plume_color = hex_to_rgb(colors[2])
    for i in range(6):
        r = int(width * 0.02) + i * 4
        py = peak_y - i * 15
        draw.ellipse([cx - r, py - r, cx + r, py + r], fill=plume_color)

    glow_color = hex_to_rgb(colors[3])
    draw.ellipse([cx - 15, peak_y - 10, cx + 15, peak_y + 10], fill=glow_color)


def generate_nature_storm(draw, width, height, colors, rng):
    """Generate storm scene with dark clouds and lightning"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.8)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    # Dark rolling clouds
    cloud_color = hex_to_rgb(colors[3])
    for i in range(4):
        cloud_y = int(height * (0.15 + i * 0.08))
        amplitude = rng.randint(15, 35)
        frequency = rng.uniform(0.005, 0.012)
        points = []
        for x in range(width):
            offset = math.sin(x * frequency + i) * amplitude
            points.append((x, int(cloud_y + offset)))
        draw.polygon(points + [(width, 0), (0, 0)], fill=cloud_color)

    # Lightning bolt
    bolt_color = hex_to_rgb(colors[4] if len(colors) > 4 else colors[-1])
    bolt_x = rng.randint(int(width * 0.3), int(width * 0.7))
    segments = [(bolt_x, int(height * 0.3))]
    y = int(height * 0.3)
    x = bolt_x
    while y < ground_y:
        x += rng.randint(-25, 25)
        y += rng.randint(30, 50)
        segments.append((x, min(y, ground_y)))
    draw.line(segments, fill=bolt_color, width=3)

    # Rain streaks
    rain_color = hex_to_rgb(colors[5] if len(colors) > 5 else colors[-1])
    for _ in range(rng.randint(40, 70)):
        rx = rng.randint(0, width)
        ry = rng.randint(0, ground_y)
        draw.line([(rx, ry), (rx - 8, ry + 20)], fill=rain_color, width=1)


def generate_nature_cave(draw, width, height, colors, rng):
    """Dark cave interior with stalactites, stalagmites, glowing crystals, and a distant light opening"""
    # Dark background
    bg = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg)

    rock_color    = hex_to_rgb(colors[2])
    dark_color    = hex_to_rgb(colors[1])
    crystal_color = hex_to_rgb(colors[4 % len(colors)])
    glow_color    = hex_to_rgb(colors[5 % len(colors)])
    floor_color   = hex_to_rgb(colors[3])

    # Cave walls — irregular left and right rock faces
    for side in [0, 1]:
        pts = [(0 if side == 0 else width, 0)]
        for y in range(0, height + 1, int(height / 10)):
            jut = rng.randint(int(width * 0.08), int(width * 0.28))
            pts.append((jut if side == 0 else width - jut, y))
        pts.append((0 if side == 0 else width, height))
        draw.polygon(pts, fill=rock_color)

    # Cave ceiling — jagged rock band across top
    ceil_pts = [(0, 0)]
    for x in range(0, width + 1, int(width / 14)):
        ch = rng.randint(int(height * 0.05), int(height * 0.22))
        ceil_pts.append((x, ch))
    ceil_pts.append((width, 0))
    draw.polygon(ceil_pts, fill=rock_color)

    # Cave floor
    floor_pts = [(0, height)]
    for x in range(0, width + 1, int(width / 12)):
        fh = rng.randint(int(height * 0.78), int(height * 0.92))
        floor_pts.append((x, fh))
    floor_pts.append((width, height))
    draw.polygon(floor_pts, fill=floor_color)

    # Stalactites hanging from ceiling
    for _ in range(rng.randint(6, 10)):
        sx = rng.randint(int(width * 0.15), int(width * 0.85))
        sy = rng.randint(int(height * 0.05), int(height * 0.18))
        sh = rng.randint(int(height * 0.08), int(height * 0.22))
        sw = rng.randint(int(width * 0.012), int(width * 0.025))
        draw.polygon([(sx - sw, sy), (sx + sw, sy), (sx, sy + sh)], fill=dark_color)

    # Stalagmites rising from floor
    for _ in range(rng.randint(5, 8)):
        sx = rng.randint(int(width * 0.15), int(width * 0.85))
        sy = int(height * 0.85)
        sh = rng.randint(int(height * 0.06), int(height * 0.18))
        sw = rng.randint(int(width * 0.01), int(width * 0.022))
        draw.polygon([(sx - sw, sy), (sx + sw, sy), (sx, sy - sh)], fill=dark_color)

    # Glowing crystals on floor/walls
    for _ in range(rng.randint(8, 14)):
        cx = rng.randint(int(width * 0.1), int(width * 0.9))
        cy = rng.randint(int(height * 0.55), int(height * 0.82))
        cr = rng.randint(int(width * 0.008), int(width * 0.02))
        draw.ellipse([cx - cr * 2, cy - cr, cx + cr * 2, cy + cr], fill=crystal_color)

    # Distant cave opening — bright ellipse in center
    open_cx, open_cy = width // 2, int(height * 0.45)
    for i in range(5, 0, -1):
        or_ = int(width * 0.04) * i
        ory = int(height * 0.06) * i
        blend = tuple(int(bg[j] * (1 - i / 6) + glow_color[j] * (i / 6)) for j in range(3))
        draw.ellipse([open_cx - or_, open_cy - ory, open_cx + or_, open_cy + ory], fill=blend)


def generate_nature_hot_spring(draw, width, height, colors, rng):
    """Steaming hot spring pool surrounded by snow-dusted rocks and pine silhouettes"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.72)
    snow_color  = hex_to_rgb(colors[5 % len(colors)])
    rock_color  = hex_to_rgb(colors[2])
    water_color = hex_to_rgb(colors[1])
    steam_color = hex_to_rgb(colors[3])
    tree_color  = hex_to_rgb(colors[3])

    # Snowy ground
    draw.rectangle([0, ground_y, width, height], fill=snow_color)

    # Rocky rim around the pool
    pool_cx, pool_cy = width // 2, int(height * 0.78)
    pool_rx, pool_ry = int(width * 0.28), int(height * 0.1)
    rim_color = rock_color
    draw.ellipse([pool_cx - pool_rx - 12, pool_cy - pool_ry - 8,
                  pool_cx + pool_rx + 12, pool_cy + pool_ry + 8], fill=rim_color)

    # Hot spring water — glowing teal pool
    draw.ellipse([pool_cx - pool_rx, pool_cy - pool_ry,
                  pool_cx + pool_rx, pool_cy + pool_ry], fill=water_color)

    # Ripple rings in pool
    for i in range(1, 4):
        draw.ellipse([pool_cx - int(pool_rx * i / 4), pool_cy - int(pool_ry * i / 4),
                      pool_cx + int(pool_rx * i / 4), pool_cy + int(pool_ry * i / 4)],
                     outline=steam_color, width=1)

    # Steam wisps rising from pool
    for _ in range(rng.randint(10, 18)):
        sx = rng.randint(pool_cx - pool_rx + 10, pool_cx + pool_rx - 10)
        sy = pool_cy - pool_ry
        for seg in range(rng.randint(4, 7)):
            nx = sx + rng.randint(-8, 8)
            ny = sy - rng.randint(12, 22)
            draw.line([(sx, sy), (nx, ny)], fill=steam_color, width=2)
            sx, sy = nx, ny

    # Snow-capped rocks around pool
    for _ in range(rng.randint(5, 8)):
        rx = rng.randint(int(width * 0.05), int(width * 0.9))
        ry = rng.randint(ground_y - int(height * 0.04), ground_y + int(height * 0.06))
        rr = rng.randint(int(width * 0.02), int(width * 0.05))
        draw.ellipse([rx - rr, ry - rr // 2, rx + rr, ry + rr // 2], fill=rock_color)
        draw.ellipse([rx - rr, ry - rr // 2, rx + rr, ry], fill=snow_color)

    # Pine tree silhouettes on sides
    for side in [0, 1]:
        for i in range(rng.randint(2, 4)):
            tx = rng.randint(int(width * (0.02 + side * 0.6)), int(width * (0.35 + side * 0.6)))
            th = rng.randint(int(height * 0.18), int(height * 0.32))
            draw.line([(tx, ground_y), (tx, ground_y - th)], fill=tree_color, width=3)
            for tier in range(3):
                tw = int(width * 0.04) - tier * int(width * 0.01)
                ty = ground_y - int(th * (0.4 + tier * 0.2))
                draw.polygon([(tx - tw, ty + int(height * 0.04)),
                               (tx, ty), (tx + tw, ty + int(height * 0.04))], fill=tree_color)


def generate_nature_coral_reef(draw, width, height, colors, rng):
    """Underwater coral reef scene with corals, fish silhouettes, and light rays"""
    # Deep water gradient background
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)],
                  fill=tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))

    sand_color   = hex_to_rgb(colors[3])
    coral_colors = [hex_to_rgb(colors[i % len(colors)]) for i in range(2, 5)]
    fish_color   = hex_to_rgb(colors[4 % len(colors)])
    ray_color    = hex_to_rgb(colors[5 % len(colors)])

    # Light rays from surface
    for _ in range(rng.randint(5, 8)):
        rx = rng.randint(int(width * 0.1), int(width * 0.9))
        ray_w = rng.randint(int(width * 0.02), int(width * 0.06))
        draw.polygon([(rx - ray_w, 0), (rx + ray_w, 0),
                      (rx + ray_w * 3, height), (rx - ray_w * 3, height)], fill=ray_color)

    # Sandy seabed
    ground_y = int(height * 0.82)
    draw.rectangle([0, ground_y, width, height], fill=sand_color)
    # Sand ripples
    for i in range(3):
        ry = ground_y + int((height - ground_y) * (i + 1) / 4)
        _wavy_band(draw, width, height, ry, 3, 0.02, hex_to_rgb(colors[2]))

    # Coral formations
    for _ in range(rng.randint(10, 16)):
        cx = rng.randint(int(width * 0.03), int(width * 0.97))
        cy = ground_y
        ch = rng.randint(int(height * 0.08), int(height * 0.28))
        cw = rng.randint(int(width * 0.01), int(width * 0.025))
        cc = rng.choice(coral_colors)
        kind = rng.choice(["branch", "fan", "dome"])
        if kind == "branch":
            # Branching coral
            draw.line([(cx, cy), (cx, cy - ch)], fill=cc, width=max(2, cw))
            for b in range(rng.randint(2, 4)):
                bx = cx + rng.randint(-int(width * 0.03), int(width * 0.03))
                by = cy - int(ch * rng.uniform(0.4, 0.8))
                draw.line([(cx, by), (bx, by - int(ch * 0.3))], fill=cc, width=max(1, cw // 2))
        elif kind == "fan":
            # Fan coral — wide flat ellipse
            draw.ellipse([cx - int(width * 0.04), cy - ch, cx + int(width * 0.04), cy], fill=cc)
        else:
            # Dome coral
            draw.ellipse([cx - int(width * 0.03), cy - int(ch * 0.5),
                          cx + int(width * 0.03), cy], fill=cc)

    # Fish silhouettes
    for _ in range(rng.randint(6, 12)):
        fx = rng.randint(int(width * 0.05), int(width * 0.95))
        fy = rng.randint(int(height * 0.15), int(height * 0.7))
        fs = rng.randint(int(width * 0.015), int(width * 0.035))
        # Body ellipse
        draw.ellipse([fx - fs, fy - fs // 2, fx + fs, fy + fs // 2], fill=fish_color)
        # Tail
        draw.polygon([(fx + fs, fy), (fx + int(fs * 1.5), fy - fs // 2),
                      (fx + int(fs * 1.5), fy + fs // 2)], fill=fish_color)


def generate_nature_dunes_night(draw, width, height, colors, rng):
    """Desert sand dunes under a star-filled night sky with a crescent moon"""
    _sky_gradient(draw, width, height, colors)

    # Stars
    star_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(120, 200)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, int(height * 0.65))
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=star_color)

    # Crescent moon
    moon_cx, moon_cy = int(width * 0.78), int(height * 0.18)
    moon_r = int(width * 0.06)
    moon_color = hex_to_rgb(colors[4 % len(colors)])
    draw.ellipse([moon_cx - moon_r, moon_cy - moon_r,
                  moon_cx + moon_r, moon_cy + moon_r], fill=moon_color)
    # Bite out of moon to make crescent
    sky_color = hex_to_rgb(colors[0])
    draw.ellipse([moon_cx - moon_r + int(moon_r * 0.4), moon_cy - moon_r,
                  moon_cx + moon_r + int(moon_r * 0.4), moon_cy + moon_r], fill=sky_color)

    # Dune layers — smooth sine waves, lit on one side
    num_dunes = rng.randint(4, 6)
    for i in range(num_dunes):
        dune_y = int(height * (0.55 + i * 0.06))
        t = i / num_dunes
        r = int(hex_to_rgb(colors[3])[0] * (1 - t) + hex_to_rgb(colors[2])[0] * t)
        g = int(hex_to_rgb(colors[3])[1] * (1 - t) + hex_to_rgb(colors[2])[1] * t)
        b = int(hex_to_rgb(colors[3])[2] * (1 - t) + hex_to_rgb(colors[2])[2] * t)
        amplitude = rng.randint(18, 45)
        frequency = rng.uniform(0.003, 0.007)
        _wavy_band(draw, width, height, dune_y, amplitude, frequency, (r, g, b))

    # Dune crest highlight (moonlit edge)
    crest_color = hex_to_rgb(colors[4 % len(colors)])
    for i in range(num_dunes):
        dune_y = int(height * (0.55 + i * 0.06))
        for x in range(0, width, 3):
            cy = int(dune_y + math.sin(x * 0.005) * 30)
            draw.line([(x, cy), (x + 3, cy)], fill=crest_color, width=1)


def generate_nature_mangrove(draw, width, height, colors, rng):
    """Mangrove forest with arching prop roots, still tidal water, and dense canopy"""
    _sky_gradient(draw, width, height, colors)

    water_y = int(height * 0.62)
    water_color  = hex_to_rgb(colors[4 % len(colors)])
    mud_color    = hex_to_rgb(colors[2])
    trunk_color  = hex_to_rgb(colors[1])
    canopy_color = hex_to_rgb(colors[0])
    root_color   = hex_to_rgb(colors[3])

    # Still tidal water
    draw.rectangle([0, water_y, width, height], fill=water_color)

    # Muddy banks at edges
    draw.rectangle([0, water_y + int(height * 0.12), int(width * 0.18), height], fill=mud_color)
    draw.rectangle([int(width * 0.82), water_y + int(height * 0.12), width, height], fill=mud_color)

    # Water surface ripples
    ripple_color = hex_to_rgb(colors[5 % len(colors)])
    for i in range(3):
        ry = water_y + int((height - water_y) * (i + 1) / 5)
        _wavy_band(draw, width, height, ry, 3, 0.016, ripple_color)

    # Mangrove trees
    num_trees = rng.randint(5, 8)
    for i in range(num_trees):
        tx = int(width * (i + 0.5) / num_trees) + rng.randint(-int(width * 0.04), int(width * 0.04))
        trunk_base = water_y + int(height * 0.04)
        trunk_top  = water_y - rng.randint(int(height * 0.18), int(height * 0.32))

        # Main trunk
        draw.line([(tx, trunk_base), (tx, trunk_top)], fill=trunk_color, width=5)

        # Arching prop roots (3–5 per tree)
        for _ in range(rng.randint(3, 5)):
            root_spread = rng.randint(int(width * 0.04), int(width * 0.09))
            side = rng.choice([-1, 1])
            root_end_x = tx + side * root_spread
            root_end_y = trunk_base + rng.randint(int(height * 0.02), int(height * 0.06))
            mid_x = tx + side * root_spread // 2
            mid_y = trunk_base - int(height * 0.04)
            draw.line([(tx, trunk_base - int(height * 0.06)),
                        (mid_x, mid_y), (root_end_x, root_end_y)],
                      fill=root_color, width=2)

        # Canopy blob
        canopy_r = rng.randint(int(width * 0.06), int(width * 0.1))
        draw.ellipse([tx - canopy_r, trunk_top - canopy_r,
                      tx + canopy_r, trunk_top + canopy_r // 2], fill=canopy_color)
        # Second canopy layer (slightly offset)
        draw.ellipse([tx - int(canopy_r * 0.7) + rng.randint(-8, 8),
                      trunk_top - int(canopy_r * 0.6),
                      tx + int(canopy_r * 0.7) + rng.randint(-8, 8),
                      trunk_top + canopy_r // 3],
                     fill=hex_to_rgb(colors[(i + 1) % len(colors)]))

    # Reflection of canopy in water
    refl_color = hex_to_rgb(colors[0])
    for i in range(num_trees):
        tx = int(width * (i + 0.5) / num_trees)
        rw = int(width * 0.07)
        rh = int(height * 0.06)
        draw.ellipse([tx - rw, water_y + int(height * 0.01),
                      tx + rw, water_y + rh], fill=refl_color)


def generate_urban_neon_city(draw, width, height, colors, rng):
    """Generate neon city scene"""
    _sky_gradient(draw, width, height, colors)

    # Buildings
    num_buildings = rng.randint(6, 10)
    building_width = width // num_buildings

    for i in range(num_buildings):
        b_x = i * building_width
        b_h = rng.randint(int(height * 0.2), int(height * 0.6))
        b_y = height - b_h

        # Building body
        b_color = hex_to_rgb(colors[2])
        draw.rectangle([b_x, b_y, b_x + building_width, height], fill=b_color)

        # Windows
        win_color = hex_to_rgb(colors[3])
        win_w = building_width // 4
        win_h = int(height * 0.05)

        for wy in range(b_y + int(height * 0.1), height - int(height * 0.1), win_h * 2):
            for wx in range(b_x + 5, b_x + building_width - 5, win_w * 2):
                if rng.random() > 0.3:
                    draw.rectangle([wx, wy, wx + win_w - 2, wy + win_h - 2], fill=win_color)


def generate_urban_skyline(draw, width, height, colors, rng):
    """Generate a classic/minimalist city skyline silhouette"""
    _sky_gradient(draw, width, height, colors)

    ground_y = height
    num_buildings = rng.randint(8, 14)
    building_width = width // num_buildings

    for i in range(num_buildings):
        b_x = i * building_width
        b_h = rng.randint(int(height * 0.15), int(height * 0.55))
        b_y = ground_y - b_h
        color = hex_to_rgb(colors[(i + 2) % len(colors)])
        draw.rectangle([b_x, b_y, b_x + building_width - 2, ground_y], fill=color)

        # A few simple square windows
        win_color = hex_to_rgb(colors[(i + 4) % len(colors)])
        win_size = max(2, building_width // 8)
        for wy in range(b_y + win_size, ground_y - win_size, win_size * 2):
            for wx in range(b_x + win_size, b_x + building_width - win_size, win_size * 2):
                draw.rectangle([wx, wy, wx + win_size, wy + win_size], fill=win_color)


def generate_urban_geometric(draw, width, height, colors, rng):
    """Generate an abstract geometric grid scene"""
    _sky_gradient(draw, width, height, colors)

    cols = rng.randint(6, 10)
    rows = rng.randint(4, 7)
    cell_w = width / cols
    cell_h = height / rows

    for row in range(rows):
        for col in range(cols):
            if rng.random() > 0.4:
                color = hex_to_rgb(colors[(row + col) % len(colors)])
                x0 = int(col * cell_w)
                y0 = int(row * cell_h)
                x1 = int(x0 + cell_w)
                y1 = int(y0 + cell_h)
                if rng.random() > 0.5:
                    draw.rectangle([x0, y0, x1, y1], fill=color)
                else:
                    draw.ellipse([x0, y0, x1, y1], fill=color)

    # Grid lines on top
    line_color = hex_to_rgb(colors[-1])
    for col in range(cols + 1):
        x = int(col * cell_w)
        draw.line([(x, 0), (x, height)], fill=line_color, width=1)
    for row in range(rows + 1):
        y = int(row * cell_h)
        draw.line([(0, y), (width, y)], fill=line_color, width=1)


def generate_urban_modern_art(draw, width, height, colors, rng):
    """Generate an abstract modern-art style scene with bold overlapping shapes"""
    bg_color = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg_color)

    num_shapes = rng.randint(10, 18)
    for i in range(num_shapes):
        color = hex_to_rgb(colors[(i + 1) % len(colors)])
        shape_kind = rng.choice(["circle", "rect", "triangle"])
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        size = rng.randint(int(width * 0.05), int(width * 0.25))

        if shape_kind == "circle":
            draw.ellipse([cx - size, cy - size, cx + size, cy + size], fill=color)
        elif shape_kind == "rect":
            angle_w = size
            angle_h = int(size * rng.uniform(0.4, 1.2))
            draw.rectangle([cx - angle_w, cy - angle_h, cx + angle_w, cy + angle_h], fill=color)
        else:
            draw.polygon([
                (cx, cy - size),
                (cx - size, cy + size),
                (cx + size, cy + size),
            ], fill=color)


def generate_urban_rooftop_garden(draw, width, height, colors, rng):
    """Rooftop garden with city skyline backdrop, planters, and greenery"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.88)
    roof_color   = hex_to_rgb(colors[2])
    plant_color  = hex_to_rgb(colors[3])
    accent_color = hex_to_rgb(colors[4 % len(colors)])
    sky_bld_color = hex_to_rgb(colors[1])

    # Distant city skyline silhouette
    num_bld = rng.randint(8, 14)
    for i in range(num_bld):
        bx = int(width * i / num_bld)
        bh = rng.randint(int(height * 0.12), int(height * 0.38))
        bw = width // num_bld - 2
        draw.rectangle([bx, ground_y - bh, bx + bw, ground_y], fill=sky_bld_color)
        # Windows
        win_color = hex_to_rgb(colors[5 % len(colors)])
        ws = max(2, bw // 5)
        for wy in range(ground_y - bh + ws, ground_y - ws, ws * 2):
            for wx in range(bx + ws, bx + bw - ws, ws * 2):
                if rng.random() > 0.4:
                    draw.rectangle([wx, wy, wx + ws, wy + ws], fill=win_color)

    # Rooftop floor
    draw.rectangle([0, ground_y, width, height], fill=roof_color)
    # Floor tiles
    tile_color = hex_to_rgb(colors[3])
    tile_size = int(width * 0.06)
    for tx in range(0, width, tile_size):
        draw.line([(tx, ground_y), (tx, height)], fill=tile_color, width=1)
    for ty in range(ground_y, height, tile_size):
        draw.line([(0, ty), (width, ty)], fill=tile_color, width=1)

    # Planter boxes
    for i in range(rng.randint(3, 5)):
        px = rng.randint(int(width * 0.05), int(width * 0.85))
        pw = rng.randint(int(width * 0.08), int(width * 0.14))
        ph = int(height * 0.04)
        py = ground_y - ph
        draw.rectangle([px, py, px + pw, ground_y], fill=accent_color)
        # Plants in planter
        for _ in range(rng.randint(2, 4)):
            gx = rng.randint(px + 4, px + pw - 4)
            gh = rng.randint(int(height * 0.04), int(height * 0.1))
            draw.line([(gx, py), (gx, py - gh)], fill=plant_color, width=2)
            cr = rng.randint(int(width * 0.015), int(width * 0.03))
            draw.ellipse([gx - cr, py - gh - cr, gx + cr, py - gh + cr // 2], fill=plant_color)

    # Standalone potted plants
    for _ in range(rng.randint(3, 6)):
        px = rng.randint(int(width * 0.05), int(width * 0.9))
        pot_h = int(height * 0.03)
        pot_w = int(width * 0.025)
        draw.polygon([(px - pot_w, ground_y), (px + pot_w, ground_y),
                       (px + int(pot_w * 0.7), ground_y - pot_h),
                       (px - int(pot_w * 0.7), ground_y - pot_h)], fill=accent_color)
        gh = rng.randint(int(height * 0.05), int(height * 0.12))
        draw.line([(px, ground_y - pot_h), (px, ground_y - pot_h - gh)], fill=plant_color, width=2)
        cr = rng.randint(int(width * 0.02), int(width * 0.035))
        draw.ellipse([px - cr, ground_y - pot_h - gh - cr,
                      px + cr, ground_y - pot_h - gh + cr // 2], fill=plant_color)


def generate_urban_subway(draw, width, height, colors, rng):
    """Underground subway station with platform, train, and overhead lights"""
    bg_color = hex_to_rgb(colors[0])
    draw.rectangle([0, 0, width, height], fill=bg_color)

    wall_color    = hex_to_rgb(colors[1])
    tile_color    = hex_to_rgb(colors[2])
    platform_color = hex_to_rgb(colors[3])
    train_color   = hex_to_rgb(colors[2])
    accent_color  = hex_to_rgb(colors[3])
    light_color   = hex_to_rgb(colors[4 % len(colors)])
    sign_color    = hex_to_rgb(colors[5 % len(colors)])

    platform_y = int(height * 0.65)
    track_y    = int(height * 0.82)

    # Tunnel walls and ceiling
    draw.rectangle([0, 0, width, platform_y], fill=wall_color)

    # Wall tiles
    tile_w, tile_h = int(width * 0.05), int(height * 0.06)
    for tx in range(0, width, tile_w):
        for ty in range(0, platform_y, tile_h):
            if (tx // tile_w + ty // tile_h) % 2 == 0:
                draw.rectangle([tx + 1, ty + 1, tx + tile_w - 1, ty + tile_h - 1], fill=tile_color)

    # Overhead lights
    for lx in range(int(width * 0.1), width, int(width * 0.18)):
        draw.rectangle([lx - int(width * 0.02), int(height * 0.04),
                         lx + int(width * 0.02), int(height * 0.08)], fill=light_color)
        # Light cone
        draw.polygon([(lx - int(width * 0.02), int(height * 0.08)),
                       (lx + int(width * 0.02), int(height * 0.08)),
                       (lx + int(width * 0.06), platform_y),
                       (lx - int(width * 0.06), platform_y)],
                     fill=tuple(min(255, c + 30) for c in bg_color))

    # Platform
    draw.rectangle([0, platform_y, width, track_y], fill=platform_color)
    # Platform edge stripe
    draw.rectangle([0, platform_y, width, platform_y + int(height * 0.015)], fill=sign_color)

    # Track bed
    draw.rectangle([0, track_y, width, height], fill=bg_color)
    # Rails
    rail_color = hex_to_rgb(colors[2])
    for rx in [int(width * 0.3), int(width * 0.7)]:
        draw.line([(rx, track_y), (rx, height)], fill=rail_color, width=3)
    # Sleepers
    for sy in range(track_y, height, int(height * 0.04)):
        draw.line([(int(width * 0.28), sy), (int(width * 0.72), sy)], fill=rail_color, width=2)

    # Train on the right side
    train_x = int(width * 0.55)
    train_top = int(height * 0.28)
    train_w = int(width * 0.42)
    train_h = platform_y - train_top
    draw.rectangle([train_x, train_top, train_x + train_w, platform_y], fill=train_color)
    # Train stripe
    draw.rectangle([train_x, train_top + int(train_h * 0.3),
                     train_x + train_w, train_top + int(train_h * 0.45)], fill=accent_color)
    # Windows
    win_color = hex_to_rgb(colors[4 % len(colors)])
    for i in range(3):
        wx = train_x + int(train_w * (i + 0.3) / 3.5)
        draw.rectangle([wx, train_top + int(train_h * 0.1),
                         wx + int(train_w * 0.12), train_top + int(train_h * 0.28)], fill=win_color)
    # Train doors
    draw.rectangle([train_x + int(train_w * 0.45), train_top + int(train_h * 0.35),
                     train_x + int(train_w * 0.55), platform_y], fill=win_color)

    # Station sign
    draw.rectangle([int(width * 0.05), int(height * 0.12),
                     int(width * 0.35), int(height * 0.22)], fill=sign_color)


def generate_urban_night_market(draw, width, height, colors, rng):
    """Bustling night market with lanterns, stalls, and glowing signs"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.78)
    ground_color  = hex_to_rgb(colors[1])
    stall_color   = hex_to_rgb(colors[2])
    lantern_color = hex_to_rgb(colors[3])
    glow_color    = hex_to_rgb(colors[4 % len(colors)])
    sign_color    = hex_to_rgb(colors[5 % len(colors)])

    # Ground / street
    draw.rectangle([0, ground_y, width, height], fill=ground_color)
    # Street reflection puddles
    for _ in range(rng.randint(3, 6)):
        px = rng.randint(int(width * 0.05), int(width * 0.85))
        pw = rng.randint(int(width * 0.06), int(width * 0.14))
        draw.ellipse([px, ground_y + int(height * 0.02),
                       px + pw, ground_y + int(height * 0.05)],
                     fill=tuple(min(255, c + 40) for c in ground_color))

    # Market stalls
    num_stalls = rng.randint(4, 6)
    for i in range(num_stalls):
        sx = int(width * i / num_stalls) + rng.randint(0, int(width * 0.04))
        sw = int(width / num_stalls) - int(width * 0.02)
        sh = rng.randint(int(height * 0.18), int(height * 0.28))
        stall_top = ground_y - sh
        draw.rectangle([sx, stall_top, sx + sw, ground_y], fill=stall_color)
        # Awning
        aw_color = hex_to_rgb(colors[(i + 2) % len(colors)])
        draw.polygon([(sx - int(sw * 0.05), stall_top),
                       (sx + sw + int(sw * 0.05), stall_top),
                       (sx + sw + int(sw * 0.1), stall_top + int(height * 0.05)),
                       (sx - int(sw * 0.1), stall_top + int(height * 0.05))], fill=aw_color)
        # Stall goods (small rectangles)
        for _ in range(rng.randint(3, 6)):
            gx = rng.randint(sx + 4, sx + sw - 8)
            gy = rng.randint(stall_top + int(height * 0.08), ground_y - int(height * 0.02))
            draw.rectangle([gx, gy, gx + int(sw * 0.2), gy + int(height * 0.04)],
                           fill=glow_color)

    # String of lanterns across the top
    rope_y = int(height * 0.18)
    draw.line([(0, rope_y), (width, rope_y)], fill=stall_color, width=2)
    for lx in range(int(width * 0.04), width, int(width * 0.07)):
        # Rope droop
        draw.line([(lx, rope_y), (lx + int(width * 0.035), rope_y + int(height * 0.03))],
                  fill=stall_color, width=1)
        # Lantern body
        lw, lh = int(width * 0.025), int(height * 0.055)
        ly = rope_y + int(height * 0.03)
        lc = hex_to_rgb(colors[(lx // int(width * 0.07) + 2) % len(colors)])
        draw.ellipse([lx - lw, ly, lx + lw, ly + lh], fill=lc)
        # Lantern glow
        draw.ellipse([lx - lw - 3, ly - 3, lx + lw + 3, ly + lh + 3],
                     outline=glow_color, width=1)

    # Glowing neon signs on buildings in background
    for _ in range(rng.randint(3, 5)):
        bx = rng.randint(int(width * 0.02), int(width * 0.8))
        by = rng.randint(int(height * 0.04), int(height * 0.14))
        bw = rng.randint(int(width * 0.08), int(width * 0.16))
        draw.rectangle([bx, by, bx + bw, by + int(height * 0.04)], fill=sign_color)


def generate_urban_industrial(draw, width, height, colors, rng):
    """Industrial zone with factories, smokestacks, pipes, and orange glow"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.82)
    ground_color  = hex_to_rgb(colors[1])
    factory_color = hex_to_rgb(colors[2])
    pipe_color    = hex_to_rgb(colors[3])
    glow_color    = hex_to_rgb(colors[4 % len(colors)])
    smoke_color   = hex_to_rgb(colors[5 % len(colors)])

    draw.rectangle([0, ground_y, width, height], fill=ground_color)

    # Factory buildings — large blocky structures
    num_factories = rng.randint(3, 5)
    for i in range(num_factories):
        fx = int(width * i / num_factories) + rng.randint(0, int(width * 0.03))
        fw = int(width / num_factories) - int(width * 0.02)
        fh = rng.randint(int(height * 0.22), int(height * 0.45))
        ft = ground_y - fh
        draw.rectangle([fx, ft, fx + fw, ground_y], fill=factory_color)
        # Industrial windows (small, sparse)
        win_color = hex_to_rgb(colors[4 % len(colors)])
        for wy in range(ft + int(height * 0.04), ground_y - int(height * 0.04), int(height * 0.08)):
            for wx in range(fx + int(fw * 0.1), fx + fw - int(fw * 0.1), int(fw * 0.3)):
                draw.rectangle([wx, wy, wx + int(fw * 0.18), wy + int(height * 0.04)], fill=win_color)
        # Roof details
        draw.rectangle([fx, ft, fx + fw, ft + int(height * 0.02)],
                       fill=hex_to_rgb(colors[3]))

    # Smokestacks
    num_stacks = rng.randint(3, 6)
    for _ in range(num_stacks):
        sx = rng.randint(int(width * 0.05), int(width * 0.92))
        sh = rng.randint(int(height * 0.28), int(height * 0.52))
        sw = int(width * 0.025)
        draw.rectangle([sx - sw, ground_y - sh, sx + sw, ground_y], fill=pipe_color)
        # Stack top rim
        draw.rectangle([sx - sw - 3, ground_y - sh - int(height * 0.015),
                         sx + sw + 3, ground_y - sh], fill=factory_color)
        # Smoke puffs
        smoke_x, smoke_y = sx, ground_y - sh - int(height * 0.015)
        for p in range(rng.randint(3, 6)):
            sr = rng.randint(int(width * 0.02), int(width * 0.05))
            smoke_x += rng.randint(-int(width * 0.02), int(width * 0.02))
            smoke_y -= rng.randint(int(height * 0.04), int(height * 0.07))
            draw.ellipse([smoke_x - sr, smoke_y - sr // 2,
                           smoke_x + sr, smoke_y + sr // 2], fill=smoke_color)

    # Horizontal pipes running across lower section
    for i in range(rng.randint(2, 4)):
        py = ground_y - int(height * 0.04) - i * int(height * 0.05)
        draw.line([(0, py), (width, py)], fill=pipe_color, width=max(3, int(height * 0.012)))
        # Pipe joints
        for jx in range(int(width * 0.1), width, int(width * 0.15)):
            draw.ellipse([jx - int(width * 0.012), py - int(height * 0.012),
                           jx + int(width * 0.012), py + int(height * 0.012)], fill=factory_color)

    # Orange glow on horizon (furnace light)
    for i in range(4, 0, -1):
        gy = ground_y - i * int(height * 0.015)
        draw.line([(0, gy), (width, gy)], fill=glow_color, width=2)


def generate_underwater_deep_ocean(draw, width, height, colors, rng):
    """Deep ocean abyss with pressure cracks, bioluminescent particles, and crushing darkness"""
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

    # Light rays from far above
    ray_color = hex_to_rgb(colors[2])
    for _ in range(rng.randint(4, 7)):
        rx = rng.randint(int(width*0.1), int(width*0.9))
        rw = rng.randint(int(width*0.01), int(width*0.03))
        draw.polygon([(rx-rw, 0), (rx+rw, 0), (rx+rw*4, height), (rx-rw*4, height)], fill=ray_color)

    # Sandy/rocky seabed
    bed_y = int(height * 0.88)
    draw.rectangle([0, bed_y, width, height], fill=hex_to_rgb(colors[3]))

    # Rock formations on seabed
    rock_color = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(5, 9)):
        rx = rng.randint(0, width)
        rh = rng.randint(int(height*0.04), int(height*0.12))
        rw = rng.randint(int(width*0.03), int(width*0.08))
        draw.ellipse([rx-rw, bed_y-rh, rx+rw, bed_y+rh//2], fill=rock_color)

    # Floating particles / marine snow
    particle_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(80, 130)):
        px = rng.randint(0, width)
        py = rng.randint(0, bed_y)
        r = rng.choice([1, 1, 2])
        draw.ellipse([px-r, py-r, px+r, py+r], fill=particle_color)


def generate_underwater_shipwreck(draw, width, height, colors, rng):
    """Sunken shipwreck on the ocean floor with algae, fish, and murky water"""
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

    # Murky light rays
    ray_color = hex_to_rgb(colors[2])
    for _ in range(rng.randint(3, 5)):
        rx = rng.randint(int(width*0.1), int(width*0.9))
        rw = rng.randint(int(width*0.015), int(width*0.03))
        draw.polygon([(rx-rw, 0), (rx+rw, 0), (rx+rw*3, height), (rx-rw*3, height)], fill=ray_color)

    # Sandy seabed
    bed_y = int(height * 0.82)
    draw.rectangle([0, bed_y, width, height], fill=hex_to_rgb(colors[3]))

    # Ship hull (large tilted rectangle)
    hull_color = hex_to_rgb(colors[4 % len(colors)])
    cx = width // 2
    hull_w = int(width * 0.38)
    hull_h = int(height * 0.14)
    hull_top = bed_y - int(height * 0.18)
    # Tilted hull as polygon
    tilt = int(height * 0.04)
    draw.polygon([
        (cx - hull_w, hull_top + tilt),
        (cx + hull_w, hull_top),
        (cx + hull_w, hull_top + hull_h),
        (cx - hull_w, hull_top + hull_h + tilt),
    ], fill=hull_color)

    # Ship deck / superstructure
    deck_color = hex_to_rgb(colors[5 % len(colors)])
    draw.rectangle([cx - int(hull_w*0.4), hull_top - int(height*0.1),
                    cx + int(hull_w*0.1), hull_top + tilt//2], fill=deck_color)

    # Mast sticking up
    draw.line([(cx - int(hull_w*0.15), hull_top - int(height*0.1)),
               (cx - int(hull_w*0.15), hull_top - int(height*0.28))],
              fill=deck_color, width=4)

    # Algae/coral growing on wreck
    algae_color = hex_to_rgb(colors[2])
    for _ in range(rng.randint(8, 14)):
        ax = rng.randint(cx - hull_w, cx + hull_w)
        ay = rng.randint(hull_top, bed_y)
        ah = rng.randint(int(height*0.03), int(height*0.08))
        draw.line([(ax, ay), (ax + rng.randint(-8, 8), ay - ah)], fill=algae_color, width=2)

    # Floating particles
    for _ in range(rng.randint(50, 80)):
        px = rng.randint(0, width)
        py = rng.randint(0, bed_y)
        draw.ellipse([px-1, py-1, px+1, py+1], fill=hex_to_rgb(colors[3]))


def generate_underwater_kelp_forest(draw, width, height, colors, rng):
    """Kelp forest with tall swaying kelp strands, fish, and filtered light"""
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

    # Light rays from surface
    ray_color = hex_to_rgb(colors[2])
    for _ in range(rng.randint(4, 6)):
        rx = rng.randint(int(width*0.1), int(width*0.9))
        rw = rng.randint(int(width*0.01), int(width*0.025))
        draw.polygon([(rx-rw, 0), (rx+rw, 0), (rx+rw*3, height), (rx-rw*3, height)], fill=ray_color)

    # Sandy seabed
    bed_y = int(height * 0.9)
    draw.rectangle([0, bed_y, width, height], fill=hex_to_rgb(colors[3]))

    # Tall kelp strands
    kelp_color = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(12, 20)):
        kx = rng.randint(int(width*0.02), int(width*0.98))
        kh = rng.randint(int(height*0.5), int(height*0.88))
        # Wavy kelp strand using segments
        x, y = kx, bed_y
        for seg in range(10):
            nx = x + int(math.sin(seg * 0.8 + rng.uniform(0, 1)) * int(width*0.02))
            ny = y - kh // 10
            draw.line([(x, y), (nx, ny)], fill=kelp_color, width=3)
            # Kelp blade
            if seg % 2 == 0:
                draw.ellipse([nx-int(width*0.015), ny-int(height*0.015),
                              nx+int(width*0.015), ny+int(height*0.015)], fill=kelp_color)
            x, y = nx, ny

    # Fish silhouettes
    fish_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(5, 10)):
        fx = rng.randint(int(width*0.05), int(width*0.95))
        fy = rng.randint(int(height*0.1), int(height*0.75))
        fs = rng.randint(int(width*0.015), int(width*0.03))
        draw.ellipse([fx-fs, fy-fs//2, fx+fs, fy+fs//2], fill=fish_color)
        draw.polygon([(fx+fs, fy), (fx+int(fs*1.5), fy-fs//2), (fx+int(fs*1.5), fy+fs//2)], fill=fish_color)


def generate_underwater_bioluminescent(draw, width, height, colors, rng):
    """Deep dark ocean with glowing bioluminescent creatures and particles"""
    # Very dark background
    draw.rectangle([0, 0, width, height], fill=hex_to_rgb(colors[0]))

    # Faint depth gradient
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

    # Glowing jellyfish
    jelly_color = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(4, 8)):
        jx = rng.randint(int(width*0.05), int(width*0.95))
        jy = rng.randint(int(height*0.1), int(height*0.8))
        jr = rng.randint(int(width*0.03), int(width*0.07))
        # Glow rings
        for i in range(4, 0, -1):
            gr = jr + i * int(width*0.008)
            draw.ellipse([jx-gr, jy-gr//2, jx+gr, jy+gr//2], fill=hex_to_rgb(colors[1]))
        draw.ellipse([jx-jr, jy-jr//2, jx+jr, jy+jr//2], fill=jelly_color)
        # Tentacles
        for t in range(rng.randint(4, 7)):
            tx = jx + rng.randint(-jr, jr)
            draw.line([(tx, jy+jr//2), (tx+rng.randint(-10,10), jy+jr+rng.randint(int(height*0.04), int(height*0.1)))],
                      fill=jelly_color, width=1)

    # Glowing orbs / plankton clusters
    orb_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(60, 100)):
        ox = rng.randint(0, width)
        oy = rng.randint(0, height)
        r = rng.choice([1, 2, 2, 3])
        draw.ellipse([ox-r, oy-r, ox+r, oy+r], fill=orb_color)

    # Glowing fish silhouettes
    fish_color = hex_to_rgb(colors[3])
    for _ in range(rng.randint(3, 6)):
        fx = rng.randint(int(width*0.05), int(width*0.9))
        fy = rng.randint(int(height*0.2), int(height*0.85))
        fs = rng.randint(int(width*0.02), int(width*0.04))
        draw.ellipse([fx-fs, fy-fs//2, fx+fs, fy+fs//2], fill=fish_color)
        draw.polygon([(fx+fs, fy), (fx+int(fs*1.5), fy-fs//2), (fx+int(fs*1.5), fy+fs//2)], fill=fish_color)
        # Eye glow
        draw.ellipse([fx+int(fs*0.4)-2, fy-2, fx+int(fs*0.4)+2, fy+2], fill=orb_color)


def generate_underwater_submarine(draw, width, height, colors, rng):
    """Submarine cruising through deep water with searchlights and bubbles"""
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

    # Submarine body
    sub_color = hex_to_rgb(colors[3])
    cx, cy = int(width*0.45), int(height*0.48)
    sub_w, sub_h = int(width*0.32), int(height*0.1)
    draw.ellipse([cx-sub_w, cy-sub_h, cx+sub_w, cy+sub_h], fill=sub_color)

    # Conning tower
    tower_color = hex_to_rgb(colors[4 % len(colors)])
    draw.rectangle([cx-int(sub_w*0.12), cy-sub_h-int(height*0.08),
                    cx+int(sub_w*0.12), cy-sub_h], fill=tower_color)

    # Periscope
    draw.line([(cx+int(sub_w*0.06), cy-sub_h-int(height*0.08)),
               (cx+int(sub_w*0.06), cy-sub_h-int(height*0.16))], fill=tower_color, width=3)
    draw.line([(cx+int(sub_w*0.06), cy-sub_h-int(height*0.16)),
               (cx+int(sub_w*0.12), cy-sub_h-int(height*0.16))], fill=tower_color, width=3)

    # Propeller
    prop_color = hex_to_rgb(colors[5 % len(colors)])
    px = cx - sub_w
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        draw.line([(px, cy), (px+int(math.cos(rad)*int(sub_h*0.8)),
                   cy+int(math.sin(rad)*int(sub_h*0.8)))], fill=prop_color, width=4)

    # Searchlight beam
    light_color = hex_to_rgb(colors[2])
    draw.polygon([(cx+sub_w, cy),
                  (cx+sub_w+int(width*0.3), cy-int(height*0.12)),
                  (cx+sub_w+int(width*0.3), cy+int(height*0.12))], fill=light_color)

    # Portholes
    port_color = hex_to_rgb(colors[2])
    for i in range(3):
        px2 = cx - int(sub_w*0.3) + i*int(sub_w*0.3)
        draw.ellipse([px2-int(sub_h*0.25), cy-int(sub_h*0.25),
                      px2+int(sub_h*0.25), cy+int(sub_h*0.25)], fill=port_color)

    # Bubbles trailing behind
    bubble_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(15, 25)):
        bx = rng.randint(int(width*0.05), cx-sub_w+int(width*0.05))
        by = rng.randint(cy-int(height*0.2), cy+int(height*0.05))
        br = rng.randint(3, 10)
        draw.ellipse([bx-br, by-br, bx+br, by+br], outline=bubble_color, width=1)


def generate_underwater_tide_pool(draw, width, height, colors, rng):
    """Rocky tide pool with shallow clear water, anemones, starfish, and pebbles"""
    # Sky
    _sky_gradient(draw, width, height, colors)

    # Rocky shore
    rock_color = hex_to_rgb(colors[2])
    ground_y = int(height * 0.55)
    draw.rectangle([0, ground_y, width, height], fill=rock_color)

    # Tide pool — shallow oval depression
    pool_color = hex_to_rgb(colors[1])
    pool_cx, pool_cy = width // 2, int(height * 0.72)
    pool_rx, pool_ry = int(width * 0.32), int(height * 0.14)
    draw.ellipse([pool_cx-pool_rx, pool_cy-pool_ry,
                  pool_cx+pool_rx, pool_cy+pool_ry], fill=pool_color)

    # Pool bottom sand
    sand_color = hex_to_rgb(colors[3])
    draw.ellipse([pool_cx-int(pool_rx*0.85), pool_cy-int(pool_ry*0.7),
                  pool_cx+int(pool_rx*0.85), pool_cy+int(pool_ry*0.7)], fill=sand_color)

    # Pebbles on pool floor
    pebble_color = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(12, 20)):
        px = rng.randint(pool_cx-int(pool_rx*0.7), pool_cx+int(pool_rx*0.7))
        py = rng.randint(pool_cy-int(pool_ry*0.5), pool_cy+int(pool_ry*0.5))
        pr = rng.randint(int(width*0.008), int(width*0.02))
        draw.ellipse([px-pr, py-pr//2, px+pr, py+pr//2], fill=pebble_color)

    # Anemones
    anem_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(4, 7)):
        ax = rng.randint(pool_cx-int(pool_rx*0.6), pool_cx+int(pool_rx*0.6))
        ay = rng.randint(pool_cy-int(pool_ry*0.4), pool_cy+int(pool_ry*0.4))
        for t in range(rng.randint(5, 8)):
            angle = math.radians(t * 360 / 7)
            tlen = rng.randint(int(height*0.02), int(height*0.05))
            draw.line([(ax, ay), (ax+int(math.cos(angle)*tlen), ay+int(math.sin(angle)*tlen))],
                      fill=anem_color, width=2)

    # Starfish
    star_color = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(2, 4)):
        sx = rng.randint(pool_cx-int(pool_rx*0.5), pool_cx+int(pool_rx*0.5))
        sy = rng.randint(pool_cy-int(pool_ry*0.3), pool_cy+int(pool_ry*0.3))
        sr = int(width*0.025)
        for arm in range(5):
            angle = math.radians(arm * 72 - 90)
            draw.line([(sx, sy), (sx+int(math.cos(angle)*sr), sy+int(math.sin(angle)*sr))],
                      fill=star_color, width=4)

    # Pool ripple
    for i in range(1, 3):
        draw.ellipse([pool_cx-int(pool_rx*0.4*i), pool_cy-int(pool_ry*0.4*i),
                      pool_cx+int(pool_rx*0.4*i), pool_cy+int(pool_ry*0.4*i)],
                     outline=pool_color, width=1)


def generate_fantasy_enchanted_forest(draw, width, height, colors, rng):
    """Magical glowing forest with luminous trees, fireflies, and mystical fog"""
    # Dark gradient sky
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.75)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[1]))

    # Fog layer on ground
    fog_color = hex_to_rgb(colors[2])
    for i in range(4):
        fy = ground_y - i * int(height*0.03)
        _wavy_band(draw, width, height, fy, 10, 0.008, fog_color)

    # Glowing enchanted trees
    trunk_color = hex_to_rgb(colors[1])
    glow_color  = hex_to_rgb(colors[3])
    leaf_color  = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(8, 14)):
        tx = rng.randint(int(width*0.02), int(width*0.98))
        th = rng.randint(int(height*0.25), int(height*0.5))
        draw.line([(tx, ground_y), (tx, ground_y-th)], fill=trunk_color, width=5)
        # Glowing canopy rings
        cr = rng.randint(int(width*0.04), int(width*0.09))
        for i in range(3, 0, -1):
            gr = cr + i * int(width*0.012)
            draw.ellipse([tx-gr, ground_y-th-gr, tx+gr, ground_y-th+gr//2],
                         fill=hex_to_rgb(colors[1]))
        draw.ellipse([tx-cr, ground_y-th-cr, tx+cr, ground_y-th+cr//2], fill=leaf_color)

    # Fireflies / magic particles
    for _ in range(rng.randint(60, 100)):
        fx = rng.randint(0, width)
        fy = rng.randint(int(height*0.3), ground_y)
        r = rng.choice([1, 2, 2])
        draw.ellipse([fx-r, fy-r, fx+r, fy+r], fill=glow_color)

    # Glowing mushrooms on ground
    mush_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(5, 9)):
        mx = rng.randint(int(width*0.05), int(width*0.95))
        mh = rng.randint(int(height*0.03), int(height*0.06))
        mw = int(mh * 0.6)
        draw.rectangle([mx-mw//2, ground_y-mh, mx+mw//2, ground_y], fill=trunk_color)
        draw.ellipse([mx-mw, ground_y-mh-mw//2, mx+mw, ground_y-mh+mw//4], fill=mush_color)


def generate_fantasy_floating_islands(draw, width, height, colors, rng):
    """Magical floating islands in the sky with waterfalls, trees, and clouds"""
    _sky_gradient(draw, width, height, colors)

    # Background clouds
    cloud_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(5, 8)):
        cx = rng.randint(0, width)
        cy = rng.randint(int(height*0.1), int(height*0.6))
        cr = rng.randint(int(width*0.05), int(width*0.12))
        draw.ellipse([cx-cr, cy-cr//2, cx+cr, cy+cr//2], fill=cloud_color)

    # Floating islands
    island_color = hex_to_rgb(colors[2])
    grass_color  = hex_to_rgb(colors[3])
    tree_color   = hex_to_rgb(colors[4 % len(colors)])
    water_color  = hex_to_rgb(colors[1])

    islands = [
        (int(width*0.25), int(height*0.38), int(width*0.18), int(height*0.07)),
        (int(width*0.65), int(height*0.28), int(width*0.14), int(height*0.06)),
        (int(width*0.5),  int(height*0.58), int(width*0.22), int(height*0.08)),
    ]
    for ix, iy, iw, ih in islands:
        # Rocky underside
        draw.ellipse([ix-iw, iy, ix+iw, iy+ih*2], fill=island_color)
        # Grassy top
        draw.ellipse([ix-iw, iy-ih, ix+iw, iy+ih], fill=grass_color)

        # Trees on island
        for _ in range(rng.randint(2, 4)):
            tx = rng.randint(ix-int(iw*0.6), ix+int(iw*0.6))
            th = rng.randint(int(height*0.06), int(height*0.12))
            draw.line([(tx, iy), (tx, iy-th)], fill=island_color, width=3)
            tr = int(width*0.025)
            draw.ellipse([tx-tr, iy-th-tr, tx+tr, iy-th+tr//2], fill=tree_color)

        # Waterfall dripping off edge
        wx = ix + int(iw*0.5)
        for seg in range(6):
            wy = iy + ih + seg * int(height*0.03)
            draw.line([(wx, wy), (wx+rng.randint(-4,4), wy+int(height*0.03))],
                      fill=water_color, width=2)


def generate_fantasy_crystal_cave(draw, width, height, colors, rng):
    """Magical crystal cave with glowing gem formations and purple light"""
    # Dark cave background
    draw.rectangle([0, 0, width, height], fill=hex_to_rgb(colors[0]))

    # Cave walls
    wall_color = hex_to_rgb(colors[1])
    for side in [0, 1]:
        pts = [(0 if side == 0 else width, 0)]
        for y in range(0, height+1, int(height/10)):
            jut = rng.randint(int(width*0.06), int(width*0.22))
            pts.append((jut if side == 0 else width-jut, y))
        pts.append((0 if side == 0 else width, height))
        draw.polygon(pts, fill=wall_color)

    # Cave ceiling
    ceil_pts = [(0, 0)]
    for x in range(0, width+1, int(width/12)):
        ch = rng.randint(int(height*0.04), int(height*0.18))
        ceil_pts.append((x, ch))
    ceil_pts.append((width, 0))
    draw.polygon(ceil_pts, fill=wall_color)

    # Cave floor
    floor_pts = [(0, height)]
    for x in range(0, width+1, int(width/10)):
        fh = rng.randint(int(height*0.82), int(height*0.92))
        floor_pts.append((x, fh))
    floor_pts.append((width, height))
    draw.polygon(floor_pts, fill=wall_color)

    # Crystal clusters — sharp pointed polygons
    crystal_colors = [hex_to_rgb(colors[i % len(colors)]) for i in range(2, 6)]
    for _ in range(rng.randint(14, 22)):
        cx = rng.randint(int(width*0.1), int(width*0.9))
        cy = rng.randint(int(height*0.55), int(height*0.88))
        ch = rng.randint(int(height*0.06), int(height*0.18))
        cw = rng.randint(int(width*0.01), int(width*0.025))
        cc = rng.choice(crystal_colors)
        draw.polygon([(cx-cw, cy), (cx, cy-ch), (cx+cw, cy)], fill=cc)
        # Glow around crystal
        for i in range(3, 0, -1):
            draw.ellipse([cx-cw*i, cy-int(ch*0.3)*i, cx+cw*i, cy+int(ch*0.1)*i],
                         fill=hex_to_rgb(colors[1]))
        draw.polygon([(cx-cw, cy), (cx, cy-ch), (cx+cw, cy)], fill=cc)

    # Ceiling crystals hanging down
    for _ in range(rng.randint(8, 14)):
        cx = rng.randint(int(width*0.15), int(width*0.85))
        cy = rng.randint(int(height*0.05), int(height*0.2))
        ch = rng.randint(int(height*0.05), int(height*0.14))
        cw = rng.randint(int(width*0.008), int(width*0.018))
        cc = rng.choice(crystal_colors)
        draw.polygon([(cx-cw, cy), (cx, cy+ch), (cx+cw, cy)], fill=cc)

    # Glowing light pool on floor
    glow_color = hex_to_rgb(colors[3])
    draw.ellipse([int(width*0.3), int(height*0.82),
                  int(width*0.7), int(height*0.95)], fill=glow_color)

    # Floating sparkles
    spark_color = hex_to_rgb(colors[5 % len(colors)])
    for _ in range(rng.randint(40, 70)):
        sx = rng.randint(int(width*0.1), int(width*0.9))
        sy = rng.randint(int(height*0.1), int(height*0.85))
        draw.ellipse([sx-1, sy-1, sx+1, sy+1], fill=spark_color)


def generate_fantasy_dragon_lair(draw, width, height, colors, rng):
    """Dark volcanic dragon lair with fire glow, treasure, and dragon silhouette"""
    # Dark fiery background
    c1, c2 = hex_to_rgb(colors[0]), hex_to_rgb(colors[1])
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

    # Cave walls
    wall_color = hex_to_rgb(colors[1])
    for side in [0, 1]:
        pts = [(0 if side == 0 else width, 0)]
        for y in range(0, height+1, int(height/8)):
            jut = rng.randint(int(width*0.08), int(width*0.25))
            pts.append((jut if side == 0 else width-jut, y))
        pts.append((0 if side == 0 else width, height))
        draw.polygon(pts, fill=wall_color)

    # Lava pool glow at bottom
    lava_color = hex_to_rgb(colors[2])
    glow_color = hex_to_rgb(colors[3])
    draw.ellipse([int(width*0.15), int(height*0.82),
                  int(width*0.85), height], fill=lava_color)
    # Lava glow rings
    for i in range(4, 0, -1):
        draw.ellipse([int(width*0.15)+i*8, int(height*0.82)+i*4,
                      int(width*0.85)-i*8, height-i*4], fill=glow_color)

    # Treasure pile
    treasure_color = hex_to_rgb(colors[4 % len(colors)])
    draw.ellipse([int(width*0.3), int(height*0.74),
                  int(width*0.7), int(height*0.86)], fill=treasure_color)
    # Treasure sparkles
    for _ in range(rng.randint(20, 35)):
        tx = rng.randint(int(width*0.32), int(width*0.68))
        ty = rng.randint(int(height*0.74), int(height*0.84))
        draw.line([(tx-3, ty), (tx+3, ty)], fill=hex_to_rgb(colors[5 % len(colors)]), width=1)
        draw.line([(tx, ty-3), (tx, ty+3)], fill=hex_to_rgb(colors[5 % len(colors)]), width=1)

    # Dragon silhouette
    dragon_color = hex_to_rgb(colors[0])
    dcx, dcy = int(width*0.55), int(height*0.42)
    # Body
    draw.ellipse([dcx-int(width*0.12), dcy-int(height*0.08),
                  dcx+int(width*0.12), dcy+int(height*0.08)], fill=dragon_color)
    # Neck
    draw.polygon([(dcx-int(width*0.04), dcy-int(height*0.08)),
                  (dcx+int(width*0.04), dcy-int(height*0.08)),
                  (dcx+int(width*0.02), dcy-int(height*0.2)),
                  (dcx-int(width*0.02), dcy-int(height*0.2))], fill=dragon_color)
    # Head
    draw.ellipse([dcx-int(width*0.04), dcy-int(height*0.28),
                  dcx+int(width*0.06), dcy-int(height*0.18)], fill=dragon_color)
    # Wing
    draw.polygon([(dcx, dcy),
                  (dcx-int(width*0.28), dcy-int(height*0.22)),
                  (dcx-int(width*0.18), dcy+int(height*0.04))], fill=dragon_color)
    draw.polygon([(dcx, dcy),
                  (dcx+int(width*0.22), dcy-int(height*0.18)),
                  (dcx+int(width*0.14), dcy+int(height*0.04))], fill=dragon_color)
    # Fire breath
    fire_color = hex_to_rgb(colors[2])
    for i in range(5, 0, -1):
        fw = int(width*0.02)*i
        draw.polygon([(dcx+int(width*0.06), dcy-int(height*0.22)),
                      (dcx+int(width*0.06)+fw*3, dcy-int(height*0.22)-fw),
                      (dcx+int(width*0.06)+fw*3, dcy-int(height*0.22)+fw)],
                     fill=hex_to_rgb(colors[(i+1) % len(colors)]))


def generate_fantasy_ancient_ruins(draw, width, height, colors, rng):
    """Overgrown ancient ruins with broken columns, vines, and misty atmosphere"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.78)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[2]))

    # Mist layer
    mist_color = hex_to_rgb(colors[1])
    for i in range(3):
        _wavy_band(draw, width, height, ground_y - i*int(height*0.04), 8, 0.007, mist_color)

    stone_color  = hex_to_rgb(colors[3])
    moss_color   = hex_to_rgb(colors[4 % len(colors)])
    vine_color   = hex_to_rgb(colors[4 % len(colors)])
    detail_color = hex_to_rgb(colors[5 % len(colors)])

    # Broken columns
    num_cols = rng.randint(5, 8)
    for i in range(num_cols):
        cx = int(width * (i + 0.5) / num_cols) + rng.randint(-int(width*0.04), int(width*0.04))
        col_h = rng.randint(int(height*0.18), int(height*0.42))
        col_w = int(width*0.03)
        col_top = ground_y - col_h
        # Column shaft
        draw.rectangle([cx-col_w, col_top, cx+col_w, ground_y], fill=stone_color)
        # Horizontal fluting lines
        for fy in range(col_top, ground_y, int(height*0.04)):
            draw.line([(cx-col_w, fy), (cx+col_w, fy)], fill=detail_color, width=1)
        # Broken top (jagged)
        draw.polygon([(cx-col_w, col_top),
                       (cx-col_w//2, col_top - rng.randint(int(height*0.02), int(height*0.05))),
                       (cx+col_w//2, col_top - rng.randint(0, int(height*0.03))),
                       (cx+col_w, col_top)], fill=detail_color)
        # Moss patches
        for _ in range(rng.randint(2, 4)):
            my = rng.randint(col_top, ground_y)
            mr = rng.randint(int(width*0.008), int(width*0.018))
            draw.ellipse([cx-mr, my-mr//2, cx+mr, my+mr//2], fill=moss_color)

    # Fallen column segment on ground
    for _ in range(rng.randint(2, 3)):
        fx = rng.randint(int(width*0.1), int(width*0.8))
        fw = rng.randint(int(width*0.08), int(width*0.14))
        fh = int(height*0.04)
        draw.ellipse([fx, ground_y-fh, fx+fw, ground_y+fh//2], fill=stone_color)

    # Crumbled wall in background
    wall_color = hex_to_rgb(colors[2])
    for i in range(rng.randint(3, 5)):
        wx = rng.randint(int(width*0.05), int(width*0.85))
        ww = rng.randint(int(width*0.06), int(width*0.14))
        wh = rng.randint(int(height*0.08), int(height*0.2))
        draw.rectangle([wx, ground_y-wh, wx+ww, ground_y], fill=wall_color)

    # Vines hanging from columns
    for _ in range(rng.randint(6, 10)):
        vx = rng.randint(int(width*0.05), int(width*0.95))
        vy_start = rng.randint(int(height*0.2), int(height*0.5))
        vlen = rng.randint(int(height*0.1), int(height*0.25))
        x, y = vx, vy_start
        for seg in range(8):
            nx = x + rng.randint(-6, 6)
            ny = y + vlen // 8
            draw.line([(x, y), (nx, ny)], fill=vine_color, width=2)
            x, y = nx, ny


def generate_fantasy_aurora_castle(draw, width, height, colors, rng):
    """Majestic castle silhouette under a magical aurora sky"""
    _sky_gradient(draw, width, height, colors)

    # Aurora bands
    aurora_colors = [hex_to_rgb(colors[i % len(colors)]) for i in range(2, 5)]
    for i, ac in enumerate(aurora_colors):
        band_y = int(height * (0.15 + i * 0.1))
        amplitude = rng.randint(25, 60)
        _wavy_band(draw, width, height, band_y, amplitude, 0.003, ac)

    # Stars
    for _ in range(rng.randint(60, 100)):
        sx = rng.randint(0, width)
        sy = rng.randint(0, int(height*0.5))
        draw.ellipse([sx-1, sy-1, sx+1, sy+1], fill=hex_to_rgb(colors[5 % len(colors)]))

    ground_y = int(height * 0.82)
    draw.rectangle([0, ground_y, width, height], fill=hex_to_rgb(colors[1]))

    # Snow/ground reflection of aurora
    refl_color = hex_to_rgb(colors[2])
    _wavy_band(draw, width, height, ground_y, 6, 0.01, refl_color)

    castle_color = hex_to_rgb(colors[1])
    cx = width // 2

    # Main keep
    keep_w = int(width * 0.1)
    keep_h = int(height * 0.32)
    keep_top = ground_y - keep_h
    draw.rectangle([cx-keep_w, keep_top, cx+keep_w, ground_y], fill=castle_color)

    # Battlements on keep
    batt_w = int(keep_w * 0.3)
    for bx in range(cx-keep_w, cx+keep_w, batt_w*2):
        draw.rectangle([bx, keep_top-int(height*0.03), bx+batt_w, keep_top], fill=castle_color)

    # Central spire
    draw.polygon([(cx-keep_w, keep_top),
                  (cx, keep_top-int(height*0.14)),
                  (cx+keep_w, keep_top)], fill=castle_color)

    # Side towers
    for side, count in [(-1, 2), (1, 2)]:
        for i in range(count):
            tx = cx + side * int(width * (0.14 + i*0.1))
            tw = int(width * 0.04)
            th = int(height * (0.22 - i*0.04))
            tt = ground_y - th
            draw.rectangle([tx-tw, tt, tx+tw, ground_y], fill=castle_color)
            # Tower spire
            draw.polygon([(tx-tw, tt),
                          (tx, tt-int(height*0.08)),
                          (tx+tw, tt)], fill=castle_color)
            # Tower battlements
            for bx in range(tx-tw, tx+tw, int(tw*0.7)):
                draw.rectangle([bx, tt-int(height*0.02), bx+int(tw*0.5), tt], fill=castle_color)

    # Connecting walls between towers
    wall_color = hex_to_rgb(colors[1])
    wall_h = int(height * 0.1)
    draw.rectangle([cx-int(width*0.24), ground_y-wall_h,
                    cx+int(width*0.24), ground_y], fill=wall_color)

    # Gate arch
    gate_w = int(width * 0.04)
    draw.rectangle([cx-gate_w, ground_y-int(height*0.1),
                    cx+gate_w, ground_y], fill=hex_to_rgb(colors[0]))
    draw.ellipse([cx-gate_w, ground_y-int(height*0.12),
                  cx+gate_w, ground_y-int(height*0.06)], fill=hex_to_rgb(colors[0]))

    # Glowing windows
    win_color = hex_to_rgb(colors[4 % len(colors)])
    for _ in range(rng.randint(6, 10)):
        wx = rng.randint(cx-keep_w+4, cx+keep_w-4)
        wy = rng.randint(keep_top+int(height*0.04), ground_y-int(height*0.06))
        wr = int(width*0.008)
        draw.ellipse([wx-wr, wy-wr*2, wx+wr, wy], fill=win_color)


def generate_urban_rainy_street(draw, width, height, colors, rng):
    """Rainy city street at night with reflections, streetlights, and wet pavement"""
    _sky_gradient(draw, width, height, colors)

    ground_y = int(height * 0.62)
    pavement_color = hex_to_rgb(colors[1])
    building_color = hex_to_rgb(colors[2])
    light_color    = hex_to_rgb(colors[4 % len(colors)])
    reflect_color  = hex_to_rgb(colors[4 % len(colors)])
    rain_color     = hex_to_rgb(colors[3])

    # Wet pavement
    draw.rectangle([0, ground_y, width, height], fill=pavement_color)

    # Buildings on both sides
    for side in [0, 1]:
        num_bld = rng.randint(2, 4)
        for i in range(num_bld):
            if side == 0:
                bx = int(width * i * 0.18)
                bw = int(width * 0.16)
            else:
                bx = int(width * (0.66 + i * 0.18))
                bw = int(width * 0.16)
            bh = rng.randint(int(height * 0.3), int(height * 0.58))
            bt = ground_y - bh
            draw.rectangle([bx, bt, bx + bw, ground_y], fill=building_color)
            # Lit windows
            win_color = hex_to_rgb(colors[5 % len(colors)])
            ws = max(3, bw // 6)
            for wy in range(bt + ws, ground_y - ws, ws * 2):
                for wx in range(bx + ws, bx + bw - ws, ws * 2):
                    if rng.random() > 0.45:
                        draw.rectangle([wx, wy, wx + ws, wy + ws], fill=win_color)
                        # Window reflection on pavement
                        ref_y = ground_y + (ground_y - wy)
                        if ref_y < height:
                            draw.rectangle([wx, ref_y, wx + ws, ref_y + ws],
                                           fill=tuple(c // 2 for c in hex_to_rgb(colors[5 % len(colors)])))

    # Streetlights
    for lx in [int(width * 0.28), int(width * 0.72)]:
        pole_color = hex_to_rgb(colors[3])
        draw.line([(lx, ground_y), (lx, int(height * 0.22))], fill=pole_color, width=3)
        draw.line([(lx, int(height * 0.22)), (lx + int(width * 0.04), int(height * 0.18))],
                  fill=pole_color, width=3)
        # Light head
        draw.ellipse([lx + int(width * 0.03), int(height * 0.16),
                       lx + int(width * 0.06), int(height * 0.2)], fill=light_color)
        # Light cone on pavement
        draw.polygon([(lx + int(width * 0.045), int(height * 0.2)),
                       (lx - int(width * 0.08), ground_y),
                       (lx + int(width * 0.17), ground_y)],
                     fill=tuple(min(255, c + 25) for c in pavement_color))
        # Reflection of light on wet street
        draw.polygon([(lx + int(width * 0.045), ground_y),
                       (lx - int(width * 0.06), ground_y + int(height * 0.12)),
                       (lx + int(width * 0.15), ground_y + int(height * 0.12))],
                     fill=tuple(c // 3 for c in light_color))

    # Rain streaks
    for _ in range(rng.randint(80, 130)):
        rx = rng.randint(0, width)
        ry = rng.randint(0, ground_y)
        draw.line([(rx, ry), (rx - 3, ry + 10)], fill=rain_color, width=1)

    # Puddle ripples on pavement
    for _ in range(rng.randint(5, 9)):
        px = rng.randint(int(width * 0.1), int(width * 0.9))
        py = rng.randint(ground_y + int(height * 0.04), height - int(height * 0.06))
        pr = rng.randint(int(width * 0.02), int(width * 0.05))
        draw.ellipse([px - pr, py - pr // 3, px + pr, py + pr // 3],
                     outline=reflect_color, width=1)


def generate_scene(width, height, scene_type, palette_colors, seed, inverted=False):
    """Generate a scene wallpaper"""
    rng = random.Random(seed)

    # Normalize scene_type to string value for comparison
    if hasattr(scene_type, 'value'):
        scene_type = scene_type.value

    premium = PREMIUM_SCENES.get(scene_type)
    if premium is not None:
        return premium(width, height, palette_colors, rng)

    bg_color = hex_to_rgb(palette_colors[0])
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    landmark_generators = [
        generate_landmark_eiffel_tower,
        generate_landmark_statue_of_liberty,
        generate_landmark_big_ben,
        generate_landmark_taj_mahal,
        generate_landmark_christ_redeemer,
        generate_landmark_colosseum,
        generate_landmark_sydney,
    ]
    world_generators = [
        generate_world_desert,
        generate_world_beach,
        generate_world_mountain,
        generate_world_valley,
        generate_world_canyon,
        generate_world_plateau,
        generate_world_savanna,
        generate_world_tundra,
    ]
    celestial_generators = [
        generate_celestial_sunrise,
        generate_celestial_sunset,
        generate_celestial_starfield,
        generate_celestial_northern_lights,
        generate_celestial_eclipse,
        generate_celestial_nebula,
        generate_celestial_galaxy,
    ]
    nature_generators = [
        generate_nature_forest,
        generate_nature_jungle,
        generate_nature_ocean,
        generate_nature_waterfall,
        generate_nature_volcano,
        generate_nature_storm,
        generate_world_meadow,
    ]
    urban_generators = [
        generate_urban_neon_city,
        generate_urban_skyline,
        generate_urban_geometric,
        generate_urban_modern_art,
    ]

    if scene_type == "eiffel_tower":
        generate_landmark_eiffel_tower(draw, width, height, palette_colors, rng)
    elif scene_type == "statue_of_liberty":
        generate_landmark_statue_of_liberty(draw, width, height, palette_colors, rng)
    elif scene_type == "big_ben":
        generate_landmark_big_ben(draw, width, height, palette_colors, rng)
    elif scene_type == "taj_mahal":
        generate_landmark_taj_mahal(draw, width, height, palette_colors, rng)
    elif scene_type == "christ_redeemer":
        generate_landmark_christ_redeemer(draw, width, height, palette_colors, rng)
    elif scene_type == "colosseum":
        generate_landmark_colosseum(draw, width, height, palette_colors, rng)
    elif scene_type == "sydney_opera_house":
        generate_landmark_sydney(draw, width, height, palette_colors, rng)
    elif scene_type == "great_wall":
        generate_landmark_great_wall(draw, width, height, palette_colors, rng)
    elif scene_type == "burj_khalifa":
        generate_landmark_burj_khalifa(draw, width, height, palette_colors, rng)
    elif scene_type == "sagrada_familia":
        generate_landmark_sagrada_familia(draw, width, height, palette_colors, rng)
    elif scene_type == "stonehenge":
        generate_landmark_stonehenge(draw, width, height, palette_colors, rng)
    elif scene_type == "machu_picchu":
        generate_landmark_machu_picchu(draw, width, height, palette_colors, rng)
    elif scene_type == "leaning_tower_pisa":
        generate_landmark_leaning_tower_pisa(draw, width, height, palette_colors, rng)
    elif scene_type == "acropolis":
        generate_landmark_acropolis(draw, width, height, palette_colors, rng)
    elif scene_type == "mount_fuji":
        generate_landmark_mount_fuji(draw, width, height, palette_colors, rng)
    elif scene_type == "desert":
        generate_world_desert(draw, width, height, palette_colors, rng)
    elif scene_type == "beach":
        generate_world_beach(draw, width, height, palette_colors, rng)
    elif scene_type == "mountain":
        generate_world_mountain(draw, width, height, palette_colors, rng)
    elif scene_type == "valley":
        generate_world_valley(draw, width, height, palette_colors, rng)
    elif scene_type == "canyon":
        generate_world_canyon(draw, width, height, palette_colors, rng)
    elif scene_type == "plateau":
        generate_world_plateau(draw, width, height, palette_colors, rng)
    elif scene_type == "savanna":
        generate_world_savanna(draw, width, height, palette_colors, rng)
    elif scene_type == "tundra":
        generate_world_tundra(draw, width, height, palette_colors, rng)
    elif scene_type == "glacier":
        generate_world_glacier(draw, width, height, palette_colors, rng)
    elif scene_type == "rainforest":
        generate_world_rainforest(draw, width, height, palette_colors, rng)
    elif scene_type == "fjord":
        generate_world_fjord(draw, width, height, palette_colors, rng)
    elif scene_type == "wetlands":
        generate_world_wetlands(draw, width, height, palette_colors, rng)
    elif scene_type == "steppe":
        generate_world_steppe(draw, width, height, palette_colors, rng)
    elif scene_type == "sunrise":
        generate_celestial_sunrise(draw, width, height, palette_colors, rng)
    elif scene_type == "sunset":
        generate_celestial_sunset(draw, width, height, palette_colors, rng)
    elif scene_type == "starfield":
        generate_celestial_starfield(draw, width, height, palette_colors, rng)
    elif scene_type == "northern_lights":
        generate_celestial_northern_lights(draw, width, height, palette_colors, rng)
    elif scene_type == "solar_eclipse":
        generate_celestial_eclipse(draw, width, height, palette_colors, rng)
    elif scene_type == "nebula":
        generate_celestial_nebula(draw, width, height, palette_colors, rng)
    elif scene_type == "galaxy":
        generate_celestial_galaxy(draw, width, height, palette_colors, rng)
    elif scene_type == "lunar_eclipse":
        generate_celestial_lunar_eclipse(draw, width, height, palette_colors, rng)
    elif scene_type == "comet":
        generate_celestial_comet(draw, width, height, palette_colors, rng)
    elif scene_type == "meteor_shower":
        generate_celestial_meteor_shower(draw, width, height, palette_colors, rng)
    elif scene_type == "binary_stars":
        generate_celestial_binary_stars(draw, width, height, palette_colors, rng)
    elif scene_type == "moonrise":
        generate_celestial_moonrise(draw, width, height, palette_colors, rng)
    elif scene_type == "forest":
        generate_nature_forest(draw, width, height, palette_colors, rng)
    elif scene_type == "jungle":
        generate_nature_jungle(draw, width, height, palette_colors, rng)
    elif scene_type == "ocean":
        generate_nature_ocean(draw, width, height, palette_colors, rng)
    elif scene_type == "waterfall":
        generate_nature_waterfall(draw, width, height, palette_colors, rng)
    elif scene_type == "volcano":
        generate_nature_volcano(draw, width, height, palette_colors, rng)
    elif scene_type == "storm":
        generate_nature_storm(draw, width, height, palette_colors, rng)
    elif scene_type == "meadow":
        generate_world_meadow(draw, width, height, palette_colors, rng)
    elif scene_type == "cave":
        generate_nature_cave(draw, width, height, palette_colors, rng)
    elif scene_type == "hot_spring":
        generate_nature_hot_spring(draw, width, height, palette_colors, rng)
    elif scene_type == "coral_reef":
        generate_nature_coral_reef(draw, width, height, palette_colors, rng)
    elif scene_type == "dunes_night":
        generate_nature_dunes_night(draw, width, height, palette_colors, rng)
    elif scene_type == "mangrove":
        generate_nature_mangrove(draw, width, height, palette_colors, rng)
    elif scene_type == "neon_city":
        generate_urban_neon_city(draw, width, height, palette_colors, rng)
    elif scene_type in ["minimalist_city", "classic_skyline"]:
        generate_urban_skyline(draw, width, height, palette_colors, rng)
    elif scene_type == "geometric_grid":
        generate_urban_geometric(draw, width, height, palette_colors, rng)
    elif scene_type == "modern_art":
        generate_urban_modern_art(draw, width, height, palette_colors, rng)
    elif scene_type == "rooftop_garden":
        generate_urban_rooftop_garden(draw, width, height, palette_colors, rng)
    elif scene_type == "subway":
        generate_urban_subway(draw, width, height, palette_colors, rng)
    elif scene_type == "night_market":
        generate_urban_night_market(draw, width, height, palette_colors, rng)
    elif scene_type == "industrial":
        generate_urban_industrial(draw, width, height, palette_colors, rng)
    elif scene_type == "rainy_street":
        generate_urban_rainy_street(draw, width, height, palette_colors, rng)
    elif scene_type == "deep_ocean":
        generate_underwater_deep_ocean(draw, width, height, palette_colors, rng)
    elif scene_type == "shipwreck":
        generate_underwater_shipwreck(draw, width, height, palette_colors, rng)
    elif scene_type == "kelp_forest":
        generate_underwater_kelp_forest(draw, width, height, palette_colors, rng)
    elif scene_type == "bioluminescent":
        generate_underwater_bioluminescent(draw, width, height, palette_colors, rng)
    elif scene_type == "submarine":
        generate_underwater_submarine(draw, width, height, palette_colors, rng)
    elif scene_type == "tide_pool":
        generate_underwater_tide_pool(draw, width, height, palette_colors, rng)
    elif scene_type == "enchanted_forest":
        generate_fantasy_enchanted_forest(draw, width, height, palette_colors, rng)
    elif scene_type == "floating_islands":
        generate_fantasy_floating_islands(draw, width, height, palette_colors, rng)
    elif scene_type == "crystal_cave":
        generate_fantasy_crystal_cave(draw, width, height, palette_colors, rng)
    elif scene_type == "dragon_lair":
        generate_fantasy_dragon_lair(draw, width, height, palette_colors, rng)
    elif scene_type == "ancient_ruins":
        generate_fantasy_ancient_ruins(draw, width, height, palette_colors, rng)
    elif scene_type == "aurora_castle":
        generate_fantasy_aurora_castle(draw, width, height, palette_colors, rng)
    else:
        # Fallback gradient
        c1, c2 = hex_to_rgb(palette_colors[0]), hex_to_rgb(palette_colors[-1])
        for y in range(height):
            t = y / height
            draw.line([(0, y), (width, y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

    return image


def export_to_bytes(image):
    """Export PIL image to PNG bytes"""
    buffer = BytesIO()
    image.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)
    return buffer.getvalue()