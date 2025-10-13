"""
Ball entity
"""
import random
import math
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
        
        # Increase speed
        self.speed = min(self.speed + BALL_SPEED_INCREMENT, BALL_MAX_SPEED)
        
        # Set new velocity
        direction = 1 if self.velocity_x < 0 else -1
        self.velocity_x = math.cos(angle) * self.speed * direction
        self.velocity_y = math.sin(angle) * self.speed
        
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