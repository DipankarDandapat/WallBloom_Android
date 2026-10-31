package com.aurawall.app.data

import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrl

enum class Quality(val key: String) { THUMB("thumb"), FULL("full") }
enum class ImageFormat(val key: String, val extension: String, val mime: String) {
    WEBP("webp", "webp", "image/webp"), PNG("png", "png", "image/png")
}

/** Fixed render sizes. Bucketing sizes keeps HTTP/disk caches hot across screens. */
object RenderSizes {
    val PHONE_BASE = 1290 to 2796
    val DESKTOP_BASE = 3840 to 2160
    val PHONE_THUMB = 540 to 1170
    val DESKTOP_THUMB = 960 to 540
    val PHONE_TILE = 270 to 585
    val DESKTOP_VIEW = 1920 to 1080

    fun thumb(orientation: Orientation) = if (orientation == Orientation.PHONE) PHONE_THUMB else DESKTOP_THUMB
    fun base(orientation: Orientation) = if (orientation == Orientation.PHONE) PHONE_BASE else DESKTOP_BASE
}

/** Builds image URLs for whichever backend generation we are talking to. */
interface ImageUrls {
    fun image(w: Wallpaper, width: Int, height: Int, quality: Quality, format: ImageFormat = ImageFormat.WEBP, download: Boolean = false): String

    fun thumb(w: Wallpaper, orientation: Orientation): String =
        RenderSizes.thumb(orientation).let { (width, height) -> image(w, width, height, Quality.THUMB) }

    fun tile(w: Wallpaper): String = RenderSizes.PHONE_TILE.let { (width, height) -> image(w, width, height, Quality.THUMB) }
}

/** v2: one cached render endpoint for every size, format and quality. */
class V2ImageUrls(base: String) : ImageUrls {
    private val root: HttpUrl = base.trim().trimEnd('/').toHttpUrl()

    override fun image(w: Wallpaper, width: Int, height: Int, quality: Quality, format: ImageFormat, download: Boolean): String =
        root.newBuilder().addPathSegments("api/v2/render").apply {
            addQueryParameter("kind", w.kind.key)
            addQueryParameter("key", w.key)
            addQueryParameter("palette", w.palette.toString())
            addQueryParameter("seed", w.seed.toString())
            if (w.inverted) addQueryParameter("inverted", "true")
            if (w.kind == Kind.PATTERN && w.key2 != null) {
                addQueryParameter("key2", w.key2)
                addQueryParameter("blend", "%.2f".format(java.util.Locale.US, w.blend))
            }
            addQueryParameter("w", width.toString())
            addQueryParameter("h", height.toString())
            addQueryParameter("quality", quality.key)
            addQueryParameter("fmt", format.key)
            if (download) addQueryParameter("download", "true")
        }.build().toString()
}

/**
 * v1: the original endpoints, used when a deployment has not been upgraded yet. They always
 * render at full size (slow) and only emit PNG, but the app keeps working.
 */
class LegacyImageUrls(base: String) : ImageUrls {
    private val root: HttpUrl = base.trim().trimEnd('/').toHttpUrl()

    override fun image(w: Wallpaper, width: Int, height: Int, quality: Quality, format: ImageFormat, download: Boolean): String {
        val desktop = width > height
        val builder = root.newBuilder()
        if (download) {
            builder.addPathSegments("api/wallpapers/download/${if (desktop) "desktop" else "mobile"}")
            if (w.kind == Kind.SCENE) {
                builder.addQueryParameter("scene_type", w.key).addQueryParameter("palette_override", w.palette.toString())
            } else {
                builder.addQueryParameter("pattern_type", w.key).addQueryParameter("palette_index", w.palette.coerceAtLeast(0).toString())
                w.key2?.let { builder.addQueryParameter("pattern_type_2", it).addQueryParameter("blend_ratio", w.blend.toString()) }
            }
        } else if (w.kind == Kind.SCENE) {
            builder.addPathSegments("api/wallpapers/scene")
                .addQueryParameter("scene_type", w.key)
                .addQueryParameter("palette_override", w.palette.toString())
                .addQueryParameter("width", width.toString())
                .addQueryParameter("height", height.toString())
        } else {
            builder.addPathSegments("api/wallpapers/preview")
                .addQueryParameter("pattern_type", w.key)
                .addQueryParameter("palette_index", w.palette.coerceAtLeast(0).toString())
                .addQueryParameter("width", width.toString())
                .addQueryParameter("height", height.toString())
            w.key2?.let { builder.addQueryParameter("pattern_type_2", it).addQueryParameter("blend_ratio", w.blend.toString()) }
        }
        return builder.addQueryParameter("seed", w.seed.toString())
            .addQueryParameter("inverted", w.inverted.toString())
            .build().toString()
    }
}
