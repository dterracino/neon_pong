# File Comparison Report
**Date:** tmp
**Repository:** neon_pong
**Total Files Analyzed:** 43

## Summary

- **Identical Files:** 36
- **Files with Differences:** 7
- **Files with Merge Conflicts:** 3 ⚠️
- **New Files:** 0
- **Errors:** 0

⚠️ **IMPORTANT:** Some files contain unresolved merge conflict markers. These must be resolved manually before changes can be applied.

## Detailed Comparison Results

### 1. `main.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 2. `shaders/background_plasma.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 3. `shaders/background_retro.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 4. `shaders/background_retrowave.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 5. `shaders/background_starfield.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 6. `shaders/background_waves.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 7. `shaders/basic.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 8. `shaders/basic.vert`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 9. `shaders/bloom_blur.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 10. `shaders/bloom_combine.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 11. `shaders/bloom_extract.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 12. `shaders/crt.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 13. `shaders/dust_overlay.frag`

**Status:** ⚠️ DIFFERENCES FOUND

**Recommendation:** MIXED CHANGES: 6 additions, 2 deletions. Review changes carefully to determine merge strategy.

**Change Summary:**
- Additions: 6 lines
- Deletions: 2 lines
- Total diff lines: 24

<details>
<summary>View Diff (first 50 lines)</summary>

```diff
--- original/shaders/dust_overlay.frag
+++ .compare/shaders/dust_overlay.frag
@@ -77,7 +77,9 @@
         float angleOffset = 0.0;
         for (int octave = 0; octave < 8; octave++) {
             float freq = pow(2.0, float(octave)) * directionChangeRate;
-            float noiseVal = noise(vec2(particleId * 0.1, timeScale * freq));
+            // Wrap time in noise lookup to prevent unbounded accumulation
+            float wrappedTime = mod(timeScale * freq, 100.0);
+            float noiseVal = noise(vec2(particleId * 0.1, wrappedTime));

             // Convert noise to angle change (±22.5 degrees = ±0.3927 radians)
             // Weight decreases with each octave for smoother motion
@@ -92,7 +94,9 @@
         vec2 velocity = vec2(cos(currentAngle), sin(currentAngle)) * baseSpeed;

         // Integrate velocity over time to get position
-        vec2 displacement = velocity * time;
+        // Wrap time to prevent runaway displacement values
+        float wrappedTime = mod(time, 100.0);
+        vec2 displacement = velocity * wrappedTime;

         // Particle position (wraps around screen)
         vec2 particlePos = vec2(
```

</details>

---

### 14. `shaders/scanlines.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 15. `shaders/text.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 16. `shaders/text.vert`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 17. `shaders/vhs.frag`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 18. `src/__init__.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 19. `src/ai/__init__.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 20. `src/ai/pong_ai.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 21. `src/audio/__init__.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 22. `src/audio/audio_manager.py`

**Status:** ⚠️ DIFFERENCES FOUND

**Recommendation:** MIXED CHANGES: 23 additions, 1 deletions. Review changes carefully to determine merge strategy.

**Change Summary:**
- Additions: 23 lines
- Deletions: 1 lines
- Total diff lines: 43

<details>
<summary>View Diff (first 50 lines)</summary>

```diff
--- original/src/audio/audio_manager.py
+++ .compare/src/audio/audio_manager.py
@@ -14,6 +14,7 @@
         self.asset_manager = asset_manager
         self.music_volume = MUSIC_VOLUME
         self.sfx_volume = SFX_VOLUME
+        self._is_ducked = False  # Track if music is currently ducked

     def play_sound(self, sound_name: str, pitch_variation: bool = False):
         """Play a sound effect by name (without extension)"""
@@ -47,10 +48,31 @@
         """Resume background music"""
         pygame.mixer.music.unpause()

+    def duck_music(self, duck_amount: float = 0.5):
+        """Lower music volume (audio ducking)
+
+        Args:
+            duck_amount: Multiplier for volume reduction (0.5 = 50% volume)
+        """
+        if not self._is_ducked:
+            self._is_ducked = True
+            ducked_volume = self.music_volume * duck_amount
+            pygame.mixer.music.set_volume(ducked_volume)
+
+    def unduck_music(self):
+        """Restore music to normal volume"""
+        if self._is_ducked:
+            self._is_ducked = False
+            pygame.mixer.music.set_volume(self.music_volume)
+
     def set_music_volume(self, volume: float):
         """Set music volume (0.0 to 1.0)"""
         self.music_volume = max(0.0, min(1.0, volume))
-        pygame.mixer.music.set_volume(self.music_volume)
+        # Apply volume immediately, respecting duck state
+        if self._is_ducked:
+            pygame.mixer.music.set_volume(self.music_volume * 0.5)
+        else:
+            pygame.mixer.music.set_volume(self.music_volume)

     def set_sfx_volume(self, volume: float):
         """Set sound effects volume (0.0 to 1.0)"""
```

</details>

---

### 23. `src/entities/__init__.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 24. `src/entities/ball.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 25. `src/entities/enhanced_particles.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 26. `src/entities/paddle.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 27. `src/entities/particle.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 28. `src/game.py`

**Status:** ⚠️ DIFFERENCES FOUND

**Recommendation:** ADDITIONS ONLY: 2 line(s) added. These additions can likely be merged into the original file. Review changes to ensure they don't conflict with existing functionality.

**Change Summary:**
- Additions: 2 lines
- Deletions: 0 lines
- Total diff lines: 11

<details>
<summary>View Diff (first 50 lines)</summary>

```diff
--- original/src/game.py
+++ .compare/src/game.py
@@ -206,6 +206,8 @@
                     logger.error("Failed to capture screenshot: %s", e)
                 self.pending_screenshot = False

+            # Always capture to memory for pause screen (non-blocking, minimal overhead)
+            self.screenshot_manager.capture_to_memory(self.screen)

             if frame_count < 5:
                 logger.debug("Frame %d complete", frame_count)
```

</details>

---

### 29. `src/managers/asset_manager.py`

**Status:** ⚠️ DIFFERENCES FOUND

**Recommendation:** MIXED CHANGES: 96 additions, 44 deletions. Review changes carefully to determine merge strategy.

**Change Summary:**
- Additions: 96 lines
- Deletions: 44 lines
- Total diff lines: 173

<details>
<summary>View Diff (first 50 lines)</summary>

```diff
--- original/src/managers/asset_manager.py
+++ .compare/src/managers/asset_manager.py
@@ -52,23 +52,90 @@
         os.makedirs(self.sounds_path, exist_ok=True)
         os.makedirs(self.music_path, exist_ok=True)

-    def get_font(self, name: Optional[str] = None, size: int = 32) -> pygame.font.Font:
-        """Get a font, creating it if not cached"""
-        key = (name, size)
-
-        if key not in self.fonts:
-            try:
-                if name and os.path.exists(os.path.join(self.fonts_path, name)):
-                    font_path = os.path.join(self.fonts_path, name)
-                    self.fonts[key] = pygame.font.Font(font_path, size)
-                    logger.debug("Loaded font '%s' at size %d", name, size)
-                else:
-                    # Use default font
-                    self.fonts[key] = pygame.font.Font(None, size)
-                    logger.debug("Using default pygame font at size %d", size)
-            except Exception as e:
-                logger.error("Error loading font %s: %s", name, e)
+    @staticmethod
+    def _normalize_asset_name(filename: str) -> str:
+        """Normalize asset name: lowercase, no extension, slug-style
+
+        Converts filename to a consistent key format:
+        - Remove extension
+        - Convert to lowercase
+        - Replace spaces, underscores, and punctuation with hyphens
+        - Remove consecutive hyphens
+        - Strip leading/trailing hyphens
+
+        Args:
+            filename: Asset filename like "Hit_Sound.wav" or "Retro Gaming.ttf"
+
+        Returns:
+            Normalized slug like "hit-sound" or "retro-gaming"
+
+        Examples:
+            "Hit_Sound.WAV" -> "hit-sound"
+            "Retro Gaming.ttf" -> "retro-gaming"
+            "background-music.ogg" -> "background-music"
+            "Menu__Select!!!.wav" -> "menu-select"
+        """
+        import re
+
+        # Remove extension and lowercase
+        name = os.path.splitext(filename)[0].lower()
+

... (123 more lines)
```

</details>

---

### 30. `src/managers/scene_manager.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 31. `src/managers/shader_manager.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 32. `src/rendering/post_process.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 33. `src/rendering/renderer.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 34. `src/scenes/game_scene.py`

**Status:** ⚠️ DIFFERENCES FOUND

**Recommendation:** ⚠️ MERGE CONFLICTS DETECTED: The .compare file contains unresolved merge conflict markers (<<<<<<< HEAD, =======, >>>>>>>). This file needs manual conflict resolution before it can be merged. The differences shown represent both sides of the conflict.

**Change Summary:**
- Additions: 28 lines
- Deletions: 6 lines
- Total diff lines: 71

<details>
<summary>View Diff (first 50 lines)</summary>

```diff
--- original/src/scenes/game_scene.py
+++ .compare/src/scenes/game_scene.py
@@ -66,20 +66,28 @@
         self.game_over = False
         self.winner = 0

+<<<<<<< HEAD
+        # Start game music
+        self.audio_manager.play_music('background')
+=======
         # Try to start game music
         self.audio_manager.play_music('game_music.ogg')
+>>>>>>> 9ebc79b77bf4f3eeeba98a93c9675350072c582b
         logger.debug("Game scene created (paddle1: %.1f,%.1f, ball: %.1f,%.1f, ai_enabled: %s)",
                     self.paddle1.x, self.paddle1.y, self.ball.x, self.ball.y, self.ai_enabled)

     def handle_event(self, event):
         if event.type == pygame.KEYDOWN:
             if event.key in (pygame.K_ESCAPE, pygame.K_p):
-                # Take screenshot for pause background before pausing
-                if self.screenshot_manager:
-                    self.screenshot_manager.capture_to_memory(self.renderer.screen)
+<<<<<<< HEAD
+                # Pause game
+                self.audio_manager.play_sound('pause')
+                pause_scene = PauseScene(self.scene_manager, self.renderer, self.audio_manager)
+=======
                 # Pause game - pass screenshot manager for blurred background
                 pause_scene = PauseScene(self.scene_manager, self.renderer, self.audio_manager,
                                         self.screenshot_manager)
+>>>>>>> 9ebc79b77bf4f3eeeba98a93c9675350072c582b
                 self.scene_manager.push_scene(pause_scene)

     def update(self, dt: float):
@@ -159,7 +167,17 @@
             else:
                 self.score2 += 1

-            self.audio_manager.play_sound('score')
+            # Play contextual score sound based on game mode
+            if self.ai_enabled:
+                # 1P mode: Score sound for player scoring, miss sound for AI scoring
+                if scorer == 1:
+                    self.audio_manager.play_sound('score')  # Player scored!
+                else:
+                    self.audio_manager.play_sound('ball-miss')  # AI scored :(
+            else:
+                # 2P mode: Always use score sound (someone scored)
+                self.audio_manager.play_sound('score')
+

... (21 more lines)
```

</details>

---

### 35. `src/scenes/menu_scene.py`

**Status:** ⚠️ DIFFERENCES FOUND

**Recommendation:** ⚠️ MERGE CONFLICTS DETECTED: The .compare file contains unresolved merge conflict markers (<<<<<<< HEAD, =======, >>>>>>>). This file needs manual conflict resolution before it can be merged. The differences shown represent both sides of the conflict.

**Change Summary:**
- Additions: 8 lines
- Deletions: 0 lines
- Total diff lines: 32

<details>
<summary>View Diff (first 50 lines)</summary>

```diff
--- original/src/scenes/menu_scene.py
+++ .compare/src/scenes/menu_scene.py
@@ -52,8 +52,13 @@
             motion_pattern=MotionPattern.RADIAL
         )

+<<<<<<< HEAD
+        # Start menu music
+        self.audio_manager.play_music('title')
+=======
         # Try to start menu music
         self.audio_manager.play_music('menu_music.ogg')
+>>>>>>> 9ebc79b77bf4f3eeeba98a93c9675350072c582b
         logger.debug("Menu scene created with particle effects")

     def handle_event(self, event):
@@ -61,12 +66,15 @@
             if event.key == pygame.K_UP:
                 self.previous_selection = self.selected_option
                 self.selected_option = (self.selected_option - 1) % len(self.options)
+                self.audio_manager.play_sound('menu-move')
                 self._on_selection_change()
             elif event.key == pygame.K_DOWN:
                 self.previous_selection = self.selected_option
                 self.selected_option = (self.selected_option + 1) % len(self.options)
+                self.audio_manager.play_sound('menu-move')
                 self._on_selection_change()
             elif event.key == pygame.K_RETURN:
+                self.audio_manager.play_sound('menu-select')
                 self._select_option()

     def _on_selection_change(self):
```

</details>

---

### 36. `src/scenes/pause_scene.py`

**Status:** ⚠️ DIFFERENCES FOUND

**Recommendation:** ⚠️ MERGE CONFLICTS DETECTED: The .compare file contains unresolved merge conflict markers (<<<<<<< HEAD, =======, >>>>>>>). This file needs manual conflict resolution before it can be merged. The differences shown represent both sides of the conflict.

**Change Summary:**
- Additions: 11 lines
- Deletions: 1 lines
- Total diff lines: 41

<details>
<summary>View Diff (first 50 lines)</summary>

```diff
--- original/src/scenes/pause_scene.py
+++ .compare/src/scenes/pause_scene.py
@@ -110,9 +110,14 @@
             logger.error("Failed to create blurred background: %s", e)

     def on_enter(self):
-        self.audio_manager.pause_music()
+        # Duck music to 50% volume instead of pausing
+        self.audio_manager.duck_music(0.5)

     def on_exit(self):
+<<<<<<< HEAD
+        # Restore music to normal volume
+        self.audio_manager.unduck_music()
+=======
         self.audio_manager.resume_music()
         # Clean up blur resources
         if self.blur_texture:
@@ -121,17 +126,22 @@
         if self.blur_fbo:
             self.blur_fbo.release()
             self.blur_fbo = None
+>>>>>>> 9ebc79b77bf4f3eeeba98a93c9675350072c582b

     def handle_event(self, event):
         if event.type == pygame.KEYDOWN:
             if event.key in (pygame.K_ESCAPE, pygame.K_p):
                 # Resume game
+                self.audio_manager.play_sound('pause')
                 self.scene_manager.pop_scene()
             elif event.key == pygame.K_UP:
+                self.audio_manager.play_sound('menu-move')
                 self.selected_option = (self.selected_option - 1) % len(self.options)
             elif event.key == pygame.K_DOWN:
+                self.audio_manager.play_sound('menu-move')
                 self.selected_option = (self.selected_option + 1) % len(self.options)
             elif event.key == pygame.K_RETURN:
+                self.audio_manager.play_sound('menu-select')
                 if self.selected_option == 0:  # Resume
                     self.scene_manager.pop_scene()
                 elif self.selected_option == 1:  # Quit to Menu
```

</details>

---

### 37. `src/utils/__init__.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 38. `src/utils/collision.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 39. `src/utils/constants.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 40. `src/utils/fps_counter.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 41. `src/utils/logging_config.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 42. `src/utils/screenshot.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

### 43. `src/utils/tweening.py`

**Status:** ✅ IDENTICAL

**Recommendation:** IDENTICAL: No differences found. No action needed.

---

## Merge Recommendations Summary

### ⚠️ Files with Unresolved Merge Conflicts (URGENT)

**Action Required:** These files contain merge conflict markers and must be manually resolved before any changes can be applied.

- `src/scenes/game_scene.py`
- `src/scenes/menu_scene.py`
- `src/scenes/pause_scene.py`

### Files That Can Likely Be Merged

- `src/game.py`

### Files Requiring Manual Review

- `shaders/dust_overlay.frag`
- `src/audio/audio_manager.py`
- `src/managers/asset_manager.py`

### Files Requiring No Action (Identical)

- `main.py`
- `shaders/background_plasma.frag`
- `shaders/background_retro.frag`
- `shaders/background_retrowave.frag`
- `shaders/background_starfield.frag`
- `shaders/background_waves.frag`
- `shaders/basic.frag`
- `shaders/basic.vert`
- `shaders/bloom_blur.frag`
- `shaders/bloom_combine.frag`
- `shaders/bloom_extract.frag`
- `shaders/crt.frag`
- `shaders/scanlines.frag`
- `shaders/text.frag`
- `shaders/text.vert`
- `shaders/vhs.frag`
- `src/__init__.py`
- `src/ai/__init__.py`
- `src/ai/pong_ai.py`
- `src/audio/__init__.py`
- `src/entities/__init__.py`
- `src/entities/ball.py`
- `src/entities/enhanced_particles.py`
- `src/entities/paddle.py`
- `src/entities/particle.py`
- `src/managers/scene_manager.py`
- `src/managers/shader_manager.py`
- `src/rendering/post_process.py`
- `src/rendering/renderer.py`
- `src/utils/__init__.py`
- `src/utils/collision.py`
- `src/utils/constants.py`
- `src/utils/fps_counter.py`
- `src/utils/logging_config.py`
- `src/utils/screenshot.py`
- `src/utils/tweening.py`

