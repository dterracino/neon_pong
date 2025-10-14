# Font Usage Guide

## Using Fonts in Neon Pong

### Default Font

The default pygame font is used when no font name is specified:

```python
renderer.draw_text("Hello World", 100, 100, 48, COLOR_PINK)
```

### Named Fonts

To use a custom font, place the font file (`.ttf`, `.otf`, or `.fon`) in the `assets/fonts/` directory, then reference it by filename:

```python
# Place your font file in assets/fonts/myfont.ttf
renderer.draw_text("Hello World", 100, 100, 48, COLOR_PINK, font_name="myfont.ttf")
```

### Font Preloading

For better performance, preload fonts during initialization:

```python
from src.managers.asset_manager import AssetManager

# Preload all fonts in the fonts directory at common sizes
asset_manager = AssetManager()
asset_manager.preload_fonts_from_directory(sizes=[24, 32, 48, 64, 72])
```

Or preload specific fonts:

```python
# Preload specific font at specific sizes
for size in [24, 48, 72]:
    asset_manager.get_font("myfont.ttf", size)
```

## Font Caching

Fonts are automatically cached by the AssetManager. Once a font is loaded at a specific size, it will be reused for subsequent requests.

Cache key: `(font_name, size)`

## Examples

### Menu Title with Large Font

```python
renderer.draw_text(
    "NEON PONG",
    WINDOW_WIDTH // 2,
    100,
    72,
    COLOR_PINK,
    font_name="title_font.ttf",  # Optional custom font
    centered=True
)
```

### Score Display

```python
renderer.draw_text(
    str(player_score),
    WINDOW_WIDTH // 4,
    50,
    64,
    COLOR_CYAN,
    centered=True
)
```

### Menu Options

```python
renderer.draw_text(
    "Start Game",
    WINDOW_WIDTH // 2,
    300,
    48,
    COLOR_YELLOW,
    centered=True
)
```

## Notes

- Font files should be placed in `assets/fonts/`
- Supported formats: `.ttf`, `.otf`, `.fon`
- Font sizes are in pixels
- Use the constants from `src.utils.constants` for consistent sizing:
  - `FONT_SIZE_LARGE = 72` (titles)
  - `FONT_SIZE_MEDIUM = 48` (menu options)
  - `FONT_SIZE_DEFAULT = 32` (default text)
  - `FONT_SIZE_SMALL = 24` (small text)
