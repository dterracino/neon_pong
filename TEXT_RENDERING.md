# Text Rendering System

## Overview

The text rendering system has been updated to use actual text instead of placeholder rectangles. The implementation uses:

1. **Pygame fonts** - For rendering text to surfaces
2. **OpenGL textures** - Text surfaces are converted to GPU textures
3. **UI overlay layer** - Text is rendered to a separate framebuffer after bloom
4. **Texture caching** - Text textures are cached for performance

## Architecture

### Rendering Pipeline

```
Scene Rendering (begin_frame)
    ↓
Draw game objects (paddles, ball, etc.) → Scene Framebuffer
    ↓
Draw text → UI Framebuffer (separate, transparent)
    ↓
Apply bloom to Scene Framebuffer
    ↓
Composite to screen (end_frame):
    1. Draw bloomed scene
    2. Draw UI overlay on top (with alpha blending)
```

### Key Components

#### 1. Renderer.draw_text()

Location: `src/rendering/renderer.py`

```python
def draw_text(self, text: str, x: float, y: float, size: int, 
              color: Tuple[float, float, float, float], 
              font_name: Optional[str] = None, centered: bool = False)
```

**Features:**
- Renders text using pygame fonts
- Converts to OpenGL texture
- Caches textures for reuse
- Supports centering
- Draws to UI layer (after bloom)

**Parameters:**
- `text`: String to render
- `x, y`: Position in screen coordinates
- `size`: Font size (use constants from `constants.py`)
- `color`: RGBA tuple (0-1 range)
- `font_name`: Optional font file in `assets/fonts/`
- `centered`: If True, centers text at x position

#### 2. Font Size Constants

Location: `src/utils/constants.py`

```python
FONT_SIZE_LARGE = 72   # For titles and big messages
FONT_SIZE_MEDIUM = 48  # For menu options
FONT_SIZE_DEFAULT = 32 # Default text size
FONT_SIZE_SMALL = 24   # For small text like controls
```

#### 3. AssetManager

Location: `src/managers/asset_manager.py`

The AssetManager provides font loading and caching:

```python
def get_font(self, name: Optional[str] = None, size: int = 32) -> pygame.font.Font
```

## Usage Examples

### Basic Text

```python
# Draw simple text
renderer.draw_text("Hello World", 100, 200, FONT_SIZE_DEFAULT, COLOR_CYAN)
```

### Centered Text

```python
# Draw centered title
renderer.draw_text(
    "NEON PONG", 
    WINDOW_WIDTH // 2, 
    150, 
    FONT_SIZE_LARGE, 
    COLOR_PINK, 
    centered=True
)
```

### Using Custom Fonts

```python
# Place font file in assets/fonts/ and reference by name
renderer.draw_text(
    "Custom Font Text", 
    400, 300, 
    48, 
    COLOR_YELLOW, 
    font_name="myfont.ttf"
)
```

## Scene Integration

### MenuScene

- Title: Large pink text, centered
- Menu options: Medium text, centered, color changes on selection
- Controls: Small text, left-aligned

### GameScene

- Scores: Large text, centered per player side
- Game over message: Large text, centered
- Instructions: Default size text, centered

### PauseScene

- Pause title: Large yellow text, centered
- Instructions: Default size yellow text, centered

## Performance Considerations

### Texture Caching

Text textures are cached using a key of:
```python
(text, size, pygame_color, font_name)
```

This means:
- Same text with same parameters = reuses texture
- Different text = creates new texture
- Dynamic text (scores) creates new textures as numbers change

### Best Practices

1. **Use constants**: Always use `FONT_SIZE_*` constants for consistency
2. **Limit unique text**: Too many unique text strings can consume GPU memory
3. **Static text is free**: After first render, cached textures are very fast
4. **Dynamic text**: Acceptable for scores and messages that change infrequently

## Adding Custom Fonts

1. Download a font file (`.ttf` or `.otf`)
2. Place in `assets/fonts/` directory
3. Reference by filename:
   ```python
   renderer.draw_text("Text", 100, 100, 32, COLOR_CYAN, font_name="myfont.ttf")
   ```

## Troubleshooting

### Text not appearing

1. Check that `begin_frame()` and `end_frame()` are called
2. Verify coordinates are within screen bounds (0-1280, 0-720)
3. Check color alpha channel (should be > 0)

### Text looks blurry

- Text uses LINEAR filtering for smooth rendering
- Small font sizes may appear less crisp
- Use larger font sizes for better clarity

### Performance issues

- Check texture cache size: `len(renderer.text_texture_cache)`
- Clear cache if needed (would need to add method)
- Reduce number of unique text strings

## Future Enhancements

Possible improvements:
- SDF (Signed Distance Field) fonts for better scaling
- Text layout system (word wrapping, alignment)
- Text effects (shadows, outlines, gradients)
- Bitmap fonts for retro aesthetic
- Font atlas for even better performance
