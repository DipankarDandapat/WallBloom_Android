package com.aurawall.app.system

import android.app.WallpaperManager
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.media.MediaScannerConnection
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.view.WindowManager
import androidx.core.content.FileProvider
import com.aurawall.app.data.WallpaperTarget
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayInputStream
import java.io.File
import java.io.IOException

/** Everything that touches the device: wallpaper manager, gallery and the share sheet. */
class DeviceActions(private val context: Context) {

    /** Physical screen size in pixels (portrait), used to render a pixel-perfect wallpaper. */
    fun screenSize(): Pair<Int, Int> {
        val wm = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val (w, h) = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            wm.maximumWindowMetrics.bounds.let { it.width() to it.height() }
        } else {
            val metrics = android.util.DisplayMetrics()
            @Suppress("DEPRECATION") wm.defaultDisplay.getRealMetrics(metrics)
            metrics.widthPixels to metrics.heightPixels
        }
        val portrait = minOf(w, h) to maxOf(w, h)
        // Keep within the backend's 4096px limit while preserving aspect ratio.
        val scale = minOf(1f, 4096f / portrait.second)
        return (portrait.first * scale).toInt().coerceAtLeast(16) to (portrait.second * scale).toInt().coerceAtLeast(16)
    }

    val canSetWallpaper: Boolean
        get() = WallpaperManager.getInstance(context).let { it.isWallpaperSupported && it.isSetWallpaperAllowed }

    suspend fun setWallpaper(bytes: ByteArray, target: WallpaperTarget) = withContext(Dispatchers.IO) {
        val manager = WallpaperManager.getInstance(context)
        if (!manager.isWallpaperSupported || !manager.isSetWallpaperAllowed) throw IOException("This device does not allow changing the wallpaper")
        // Decoding first validates the image so a bad response never blanks the wallpaper.
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size) ?: throw IOException("Could not decode wallpaper")
        val flags = when (target) {
            WallpaperTarget.HOME -> WallpaperManager.FLAG_SYSTEM
            WallpaperTarget.LOCK -> WallpaperManager.FLAG_LOCK
            WallpaperTarget.BOTH -> WallpaperManager.FLAG_SYSTEM or WallpaperManager.FLAG_LOCK
        }
        try {
            manager.setBitmap(bitmap, null, true, flags)
        } finally {
            bitmap.recycle()
        }
    }

    /** Saves into Pictures/WallBloom. Android 8-9 need WRITE_EXTERNAL_STORAGE (requested by the UI). */
    suspend fun saveToGallery(bytes: ByteArray, displayName: String, mime: String): Uri = withContext(Dispatchers.IO) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val values = ContentValues().apply {
                put(MediaStore.Images.Media.DISPLAY_NAME, displayName)
                put(MediaStore.Images.Media.MIME_TYPE, mime)
                put(MediaStore.Images.Media.RELATIVE_PATH, "${Environment.DIRECTORY_PICTURES}/$FOLDER")
                put(MediaStore.Images.Media.IS_PENDING, 1)
            }
            val resolver = context.contentResolver
            val uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values) ?: throw IOException("Unable to create image")
            try {
                resolver.openOutputStream(uri)?.use { it.write(bytes) } ?: throw IOException("Unable to write image")
                values.clear()
                values.put(MediaStore.Images.Media.IS_PENDING, 0)
                resolver.update(uri, values, null, null)
                uri
            } catch (e: Exception) {
                resolver.delete(uri, null, null)
                throw e
            }
        } else {
            @Suppress("DEPRECATION")
            val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), FOLDER).apply { mkdirs() }
            val file = File(dir, displayName)
            file.writeBytes(bytes)
            MediaScannerConnection.scanFile(context, arrayOf(file.absolutePath), arrayOf(mime), null)
            Uri.fromFile(file)
        }
    }

    /** Writes the image to the app cache and returns a share-sheet intent for it. */
    suspend fun shareIntent(bytes: ByteArray, displayName: String, mime: String, text: String): Intent = withContext(Dispatchers.IO) {
        val dir = File(context.cacheDir, "shared").apply { mkdirs() }
        dir.listFiles()?.forEach { it.delete() }
        val file = File(dir, displayName).apply { writeBytes(bytes) }
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.files", file)
        Intent.createChooser(
            Intent(Intent.ACTION_SEND).apply {
                type = mime
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_TEXT, text)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            },
            "Share wallpaper",
        ).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }

    companion object {
        const val FOLDER = "WallBloom"
    }
}
