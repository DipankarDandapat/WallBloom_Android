package com.aurawall.app.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Casino
import androidx.compose.material.icons.rounded.DesktopWindows
import androidx.compose.material.icons.rounded.Favorite
import androidx.compose.material.icons.rounded.FavoriteBorder
import androidx.compose.material.icons.rounded.Fullscreen
import androidx.compose.material.icons.rounded.InvertColors
import androidx.compose.material.icons.rounded.Layers
import androidx.compose.material.icons.rounded.Palette
import androidx.compose.material.icons.rounded.Smartphone
import androidx.compose.material.icons.rounded.Texture
import androidx.compose.material.icons.rounded.Landscape
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.aurawall.app.data.Catalog
import com.aurawall.app.data.Kind
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.Quality
import com.aurawall.app.data.Wallpaper
import com.aurawall.app.ui.AppNavigator
import com.aurawall.app.ui.AppViewModel
import com.aurawall.app.ui.CatalogState
import com.aurawall.app.ui.StudioState
import com.aurawall.app.ui.components.AccentChip
import com.aurawall.app.ui.components.EmptyState
import com.aurawall.app.ui.components.PaletteChip
import com.aurawall.app.ui.components.PrimaryGradientButton
import com.aurawall.app.ui.components.SegmentedPill
import com.aurawall.app.ui.components.SkeletonCard
import com.aurawall.app.ui.components.WallpaperCard
import com.aurawall.app.ui.components.sharedKey
import kotlin.random.Random

/** Seed used for picker tiles so each tile is rendered (and cached) once per palette. */
private const val TILE_SEED = 31_337

@Composable
fun StudioScreen(vm: AppViewModel, navigator: AppNavigator) {
    val catalogState by vm.catalog.collectAsStateWithLifecycle()
    val studio by vm.studio.collectAsStateWithLifecycle()
    val settings by vm.settings.collectAsStateWithLifecycle()
    val favorites by vm.favorites.collectAsStateWithLifecycle()
    val catalog = (catalogState as? CatalogState.Ready)?.catalog
    if (catalog == null) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            EmptyState(Icons.Rounded.Palette, "Studio is warming up", "The pattern library loads with the catalog.")
        }
        return
    }
    val orientation = settings.orientation
    val wallpaper = vm.studioWallpaper(catalog, studio)
    val isFavorite = favorites.any { it.id == wallpaper.id }
    val update = vm::updateStudio

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).statusBarsPadding()
            .padding(start = 16.dp, end = 16.dp, top = 12.dp, bottom = NavBarClearance),
        verticalArrangement = Arrangement.spacedBy(18.dp),
    ) {
        Column {
            Text("Studio", style = MaterialTheme.typography.headlineLarge, color = MaterialTheme.colorScheme.onBackground)
            Text("Compose your own wallpaper from ${catalog.patterns.size} generators and ${catalog.palettes.size} palettes", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }

        StudioPreview(vm, wallpaper, orientation, isFavorite, onShuffle = { update { it.copy(seed = Random.nextInt(100_000, 999_999)) } }) {
            navigator.preview(listOf(wallpaper), 0, orientation, "studio")
        }

        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SegmentedPill(
                listOf(Kind.PATTERN to "Pattern", Kind.SCENE to "Scene"), studio.source, { kind -> update { it.copy(source = kind) } },
                icons = listOf(Icons.Rounded.Texture, Icons.Rounded.Landscape), modifier = Modifier.weight(1f),
            )
            SegmentedPill(
                listOf(Orientation.PHONE to "", Orientation.DESKTOP to ""), orientation, vm::setOrientation,
                icons = listOf(Icons.Rounded.Smartphone, Icons.Rounded.DesktopWindows), modifier = Modifier.width(112.dp),
            )
        }

        AnimatedContent(studio.source, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "studio-source") { source ->
            Column(verticalArrangement = Arrangement.spacedBy(18.dp)) {
                if (source == Kind.PATTERN) PatternControls(vm, catalog, studio)
                else SceneControls(vm, catalog, studio)
            }
        }

        PrimaryGradientButton(
            "Preview full screen", Icons.Rounded.Fullscreen,
            onClick = { navigator.preview(listOf(wallpaper), 0, orientation, "studio") }, modifier = Modifier.fillMaxWidth(),
        )
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            StudioAction(if (isFavorite) "Saved" else "Save", if (isFavorite) Icons.Rounded.Favorite else Icons.Rounded.FavoriteBorder, Modifier.weight(1f)) { vm.toggleFavorite(wallpaper) }
            StudioAction("Seed ${studio.seed}", Icons.Rounded.Casino, Modifier.weight(1f)) { update { it.copy(seed = Random.nextInt(100_000, 999_999)) } }
        }
    }
}

@Composable
private fun StudioPreview(vm: AppViewModel, w: Wallpaper, orientation: Orientation, favorite: Boolean, onShuffle: () -> Unit, onOpen: () -> Unit) {
    // The live preview uses a fast thumbnail render; the full-screen preview loads full quality.
    val (width, height) = if (orientation == Orientation.PHONE) 720 to 1560 else 1280 to 720
    val url = vm.urls.image(w, width, height, Quality.THUMB)
    Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
        Box(Modifier.then(if (orientation == Orientation.PHONE) Modifier.height(440.dp).aspectRatio(PHONE_ASPECT) else Modifier.fillMaxWidth().aspectRatio(DESKTOP_ASPECT))) {
            WallpaperCard(w, url, onClick = onOpen, sharedKey = sharedKey(w, orientation, "studio"), corner = 28.dp, isFavorite = favorite, modifier = Modifier.fillMaxSize())
            FilledTonalIconButton(onShuffle, modifier = Modifier.align(Alignment.TopStart).padding(10.dp)) {
                Icon(Icons.Rounded.Casino, "New variation")
            }
        }
    }
}

@Composable
private fun StudioAction(label: String, icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier, onClick: () -> Unit) {
    Row(
        modifier.clip(RoundedCornerShape(16.dp)).background(MaterialTheme.colorScheme.surfaceContainerHigh)
            .clickable(role = Role.Button, onClick = onClick).padding(vertical = 14.dp),
        horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, null, Modifier.size(18.dp), tint = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.width(8.dp))
        Text(label, style = MaterialTheme.typography.labelLarge, maxLines = 1, overflow = TextOverflow.Ellipsis,
            color = MaterialTheme.colorScheme.onSurface)
    }
}

@Composable
private fun ControlLabel(title: String, detail: String? = null) {
    Row(verticalAlignment = Alignment.Bottom) {
        Text(title, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onBackground, modifier = Modifier.weight(1f))
        detail?.let { Text(it, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant) }
    }
}

@Composable
private fun PatternControls(vm: AppViewModel, catalog: Catalog, s: StudioState) {
    val update = vm::updateStudio
    val category = s.patternCategory ?: catalog.pattern(s.pattern)?.category ?: catalog.patternCategories.firstOrNull()?.id
    val patterns = catalog.patterns.filter { category == null || it.category == category || catalog.patternCategories.size <= 1 }

    ControlLabel("Generator", catalog.pattern(s.pattern)?.name)
    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        items(catalog.patternCategories, key = { it.id }) { c ->
            AccentChip(c.name, c.icon, c.emoji, c.accent, c.id == category, onClick = { update { it.copy(patternCategory = c.id) } })
        }
    }
    TileRow(
        patterns.map { catalog.wallpaper(Kind.PATTERN, it.key, s.palette, TILE_SEED, s.inverted) },
        selectedKey = s.pattern, vm = vm,
    ) { key -> update { it.copy(pattern = key, patternCategory = category) } }

    ControlLabel("Palette", catalog.palette(s.palette)?.name)
    PaletteRow(catalog, s.palette, includeOriginal = false) { id -> update { it.copy(palette = id) } }

    ToggleRow("Invert colours", "Flip every colour for a negative look", Icons.Rounded.InvertColors, s.inverted) { v -> update { it.copy(inverted = v) } }
    ToggleRow("Blend a second pattern", "Layer two generators together", Icons.Rounded.Layers, s.blendEnabled) { v -> update { it.copy(blendEnabled = v) } }
    AnimatedVisibility(s.blendEnabled, enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            TileRow(
                catalog.patterns.filter { it.featured }.map { catalog.wallpaper(Kind.PATTERN, it.key, s.palette, TILE_SEED, s.inverted) },
                selectedKey = s.pattern2, vm = vm,
            ) { key -> update { it.copy(pattern2 = key) } }
            ControlLabel("Blend strength", "${(s.blend * 100).toInt()}%")
            // Round to 5% steps so slider movement maps onto a small, cacheable set of renders.
            Slider(s.blend, { v -> update { it.copy(blend = (v * 20).toInt() / 20f) } }, valueRange = 0f..1f, steps = 19)
        }
    }
}

@Composable
private fun SceneControls(vm: AppViewModel, catalog: Catalog, s: StudioState) {
    val update = vm::updateStudio
    val theme = catalog.sceneThemes.firstOrNull { it.id == s.sceneTheme } ?: catalog.scene(s.scene)?.first ?: catalog.sceneThemes.firstOrNull()
    ControlLabel("Scene", catalog.scene(s.scene)?.second?.name)
    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        items(catalog.sceneThemes, key = { it.id }) { t ->
            AccentChip(t.name, t.icon, t.emoji, t.accent, t.id == theme?.id, onClick = { update { it.copy(sceneTheme = t.id) } })
        }
    }
    TileRow(
        theme?.scenes.orEmpty().map { catalog.wallpaper(Kind.SCENE, it.key, s.scenePalette, TILE_SEED, s.inverted) },
        selectedKey = s.scene, vm = vm,
    ) { key -> update { it.copy(scene = key, sceneTheme = theme?.id) } }
    ControlLabel("Colours", if (s.scenePalette < 0) "Original" else catalog.palette(s.scenePalette)?.name)
    PaletteRow(catalog, s.scenePalette, includeOriginal = true, originalColors = catalog.scene(s.scene)?.second?.colors) { id -> update { it.copy(scenePalette = id) } }
    ToggleRow("Invert colours", "Flip every colour for a negative look", Icons.Rounded.InvertColors, s.inverted) { v -> update { it.copy(inverted = v) } }
}

@Composable
private fun TileRow(items: List<Wallpaper>, selectedKey: String, vm: AppViewModel, onPick: (String) -> Unit) {
    val state = rememberLazyListState(initialFirstVisibleItemIndex = items.indexOfFirst { it.key == selectedKey }.coerceAtLeast(0))
    LazyRow(state = state, horizontalArrangement = Arrangement.spacedBy(10.dp), contentPadding = PaddingValues(vertical = 2.dp)) {
        if (items.isEmpty()) items(4) { SkeletonCard(Modifier.width(84.dp).aspectRatio(PHONE_ASPECT), 16.dp) }
        items(items, key = { it.key }) { item ->
            val selected = item.key == selectedKey
            val scale by animateFloatAsState(if (selected) 1f else .94f, label = "tile")
            Column(Modifier.width(84.dp).graphicsLayer { scaleX = scale; scaleY = scale }, horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    Modifier.fillMaxWidth().aspectRatio(PHONE_ASPECT)
                        .border(BorderStroke(if (selected) 2.5.dp else 0.dp, if (selected) MaterialTheme.colorScheme.primary else Color.Transparent), RoundedCornerShape(18.dp))
                        .padding(if (selected) 3.dp else 0.dp),
                ) {
                    WallpaperCard(item, vm.urls.tile(item), onClick = { onPick(item.key) }, showLabel = false, corner = 15.dp, modifier = Modifier.fillMaxSize())
                }
                Spacer(Modifier.height(6.dp))
                Text(
                    item.name, style = MaterialTheme.typography.labelSmall, maxLines = 1, overflow = TextOverflow.Ellipsis,
                    color = if (selected) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
fun PaletteRow(catalog: Catalog, selected: Int, includeOriginal: Boolean, originalColors: List<String>? = null, onPick: (Int) -> Unit) {
    val initial = (if (includeOriginal) 1 else 0) + catalog.palettes.indexOfFirst { it.id == selected }.coerceAtLeast(0)
    val state = rememberLazyListState(initialFirstVisibleItemIndex = if (selected < 0) 0 else initial)
    LazyRow(state = state, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        if (includeOriginal) item(key = "original") {
            PaletteChip(null, selected < 0, onClick = { onPick(-1) }, label = "Original", colors = originalColors?.takeIf { it.isNotEmpty() } ?: listOf("#8B7CFF", "#FF7AB6", "#5CE1E6"))
        }
        items(catalog.palettes, key = { it.id }) { palette -> PaletteChip(palette, palette.id == selected, onClick = { onPick(palette.id) }) }
    }
}

@Composable
private fun ToggleRow(title: String, subtitle: String, icon: androidx.compose.ui.graphics.vector.ImageVector, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(MaterialTheme.colorScheme.surfaceContainerHigh)
            .clickable(role = Role.Switch) { onChange(!checked) }.padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, null, tint = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurface)
            Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Switch(checked, onChange)
    }
}
