# Asset Loading - Simplified Design

## Overview

The `AssetManager` now uses a clean, DRY-compliant approach with an `is_preloading` property and optional completion callback. No more wasteful double-pass through the filesystem.

## Design Pattern: Option 4 (Property + Optional Callback)

### Key Features

1. **`is_preloading` Property**: Check loading status at any time
2. **Optional `on_complete` Callback**: Get notified when loading finishes
3. **Single Pass**: Assets loaded once, no pre-counting phase
4. **Clean API**: Simple function call, no forced syntax patterns

## API

### Property

```python
@property
def is_preloading(self) -> bool:
    """Check if assets are currently being loaded"""
```

### Main Function

```python
def preload_assets(
    self, 
    font_sizes: Optional[list] = None,
    on_complete: Optional[Callable[[int, int, int], None]] = None
) -> Tuple[int, int, int]:
    """Preload all assets (sounds, music, fonts)
    
    Args:
        font_sizes: List of font sizes to preload. If None, uses constants (24, 32, 48, 72)
        on_complete: Optional callback(sounds, music, fonts) called when complete
        
    Returns:
        Tuple of (sounds_loaded, music_registered, fonts_loaded)
    """
```

### Individual Functions

```python
def preload_sounds(self) -> int:
    """Load all sound files. Returns count."""

def preload_music(self) -> int:
    """Register all music files. Returns count."""

def preload_fonts(self, sizes: Optional[list] = None) -> int:
    """Load all fonts at specified sizes. Returns count."""
```

## Usage Examples

### Basic Usage (Blocking)

```python
# Simple blocking load
sounds, music, fonts = asset_manager.preload_assets()
print(f"Loaded: {sounds} sounds, {music} music, {fonts} fonts")
```

### With Completion Callback

```python
def on_loaded(sounds: int, music: int, fonts: int):
    print(f"Assets ready: {sounds} sounds, {music} music, {fonts} fonts")

# Callback fires after loading completes
asset_manager.preload_assets(on_complete=on_loaded)
```

### With Loading Screen (Polling Pattern)

```python
import threading

def load_assets_async():
    """Load assets in background thread"""
    asset_manager.preload_assets()

# Start loading in background
thread = threading.Thread(target=load_assets_async, daemon=True)
thread.start()

# Show loading screen while assets load
while asset_manager.is_preloading:
    render_loading_screen()
    # Show spinner or marquee
    pygame.display.flip()

# Assets loaded, continue to game
start_game()
```

### With Custom Font Sizes

```python
# Preload only specific font sizes
sounds, music, fonts = asset_manager.preload_assets(
    font_sizes=[16, 24, 32, 48]
)
```

## Implementation Details

### State Management

```python
class AssetManager:
    def __init__(self):
        self._is_preloading = False  # Tracks loading state
        
    @property
    def is_preloading(self) -> bool:
        return self._is_preloading
    
    def preload_assets(self, ...):
        self._is_preloading = True
        try:
            # Load assets
            sounds = self.preload_sounds()
            music = self.preload_music()
            fonts = self.preload_fonts(sizes)
            return (sounds, music, fonts)
        finally:
            # Always cleanup, even on exception
            self._is_preloading = False
            if on_complete:
                on_complete(sounds, music, fonts)
```

### Thread Safety Note

The current implementation is **not thread-safe**. If you need concurrent access:

```python
import threading

class AssetManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._is_preloading = False
    
    @property
    def is_preloading(self) -> bool:
        with self._lock:
            return self._is_preloading
    
    def preload_assets(self, ...):
        with self._lock:
            if self._is_preloading:
                raise RuntimeError("Assets already loading")
            self._is_preloading = True
        
        try:
            # ... load assets ...
        finally:
            with self._lock:
                self._is_preloading = False
```

## Benefits of This Design

### 1. DRY Compliance ✅
- Single pass through filesystem
- No duplicate file scanning
- No wasted iteration

### 2. Simple API ✅
- Direct function call, no forced patterns
- Optional callback for flexibility
- Property for polling scenarios

### 3. Flexible Usage ✅
- Works in blocking mode (current)
- Easy to adapt for threading
- Easy to adapt for async/await

### 4. Clean Code ✅
- Short, readable implementation
- Minimal overhead
- Easy to maintain

## Comparison: Before vs After

### Before (Progress Callback - Violated DRY)

```python
# BAD: Scanned filesystem twice
def preload_assets(self, progress_callback=None):
    # Phase 1: Count everything (first scan)
    total = count_sounds() + count_music() + count_fonts()
    
    # Phase 2: Load everything (second scan)
    for asset in discover_assets():
        load(asset)
        progress_callback(current, total)
```

**Problems:**
- 🔴 Doubled filesystem I/O
- 🔴 Complex progress tracking
- 🔴 More code to maintain

### After (Property + Callback - DRY Compliant)

```python
# GOOD: Single pass through filesystem
def preload_assets(self, on_complete=None):
    self._is_preloading = True
    try:
        sounds = preload_sounds()  # Loads on first scan
        music = preload_music()    # Loads on first scan
        fonts = preload_fonts()    # Loads on first scan
        return (sounds, music, fonts)
    finally:
        self._is_preloading = False
        if on_complete:
            on_complete(sounds, music, fonts)
```

**Benefits:**
- ✅ Single filesystem scan
- ✅ Simple implementation
- ✅ Less code to maintain

## Real-World Usage (Current Game)

```python
# In game.py
def on_assets_loaded(sounds: int, music: int, fonts: int):
    """Called when asset loading completes"""
    print(f"[INFO] Asset loading complete: {sounds} sounds, {music} music, {fonts} fonts")

sounds, music, fonts = self.asset_manager.preload_assets(
    on_complete=on_assets_loaded
)
```

**Output:**
```
[DEBUG] AssetManager.preload_assets: Starting asset preloading...
[DEBUG] AssetManager.preload_assets: Loading sounds...
[DEBUG] AssetManager.preload_sounds: No sound files found...
[DEBUG] AssetManager.preload_assets: Registering music...
[DEBUG] AssetManager.preload_music: No music files found...
[DEBUG] AssetManager.preload_assets: Loading fonts...
[DEBUG] AssetManager.preload_fonts: Preloading 1 fonts at 5 sizes...
[DEBUG] AssetManager.preload_assets: Asset preloading complete!
[INFO] Asset loading complete: 0 sounds, 0 music, 5 fonts
```

## Future Enhancements

These can be added without breaking the API:

1. **Async/Await Support**:
   ```python
   async def preload_assets_async(self, ...): ...
   ```

2. **Parallel Loading**:
   ```python
   # Load sounds and fonts in parallel
   with ThreadPoolExecutor() as pool:
       future_sounds = pool.submit(self.preload_sounds)
       future_fonts = pool.submit(self.preload_fonts)
   ```

3. **Progress Estimation** (without DRY violation):
   ```python
   # Emit events during loading instead of pre-counting
   for sound in discover_sounds():
       load(sound)
       emit_event("sound_loaded", sound)
   ```

4. **Lazy Loading**:
   ```python
   # Only load when first accessed
   asset_manager.enable_lazy_loading()
   ```

All of these maintain the simple `is_preloading` + `on_complete` pattern.
