package com.aurawall.app.data

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException

class HttpException(val code: Int, message: String) : IOException(message)

private const val TAG = "WallBloomApi"

/**
 * Retries [block] up to [maxAttempts] times on server errors (500/502/503) or transient
 * IOExceptions. Uses exponential back-off: 500 ms → 1 000 ms → 2 000 ms.
 *
 * "Canceled" IOExceptions (OkHttp scroll-away cancellations) are NOT retried here —
 * Coil re-issues those automatically when the item comes back into view.
 */
private suspend fun <T> withRetry(tag: String, maxAttempts: Int = 3, block: suspend () -> T): T {
    var lastError: Exception? = null
    repeat(maxAttempts) { attempt ->
        try {
            return block()
        } catch (e: HttpException) {
            if (e.code !in listOf(500, 502, 503)) throw e   // 4xx / other 5xx → don't retry
            lastError = e
            Log.w(TAG, "$tag HTTP ${e.code}, retry ${attempt + 1}/$maxAttempts")
        } catch (e: IOException) {
            if (e.message?.contains("Canceled", ignoreCase = true) == true) throw e
            lastError = e
            Log.w(TAG, "$tag IOException retry ${attempt + 1}/$maxAttempts: ${e.message}")
        }
        delay(500L * (1 shl attempt))   // 500 ms, 1 000 ms, 2 000 ms
    }
    throw lastError!!
}

/** Thin HTTP layer over the WallBloom backend. All calls run on [Dispatchers.IO]. */
class WallBloomApi(private val client: OkHttpClient, baseUrl: String) {
    val root: HttpUrl = baseUrl.trim().trimEnd('/').toHttpUrl()

    private fun url(path: String, query: HttpUrl.Builder.() -> Unit = {}) =
        root.newBuilder().addPathSegments(path).apply(query).build()

    suspend fun health(): Boolean = runCatching { getString(url("health")); true }.getOrDefault(false)

    suspend fun catalogV2(): String = withRetry("catalogV2") { getString(url("api/v2/catalog")) }

    suspend fun feedV2(collection: String?, page: Int, pageSize: Int, salt: Long?): String =
        withRetry("feedV2") {
            getString(url("api/v2/feed") {
                collection?.let { addQueryParameter("collection", it) }
                addQueryParameter("page", page.toString())
                addQueryParameter("page_size", pageSize.toString())
                salt?.let { addQueryParameter("salt", it.toString()) }
            })
        }

    suspend fun patternsV1(): String = withRetry("patternsV1") { getString(url("api/patterns")) }
    suspend fun palettesV1(): String = withRetry("palettesV1") { getString(url("api/palettes")) }
    suspend fun scenesV1(): String   = withRetry("scenesV1")   { getString(url("api/scenes")) }

    suspend fun bytes(url: String): ByteArray = withRetry("bytes") {
        withContext(Dispatchers.IO) {
            client.newCall(Request.Builder().url(url).build()).execute().use { response ->
                if (!response.isSuccessful) throw HttpException(response.code, "HTTP ${response.code}")
                response.body?.bytes()?.takeIf { it.isNotEmpty() } ?: throw IOException("Empty image response")
            }
        }
    }

    /** Streams bytes and reports 0..1 progress. Retried automatically by [withRetry]. */
    suspend fun bytesWithProgress(url: String, onProgress: (Float) -> Unit): ByteArray =
        withRetry("bytesWithProgress") {
            onProgress(0f)  // reset progress bar on each attempt so the UI reflects the restart
            withContext(Dispatchers.IO) {
                client.newCall(Request.Builder().url(url).build()).execute().use { response ->
                    if (!response.isSuccessful) throw HttpException(response.code, "HTTP ${response.code}")
                    val body = response.body ?: throw IOException("Empty image response")
                    val total = body.contentLength()
                    val out = java.io.ByteArrayOutputStream(if (total > 0) total.toInt() else 512 * 1024)
                    val chunk = ByteArray(8 * 1024)
                    var received = 0L
                    val stream = body.byteStream()
                    while (true) {
                        val read = stream.read(chunk)
                        if (read == -1) break
                        out.write(chunk, 0, read)
                        received += read
                        if (total > 0) onProgress((received.toFloat() / total).coerceIn(0f, 1f))
                    }
                    if (out.size() == 0) throw IOException("Empty image response")
                    out.toByteArray()
                }
            }
        }

    private suspend fun getString(url: HttpUrl): String = withContext(Dispatchers.IO) {
        client.newCall(Request.Builder().url(url).build()).execute().use { response ->
            if (!response.isSuccessful) throw HttpException(response.code, "HTTP ${response.code} for ${url.encodedPath}")
            response.body?.string() ?: throw IOException("Empty response")
        }
    }
}
