#!/usr/bin/env python3
"""
Visual demonstration of all tweening/easing types.

This script creates an interactive window showing all available easing functions
with animated balls that demonstrate each easing style. The visual comparison
makes it easy to understand how each easing type behaves.

Controls:
- SPACE: Restart all animations
- ESC: Exit
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from src.utils.tweening import EaseType, Tween, TweenManager


# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60

# Colors (RGB)
BG_COLOR = (13, 5, 38)  # Dark purple background
TEXT_COLOR = (255, 255, 255)
GRID_COLOR = (50, 50, 80)

# Animation settings
ANIMATION_DURATION = 2.0  # seconds
START_X = 100
END_X = WINDOW_WIDTH - 100
BALL_RADIUS = 8

# Easing types to demonstrate (grouped by category)
EASING_GROUPS = [
    ("Basic", [
        EaseType.LINEAR,
    ]),
    ("Quadratic", [
        EaseType.QUAD_IN,
        EaseType.QUAD_OUT,
        EaseType.QUAD_IN_OUT,
    ]),
    ("Cubic", [
        EaseType.CUBIC_IN,
        EaseType.CUBIC_OUT,
        EaseType.CUBIC_IN_OUT,
    ]),
    ("Quartic", [
        EaseType.QUART_IN,
        EaseType.QUART_OUT,
        EaseType.QUART_IN_OUT,
    ]),
    ("Quintic", [
        EaseType.QUINT_IN,
        EaseType.QUINT_OUT,
        EaseType.QUINT_IN_OUT,
    ]),
    ("Sine", [
        EaseType.SINE_IN,
        EaseType.SINE_OUT,
        EaseType.SINE_IN_OUT,
    ]),
    ("Exponential", [
        EaseType.EXPO_IN,
        EaseType.EXPO_OUT,
        EaseType.EXPO_IN_OUT,
    ]),
    ("Circular", [
        EaseType.CIRC_IN,
        EaseType.CIRC_OUT,
        EaseType.CIRC_IN_OUT,
    ]),
    ("Elastic", [
        EaseType.ELASTIC_IN,
        EaseType.ELASTIC_OUT,
        EaseType.ELASTIC_IN_OUT,
    ]),
    ("Back", [
        EaseType.BACK_IN,
        EaseType.BACK_OUT,
        EaseType.BACK_IN_OUT,
    ]),
    ("Bounce", [
        EaseType.BOUNCE_IN,
        EaseType.BOUNCE_OUT,
        EaseType.BOUNCE_IN_OUT,
    ]),
]

# Flatten list and assign colors
ALL_EASE_TYPES = []
EASE_COLORS = []

# Color palette for different groups
GROUP_COLORS = [
    (255, 113, 206),  # Pink
    (1, 205, 254),    # Cyan
    (185, 103, 255),  # Purple
    (253, 255, 106),  # Yellow
    (5, 255, 161),    # Mint
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 200, 255),  # Light Blue
    (255, 150, 50),   # Orange
    (200, 100, 255),  # Lavender
    (255, 200, 100),  # Peach
]

for group_idx, (group_name, ease_types) in enumerate(EASING_GROUPS):
    color = GROUP_COLORS[group_idx % len(GROUP_COLORS)]
    for ease_type in ease_types:
        ALL_EASE_TYPES.append(ease_type)
        EASE_COLORS.append(color)


class TweeningDemo:
    """Main demo application"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tweening Library - Easing Functions Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        self.running = True
        self.tweens: list[Tween] = []
        
        # Create all tweens
        self.create_tweens()
    
    def create_tweens(self):
        """Create a tween for each easing type"""
        self.tweens = []
        for ease_type in ALL_EASE_TYPES:
            tween = Tween(START_X, END_X, ANIMATION_DURATION, ease_type)
            self.tweens.append(tween)
    
    def restart_animations(self):
        """Restart all animations"""
        for tween in self.tweens:
            tween.reset()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.restart_animations()
    
    def update(self, dt: float):
        """Update all tweens"""
        for tween in self.tweens:
            tween.update(dt)
        
        # Auto-restart when all animations complete
        if all(tween.is_complete for tween in self.tweens):
            self.restart_animations()
    
    def draw(self):
        """Draw the demo"""
        self.screen.fill(BG_COLOR)
        
        # Draw title
        title_text = self.title_font.render(
            "Tweening Library - All Easing Functions", True, TEXT_COLOR
        )
        self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 10))
        
        # Draw instructions
        instructions = self.font.render(
            "Press SPACE to restart animations | ESC to exit", True, (200, 200, 200)
        )
        self.screen.blit(instructions, (WINDOW_WIDTH // 2 - instructions.get_width() // 2, 45))
        
        # Calculate layout
        row_height = 25
        start_y = 90
        
        # Draw grid lines for reference
        pygame.draw.line(self.screen, GRID_COLOR, (START_X, start_y - 10), 
                        (START_X, WINDOW_HEIGHT - 20), 1)
        pygame.draw.line(self.screen, GRID_COLOR, (END_X, start_y - 10), 
                        (END_X, WINDOW_HEIGHT - 20), 1)
        
        # Draw each tween
        current_group = None
        y_offset = start_y
        
        for i, (tween, ease_type, color) in enumerate(zip(self.tweens, ALL_EASE_TYPES, EASE_COLORS)):
            # Find which group this belongs to
            for group_name, group_types in EASING_GROUPS:
                if ease_type in group_types:
                    if current_group != group_name:
                        # Draw group header
                        current_group = group_name
                        y_offset += 10
                        group_text = self.font.render(f"--- {group_name} ---", True, (150, 150, 150))
                        self.screen.blit(group_text, (10, y_offset))
                        y_offset += row_height
                    break
            
            # Get current position
            x = int(tween.value)
            y = y_offset
            
            # Draw the ball
            pygame.draw.circle(self.screen, color, (x, y), BALL_RADIUS)
            
            # Draw progress bar background
            bar_width = END_X - START_X
            bar_height = 3
            bar_y = y + BALL_RADIUS + 2
            pygame.draw.rect(self.screen, (40, 40, 60), 
                           (START_X, bar_y, bar_width, bar_height))
            
            # Draw progress bar fill
            progress_width = int(bar_width * tween.progress)
            if progress_width > 0:
                # Fade the color for the progress bar
                bar_color = tuple(int(c * 0.6) for c in color)
                pygame.draw.rect(self.screen, bar_color, 
                               (START_X, bar_y, progress_width, bar_height))
            
            # Draw label
            label = ease_type.value.replace('_', ' ').title()
            label_text = self.font.render(label, True, TEXT_COLOR)
            self.screen.blit(label_text, (END_X + 15, y - 8))
            
            y_offset += row_height
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()


def test_basic_tween():
    """Test basic tween functionality without pygame"""
    print("Testing basic tween functionality...")
    
    # Test linear tween
    tween = Tween(0, 100, 1.0, EaseType.LINEAR)
    assert tween.value == 0, "Initial value should be 0"
    
    # Update halfway
    tween.update(0.5)
    assert abs(tween.value - 50) < 0.1, f"Value at 0.5s should be ~50, got {tween.value}"
    assert not tween.is_complete, "Tween should not be complete"
    
    # Update to completion
    tween.update(0.5)
    assert abs(tween.value - 100) < 0.1, f"Final value should be ~100, got {tween.value}"
    assert tween.is_complete, "Tween should be complete"
    
    print("✓ Basic tween test passed")
    return True


def test_tween_manager():
    """Test tween manager functionality"""
    print("Testing tween manager...")
    
    manager = TweenManager()
    
    # Add multiple tweens
    tween1 = manager.add_tween(0, 100, 1.0, EaseType.LINEAR)
    tween2 = manager.add_tween(50, 150, 2.0, EaseType.QUAD_OUT)
    
    assert manager.active_count == 2, "Manager should have 2 active tweens"
    
    # Update
    manager.update(0.5)
    assert abs(tween1.value - 50) < 0.1, "Tween1 value should be ~50"
    assert not tween1.is_complete, "Tween1 should not be complete"
    
    # Complete first tween
    manager.update(0.5)
    assert tween1.is_complete, "Tween1 should be complete"
    
    # Manager should auto-remove completed tweens on next update
    manager.update(0.1)
    assert manager.active_count == 1, "Manager should have 1 active tween"
    
    print("✓ Tween manager test passed")
    return True


def test_all_easing_functions():
    """Test that all easing functions work without errors"""
    print("Testing all easing functions...")
    
    for ease_type in ALL_EASE_TYPES:
        tween = Tween(0, 100, 1.0, ease_type)
        
        # Test at various points
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            tween.elapsed = t
            value = tween.value
            assert isinstance(value, (int, float)), f"{ease_type} should return numeric value"
        
        print(f"  ✓ {ease_type.value}")
    
    print("✓ All easing functions test passed")
    return True


def test_callback():
    """Test completion callback"""
    print("Testing completion callback...")
    
    callback_called = [False]  # Use list to modify in nested function
    
    def on_complete():
        callback_called[0] = True
    
    tween = Tween(0, 100, 1.0, EaseType.LINEAR, on_complete=on_complete)
    tween.update(1.0)
    
    assert callback_called[0], "Callback should have been called"
    assert tween.is_complete, "Tween should be complete"
    
    print("✓ Callback test passed")
    return True


if __name__ == '__main__':
    print("=" * 70)
    print("Tweening Library Test Suite")
    print("=" * 70)
    print()
    
    # Run unit tests
    tests = [
        test_basic_tween(),
        test_tween_manager(),
        test_all_easing_functions(),
        test_callback(),
    ]
    
    print()
    print("=" * 70)
    if all(tests):
        print("✓ All unit tests PASSED!")
        print()
        print("Starting visual demonstration...")
        print("=" * 70)
        print()
        
        # Run visual demo
        demo = TweeningDemo()
        demo.run()
    else:
        print("✗ Some tests FAILED!")
        sys.exit(1)
