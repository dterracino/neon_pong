"""
Paddle entity
"""
import pygame
from src.utils.constants import (
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED,
    WINDOW_HEIGHT, COLOR_CYAN, COLOR_PINK
)
from src.utils.collision import AABB


class Paddle:
    """Represents a player paddle"""
    
    def __init__(self, x: float, y: float, player_num: int):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.velocity_y = 0
        self.player_num = player_num
        
        # Color based on player
        self.color = COLOR_CYAN if player_num == 1 else COLOR_PINK
        
        # Hit flash effect
        self.hit_flash = 0.0

        # Spin factor: how much paddle velocity influences ball trajectory on hit
        self.spin_factor = 0.25
        
    @property
    def bounds(self) -> AABB:
        """Get collision bounds"""
        return AABB(self.x, self.y, self.width, self.height)
    
    def update(self, dt: float):
        """Update paddle position"""
        # Move paddle
        self.y += self.velocity_y * dt
        
        # Clamp to screen bounds
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))
        
        # Update hit flash
        if self.hit_flash > 0:
            self.hit_flash -= dt * 3
            self.hit_flash = max(0, self.hit_flash)
    
    def move_up(self):
        """Start moving up"""
        self.velocity_y = -self.speed
    
    def move_down(self):
        """Start moving down"""
        self.velocity_y = self.speed
    
    def stop(self):
        """Stop moving"""
        self.velocity_y = 0
    
    def handle_input(self, keys):
        """Handle keyboard input"""
        if self.player_num == 1:
            if keys[pygame.K_w]:
                self.move_up()
            elif keys[pygame.K_s]:
                self.move_down()
            else:
                self.stop()
        elif self.player_num == 2:
            if keys[pygame.K_UP]:
                self.move_up()
            elif keys[pygame.K_DOWN]:
                self.move_down()
            else:
                self.stop()
    
    def on_hit(self):
        """Called when paddle hits the ball"""
        self.hit_flash = 1.0
    
    def get_color(self) -> tuple:
        """Get current color with hit flash effect"""
        if self.hit_flash > 0:
            # Brighten color on hit
            return tuple(min(1.0, c + self.hit_flash * 0.5) for c in self.color)
        return self.color