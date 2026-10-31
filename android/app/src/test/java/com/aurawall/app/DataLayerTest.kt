package com.aurawall.app

import com.aurawall.app.data.ApiMode
import com.aurawall.app.data.CatalogJson
import com.aurawall.app.data.ImageFormat
import com.aurawall.app.data.Kind
import com.aurawall.app.data.LegacyCatalog
import com.aurawall.app.data.LegacyImageUrls
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.Quality
import com.aurawall.app.data.V2ImageUrls
import com.aurawall.app.data.WallBloomApi
import com.aurawall.app.data.WallpaperRepository
import com.aurawall.app.ui.screens.searchCatalog
import kotlinx.coroutines.test.runTest
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import okhttp3.mockwebserver.Dispatcher
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import okhttp3.mockwebserver.RecordedRequest
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.io.File
import java.nio.file.Files

class DataLayerTest {
    private fun fixture(name: String) = javaClass.classLoader!!.getResource(name)!!.readText()

    private val catalog by lazy { CatalogJson.parseCatalog(fixture("catalog_v2.json")) }

    @Test fun parsesV2Catalog() {
        assertEquals(2, catalog.apiVersion)
        assertTrue(catalog.patterns.size >= 100)
        assertTrue(catalog.palettes.size >= 70)
        assertTrue(catalog.sceneThemes.any { it.id == "minimal" && it.scenes.size >= 8 })
        assertTrue(catalog.collections.all { it.icon.isNotBlank() && it.accent.startsWith("#") })
        assertEquals(6, catalog.hero.size)
        assertTrue(catalog.patternCategories.all { cat -> catalog.patterns.any { it.category == cat.id } })
    }

    @Test fun feedItemIdsMatchBackendIds() {
        val json = org.json.JSONObject(fixture("feed_v2.json")).getJSONArray("items")
        val items = CatalogJson.parseFeed(fixture("feed_v2.json"))
        assertEquals(json.length(), items.size)
        items.forEachIndexed { i, item -> assertEquals(json.getJSONObject(i).getString("id"), item.id) }
    }

    @Test fun favouritesRoundTrip() {
        val blended = catalog.wallpaper(Kind.PATTERN, "mesh_gradient", 50, 123, inverted = true, key2 = "flow_lines", blend = .35f)
        val scene = catalog.wallpaper(Kind.SCENE, "ocean_sunset", -1, 9)
        val restored = CatalogJson.parseWallpapers(CatalogJson.wallpapersToJson(listOf(blended, scene)))
        assertEquals(listOf(blended, scene), restored)
        assertEquals(emptyList<Any>(), CatalogJson.parseWallpapers("not json"))
    }

    @Test fun catalogFillsNamesAndColours() {
        val scene = catalog.wallpaper(Kind.SCENE, "aurora_lake", -1, 1)
        assertEquals("Aurora Lake", scene.name)
        assertEquals("Minimal", scene.subtitle)
        assertEquals(6, scene.colors.size)
        val recoloured = catalog.wallpaper(Kind.SCENE, "aurora_lake", 3, 1)
        assertEquals(catalog.palette(3)!!.colors, recoloured.colors)
        // Patterns never use the "scene default" palette.
        assertEquals(0, catalog.wallpaper(Kind.PATTERN, "waves", -1, 1).palette)
    }

    @Test fun v2UrlsEncodeEveryParameter() {
        val w = catalog.wallpaper(Kind.PATTERN, "silk_waves", 12, 777, inverted = true, key2 = "bokeh", blend = .4f)
        val url = V2ImageUrls("http://10.0.2.2:8000/").image(w, 1080, 2400, Quality.FULL, ImageFormat.PNG, download = true).toHttpUrl()
        assertEquals("/api/v2/render", url.encodedPath)
        assertEquals("pattern", url.queryParameter("kind"))
        assertEquals("silk_waves", url.queryParameter("key"))
        assertEquals("12", url.queryParameter("palette"))
        assertEquals("777", url.queryParameter("seed"))
        assertEquals("true", url.queryParameter("inverted"))
        assertEquals("bokeh", url.queryParameter("key2"))
        assertEquals("0.40", url.queryParameter("blend"))
        assertEquals("1080", url.queryParameter("w"))
        assertEquals("2400", url.queryParameter("h"))
        assertEquals("full", url.queryParameter("quality"))
        assertEquals("png", url.queryParameter("fmt"))
        assertEquals("true", url.queryParameter("download"))
    }

    @Test fun thumbnailsUseFixedBuckets() {
        val urls = V2ImageUrls("https://example.com")
        val w = catalog.hero.first()
        val phone = urls.thumb(w, Orientation.PHONE).toHttpUrl()
        val desktop = urls.thumb(w, Orientation.DESKTOP).toHttpUrl()
        assertEquals("540" to "1170", phone.queryParameter("w") to phone.queryParameter("h"))
        assertEquals("960" to "540", desktop.queryParameter("w") to desktop.queryParameter("h"))
        assertEquals("thumb", phone.queryParameter("quality"))
        assertNull(phone.queryParameter("inverted"))
    }

    @Test fun legacyUrlsTargetV1Endpoints() {
        val urls = LegacyImageUrls("https://wallbloom.onrender.com")
        val scene = catalog.wallpaper(Kind.SCENE, "eiffel_tower", -1, 5)
        val pattern = catalog.wallpaper(Kind.PATTERN, "waves", 4, 5)
        assertEquals("/api/wallpapers/scene", urls.image(scene, 390, 844, Quality.THUMB).toHttpUrl().encodedPath)
        assertEquals("/api/wallpapers/preview", urls.image(pattern, 390, 844, Quality.THUMB).toHttpUrl().encodedPath)
        val desktopDownload = urls.image(scene, 3840, 2160, Quality.FULL, ImageFormat.PNG, download = true).toHttpUrl()
        assertEquals("/api/wallpapers/download/desktop", desktopDownload.encodedPath)
        assertEquals("eiffel_tower", desktopDownload.queryParameter("scene_type"))
        assertEquals("-1", desktopDownload.queryParameter("palette_override"))
    }

    @Test fun legacyCatalogAndFeedAreDeterministic() {
        val legacy = LegacyCatalog.build(fixture("patterns_v1.json"), fixture("palettes_v1.json"), fixture("scenes_v1.json"))
        assertEquals(1, legacy.apiVersion)
        assertEquals(legacy.sceneThemes.size, legacy.collections.size)
        assertEquals(6, legacy.hero.size)
        val a = LegacyCatalog.feed(legacy, null, 0, 24, 42)
        assertEquals(a, LegacyCatalog.feed(legacy, null, 0, 24, 42))
        assertFalse(a == LegacyCatalog.feed(legacy, null, 1, 24, 42))
        val themed = LegacyCatalog.feed(legacy, "celestial", 0, 10, 1)
        assertTrue(themed.all { it.kind == Kind.SCENE && it.category == "celestial" })
    }

    @Test fun searchFindsScenesPatternsAndPalettes() {
        assertTrue(searchCatalog(catalog, "sunset").any { it.key == "ocean_sunset" })
        assertTrue(searchCatalog(catalog, "geometric").any { it.kind == Kind.PATTERN })
        assertTrue(searchCatalog(catalog, "cyberpunk").all { it.kind == Kind.PATTERN && catalog.palette(it.palette)?.name == "Cyberpunk" })
        assertTrue(searchCatalog(catalog, "x").isEmpty())
    }
}

class RepositoryTest {
    private lateinit var server: MockWebServer
    private lateinit var dir: File
    private fun fixture(name: String) = javaClass.classLoader!!.getResource(name)!!.readText()

    @Before fun setUp() {
        server = MockWebServer()
        dir = Files.createTempDirectory("wb").toFile()
    }

    @After fun tearDown() {
        server.shutdown()
        dir.deleteRecursively()
    }

    private fun serve(v2: Boolean) {
        server.dispatcher = object : Dispatcher() {
            override fun dispatch(request: RecordedRequest): MockResponse = when (request.requestUrl!!.encodedPath) {
                "/api/v2/catalog" -> if (v2) MockResponse().setBody(fixture("catalog_v2.json")) else MockResponse().setResponseCode(404)
                "/api/v2/feed" -> MockResponse().setBody(fixture("feed_v2.json"))
                "/api/patterns" -> MockResponse().setBody(fixture("patterns_v1.json"))
                "/api/palettes" -> MockResponse().setBody(fixture("palettes_v1.json"))
                "/api/scenes" -> MockResponse().setBody(fixture("scenes_v1.json"))
                "/health" -> MockResponse().setBody("{}")
                else -> MockResponse().setResponseCode(404)
            }
        }
        server.start()
    }

    private fun repo() = WallpaperRepository(WallBloomApi(OkHttpClient(), server.url("/").toString()), dir)

    @Test fun usesV2WhenAvailableAndCachesCatalog() = runTest {
        serve(v2 = true)
        val repo = repo()
        assertNull(repo.cachedCatalog())
        val catalog = repo.refreshCatalog()
        assertEquals(ApiMode.V2, repo.mode)
        assertEquals(5, repo.feed(null, 0, null).size)
        assertTrue(repo.urls is V2ImageUrls)
        // A fresh repository (next app launch) can render instantly from disk.
        val cached = repo().cachedCatalog()
        assertNotNull(cached)
        assertEquals(catalog.patterns.size, cached!!.patterns.size)
        assertTrue(repo.health())
    }

    @Test fun fallsBackToLegacyApiOn404() = runTest {
        serve(v2 = false)
        val repo = repo()
        val catalog = repo.refreshCatalog()
        assertEquals(ApiMode.LEGACY, repo.mode)
        assertEquals(1, catalog.apiVersion)
        assertTrue(repo.urls is LegacyImageUrls)
        assertEquals(24, repo.feed(null, 0, 7).size)
        val next = repo()
        assertNotNull(next.cachedCatalog())
        assertEquals(ApiMode.LEGACY, next.mode)
    }

    @Test fun serverErrorsAreNotTreatedAsLegacy() = runTest {
        server.dispatcher = object : Dispatcher() {
            override fun dispatch(request: RecordedRequest) = MockResponse().setResponseCode(503)
        }
        server.start()
        val result = runCatching { repo().refreshCatalog() }
        assertTrue(result.isFailure)
        assertFalse(repo().health())
    }
}
