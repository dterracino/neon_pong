#!/usr/bin/env python3
"""
Visual demonstration of all tweening/easing types - Screenshot version.

This creates a static visualization of all easing functions for documentation.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from src.utils.tweening import EaseType, Tween

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
BG_COLOR = (13, 5, 38)  # Dark purple background
TEXT_COLOR = (255, 255, 255)
GRID_COLOR = (50, 50, 80)

# Animation settings
START_X = 100
END_X = WINDOW_WIDTH - 100
BALL_RADIUS = 8

# Easing types to demonstrate (grouped by category)
EASING_GROUPS = [
    ("Basic", [EaseType.LINEAR]),
    ("Quadratic", [EaseType.QUAD_IN, EaseType.QUAD_OUT, EaseType.QUAD_IN_OUT]),
    ("Cubic", [EaseType.CUBIC_IN, EaseType.CUBIC_OUT, EaseType.CUBIC_IN_OUT]),
    ("Quartic", [EaseType.QUART_IN, EaseType.QUART_OUT, EaseType.QUART_IN_OUT]),
    ("Quintic", [EaseType.QUINT_IN, EaseType.QUINT_OUT, EaseType.QUINT_IN_OUT]),
    ("Sine", [EaseType.SINE_IN, EaseType.SINE_OUT, EaseType.SINE_IN_OUT]),
    ("Exponential", [EaseType.EXPO_IN, EaseType.EXPO_OUT, EaseType.EXPO_IN_OUT]),
    ("Circular", [EaseType.CIRC_IN, EaseType.CIRC_OUT, EaseType.CIRC_IN_OUT]),
    ("Elastic", [EaseType.ELASTIC_IN, EaseType.ELASTIC_OUT, EaseType.ELASTIC_IN_OUT]),
    ("Back", [EaseType.BACK_IN, EaseType.BACK_OUT, EaseType.BACK_IN_OUT]),
    ("Bounce", [EaseType.BOUNCE_IN, EaseType.BOUNCE_OUT, EaseType.BOUNCE_IN_OUT]),
]

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

# Flatten list and assign colors
ALL_EASE_TYPES = []
EASE_COLORS = []

for group_idx, (group_name, ease_types) in enumerate(EASING_GROUPS):
    color = GROUP_COLORS[group_idx % len(GROUP_COLORS)]
    for ease_type in ease_types:
        ALL_EASE_TYPES.append(ease_type)
        EASE_COLORS.append(color)


def create_visualization(progress: float):
    """Create a single frame visualization at the given progress (0.0 to 1.0)"""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tweening Library - Easing Functions")
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 32)
    
    # Create tweens
    tweens = []
    for ease_type in ALL_EASE_TYPES:
        tween = Tween(START_X, END_X, 1.0, ease_type)
        tween.elapsed = progress  # Set to specific progress
        tweens.append(tween)
    
    # Draw
    screen.fill(BG_COLOR)
    
    # Draw title
    title_text = title_font.render(
        "Tweening Library - All Easing Functions", True, TEXT_COLOR
    )
    screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 10))
    
    # Draw instructions
    instructions = font.render(
        f"Animation Progress: {int(progress * 100)}%", True, (200, 200, 200)
    )
    screen.blit(instructions, (WINDOW_WIDTH // 2 - instructions.get_width() // 2, 45))
    
    # Calculate layout
    row_height = 25
    start_y = 90
    
    # Draw grid lines for reference
    pygame.draw.line(screen, GRID_COLOR, (START_X, start_y - 10), 
                    (START_X, WINDOW_HEIGHT - 20), 1)
    pygame.draw.line(screen, GRID_COLOR, (END_X, start_y - 10), 
                    (END_X, WINDOW_HEIGHT - 20), 1)
    
    # Draw each tween
    current_group = None
    y_offset = start_y
    
    for i, (tween, ease_type, color) in enumerate(zip(tweens, ALL_EASE_TYPES, EASE_COLORS)):
        # Find which group this belongs to
        for group_name, group_types in EASING_GROUPS:
            if ease_type in group_types:
                if current_group != group_name:
                    # Draw group header
                    current_group = group_name
                    y_offset += 10
                    group_text = font.render(f"--- {group_name} ---", True, (150, 150, 150))
                    screen.blit(group_text, (10, y_offset))
                    y_offset += row_height
                break
        
        # Get current position
        x = int(tween.value)
        y = y_offset
        
        # Draw the ball
        pygame.draw.circle(screen, color, (x, y), BALL_RADIUS)
        
        # Draw progress bar background
        bar_width = END_X - START_X
        bar_height = 3
        bar_y = y + BALL_RADIUS + 2
        pygame.draw.rect(screen, (40, 40, 60), 
                       (START_X, bar_y, bar_width, bar_height))
        
        # Draw progress bar fill
        progress_width = int(bar_width * tween.progress)
        if progress_width > 0:
            bar_color = tuple(int(c * 0.6) for c in color)
            pygame.draw.rect(screen, bar_color, 
                           (START_X, bar_y, progress_width, bar_height))
        
        # Draw label
        label = ease_type.value.replace('_', ' ').title()
        label_text = font.render(label, True, TEXT_COLOR)
        screen.blit(label_text, (END_X + 15, y - 8))
        
        y_offset += row_height
    
    pygame.display.flip()
    
    # Save screenshot
    screenshot_path = "/tmp/tweening_demo.png"
    pygame.image.save(screen, screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    pygame.quit()
    return screenshot_path


if __name__ == '__main__':
    # Create visualization at 60% progress (good point to show differences)
    screenshot_path = create_visualization(0.6)
    print(f"\n✓ Tweening visualization created successfully!")
    print(f"  Location: {screenshot_path}")
