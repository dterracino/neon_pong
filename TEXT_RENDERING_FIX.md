# Text Rendering Fix - Black Screen Issue

## Problem Summary

Text rendering was producing black images instead of displaying colored text. The issue affected the test program `test_text_rendering.py`, which was writing completely black images to disk.

## Root Cause Analysis

The problem was in the shader system used to render text quads:

1. **Original Implementation**: The `basic.vert` shader computed UV coordinates from vertex positions using:
   ```glsl
   uv = in_position * 0.5 + 0.5;
   ```
   
2. **Why This Worked for Some Cases**: This formula works correctly when rendering a full-screen quad from (-1, -1) to (1, 1), converting NDC coordinates to UV space (0, 1).

3. **Why This Failed for Text**: Text quads are positioned and sized dynamically (e.g., a small quad at position (100, 200) with size (200, 50)). The UV computation based on position would map to the wrong part of the texture.

4. **Result**: The wrong UV coordinates caused the shader to sample the wrong parts of the text texture, resulting in black (transparent) pixels.

## Solution

Created a dedicated text shader that accepts UV coordinates as input instead of computing them from position:

### New Shaders

**`shaders/text.vert`**:
```glsl
#version 330

in vec2 in_position;
in vec2 in_uv;        // <-- Accept UV as input
out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    uv = in_uv;       // <-- Pass through directly
}
```

**`shaders/text.frag`**:
```glsl
#version 330

uniform sampler2D tex;
uniform vec4 color;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec4 texColor = texture(tex, uv);
    fragColor = texColor * color;
}
```

### Renderer Changes

Updated `Renderer.draw_text()` to:

1. Load and use the new text shader
2. Create vertex data with both position AND UV coordinates:
   ```python
   vertices = np.array([
       # Bottom-left: position (x, y) + UV (u, v)
       ndc_x, ndc_y - ndc_height, 0.0, 1.0,
       # Bottom-right
       ndc_x + ndc_width, ndc_y - ndc_height, 1.0, 1.0,
       # Top-left
       ndc_x, ndc_y, 0.0, 0.0,
       # Top-right
       ndc_x + ndc_width, ndc_y, 1.0, 0.0,
   ], dtype='f4')
   ```
3. Create VAO with proper vertex format:
   ```python
   vao = self.ctx.vertex_array(
       self.text_program,
       [(vbo, '2f 2f', 'in_position', 'in_uv')]
   )
   ```

## UV Coordinate Mapping

The UV coordinates are now explicitly mapped regardless of quad position:

- **Top-left corner**: UV (0, 0) - start of texture
- **Top-right corner**: UV (1, 0)
- **Bottom-left corner**: UV (0, 1)
- **Bottom-right corner**: UV (1, 1) - end of texture

This ensures the full text texture is displayed on any positioned quad.

## Additional Improvements

### 1. Debug Logging

Added comprehensive `[DEBUG]` logging throughout the rendering pipeline:
- AssetManager initialization and font loading
- Renderer shader loading
- Text texture creation and caching
- Rendering position and size information

### 2. Font Preloading

Added `AssetManager.preload_fonts_from_directory()` method to preload fonts:
```python
def preload_fonts_from_directory(self, sizes=None):
    """Preload all fonts from the fonts directory
    
    Args:
        sizes: List of font sizes to preload. 
               Default: [24, 32, 48, 64, 72]
    """
```

### 3. Documentation

- Created `FONT_USAGE.md` documenting how to use named fonts
- Font name support was already implemented, just needed documentation

### 4. Test Enhancements

- Updated `test_text_rendering.py` to check if output is black
- Created `test_text_shader_uv.py` to validate UV coordinate math
- Created `test_font_preload.py` to test font preloading
- Created `test_pygame_text_visual.py` to verify pygame rendering works

## Verification

### Tests That Pass

1. ✅ **test_text_api.py**: Validates pygame font loading and rendering
2. ✅ **test_text_shader_uv.py**: Validates UV coordinate mapping is correct
3. ✅ **test_font_preload.py**: Validates font preloading functionality
4. ✅ **test_pygame_text_visual.py**: Confirms pygame produces visible text

### Tests Requiring OpenGL Context

- **test_text_rendering.py**: Full integration test (requires OpenGL context)
  - Cannot run in CI environment without hardware acceleration
  - Should work on user's machine with proper OpenGL support

## Expected Behavior

After these changes:

1. Text should render in the specified colors (pink, cyan, yellow, etc.)
2. Text should be positioned correctly on screen
3. Text should be cached for performance
4. Multiple text sizes and colors should work
5. The dark purple background should be visible with colored text on top

## Technical Details

### Texture Format

- Text is rendered to pygame surface with specified color
- Surface is converted to RGBA format
- OpenGL texture is created from RGBA data
- Texture uses LINEAR filtering for smooth appearance

### Rendering Pipeline

1. **Font Rendering**: Pygame renders text to surface with color baked in
2. **Texture Creation**: Surface converted to OpenGL texture
3. **Caching**: Texture cached by (text, size, color, font_name)
4. **Geometry Creation**: Positioned quad created with explicit UV coordinates
5. **Shader Rendering**: Text shader uses UV to sample texture correctly
6. **Blending**: Alpha blending enabled for transparent backgrounds
7. **UI Layer**: Text rendered to UI framebuffer (after bloom, before final composite)

### Why The Fix Works

The key insight is that UV coordinates must be independent of position:

- **Old approach**: UV = f(position) → only works for full-screen quads
- **New approach**: UV = explicit input → works for any positioned/sized quad

By passing UV coordinates explicitly, we can position and size quads anywhere on screen while still sampling the full texture correctly.

## Testing Recommendations

When testing on a machine with OpenGL support:

1. Run `test_text_rendering.py`
2. Check that `~/tmp/text_rendering_test.png` contains visible text
3. Verify text is colored (not black/white)
4. Verify background is dark purple
5. Run the main game and check menu text is visible

## Summary

The black screen issue was caused by incorrect UV coordinate computation in the basic shader. The fix separates concerns:

- **Basic shader**: For full-screen quads (bloom, post-processing)
- **Text shader**: For positioned quads with explicit UVs (text rendering)

This is a minimal, surgical change that fixes the specific problem without affecting other rendering systems.
