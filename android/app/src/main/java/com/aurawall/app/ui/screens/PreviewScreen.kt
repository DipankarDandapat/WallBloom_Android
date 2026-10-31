@file:OptIn(ExperimentalMaterial3Api::class, androidx.compose.foundation.ExperimentalFoundationApi::class)

package com.aurawall.app.ui.screens

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.rememberTransformableState
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.AddToHomeScreen
import androidx.compose.material.icons.rounded.Casino
import androidx.compose.material.icons.rounded.Download
import androidx.compose.material.icons.rounded.Favorite
import androidx.compose.material.icons.rounded.FavoriteBorder
import androidx.compose.material.icons.rounded.Home
import androidx.compose.material.icons.rounded.Info
import androidx.compose.material.icons.rounded.Lock
import androidx.compose.material.icons.rounded.Palette
import androidx.compose.material.icons.rounded.PhonelinkLock
import androidx.compose.material.icons.rounded.Share
import androidx.compose.material.icons.rounded.Smartphone
import androidx.compose.material.icons.rounded.Wallpaper
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.aurawall.app.data.Catalog
import com.aurawall.app.data.Kind
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.Quality
import com.aurawall.app.data.RenderSizes
import com.aurawall.app.data.Wallpaper
import com.aurawall.app.data.WallpaperTarget
import com.aurawall.app.ui.ActionKind
import com.aurawall.app.ui.AppViewModel
import com.aurawall.app.ui.CatalogState
import com.aurawall.app.ui.components.GlassIconButton
import com.aurawall.app.ui.components.PaletteStrip
import com.aurawall.app.ui.components.PrimaryGradientButton
import com.aurawall.app.ui.components.placeholderBrush
import com.aurawall.app.ui.components.sharedKey
import com.aurawall.app.ui.components.sharedWallpaper
import com.aurawall.app.ui.theme.Brand
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.random.Random

private enum class Mockup { NONE, LOCK, HOME }

@Composable
fun PreviewScreen(vm: AppViewModel, origin: String, onBack: () -> Unit) {
    val session = vm.preview.collectAsStateWithLifecycle().value
    if (session == null || session.items.isEmpty()) {
        LaunchedEffect(Unit) { onBack() }
        return
    }
    val catalog = (vm.catalog.collectAsStateWithLifecycle().value as? CatalogState.Ready)?.catalog
    val favorites by vm.favorites.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    val orientation = session.orientation
    val phone = orientation == Orientation.PHONE
    val pager = rememberPagerState(initialPage = session.startIndex) { session.items.size }
    val item = session.items[pager.currentPage.coerceIn(0, session.items.lastIndex)]
    val originalStart = remember { session.items[session.startIndex].id }
    val context = LocalContext.current

    var chrome by remember { mutableStateOf(true) }
    var zoomed by remember { mutableStateOf(false) }
    var mockup by remember { mutableStateOf(Mockup.NONE) }
    var recolor by remember { mutableStateOf(false) }
    var applySheet by remember { mutableStateOf(false) }
    var infoSheet by remember { mutableStateOf(false) }
    val isFavorite = favorites.any { it.id == item.id }

    ImmersiveMode()

    // Android 8-9 need storage permission to write into Pictures/.
    val storagePermission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) vm.download(item, orientation) else vm.notify("Storage permission is needed to save wallpapers", isError = true)
    }
    val download = {
        val needsPermission = Build.VERSION.SDK_INT < Build.VERSION_CODES.Q &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
        if (needsPermission) storagePermission.launch(Manifest.permission.WRITE_EXTERNAL_STORAGE) else vm.download(item, orientation)
    }

    Box(Modifier.fillMaxSize().background(Color.Black)) {
        HorizontalPager(pager, userScrollEnabled = !zoomed, beyondViewportPageCount = 1, modifier = Modifier.fillMaxSize()) { page ->
            val pageItem = session.items[page]
            val key = if (pageItem.id == originalStart && page == session.startIndex) sharedKey(pageItem, orientation, origin) else null
            ZoomableWallpaper(
                vm, pageItem, orientation, key,
                onTap = { chrome = !chrome },
                onZoomChange = { if (page == pager.currentPage) zoomed = it },
            )
        }

        if (phone) DeviceMockup(mockup)

        // Soft scrims keep controls legible on bright wallpapers.
        AnimatedVisibility(chrome, enter = fadeIn(), exit = fadeOut()) {
            Box(Modifier.fillMaxSize()) {
                Box(Modifier.fillMaxWidth().height(160.dp).background(Brush.verticalGradient(listOf(Color.Black.copy(alpha = .55f), Color.Transparent))))
                Box(Modifier.align(Alignment.BottomCenter).fillMaxWidth().height(300.dp).background(Brush.verticalGradient(listOf(Color.Transparent, Color.Black.copy(alpha = .7f)))))
            }
        }

        AnimatedVisibility(
            chrome, enter = fadeIn() + slideInVertically { -it / 2 }, exit = fadeOut() + slideOutVertically { -it / 2 },
            modifier = Modifier.align(Alignment.TopCenter),
        ) {
            Row(Modifier.fillMaxWidth().statusBarsPadding().padding(horizontal = 12.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                GlassIconButton(Icons.AutoMirrored.Rounded.ArrowBack, "Back", onBack)
                Spacer(Modifier.width(12.dp))
                Column(Modifier.weight(1f)) {
                    AnimatedContent(item.name, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "title") {
                        Text(it, color = Color.White, style = MaterialTheme.typography.titleMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                    Text(
                        listOf(item.subtitle, if (session.items.size > 1) "${pager.currentPage + 1} / ${session.items.size}" else null).filterNot { it.isNullOrBlank() }.joinToString(" · "),
                        color = Color.White.copy(alpha = .7f), style = MaterialTheme.typography.labelMedium, maxLines = 1,
                    )
                }
                if (phone) {
                    GlassIconButton(
                        when (mockup) { Mockup.NONE -> Icons.Rounded.Smartphone; Mockup.LOCK -> Icons.Rounded.Lock; Mockup.HOME -> Icons.Rounded.Home },
                        "Preview on lock or home screen",
                        onClick = { mockup = Mockup.entries[(mockup.ordinal + 1) % Mockup.entries.size] },
                    )
                    Spacer(Modifier.width(8.dp))
                }
                FavoriteButton(isFavorite) { vm.toggleFavorite(item) }
            }
        }

        AnimatedVisibility(
            chrome, enter = fadeIn() + slideInVertically { it / 2 }, exit = fadeOut() + slideOutVertically { it / 2 },
            modifier = Modifier.align(Alignment.BottomCenter),
        ) {
            Column(Modifier.fillMaxWidth().navigationBarsPadding().padding(horizontal = 16.dp, vertical = 12.dp)) {
                AnimatedVisibility(recolor && catalog != null, enter = expandVertically() + fadeIn(), exit = shrinkVertically() + fadeOut()) {
                    if (catalog != null) RecolorRow(catalog, item) { paletteId ->
                        vm.replacePreviewItem(pager.currentPage, rebuild(catalog, item, palette = paletteId))
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.padding(bottom = 12.dp)) {
                    QuickChip(Icons.Rounded.Casino, "Shuffle") {
                        if (catalog != null) vm.replacePreviewItem(pager.currentPage, rebuild(catalog, item, seed = Random.nextInt(100_000, 999_999)))
                    }
                    QuickChip(Icons.Rounded.Palette, "Recolour", active = recolor) { recolor = !recolor }
                    QuickChip(Icons.Rounded.Info, "Details") { infoSheet = true }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                    val downloading = busy?.let { it.kind == ActionKind.DOWNLOAD && it.wallpaperId == item.id } == true
                    val sharing = busy?.let { it.kind == ActionKind.SHARE && it.wallpaperId == item.id } == true
                    val applying = busy?.let { it.kind == ActionKind.APPLY && it.wallpaperId == item.id } == true
                    if (phone) {
                        RoundAction(Icons.Rounded.Download, "Download", downloading, download)
                        PrimaryGradientButton("Set wallpaper", Icons.Rounded.Wallpaper, onClick = { applySheet = true }, loading = applying, modifier = Modifier.weight(1f))
                    } else {
                        PrimaryGradientButton("Download 4K", Icons.Rounded.Download, onClick = download, loading = downloading, modifier = Modifier.weight(1f))
                    }
                    RoundAction(Icons.Rounded.Share, "Share", sharing) { vm.share(item, orientation) { intent -> context.startActivity(intent) } }
                }
            }
        }

        if (busy?.kind == ActionKind.APPLY) BusyOverlay("Setting wallpaper…")
    }

    if (applySheet) ApplySheet(onDismiss = { applySheet = false }) { target ->
        applySheet = false
        if (!vm.device.canSetWallpaper) vm.notify("This device doesn't allow changing the wallpaper", isError = true)
        else vm.apply(item, target)
    }
    if (infoSheet) InfoSheet(item, orientation, catalog, vm) { infoSheet = false }
}

private fun rebuild(catalog: Catalog, w: Wallpaper, palette: Int = w.palette, seed: Int = w.seed): Wallpaper =
    catalog.wallpaper(w.kind, w.key, palette, seed, w.inverted, w.key2, w.blend)

/** Pinch / double-tap zoom. Panning only engages while zoomed so the pager can still swipe. */
@Composable
private fun ZoomableWallpaper(
    vm: AppViewModel,
    item: Wallpaper,
    orientation: Orientation,
    sharedKey: String?,
    onTap: () -> Unit,
    onZoomChange: (Boolean) -> Unit,
) {
    var scale by remember(item.id) { mutableFloatStateOf(1f) }
    var offset by remember(item.id) { mutableStateOf(Offset.Zero) }
    val animatedScale by animateFloatAsState(scale, spring(Spring.DampingRatioNoBouncy, Spring.StiffnessMediumLow), label = "zoom")
    val transform = rememberTransformableState { zoom, pan, _ ->
        scale = (scale * zoom).coerceIn(1f, 4f)
        offset = if (scale > 1f) offset + pan * scale else Offset.Zero
        onZoomChange(scale > 1.01f)
    }
    val phone = orientation == Orientation.PHONE
    val thumbUrl = vm.urls.thumb(item, orientation)
    val (w, h) = if (phone) vm.device.screenSize() else RenderSizes.DESKTOP_VIEW
    val fullUrl = vm.urls.image(item, w, h, Quality.FULL)
    val context = LocalContext.current

    Box(
        Modifier.fillMaxSize()
            .pointerInput(item.id) {
                detectTapGestures(
                    onTap = { onTap() },
                    onDoubleTap = {
                        if (scale > 1f) { scale = 1f; offset = Offset.Zero } else scale = 2.5f
                        onZoomChange(scale > 1f)
                    },
                )
            }
            .transformable(transform, canPan = { scale > 1f }),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            Modifier
                .then(if (phone) Modifier.fillMaxSize() else Modifier.fillMaxWidth().aspectRatio(DESKTOP_ASPECT))
                .sharedWallpaper(sharedKey)
                .graphicsLayer { scaleX = animatedScale; scaleY = animatedScale; translationX = offset.x; translationY = offset.y }
                .background(placeholderBrush(item.colors, Color.DarkGray)),
        ) {
            AsyncImage(
                model = ImageRequest.Builder(context).data(fullUrl).memoryCacheKey(fullUrl)
                    // The grid thumbnail is already in memory: show it instantly, then sharpen.
                    .placeholderMemoryCacheKey(thumbUrl).crossfade(300).build(),
                contentDescription = item.name,
                contentScale = if (phone) ContentScale.Crop else ContentScale.Fit,
                modifier = Modifier.fillMaxSize(),
            )
        }
    }
}

@Composable
private fun ImmersiveMode() {
    val view = LocalView.current
    DisposableEffect(view) {
        val window = (view.context as? Activity)?.window
        val controller = window?.let { WindowCompat.getInsetsController(it, view) }
        controller?.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        controller?.hide(WindowInsetsCompat.Type.statusBars())
        val wasLight = controller?.isAppearanceLightNavigationBars
        controller?.isAppearanceLightNavigationBars = false
        onDispose {
            controller?.show(WindowInsetsCompat.Type.statusBars())
            if (wasLight != null) controller.isAppearanceLightNavigationBars = wasLight
        }
    }
}

/** Lock-screen clock or home-screen icon grid drawn over the wallpaper for a realistic preview. */
@Composable
private fun DeviceMockup(mockup: Mockup) {
    AnimatedContent(mockup, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "mockup", modifier = Modifier.fillMaxSize()) { mode ->
        when (mode) {
            Mockup.NONE -> Box(Modifier.fillMaxSize())
            Mockup.LOCK -> Column(Modifier.fillMaxSize().statusBarsPadding().padding(top = 110.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                val now = remember { Date() }
                Text(SimpleDateFormat("EEEE, d MMMM", Locale.getDefault()).format(now), color = Color.White, fontSize = 17.sp, fontWeight = FontWeight.Medium)
                Text(SimpleDateFormat("HH:mm", Locale.getDefault()).format(now), color = Color.White, fontSize = 92.sp, fontWeight = FontWeight.Light, letterSpacing = (-2).sp)
            }
            Mockup.HOME -> Column(Modifier.fillMaxSize().statusBarsPadding().padding(top = 120.dp, start = 28.dp, end = 28.dp)) {
                repeat(2) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        repeat(4) { MockIcon() }
                    }
                    Spacer(Modifier.height(26.dp))
                }
                Spacer(Modifier.weight(1f))
                Row(
                    Modifier.fillMaxWidth().padding(bottom = 210.dp).clip(RoundedCornerShape(30.dp)).background(Color.White.copy(alpha = .18f)).padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) { repeat(4) { MockIcon() } }
            }
        }
    }
}

@Composable
private fun MockIcon() = Box(Modifier.size(54.dp).clip(RoundedCornerShape(17.dp)).background(Color.White.copy(alpha = .78f)))

@Composable
private fun FavoriteButton(active: Boolean, onClick: () -> Unit) {
    val scale by animateFloatAsState(if (active) 1.15f else 1f, spring(Spring.DampingRatioHighBouncy, Spring.StiffnessMedium), label = "fav")
    Box(Modifier.graphicsLayer { scaleX = scale; scaleY = scale }) {
        GlassIconButton(
            if (active) Icons.Rounded.Favorite else Icons.Rounded.FavoriteBorder,
            if (active) "Remove from favourites" else "Add to favourites", onClick,
            tint = if (active) Brand.Pink else Color.White,
        )
    }
}

@Composable
private fun QuickChip(icon: ImageVector, label: String, active: Boolean = false, onClick: () -> Unit) {
    Surface(
        onClick = onClick, shape = RoundedCornerShape(50),
        color = if (active) Color.White.copy(alpha = .28f) else Color.Black.copy(alpha = .35f),
        border = BorderStroke(1.dp, Color.White.copy(alpha = .16f)),
    ) {
        Row(Modifier.padding(horizontal = 14.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, null, tint = Color.White, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(6.dp))
            Text(label, color = Color.White, style = MaterialTheme.typography.labelLarge)
        }
    }
}

@Composable
private fun RoundAction(icon: ImageVector, label: String, loading: Boolean, onClick: () -> Unit) {
    Surface(
        onClick = onClick, enabled = !loading, shape = RoundedCornerShape(18.dp), modifier = Modifier.size(54.dp),
        color = Color.White.copy(alpha = .16f), border = BorderStroke(1.dp, Color.White.copy(alpha = .2f)),
    ) {
        Box(contentAlignment = Alignment.Center) {
            AnimatedContent(loading, transitionSpec = { scaleIn() togetherWith scaleOut() }, label = label) { busy ->
                if (busy) androidx.compose.material3.CircularProgressIndicator(Modifier.size(22.dp), color = Color.White, strokeWidth = 2.dp)
                else Icon(icon, label, tint = Color.White)
            }
        }
    }
}

@Composable
private fun RecolorRow(catalog: Catalog, item: Wallpaper, onPick: (Int) -> Unit) {
    Box(Modifier.padding(bottom = 12.dp).clip(RoundedCornerShape(22.dp)).background(Color.Black.copy(alpha = .45f)).padding(vertical = 12.dp, horizontal = 8.dp)) {
        PaletteRowDark(catalog, item, onPick)
    }
}

@Composable
private fun PaletteRowDark(catalog: Catalog, item: Wallpaper, onPick: (Int) -> Unit) {
    val originalColors = if (item.kind == Kind.SCENE) catalog.scene(item.key)?.second?.colors else null
    androidx.compose.material3.MaterialTheme(colorScheme = androidx.compose.material3.darkColorScheme(primary = Color.White, onSurface = Color.White, onSurfaceVariant = Color.White.copy(alpha = .7f))) {
        PaletteRow(catalog, item.palette, includeOriginal = item.kind == Kind.SCENE, originalColors = originalColors, onPick = onPick)
    }
}

@Composable
private fun BusyOverlay(text: String) {
    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = .45f)).clickable(enabled = true, onClick = {}), contentAlignment = Alignment.Center) {
        Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
            Row(Modifier.padding(horizontal = 24.dp, vertical = 20.dp), verticalAlignment = Alignment.CenterVertically) {
                androidx.compose.material3.CircularProgressIndicator(Modifier.size(24.dp), strokeWidth = 2.5.dp)
                Spacer(Modifier.width(16.dp))
                Text(text, style = MaterialTheme.typography.titleSmall)
            }
        }
    }
}

@Composable
private fun ApplySheet(onDismiss: () -> Unit, onApply: (WallpaperTarget) -> Unit) {
    val state = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val scope = rememberCoroutineScope()
    ModalBottomSheet(onDismissRequest = onDismiss, sheetState = state, containerColor = MaterialTheme.colorScheme.surfaceContainer) {
        Column(Modifier.padding(horizontal = 20.dp).padding(bottom = 28.dp)) {
            Text("Set wallpaper", style = MaterialTheme.typography.headlineSmall)
            Text("Rendered pixel-perfect for this screen", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(18.dp))
            listOf(
                Triple(WallpaperTarget.HOME, Icons.Rounded.AddToHomeScreen, "Home screen" to "Behind your apps and widgets"),
                Triple(WallpaperTarget.LOCK, Icons.Rounded.PhonelinkLock, "Lock screen" to "What you see before unlocking"),
                Triple(WallpaperTarget.BOTH, Icons.Rounded.Wallpaper, "Home & lock screens" to "One look everywhere"),
            ).forEach { (target, icon, text) ->
                Row(
                    Modifier.fillMaxWidth().padding(vertical = 5.dp).clip(RoundedCornerShape(18.dp))
                        .background(MaterialTheme.colorScheme.surfaceContainerHigh)
                        .clickable(role = Role.Button) { scope.launch { state.hide() }.invokeOnCompletion { onApply(target) } }
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(Modifier.size(44.dp).clip(RoundedCornerShape(14.dp)).background(Brand.SoftGradient), contentAlignment = Alignment.Center) {
                        Icon(icon, null, tint = Color.White)
                    }
                    Spacer(Modifier.width(14.dp))
                    Column {
                        Text(text.first, style = MaterialTheme.typography.titleSmall)
                        Text(text.second, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
    }
}

@Composable
private fun InfoSheet(item: Wallpaper, orientation: Orientation, catalog: Catalog?, vm: AppViewModel, onDismiss: () -> Unit) {
    ModalBottomSheet(onDismissRequest = onDismiss, containerColor = MaterialTheme.colorScheme.surfaceContainer) {
        Column(Modifier.padding(horizontal = 20.dp).padding(bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Text(item.name, style = MaterialTheme.typography.headlineSmall)
            PaletteStrip(item.colors.ifEmpty { listOf("#444444", "#888888") }, Modifier.fillMaxWidth().height(44.dp))
            val category = when (item.kind) {
                Kind.SCENE -> catalog?.scene(item.key)?.first?.name
                Kind.PATTERN -> catalog?.patternCategories?.firstOrNull { it.id == item.category }?.name
            }
            val (dw, dh) = vm.device.screenSize()
            listOf(
                "Type" to (if (item.kind == Kind.SCENE) "Illustrated scene" else "Procedural pattern"),
                "Category" to (category ?: "—"),
                "Colours" to (if (item.palette < 0) "Original scene palette" else catalog?.palette(item.palette)?.name ?: "Palette ${item.palette}"),
                "Seed" to item.seed.toString(),
                "Blend" to (item.key2?.let { "${catalog?.pattern(it)?.name ?: it} · ${(item.blend * 100).toInt()}%" } ?: "—"),
                "Download" to (if (orientation == Orientation.PHONE) "${RenderSizes.PHONE_BASE.first}×${RenderSizes.PHONE_BASE.second} PNG" else "3840×2160 (4K) PNG"),
                "As wallpaper" to (if (orientation == Orientation.PHONE) "${dw}×$dh, fitted to this screen" else "Desktop wallpapers are download-only"),
            ).filterNot { it.second == "—" && it.first == "Blend" }.forEach { (label, value) ->
                Row {
                    Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.width(120.dp))
                    Text(value, style = MaterialTheme.typography.bodyMedium)
                }
            }
            Spacer(Modifier.height(4.dp))
            Text(
                "Every WallBloom wallpaper is generated from its parameters, so the same seed always produces the same image.",
                style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}
