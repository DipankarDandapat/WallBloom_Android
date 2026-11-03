package com.aurawall.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CleaningServices
import androidx.compose.material.icons.rounded.Contrast
import androidx.compose.material.icons.rounded.DarkMode
import androidx.compose.material.icons.rounded.Info
import androidx.compose.material.icons.rounded.LightMode
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.annotation.ExperimentalCoilApi
import coil.imageLoader
import com.aurawall.app.BuildConfig
import com.aurawall.app.data.ThemeMode
import com.aurawall.app.ui.AppViewModel
import com.aurawall.app.ui.components.SegmentedPill
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@OptIn(ExperimentalCoilApi::class)
@Composable
fun SettingsScreen(vm: AppViewModel, onBack: () -> Unit) {
    val settings by vm.settings.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val isDark = settings.theme == ThemeMode.DARK

    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        SubScreenTopBar("Settings", onBack)
        Column(
            Modifier.verticalScroll(rememberScrollState()).padding(horizontal = 16.dp).navigationBarsPadding().padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Group("Appearance") {
                Text("Theme", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurface)
                Spacer(Modifier.size(10.dp))
                SegmentedPill(
                    listOf(ThemeMode.LIGHT to "Light", ThemeMode.DARK to "Dark"), settings.theme, vm::setTheme,
                    icons = listOf(Icons.Rounded.LightMode, Icons.Rounded.DarkMode), modifier = Modifier.fillMaxWidth(),
                )
                Spacer(Modifier.size(6.dp))
                // AMOLED only enabled when dark mode is active
                SettingRow(
                    Icons.Rounded.Contrast,
                    "AMOLED black",
                    if (isDark) "Pure black backgrounds" else "Only available in Dark mode",
                    onClick = if (isDark) ({ vm.setAmoled(!settings.amoled) }) else null,
                    modifier = if (!isDark) Modifier.alpha(0.4f) else Modifier,
                ) {
                    Switch(checked = settings.amoled && isDark, onCheckedChange = if (isDark) { v -> vm.setAmoled(v) } else null, enabled = isDark)
                }
            }
            Group("Storage") {
                SettingRow(Icons.Rounded.CleaningServices, "Clear image cache", "Frees disk space; wallpapers re-download on demand", onClick = {
                    scope.launch {
                        withContext(Dispatchers.IO) { context.imageLoader.diskCache?.clear() }
                        context.imageLoader.memoryCache?.clear()
                        vm.notify("Image cache cleared")
                    }
                })
            }
            Group("About") {
                SettingRow(Icons.Rounded.Info, "WallBloom ${BuildConfig.VERSION_NAME}", "Procedural wallpapers, generated on demand. No account needed.")
            }
        }
    }
}

@Composable
private fun Group(title: String, content: @Composable () -> Unit) {
    Column {
        Text(title.uppercase(), style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary, modifier = Modifier.padding(start = 6.dp, bottom = 8.dp))
        Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(22.dp)).background(MaterialTheme.colorScheme.surfaceContainerHigh).padding(16.dp)) { content() }
    }
}

@Composable
private fun SettingRow(
    icon: ImageVector,
    title: String,
    subtitle: String,
    onClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
    trailing: (@Composable () -> Unit)? = null,
) {
    Row(
        modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp))
            .then(if (onClick != null) Modifier.clickable(role = Role.Button, onClick = onClick) else Modifier)
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(Modifier.size(38.dp).clip(RoundedCornerShape(12.dp)).background(MaterialTheme.colorScheme.primary.copy(alpha = .14f)), contentAlignment = Alignment.Center) {
            Icon(icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
        }
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurface)
            Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        trailing?.invoke()
    }
}
