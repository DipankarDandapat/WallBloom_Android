package com.aurawall.app.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

enum class ApiMode { V2, LEGACY }

/**
 * Single source of truth for catalog + feed data.
 *
 * The catalog is cached on disk so the app opens instantly (even offline or while a free-tier
 * server is cold-starting) and is refreshed in the background. If the server does not expose
 * the v2 API, the repository transparently falls back to the original v1 endpoints.
 */
class WallpaperRepository(
    private val api: WallBloomApi,
    private val cacheDir: File,
) {
    @Volatile var mode: ApiMode = ApiMode.V2
        private set
    @Volatile private var catalog: Catalog? = null

    private val v2Urls = V2ImageUrls(api.root.toString())
    private val legacyUrls = LegacyImageUrls(api.root.toString())
    val urls: ImageUrls get() = if (mode == ApiMode.V2) v2Urls else legacyUrls
    val baseUrl: String get() = api.root.toString()

    private val v2File get() = File(cacheDir, "catalog_v2.json")
    private val legacyFile get() = File(cacheDir, "catalog_v1.json")

    /** Last catalog stored on disk, or null on first launch. */
    suspend fun cachedCatalog(): Catalog? = withContext(Dispatchers.IO) {
        val parsed = runCatching {
            when {
                v2File.exists() -> CatalogJson.parseCatalog(v2File.readText()).also { mode = ApiMode.V2 }
                legacyFile.exists() -> legacyFile.readText().split(SEPARATOR).let { (a, b, c) ->
                    LegacyCatalog.build(a, b, c).also { mode = ApiMode.LEGACY }
                }
                else -> null
            }
        }.getOrNull()
        parsed?.also { catalog = it }
    }

    /** Fetches the newest catalog from the network and persists it. */
    suspend fun refreshCatalog(): Catalog {
        val fresh = try {
            val json = api.catalogV2()
            CatalogJson.parseCatalog(json).also {
                write(v2File, json)
                legacyFile.delete()
                mode = ApiMode.V2
            }
        } catch (e: HttpException) {
            if (e.code != 404) throw e
            val patterns = api.patternsV1()
            val palettes = api.palettesV1()
            val scenes = api.scenesV1()
            LegacyCatalog.build(patterns, palettes, scenes).also {
                write(legacyFile, listOf(patterns, palettes, scenes).joinToString(SEPARATOR))
                v2File.delete()
                mode = ApiMode.LEGACY
            }
        }
        catalog = fresh
        return fresh
    }

    suspend fun feed(collection: String?, page: Int, salt: Long?, pageSize: Int = PAGE_SIZE): List<Wallpaper> =
        when (mode) {
            ApiMode.V2 -> CatalogJson.parseFeed(api.feedV2(collection, page, pageSize, salt))
            ApiMode.LEGACY -> {
                val current = catalog ?: refreshCatalog()
                LegacyCatalog.feed(current, collection, page, pageSize, salt ?: (System.currentTimeMillis() / 86_400_000L))
            }
        }

    suspend fun bytes(url: String): ByteArray = api.bytes(url)

    suspend fun health(): Boolean = api.health()

    private suspend fun write(file: File, text: String) = withContext(Dispatchers.IO) {
        runCatching {
            file.parentFile?.mkdirs()
            val tmp = File(file.parentFile, file.name + ".tmp")
            tmp.writeText(text)
            tmp.renameTo(file)
        }
    }

    companion object {
        const val PAGE_SIZE = 24
        private const val SEPARATOR = "\n\u0000\n"
    }
}
