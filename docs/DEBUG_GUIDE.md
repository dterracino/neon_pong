# Debug Guide for Neon Pong

## Overview

This game now includes comprehensive debug logging to help diagnose issues when the game displays a black screen or doesn't work as expected.

## Debug Output

When you run the game with `python main.py`, you will see detailed debug output in the console showing:

1. **Game Initialization** - What components are being initialized and in what order
2. **Shader Loading** - Whether shaders are loading successfully and from where
3. **Renderer Setup** - If the renderer and post-processor are configured properly
4. **Scene Management** - Which scenes are active and when transitions occur
5. **Game Loop** - Frame-by-frame updates for the first few frames

## Common Issues and Solutions

### Issue: Black Screen on Startup

**Debug Output to Check:**

```plaintext
[DEBUG] Game.run: Starting main game loop...
[DEBUG] Game.run: Frame 0, dt=0.0167
[DEBUG] Game.run: Rendering scene: MenuScene
```

If you see these messages, the game loop is running. Check for:

**Shader Loading Errors:**

```plaintext
[ERROR] ShaderManager.load_shader: Shader file not found: ...
[ERROR] Renderer.__init__: Failed to load basic shader!
```

**Solution:** Ensure the `shaders/` directory exists with all required shader files:

- `basic.vert`
- `basic.frag`
- `bloom_extract.frag`
- `bloom_blur.frag`
- `bloom_combine.frag`

**Rendering Errors:**

```plaintext
[ERROR] Renderer.draw_rect: Cannot draw - basic_program not loaded!
[ERROR] Renderer.end_frame: Cannot render - basic_program not loaded or 'tex' uniform missing!
```

**Solution:** This indicates shader loading failed. Check shader files for syntax errors.

### Issue: Game Doesn't Start

**Debug Output to Check:**
Look for where initialization stops. For example:

```plaintext
[DEBUG] Game.__init__: Creating window (1280x720)...
Error running game: ...
```

This indicates an issue creating the OpenGL window. Common causes:

- Graphics drivers not installed
- OpenGL 3.3 not supported
- Display not available

### Issue: Audio Warnings

```plaintext
[WARNING] Game.__init__: Failed to initialize pygame.mixer: ...
[WARNING] Game.__init__: Continuing without audio...
```

This is normal if audio devices aren't available. The game will continue without sound.

### Issue: Scene Not Rendering

If you see the game loop running but no scene updates:

```plaintext
[DEBUG] Game.run: Frame 0, dt=0.0167
[DEBUG] Game.run: Frame 0 complete
```

But no "Updating scene" or "Rendering scene" messages, check:

```plaintext
[DEBUG] SceneManager.push_scene: Scene stack size: 0
```

If scene stack is 0, no scenes are active. Check scene initialization.

## Debug Levels

- `[DEBUG]` - Normal operation information
- `[WARNING]` - Non-critical issues (game continues)
- `[ERROR]` - Critical issues that prevent rendering or operation

## Testing Debug Output

Run the included test script to see a simulation of the debug output:

```bash
python tests/test_debug_output.py
```

This shows what normal debug output looks like without actually running the game (useful for systems without OpenGL).

## Disabling Debug Output

To reduce console output, you can comment out or remove the `print()` statements with `[DEBUG]` prefix in:

- `src/game.py`
- `src/managers/shader_manager.py`
- `src/managers/scene_manager.py`
- `src/rendering/renderer.py`
- `src/rendering/post_process.py`
- `src/scenes/menu_scene.py`
- `src/scenes/game_scene.py`

## Understanding Game Flow

Normal startup sequence:

1. Initialize pygame
2. Create window with OpenGL context
3. Initialize managers (asset, shader, audio)
4. Initialize renderer (loads shaders)
5. Create scene manager
6. Push initial menu scene
7. Start game loop
8. Each frame: handle events → update scene → render scene → swap buffers

## Getting Help

When reporting issues, include:

1. Full debug output from game startup
2. Your operating system and graphics card
3. Output from `python --version` and `pip list | grep -E "pygame|moderngl"`

The debug output will help identify exactly where the problem occurs in the initialization or rendering pipeline.
