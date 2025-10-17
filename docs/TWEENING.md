# Tweening Library

A comprehensive tweening/easing library for smooth animations and transitions in Neon Pong.

## Overview

The tweening library provides smooth interpolation between values using various easing functions. It's perfect for:
- Animated UI transitions
- Screen transitions between scenes
- Smooth movement of game objects
- Camera movements
- Property animations (position, scale, rotation, opacity, etc.)

## Features

- **31 Easing Functions**: Complete set of common easing types
- **Simple API**: Easy to use `Tween` class for individual animations
- **Tween Manager**: Manage multiple concurrent animations
- **Completion Callbacks**: Execute code when animations finish
- **Zero Dependencies**: Pure Python implementation using only math module

## Available Easing Types

The library includes all standard easing functions with in, out, and in-out variations:

### Basic
- `LINEAR` - Constant speed, no acceleration

### Quadratic (Quad)
- `QUAD_IN` - Accelerating from zero velocity
- `QUAD_OUT` - Decelerating to zero velocity
- `QUAD_IN_OUT` - Acceleration then deceleration

### Cubic
- `CUBIC_IN` - Stronger acceleration from zero
- `CUBIC_OUT` - Stronger deceleration to zero
- `CUBIC_IN_OUT` - Acceleration then deceleration

### Quartic (Quart)
- `QUART_IN` - Very strong acceleration
- `QUART_OUT` - Very strong deceleration
- `QUART_IN_OUT` - Strong acceleration then deceleration

### Quintic (Quint)
- `QUINT_IN` - Extremely strong acceleration
- `QUINT_OUT` - Extremely strong deceleration
- `QUINT_IN_OUT` - Extreme acceleration then deceleration

### Sine
- `SINE_IN` - Smooth sinusoidal acceleration
- `SINE_OUT` - Smooth sinusoidal deceleration
- `SINE_IN_OUT` - Smooth sinusoidal in/out

### Exponential (Expo)
- `EXPO_IN` - Exponential acceleration
- `EXPO_OUT` - Exponential deceleration
- `EXPO_IN_OUT` - Exponential in/out

### Circular (Circ)
- `CIRC_IN` - Circular acceleration
- `CIRC_OUT` - Circular deceleration
- `CIRC_IN_OUT` - Circular in/out

### Elastic
- `ELASTIC_IN` - Elastic snap-in effect
- `ELASTIC_OUT` - Elastic snap-out effect (bouncy overshoot)
- `ELASTIC_IN_OUT` - Elastic both ways

### Back
- `BACK_IN` - Pulls back before moving forward
- `BACK_OUT` - Overshoots then settles back
- `BACK_IN_OUT` - Backs up then overshoots

### Bounce
- `BOUNCE_IN` - Bouncing into position
- `BOUNCE_OUT` - Bouncing to rest
- `BOUNCE_IN_OUT` - Bouncing in and out

## Usage Examples

### Basic Tween

```python
from src.utils.tweening import Tween, EaseType

# Create a tween that goes from 0 to 100 over 2 seconds
tween = Tween(0, 100, 2.0, EaseType.QUAD_IN_OUT)

# In your game loop:
def update(dt):
    tween.update(dt)
    current_value = tween.value
    
    # Use current_value for animation
    sprite.x = current_value
    
    if tween.is_complete:
        # Animation finished
        pass
```

### With Completion Callback

```python
from src.utils.tweening import Tween, EaseType

def on_animation_complete():
    print("Animation finished!")
    # Start next animation, change scene, etc.

tween = Tween(
    start=0, 
    end=100, 
    duration=1.0, 
    ease_type=EaseType.BOUNCE_OUT,
    on_complete=on_animation_complete
)
```

### Using TweenManager

```python
from src.utils.tweening import TweenManager, EaseType

# Create manager
manager = TweenManager()

# Add multiple tweens
x_tween = manager.add_tween(0, 640, 1.0, EaseType.CUBIC_OUT)
y_tween = manager.add_tween(0, 360, 1.0, EaseType.CUBIC_OUT)
alpha_tween = manager.add_tween(0, 1, 0.5, EaseType.LINEAR)

# In your game loop:
def update(dt):
    manager.update(dt)
    
    # Use the values
    sprite.x = x_tween.value
    sprite.y = y_tween.value
    sprite.alpha = alpha_tween.value
    
    print(f"Active animations: {manager.active_count}")
```

### Animating Object Properties

```python
from src.utils.tweening import Tween, EaseType

class AnimatedSprite:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.tweens = []
    
    def move_to(self, target_x, target_y, duration=1.0):
        # Create tweens for x and y
        x_tween = Tween(self.x, target_x, duration, EaseType.QUAD_IN_OUT)
        y_tween = Tween(self.y, target_y, duration, EaseType.QUAD_IN_OUT)
        
        self.tweens = [x_tween, y_tween]
    
    def update(self, dt):
        for tween in self.tweens:
            tween.update(dt)
        
        # Update positions
        if len(self.tweens) >= 2:
            self.x = self.tweens[0].value
            self.y = self.tweens[1].value
        
        # Remove completed tweens
        self.tweens = [t for t in self.tweens if not t.is_complete]
```

### Screen Transitions

```python
from src.utils.tweening import Tween, EaseType

class FadeTransition:
    def __init__(self, duration=0.5):
        self.fade_tween = Tween(
            start=0, 
            end=1, 
            duration=duration,
            ease_type=EaseType.SINE_IN_OUT,
            on_complete=self.on_fade_complete
        )
        self.opacity = 0
    
    def update(self, dt):
        self.fade_tween.update(dt)
        self.opacity = self.fade_tween.value
    
    def on_fade_complete(self):
        # Change scene, etc.
        pass
```

### UI Animations

```python
from src.utils.tweening import TweenManager, EaseType

class MenuButton:
    def __init__(self):
        self.scale = 1.0
        self.manager = TweenManager()
    
    def on_hover(self):
        # Scale up with elastic effect
        self.manager.clear()  # Cancel any existing animations
        self.manager.add_tween(
            self.scale, 1.2, 0.3, 
            EaseType.ELASTIC_OUT
        )
    
    def on_unhover(self):
        # Scale back down
        self.manager.clear()
        self.manager.add_tween(
            self.scale, 1.0, 0.2, 
            EaseType.BACK_OUT
        )
    
    def update(self, dt):
        self.manager.update(dt)
        if self.manager.active_count > 0:
            # Get the first tween's value
            self.scale = list(self.manager.tweens)[0].value if self.manager.tweens else 1.0
```

## Testing

Run the comprehensive test suite and visual demo:

```bash
python tests/test_tweening.py
```

This will:
1. Run unit tests to verify all easing functions work correctly
2. Launch an interactive visual demo showing all easing types in action

The visual demo shows all 31 easing functions simultaneously, making it easy to compare behaviors and choose the right one for your needs.

### Visual Demo Controls
- **SPACE**: Restart all animations
- **ESC**: Exit demo

## API Reference

### `Tween` Class

#### Constructor
```python
Tween(start: float, end: float, duration: float, 
      ease_type: EaseType = EaseType.LINEAR,
      on_complete: Optional[Callable[[], None]] = None)
```

#### Properties
- `value: float` - Current interpolated value
- `progress: float` - Progress from 0.0 to 1.0
- `is_complete: bool` - Whether the tween has finished

#### Methods
- `update(dt: float)` - Update the tween by delta time
- `reset()` - Reset the tween to the beginning

### `TweenManager` Class

#### Constructor
```python
TweenManager()
```

#### Methods
- `add_tween(start, end, duration, ease_type, on_complete)` - Add a new tween
- `update(dt: float)` - Update all tweens
- `clear()` - Remove all tweens

#### Properties
- `active_count: int` - Number of active tweens

### `EaseType` Enum

See "Available Easing Types" section above for all 31 types.

## Integration with Neon Pong

The tweening library can be used throughout the game:

1. **Menu Animations**: Smooth transitions between menu options
2. **Scene Transitions**: Fade in/out between scenes
3. **Paddle Movement**: Smooth AI paddle movement
4. **Ball Effects**: Special ball movement effects
5. **Particle Effects**: Advanced particle animations
6. **UI Elements**: Animated buttons, popups, and indicators
7. **Camera Shake**: Smooth camera movement effects
8. **Score Display**: Animated score changes

## Performance

- Lightweight implementation with minimal overhead
- No external dependencies beyond Python's `math` module
- Efficient for managing dozens of concurrent animations
- Suitable for real-time game use at 60+ FPS

## Credits

Based on standard easing equations popularized by Robert Penner and used throughout the game development industry.
