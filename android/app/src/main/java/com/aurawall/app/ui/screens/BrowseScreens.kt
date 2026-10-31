@file:OptIn(ExperimentalMaterial3Api::class)

package com.aurawall.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.DesktopWindows
import androidx.compose.material.icons.rounded.FavoriteBorder
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.SearchOff
import androidx.compose.material.icons.rounded.Shuffle
import androidx.compose.material.icons.rounded.Smartphone
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.aurawall.app.data.Catalog
import com.aurawall.app.data.Kind
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.Wallpaper
import com.aurawall.app.ui.AppNavigator
import com.aurawall.app.ui.AppViewModel
import com.aurawall.app.ui.CatalogState
import com.aurawall.app.ui.FeedState
import com.aurawall.app.ui.components.AccentChip
import com.aurawall.app.ui.components.DynamicIcon
import com.aurawall.app.ui.components.EmptyState
import com.aurawall.app.ui.components.SegmentedPill
import com.aurawall.app.ui.components.WallpaperCard
import com.aurawall.app.ui.components.parseColor
import com.aurawall.app.ui.components.sharedKey
import kotlin.random.Random

@Composable
fun SubScreenTopBar(title: String, onBack: () -> Unit, subtitle: String? = null, leading: (@Composable () -> Unit)? = null, actions: @Composable () -> Unit = {}) {
    Row(Modifier.fillMaxWidth().statusBarsPadding().padding(horizontal = 4.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
        IconButton(onBack) { Icon(Icons.AutoMirrored.Rounded.ArrowBack, "Back") }
        leading?.let { it(); Spacer(Modifier.width(10.dp)) }
        Column(Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onBackground)
            subtitle?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant) }
        }
        actions()
    }
}

@Composable
private fun OrientationPill(orientation: Orientation, onChange: (Orientation) -> Unit, modifier: Modifier = Modifier) =
    SegmentedPill(
        listOf(Orientation.PHONE to "Phone", Orientation.DESKTOP to "Desktop"), orientation, onChange,
        icons = listOf(Icons.Rounded.Smartphone, Icons.Rounded.DesktopWindows), modifier = modifier,
    )

// ---------------------------------------------------------------------------------------------
// Collection
// ---------------------------------------------------------------------------------------------

@Composable
fun CollectionScreen(vm: AppViewModel, navigator: AppNavigator, id: String) {
    val catalog = (vm.catalog.collectAsStateWithLifecycle().value as? CatalogState.Ready)?.catalog
    val settings by vm.settings.collectAsStateWithLifecycle()
    val feeds by vm.feeds.collectAsStateWithLifecycle()
    val favorites by vm.favorites.collectAsStateWithLifecycle()
    val collection = catalog?.collections?.firstOrNull { it.id == id }
    val feed = feeds[vm.feedKey(id)] ?: FeedState()
    val orientation = settings.orientation
    LaunchedEffect(id, catalog != null) { if (catalog != null) vm.ensureFeed(id) }
    val grid = rememberLazyGridState()
    InfiniteScroll(grid, feed) { vm.loadMore(id) }

    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        SubScreenTopBar(
            collection?.name ?: "Collection", navigator::back, collection?.subtitle,
            leading = collection?.let { c ->
                {
                    Box(Modifier.size(38.dp).clip(RoundedCornerShape(12.dp)).background(parseColor(c.accent)), contentAlignment = Alignment.Center) {
                        DynamicIcon(c.icon, c.emoji, Color.White, 22.dp)
                    }
                }
            },
        )
        PullToRefreshBox(feed.refreshing, onRefresh = { vm.refreshFeed(id) }, modifier = Modifier.fillMaxSize()) {
            LazyVerticalGrid(
                GridCells.Fixed(orientation.columns()), state = grid,
                contentPadding = PaddingValues(16.dp, 4.dp, 16.dp, 24.dp + WindowInsets.navigationBars.asPaddingValues().calculateBottomPadding()),
                horizontalArrangement = Arrangement.spacedBy(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                fullSpan("orientation") { OrientationPill(orientation, vm::setOrientation, Modifier.fillMaxWidth()) }
                feedItems(feed, orientation, vm, "collection-$id", favorites.mapTo(HashSet()) { it.id }) { index ->
                    navigator.preview(feed.items, index, orientation, "collection-$id")
                }
                feedFooter(feed, orientation) { vm.loadMore(id) }
            }
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Scenes
// ---------------------------------------------------------------------------------------------

@Composable
fun ScenesScreen(vm: AppViewModel, navigator: AppNavigator) {
    val state by vm.catalog.collectAsStateWithLifecycle()
    val settings by vm.settings.collectAsStateWithLifecycle()
    val favorites by vm.favorites.collectAsStateWithLifecycle()
    val catalog = (state as? CatalogState.Ready)?.catalog
    var themeId by rememberSaveable { mutableStateOf<String?>(null) }
    // One seed per visit keeps thumbnails cacheable; "Shuffle" re-rolls every scene's variation.
    var seed by rememberSaveable { mutableIntStateOf(20_251) }
    val orientation = settings.orientation
    val theme = catalog?.sceneThemes?.firstOrNull { it.id == themeId } ?: catalog?.sceneThemes?.firstOrNull()
    val items = remember(catalog, theme, seed) {
        if (catalog == null || theme == null) emptyList()
        else theme.scenes.mapIndexed { i, scene -> catalog.wallpaper(Kind.SCENE, scene.key, -1, seed + i * 7919) }
    }
    val favoriteIds = favorites.mapTo(HashSet()) { it.id }

    LazyVerticalGrid(
        GridCells.Fixed(orientation.columns()),
        contentPadding = PaddingValues(16.dp, WindowInsets.statusBars.asPaddingValues().calculateTopPadding() + 12.dp, 16.dp, NavBarClearance),
        horizontalArrangement = Arrangement.spacedBy(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp),
        modifier = Modifier.fillMaxSize(),
    ) {
        fullSpan("title") {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("Scenes", style = MaterialTheme.typography.headlineLarge, color = MaterialTheme.colorScheme.onBackground)
                    Text(
                        "${catalog?.sceneThemes?.sumOf { it.scenes.size } ?: 0} illustrated worlds across ${catalog?.sceneThemes?.size ?: 0} themes",
                        style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                IconButton({ seed = Random.nextInt(100_000, 999_999) }) { Icon(Icons.Rounded.Shuffle, "New variations") }
            }
        }
        fullSpan("orientation") { OrientationPill(orientation, vm::setOrientation, Modifier.fillMaxWidth()) }
        if (catalog == null) {
            skeletons(orientation)
        } else {
            fullSpan("themes") {
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(catalog.sceneThemes, key = { it.id }) { t ->
                        AccentChip("${t.name} · ${t.scenes.size}", t.icon, t.emoji, t.accent, t.id == theme?.id, onClick = { themeId = t.id })
                    }
                }
            }
            if (theme != null && theme.description.isNotBlank()) fullSpan("theme-desc") {
                Text(theme.description, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            itemsIndexed(items, key = { _, item -> "scenes-${item.id}" }) { index, item ->
                WallpaperCard(
                    item, vm.urls.thumb(item, orientation), onClick = { navigator.preview(items, index, orientation, "scenes") },
                    onLongClick = { vm.toggleFavorite(item) }, sharedKey = sharedKey(item, orientation, "scenes"),
                    isFavorite = item.id in favoriteIds,
                    modifier = Modifier.animateItem().fillMaxWidth().aspectRatio(orientation.aspect()),
                )
            }
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Saved
// ---------------------------------------------------------------------------------------------

@Composable
fun SavedScreen(vm: AppViewModel, navigator: AppNavigator, onExplore: () -> Unit) {
    val favorites by vm.favorites.collectAsStateWithLifecycle()
    val settings by vm.settings.collectAsStateWithLifecycle()
    val orientation = settings.orientation
    if (favorites.isEmpty()) {
        Box(Modifier.fillMaxSize().padding(bottom = NavBarClearance), contentAlignment = Alignment.Center) {
            EmptyState(
                Icons.Rounded.FavoriteBorder, "No favourites yet",
                "Tap the heart in a preview, or long-press any wallpaper, to keep it here.",
                action = "Discover wallpapers", onAction = onExplore,
            )
        }
        return
    }
    LazyVerticalGrid(
        GridCells.Fixed(orientation.columns()),
        contentPadding = PaddingValues(16.dp, WindowInsets.statusBars.asPaddingValues().calculateTopPadding() + 12.dp, 16.dp, NavBarClearance),
        horizontalArrangement = Arrangement.spacedBy(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp),
        modifier = Modifier.fillMaxSize(),
    ) {
        fullSpan("title") {
            Column {
                Text("Saved", style = MaterialTheme.typography.headlineLarge, color = MaterialTheme.colorScheme.onBackground)
                Text("${favorites.size} favourite${if (favorites.size == 1) "" else "s"} · long-press to remove", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
        fullSpan("orientation") { OrientationPill(orientation, vm::setOrientation, Modifier.fillMaxWidth()) }
        itemsIndexed(favorites, key = { _, item -> "saved-${item.id}" }) { index, item ->
            WallpaperCard(
                item, vm.urls.thumb(item, orientation), onClick = { navigator.preview(favorites, index, orientation, "saved") },
                onLongClick = { vm.toggleFavorite(item) }, sharedKey = sharedKey(item, orientation, "saved"),
                modifier = Modifier.animateItem().fillMaxWidth().aspectRatio(orientation.aspect()),
            )
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------------------------

private val Suggestions = listOf("Minimal", "Sunset", "Galaxy", "Neon", "Ocean", "Forest", "Gradient", "Mountains", "Geometric", "Night")

/** Searches the catalog by name, theme, category and palette, then renders each hit as a wallpaper. */
fun searchCatalog(catalog: Catalog, query: String, seed: Int = 77_777): List<Wallpaper> {
    val q = query.trim().lowercase()
    if (q.length < 2) return emptyList()
    val scenes = catalog.sceneThemes.flatMap { theme ->
        theme.scenes.filter { q in it.name.lowercase() || q in it.key || q in theme.name.lowercase() }
            .map { catalog.wallpaper(Kind.SCENE, it.key, -1, seed) }
    }
    val categoryNames = catalog.patternCategories.associate { it.id to it.name.lowercase() }
    val palettes = catalog.palettes.filter { q in it.name.lowercase() || it.tags.any { tag -> q in tag } }
    val patternHits = catalog.patterns.filter { q in it.name.lowercase() || q in it.key || q in categoryNames[it.category].orEmpty() }
    val patterns = patternHits.mapIndexed { i, p ->
        val palette = catalog.palettes.getOrNull((p.key.hashCode() and 0x7fffffff) % catalog.palettes.size.coerceAtLeast(1))?.id ?: 0
        catalog.wallpaper(Kind.PATTERN, p.key, palette, seed + i)
    }
    // A palette match shows the best patterns dressed in that palette.
    val featured = catalog.patterns.filter { it.featured }.take(8)
    val paletteHits = palettes.take(3).flatMap { pal -> featured.mapIndexed { i, p -> catalog.wallpaper(Kind.PATTERN, p.key, pal.id, seed + 31 * i) } }
    return (scenes + patterns + paletteHits).distinctBy { it.id }.take(60)
}

@Composable
fun SearchScreen(vm: AppViewModel, navigator: AppNavigator) {
    val catalog = (vm.catalog.collectAsStateWithLifecycle().value as? CatalogState.Ready)?.catalog
    val settings by vm.settings.collectAsStateWithLifecycle()
    var query by rememberSaveable { mutableStateOf("") }
    val results = remember(catalog, query) { if (catalog == null) emptyList() else searchCatalog(catalog, query) }
    val focus = remember { FocusRequester() }
    val focusManager = LocalFocusManager.current
    val orientation = settings.orientation
    LaunchedEffect(Unit) { runCatching { focus.requestFocus() } }

    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(Modifier.statusBarsPadding().padding(horizontal = 8.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(navigator::back) { Icon(Icons.AutoMirrored.Rounded.ArrowBack, "Back") }
            TextField(
                query, { query = it },
                placeholder = { Text("Scenes, patterns, colours…") },
                leadingIcon = { Icon(Icons.Rounded.Search, null) },
                trailingIcon = { if (query.isNotEmpty()) IconButton({ query = "" }) { Icon(Icons.Rounded.Close, "Clear search") } },
                singleLine = true,
                shape = RoundedCornerShape(18.dp),
                colors = TextFieldDefaults.colors(
                    focusedIndicatorColor = Color.Transparent, unfocusedIndicatorColor = Color.Transparent,
                    focusedContainerColor = MaterialTheme.colorScheme.surfaceContainerHigh, unfocusedContainerColor = MaterialTheme.colorScheme.surfaceContainerHigh,
                ),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                keyboardActions = KeyboardActions(onSearch = { focusManager.clearFocus() }),
                modifier = Modifier.weight(1f).focusRequester(focus),
            )
        }
        when {
            query.trim().length < 2 -> Column(Modifier.padding(20.dp)) {
                Text("Try searching for", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(Modifier.size(12.dp))
                FlowChips(Suggestions) { query = it }
            }
            results.isEmpty() -> EmptyState(Icons.Rounded.SearchOff, "Nothing found", "Try a mood like \"calm\", a colour like \"violet\" or a place like \"Paris\".", Modifier.fillMaxWidth())
            else -> LazyVerticalGrid(
                GridCells.Fixed(orientation.columns()),
                contentPadding = PaddingValues(16.dp, 4.dp, 16.dp, 24.dp + WindowInsets.navigationBars.asPaddingValues().calculateBottomPadding()),
                horizontalArrangement = Arrangement.spacedBy(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                fullSpan("count") { Text("${results.size} results", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                itemsIndexed(results, key = { _, item -> "search-${item.id}" }) { index, item ->
                    WallpaperCard(
                        item, vm.urls.thumb(item, orientation), onClick = { navigator.preview(results, index, orientation, "search") },
                        onLongClick = { vm.toggleFavorite(item) }, sharedKey = sharedKey(item, orientation, "search"),
                        modifier = Modifier.animateItem().fillMaxWidth().aspectRatio(orientation.aspect()),
                    )
                }
            }
        }
    }
}

@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
private fun FlowChips(items: List<String>, onClick: (String) -> Unit) {
    androidx.compose.foundation.layout.FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        items.forEach { label -> AccentChip(label, null, "🔎", "#8B7CFF", false, onClick = { onClick(label) }) }
    }
}
