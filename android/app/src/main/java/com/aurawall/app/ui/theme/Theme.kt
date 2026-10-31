package com.aurawall.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.aurawall.app.data.Settings
import com.aurawall.app.data.ThemeMode

object Brand {
    val Ink = Color(0xFF0B0D17)
    val Violet = Color(0xFF8B7CFF)
    val Indigo = Color(0xFF3B2FD9)
    val Pink = Color(0xFFFF7AB6)
    val Cyan = Color(0xFF5CE1E6)
    val Success = Color(0xFF4ADE80)
    val Danger = Color(0xFFFF6B7A)

    val Gradient = Brush.linearGradient(listOf(Indigo, Violet, Pink))
    val SoftGradient = Brush.linearGradient(listOf(Violet.copy(alpha = .9f), Pink.copy(alpha = .9f)))
}

private fun darkScheme(amoled: Boolean) = darkColorScheme(
    primary = Brand.Violet,
    onPrimary = Color.White,
    primaryContainer = Color(0xFF2A2366),
    onPrimaryContainer = Color(0xFFE4DFFF),
    secondary = Brand.Pink,
    onSecondary = Color(0xFF3A0820),
    tertiary = Brand.Cyan,
    background = if (amoled) Color.Black else Brand.Ink,
    onBackground = Color(0xFFF1F2F8),
    surface = if (amoled) Color.Black else Brand.Ink,
    onSurface = Color(0xFFF1F2F8),
    surfaceVariant = if (amoled) Color(0xFF0E0F14) else Color(0xFF1A1E2E),
    onSurfaceVariant = Color(0xFF9AA1BD),
    surfaceContainerLowest = if (amoled) Color.Black else Color(0xFF080A12),
    surfaceContainerLow = if (amoled) Color(0xFF07080C) else Color(0xFF10131F),
    surfaceContainer = if (amoled) Color(0xFF0C0D12) else Color(0xFF151927),
    surfaceContainerHigh = if (amoled) Color(0xFF121319) else Color(0xFF1C2132),
    surfaceContainerHighest = if (amoled) Color(0xFF191A21) else Color(0xFF242A3E),
    outline = Color(0xFF39405A),
    outlineVariant = if (amoled) Color(0xFF1A1B22) else Color(0xFF242A3E),
    error = Brand.Danger,
    inverseSurface = Color(0xFFF1F2F8),
    inverseOnSurface = Brand.Ink,
)

private val LightScheme = lightColorScheme(
    primary = Color(0xFF5B45E0),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE6E1FF),
    onPrimaryContainer = Color(0xFF1E1366),
    secondary = Color(0xFFD9488F),
    tertiary = Color(0xFF0E9BA3),
    background = Color(0xFFF6F6FB),
    onBackground = Color(0xFF14151F),
    surface = Color(0xFFF6F6FB),
    onSurface = Color(0xFF14151F),
    surfaceVariant = Color(0xFFECECF4),
    onSurfaceVariant = Color(0xFF5E6278),
    surfaceContainerLowest = Color.White,
    surfaceContainerLow = Color(0xFFF9F9FD),
    surfaceContainer = Color.White,
    surfaceContainerHigh = Color(0xFFEFEFF6),
    surfaceContainerHighest = Color(0xFFE6E6EF),
    outline = Color(0xFFC9CBD9),
    outlineVariant = Color(0xFFE2E3EC),
    error = Color(0xFFD93A4A),
)

private val AppTypography = Typography().run {
    copy(
        displaySmall = displaySmall.copy(fontWeight = FontWeight.Bold, letterSpacing = (-0.5).sp),
        headlineLarge = headlineLarge.copy(fontWeight = FontWeight.Bold, letterSpacing = (-0.6).sp),
        headlineMedium = headlineMedium.copy(fontWeight = FontWeight.Bold, letterSpacing = (-0.4).sp),
        headlineSmall = headlineSmall.copy(fontWeight = FontWeight.Bold, letterSpacing = (-0.2).sp),
        titleLarge = titleLarge.copy(fontWeight = FontWeight.Bold),
        titleMedium = titleMedium.copy(fontWeight = FontWeight.SemiBold),
        titleSmall = titleSmall.copy(fontWeight = FontWeight.SemiBold),
        labelLarge = labelLarge.copy(fontWeight = FontWeight.SemiBold),
        labelMedium = labelMedium.copy(fontWeight = FontWeight.SemiBold),
    )
}

val Caption = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium, letterSpacing = 0.2.sp)

@Composable
fun isDarkTheme(settings: Settings): Boolean = when (settings.theme) {
    ThemeMode.SYSTEM -> isSystemInDarkTheme()
    ThemeMode.DARK -> true
    ThemeMode.LIGHT -> false
}

@Composable
fun WallBloomTheme(settings: Settings, content: @Composable () -> Unit) {
    val dark = isDarkTheme(settings)
    MaterialTheme(
        colorScheme = if (dark) darkScheme(settings.amoled) else LightScheme,
        typography = AppTypography,
        content = content,
    )
}
