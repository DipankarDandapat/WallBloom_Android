package com.aurawall.app

import android.graphics.Color
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.aurawall.app.ui.AppViewModel
import com.aurawall.app.ui.CatalogState
import com.aurawall.app.ui.WallBloomApp
import com.aurawall.app.ui.theme.WallBloomTheme
import com.aurawall.app.ui.theme.isDarkTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val splash = installSplashScreen()
        super.onCreate(savedInstanceState)
        var ready = false
        // Release the OS splash immediately; our SplashScreen composable handles the health gate.
        splash.setKeepOnScreenCondition { !ready }
        setContent {
            val vm: AppViewModel = viewModel(factory = AppViewModel.Factory)
            val settings by vm.settings.collectAsStateWithLifecycle()
            val catalog by vm.catalog.collectAsStateWithLifecycle()
            if (catalog !is CatalogState.Loading || (catalog as CatalogState.Loading).slow) ready = true
            DisposableEffect(Unit) {
                val handler = android.os.Handler(mainLooper)
                val release = Runnable { ready = true }
                handler.postDelayed(release, 900)
                onDispose { handler.removeCallbacks(release) }
            }
            WallBloomTheme(settings) {
                val dark = isDarkTheme(settings)
                DisposableEffect(dark) {
                    val style = if (dark) SystemBarStyle.dark(Color.TRANSPARENT) else SystemBarStyle.light(Color.TRANSPARENT, Color.TRANSPARENT)
                    enableEdgeToEdge(statusBarStyle = style, navigationBarStyle = style)
                    onDispose { }
                }
                WallBloomApp(vm)
            }
        }
    }
}
