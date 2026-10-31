package com.aurawall.app.data

/** Which device a wallpaper is framed for. Only phone wallpapers can be applied on-device. */
enum class Orientation(val key: String) {
    PHONE("phone"), DESKTOP("desktop");

    companion object {
        fun from(key: String?) = entries.firstOrNull { it.key == key } ?: PHONE
    }
}

enum class Kind(val key: String) {
    PATTERN("pattern"), SCENE("scene");

    companion object {
        fun from(key: String) = entries.first { it.key == key }
    }
}

/** Where a wallpaper is applied on the phone. */
enum class WallpaperTarget { HOME, LOCK, BOTH }

/**
 * A fully specified, reproducible wallpaper. The backend renders the same pixels for the same
 * parameters, so this doubles as a favourite and as the input for any size we need.
 */
data class Wallpaper(
    val kind: Kind,
    val key: String,
    val name: String,
    val subtitle: String,
    val category: String,
    /** Palette index; -1 means the scene's own default palette. */
    val palette: Int,
    val seed: Int,
    val inverted: Boolean = false,
    val colors: List<String> = emptyList(),
    /** Optional second pattern blended into the first (patterns only). */
    val key2: String? = null,
    val blend: Float = 0.5f,
) {
    val id: String
        get() = buildString {
            append(kind.key).append(':').append(key).append(':').append(palette).append(':').append(seed)
            append(':').append(if (inverted) 1 else 0)
            if (key2 != null) append(':').append(key2).append('@').append((blend * 100).toInt())
        }
}

data class Palette(val id: Int, val name: String, val colors: List<String>, val tags: List<String> = emptyList())

data class PatternInfo(val key: String, val name: String, val category: String, val glyph: String, val featured: Boolean)

data class PatternCategory(
    val id: String,
    val name: String,
    val icon: String,
    val emoji: String,
    val accent: String,
    val description: String,
)

data class Scene(val key: String, val name: String, val emoji: String, val colors: List<String>)

data class SceneTheme(
    val id: String,
    val name: String,
    val icon: String,
    val emoji: String,
    val accent: String,
    val description: String,
    val scenes: List<Scene>,
)

data class WallCollection(
    val id: String,
    val name: String,
    val subtitle: String,
    val icon: String,
    val emoji: String,
    val accent: String,
    val cover: Wallpaper,
)

data class Catalog(
    val apiVersion: Int,
    val patternCategories: List<PatternCategory>,
    val patterns: List<PatternInfo>,
    val sceneThemes: List<SceneTheme>,
    val palettes: List<Palette>,
    val collections: List<WallCollection>,
    val hero: List<Wallpaper>,
) {
    fun palette(id: Int): Palette? = palettes.getOrNull(id)?.takeIf { it.id == id } ?: palettes.firstOrNull { it.id == id }
    fun pattern(key: String): PatternInfo? = patterns.firstOrNull { it.key == key }
    fun scene(key: String): Pair<SceneTheme, Scene>? =
        sceneThemes.firstNotNullOfOrNull { theme -> theme.scenes.firstOrNull { it.key == key }?.let { theme to it } }

    /** Builds a wallpaper for [key] with display names and colours filled in from the catalog. */
    fun wallpaper(kind: Kind, key: String, palette: Int, seed: Int, inverted: Boolean = false, key2: String? = null, blend: Float = .5f): Wallpaper {
        val paletteInfo = palette(palette)
        return if (kind == Kind.SCENE) {
            val (theme, scene) = scene(key) ?: (null to null)
            Wallpaper(
                kind, key, scene?.name ?: key.prettify(),
                if (palette < 0) theme?.name.orEmpty() else paletteInfo?.name.orEmpty(),
                theme?.id.orEmpty(), palette, seed, inverted,
                if (palette < 0) scene?.colors.orEmpty() else paletteInfo?.colors.orEmpty(),
            )
        } else {
            val info = pattern(key)
            val p = palette.coerceAtLeast(0)
            Wallpaper(
                kind, key, info?.name ?: key.prettify(), palette(p)?.name.orEmpty(), info?.category.orEmpty(),
                p, seed, inverted, palette(p)?.colors.orEmpty(), key2, blend,
            )
        }
    }
}

fun String.prettify(): String = split('_').joinToString(" ") { part -> part.replaceFirstChar { it.uppercase() } }
