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
            // Free-tier hosts can take a while to cold start and render 4K images.
            .readTimeout(90, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .addInterceptor(ChuckerInterceptor(this))
            .build()
    }

    val repository: WallpaperRepository by lazy {
        WallpaperRepository(WallBloomApi(httpClient, BuildConfig.API_BASE_URL), filesDir)
    }
    val prefs: UserPrefs by lazy { UserPrefs(this) }
    val device: DeviceActions by lazy { DeviceActions(this) }

    override fun newImageLoader(): ImageLoader = ImageLoader.Builder(this)
        .okHttpClient(httpClient)
        .memoryCache { MemoryCache.Builder(this).maxSizePercent(0.25).build() }
        .diskCache { DiskCache.Builder().directory(cacheDir.resolve("images")).maxSizeBytes(300L * 1024 * 1024).build() }
        // Renders are deterministic; cache them even though they are fetched with query strings.
        .respectCacheHeaders(false)
        .crossfade(220)
        .build()
}
