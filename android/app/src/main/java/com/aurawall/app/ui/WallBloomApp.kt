@file:OptIn(ExperimentalSharedTransitionApi::class)

package com.aurawall.app.ui

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.ExperimentalSharedTransitionApi
import androidx.compose.animation.SharedTransitionLayout
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.animation.expandHorizontally
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.shrinkHorizontally
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.slideOutVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.ErrorOutline
import androidx.compose.material.icons.rounded.Explore
import androidx.compose.material.icons.rounded.Favorite
import androidx.compose.material.icons.rounded.Landscape
import androidx.compose.material.icons.rounded.Tune
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.aurawall.app.data.Orientation
import com.aurawall.app.data.Wallpaper
import com.aurawall.app.ui.components.LocalNavAnimatedScope
import com.aurawall.app.ui.components.LocalSharedTransitionScope
import com.aurawall.app.ui.screens.CollectionScreen
import com.aurawall.app.ui.screens.DiscoverScreen
import com.aurawall.app.ui.screens.PreviewScreen
import com.aurawall.app.ui.screens.SavedScreen
import com.aurawall.app.ui.screens.ScenesScreen
import com.aurawall.app.ui.screens.SearchScreen
import com.aurawall.app.ui.screens.SettingsScreen
import com.aurawall.app.ui.screens.SplashScreen
import com.aurawall.app.ui.screens.StudioScreen
import com.aurawall.app.ui.theme.Brand
import kotlinx.coroutines.delay

enum class Tab(val label: String, val icon: ImageVector) {
    DISCOVER("Discover", Icons.Rounded.Explore),
    SCENES("Scenes", Icons.Rounded.Landscape),
    STUDIO("Studio", Icons.Rounded.Tune),
    SAVED("Saved", Icons.Rounded.Favorite),
}

object Routes {
    const val SPLASH = "splash"
    const val HOME = "home"
    const val PREVIEW = "preview"
    const val SEARCH = "search"
    const val SETTINGS = "settings"
    const val COLLECTION = "collection/{id}"
    fun collection(id: String) = "collection/$id"
}

/** Navigation actions shared by every screen. */
class AppNavigator(private val nav: NavHostController, private val vm: AppViewModel) {
    fun preview(items: List<Wallpaper>, index: Int, orientation: Orientation, origin: String) {
        vm.openPreview(items, index, orientation)
        nav.navigate("${Routes.PREVIEW}?origin=$origin") { launchSingleTop = true }
    }
    fun collection(id: String) = nav.navigate(Routes.collection(id))
    fun search() = nav.navigate(Routes.SEARCH)
    fun settings() = nav.navigate(Routes.SETTINGS)
    fun back() = nav.popBackStack()
}

@Composable
fun WallBloomApp(vm: AppViewModel) {
    val nav = rememberNavController()
    val navigator = androidx.compose.runtime.remember(nav, vm) { AppNavigator(nav, vm) }
    var tab by rememberSaveable { mutableStateOf(Tab.DISCOVER) }
    var message by androidx.compose.runtime.remember { mutableStateOf<UiMessage?>(null) }

    LaunchedEffect(vm) { vm.messages.collect { message = it } }
    LaunchedEffect(message) { if (message != null) { delay(3200); message = null } }

    Box(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        SharedTransitionLayout {
            CompositionLocalProvider(LocalSharedTransitionScope provides this) {
                NavHost(
                    nav, startDestination = Routes.SPLASH,
                    enterTransition = { slideInHorizontally(tween(320)) { it / 5 } + fadeIn(tween(320)) },
                    exitTransition = { fadeOut(tween(220)) },
                    popEnterTransition = { fadeIn(tween(280)) },
                    popExitTransition = { slideOutHorizontally(tween(280)) { it / 5 } + fadeOut(tween(240)) },
                ) {
                    composable(Routes.SPLASH) {
                        SplashScreen(vm) {
                            nav.navigate(Routes.HOME) {
                                popUpTo(Routes.SPLASH) { inclusive = true }
                            }
                        }
                    }
                    composable(Routes.HOME) {
                        CompositionLocalProvider(LocalNavAnimatedScope provides this) {
                            HomeShell(vm, navigator, tab) { tab = it }
                        }
                    }
                    composable(
                        "${Routes.PREVIEW}?origin={origin}",
                        enterTransition = { fadeIn(tween(260)) }, exitTransition = { fadeOut(tween(200)) },
                        popEnterTransition = { fadeIn(tween(260)) }, popExitTransition = { fadeOut(tween(260)) },
                    ) { entry ->
                        CompositionLocalProvider(LocalNavAnimatedScope provides this) {
                            PreviewScreen(vm, entry.arguments?.getString("origin") ?: "", onBack = navigator::back)
                        }
                    }
                    composable(Routes.COLLECTION) { entry ->
                        CompositionLocalProvider(LocalNavAnimatedScope provides this) {
                            CollectionScreen(vm, navigator, entry.arguments?.getString("id").orEmpty())
                        }
                    }
                    composable(Routes.SEARCH) {
                        CompositionLocalProvider(LocalNavAnimatedScope provides this) { SearchScreen(vm, navigator) }
                    }
                    composable(Routes.SETTINGS) { SettingsScreen(vm, onBack = navigator::back) }
                }
            }
        }

        AnimatedVisibility(
            visible = message != null,
            enter = slideInVertically { -it } + fadeIn(), exit = slideOutVertically { -it } + fadeOut(),
            modifier = Modifier.align(Alignment.TopCenter).statusBarsPadding().padding(top = 8.dp, start = 16.dp, end = 16.dp),
        ) {
            message?.let { MessageToast(it) }
        }
    }
}

@Composable
private fun HomeShell(vm: AppViewModel, navigator: AppNavigator, tab: Tab, onTab: (Tab) -> Unit) {
    Box(Modifier.fillMaxSize()) {
        AnimatedContent(
            targetState = tab,
            transitionSpec = {
                val forward = targetState.ordinal > initialState.ordinal
                (fadeIn(tween(240)) + slideInHorizontally(tween(280)) { if (forward) it / 10 else -it / 10 })
                    .togetherWith(fadeOut(tween(160)))
            },
            label = "tabs",
        ) { current ->
            when (current) {
                Tab.DISCOVER -> DiscoverScreen(vm, navigator)
                Tab.SCENES -> ScenesScreen(vm, navigator)
                Tab.STUDIO -> StudioScreen(vm, navigator)
                Tab.SAVED -> SavedScreen(vm, navigator, onExplore = { onTab(Tab.DISCOVER) })
            }
        }
        FloatingNavBar(tab, onTab, Modifier.align(Alignment.BottomCenter).navigationBarsPadding().padding(bottom = 12.dp))
    }
}

@Composable
private fun FloatingNavBar(selected: Tab, onSelect: (Tab) -> Unit, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.shadow(24.dp, RoundedCornerShape(28.dp), ambientColor = Color.Black, spotColor = Color.Black),
        shape = RoundedCornerShape(28.dp),
        color = MaterialTheme.colorScheme.surfaceContainerHigh.copy(alpha = .94f),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
    ) {
        Row(Modifier.padding(6.dp).height(48.dp), horizontalArrangement = Arrangement.spacedBy(4.dp), verticalAlignment = Alignment.CenterVertically) {
            Tab.entries.forEach { tab ->
                val active = tab == selected
                Row(
                    Modifier.clip(RoundedCornerShape(22.dp))
                        .then(if (active) Modifier.background(Brand.SoftGradient) else Modifier)
                        .clickable(role = Role.Tab, onClickLabel = tab.label) { onSelect(tab) }
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(tab.icon, tab.label, tint = if (active) Color.White else MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.size(22.dp))
                    AnimatedVisibility(
                        active,
                        enter = expandHorizontally(spring(Spring.DampingRatioLowBouncy, Spring.StiffnessMediumLow)) + fadeIn(),
                        exit = shrinkHorizontally(spring(stiffness = Spring.StiffnessMedium)) + fadeOut(),
                    ) {
                        Row {
                            Spacer(Modifier.width(8.dp))
                            Text(tab.label, color = Color.White, style = MaterialTheme.typography.labelLarge)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MessageToast(message: UiMessage) {
    Surface(
        shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.inverseSurface,
        shadowElevation = 12.dp,
    ) {
        Row(Modifier.padding(horizontal = 16.dp, vertical = 13.dp), verticalAlignment = Alignment.CenterVertically) {
            AnimatedContent(message.isError, transitionSpec = { scaleIn() togetherWith fadeOut() }, label = "toast-icon") { error ->
                Icon(
                    if (error) Icons.Rounded.ErrorOutline else Icons.Rounded.CheckCircle, null,
                    tint = if (error) Brand.Danger else Brand.Success, modifier = Modifier.size(20.dp),
                )
            }
            Spacer(Modifier.width(10.dp))
            Text(message.text, color = MaterialTheme.colorScheme.inverseOnSurface, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
