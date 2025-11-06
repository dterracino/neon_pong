# Text Effects System

## Overview

The enhanced text rendering system now supports various visual effects applied through shaders, including stroke outlines, drop shadows, and gradient overlays. **Each text element can have its own unique combination of effects applied independently** - this allows for maximum creative flexibility on a single screen.

## Key Feature: Independent Per-Text Effects

**Important:** Each call to `draw_text()` can specify its own unique `TextEffects` configuration. The effects are applied per-text-element, not globally:

```python
# Title with ALL effects
title_fx = TextEffects(stroke_width=3.0, shadow_offset=(2,2), gradient_enabled=True, ...)
renderer.draw_text("NEON PONG", x, y, 72, color, effects=title_fx)

# Player text with ONLY stroke (different from title)
player_fx = TextEffects(stroke_width=1.5, stroke_color=(0,0,0,1))
renderer.draw_text("Player 1", x, y, 32, color, effects=player_fx)

# Score with NO effects (rendered on same frame)
renderer.draw_text("0", x, y, 64, color)
```

All three texts above render on the same frame with completely different effect configurations. The system renders each text individually with its own effect parameters.

## Text Effects

### Available Effects

#### 1. Stroke/Outline
Adds a colored outline around text for better readability and visual pop.

```python
from src.rendering.renderer import TextEffects

stroke_effect = TextEffects(
    stroke_width=2.5,  # Width in pixels
    stroke_color=(0.0, 0.0, 0.0, 1.0)  # RGBA (black outline)
)

renderer.draw_text("Outlined Text", x, y, size, COLOR_CYAN, effects=stroke_effect)
```

#### 2. Drop Shadow
Adds a soft shadow behind text for depth.

```python
shadow_effect = TextEffects(
    shadow_offset=(2.0, 2.0),  # X, Y offset in pixels
    shadow_blur=3.0,  # Blur amount
    shadow_color=(0.0, 0.0, 0.0, 0.8)  # RGBA (semi-transparent black)
)

renderer.draw_text("Shadow Text", x, y, size, COLOR_YELLOW, effects=shadow_effect)
```

#### 3. Gradient Overlay
Applies a vertical gradient to text.

```python
gradient_effect = TextEffects(
    gradient_enabled=True,
    gradient_color_top=COLOR_YELLOW,
    gradient_color_bottom=COLOR_PINK
)

renderer.draw_text("Gradient Text", x, y, size, (1.0, 1.0, 1.0, 1.0), effects=gradient_effect)
```

#### 4. Combined Effects
Multiple effects can be combined:

```python
combined_effect = TextEffects(
    stroke_width=2.0,
    stroke_color=(0.0, 0.0, 0.0, 1.0),
    shadow_offset=(2.5, 2.5),
    shadow_blur=4.0,
    shadow_color=(0.0, 0.0, 0.0, 0.7),
    gradient_enabled=True,
    gradient_color_top=COLOR_YELLOW,
    gradient_color_bottom=COLOR_PINK
)

renderer.draw_text("All Effects", x, y, size, (1.0, 1.0, 1.0, 1.0), effects=combined_effect)
```

## Bloom Control

Text can be rendered either before or after the bloom post-processing effect:

### After Bloom (Default) - Crisp Text
```python
# Renders to UI overlay (no bloom applied)
renderer.draw_text("Menu Text", x, y, size, COLOR_CYAN)
```

### Before Bloom - Glowing Text
```python
# Renders to scene (bloom applied)
renderer.draw_text("Score: 999", x, y, size, COLOR_PINK, render_before_bloom=True)
```

This allows you to have:
- **Crisp, readable UI text** (menus, instructions)
- **Glowing, stylized text** (scores, titles, special effects)

## Complete API

```python
def draw_text(
    text: str,                              # Text to render
    x: float,                               # Screen X position
    y: float,                               # Screen Y position  
    size: int,                              # Font size in pixels
    color: Tuple[float, float, float, float],  # RGBA (0-1)
    font_name: Optional[str] = None,        # Font file (None = default)
    centered: bool = False,                 # Center at X position
    effects: Optional[TextEffects] = None,  # Visual effects
    render_before_bloom: bool = False       # Apply bloom effect
)
```

## Performance

### Effect Performance Impact

| Effect Type | Performance | Notes |
|------------|-------------|-------|
| None (basic) | ~0.1-0.5ms | Cached, very fast |
| Stroke | ~0.5-1.0ms | GPU shader, minimal impact |
| Shadow | ~0.8-1.5ms | Requires multiple samples |
| Gradient | ~0.4-0.8ms | GPU shader, minimal impact |
| Combined | ~1.0-2.0ms | All effects together |

### Optimization Tips

1. **Cache Benefits**: Static text with same effects is cached
2. **Batch Similar Effects**: Group text with same effects together
3. **Use Bloom Sparingly**: Only for special effects, not UI text
4. **Limit Shadow Blur**: Higher blur = more samples = slower

## Shader Implementation

Effects are implemented in `shaders/text_effects.frag`:

- **Stroke**: SDF-based edge detection
- **Shadow**: Multi-sample box blur
- **Gradient**: UV-based interpolation
- **All GPU-accelerated**: No CPU overhead

## Examples

### Title Screen
```python
# Large title with stroke
title_effects = TextEffects(
    stroke_width=3.0,
    stroke_color=(0.0, 0.0, 0.0, 1.0)
)
renderer.draw_text("NEON PONG", WINDOW_WIDTH // 2, 150, 72, 
                   COLOR_PINK, centered=True, effects=title_effects)

# Menu options (no effects for clarity)
for i, option in enumerate(["Start Game", "Options", "Quit"]):
    y = 350 + i * 80
    renderer.draw_text(option, WINDOW_WIDTH // 2, y, 48, 
                       COLOR_CYAN, centered=True)
```

### Gameplay
```python
# Scores with bloom glow
renderer.draw_text(str(score1), WINDOW_WIDTH // 4, 50, 64,
                   COLOR_CYAN, centered=True, render_before_bloom=True)

renderer.draw_text(str(score2), WINDOW_WIDTH * 3 // 4, 50, 64,
                   COLOR_PINK, centered=True, render_before_bloom=True)
```

### Pause Screen
```python
# "PAUSED" with gradient
gradient = TextEffects(
    gradient_enabled=True,
    gradient_color_top=COLOR_YELLOW,
    gradient_color_bottom=COLOR_PINK
)
renderer.draw_text("PAUSED", WINDOW_WIDTH // 2, 200, 72,
                   (1.0, 1.0, 1.0, 1.0), centered=True, effects=gradient)
```

## Testing

### Visual Demo
```bash
python tests/test_text_effects_demo.py
```
Shows all effects side-by-side in a window.

### Performance Benchmark
```bash
python tests/test_text_performance.py
```
Benchmarks various scenarios:
- Title screen (static text)
- Gameplay (dynamic scores)
- Pause screen
- Complex scenes with many effects
- Cache state comparisons

## Technical Details

### Single-Call Batched Rendering with Per-Vertex Effects

The system uses **vertex attributes** to pass effect parameters, enabling true batched rendering with a single draw call:

1. **Extended Vertex Format**: Each vertex contains position, UV, and all effect parameters (29 floats total)
2. **Single Atlas**: All text surfaces packed into one texture
3. **Single VBO Write**: All vertices with effect data written at once
4. **Single Render Call**: One draw call renders all text with independent effects

**Vertex Layout:**
```
Position (2) + UV (2) + Color (4) + 
StrokeWidth (1) + StrokeColor (4) + 
ShadowOffset (2) + ShadowBlur (1) + ShadowColor (4) + 
GradientEnabled (1) + GradientTop (4) + GradientBottom (4) = 29 floats
```

**Implementation:**
```python
# Build ALL vertices with effect data
for call in batch:
    effects = call.effects or TextEffects()
    effect_data = [
        *call.color, effects.stroke_width, *effects.stroke_color,
        *effects.shadow_offset, effects.shadow_blur, *effects.shadow_color,
        1.0 if effects.gradient_enabled else 0.0,
        *effects.gradient_color_top, *effects.gradient_color_bottom
    ]
    
    # Create 6 vertices (2 triangles) with position, UV, and effect data
    vertices.extend([
        pos_x, pos_y, uv_x, uv_y, *effect_data,  # Vertex 1
        pos_x, pos_y, uv_x, uv_y, *effect_data,  # Vertex 2
        # ... (6 vertices total per text quad)
    ])

# Single VBO write
vbo.write(all_vertices)

# Single render call for ALL text
vao.render(TRIANGLES, vertices=total_vertex_count)
```

**Shader Processing:**
The vertex shader receives effect parameters as attributes and passes them to the fragment shader where they're applied per-fragment. Since all 6 vertices of a quad have identical effect data, the interpolated values in the fragment shader are consistent across the quad.

### Coordinate Systems

The system properly handles pygame vs OpenGL coordinate systems:
- **Pygame**: Origin at top-left, Y increases downward
- **OpenGL**: Origin at bottom-left, Y increases upward
- **UV Mapping**: Automatically flipped for correct text orientation

### Texture Atlas

Text is rendered to a texture atlas per frame:
1. Render text surfaces with pygame (cached)
2. Pack into single texture atlas
3. Generate vertex data with UV coordinates
4. Upload to GPU and render in one draw call

### Shader Pipeline

Two shader programs:
- **text.vert/frag**: Basic text rendering (no effects)
- **text_effects.vert/frag**: Text with effects

The system automatically selects the appropriate shader based on whether effects are enabled.

## Troubleshooting

### Text appears upside down
The UV coordinates are automatically flipped to handle pygame vs OpenGL differences. If text still appears inverted, check that you're using the correct shader.

### Effects not working
Ensure you're passing a `TextEffects` instance:
```python
# Wrong
renderer.draw_text("Text", x, y, size, color, stroke_width=2.0)

# Correct
effects = TextEffects(stroke_width=2.0)
renderer.draw_text("Text", x, y, size, color, effects=effects)
```

### Performance issues
1. Check cache statistics: `renderer.get_text_cache_stats()`
2. Reduce shadow blur amount
3. Batch text with same effects
4. Avoid effects on frequently changing text

## Future Enhancements

Potential additions (not currently implemented):
- SDF (Signed Distance Field) fonts for better scaling
- Additional effect types (glow, chromatic aberration)
- Per-character effects and animations
- Text outline with separate colors
- Multiple shadow layers
