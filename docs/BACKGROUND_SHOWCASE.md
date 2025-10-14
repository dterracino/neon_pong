# Background Shader Showcase

## Overview

Neon Pong now features **shader-drawn animated backgrounds** that add visual flair without distracting from gameplay!

## Quick Start

To change the background, edit `src/utils/constants.py`:

```python
BACKGROUND_TYPE = "starfield"  # Change this!
```

Available options:
- `"starfield"` ⭐ - Beautiful parallax starfield (default)
- `"plasma"` 🌊 - Smooth flowing plasma effect
- `"waves"` 〰️ - Animated wave patterns with retro grid
- `"solid"` ⬛ - Simple solid color (best performance)

## Background Descriptions

### Starfield ⭐ (Recommended)
A mesmerizing parallax starfield with three layers of stars moving at different speeds. Features twinkling stars in neon colors (cyan, pink, purple) and subtle nebula clouds. Perfect for that space-age neon aesthetic.

**Vibe**: Cosmic, dreamy, classic
**Performance**: Excellent

### Plasma 🌊
A hypnotic flowing plasma effect created with multiple sine waves. Colors smoothly transition through the neon palette (purple → pink → cyan). Brightness is reduced to 30% to keep it non-intrusive.

**Vibe**: Psychedelic, smooth, organic
**Performance**: Excellent

### Waves 〰️
Animated horizontal and vertical wave patterns with a retro grid overlay. Cyan waves represent positive peaks, pink represents negative. Great for that synthwave/retrowave aesthetic.

**Vibe**: Retro, rhythmic, 80s
**Performance**: Excellent

### Solid ⬛
A simple dark purple background. Use this if you want minimal distraction or need maximum performance (though all shader backgrounds are highly optimized).

**Vibe**: Classic, clean, focused
**Performance**: Maximum

## Technical Details

All backgrounds:
- ✅ Run entirely on GPU (no CPU overhead)
- ✅ Render at 60 FPS on modest hardware
- ✅ Use authentic shader programming (GLSL)
- ✅ Animate smoothly in real-time
- ✅ Match the neon/vaporwave color palette
- ✅ Are non-intrusive (won't distract from gameplay)

## Examples

### Before (Solid Background)
```python
BACKGROUND_TYPE = "solid"
```
A simple dark purple background. Functional but static.

### After (Starfield)
```python
BACKGROUND_TYPE = "starfield"
```
Animated stars flowing by with parallax depth! Much more engaging.

### Alternative (Plasma)
```python
BACKGROUND_TYPE = "plasma"
```
Smooth flowing colors creating an organic, mesmerizing effect.

### Retro Option (Waves)
```python
BACKGROUND_TYPE = "waves"
```
Wave patterns with grid lines for that classic synthwave look.

## See Also

- **BACKGROUND_SHADERS.md** - Full technical documentation
- **test_background_shaders.py** - Validation tests
- **test_background_integration.py** - Integration tests

## Credits

Shader effects implemented using:
- ModernGL for modern OpenGL rendering
- GLSL (OpenGL Shading Language) for GPU programming
- Mathematical functions (sine waves, noise, hashing) for procedural generation
