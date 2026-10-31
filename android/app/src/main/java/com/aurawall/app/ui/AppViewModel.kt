package com.aurawall.app.ui

import android.content.Intent
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.aurawall.app.WallBloomApplication
import com.aurawall.app.data.ApiMode
import com.aurawall.app.data.Catalog
import com.aurawall.app.data.ImageFormat
import com.aurawall.app.data.Kind
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.Quality
import com.aurawall.app.data.RenderSizes
import com.aurawall.app.data.Settings
import com.aurawall.app.data.ThemeMode
import com.aurawall.app.data.UserPrefs
import com.aurawall.app.data.Wallpaper
import com.aurawall.app.data.WallpaperRepository
import com.aurawall.app.data.WallpaperTarget
import com.aurawall.app.system.DeviceActions
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.random.Random

sealed interface CatalogState {
    data class Loading(val slow: Boolean = false) : CatalogState
    data class Ready(val catalog: Catalog) : CatalogState
    data class Failed(val message: String) : CatalogState
}

data class FeedState(
    val items: List<Wallpaper> = emptyList(),
    val nextPage: Int = 0,
    val loading: Boolean = false,
    val refreshing: Boolean = false,
    val error: String? = null,
    val salt: Long? = null,
)

enum class ActionKind { DOWNLOAD, APPLY, SHARE }
data class ActionProgress(val wallpaperId: String, val kind: ActionKind)

data class UiMessage(val text: String, val isError: Boolean = false, val id: Long = System.nanoTime())

/** Studio editor state; lives in the ViewModel so it survives tab switches. */
data class StudioState(
    val source: Kind = Kind.PATTERN,
    val patternCategory: String? = null,
    val pattern: String = "mesh_gradient",
    val sceneTheme: String? = null,
    val scene: String = "ocean_sunset",
    val palette: Int = 50,
    /** Scenes: -1 keeps the scene's own colours. */
    val scenePalette: Int = -1,
    val inverted: Boolean = false,
    val seed: Int = 424242,
    val blendEnabled: Boolean = false,
    val pattern2: String = "flow_lines",
    val blend: Float = 0.5f,
)

class PreviewSession(val items: List<Wallpaper>, val startIndex: Int, val orientation: Orientation)

class AppViewModel(
    private val repository: WallpaperRepository,
    private val prefs: UserPrefs,
    val device: DeviceActions,
) : ViewModel() {

    private val _catalog = MutableStateFlow<CatalogState>(CatalogState.Loading())
    val catalog: StateFlow<CatalogState> = _catalog.asStateFlow()

    private val _feeds = MutableStateFlow<Map<String, FeedState>>(emptyMap())
    val feeds: StateFlow<Map<String, FeedState>> = _feeds.asStateFlow()

    val favorites: StateFlow<List<Wallpaper>> = prefs.favorites.stateIn(viewModelScope, SharingStarted.Eagerly, emptyList())
    val settings: StateFlow<Settings> = prefs.settings.stateIn(viewModelScope, SharingStarted.Eagerly, Settings())

    private val _busy = MutableStateFlow<ActionProgress?>(null)
    val busy: StateFlow<ActionProgress?> = _busy.asStateFlow()

    private val _messages = Channel<UiMessage>(Channel.BUFFERED)
    val messages = _messages.receiveAsFlow()

    private val _studio = MutableStateFlow(StudioState())
    val studio: StateFlow<StudioState> = _studio.asStateFlow()

    private val _preview = MutableStateFlow<PreviewSession?>(null)
    val preview: StateFlow<PreviewSession?> = _preview.asStateFlow()

    private val _serverOnline = MutableStateFlow<Boolean?>(null)
    val serverOnline: StateFlow<Boolean?> = _serverOnline.asStateFlow()

    val urls get() = repository.urls
    val apiMode: ApiMode get() = repository.mode
    val baseUrl: String get() = repository.baseUrl

    private var catalogJob: Job? = null
    private val feedJobs = mutableMapOf<String, Job>()

    init {
        loadCatalog()
    }

    // ------------------------------------------------------------------ catalog

    fun loadCatalog() {
        catalogJob?.cancel()
        catalogJob = viewModelScope.launch {
            val cached = repository.cachedCatalog()
            if (cached != null) _catalog.value = CatalogState.Ready(cached)
            else _catalog.value = CatalogState.Loading()
            var attempt = 0
            while (true) {
                try {
                    val fresh = repository.refreshCatalog()
                    val modeChanged = cached != null && cached.apiVersion != fresh.apiVersion
                    _catalog.value = CatalogState.Ready(fresh)
                    _serverOnline.value = true
                    if (cached == null || modeChanged) resetFeeds()
                    return@launch
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    _serverOnline.value = false
                    attempt++
                    if (_catalog.value !is CatalogState.Ready) {
                        // Free-tier servers sleep; keep trying quietly for about a minute first.
                        _catalog.value = if (attempt < 12) CatalogState.Loading(slow = attempt >= 2)
                        else CatalogState.Failed(e.message ?: "Server unreachable")
                        if (attempt >= 12) return@launch
                    } else if (attempt >= 3) {
                        return@launch // We have cached content; stop retrying silently.
                    }
                    delay((1500L * attempt).coerceAtMost(6000L))
                }
            }
        }
    }

    fun checkServer() = viewModelScope.launch { _serverOnline.value = repository.health() }

    // ------------------------------------------------------------------ feeds

    fun feedKey(collection: String?) = collection ?: DISCOVER

    fun ensureFeed(collection: String?) {
        val state = _feeds.value[feedKey(collection)]
        if (state == null || (state.items.isEmpty() && !state.loading && state.error == null)) loadMore(collection)
    }

    fun loadMore(collection: String?) {
        val key = feedKey(collection)
        val current = _feeds.value[key] ?: FeedState()
        if (current.loading || feedJobs[key]?.isActive == true) return
        if (_catalog.value !is CatalogState.Ready) return
        updateFeed(key) { it.copy(loading = true, error = null) }
        feedJobs[key] = viewModelScope.launch {
            try {
                val page = repository.feed(collection, current.nextPage, current.salt)
                updateFeed(key) { state ->
                    val seen = state.items.mapTo(HashSet()) { it.id }
                    state.copy(items = state.items + page.filter { seen.add(it.id) }, nextPage = state.nextPage + 1, loading = false, refreshing = false)
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                updateFeed(key) { it.copy(loading = false, refreshing = false, error = e.message ?: "Couldn't load wallpapers") }
            }
        }
    }

    /** Pull-to-refresh: a new salt gives a brand-new (still cacheable) shuffle of the feed. */
    fun refreshFeed(collection: String?) {
        val key = feedKey(collection)
        feedJobs[key]?.cancel()
        _feeds.update { it + (key to FeedState(refreshing = true, salt = Random.nextLong(1, 99_999_999))) }
        if (_catalog.value !is CatalogState.Ready) loadCatalog()
        loadMore(collection)
    }

    private fun resetFeeds() {
        feedJobs.values.forEach { it.cancel() }
        feedJobs.clear()
        _feeds.value = emptyMap()
    }

    private fun updateFeed(key: String, transform: (FeedState) -> FeedState) =
        _feeds.update { it + (key to transform(it[key] ?: FeedState())) }

    // ------------------------------------------------------------------ preview

    fun openPreview(items: List<Wallpaper>, index: Int, orientation: Orientation) {
        _preview.value = PreviewSession(items, index.coerceIn(0, (items.size - 1).coerceAtLeast(0)), orientation)
    }

    /** Swaps an item inside the current session (recolour / new variation) and keeps the page. */
    fun replacePreviewItem(index: Int, item: Wallpaper) {
        val session = _preview.value ?: return
        val items = session.items.toMutableList().also { if (index in it.indices) it[index] = item }
        _preview.value = PreviewSession(items, index, session.orientation)
    }

    // ------------------------------------------------------------------ user state

    fun toggleFavorite(w: Wallpaper) = viewModelScope.launch {
        val added = prefs.toggleFavorite(w)
        _messages.send(UiMessage(if (added) "Saved to favourites" else "Removed from favourites"))
    }

    fun setTheme(mode: ThemeMode) = viewModelScope.launch { prefs.setTheme(mode) }
    fun setAmoled(enabled: Boolean) = viewModelScope.launch { prefs.setAmoled(enabled) }
    fun setOrientation(orientation: Orientation) = viewModelScope.launch { prefs.setOrientation(orientation) }

    fun updateStudio(transform: (StudioState) -> StudioState) = _studio.update(transform)

    fun studioWallpaper(catalog: Catalog, s: StudioState = _studio.value): Wallpaper =
        if (s.source == Kind.SCENE) catalog.wallpaper(Kind.SCENE, s.scene, s.scenePalette, s.seed, s.inverted)
        else catalog.wallpaper(Kind.PATTERN, s.pattern, s.palette, s.seed, s.inverted, if (s.blendEnabled) s.pattern2 else null, s.blend)

    // ------------------------------------------------------------------ device actions

    fun download(w: Wallpaper, orientation: Orientation) = runAction(w, ActionKind.DOWNLOAD) {
        val (width, height) = RenderSizes.base(orientation)
        val bytes = repository.bytes(urls.image(w, width, height, Quality.FULL, ImageFormat.PNG, download = true))
        device.saveToGallery(bytes, fileName(w, width, height, "png"), "image/png")
        val label = if (orientation == Orientation.DESKTOP) "4K desktop wallpaper" else "Wallpaper"
        "$label saved to Pictures/${DeviceActions.FOLDER}"
    }

    fun apply(w: Wallpaper, target: WallpaperTarget) = runAction(w, ActionKind.APPLY) {
        val (width, height) = device.screenSize()
        val bytes = repository.bytes(urls.image(w, width, height, Quality.FULL, ImageFormat.PNG))
        device.setWallpaper(bytes, target)
        when (target) {
            WallpaperTarget.HOME -> "Home screen wallpaper set"
            WallpaperTarget.LOCK -> "Lock screen wallpaper set"
            WallpaperTarget.BOTH -> "Wallpaper set on home & lock screen"
        }
    }

    fun share(w: Wallpaper, orientation: Orientation, launch: (Intent) -> Unit) = runAction(w, ActionKind.SHARE) {
        val (width, height) = if (orientation == Orientation.PHONE) RenderSizes.PHONE_BASE else RenderSizes.DESKTOP_VIEW
        val bytes = repository.bytes(urls.image(w, width, height, Quality.FULL, ImageFormat.PNG))
        launch(device.shareIntent(bytes, fileName(w, width, height, "png"), "image/png", "${w.name} · made with WallBloom"))
        null
    }

    private fun runAction(w: Wallpaper, kind: ActionKind, block: suspend () -> String?) {
        if (_busy.value != null) return
        _busy.value = ActionProgress(w.id, kind)
        viewModelScope.launch {
            try {
                block()?.let { _messages.send(UiMessage(it)) }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                val verb = when (kind) { ActionKind.DOWNLOAD -> "Download"; ActionKind.APPLY -> "Setting wallpaper"; ActionKind.SHARE -> "Sharing" }
                _messages.send(UiMessage("$verb failed: ${e.message ?: "check your connection"}", isError = true))
            } finally {
                _busy.value = null
            }
        }
    }

    fun notify(text: String, isError: Boolean = false) = viewModelScope.launch { _messages.send(UiMessage(text, isError)) }

    private fun fileName(w: Wallpaper, width: Int, height: Int, ext: String) =
        "wallbloom_${w.key}_${width}x${height}_${w.seed}.$ext"

    companion object {
        const val DISCOVER = "__discover__"

        val Factory: ViewModelProvider.Factory = viewModelFactory {
            initializer {
                val app = this[ViewModelProvider.AndroidViewModelFactory.APPLICATION_KEY] as WallBloomApplication
                AppViewModel(app.repository, app.prefs, app.device)
            }
        }
    }
}
