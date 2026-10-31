package com.aurawall.app.data

import org.json.JSONArray
import org.json.JSONObject

/** JSON mapping for the v2 API and for locally persisted data (favourites, cached catalog). */
object CatalogJson {

    fun parseCatalog(json: String): Catalog {
        val root = JSONObject(json)
        return Catalog(
            apiVersion = root.optInt("version", 2),
            patternCategories = root.getJSONArray("pattern_categories").objects().map {
                PatternCategory(
                    it.getString("id"), it.getString("name"), it.optString("icon"), it.optString("emoji", "🎨"),
                    it.optString("accent", "#8B7CFF"), it.optString("description"),
                )
            },
            patterns = root.getJSONArray("patterns").objects().map {
                PatternInfo(
                    it.getString("key"), it.getString("name"), it.optString("category", "artistic"),
                    it.optString("glyph", "🎨"), it.optBoolean("featured"),
                )
            },
            sceneThemes = root.getJSONArray("scene_themes").objects().map { theme ->
                SceneTheme(
                    theme.getString("id"), theme.getString("name"), theme.optString("icon"),
                    theme.optString("emoji", "🌍"), theme.optString("accent", "#8B7CFF"),
                    theme.optString("description"),
                    theme.getJSONArray("scenes").objects().map {
                        Scene(it.getString("key"), it.getString("name"), it.optString("emoji", "🎨"), it.optJSONArray("colors").strings())
                    },
                )
            },
            palettes = root.getJSONArray("palettes").objects().map(::parsePalette),
            collections = root.optJSONArray("collections").objects().map {
                WallCollection(
                    it.getString("id"), it.getString("name"), it.optString("subtitle"), it.optString("icon"),
                    it.optString("emoji", "✨"), it.optString("accent", "#8B7CFF"), parseWallpaper(it.getJSONObject("cover")),
                )
            },
            hero = root.optJSONArray("hero").objects().map(::parseWallpaper),
        )
    }

    fun parsePalette(it: JSONObject) =
        Palette(it.getInt("id"), it.optString("name", "Palette ${it.getInt("id") + 1}"), it.getJSONArray("colors").strings(), it.optJSONArray("tags").strings())

    fun parseFeed(json: String): List<Wallpaper> = JSONObject(json).getJSONArray("items").objects().map(::parseWallpaper)

    fun parseWallpaper(it: JSONObject) = Wallpaper(
        kind = Kind.from(it.getString("kind")),
        key = it.getString("key"),
        name = it.optString("name", it.getString("key").prettify()),
        subtitle = it.optString("subtitle"),
        category = it.optString("category"),
        palette = it.optInt("palette", -1),
        seed = it.getInt("seed"),
        inverted = it.optBoolean("inverted"),
        colors = it.optJSONArray("colors").strings(),
        key2 = it.optString("key2").takeIf { value -> value.isNotBlank() && value != "null" },
        blend = it.optDouble("blend", .5).toFloat(),
    )

    fun wallpaperToJson(w: Wallpaper): JSONObject = JSONObject().apply {
        put("kind", w.kind.key)
        put("key", w.key)
        put("name", w.name)
        put("subtitle", w.subtitle)
        put("category", w.category)
        put("palette", w.palette)
        put("seed", w.seed)
        put("inverted", w.inverted)
        put("colors", JSONArray(w.colors))
        w.key2?.let { put("key2", it) }
        put("blend", w.blend.toDouble())
    }

    fun wallpapersToJson(items: List<Wallpaper>): String = JSONArray().apply { items.forEach { put(wallpaperToJson(it)) } }.toString()

    fun parseWallpapers(json: String?): List<Wallpaper> =
        if (json.isNullOrBlank()) emptyList() else runCatching { JSONArray(json).objects().map(::parseWallpaper) }.getOrDefault(emptyList())

    private fun JSONArray?.objects(): List<JSONObject> = if (this == null) emptyList() else List(length()) { getJSONObject(it) }
    private fun JSONArray?.strings(): List<String> = if (this == null) emptyList() else List(length()) { getString(it) }
}
