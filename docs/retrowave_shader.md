# Retrowave Background Shader

## Overview
A new background shader type that creates a classic retrowave/synthwave aesthetic for Neon Pong.

## Visual Features
- **Perspective Grid Floor**: Cyan grid lines with proper perspective that animate towards the viewer
- **Gradient Sky**: Purple to pink gradient for that classic retrowave look
- **Animated Sun**: Neon pink sun on the horizon with glow and horizontal stripes
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
- `shaders/background_retrowave.frag` - New GLSL fragment shader
- `src/rendering/renderer.py` - Added retrowave background loading
- `src/utils/constants.py` - Documented retrowave as valid option
- `tests/test_background_shaders.py` - Added retrowave shader tests

### Shader Uniforms
- `uniform float time` - Animation time in seconds
- `uniform vec2 resolution` - Screen resolution for aspect ratio and scan lines

### Color Palette
- Sky Top: Dark purple `(0.05, 0.02, 0.15)`
- Sky Horizon: Purple `(0.4, 0.15, 0.5)`
- Sun: Neon pink `(1.0, 0.44, 0.81)`
- Grid: Cyan `(0.0, 0.8, 0.996)`
- Floor: Very dark purple `(0.02, 0.01, 0.08)`

### Animation
- Grid moves forward at constant speed (0.3 units per second)
- Sun remains static on the horizon
- Scan lines are stationary based on screen space

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
![Retrowave Background](https://github.com/user-attachments/assets/58ce902e-0a2e-401b-8cff-8903e8aa4409)

The shader creates an immersive retrowave atmosphere perfect for the neon aesthetic of the game!
