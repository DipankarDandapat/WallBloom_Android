package com.aurawall.app

import android.app.Application
import coil.ImageLoader
import coil.ImageLoaderFactory
import coil.disk.DiskCache
import coil.memory.MemoryCache
import com.aurawall.app.data.UserPrefs
import com.aurawall.app.data.WallBloomApi
import com.aurawall.app.data.WallpaperRepository
import com.aurawall.app.system.DeviceActions
import com.chuckerteam.chucker.api.ChuckerInterceptor
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

/** Manual dependency container; the app is small enough not to need a DI framework. */
class WallBloomApplication : Application(), ImageLoaderFactory {

    val httpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(90, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .addInterceptor(ChuckerInterceptor(this))
            .build()
    }

    // Separate client for Coil thumbnails: max 3 concurrent requests so fast scrolling
    // never floods the render server with 10+ simultaneous thumb renders.
    // Also retries once on IOException (Canceled) after a short back-off so images
    // that were mid-flight when the user scrolled away load correctly on scroll-back.
    private val imageHttpClient: OkHttpClient by lazy {
        httpClient.newBuilder()
            .dispatcher(okhttp3.Dispatcher().also { it.maxRequestsPerHost = 3 })
            .addInterceptor { chain ->
                var attempt = 0
                var lastEx: Exception? = null
                while (attempt < 3) {
                    try {
                        return@addInterceptor chain.proceed(chain.request())
                    } catch (e: java.io.IOException) {
                        lastEx = e
                        attempt++
                        if (attempt < 3) Thread.sleep(300L * attempt)
                    }
                }
                throw lastEx!!
            }
            .build()
    }

    val repository: WallpaperRepository by lazy {
        WallpaperRepository(WallBloomApi(httpClient, BuildConfig.API_BASE_URL), filesDir)
    }
    val prefs: UserPrefs by lazy { UserPrefs(this) }
    val device: DeviceActions by lazy { DeviceActions(this) }

    override fun newImageLoader(): ImageLoader = ImageLoader.Builder(this)
        .okHttpClient(imageHttpClient)
        .memoryCache { MemoryCache.Builder(this).maxSizePercent(0.25).build() }
        .diskCache { DiskCache.Builder().directory(cacheDir.resolve("images")).maxSizeBytes(300L * 1024 * 1024).build() }
        // Renders are deterministic; cache them even though they are fetched with query strings.
        .respectCacheHeaders(false)
        .crossfade(220)
        .build()
}
