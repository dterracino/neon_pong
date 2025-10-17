# Retro Background Shader

## Overview
A new background shader type that creates a classic 80s synthwave/retrowave aesthetic for Neon Pong, closely matching traditional retrowave imagery.

## Visual Features
- **Large Striped Sun**: Yellow to pink gradient sun positioned on the horizon with horizontal dark stripes cutting through it - the quintessential retrowave sun
- **Wireframe Mountains**: Three layers of black silhouette mountains with cyan wireframe overlay for depth and parallax
- **Perspective Grid Floor**: Hot pink/magenta grid lines with proper perspective that animate towards the viewer
- **Starfield**: Scattered white stars in the upper purple sky
- **Dark Purple Gradient Sky**: Very dark blue/purple at top transitioning to lighter purple at horizon
- **CRT Scan Lines**: Subtle horizontal lines for authentic retro CRT monitor effect
- **Vignette**: Soft darkening at edges for depth

## Difference from Retrowave Shader

The "retro" shader is a more traditional implementation of the synthwave aesthetic, while "retrowave" is kept for debugging and represents an earlier iteration. Key differences:

**Retro Shader:**
- Large half-circle sun sitting ON the horizon (classic look)
- Dark horizontal stripes through the sun
- Solid black mountains with cyan wireframe overlay
- Darker, more purple color scheme
- Simpler, more authentic to 80s aesthetic

**Retrowave Shader:**
- Sun positioned above horizon
- More complex procedural mountains
- Full gradient sun without prominent stripes
- Brighter colors
- More modern interpretation

## Usage

To enable the retro background, edit `src/utils/constants.py`:

```python
BACKGROUND_TYPE = "retro"  # Options: "starfield", "plasma", "waves", "retrowave", "retro", "solid"
```

Then run the game:
```bash
python main.py
```

## Technical Details

### Files
- `shaders/background_retro.frag` - GLSL fragment shader with classic synthwave rendering

### Shader Uniforms
- `uniform float time` - Animation time in seconds
- `uniform vec2 resolution` - Screen resolution for aspect ratio and scan lines

### Color Palette
- Sky Top: Very dark blue `(0.02, 0.0, 0.15)`
- Sky Horizon: Dark purple `(0.2, 0.05, 0.3)`
- Sun Top: Bright yellow `(1.0, 0.95, 0.2)`
- Sun Bottom: Pink/coral `(1.0, 0.3, 0.4)`
- Grid: Hot pink/magenta `(1.0, 0.1, 0.5)`
- Mountains: Black silhouette `(0.0, 0.0, 0.0)`
- Mountain Wire: Cyan `(0.0, 0.6, 0.8)`

### Animation
- Grid moves forward at constant speed (0.2 units per second)
- Mountains scroll slowly with parallax (3 layers at different speeds)
- Sun remains static with horizontal stripes
- Scan lines are stationary based on screen space

### Key Features

1. **Authentic Sun**: The sun is rendered as a large half-circle sitting directly on the horizon with prominent dark horizontal stripes, matching the iconic 80s synthwave aesthetic

2. **Wireframe Mountains**: Mountains are rendered as solid black silhouettes with cyan wireframe lines, creating depth through multiple parallax layers

3. **Classic Grid**: The perspective grid uses hot pink/magenta color and extends from the viewer into the distance with proper perspective correction

4. **Atmospheric Sky**: Dark purple gradient creates the moody, nostalgic atmosphere typical of synthwave art

## Testing

Run the shader validation tests:
```bash
python tests/test_background_shaders.py
```

For visual testing in the demo app:
```bash
python demo_backgrounds.py
# Press 5 to view the Retro shader
```

## Screenshot

![Retro Background Shader](https://github.com/user-attachments/assets/096e38db-0992-4fdb-a919-d23c9a41029b)

The shader creates an authentic 80s synthwave atmosphere with the large striped sun, wireframe mountains, and perspective grid floor - perfectly capturing the classic retrowave aesthetic!

## Notes

This shader is designed to closely match traditional retrowave imagery with the large striped sun on the horizon. The "retrowave" shader remains available for comparison and debugging purposes.
