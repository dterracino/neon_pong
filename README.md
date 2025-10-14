# Neon Pong with ModernGL Bloom Effects

A retro Pong game with modern graphics featuring neon-vaporwave aesthetics, bloom post-processing effects using ModernGL shaders, and proper audio management.

## Features

- 🎮 Classic Pong gameplay with modern graphics
- ✨ Bloom post-processing effects using ModernGL
- 🌌 **Shader-drawn animated backgrounds** (starfield, plasma, waves)
- 🌈 Neon-vaporwave color scheme
- 🎵 Sound effects and background music support
- 🎯 Two-player local multiplayer
- 🤖 AI opponent option
- 💫 Particle effects and screen shake
- 🔍 Comprehensive debug logging for troubleshooting

## Architecture

- **DRY Principles**: No code duplication, reusable components
- **Separation of Concerns**: Logical file separation by responsibility
- **Asset Management**: Centralized asset loading and caching
- **Shader Management**: Dynamic shader compilation and management
- **Scene System**: Modular scene management

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

### Troubleshooting

If the game displays a black screen or doesn't start properly, check the console output for debug messages. See [docs/DEBUG_GUIDE.md](docs/DEBUG_GUIDE.md) for detailed troubleshooting instructions.

You can also run `python tests/test_debug_output.py` to see what normal debug output should look like.

## Controls

- **Player 1**: W (up) / S (down)
- **Player 2**: Up Arrow / Down Arrow
- **Pause**: ESC or P
- **Menu**: Arrow keys + Enter

## Project Structure

```
pong-moderngl/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── src/                         # Source code
│   ├── entities/                # Game entities (Ball, Paddle, etc.)
│   ├── managers/                # Asset, Shader, Scene managers
│   ├── rendering/               # ModernGL rendering & post-processing
│   ├── scenes/                  # Game scenes (Menu, Game, Pause)
│   ├── audio/                   # Audio management
│   └── utils/                   # Constants and utilities
├── assets/                      # Game assets
│   ├── fonts/                   # Font files
│   ├── sounds/                  # Sound effects
│   └── music/                   # Background music
└── shaders/                     # GLSL shaders
    ├── basic.vert               # Basic vertex shader
    ├── basic.frag               # Basic fragment shader
    ├── text.vert/frag           # Text rendering shaders
    ├── background_*.frag        # Animated background shaders
    ├── bloom_extract.frag       # Bloom extraction
    ├── bloom_blur.frag          # Gaussian blur
    └── bloom_combine.frag       # Bloom combining
```

## Technical Details

### Graphics Pipeline

1. **Background Rendering**: Shader-drawn animated background
2. **Scene Rendering**: Game objects rendered to framebuffer
3. **Bloom Extraction**: Extract bright pixels above threshold
4. **Gaussian Blur**: Multi-pass blur for glow effect
5. **Combine**: Merge original scene with bloom
6. **Display**: Final image to screen

### Animated Backgrounds

Choose from multiple GPU-rendered backgrounds in `src/utils/constants.py`:
- **Starfield**: Parallax star layers with twinkling (default)
- **Plasma**: Smooth flowing neon colors
- **Waves**: Animated wave patterns with retro grid
- **Solid**: Static background for maximum performance

See [docs/BACKGROUND_SHADERS.md](docs/BACKGROUND_SHADERS.md) for details.

### Color Scheme

- **Pink**: #FF71CE
- **Cyan**: #01CDFE
- **Purple**: #B967FF
- **Yellow**: #FDFF6A
- **Mint**: #05FFA1

## Dependencies

- `pygame>=2.5.0` - Game framework and audio
- `moderngl>=5.8.0` - OpenGL rendering
- `numpy>=1.24.0` - Array operations
- `PyGLM>=2.7.0` - Mathematics library

## License

MIT License - Feel free to use and modify!