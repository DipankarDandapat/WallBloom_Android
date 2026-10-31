@file:OptIn(ExperimentalSharedTransitionApi::class, ExperimentalFoundationApi::class)

package com.aurawall.app.ui.components

import androidx.compose.animation.AnimatedVisibilityScope
import androidx.compose.animation.ExperimentalSharedTransitionApi
import androidx.compose.animation.SharedTransitionScope
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import coil.compose.AsyncImagePainter
import coil.request.ImageRequest
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.Palette
import com.aurawall.app.data.Wallpaper
import com.aurawall.app.ui.theme.Brand
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Favorite

// ---------------------------------------------------------------------------------------------
// Shared element plumbing
// ---------------------------------------------------------------------------------------------

val LocalSharedTransitionScope = compositionLocalOf<SharedTransitionScope?> { null }
val LocalNavAnimatedScope = compositionLocalOf<AnimatedVisibilityScope?> { null }

fun sharedKey(item: Wallpaper, orientation: Orientation, origin: String) = "wp|$origin|${orientation.key}|${item.id}"

/** Morphs a grid card into the full-screen preview (and back). No-op outside a shared scope. */
@Composable
fun Modifier.sharedWallpaper(key: String?, shape: Shape = RoundedCornerShape(0.dp)): Modifier {
    val shared = LocalSharedTransitionScope.current ?: return this
    val animated = LocalNavAnimatedScope.current ?: return this
    if (key == null) return this
    return with(shared) {
        this@sharedWallpaper.sharedBounds(
            rememberSharedContentState(key),
            animatedVisibilityScope = animated,
            clipInOverlayDuringTransition = OverlayClip(shape),
        )
    }
}

// ---------------------------------------------------------------------------------------------
// Colour helpers
// ---------------------------------------------------------------------------------------------

fun parseColor(value: String?, fallback: Color = Color(0xFF2A2F45)): Color =
    try { if (value.isNullOrBlank()) fallback else Color(android.graphics.Color.parseColor(value)) } catch (_: Exception) { fallback }

/** Instant placeholder built from the wallpaper's own palette, shown before pixels arrive. */
fun placeholderBrush(colors: List<String>, fallback: Color): Brush = when {
    colors.isEmpty() -> Brush.linearGradient(listOf(fallback, fallback.copy(alpha = .7f)))
    colors.size == 1 -> Brush.linearGradient(listOf(parseColor(colors[0]), parseColor(colors[0])))
    else -> Brush.linearGradient(colors.map { parseColor(it) })
}

// ---------------------------------------------------------------------------------------------
// Shimmer
// ---------------------------------------------------------------------------------------------

@Composable
fun Modifier.shimmer(visible: Boolean = true): Modifier {
    if (!visible) return this
    val transition = rememberInfiniteTransition(label = "shimmer")
    val progress by transition.animateFloat(0f, 1f, infiniteRepeatable(tween(1300, easing = LinearEasing)), label = "shimmer-progress")
    return this.graphicsLayer { }.background(
        Brush.linearGradient(
            colors = listOf(Color.White.copy(alpha = 0f), Color.White.copy(alpha = .16f), Color.White.copy(alpha = 0f)),
            start = androidx.compose.ui.geometry.Offset(-600f + 1600f * progress, 0f),
            end = androidx.compose.ui.geometry.Offset(-200f + 1600f * progress, 400f),
        ),
    )
}

@Composable
fun SkeletonCard(modifier: Modifier, corner: Dp = 22.dp) {
    Box(modifier.clip(RoundedCornerShape(corner)).background(MaterialTheme.colorScheme.surfaceContainerHigh).shimmer())
}

// ---------------------------------------------------------------------------------------------
// Wallpaper card
// ---------------------------------------------------------------------------------------------

@Composable
fun WallpaperCard(
    item: Wallpaper,
    url: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    onLongClick: (() -> Unit)? = null,
    sharedKey: String? = null,
    corner: Dp = 22.dp,
    showLabel: Boolean = true,
    isFavorite: Boolean = false,
) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val scale by animateFloatAsState(if (pressed) .955f else 1f, spring(Spring.DampingRatioMediumBouncy, Spring.StiffnessMedium), label = "card-press")
    var loading by remember(url) { mutableStateOf(true) }
    val haptics = LocalHapticFeedback.current
    val shape = RoundedCornerShape(corner)
    val fallback = MaterialTheme.colorScheme.surfaceContainerHigh

    Box(
        modifier
            .graphicsLayer { scaleX = scale; scaleY = scale }
            .sharedWallpaper(sharedKey, shape)
            .clip(shape)
            .background(placeholderBrush(item.colors, fallback))
            .combinedClickable(
                interactionSource = interaction,
                indication = null,
                role = Role.Button,
                onClickLabel = "Preview ${item.name}",
                onLongClick = onLongClick?.let { action -> { haptics.performHapticFeedback(HapticFeedbackType.LongPress); action() } },
                onClick = onClick,
            ),
    ) {
        AsyncImage(
            model = ImageRequest.Builder(LocalContext.current).data(url).memoryCacheKey(url).build(),
            contentDescription = item.name,
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize(),
            onState = { loading = it is AsyncImagePainter.State.Loading || it is AsyncImagePainter.State.Empty },
        )
        if (loading) Box(Modifier.fillMaxSize().shimmer())
        if (showLabel) {
            Box(
                Modifier.align(Alignment.BottomStart).fillMaxWidth()
                    .background(Brush.verticalGradient(listOf(Color.Transparent, Color.Black.copy(alpha = .62f))))
                    .padding(start = 12.dp, end = 12.dp, top = 28.dp, bottom = 10.dp),
            ) {
                Column {
                    Text(item.name, color = Color.White, style = MaterialTheme.typography.labelLarge, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    if (item.subtitle.isNotBlank()) {
                        Text(item.subtitle, color = Color.White.copy(alpha = .72f), style = MaterialTheme.typography.labelSmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                }
            }
        }
        if (isFavorite) {
            Box(
                Modifier.align(Alignment.TopEnd).padding(8.dp).size(26.dp).clip(CircleShape).background(Color.Black.copy(alpha = .35f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.Rounded.Favorite, null, tint = Color(0xFFFF7AB6), modifier = Modifier.size(15.dp))
            }
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Small building blocks
// ---------------------------------------------------------------------------------------------

@Composable
fun SectionHeader(title: String, modifier: Modifier = Modifier, subtitle: String? = null, action: String? = null, onAction: (() -> Unit)? = null) {
    Row(modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onBackground)
            if (subtitle != null) Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        if (action != null && onAction != null) {
            Text(
                action, color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.labelLarge,
                modifier = Modifier.clip(RoundedCornerShape(10.dp)).clickable(onClick = onAction).padding(horizontal = 10.dp, vertical = 6.dp),
            )
        }
    }
}

/** Pill segmented control with a sliding, springy indicator. */
@Composable
fun <T> SegmentedPill(options: List<Pair<T, String>>, selected: T, onSelect: (T) -> Unit, modifier: Modifier = Modifier, icons: List<ImageVector>? = null) {
    val index = options.indexOfFirst { it.first == selected }.coerceAtLeast(0)
    BoxWithConstraints(
        modifier.clip(RoundedCornerShape(50)).background(MaterialTheme.colorScheme.surfaceContainerHigh).padding(4.dp),
    ) {
        val segment = maxWidth / options.size
        val offset by animateDpAsState(segment * index, spring(Spring.DampingRatioLowBouncy, Spring.StiffnessMediumLow), label = "pill")
        Box(Modifier.offset(x = offset).width(segment).height(36.dp).clip(RoundedCornerShape(50)).background(Brand.SoftGradient))
        Row(Modifier.fillMaxWidth().height(36.dp)) {
            options.forEachIndexed { i, (value, label) ->
                val active = i == index
                Row(
                    Modifier.weight(1f).fillMaxHeight().clip(RoundedCornerShape(50)).clickable(role = Role.Tab) { onSelect(value) },
                    horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically,
                ) {
                    val tint = if (active) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
                    icons?.getOrNull(i)?.let { Icon(it, null, tint = tint, modifier = Modifier.size(16.dp)); Spacer(Modifier.width(6.dp)) }
                    Text(label, color = tint, style = MaterialTheme.typography.labelLarge)
                }
            }
        }
    }
}

/** Chip with a server-driven icon and accent colour. */
@Composable
fun AccentChip(label: String, icon: String?, emoji: String, accent: String, selected: Boolean, onClick: () -> Unit, modifier: Modifier = Modifier) {
    val accentColor = parseColor(accent, MaterialTheme.colorScheme.primary)
    val bg = if (selected) accentColor.copy(alpha = .22f) else MaterialTheme.colorScheme.surfaceContainerHigh
    val border = if (selected) accentColor else Color.Transparent
    Row(
        modifier.clip(RoundedCornerShape(50)).background(bg).border(BorderStroke(1.dp, border), RoundedCornerShape(50))
            .clickable(role = Role.Tab, onClick = onClick).padding(horizontal = 14.dp, vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        DynamicIcon(icon, emoji, tint = if (selected) accentColor else MaterialTheme.colorScheme.onSurfaceVariant, size = 18.dp)
        Spacer(Modifier.width(7.dp))
        Text(label, style = MaterialTheme.typography.labelLarge, color = if (selected) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
fun PaletteStrip(colors: List<String>, modifier: Modifier = Modifier) {
    Row(modifier.clip(RoundedCornerShape(8.dp))) {
        colors.forEach { Box(Modifier.weight(1f).fillMaxHeight().background(parseColor(it))) }
    }
}

@Composable
fun PaletteChip(palette: Palette?, selected: Boolean, onClick: () -> Unit, modifier: Modifier = Modifier, label: String? = null, colors: List<String>? = null) {
    val ring by animateDpAsState(if (selected) 2.dp else 0.dp, label = "palette-ring")
    Column(modifier.width(64.dp).clickable(role = Role.RadioButton, onClick = onClick), horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            Modifier.size(52.dp).clip(CircleShape)
                .border(ring, MaterialTheme.colorScheme.primary, CircleShape).padding(if (selected) 4.dp else 0.dp).clip(CircleShape)
                .background(Brush.sweepGradient((colors ?: palette?.colors.orEmpty()).ifEmpty { listOf("#444444", "#888888") }.map { parseColor(it) }.let { it + it.first() })),
        )
        Spacer(Modifier.height(5.dp))
        Text(
            label ?: palette?.name.orEmpty(), style = MaterialTheme.typography.labelSmall, maxLines = 1, overflow = TextOverflow.Ellipsis,
            color = if (selected) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
fun EmptyState(icon: ImageVector, title: String, body: String, modifier: Modifier = Modifier, action: String? = null, onAction: (() -> Unit)? = null) {
    Column(modifier.padding(32.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Box(Modifier.size(84.dp).clip(RoundedCornerShape(28.dp)).background(Brand.Gradient), contentAlignment = Alignment.Center) {
            Icon(icon, null, tint = Color.White, modifier = Modifier.size(38.dp))
        }
        Spacer(Modifier.height(18.dp))
        Text(title, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onBackground)
        Spacer(Modifier.height(6.dp))
        Text(body, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
        if (action != null && onAction != null) {
            Spacer(Modifier.height(20.dp))
            Button(onAction, shape = RoundedCornerShape(16.dp), contentPadding = PaddingValues(horizontal = 22.dp, vertical = 12.dp)) { Text(action) }
        }
    }
}

/** Round translucent icon button used over imagery. */
@Composable
fun GlassIconButton(icon: ImageVector, description: String, onClick: () -> Unit, modifier: Modifier = Modifier, tint: Color = Color.White, size: Dp = 44.dp) {
    Surface(
        onClick = onClick, modifier = modifier.size(size), shape = CircleShape,
        color = Color.Black.copy(alpha = .38f), border = BorderStroke(1.dp, Color.White.copy(alpha = .14f)),
    ) {
        Box(contentAlignment = Alignment.Center) { Icon(icon, description, tint = tint, modifier = Modifier.size(size * .48f)) }
    }
}

@Composable
fun PrimaryGradientButton(text: String, icon: ImageVector?, onClick: () -> Unit, modifier: Modifier = Modifier, loading: Boolean = false, enabled: Boolean = true) {
    Button(
        onClick = onClick, enabled = enabled && !loading, modifier = modifier.height(54.dp), shape = RoundedCornerShape(18.dp),
        contentPadding = PaddingValues(0.dp), colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent, disabledContainerColor = Color.Transparent),
    ) {
        Box(Modifier.fillMaxSize().background(Brand.Gradient, alpha = if (enabled) 1f else .5f), contentAlignment = Alignment.Center) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (loading) androidx.compose.material3.CircularProgressIndicator(Modifier.size(20.dp), color = Color.White, strokeWidth = 2.dp)
                else icon?.let { Icon(it, null, tint = Color.White, modifier = Modifier.size(20.dp)) }
                Spacer(Modifier.width(8.dp))
                Text(text, color = Color.White, style = MaterialTheme.typography.titleSmall)
            }
        }
    }
}
