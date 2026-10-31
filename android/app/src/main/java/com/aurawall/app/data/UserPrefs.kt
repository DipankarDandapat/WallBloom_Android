package com.aurawall.app.data

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

enum class ThemeMode { SYSTEM, LIGHT, DARK }

data class Settings(
    val theme: ThemeMode = ThemeMode.DARK,
    val amoled: Boolean = false,
    val orientation: Orientation = Orientation.PHONE,
)

private val Context.dataStore by preferencesDataStore(name = "wallbloom")

/** Persisted user state: favourites and appearance settings. */
class UserPrefs(private val context: Context) {
    private val favoritesKey = stringPreferencesKey("favorites")
    private val themeKey = stringPreferencesKey("theme")
    private val amoledKey = booleanPreferencesKey("amoled")
    private val orientationKey = stringPreferencesKey("orientation")

    val favorites: Flow<List<Wallpaper>> = context.dataStore.data.map { CatalogJson.parseWallpapers(it[favoritesKey]) }

    val settings: Flow<Settings> = context.dataStore.data.map { prefs ->
        Settings(
            theme = prefs[themeKey]?.let { runCatching { ThemeMode.valueOf(it) }.getOrNull() } ?: ThemeMode.DARK,
            amoled = prefs[amoledKey] ?: false,
            orientation = Orientation.from(prefs[orientationKey]),
        )
    }

    /** Adds or removes [wallpaper]; returns true when it is now a favourite. */
    suspend fun toggleFavorite(wallpaper: Wallpaper): Boolean {
        var added = false
        context.dataStore.edit { prefs ->
            val current = CatalogJson.parseWallpapers(prefs[favoritesKey])
            val next = if (current.any { it.id == wallpaper.id }) current.filterNot { it.id == wallpaper.id }
            else listOf(wallpaper) + current
            added = next.size > current.size
            prefs[favoritesKey] = CatalogJson.wallpapersToJson(next)
        }
        return added
    }

    suspend fun setTheme(mode: ThemeMode) = context.dataStore.edit { it[themeKey] = mode.name }
    suspend fun setAmoled(enabled: Boolean) = context.dataStore.edit { it[amoledKey] = enabled }
    suspend fun setOrientation(orientation: Orientation) = context.dataStore.edit { it[orientationKey] = orientation.key }
}
