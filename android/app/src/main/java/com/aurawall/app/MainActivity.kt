package com.aurawall.app

import android.content.ContentValues
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Computer
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.InvertColors
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Shuffle
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.Smartphone
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.chuckerteam.chucker.api.ChuckerInterceptor
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import kotlin.random.Random

private val Ink = Color(0xFF080B14)
private val Surface1 = Color(0xFF101625)
private val Surface2 = Color(0xFF171E31)
private val Surface3 = Color(0xFF202941)
private val Primary = Color(0xFF7357FF)
private val Secondary = Color(0xFFB56BFF)
private val Cyan = Color(0xFF52D9FF)
private val Muted = Color(0xFF9099B5)

private data class Pattern(val type: String, val name: String, val description: String)
private data class Palette(val id: Int, val name: String, val colors: List<String>)
private data class Scene(val id: String, val name: String, val theme: String, val emoji: String)
private data class ThemeGroup(val id: String, val name: String, val emoji: String, val scenes: List<Scene>)
private enum class EditorMode { PATTERNS, SCENES }

private val FALLBACK_PATTERNS = listOf(
    Pattern("hills", "Hills", "Layered landscape"), Pattern("waves", "Waves", "Flowing lines"),
    Pattern("dunes", "Dunes", "Soft desert curves"), Pattern("mountains", "Mountains", "Ridgeline forms"),
    Pattern("aurora", "Aurora", "Northern light ribbons"), Pattern("galaxy", "Galaxy", "Deep-space glow"),
    Pattern("geometric", "Geometric", "Structured forms"), Pattern("spiral", "Spiral", "Rotating motion"),
    Pattern("gradient", "Gradient", "Smooth color field"), Pattern("cellular", "Cellular", "Organic cells"),
    Pattern("lightning", "Lightning", "Electric branches"), Pattern("bubbles", "Bubbles", "Floating circles")
)
private val FALLBACK_PALETTES = listOf(
    Palette(0, "Charcoal", listOf("#1A1A1A", "#4A4A4A", "#8A8A8A", "#D0D0D0")),
    Palette(1, "Ocean Blue", listOf("#001F3F", "#0074D9", "#7FDBCA", "#B3E5FC")),
    Palette(2, "Sunrise", listOf("#FF6B35", "#F7931E", "#FDB833", "#FFF4E6")),
    Palette(3, "Purple", listOf("#2D1B4E", "#6A0572", "#AB47BC", "#E1BEE7")),
    Palette(4, "Forest", listOf("#102A24", "#1B5E49", "#66BB6A", "#D7F9E9")),
    Palette(5, "Deep Space", listOf("#090A1A", "#252A68", "#663399", "#D5C7FF"))
)
private val FALLBACK_THEMES = listOf(
    ThemeGroup("world", "World", "🌍", listOf(Scene("desert", "Desert", "world", "🏜️"), Scene("beach", "Beach", "world", "🏖️"), Scene("mountain", "Mountain", "world", "🏔️"))),
    ThemeGroup("celestial", "Celestial", "🌌", listOf(Scene("sunrise", "Sunrise", "celestial", "🌅"), Scene("starfield", "Starfield", "celestial", "✨"), Scene("nebula", "Nebula", "celestial", "🪐"))),
    ThemeGroup("nature", "Nature", "🌿", listOf(Scene("forest", "Forest", "nature", "🌲"), Scene("ocean", "Ocean", "nature", "🌊"), Scene("waterfall", "Waterfall", "nature", "💧")))
)

private class AuraApi(context: android.content.Context, private val base: String) {
    private val client = OkHttpClient.Builder().addInterceptor(ChuckerInterceptor(context.applicationContext)).build()

    private fun url(path: String, query: okhttp3.HttpUrl.Builder.() -> Unit = {}): String =
        base.trim().trimEnd('/').toHttpUrl().newBuilder()
            .addPathSegments(path.trimStart('/')).apply(query).build().toString()

    suspend fun health(): Boolean = withContext(Dispatchers.IO) {
        get(url("health")).use { response -> response.code == 200 }
    }

    suspend fun patterns(): List<Pattern> = get(url("api/patterns")).use { response ->
        val array = JSONObject(response.body!!.string()).getJSONArray("patterns")
        List(array.length()) { index ->
            val item = array.getJSONObject(index)
            Pattern(item.getString("type"), item.getString("name"), item.getString("description"))
        }
    }

    suspend fun palettes(): List<Palette> = get(url("api/palettes")).use { response ->
        val array = JSONArray(response.body!!.string())
        List(array.length()) { index ->
            val item = array.getJSONObject(index)
            val colors = item.getJSONArray("colors")
            Palette(item.getInt("id"), item.getString("name"), List(colors.length()) { colors.getString(it) })
        }
    }

    suspend fun scenes(): List<ThemeGroup> = get(url("api/scenes")).use { response ->
        val groups = JSONObject(response.body!!.string()).getJSONArray("themes")
        List(groups.length()) { groupIndex ->
            val group = groups.getJSONObject(groupIndex)
            val scenes = group.getJSONArray("scenes")
            ThemeGroup(
                group.getString("id"), group.getString("name"), group.optString("emoji", "🌍"),
                List(scenes.length()) { sceneIndex ->
                    val scene = scenes.getJSONObject(sceneIndex)
                    Scene(scene.getString("id"), scene.getString("name"), scene.getString("theme"), scene.optString("emoji", "🎨"))
                }
            )
        }
    }

    fun patternPreview(pattern: String, palette: Int, seed: Int, inverted: Boolean, width: Int, height: Int, second: String? = null, ratio: Float = .5f) = url("api/wallpapers/preview") {
        addQueryParameter("pattern_type", pattern)
        addQueryParameter("palette_index", palette.toString())
        addQueryParameter("seed", seed.toString())
        addQueryParameter("inverted", inverted.toString())
        addQueryParameter("width", width.toString())
        addQueryParameter("height", height.toString())
        second?.let { addQueryParameter("pattern_type_2", it); addQueryParameter("blend_ratio", ratio.toString()) }
    }

    fun scenePreview(scene: String, seed: Int, inverted: Boolean, width: Int, height: Int, palette: Int) = url("api/wallpapers/scene") {
        addQueryParameter("scene_type", scene)
        addQueryParameter("seed", seed.toString())
        addQueryParameter("inverted", inverted.toString())
        addQueryParameter("width", width.toString())
        addQueryParameter("height", height.toString())
        addQueryParameter("palette_override", palette.toString())
    }

    fun patternDownload(device: String, pattern: String, palette: Int, seed: Int, inverted: Boolean, second: String? = null, ratio: Float = .5f) = url("api/wallpapers/download/$device") {
        addQueryParameter("pattern_type", pattern)
        addQueryParameter("palette_index", palette.toString())
        addQueryParameter("seed", seed.toString())
        addQueryParameter("inverted", inverted.toString())
        second?.let { addQueryParameter("pattern_type_2", it); addQueryParameter("blend_ratio", ratio.toString()) }
    }

    fun sceneDownload(device: String, scene: String, seed: Int, inverted: Boolean, palette: Int) = url("api/wallpapers/download/$device") {
        addQueryParameter("scene_type", scene)
        addQueryParameter("seed", seed.toString())
        addQueryParameter("inverted", inverted.toString())
        addQueryParameter("palette_override", palette.toString())
    }

    private suspend fun get(endpoint: String) = withContext(Dispatchers.IO) {
        client.newCall(Request.Builder().url(endpoint).get().build()).execute().also {
            if (!it.isSuccessful) throw IOException("HTTP ${it.code}")
        }
    }

    suspend fun download(endpoint: String): ByteArray = withContext(Dispatchers.IO) {
        get(endpoint).use { response -> response.body?.bytes() ?: throw IOException("Empty image response") }
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { WallBloomApp() }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun WallBloomApp() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val api = remember { AuraApi(context, BuildConfig.API_BASE_URL) }
    var patterns by remember { mutableStateOf<List<Pattern>>(emptyList()) }
    var palettes by remember { mutableStateOf<List<Palette>>(emptyList()) }
    var themes by remember { mutableStateOf<List<ThemeGroup>>(emptyList()) }
    var mode by remember { mutableStateOf(EditorMode.PATTERNS) }
    var uiDark by rememberSaveable { mutableStateOf(true) }
    var pattern by remember { mutableStateOf("hills") }
    var secondPattern by remember { mutableStateOf("waves") }
    var selectedPalette by remember { mutableIntStateOf(0) }
    var scene by remember { mutableStateOf("desert") }
    var sceneTheme by remember { mutableStateOf("") }
    var seed by remember { mutableIntStateOf(Random.nextInt(100000, 999999)) }
    var inverted by remember { mutableStateOf(false) }
    var blend by remember { mutableStateOf(false) }
    var blendRatio by remember { mutableFloatStateOf(.5f) }
    var patternsExpanded by rememberSaveable { mutableStateOf(false) }
    var loading by remember { mutableStateOf(true) }
    var message by remember { mutableStateOf<String?>(null) }
    var checkingServer by remember { mutableStateOf(true) }
    var hasLoadedOnce by rememberSaveable { mutableStateOf(false) }
    var connectionError by remember { mutableStateOf<String?>(null) }
    var foregroundTick by remember { mutableIntStateOf(0) }
    val lifecycleOwner = LocalLifecycleOwner.current

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_START) foregroundTick++
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    LaunchedEffect(foregroundTick) {
        checkingServer = true
        connectionError = null
        if (!hasLoadedOnce) {
            while (!hasLoadedOnce) {
                try {
                    if (!api.health()) throw IOException("Health endpoint did not return HTTP 200")
                    patterns = api.patterns()
                    palettes = api.palettes()
                    themes = api.scenes()
                    if (themes.isNotEmpty()) {
                        sceneTheme = themes.first().id
                        scene = themes.first().scenes.firstOrNull()?.id ?: scene
                    }
                    hasLoadedOnce = patterns.isNotEmpty() && palettes.isNotEmpty()
                    if (!hasLoadedOnce) throw IOException("Catalog response was empty")
                    loading = false
                } catch (_: Exception) {
                    connectionError = "Waiting for WallBloom server…"
                    loading = true
                    delay(1500)
                }
            }
        } else {
            try {
                if (!api.health()) throw IOException("Health endpoint did not return HTTP 200")
            } catch (_: Exception) {
                connectionError = "Server check failed; showing the last loaded catalog."
            }
        }
        checkingServer = false
    }

    val activeTheme = themes.find { it.id == sceneTheme } ?: themes.find { group -> group.scenes.any { it.id == scene } }
    val desktopPreview = if (mode == EditorMode.PATTERNS) {
        api.patternPreview(pattern, selectedPalette, seed, inverted, 1280, 720, if (blend) secondPattern else null, blendRatio)
    } else {
        api.scenePreview(scene, seed, inverted, 390, 844, selectedPalette)
    }
    val mobilePreview = if (mode == EditorMode.PATTERNS) {
        api.patternPreview(pattern, selectedPalette, seed, inverted, 390, 844, if (blend) secondPattern else null, blendRatio)
    } else {
        api.scenePreview(scene, seed, inverted, 390, 844, selectedPalette)
    }

    MaterialTheme(colorScheme = if (uiDark) darkColorScheme(background = Ink, surface = Surface1, primary = Primary, secondary = Secondary) else lightColorScheme(background = Color(0xFFF7F7FB), surface = Color.White, primary = Color(0xFF5B45D9), secondary = Color(0xFF8E44C7), onBackground = Color(0xFF171827), onSurface = Color(0xFF171827))) {
        if (!hasLoadedOnce) {
            LaunchScreen(checkingServer, connectionError) { foregroundTick++ }
        } else Scaffold(
            containerColor = MaterialTheme.colorScheme.background,
            topBar = {
                TopAppBar(
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(Modifier.size(38.dp).clip(RoundedCornerShape(12.dp)).background(BrandGradient), contentAlignment = Alignment.Center) {
                                Text("W", color = Color.White, fontSize = 22.sp, fontWeight = FontWeight.Black)
                            }
                            Spacer(Modifier.width(10.dp))
                            Column {
                                Text("WallBloom", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                                Text("Wallpaper generator", color = if (uiDark) Muted else Color(0xFF64677A), fontSize = 11.sp)
                            }
                        }
                    },
                    actions = {
                        IconButton(onClick = { uiDark = !uiDark }) { Icon(if (uiDark) Icons.Default.LightMode else Icons.Default.DarkMode, "Toggle light and dark mode") }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background)
                )
            }
        ) { padding ->
            Column(
                Modifier.padding(padding).fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 16.dp, vertical = 10.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp)
            ) {
                HeroCard()
                ModeTabs(mode) { mode = it }
                PreviewBoard(
                    desktopPreview, mobilePreview, loading, pattern, scene, mode,
                    onDownloadDesktop = {
                        scope.launch {
                            try {
                                val endpoint = if (mode == EditorMode.PATTERNS) api.patternDownload("desktop", pattern, selectedPalette, seed, inverted, if (blend) secondPattern else null, blendRatio) else api.sceneDownload("desktop", scene, seed, inverted, selectedPalette)
                                savePng(context, api.download(endpoint), "wallbloom_desktop_$seed")
                                message = "Desktop 4K saved to Pictures/WallBloom"
                            } catch (error: Exception) { message = "Download failed: ${error.message ?: "check the API"}" }
                        }
                    },
                    onDownloadMobile = {
                        scope.launch {
                            try {
                                val endpoint = if (mode == EditorMode.PATTERNS) api.patternDownload("mobile", pattern, selectedPalette, seed, inverted, if (blend) secondPattern else null, blendRatio) else api.sceneDownload("mobile", scene, seed, inverted, selectedPalette)
                                savePng(context, api.download(endpoint), "wallbloom_mobile_$seed")
                                message = "Mobile wallpaper saved to Pictures/WallBloom"
                            } catch (error: Exception) { message = "Download failed: ${error.message ?: "check the API"}" }
                        }
                    }
                )
                ActionButton("New variation", Icons.Default.Shuffle, Modifier.fillMaxWidth()) { seed = Random.nextInt(100000, 999999) }

                if (mode == EditorMode.PATTERNS) {
                    SectionHeader("Pattern library", "Choose a visual language")
                    PatternPicker(patterns, pattern, expanded = patternsExpanded, onExpandedChange = { patternsExpanded = it }) { pattern = it }
                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                        Column(Modifier.weight(1f)) {
                            Text("Blend two patterns", fontWeight = FontWeight.SemiBold)
                            Text("Layer a second texture into the scene", color = Muted, fontSize = 12.sp)
                        }
                        Switch(blend, { blend = it })
                    }
                    if (blend) {
                        PatternPicker(patterns, secondPattern, compact = true, expanded = true, onExpandedChange = {}) { secondPattern = it }
                        Text("Blend strength ${(blendRatio * 100).toInt()}%", color = Muted, fontSize = 12.sp)
                        Slider(blendRatio, { blendRatio = it }, valueRange = 0f..1f)
                    }
                } else {
                    SectionHeader("Scene library", "Explore places, nature and celestial moods")
                    ThemePicker(themes, sceneTheme) { selected ->
                        sceneTheme = selected
                        themes.find { it.id == selected }?.scenes?.firstOrNull()?.let { scene = it.id }
                    }
                    ScenePicker(activeTheme?.scenes ?: emptyList(), scene) { scene = it }
                }

                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text("Color direction", fontSize = 17.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(3.dp)); Text("Curated palettes from the WallBloom engine", fontSize = 12.sp, color = Muted)
                    }
                    IconButton(onClick = { inverted = !inverted }) {
                        Icon(Icons.Default.InvertColors, "Invert colors", tint = if (inverted) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                PalettePicker(palettes, selectedPalette) { selectedPalette = it }
                if (palettes.isNotEmpty()) {
                    val palette = palettes[selectedPalette.coerceIn(0, palettes.lastIndex)]
                    PalettePreview(palette)
                }

                ConnectionFooter(loading)
                Spacer(Modifier.height(10.dp))
            }
        }
        message?.let { toast ->
            Surface(Modifier.padding(16.dp), shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surfaceVariant, shadowElevation = 10.dp) {
                Row(Modifier.padding(horizontal = 16.dp, vertical = 13.dp), verticalAlignment = Alignment.CenterVertically) {
                    if (toast.startsWith("API unavailable")) Icon(Icons.Default.CloudOff, null, tint = Color(0xFFFFB4AB)) else Icon(Icons.Default.Check, null, tint = Cyan)
                    Spacer(Modifier.width(8.dp)); Text(toast, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 12.sp)
                }
            }
            LaunchedEffect(toast) { kotlinx.coroutines.delay(4000); message = null }
        }
    }
}

private val BrandGradient = Brush.linearGradient(listOf(Color(0xFF5B5FEF), Color(0xFFB84CFF)))
private val PreviewGradient = Brush.linearGradient(listOf(Color(0xFF252B4A), Color(0xFF121727)))

@Composable private fun LaunchScreen(checking: Boolean, error: String?, onRetry: () -> Unit) {
    Box(Modifier.fillMaxSize().background(Ink), contentAlignment = Alignment.Center) {
        Column(Modifier.padding(32.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Box(Modifier.size(82.dp).clip(RoundedCornerShape(24.dp)).background(BrandGradient), contentAlignment = Alignment.Center) {
                Text("W", color = Color.White, fontSize = 46.sp, fontWeight = FontWeight.Black)
            }
            Spacer(Modifier.height(20.dp))
            Text("WallBloom", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Text(if (checking) "Connecting to the server" else "Server connection required", color = Muted, fontSize = 14.sp, textAlign = TextAlign.Center)
            Spacer(Modifier.height(20.dp))
            if (checking) CircularProgressIndicator(color = Cyan, strokeWidth = 3.dp)
            else Button(onClick = onRetry, colors = ButtonDefaults.buttonColors(containerColor = Primary), shape = RoundedCornerShape(14.dp)) { Text("Retry connection") }
            if (error != null) { Spacer(Modifier.height(18.dp)); Text(error, color = Color(0xFFFFB4AB), fontSize = 12.sp, textAlign = TextAlign.Center) }
            Spacer(Modifier.height(22.dp))
            Text("Checking https://wallbloom.onrender.com/health", color = Color(0xFF68718C), fontSize = 10.sp, textAlign = TextAlign.Center)
        }
    }
}

@Composable private fun HeroCard() {
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface), shape = RoundedCornerShape(24.dp)) {
        Column(Modifier.padding(20.dp)) {
            Text("Your screen, reimagined.", fontSize = 25.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            Text("Compose a unique wallpaper from procedural patterns, cinematic scenes and curated color stories.", color = Muted, fontSize = 13.sp, lineHeight = 19.sp)
            Spacer(Modifier.height(16.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(8.dp).clip(CircleShape).background(Cyan)); Spacer(Modifier.width(8.dp)); Text("Real-time generator", color = MaterialTheme.colorScheme.onSurface, fontWeight = FontWeight.SemiBold, fontSize = 12.sp); Spacer(Modifier.width(8.dp)); Text("•", color = Muted); Spacer(Modifier.width(8.dp)); Text("4K export", color = Muted, fontSize = 12.sp)
            }
        }
    }
}

@Composable private fun ModeTabs(mode: EditorMode, onChange: (EditorMode) -> Unit) {
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(MaterialTheme.colorScheme.surface).padding(4.dp)) {
        listOf(EditorMode.PATTERNS to "🎨  Patterns", EditorMode.SCENES to "🌍  Scenes").forEach { (value, label) ->
            Text(label, Modifier.weight(1f).clip(RoundedCornerShape(12.dp)).background(if (mode == value) Primary else Color.Transparent).clickable { onChange(value) }.padding(vertical = 13.dp), color = if (mode == value) Color.White else MaterialTheme.colorScheme.onSurface, textAlign = TextAlign.Center, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
        }
    }
}

@Composable private fun PreviewBoard(
    desktop: String, mobile: String, loading: Boolean, pattern: String, scene: String, mode: EditorMode,
    onDownloadDesktop: () -> Unit, onDownloadMobile: () -> Unit
) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
        PreviewCard(desktop, if (mode == EditorMode.PATTERNS) pattern.replace('_', ' ').replaceFirstChar { it.uppercase() } else scene.replace('_', ' ').replaceFirstChar { it.uppercase() }, Modifier.weight(1f).aspectRatio(1.62f), loading, onDownloadDesktop)
        PreviewCard(mobile, "Mobile", Modifier.width(112.dp).aspectRatio(.52f), loading, onDownloadMobile)
    }
}

@Composable private fun PreviewCard(url: String, label: String, modifier: Modifier, loading: Boolean, onDownload: () -> Unit) {
    Box(modifier.clip(RoundedCornerShape(22.dp)).background(PreviewGradient).border(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = .35f), RoundedCornerShape(22.dp))) {
        if (loading) CircularProgressIndicator(Modifier.align(Alignment.Center).size(28.dp), color = Cyan, strokeWidth = 2.dp)
        else AsyncImage(ImageRequest.Builder(LocalContext.current).data(url).crossfade(true).build(), label, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
        Row(Modifier.align(Alignment.BottomStart).padding(8.dp).clip(RoundedCornerShape(10.dp)).background(Color.Black.copy(alpha = .62f)).padding(start = 8.dp, end = 3.dp, top = 3.dp, bottom = 3.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Visibility, "Preview", tint = Color.White, modifier = Modifier.size(15.dp))
            Spacer(Modifier.width(5.dp)); Text(label, color = Color.White, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.width(2.dp)); IconButton(onClick = onDownload, modifier = Modifier.size(30.dp)) { Icon(Icons.Default.Download, "Download $label wallpaper", tint = Color.White, modifier = Modifier.size(17.dp)) }
        }
    }
}

@Composable private fun ActionButton(label: String, icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier, onClick: () -> Unit) {
    Button(onClick, modifier.height(48.dp), colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.surfaceVariant, contentColor = MaterialTheme.colorScheme.onSurfaceVariant), shape = RoundedCornerShape(14.dp), contentPadding = PaddingValues(horizontal = 12.dp)) { Icon(icon, null, modifier = Modifier.size(17.dp)); Spacer(Modifier.width(7.dp)); Text(label, fontSize = 12.sp, fontWeight = FontWeight.SemiBold) }
}

@Composable private fun SectionHeader(title: String, subtitle: String) {
    Column {
        Text(title, fontSize = 17.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(3.dp)); Text(subtitle, fontSize = 12.sp, color = Muted)
    }
}

@Composable private fun PatternPicker(items: List<Pattern>, selected: String, compact: Boolean = false, expanded: Boolean = false, onExpandedChange: (Boolean) -> Unit, onPick: (String) -> Unit) {
    val columns = 4
    val visibleItems = if (compact || expanded) items else items.take(40)
    val gridHeight = if (compact) 250.dp else (((visibleItems.size + columns - 1) / columns) * 76).dp
    Column(Modifier.fillMaxWidth()) {
        androidx.compose.foundation.lazy.grid.LazyVerticalGrid(
            columns = androidx.compose.foundation.lazy.grid.GridCells.Fixed(columns),
            modifier = Modifier.fillMaxWidth().height(gridHeight),
            horizontalArrangement = Arrangement.spacedBy(7.dp),
            verticalArrangement = Arrangement.spacedBy(7.dp),
            userScrollEnabled = compact,
            contentPadding = PaddingValues(vertical = 4.dp)
        ) {
            items(visibleItems.size) { index ->
                val item = visibleItems[index]
                val active = item.type == selected
                Column(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                        .background(if (active) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface)
                        .border(1.dp, if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline.copy(alpha = .45f), RoundedCornerShape(12.dp))
                        .clickable { onPick(item.type) }.padding(vertical = 8.dp, horizontal = 4.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Box(Modifier.size(34.dp).clip(RoundedCornerShape(9.dp)).background(patternBrush(item.type)), contentAlignment = Alignment.Center) {
                        Text(patternGlyph(item.type), fontSize = 18.sp, color = Color.White)
                    }
                    Spacer(Modifier.height(4.dp))
                    Text(item.name.replace('_', ' '), color = MaterialTheme.colorScheme.onSurface, fontSize = 9.sp, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center)
                }
            }
        }
        if (!compact && items.size > 40) {
            Text(
                if (expanded) "Show less" else "View more (${items.size - 40} more)",
                Modifier.fillMaxWidth().clickable { onExpandedChange(!expanded) }.padding(vertical = 12.dp),
                color = MaterialTheme.colorScheme.primary, textAlign = TextAlign.Center, fontSize = 12.sp, fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable private fun ThemePicker(items: List<ThemeGroup>, selected: String, onPick: (String) -> Unit) {
    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp), contentPadding = PaddingValues(vertical = 2.dp)) { items(items) { group -> FilterChip(selected = group.id == selected, onClick = { onPick(group.id) }, label = { Text("${group.emoji} ${group.name}", fontSize = 12.sp) }) } }
}

@Composable private fun ScenePicker(items: List<Scene>, selected: String, onPick: (String) -> Unit) {
    LazyRow(horizontalArrangement = Arrangement.spacedBy(9.dp), contentPadding = PaddingValues(vertical = 3.dp)) { items(items) { scene -> val active = scene.id == selected; Column(Modifier.width(126.dp).clip(RoundedCornerShape(15.dp)).background(if (active) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface).border(1.dp, if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline.copy(alpha = .45f), RoundedCornerShape(15.dp)).clickable { onPick(scene.id) }.padding(10.dp)) { Text(scene.emoji, fontSize = 26.sp); Spacer(Modifier.height(8.dp)); Text(scene.name, color = MaterialTheme.colorScheme.onSurface, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, maxLines = 2, overflow = TextOverflow.Ellipsis) } } }
}

@Composable private fun PalettePicker(items: List<Palette>, selected: Int, onPick: (Int) -> Unit) {
    val gridHeight = (((items.size + 2) / 3) * 68).dp
    androidx.compose.foundation.lazy.grid.LazyVerticalGrid(
        columns = androidx.compose.foundation.lazy.grid.GridCells.Fixed(3),
        modifier = Modifier.fillMaxWidth().height(gridHeight),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(vertical = 4.dp)
    ) {
        items(items.size) { index ->
            val palette = items[index]
            val active = palette.id == selected
            Column(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                    .background(if (active) Color(0xFF2B2059) else MaterialTheme.colorScheme.surface)
                    .border(1.dp, if (active) Primary else Color.White.copy(alpha = .08f), RoundedCornerShape(12.dp))
                    .clickable { onPick(palette.id) }.padding(7.dp)
            ) {
                Row(Modifier.fillMaxWidth().height(25.dp).clip(RoundedCornerShape(6.dp))) {
                    palette.colors.take(4).forEach { color -> Box(Modifier.weight(1f).fillMaxHeight().background(parseColor(color))) }
                }
                Spacer(Modifier.height(5.dp))
                Text(palette.name, color = MaterialTheme.colorScheme.onSurface, fontSize = 9.sp, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
            }
        }
    }
}

@Composable private fun PalettePreview(palette: Palette) {
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface), shape = RoundedCornerShape(16.dp)) { Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) { Column(Modifier.weight(1f)) { Text(palette.name, fontWeight = FontWeight.SemiBold); Text("Current color direction", color = Muted, fontSize = 11.sp) }; Row(Modifier.width(120.dp).height(40.dp).clip(RoundedCornerShape(10.dp))) { palette.colors.forEach { color -> Box(Modifier.weight(1f).fillMaxHeight().background(parseColor(color))) } } } }
}

@Composable private fun ConnectionFooter(loading: Boolean) {
    Row(Modifier.fillMaxWidth().padding(top = 2.dp), verticalAlignment = Alignment.CenterVertically) { Icon(if (loading) Icons.Default.Refresh else Icons.Default.Check, null, tint = if (loading) Color(0xFFFFC857) else Cyan, modifier = Modifier.size(13.dp)); Spacer(Modifier.width(6.dp)); Text(if (loading) "Connecting to WallBloom engine…" else "WallBloom engine connected", color = Muted, fontSize = 10.sp); Spacer(Modifier.weight(1f)); Text("v1.0", color = Muted, fontSize = 10.sp) }
}

private fun parseColor(value: String): Color = try { Color(android.graphics.Color.parseColor(value)) } catch (_: Exception) { Color.Gray }
private fun patternGlyph(type: String): String = mapOf(
    "hills" to "⛰", "waves" to "🌊", "dunes" to "🏜", "mountains" to "🗻", "arcs" to "🌈",
    "scribble" to "✏️", "geometric" to "🔷", "noise" to "🌫", "gradient" to "🎨", "cellular" to "🔲",
    "spiral" to "🌀", "hexagon" to "⬡", "aurora" to "🌌", "mandala" to "🪷", "vortex" to "💫",
    "lightning" to "⚡", "bubbles" to "🫧", "diamond" to "💎", "lava" to "🌋", "circuit" to "🔌",
    "galaxy" to "🌠", "ripple" to "💧", "mosaic" to "🪟", "terraces" to "🏔", "tides" to "🌬",
    "sandstorm" to "🌪", "peaks" to "⛰", "rings" to "🎯", "brushstroke" to "🖌", "contour" to "🗺",
    "plaid" to "🧣", "starburst" to "✨", "weave" to "🧺", "pebbles" to "🪨", "chevron" to "〽️",
    "fractal" to "🔺", "cobweb" to "🕸", "origami" to "📐", "noodles" to "🍜", "crystals" to "💠",
    "smoke" to "💨", "labyrinth" to "🌀", "polka" to "🔵", "feathers" to "🪶", "scales" to "🐟",
    "crosshatch" to "✖️", "dna" to "🧬", "binary_rain" to "💻", "radar" to "📡", "topographic" to "🗾",
    "waveform" to "〰️", "satellite" to "🛰️", "sonar" to "🔊", "datastream" to "📊", "fiber_optic" to "🔆",
    "neural" to "🧠", "coral" to "🪸", "snowflakes" to "❄️", "raindrops" to "🌧", "vines" to "🌿",
    "clouds" to "☁️", "bamboo" to "🎋", "cracks" to "🪨", "roots" to "🌱", "voronoi" to "🔹",
    "kaleidoscope" to "🔮", "triangular_mesh" to "📐", "pinwheel" to "🎡", "prism" to "🔻", "hypnotic" to "🌐",
    "plasma" to "⚡", "interference" to "〰️", "turbulence" to "🌪", "ink_blot" to "🖋", "watercolor" to "🎨",
    "pointillism" to "🔴", "maze" to "🧩", "constellation" to "⭐", "lace" to "🕸", "glitch" to "📺",
    "stained_glass" to "🪟", "topsoil" to "🌾", "fish_net" to "🎣", "honeycomb_flow" to "🍯", "pixel_sort" to "🖥️",
    "sand_ripple" to "🏖️", "tree_rings" to "🌳", "lightning_field" to "⚡", "soap_bubble" to "🫧",
    "celtic_knot" to "☘️", "meteor_shower" to "🌠", "lenticular" to "🌈", "brush_grid" to "🖌️", "neon_grid" to "🔲"
)[type.lowercase()] ?: "🎨"
private fun patternFamily(type: String): String = when { type in listOf("hills", "waves", "dunes", "mountains", "peaks") -> "Nature"; type.contains("grid") || type.contains("hex") || type.contains("mesh") -> "Geometric"; type.contains("galaxy") || type.contains("aurora") || type.contains("nebula") -> "Celestial"; else -> "Abstract" }
private fun patternBrush(type: String): Brush = when (patternFamily(type)) { "Nature" -> Brush.linearGradient(listOf(Color(0xFF1E5B68), Color(0xFF8BC6A8))); "Geometric" -> Brush.linearGradient(listOf(Color(0xFF452D83), Color(0xFF39A8C8))); "Celestial" -> Brush.linearGradient(listOf(Color(0xFF17114D), Color(0xFFCB5CE6))); else -> Brush.linearGradient(listOf(Color(0xFF29355B), Color(0xFF7C58C7))) }

private fun savePng(context: android.content.Context, bytes: ByteArray, name: String) {
    val values = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, "$name.png")
        put(MediaStore.Images.Media.MIME_TYPE, "image/png")
        put(MediaStore.Images.Media.RELATIVE_PATH, "${Environment.DIRECTORY_PICTURES}/WallBloom")
        put(MediaStore.Images.Media.IS_PENDING, 1)
    }
    val resolver = context.contentResolver
    val uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values) ?: error("Unable to create image")
    resolver.openOutputStream(uri).use { output -> output?.write(bytes) ?: error("Unable to write image") }
    values.clear(); values.put(MediaStore.Images.Media.IS_PENDING, 0); resolver.update(uri, values, null, null)
    Toast.makeText(context, "Saved to Pictures/WallBloom", Toast.LENGTH_SHORT).show()
}
