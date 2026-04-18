"""
Ball entity
"""
import random
import math
import pygame
from src.utils.constants import (
    BALL_SIZE, BALL_SPEED_INITIAL, BALL_SPEED_INCREMENT,
    BALL_MAX_SPEED, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_YELLOW
)
from src.utils.collision import AABB


class Ball:
    """Represents the game ball"""
    
    def __init__(self, x: float, y: float):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.size = BALL_SIZE
        self.speed = BALL_SPEED_INITIAL
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.color = COLOR_YELLOW
        self.trail_positions: list[tuple[float, float]] = []
        
        # Sprite support (optional)
        self.sprite: pygame.Surface | None = None
        
        self.reset()
    
    @property
    def bounds(self) -> AABB:
        """Get collision bounds"""
        return AABB(self.x, self.y, self.size, self.size)
    
    def reset(self):
        """Reset ball to center with random direction"""
        self.x = self.start_x
        self.y = self.start_y
        self.speed = BALL_SPEED_INITIAL
        self.trail_positions.clear()
        
        # Random angle between -45 and 45 degrees, going left or right
        angle = random.uniform(-math.pi/4, math.pi/4)
        direction = random.choice([-1, 1])
        
        self.velocity_x = math.cos(angle) * self.speed * direction
        self.velocity_y = math.sin(angle) * self.speed
    
    def update(self, dt: float):
        """Update ball position"""
        # Move ball
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Store trail position
        self.trail_positions.append((self.x + self.size/2, self.y + self.size/2))
        if len(self.trail_positions) > 10:
            self.trail_positions.pop(0)
        
        # Bounce off top and bottom walls
        if self.y <= 0:
            self.y = 0
            self.velocity_y = abs(self.velocity_y)
            return 'wall'
        elif self.y >= WINDOW_HEIGHT - self.size:
            self.y = WINDOW_HEIGHT - self.size
            self.velocity_y = -abs(self.velocity_y)
            return 'wall'
        
        return None
    
    def bounce_paddle(self, paddle):
        """Bounce off paddle with angle variation"""
        # Calculate where ball hit paddle (0 = center, -1 = top, 1 = bottom)
        paddle_center = paddle.y + paddle.height / 2
        ball_center = self.y + self.size / 2
        hit_pos = (ball_center - paddle_center) / (paddle.height / 2)
        hit_pos = max(-1, min(1, hit_pos))
        
        # Calculate new angle based on hit position
        max_angle = math.pi / 3  # 60 degrees
        angle = hit_pos * max_angle
        
        # Increase speed on each hit (baseline acceleration)
        self.speed = min(self.speed + BALL_SPEED_INCREMENT, BALL_MAX_SPEED)

        # Set new velocity, blending in paddle spin
        direction = 1 if self.velocity_x < 0 else -1
        new_vx = math.cos(angle) * self.speed * direction
        base_vy = math.sin(angle) * self.speed

        # Spin: moving paddle deflects ball and adds speed, like a tennis racket.
        # spin_factor is set per-paddle (player=0.25, AI varies by difficulty)
        spin_influence = paddle.velocity_y * paddle.spin_factor
        new_vy = base_vy + spin_influence

        # The resulting magnitude may exceed self.speed — that's intentional.
        # Cap at BALL_MAX_SPEED and sync self.speed to the actual speed.
        actual_speed = math.sqrt(new_vx ** 2 + new_vy ** 2)
        if actual_speed > BALL_MAX_SPEED:
            scale = BALL_MAX_SPEED / actual_speed
            new_vx *= scale
            new_vy *= scale
            actual_speed = BALL_MAX_SPEED

        self.speed = actual_speed
        self.velocity_x = new_vx
        self.velocity_y = new_vy
        
        # Move ball out of paddle
        if direction == 1:  # Hit left paddle
            self.x = paddle.x + paddle.width
        else:  # Hit right paddle
            self.x = paddle.x - self.size
    
    def is_out_of_bounds(self) -> int:
        """Check if ball is out of bounds, return 1 or 2 for player that scored"""
        if self.x < -self.size:
            return 2  # Player 2 scored
        elif self.x > WINDOW_WIDTH:
            return 1  # Player 1 scored
        return 0
    
    def set_sprite(self, sprite: pygame.Surface | None):
        """Set the ball sprite image
        
        Args:
            sprite: pygame Surface to use as sprite, or None to use default circle
        """
        self.sprite = sprite