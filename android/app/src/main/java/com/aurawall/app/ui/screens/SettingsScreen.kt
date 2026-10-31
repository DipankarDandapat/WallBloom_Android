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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Brightness6
import androidx.compose.material.icons.rounded.CleaningServices
import androidx.compose.material.icons.rounded.Cloud
import androidx.compose.material.icons.rounded.Contrast
import androidx.compose.material.icons.rounded.DarkMode
import androidx.compose.material.icons.rounded.Info
import androidx.compose.material.icons.rounded.LightMode
import androidx.compose.material.icons.rounded.PhoneAndroid
import androidx.compose.material.icons.rounded.Refresh
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.annotation.ExperimentalCoilApi
import coil.imageLoader
import com.aurawall.app.BuildConfig
import com.aurawall.app.data.ApiMode
import com.aurawall.app.data.ThemeMode
import com.aurawall.app.ui.AppViewModel
import com.aurawall.app.ui.components.SegmentedPill
import com.aurawall.app.ui.theme.Brand
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@OptIn(ExperimentalCoilApi::class)
@Composable
fun SettingsScreen(vm: AppViewModel, onBack: () -> Unit) {
    val settings by vm.settings.collectAsStateWithLifecycle()
    val online by vm.serverOnline.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    LaunchedEffect(Unit) { vm.checkServer() }

    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        SubScreenTopBar("Settings", onBack)
        Column(
            Modifier.verticalScroll(rememberScrollState()).padding(horizontal = 16.dp).navigationBarsPadding().padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Group("Appearance") {
                Text("Theme", style = MaterialTheme.typography.titleSmall)
                Spacer(Modifier.size(10.dp))
                SegmentedPill(
                    listOf(ThemeMode.SYSTEM to "Auto", ThemeMode.LIGHT to "Light", ThemeMode.DARK to "Dark"), settings.theme, vm::setTheme,
                    icons = listOf(Icons.Rounded.Brightness6, Icons.Rounded.LightMode, Icons.Rounded.DarkMode), modifier = Modifier.fillMaxWidth(),
                )
                Spacer(Modifier.size(6.dp))
                SettingRow(Icons.Rounded.Contrast, "AMOLED black", "Pure black backgrounds in dark mode", onClick = { vm.setAmoled(!settings.amoled) }) {
                    Switch(settings.amoled, vm::setAmoled)
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
            Group("Wallpaper engine") {
                SettingRow(
                    Icons.Rounded.Cloud, vm.baseUrl.removePrefix("https://").removePrefix("http://").trimEnd('/'),
                    when (online) { true -> "Online · ${if (vm.apiMode == ApiMode.V2) "API v2" else "Legacy API v1"}"; false -> "Unreachable"; null -> "Checking…" },
                    trailing = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(Modifier.size(10.dp).clip(CircleShape).background(when (online) { true -> Brand.Success; false -> Brand.Danger; null -> Color.Gray }))
                            IconButton(vm::checkServer) { Icon(Icons.Rounded.Refresh, "Check server") }
                        }
                    },
                )
                SettingRow(Icons.Rounded.PhoneAndroid, "Wallpaper resolution", vm.device.screenSize().let { (w, h) -> "Rendered for this screen at ${w}×$h" })
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
private fun SettingRow(icon: ImageVector, title: String, subtitle: String, onClick: (() -> Unit)? = null, trailing: (@Composable () -> Unit)? = null) {
    Row(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp))
            .then(if (onClick != null) Modifier.clickable(role = Role.Button, onClick = onClick) else Modifier).padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(Modifier.size(38.dp).clip(RoundedCornerShape(12.dp)).background(MaterialTheme.colorScheme.primary.copy(alpha = .14f)), contentAlignment = Alignment.Center) {
            Icon(icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
        }
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleSmall)
            Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        trailing?.invoke()
    }
}
