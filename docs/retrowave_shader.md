# Retrowave Background Shader

## Overview
A new background shader type that creates a classic retrowave/synthwave aesthetic for Neon Pong.

## Visual Features
- **Large Gradient Sun**: Yellow to orange to pink gradient sun with horizontal stripes cutting through it
- **Wireframe Mountains**: Three layers of cyan wireframe mountains with depth parallax
- **Perspective Grid Floor**: Magenta/pink grid lines with proper perspective that animate towards the viewer
- **Starfield**: Scattered white stars in the upper sky
- **Gradient Sky**: Purple to dark purple gradient for that classic retrowave look
- **CRT Scan Lines**: Subtle horizontal lines for authentic retro CRT monitor effect
- **Vignette**: Soft darkening at the edges for depth

## Usage

To enable the retrowave background, edit `src/utils/constants.py`:

```python
BACKGROUND_TYPE = "retrowave"  # Options: "starfield", "plasma", "waves", "retrowave", "solid"
```

Then run the game:
```bash
python main.py
```

## Technical Details

### Files Modified
- `shaders/background_retrowave.frag` - GLSL fragment shader with full retrowave scene
- `src/rendering/renderer.py` - Added retrowave background loading
- `src/utils/constants.py` - Documented retrowave as valid option
- `tests/test_background_shaders.py` - Added retrowave shader tests

### Shader Uniforms
- `uniform float time` - Animation time in seconds
- `uniform vec2 resolution` - Screen resolution for aspect ratio and scan lines

### Color Palette
- Sky Top: Dark purple `(0.05, 0.02, 0.15)`
- Sky Horizon: Purple `(0.4, 0.15, 0.5)`
- Sun Gradient: Yellow to Orange to Pink
- Grid: Magenta/Pink `(1.0, 0.2, 0.6)`
- Mountains: Cyan `(0.0, 0.8, 0.996)`
- Stars: White with purple tint

### Animation
- Grid moves forward at constant speed (0.3 units per second)
- Mountains scroll slowly with parallax (3 layers at different speeds)
- Sun remains static with horizontal stripes
- Scan lines are stationary based on screen space

### Retrowave Elements
The shader includes all the iconic elements of classic retrowave/synthwave art:
1. **Large Sun**: Positioned in the upper third with a gradient from yellow (top) through orange (middle) to pink (bottom)
2. **Horizontal Stripes**: Dark stripes cutting through the sun for that classic 80s VHS aesthetic
3. **Wireframe Mountains**: Three layers of procedurally-generated triangular mountains with cyan wireframe
4. **Perspective Grid**: Pink/magenta grid floor that extends to the horizon
5. **Starfield**: Scattered stars in the night sky
6. **Purple Sky**: Classic retrowave purple gradient background

## Testing

Run the shader validation tests:
```bash
python tests/test_background_shaders.py
```

For visual testing:
```bash
python tests/test_retrowave_visual.py
```

## Screenshot
![Retrowave Background](https://github.com/user-attachments/assets/87005041-48d5-4266-8f67-6d92f96cec71)

The shader creates an immersive retrowave atmosphere with wireframe mountains, a large gradient sun with horizontal stripes, perspective grid floor, and starfield - perfect for the neon aesthetic of the game!

