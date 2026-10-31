package com.aurawall.app.ui.components

import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AccountBalance
import androidx.compose.material.icons.rounded.Apartment
import androidx.compose.material.icons.rounded.AutoAwesome
import androidx.compose.material.icons.rounded.AutoFixHigh
import androidx.compose.material.icons.rounded.BlurOn
import androidx.compose.material.icons.rounded.Bolt
import androidx.compose.material.icons.rounded.Brush
import androidx.compose.material.icons.rounded.Castle
import androidx.compose.material.icons.rounded.Category
import androidx.compose.material.icons.rounded.DarkMode
import androidx.compose.material.icons.rounded.Eco
import androidx.compose.material.icons.rounded.FilterHdr
import androidx.compose.material.icons.rounded.Forest
import androidx.compose.material.icons.rounded.Gradient
import androidx.compose.material.icons.rounded.Landscape
import androidx.compose.material.icons.rounded.LocalFireDepartment
import androidx.compose.material.icons.rounded.Memory
import androidx.compose.material.icons.rounded.NightsStay
import androidx.compose.material.icons.rounded.Palette
import androidx.compose.material.icons.rounded.Park
import androidx.compose.material.icons.rounded.Public
import androidx.compose.material.icons.rounded.RocketLaunch
import androidx.compose.material.icons.rounded.Spa
import androidx.compose.material.icons.rounded.Star
import androidx.compose.material.icons.rounded.Texture
import androidx.compose.material.icons.rounded.Water
import androidx.compose.material.icons.rounded.WbSunny
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Icons are chosen by the backend (Material Symbols names) so categories and collections can be
 * added or re-skinned without an app update. Unknown names fall back to the server-provided emoji.
 */
object IconRegistry {
    private val icons: Map<String, ImageVector> = mapOf(
        "account_balance" to Icons.Rounded.AccountBalance,
        "apartment" to Icons.Rounded.Apartment,
        "auto_awesome" to Icons.Rounded.AutoAwesome,
        "auto_fix_high" to Icons.Rounded.AutoFixHigh,
        "blur_on" to Icons.Rounded.BlurOn,
        "bolt" to Icons.Rounded.Bolt,
        "brush" to Icons.Rounded.Brush,
        "castle" to Icons.Rounded.Castle,
        "category" to Icons.Rounded.Category,
        "dark_mode" to Icons.Rounded.DarkMode,
        "eco" to Icons.Rounded.Eco,
        "filter_hdr" to Icons.Rounded.FilterHdr,
        "forest" to Icons.Rounded.Forest,
        "gradient" to Icons.Rounded.Gradient,
        "landscape" to Icons.Rounded.Landscape,
        "local_fire_department" to Icons.Rounded.LocalFireDepartment,
        "memory" to Icons.Rounded.Memory,
        "nights_stay" to Icons.Rounded.NightsStay,
        "palette" to Icons.Rounded.Palette,
        "park" to Icons.Rounded.Park,
        "public" to Icons.Rounded.Public,
        "rocket_launch" to Icons.Rounded.RocketLaunch,
        "spa" to Icons.Rounded.Spa,
        "star" to Icons.Rounded.Star,
        "texture" to Icons.Rounded.Texture,
        "water" to Icons.Rounded.Water,
        "wb_sunny" to Icons.Rounded.WbSunny,
    )

    fun find(name: String?): ImageVector? = name?.let { icons[it.lowercase()] }
}

@Composable
fun DynamicIcon(name: String?, emoji: String, tint: Color, size: Dp = 20.dp, modifier: Modifier = Modifier) {
    val vector = IconRegistry.find(name)
    if (vector != null) Icon(vector, contentDescription = null, tint = tint, modifier = modifier.size(size))
    else Text(emoji.ifBlank { "✨" }, fontSize = (size.value * 0.85f).sp, modifier = modifier)
}
