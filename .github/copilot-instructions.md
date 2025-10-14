# AI Coding Agent Instructions for Neon Pong

## Architecture Overview

This is a modern Pong game built with **pygame + ModernGL** featuring a **multi-stage graphics pipeline**:

1. **Scene Rendering** → Game objects to framebuffer
2. **Bloom Post-Processing** → Extract bright pixels, blur, combine  
3. **Background Shaders** → GPU-animated backgrounds (starfield/plasma/waves)
4. **Text Rendering** → Custom shader-based text with UV mapping

**Key Architectural Pattern**: Singleton managers (`AssetManager`, `ShaderManager`, `AudioManager`) with dependency injection through constructors.

## Critical File Relationships

- `main.py` → `src/game.py` → Core game loop + manager initialization
- `src/game.py` orchestrates: Renderer → SceneManager → AudioManager
- `src/rendering/renderer.py` + `post_process.py` = Complete graphics pipeline
- `src/managers/shader_manager.py` = GLSL shader compilation & caching
- `shaders/*.{vert,frag}` = All rendering effects (basic, text, bloom, backgrounds)

## Debug-First Development

**Always check console output first** - extensive debug logging shows:
- Shader compilation success/failure with file paths
- Manager initialization order and dependencies  
- Scene transitions and rendering calls
- Frame-by-frame updates for first 5 frames

Run `python tests/test_debug_output.py` to see expected debug patterns.

## Shader System Patterns

**Loading Convention**: `shader_manager.load_shader(name, vertex_file, fragment_file)`
- Cached by name - subsequent calls return existing program
- Always check return value: `None` indicates compilation failure
- Shaders stored in `shaders/` directory with `.vert`/`.frag` extensions

**Background Shaders**: Configure via `BACKGROUND_TYPE` in `constants.py`
- `"starfield"` (default) - Parallax star layers with twinkling
- `"plasma"` - Flowing neon colors  
- `"waves"` - Animated wave patterns with retro grid

## Scene System

**Pattern**: `SceneManager` uses stack-based scene management
- `push_scene()` - Add new scene (calls `on_enter()`)
- `change_scene()` - Replace current scene
- `pop_scene()` - Return to previous scene
- Each scene: `update(dt)`, `render()`, `handle_event(event)`

**Scene Files**: `src/scenes/{menu,game,pause}_scene.py`

## Testing & Validation

**Visual Tests**: `tests/test_*_visual.py` files create minimal test windows
**Integration Tests**: `tests/test_*_integration.py` validate component interactions
**Debug Tests**: `tests/test_debug_output.py` simulates normal execution flow

**Test Pattern**: Create minimal pygame + ModernGL context, test specific components

## Color Scheme & Constants

All colors defined in `src/utils/constants.py` as normalized RGBA tuples:
- `COLOR_PINK = (1.0, 0.44, 0.81, 1.0)` - Primary UI color
- `COLOR_CYAN = (0.0, 0.8, 0.996, 1.0)` - Player 1  
- `COLOR_PURPLE = (0.725, 0.4, 1.0, 1.0)` - Player 2

**Font Sizes**: `FONT_SIZE_{LARGE|MEDIUM|DEFAULT|SMALL}` for consistent text scaling

## Common Debugging Commands

```bash
python main.py                        # Full game with debug output
python tests/test_debug_output.py     # Simulate normal debug flow
python tests/test_background_shaders.py # Test shader loading only
```

**FPS Display**: Press `F3` in-game to toggle performance metrics overlay

## ModernGL Integration Points

**Framebuffer Pipeline**: Scene → Bloom Extract → Blur Passes → Combine → Screen
**VAO Management**: Renderer creates and manages vertex array objects for quads
**Texture Handling**: Post-processor manages multiple framebuffers for bloom effect
**Shader Uniforms**: Time-based uniforms for animated backgrounds, color uniforms for entities

## Development Workflow

1. **Shader Changes**: Restart game - no hot reloading
2. **Code Changes**: Standard Python reload patterns
3. **New Features**: Add debug prints following existing `[DEBUG] ClassName.method: message` pattern
4. **Asset Changes**: Assets loaded through `AssetManager` singleton

When modifying graphics code, always test with multiple background types to ensure compatibility across the shader pipeline.