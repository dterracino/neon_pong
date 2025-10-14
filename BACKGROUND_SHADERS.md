# Background Shaders System

## Overview

The neon pong game now features impressive shader-drawn animated backgrounds that add visual interest without detracting from the gameplay. The backgrounds are rendered efficiently using GPU fragment shaders.

## Available Backgrounds

### 1. Starfield (Default)
A beautiful parallax starfield with multiple layers of stars moving at different speeds, creating depth. Features:
- Three layers of stars with different sizes and speeds
- Distant slow-moving stars (small, dim)
- Mid-distance medium stars
- Close fast-moving bright stars with twinkling effect
- Stars colored in cyan, pink, and purple tints (matching the neon theme)
- Subtle nebula-like clouds for atmosphere
- Smooth gradient background

**Performance**: Very efficient, suitable for all hardware

### 2. Plasma
A smooth, flowing plasma effect with neon colors. Features:
- Multiple sine waves creating organic movement
- Color transitions through the neon palette (purple → pink → cyan)
- Reduced brightness (30%) to avoid distraction
- Depth variation for visual interest
- Hypnotic but non-intrusive animation

**Performance**: Very efficient, suitable for all hardware

### 3. Waves
Animated wave patterns with a retro grid aesthetic. Features:
- Horizontal and vertical wave animations
- Cyan waves for positive peaks, pink for negative
- Subtle grid overlay for retro feel
- Smooth, rhythmic movement
- Less busy than plasma, more dynamic than solid

**Performance**: Very efficient, suitable for all hardware

### 4. Solid (Fallback)
A simple solid dark purple background, used when:
- Background shaders are disabled
- Shader compilation fails
- Maximum performance is needed

## Configuration

Edit `src/utils/constants.py`:

```python
# Background settings
BACKGROUND_TYPE = "starfield"  # Options: "starfield", "plasma", "waves", "solid"
```

Change `BACKGROUND_TYPE` to one of:
- `"starfield"` - Parallax starfield (default, recommended)
- `"plasma"` - Smooth plasma effect
- `"waves"` - Animated wave patterns with grid
- `"solid"` - Solid color background

## Technical Details

### Architecture

The background rendering is integrated into the main rendering pipeline:

```
begin_frame() → Render animated background → Clear scene → Render game objects → Apply bloom → Composite to screen
```

### Shader Files

- `shaders/background_starfield.frag` - Starfield fragment shader
- `shaders/background_plasma.frag` - Plasma fragment shader
- `shaders/background_waves.frag` - Wave pattern fragment shader
- All use `shaders/basic.vert` as the vertex shader

### Uniforms

Both background shaders accept:
- `float time` - Elapsed time for animation
- `vec2 resolution` - Screen resolution (1280x720)

### Rendering Process

1. **Initialization** (in `Renderer.__init__`):
   - Load background shader based on `BACKGROUND_TYPE`
   - Create VAO for fullscreen quad
   - Initialize time tracking

2. **Per-Frame Update** (in `Game.run`):
   - `renderer.update_time(dt)` updates animation time

3. **Rendering** (in `Renderer.begin_frame`):
   - Bind scene framebuffer
   - If background enabled: render fullscreen quad with background shader
   - If background disabled: clear with solid color
   - Continue with normal game rendering

### Performance

- Backgrounds render once per frame as a fullscreen quad
- Fragment shader runs on GPU in parallel
- No CPU overhead beyond setting uniforms
- Both shaders are optimized for smooth 60 FPS on modest hardware

## Design Principles

The backgrounds follow these principles:

1. **Non-Intrusive**: Colors are darkened and muted to avoid distracting from gameplay
2. **Theme-Appropriate**: Use the neon/vaporwave color palette (pink, cyan, purple)
3. **Smooth Animation**: Slow, fluid movements that enhance rather than distract
4. **Performance**: Efficient GPU rendering with minimal overhead
5. **Configurable**: Easy to switch between effects or disable

## Testing

Two test scripts validate the background system:

### test_background_shaders.py
Tests shader file validity:
- Shader files exist and have correct syntax
- Required uniforms are present
- Constants are properly configured

### test_background_integration.py
Tests integration with the renderer:
- Renderer imports successfully with new code
- Background logic is present
- Game loop calls update_time()

Run tests:
```bash
python3 test_background_shaders.py
python3 test_background_integration.py
```

## Extending

To add a new background effect:

1. **Create shader**: Add `shaders/background_yourname.frag`
   - Must have uniforms: `float time`, `vec2 resolution`
   - Input: `vec2 uv` (0-1 range)
   - Output: `vec4 fragColor`

2. **Update constants**: Add option to `BACKGROUND_TYPE` in `constants.py`

3. **Update renderer**: Add loading logic in `Renderer.__init__`:
   ```python
   elif BACKGROUND_TYPE == "yourname":
       self.background_program = shader_manager.load_shader(
           'background_yourname', 'basic.vert', 'background_yourname.frag'
       )
   ```

## Troubleshooting

### Background not showing
- Check that `BACKGROUND_TYPE` is set correctly
- Verify shader files exist in `shaders/` directory
- Check console for shader compilation errors

### Performance issues
- Switch to `"solid"` background type
- Check GPU drivers are up to date

### Colors too bright/distracting
- Edit the shader file and reduce color multiplier
- For starfield: reduce star brightness values
- For plasma: reduce the `color *= 0.3` multiplier further
