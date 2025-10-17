#!/usr/bin/env python3
"""
Example: Using the tweening library for a simple animation.

This example shows how to use the tweening library to create smooth
animations for game objects.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from src.utils.tweening import TweenManager, EaseType

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BG_COLOR = (13, 5, 38)
BALL_COLOR = (1, 205, 254)  # Cyan

class AnimatedBall:
    """A ball that can be animated using tweens"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.tween_manager = TweenManager()
        self.x_tween = None
        self.y_tween = None
    
    def move_to(self, target_x, target_y, duration=1.0, ease_type=EaseType.QUAD_IN_OUT):
        """Smoothly move the ball to a target position"""
        # Remove existing position tweens if any
        # This allows the ball to change direction mid-animation
        if self.x_tween and not self.x_tween.is_complete:
            self.tween_manager.tweens.remove(self.x_tween)
        if self.y_tween and not self.y_tween.is_complete:
            self.tween_manager.tweens.remove(self.y_tween)
        
        # Create new tweens for x and y
        self.x_tween = self.tween_manager.add_tween(
            self.x, target_x, duration, ease_type
        )
        self.y_tween = self.tween_manager.add_tween(
            self.y, target_y, duration, ease_type
        )
    
    def update(self, dt):
        """Update the ball's position based on active tweens"""
        self.tween_manager.update(dt)
        
        # Update position from tweens
        if self.x_tween:
            self.x = self.x_tween.value
        if self.y_tween:
            self.y = self.y_tween.value
    
    def draw(self, screen):
        """Draw the ball"""
        pygame.draw.circle(screen, BALL_COLOR, (int(self.x), int(self.y)), self.radius)


def main():
    """Main example"""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tweening Example - Click to move ball")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Create a ball
    ball = AnimatedBall(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    # Current easing type
    easing_types = [
        EaseType.LINEAR,
        EaseType.QUAD_IN_OUT,
        EaseType.CUBIC_IN_OUT,
        EaseType.ELASTIC_OUT,
        EaseType.BOUNCE_OUT,
        EaseType.BACK_OUT,
    ]
    current_easing_index = 1
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Move ball to click position with current easing
                mouse_x, mouse_y = event.pos
                ease_type = easing_types[current_easing_index]
                ball.move_to(mouse_x, mouse_y, 1.0, ease_type)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Cycle through easing types
                    current_easing_index = (current_easing_index + 1) % len(easing_types)
        
        # Update
        ball.update(dt)
        
        # Draw
        screen.fill(BG_COLOR)
        ball.draw(screen)
        
        # Draw current easing type
        current_ease = easing_types[current_easing_index]
        ease_text = font.render(
            f"Current Easing: {current_ease.value.replace('_', ' ').title()}", 
            True, (255, 255, 255)
        )
        screen.blit(ease_text, (10, 10))
        
        instructions = font.render(
            "Click to move ball | SPACE to change easing", 
            True, (200, 200, 200)
        )
        screen.blit(instructions, (10, 40))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == '__main__':
    print("Starting Tweening Example...")
    print("Click anywhere to move the ball with smooth animation")
    print("Press SPACE to cycle through different easing types")
    print()
    main()
