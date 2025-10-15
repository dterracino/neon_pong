# Asset Loading System

## Overview

The `AssetManager` automatically discovers and loads all assets from their respective directories. Assets are stored in dictionaries with **lowercase filename keys (without extensions)**.

## Directory Structure

```
assets/
├── fonts/          # .ttf, .otf, .fon files
├── sounds/         # .wav, .ogg, .mp3, .flac files
└── music/          # .wav, .ogg, .mp3, .flac, .mid, .midi files
```

## Automatic Loading

Assets are automatically loaded during game initialization:

```python
# In game.py
self.asset_manager = AssetManager()
self.asset_manager.preload_sounds()   # Loads all sound files
self.asset_manager.preload_music()    # Registers all music files
self.asset_manager.preload_fonts()    # Loads all fonts at default sizes
```

## Usage Examples

### Sounds

**File**: `assets/sounds/paddle_hit.wav`

```python
# Play sound by name (without extension)
audio_manager.play_sound('paddle_hit')

# Get sound directly from asset manager
sound = asset_manager.get_sound('paddle_hit')
if sound:
    sound.play()
```

### Music

**File**: `assets/music/background_theme.ogg`

```python
# Load and play music by name (without extension)
audio_manager.play_music('background_theme')

# Get music file path
music_path = asset_manager.get_music_path('background_theme')
```

### Fonts

**File**: `assets/fonts/ARCADECLASSIC.TTF`

```python
# Get font by filename and size
font = asset_manager.get_font('ARCADECLASSIC.TTF', 48)

# Get default pygame font
font = asset_manager.get_font(None, 32)
```

## Key Features

1. **Case-Insensitive**: All lookups use lowercase keys
   - File: `Paddle_Hit.WAV` → Key: `paddle_hit`
   - File: `Background_Theme.ogg` → Key: `background_theme`

2. **Extension Agnostic**: Reference assets without extensions
   ```python
   # Both files work the same way:
   # paddle_hit.wav
   # paddle_hit.ogg
   audio_manager.play_sound('paddle_hit')
   ```

3. **Automatic Discovery**: Just drop files in the correct folder
   - No need to manually register each asset
   - All files are discovered on startup

4. **Graceful Fallback**: Missing assets don't crash the game
   - Sounds/music return `None` if not found
   - Fonts fall back to default pygame font

## Adding New Assets

### To Add Sounds:
1. Place `.wav`, `.ogg`, `.mp3`, or `.flac` files in `assets/sounds/`
2. Restart the game (auto-loaded on startup)
3. Use filename (without extension) in code: `play_sound('your_sound')`

### To Add Music:
1. Place audio files in `assets/music/`
2. Restart the game (auto-registered on startup)
3. Use filename (without extension) in code: `play_music('your_music')`

### To Add Fonts:
1. Place `.ttf`, `.otf`, or `.fon` files in `assets/fonts/`
2. Restart the game (auto-loaded at default sizes)
3. Use filename in code: `get_font('your_font.ttf', 48)`

## Default Font Sizes

Fonts are preloaded at these sizes by default (from constants):
- `FONT_SIZE_SMALL = 24`
- `FONT_SIZE_DEFAULT = 32`
- `FONT_SIZE_MEDIUM = 48`
- `FONT_SIZE_LARGE = 72`

To preload custom sizes:
```python
asset_manager.preload_fonts(sizes=[16, 20, 36, 80])
```

## Debug Output

The asset manager provides detailed debug logs:

```
[DEBUG] AssetManager.preload_sounds: Loading 4 sound files...
[DEBUG] AssetManager.load_sound: Loaded sound 'paddle_hit' from paddle_hit.wav
[DEBUG] AssetManager.preload_sounds: Loaded 4 sounds

[DEBUG] AssetManager.preload_music: Found 2 music files...
[DEBUG] AssetManager.preload_music: Registered music 'background_theme' -> background_theme.ogg
[DEBUG] AssetManager.preload_music: Registered 2 music files

[DEBUG] AssetManager.preload_fonts: Preloading 1 fonts at 5 sizes...
[DEBUG] AssetManager.preload_fonts: Preloaded ARCADECLASSIC.TTF at size 24
[DEBUG] AssetManager.preload_fonts: Preloaded 5 font/size combinations
```

## Singleton Pattern

`AssetManager` is a singleton - the same instance is shared everywhere:

```python
# These all reference the same instance
asset_manager1 = AssetManager()
asset_manager2 = AssetManager()
assert asset_manager1 is asset_manager2  # True
```

This ensures assets are loaded only once and shared across all systems.
