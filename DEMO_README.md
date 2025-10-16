# Background Shader Demo

An interactive demo application to visualize all background shaders used in Neon Pong.

## Features

- **Interactive Shader Switching** - Press number keys 1-4 to instantly switch between different background shaders
- **Real-time Animation** - All shaders are animated in real-time with proper time and resolution uniforms
- **Full-Screen Display** - 1280x720 window showcasing each shader in its full glory

## Available Shaders

1. **Starfield** (Press 1)
   - Parallax starfield with multiple layers
   - Twinkling stars in neon colors
   - Swirling nebula effects

2. **Plasma** (Press 2)
   - Flowing plasma effect with multiple sine waves
   - Smooth color transitions through neon palette
   - Hypnotic organic movement

3. **Waves** (Press 3)
   - Animated wave patterns
   - Retro grid overlay
   - Cyan and pink color scheme

4. **Retrowave** (Press 4)
   - Classic synthwave aesthetic
   - Wireframe mountains with parallax
   - Large gradient sun with horizontal stripes
   - Perspective grid floor
   - Starfield

5. **Retro** (Press 5)
   - Synthwave with large striped sun
   - Wireframe mountains (solid fill with cyan wire)
   - Pink/magenta perspective grid
   - Based on classic 80s aesthetic

## Usage

### Running the Demo

```bash
# Make sure you have the required dependencies installed
pip install -r requirements.txt

# Run the demo
python demo_backgrounds.py
```

### Controls

- **1** - Switch to Starfield shader
- **2** - Switch to Plasma shader
- **3** - Switch to Waves shader
- **4** - Switch to Retrowave shader
- **5** - Switch to Retro shader
- **H** - Print current shader information to console
- **ESC** - Exit the demo

## Technical Details

The demo application uses:
- **pygame** for window management and event handling
- **ModernGL** for OpenGL context and shader rendering
- **ShaderManager** from the main game for shader compilation and loading

All shaders use the same vertex shader (`basic.vert`) and render to a fullscreen quad.

## Screenshots

When running, each shader provides unique visual effects:

- **Starfield**: Deep space with twinkling stars and nebula clouds
- **Plasma**: Flowing neon colors with smooth transitions
- **Waves**: Retro-style animated waves with grid overlay
- **Retrowave**: Complete synthwave scene with all classic elements (for debugging)
- **Retro**: Classic 80s synthwave with large striped sun and wireframe mountains

## Development

This demo is useful for:
- Testing shader changes without running the full game
- Showcasing the visual styles available in Neon Pong
- Debugging shader compilation and rendering issues
- Creating screenshots and promotional material

## Notes

- The demo runs at 60 FPS
- All shaders receive the same `time` uniform for synchronized animation
- Resolution is set to 1280x720 (standard HD)
- Shaders are loaded once at startup for performance
