# Sprite System

The neon pong game now supports sprite-based rendering for paddles and balls, while maintaining the existing shader-based procedural rendering as a fallback.

## Quick Start

### 1. Add sprite images to `assets/images/`

Supported formats: PNG, JPG, JPEG, BMP, GIF, TGA

Example sprites:

- `paddle1.png` - Player 1 paddle sprite
- `paddle2.png` - Player 2 paddle sprite  
- `ball.png` - Ball sprite

### 2. Load sprites in your scene

```python
from src.managers.asset_manager import AssetManager

# In your scene initialization
asset_manager = AssetManager()
asset_manager.preload_images()  # Load all images from assets/images/

# Set paddle sprites
paddle1_sprite = asset_manager.get_image('paddle1')  # Name without extension
paddle2_sprite = asset_manager.get_image('paddle2')
self.paddle1.set_sprite(paddle1_sprite)
self.paddle2.set_sprite(paddle2_sprite)

# Set ball sprite
ball_sprite = asset_manager.get_image('ball')
self.ball.set_sprite(ball_sprite)
```

### 3. Sprites are automatically rendered

If a sprite is set, it will be used instead of the procedural rectangle/circle. The sprite inherits all the same effects:

- **Paddles**: Color tinting on hit flash
- **Ball**: Color tinting, trail effect (trail still uses circles)

## API Reference

### AssetManager

```python
# Load all images at once
count = asset_manager.preload_images()  # Returns number of images loaded

# Load a specific image
surface = asset_manager.load_image('my_sprite.png')  # Returns pygame.Surface

# Get a previously loaded image
surface = asset_manager.get_image('my-sprite')  # Name is normalized (no extension, lowercase, hyphens)
```

### Entity Methods

```python
# Paddle
paddle.set_sprite(sprite_surface)  # Set sprite, or None to use default rectangle
paddle.sprite  # Access current sprite (pygame.Surface | None)

# Ball
ball.set_sprite(sprite_surface)  # Set sprite, or None to use default circle
ball.sprite  # Access current sprite (pygame.Surface | None)
```

### Renderer

```python
renderer.draw_sprite(
    sprite,          # pygame.Surface
    x, y,           # Position (top-left corner)
    width, height,  # Size (None = use sprite dimensions)
    color           # RGBA tint (1,1,1,1 = no tint)
)
```

## Sprite Specifications

### Paddle Sprites

- **Recommended size**: ~20x100 pixels (will be scaled to match PADDLE_WIDTH x PADDLE_HEIGHT)
- **Format**: PNG with alpha channel for transparency
- **Colors**: Any - color tinting is applied for hit flash effect
- **Player differentiation**: Create separate sprites for each player, or use the same sprite (colors can be tinted)

### Ball Sprites

- **Recommended size**: 20x20 pixels (will be scaled to match BALL_SIZE)
- **Format**: PNG with alpha channel
- **Shape**: Should be roughly square/circular for collision to look natural
- **Trail**: The trail still renders as circles regardless of ball sprite

## Technical Details

### Rendering Pipeline

1. Sprites are converted to OpenGL textures on the fly
2. Rendered using the existing `basic` shader program
3. UV mapping: (0,0) = top-left, (1,1) = bottom-right
4. Texture filtering: NEAREST (pixel-perfect for retro aesthetic)
5. Color tinting multiplies sprite colors with the tint color

### Performance

- Sprites create/destroy OpenGL textures each frame (trade-off for simplicity)
- For better performance, consider caching textures in Renderer (future optimization)
- Current implementation is fine for 2 paddles + 1 ball

### Fallback Behavior

- If no sprite is set (`sprite = None`), the game uses procedural drawing:
  - Paddles: Colored rectangles (`draw_rect`)
  - Ball: Colored circle (`draw_circle`)
- This allows mixing sprite and procedural rendering

## Example: Creating Simple Test Sprites

```python
# Create a simple colored rectangle sprite for testing
import pygame

# Create paddle sprite (20x100 cyan rectangle)
paddle_sprite = pygame.Surface((20, 100), pygame.SRCALPHA)
paddle_sprite.fill((0, 205, 254, 255))  # Cyan with full alpha

# Create ball sprite (20x20 yellow circle)
ball_sprite = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.circle(ball_sprite, (255, 234, 0, 255), (10, 10), 10)

# Save for future use
pygame.image.save(paddle_sprite, 'assets/images/paddle_test.png')
pygame.image.save(ball_sprite, 'assets/images/ball_test.png')
```

## Future Enhancements

- Animated sprites (sprite sheets)
- Particle system sprite support
- Texture caching in Renderer for better performance
- Rotation support for sprites
- Advanced blend modes
