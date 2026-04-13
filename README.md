# Neon Pong with ModernGL Bloom Effects

A retro Pong game with modern graphics featuring neon-vaporwave aesthetics, bloom post-processing effects using ModernGL shaders, and proper audio management.

## Features

- 🎮 Classic Pong gameplay with modern graphics
- ✨ Bloom post-processing effects using ModernGL
- 🌌 **Shader-drawn animated backgrounds** (starfield, plasma, waves)
- 🎨 **Retro style effects** (scanlines, CRT, VHS) - NEW!
- 🌈 Neon-vaporwave color scheme
- 🎵 Sound effects and background music support
- 🎯 Single-player vs AI or two-player local multiplayer
- 🤖 AI opponent with three difficulty levels (Easy, Normal, Hard)
- 🏓 **Spin mechanic** — moving paddle while hitting deflects the ball, altering its exit angle
- 💫 Particle effects and screen shake
- 🚀 **Performance-optimized text rendering with intelligent caching**
- 📸 **Screenshot capture** with Ctrl-S
- 🎬 **Comprehensive tweening library** with 31 easing functions for smooth animations
- 🔍 Comprehensive debug logging for troubleshooting

## Architecture

- **DRY Principles**: No code duplication, reusable components
- **Separation of Concerns**: Logical file separation by responsibility
- **Asset Management**: Centralized asset loading and caching
- **Shader Management**: Dynamic shader compilation and management
- **Scene System**: Modular scene management
- **Text Cache System**: LRU cache for optimized text rendering performance

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

- **Menu Navigation**: Arrow keys + Enter to select
  - **1 Player**: Play against AI opponent
  - **2 Player**: Play against another human
- **Player 1**: W (up) / S (down)
- **Player 2**: Up Arrow / Down Arrow (in 2 Player mode)
- **Pause**: ESC or P
- **Screenshot**: Ctrl-S (saves to `screenshots/` directory)
- **FPS Display**: F3 (toggle performance metrics)

## Project Structure

```text
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
    ├── bloom_combine.frag       # Bloom combining
    ├── scanlines.frag           # Scanlines effect
    ├── crt.frag                 # CRT monitor effect
    └── vhs.frag                 # VHS tape effect
```

## Technical Details

### Graphics Pipeline

1. **Background Rendering**: Shader-drawn animated background
2. **Scene Rendering**: Game objects rendered to framebuffer
3. **Bloom Extraction**: Extract bright pixels above threshold
4. **Gaussian Blur**: Multi-pass blur for glow effect
5. **Bloom Combine**: Merge original scene with bloom
6. **Style Effect**: Optional retro effect (scanlines, CRT, VHS) - NEW!
7. **Display**: Final image to screen

### Animated Backgrounds

Choose from multiple GPU-rendered backgrounds in `src/utils/constants.py`:

- **Starfield**: Parallax star layers with twinkling (default)
- **Plasma**: Smooth flowing neon colors
- **Waves**: Animated wave patterns with retro grid
- **Solid**: Static background for maximum performance

### Post-Processing Style Effects

Apply retro visual effects in `src/utils/constants.py`:

- **None**: Clean modern look (default)
- **Scanlines**: Horizontal scanlines like old monitors
- **CRT**: Full CRT simulation with curvature and phosphor glow
- **VHS**: VHS tape artifacts with tracking errors and noise

See [docs/POST_PROCESSING_EFFECTS.md](docs/POST_PROCESSING_EFFECTS.md) for detailed information.

See [docs/BACKGROUND_SHADERS.md](docs/BACKGROUND_SHADERS.md) for details.

### Tweening/Animation System

The game includes a comprehensive tweening library with 31 easing functions for smooth animations:

- **11 Easing Categories**: Linear, Quad, Cubic, Quart, Quint, Sine, Expo, Circ, Elastic, Back, Bounce
- **In/Out/InOut Variations**: Fine control over animation curves
- **TweenManager**: Manage multiple concurrent animations
- **Perfect for**: UI transitions, screen fades, smooth movement, particle effects

See [docs/TWEENING.md](docs/TWEENING.md) for complete documentation and examples.

### AI Opponent

The AI paddle is controlled by a trajectory-prediction system with three configurable difficulty levels:

| Feature | Easy | Normal | Hard |
| --- | --- | --- | --- |
| Reaction time | 0.3 s | 0.15 s | 0.05 s |
| Movement speed | 60% | 80% | 100% |
| Prediction error | ±80 px | ±40 px | ±15 px |
| Target update rate | 5 Hz | 10 Hz | 20 Hz |
| Spin influence | None | Same as player | 2× player |
| Adaptive difficulty | No | No | Yes |

**Spin influence** — On Normal the AI generates the same spin effect as a human player when its paddle is in motion at contact. On Hard the influence is doubled, allowing the AI to hit sharper deflection angles.

**Adaptive difficulty (Hard only)** — If the AI falls 3 or more points behind, it automatically tightens its reaction time, reduces prediction error, and increases speed to compensate.

### Spin Mechanic

When a paddle is moving at the moment the ball makes contact, the paddle's vertical velocity is blended into the ball's outgoing trajectory:

- A paddle moving **in the same direction** as the ball's Y-velocity steepens the angle.
- A paddle moving **against** the ball's Y-velocity flattens it, or even reverses it back toward center.
- The ball speed is **preserved** — the velocity vector is renormalized after spin is applied, so spin changes direction only, never speed.

The blend weight (`spin_factor`) is 0.25 for human players — at full paddle speed this shifts the Y component by 25% before renormalization.

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
