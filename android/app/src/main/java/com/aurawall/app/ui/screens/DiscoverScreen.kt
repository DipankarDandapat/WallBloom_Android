@file:OptIn(ExperimentalMaterial3Api::class)

package com.aurawall.app.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyGridScope
import androidx.compose.foundation.lazy.grid.LazyGridState
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.PagerState
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CloudOff
import androidx.compose.material.icons.rounded.DesktopWindows
import androidx.compose.material.icons.rounded.Refresh
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.Settings
import androidx.compose.material.icons.rounded.Smartphone
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.util.lerp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.foundation.interaction.collectIsDraggedAsState
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.WallCollection
import com.aurawall.app.data.Wallpaper
import com.aurawall.app.ui.AppNavigator
import com.aurawall.app.ui.AppViewModel
import com.aurawall.app.ui.CatalogState
import com.aurawall.app.ui.FeedState
import com.aurawall.app.ui.components.DynamicIcon
import com.aurawall.app.ui.components.EmptyState
import com.aurawall.app.ui.components.SectionHeader
import com.aurawall.app.ui.components.SegmentedPill
import com.aurawall.app.ui.components.SkeletonCard
import com.aurawall.app.ui.components.WallpaperCard
import com.aurawall.app.ui.components.parseColor
import com.aurawall.app.ui.components.sharedKey
import com.aurawall.app.ui.theme.Brand
import kotlinx.coroutines.delay
import java.util.Calendar
import kotlin.math.absoluteValue

const val PHONE_ASPECT = 1290f / 2796f
const val DESKTOP_ASPECT = 16f / 9f
fun Orientation.aspect() = if (this == Orientation.PHONE) PHONE_ASPECT else DESKTOP_ASPECT
fun Orientation.columns() = 2

/** Bottom padding so content clears the floating navigation bar. */
val NavBarClearance = 110.dp

@Composable
fun DiscoverScreen(vm: AppViewModel, navigator: AppNavigator) {
    val catalogState by vm.catalog.collectAsStateWithLifecycle()
    val settings by vm.settings.collectAsStateWithLifecycle()
    val feeds by vm.feeds.collectAsStateWithLifecycle()
    val favorites by vm.favorites.collectAsStateWithLifecycle()
    val orientation = settings.orientation
    val feed = feeds[vm.feedKey(null)] ?: FeedState()
    val catalog = (catalogState as? CatalogState.Ready)?.catalog

    LaunchedEffect(catalog != null) { if (catalog != null) vm.ensureFeed(null) }

    val gridState = rememberLazyGridState()
    InfiniteScroll(gridState, feed) { vm.loadMore(null) }

    PullToRefreshBox(isRefreshing = feed.refreshing, onRefresh = { vm.refreshFeed(null) }, modifier = Modifier.fillMaxSize()) {
        LazyVerticalGrid(
            columns = GridCells.Fixed(orientation.columns()),
            state = gridState,
            contentPadding = PaddingValues(
                start = 16.dp, end = 16.dp,
                top = WindowInsets.statusBars.asPaddingValues().calculateTopPadding() + 8.dp,
                bottom = NavBarClearance,
            ),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            modifier = Modifier.fillMaxSize(),
        ) {
            fullSpan("top") { DiscoverTopBar(onSearch = navigator::search, onSettings = navigator::settings) }
            fullSpan("greeting") { Greeting() }
            fullSpan("orientation") {
                SegmentedPill(
                    listOf(Orientation.PHONE to "Phone", Orientation.DESKTOP to "Desktop"), orientation, vm::setOrientation,
                    icons = listOf(Icons.Rounded.Smartphone, Icons.Rounded.DesktopWindows), modifier = Modifier.fillMaxWidth(),
                )
            }
            when (catalogState) {
                is CatalogState.Loading -> {
                    fullSpan("loading") { ConnectingBanner((catalogState as CatalogState.Loading).slow) }
                    skeletons(orientation)
                }
                is CatalogState.Failed -> fullSpan("failed") {
                    EmptyState(
                        Icons.Rounded.CloudOff, "Can't reach WallBloom",
                        "Check your connection and try again. ${(catalogState as CatalogState.Failed).message}",
                        action = "Retry", onAction = vm::loadCatalog,
                    )
                }
                is CatalogState.Ready -> {
                    val ready = catalogState as CatalogState.Ready
                    if (ready.catalog.hero.isNotEmpty()) fullSpan("hero") {
                        HeroCarousel(ready.catalog.hero, orientation, vm) { index ->
                            navigator.preview(ready.catalog.hero, index, orientation, "hero")
                        }
                    }
                    if (ready.catalog.collections.isNotEmpty()) {
                        fullSpan("collections-header") { SectionHeader("Collections", subtitle = "Curated moods, refreshed daily") }
                        fullSpan("collections") { CollectionsRow(ready.catalog.collections, vm, onOpen = navigator::collection) }
                    }
                    fullSpan("feed-header") {
                        SectionHeader("For you", subtitle = "Pull down for a fresh shuffle", modifier = Modifier.padding(top = 8.dp))
                    }
                    feedItems(feed, orientation, vm, "discover", favorites.mapTo(HashSet()) { it.id }) { index ->
                        navigator.preview(feed.items, index, orientation, "discover")
                    }
                    feedFooter(feed, orientation) { vm.loadMore(null) }
                }
            }
        }
    }
}

fun LazyGridScope.fullSpan(key: String, content: @Composable () -> Unit) =
    item(key = key, span = { GridItemSpan(maxLineSpan) }) { content() }

fun LazyGridScope.skeletons(orientation: Orientation, count: Int = 6) =
    items(count, key = { "skeleton-$it" }) { SkeletonCard(Modifier.fillMaxWidth().aspectRatio(orientation.aspect())) }

fun LazyGridScope.feedItems(
    feed: FeedState,
    orientation: Orientation,
    vm: AppViewModel,
    origin: String,
    favoriteIds: Set<String>,
    onOpen: (Int) -> Unit,
) {
    itemsIndexed(feed.items, key = { _, item -> "$origin-${item.id}" }) { index, item ->
        WallpaperCard(
            item = item,
            url = vm.urls.thumb(item, orientation),
            onClick = { onOpen(index) },
            onLongClick = { vm.toggleFavorite(item) },
            sharedKey = sharedKey(item, orientation, origin),
            isFavorite = item.id in favoriteIds,
            modifier = Modifier.animateItem().fillMaxWidth().aspectRatio(orientation.aspect()),
        )
    }
}

fun LazyGridScope.feedFooter(feed: FeedState, orientation: Orientation, onRetry: () -> Unit) {
    when {
        feed.items.isEmpty() && feed.error == null -> skeletons(orientation, 4)
        feed.error != null -> fullSpan("feed-error") {
            Column(Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("Couldn't load more wallpapers", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(Modifier.height(10.dp))
                OutlinedButton(onRetry, shape = RoundedCornerShape(14.dp)) {
                    Icon(Icons.Rounded.Refresh, null, Modifier.size(18.dp)); Spacer(Modifier.width(6.dp)); Text("Try again")
                }
            }
        }
        feed.loading -> fullSpan("feed-loading") {
            Box(Modifier.fillMaxWidth().padding(20.dp), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(Modifier.size(28.dp), strokeWidth = 2.5.dp)
            }
        }
    }
}

/** Loads the next page when the user is within a few items of the end. */
@Composable
fun InfiniteScroll(state: LazyGridState, feed: FeedState, threshold: Int = 8, loadMore: () -> Unit) {
    val shouldLoad by remember(state) {
        derivedStateOf {
            val info = state.layoutInfo
            val last = info.visibleItemsInfo.lastOrNull()?.index ?: 0
            info.totalItemsCount > 0 && last >= info.totalItemsCount - threshold
        }
    }
    LaunchedEffect(state, feed.items.size, feed.error) {
        snapshotFlow { shouldLoad }.collect { if (it && !feed.loading && feed.error == null && feed.items.isNotEmpty()) loadMore() }
    }
}

@Composable
private fun DiscoverTopBar(onSearch: () -> Unit, onSettings: () -> Unit) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        BrandMark(36)
        Spacer(Modifier.width(10.dp))
        Text("WallBloom", style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onBackground, modifier = Modifier.weight(1f))
        IconButton(onSearch) { Icon(Icons.Rounded.Search, "Search wallpapers") }
        IconButton(onSettings) { Icon(Icons.Rounded.Settings, "Settings") }
    }
}

@Composable
fun BrandMark(size: Int) {
    Box(Modifier.size(size.dp).clip(RoundedCornerShape((size * .32f).dp)).background(Brand.Gradient), contentAlignment = Alignment.Center) {
        // Four-petal bloom drawn with circles, echoing the launcher icon.
        val petal = (size * .3f).dp
        Box(Modifier.size(petal).graphicsLayer { translationY = -size * .28f * density }.clip(CircleShape).background(Color.White))
        Box(Modifier.size(petal).graphicsLayer { translationY = size * .28f * density }.clip(CircleShape).background(Color.White))
        Box(Modifier.size(petal).graphicsLayer { translationX = -size * .28f * density }.clip(CircleShape).background(Color.White))
        Box(Modifier.size(petal).graphicsLayer { translationX = size * .28f * density }.clip(CircleShape).background(Color.White))
        Box(Modifier.size((size * .26f).dp).clip(CircleShape).background(Brand.Violet))
    }
}

@Composable
private fun Greeting() {
    val hour = remember { Calendar.getInstance().get(Calendar.HOUR_OF_DAY) }
    val greeting = when (hour) { in 5..11 -> "Good morning"; in 12..16 -> "Good afternoon"; in 17..21 -> "Good evening"; else -> "Late night picks" }
    Column(Modifier.padding(top = 6.dp, bottom = 2.dp)) {
        Text(greeting, style = MaterialTheme.typography.headlineLarge, color = MaterialTheme.colorScheme.onBackground)
        Text("Fresh wallpapers, rendered for you today", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun ConnectingBanner(slow: Boolean) {
    Row(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(MaterialTheme.colorScheme.surfaceContainerHigh).padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        CircularProgressIndicator(Modifier.size(22.dp), strokeWidth = 2.5.dp)
        Spacer(Modifier.width(14.dp))
        AnimatedContent(slow, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "connecting") { isSlow ->
            Column {
                Text(if (isSlow) "Waking up the wallpaper engine…" else "Connecting…", style = MaterialTheme.typography.titleSmall)
                if (isSlow) Text("The server sleeps when idle; the first launch can take up to a minute.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

@Composable
private fun HeroCarousel(items: List<Wallpaper>, orientation: Orientation, vm: AppViewModel, onOpen: (Int) -> Unit) {
    val pager = rememberPagerState { items.size }
    AutoAdvance(pager)
    val phone = orientation == Orientation.PHONE
    Column {
        HorizontalPager(
            pager,
            contentPadding = PaddingValues(horizontal = if (phone) 72.dp else 8.dp),
            pageSpacing = 14.dp,
            modifier = Modifier.fillMaxWidth().height(if (phone) 400.dp else 210.dp),
        ) { page ->
            val offset = ((pager.currentPage - page) + pager.currentPageOffsetFraction).absoluteValue.coerceIn(0f, 1f)
            val item = items[page]
            Box(
                Modifier.fillMaxSize().graphicsLayer {
                    // Depth effect: neighbours shrink and dim as they move away from centre.
                    val scale = lerp(1f, .88f, offset)
                    scaleX = scale; scaleY = scale
                    alpha = lerp(1f, .55f, offset)
                },
            ) {
                WallpaperCard(
                    item, vm.urls.thumb(item, orientation), onClick = { onOpen(page) },
                    sharedKey = sharedKey(item, orientation, "hero"), corner = 28.dp,
                    modifier = Modifier.fillMaxSize(),
                )
                Text(
                    "FEATURED", color = Color.White, style = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.align(Alignment.TopStart).padding(12.dp).clip(RoundedCornerShape(8.dp))
                        .background(Color.Black.copy(alpha = .35f)).padding(horizontal = 8.dp, vertical = 4.dp),
                )
            }
        }
        Spacer(Modifier.height(12.dp))
        PagerDots(pager, items.size, Modifier.align(Alignment.CenterHorizontally))
    }
}

@Composable
fun PagerDots(pager: PagerState, count: Int, modifier: Modifier = Modifier) {
    Row(modifier, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        repeat(count) { index ->
            val active = pager.currentPage == index
            val width by animateDpAsState(if (active) 22.dp else 7.dp, label = "dot")
            Box(
                Modifier.height(7.dp).width(width).clip(CircleShape)
                    .background(if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline),
            )
        }
    }
}

@Composable
private fun AutoAdvance(pager: PagerState) {
    val dragged by pager.interactionSource.collectIsDraggedAsState()
    LaunchedEffect(pager, dragged) {
        if (dragged || pager.pageCount < 2) return@LaunchedEffect
        while (true) {
            delay(5000)
            pager.animateScrollToPage((pager.currentPage + 1) % pager.pageCount)
        }
    }
}

@Composable
private fun CollectionsRow(collections: List<WallCollection>, vm: AppViewModel, onOpen: (String) -> Unit) {
    LazyRow(horizontalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(end = 16.dp)) {
        itemsIndexed(collections, key = { _, c -> c.id }) { _, collection ->
            CollectionCard(collection, vm.urls.thumb(collection.cover, Orientation.PHONE)) { onOpen(collection.id) }
        }
    }
}

@Composable
private fun CollectionCard(collection: WallCollection, coverUrl: String, onClick: () -> Unit) {
    val accent = parseColor(collection.accent)
    Box(Modifier.width(150.dp).height(200.dp)) {
        WallpaperCard(collection.cover, coverUrl, onClick = onClick, showLabel = false, corner = 24.dp, modifier = Modifier.fillMaxSize())
        Box(
            Modifier.fillMaxSize().clip(RoundedCornerShape(24.dp))
                .background(Brush.verticalGradient(listOf(Color.Transparent, accent.copy(alpha = .35f), Color.Black.copy(alpha = .82f)))),
        )
        Column(Modifier.align(Alignment.BottomStart).padding(12.dp)) {
            Box(Modifier.size(34.dp).clip(RoundedCornerShape(11.dp)).background(accent.copy(alpha = .9f)), contentAlignment = Alignment.Center) {
                DynamicIcon(collection.icon, collection.emoji, tint = Color.White, size = 20.dp)
            }
            Spacer(Modifier.height(8.dp))
            Text(collection.name, style = MaterialTheme.typography.titleSmall, color = Color.White)
            Text(collection.subtitle, style = MaterialTheme.typography.labelSmall, color = Color.White.copy(alpha = .75f), maxLines = 2, textAlign = TextAlign.Start)
        }
    }
}
