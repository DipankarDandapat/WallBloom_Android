package com.aurawall.app.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException

class HttpException(val code: Int, message: String) : IOException(message)

/** Thin HTTP layer over the WallBloom backend. All calls run on [Dispatchers.IO]. */
class WallBloomApi(private val client: OkHttpClient, baseUrl: String) {
    val root: HttpUrl = baseUrl.trim().trimEnd('/').toHttpUrl()

    private fun url(path: String, query: HttpUrl.Builder.() -> Unit = {}) =
        root.newBuilder().addPathSegments(path).apply(query).build()

    suspend fun health(): Boolean = runCatching { getString(url("health")); true }.getOrDefault(false)

    suspend fun catalogV2(): String = getString(url("api/v2/catalog"))

    suspend fun feedV2(collection: String?, page: Int, pageSize: Int, salt: Long?): String = getString(url("api/v2/feed") {
        collection?.let { addQueryParameter("collection", it) }
        addQueryParameter("page", page.toString())
        addQueryParameter("page_size", pageSize.toString())
        salt?.let { addQueryParameter("salt", it.toString()) }
    })

    suspend fun patternsV1(): String = getString(url("api/patterns"))
    suspend fun palettesV1(): String = getString(url("api/palettes"))
    suspend fun scenesV1(): String = getString(url("api/scenes"))

    suspend fun bytes(url: String): ByteArray = withContext(Dispatchers.IO) {
        client.newCall(Request.Builder().url(url).build()).execute().use { response ->
            if (!response.isSuccessful) throw HttpException(response.code, "HTTP ${response.code}")
            response.body?.bytes()?.takeIf { it.isNotEmpty() } ?: throw IOException("Empty image response")
        }
    }

    private suspend fun getString(url: HttpUrl): String = withContext(Dispatchers.IO) {
        client.newCall(Request.Builder().url(url).build()).execute().use { response ->
            if (!response.isSuccessful) throw HttpException(response.code, "HTTP ${response.code} for ${url.encodedPath}")
            response.body?.string() ?: throw IOException("Empty response")
        }
    }
}
