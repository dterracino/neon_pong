# Quick Reference: Files with Differences

This document provides a quick lookup for the 7 files that have differences between the `.compare` folder and the repository.

## Priority 1: Merge Conflicts (Requires Manual Resolution) 🚨

### 1. `src/scenes/game_scene.py`

**Conflicts:**

- Line 66-74: Music playback method
  - HEAD: `self.audio_manager.play_music('background')`
  - Other: `self.audio_manager.play_music('game_music.ogg')`
  
- Line 81-87: Pause screen setup
  - HEAD: Simple pause with sound effect
  - Other: Screenshot capture for blurred background
  
- Line 167-177: Score sound logic
  - HEAD: Standard score sound
  - Other: Contextual sounds (score vs ball-miss) based on game mode

**Decision Needed:** Choose audio API approach (normalized names vs file extensions)

---

### 2. `src/scenes/menu_scene.py`

**Conflicts:**

- Line 52-60: Music playback method
  - HEAD: `self.audio_manager.play_music('title')`
  - Other: `self.audio_manager.play_music('menu_music.ogg')`
  
- Lines 67, 73, 76: Menu navigation sound effects
  - HEAD: Includes `menu-move` and `menu-select` sounds
  - Other: No sound effects

**Decision Needed:**

1. Choose audio API approach
2. Decide if menu navigation sounds should be included

---

### 3. `src/scenes/pause_scene.py`

**Conflicts:**

- Line 110-124: Pause behavior
  - HEAD: `duck_music(0.5)` - Lower volume to 50%
  - Other: `pause_music()` - Stop music completely
  
- Lines 131, 134, 137, 139: Menu navigation sounds
  - HEAD: Includes `pause`, `menu-move`, `menu-select` sounds
  - Other: No sound effects

**Decision Needed:**

1. Choose pause behavior (ducking vs stopping music)
2. Decide if pause menu sounds should be included

**Note:** Audio ducking requires the changes in `src/audio/audio_manager.py`

---

## Priority 2: Safe to Merge After Review ✅

### 4. `src/game.py`

**Changes:** 2 lines added (no deletions)

```python
# Always capture to memory for pause screen (non-blocking, minimal overhead)
self.screenshot_manager.capture_to_memory(self.screen)
```

**Location:** Line 208-209 (after screenshot save logic)

**Purpose:** Continuously captures screen to memory so pause screen can show blurred background

**Risk:** Low - non-invasive addition

**Recommendation:** Merge after confirming it works with pause screen implementation

---

## Priority 3: Requires Detailed Review 📋

### 5. `shaders/dust_overlay.frag`

**Changes:** 6 additions, 2 deletions (mixed)

**Key Modifications:**

**Change 1 (Lines 80-82):**

```glsl
// OLD:
float noiseVal = noise(vec2(particleId * 0.1, timeScale * freq));

// NEW:
float wrappedTime = mod(timeScale * freq, 100.0);
float noiseVal = noise(vec2(particleId * 0.1, wrappedTime));
```

**Change 2 (Lines 97-99):**

```glsl
// OLD:
vec2 displacement = velocity * time;

// NEW:
float wrappedTime = mod(time, 100.0);
vec2 displacement = velocity * wrappedTime;
```

**Purpose:** Prevent floating-point precision issues by wrapping time values

**Risk:** Low - this is a bug fix

**Recommendation:** Merge - prevents potential shader issues in long-running sessions

---

### 6. `src/audio/audio_manager.py`

**Changes:** 23 additions, 1 deletion (mostly additions)

**New Features Added:**

1. **Duck/Unduck Methods:**

```python
def duck_music(self, duck_amount: float = 0.5):
    """Lower music volume (audio ducking)"""
    if not self._is_ducked:
        self._is_ducked = True
        ducked_volume = self.music_volume * duck_amount
        pygame.mixer.music.set_volume(ducked_volume)

def unduck_music(self):
    """Restore music to normal volume"""
    if self._is_ducked:
        self._is_ducked = False
        pygame.mixer.music.set_volume(self.music_volume)
```

1. **State Tracking:**

- Added `self._is_ducked` flag to track ducking state

1. **Modified `set_music_volume()`:**

- Now respects ducking state when changing volume

**Dependencies:** Used by `src/scenes/pause_scene.py` (if ducking approach is chosen)

**Risk:** Low - backward compatible, adds functionality without breaking existing code

**Recommendation:** Merge if audio ducking feature is desired (pairs with pause_scene changes)

---

### 7. `src/managers/asset_manager.py`

**Changes:** 96 additions, 44 deletions (major refactoring)

**Major Changes:**

1. **New Static Method:**

```python
@staticmethod
def _normalize_asset_name(filename: str) -> str:
    """Normalize asset name: lowercase, no extension, slug-style"""
```

1. **Asset Naming Convention:**

- Converts filenames to lowercase, hyphenated format
- Removes file extensions
- Examples:
  - `"Hit_Sound.WAV"` → `"hit-sound"`
  - `"Retro Gaming.ttf"` → `"retro-gaming"`
  - `"Menu__Select!!!.wav"` → `"menu-select"`

1. **Modified Methods:**

- Significant changes to `get_font()` and asset lookup logic
- Changes to how assets are cached and retrieved

**Dependencies:**

- Affects how all assets are referenced throughout the codebase
- Related to the audio API conflicts (normalized names vs file extensions)

**Risk:** High - breaking changes if asset names don't match new convention

**Recommendation:**

1. Review thoroughly
2. Test with all existing assets
3. May need to rename asset files or update references
4. Consider as part of larger audio system refactoring

---

## Dependency Chain

If implementing the changes, follow this order:

1. **Resolve Conflicts First:**
   - Decide on audio API (normalized vs file extensions)
   - This decision affects game_scene, menu_scene, pause_scene, and asset_manager

2. **Then Choose Path A or B:**

   **Path A: Normalized Names + Audio Ducking**
   - Merge `src/managers/asset_manager.py`
   - Merge `src/audio/audio_manager.py`
   - Resolve conflicts choosing "HEAD" side (normalized names, ducking)
   - Ensure all audio files match normalized naming

   **Path B: File Extensions + Music Pausing**
   - Resolve conflicts choosing "Other" side (file extensions, pausing)
   - Do NOT merge asset_manager.py changes
   - Do NOT merge audio_manager.py audio ducking changes
   - Keep existing asset naming

3. **Finally, Safe Additions:**
   - Merge `shaders/dust_overlay.frag` (independent bug fix)
   - Merge `src/game.py` (if pause screen uses screenshot)

---

## Asset File Implications

If choosing Path A (normalized names), ensure these audio files exist:

- `background.ogg` or similar (for game music)
- `title.ogg` or similar (for menu music)
- `pause.wav` or similar (for pause sound)
- `menu-move.wav` or similar (for menu navigation)
- `menu-select.wav` or similar (for menu selection)
- `score.wav` (for scoring)
- `ball-miss.wav` (for missed ball in 1P mode)

Current asset references in conflicts suggest files may use different names.

---

## Testing Checklist

After merging any changes, test:

- [ ] Game music starts correctly in game scene
- [ ] Menu music plays in menu
- [ ] Pause menu behavior (music ducking or stopping)
- [ ] Menu navigation sounds work (if included)
- [ ] Pause screen background blur (if screenshot capture included)
- [ ] Score sounds in both 1P and 2P modes
- [ ] Dust overlay shader runs without issues
- [ ] All assets load correctly with new naming (if asset_manager merged)

---

## Files with No Changes (36 files)

These files are identical and require no action:

- All core game files (`main.py`)
- All AI files
- All entity files  
- All rendering files
- Most shader files (16 of 17)
- All utility files
- Scene and shader manager files

See COMPARISON_REPORT.md for complete list.
