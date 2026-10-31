package com.aurawall.app.data

import org.json.JSONArray
import org.json.JSONObject
import kotlin.random.Random

/**
 * Builds a [Catalog] and a curated feed from the original v1 endpoints so the app still works
 * against a backend that has not been upgraded to the v2 API.
 */
object LegacyCatalog {
    private val featured = listOf(
        "waves", "dunes", "hexagon", "vortex", "diamond", "mosaic", "terraces", "tides", "chevron", "origami",
        "crystals", "scales", "dna", "topographic", "voronoi", "kaleidoscope", "triangular_mesh", "plasma",
        "interference", "turbulence", "stained_glass", "honeycomb_flow", "tree_rings", "lenticular", "patchwork",
        "sunburst", "wire_frame", "mandala", "weave", "lava", "smoke", "pointillism", "pixel_sort", "aurora",
    )
    private val themeIcons = mapOf(
        "landmarks" to "account_balance", "world_scenes" to "public", "celestial" to "nights_stay",
        "nature_elements" to "forest", "urban" to "apartment", "underwater" to "water", "fantasy" to "castle",
        "minimal" to "filter_hdr",
    )
    private val accents = listOf("#9D8CFF", "#FFB86B", "#58C4DD", "#6FCF97", "#FF6FAE", "#3DC9F5", "#C38BFF", "#F4A261")

    fun build(patternsJson: String, palettesJson: String, scenesJson: String): Catalog {
        val patternArray = JSONObject(patternsJson).getJSONArray("patterns")
        val patterns = List(patternArray.length()) { index ->
            val item = patternArray.getJSONObject(index)
            val key = item.getString("type")
            PatternInfo(key, item.optString("name", key.prettify()).replace('_', ' '), "all", "🎨", key in featured)
        }
        val paletteArray = JSONArray(palettesJson)
        val palettes = List(paletteArray.length()) { CatalogJson.parsePalette(paletteArray.getJSONObject(it)) }
        val themeArray = JSONObject(scenesJson).getJSONArray("themes")
        val themes = List(themeArray.length()) { index ->
            val group = themeArray.getJSONObject(index)
            val id = group.getString("id")
            val scenes = group.getJSONArray("scenes")
            SceneTheme(
                id, group.optString("name", id.prettify()), themeIcons[id].orEmpty(), group.optString("emoji", "🌍"),
                accents[index % accents.size], "",
                List(scenes.length()) { s ->
                    val scene = scenes.getJSONObject(s)
                    Scene(scene.getString("id"), scene.getString("name"), scene.optString("emoji", "🎨"), emptyList())
                },
            )
        }
        val base = Catalog(
            apiVersion = 1,
            patternCategories = listOf(PatternCategory("all", "All patterns", "category", "🎨", "#7C8CFF", "")),
            patterns = patterns, sceneThemes = themes, palettes = palettes, collections = emptyList(), hero = emptyList(),
        )
        val collections = themes.map { theme ->
            WallCollection(theme.id, theme.name, "${theme.scenes.size} scenes", theme.icon, theme.emoji, theme.accent,
                feed(base, theme.id, 0, 1, 0).first())
        }
        return base.copy(collections = collections, hero = feed(base, null, 0, 6, 1))
    }

    /** Deterministic, infinite feed mixing scenes and the best-looking patterns. */
    fun feed(catalog: Catalog, collection: String?, page: Int, pageSize: Int, salt: Long): List<Wallpaper> {
        val scenes = catalog.sceneThemes.filter { collection == null || it.id == collection }.flatMap { it.scenes }
        val patternKeys = if (collection == null) catalog.patterns.filter { it.featured }.map { it.key } else emptyList()
        val pool = scenes.map { Kind.SCENE to it.key } + patternKeys.map { Kind.PATTERN to it }
        if (pool.isEmpty()) return emptyList()
        return (page * pageSize until (page + 1) * pageSize).map { index ->
            val random = Random("${collection ?: "discover"}:$salt:$index".hashCode())
            val (kind, key) = pool[random.nextInt(pool.size)]
            val palette = if (kind == Kind.SCENE) -1 else random.nextInt(catalog.palettes.size.coerceAtLeast(1))
            catalog.wallpaper(kind, key, palette, random.nextInt(100_000, 999_999))
        }
    }
}
