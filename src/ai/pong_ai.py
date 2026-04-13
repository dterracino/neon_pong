"""
AI Opponent for Pong

Provides intelligent paddle control with multiple difficulty levels.
Features human-like behavior including reaction delays, prediction errors,
and adaptive difficulty.
"""
import logging
import random
from typing import Optional
from src.entities.paddle import Paddle
from src.entities.ball import Ball
from src.utils.constants import WINDOW_HEIGHT, PADDLE_SPEED

logger = logging.getLogger(__name__)


class PongAI:
    """AI controller for paddle opponent
    
    Implements human-like behavior with:
    - Ball trajectory prediction
    - Reaction delays based on difficulty
    - Movement errors and imperfection
    - Periodic decision updates (not every frame)
    - Dead zone for micro-adjustments
    """
    
    def __init__(self, paddle: Paddle, ball: Ball, difficulty: str = 'normal'):
        """Initialize AI controller
        
        Args:
            paddle: The paddle to control
            ball: The ball to track
            difficulty: 'easy', 'normal', or 'hard'
        """
        self.paddle = paddle
        self.ball = ball
        self.difficulty = difficulty
        
        # Load difficulty configuration
        from src.utils.constants import AI_DIFFICULTIES
        self.config = AI_DIFFICULTIES[difficulty].copy()
        
        # AI state
        self.target_y: Optional[float] = None
        self.reaction_timer = 0.0
        self.update_timer = 0.0
        self.is_reacting = False
        
        # Apply spin factor to the controlled paddle
        self.paddle.spin_factor = self.config['spin_factor']

        logger.debug("AI initialized with difficulty '%s'", difficulty)
        logger.debug("AI config: %s", self.config)
    
    def update(self, dt: float):
        """Update AI decision making and paddle control
        
        Args:
            dt: Delta time in seconds
        """
        # Periodically update target position (not every frame)
        self.update_timer += dt
        if self.update_timer >= self.config['update_frequency']:
            self.update_timer = 0.0
            self._recalculate_target()
        
        # Handle reaction delay
        if self.target_y is not None and not self.is_reacting:
            self.reaction_timer += dt
            if self.reaction_timer >= self.config['reaction_time']:
                self.is_reacting = True
                self.reaction_timer = 0.0
        
        # Move paddle toward target if reacting
        if self.is_reacting and self.target_y is not None:
            self._move_toward_target()
    
    def _recalculate_target(self):
        """Recalculate target paddle position based on ball state"""
        old_target = self.target_y
        
        # Only react if ball is moving toward AI paddle
        if self.ball.velocity_x > 0:
            # Predict where ball will be when it reaches paddle
            new_target = self._predict_ball_position()
        else:
            # Ball moving away - return to center position
            new_target = WINDOW_HEIGHT / 2
        
        # Only reset reaction if target changed significantly
        if old_target is None or abs(new_target - old_target) > 30:
            self.target_y = new_target
            self.is_reacting = False
            self.reaction_timer = 0.0
            
            # If ball is moving away, react immediately (no delay)
            if self.ball.velocity_x <= 0:
                self.is_reacting = True
        else:
            # Target hasn't changed much, keep current reaction state
            self.target_y = new_target
    
    def _predict_ball_position(self) -> float:
        """Predict where ball will intersect with paddle's x position
        
        Returns:
            Predicted Y coordinate (with difficulty-based error)
        """
        # Calculate time until ball reaches paddle
        distance_to_paddle = abs(self.ball.x - self.paddle.x)
        
        # Avoid division by zero
        if abs(self.ball.velocity_x) < 0.1:
            return self.ball.y + self.paddle.height / 2
        
        time_to_reach = distance_to_paddle / abs(self.ball.velocity_x)
        
        # Predict Y position
        predicted_y = self.ball.y + (self.ball.velocity_y * time_to_reach)
        
        # Handle wall bounces in prediction (simple version - one bounce)
        if predicted_y < 0:
            predicted_y = -predicted_y
        elif predicted_y > WINDOW_HEIGHT:
            predicted_y = 2 * WINDOW_HEIGHT - predicted_y
        
        # For hard difficulty, handle multiple bounces more accurately
        if self.difficulty == 'hard':
            bounces = 0
            temp_y = predicted_y
            temp_vel_y = self.ball.velocity_y
            
            # Simulate up to 3 bounces
            while bounces < 3 and (temp_y < 0 or temp_y > WINDOW_HEIGHT):
                if temp_y < 0:
                    temp_y = -temp_y
                    temp_vel_y = abs(temp_vel_y)
                elif temp_y > WINDOW_HEIGHT:
                    temp_y = 2 * WINDOW_HEIGHT - temp_y
                    temp_vel_y = -abs(temp_vel_y)
                bounces += 1
            
            predicted_y = temp_y
        
        # Add difficulty-based prediction error
        error_range = self.config['prediction_error']
        error = random.uniform(-error_range, error_range)
        
        # Clamp to valid screen space
        predicted_y = max(0, min(WINDOW_HEIGHT, predicted_y + error))
        
        return predicted_y
    
    def _move_toward_target(self):
        """Move paddle smoothly toward target position with dead zone"""
        if self.target_y is None:
            self.paddle.stop()
            return
        
        # Calculate distance to target (aim for center of paddle)
        paddle_center = self.paddle.y + self.paddle.height / 2
        distance = self.target_y - paddle_center
        
        # Dead zone - don't move if close enough
        dead_zone = self.config.get('dead_zone', 15)
        if abs(distance) < dead_zone:
            self.paddle.stop()
            return
        
        # Move toward target at difficulty-adjusted speed
        speed = PADDLE_SPEED * self.config['speed_multiplier']
        
        if distance > 0:
            self.paddle.velocity_y = speed
        else:
            self.paddle.velocity_y = -speed
    
    def adjust_difficulty_adaptive(self, player_score: int, ai_score: int):
        """Dynamically adjust difficulty based on score difference
        
        Args:
            player_score: Human player's score
            ai_score: AI's score
        """
        if not self.config.get('adaptive', False):
            return
        
        score_diff = player_score - ai_score
        
        # Player winning by 3+ points - make AI harder
        if score_diff >= 3:
            self.config['speed_multiplier'] = min(1.0, self.config['speed_multiplier'] + 0.05)
            self.config['prediction_error'] = max(10, self.config['prediction_error'] - 5)
            self.config['reaction_time'] = max(0.05, self.config['reaction_time'] - 0.02)
            logger.debug("Increased difficulty (player ahead by %d)", score_diff)
        
        # AI winning by 3+ points - make AI easier
        elif score_diff <= -3:
            self.config['speed_multiplier'] = max(0.5, self.config['speed_multiplier'] - 0.05)
            self.config['prediction_error'] = min(100, self.config['prediction_error'] + 10)
            self.config['reaction_time'] = min(0.5, self.config['reaction_time'] + 0.02)
            logger.debug("Decreased difficulty (AI ahead by %d)", abs(score_diff))
    
    def reset(self):
        """Reset AI state (call when ball resets)"""
        self.target_y = None
        self.reaction_timer = 0.0
        self.update_timer = 0.0
        self.is_reacting = False
        self.paddle.stop()
