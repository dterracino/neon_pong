"""
Main gameplay scene
"""
import logging
import math
import pygame
import random
import time
from typing import Optional
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer, TextEffects
from src.managers.audio_manager import AudioManager
from src.entities.paddle import Paddle
from src.entities.ball import Ball
from src.entities.particle import ParticleSystem
from src.entities.enhanced_particles import EnhancedParticleSystem
from src.scenes.pause_scene import PauseScene
from src.ai.pong_ai import PongAI
from src.utils.game_time import GameTime
from src.utils.impact_effects import ImpactEffectsSystem
from src.utils.ai_indicator import AIThinkingIndicator
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PADDLE_OFFSET,
    WINNING_SCORE, PARTICLE_COUNT, PARTICLE_LIFETIME,
    BALL_MAX_SPEED,
    COLOR_CYAN, COLOR_PINK, COLOR_YELLOW, COLOR_PURPLE, COLOR_MINT,
    FONT_SIZE_LARGE, FONT_SIZE_DEFAULT
)

logger = logging.getLogger(__name__)


class GameScene(Scene):
    """Main game scene"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager, 
                 ai_enabled: bool = False, ai_difficulty: str = 'normal',
                 screenshot_manager=None, achievement_manager=None, asset_manager=None):
        logger.debug("Creating game scene")
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.screenshot_manager = screenshot_manager
        self.achievement_manager = achievement_manager
        self.asset_manager = asset_manager
        self.ai_enabled = ai_enabled
        self.ai_difficulty = ai_difficulty
        
        # Create entities
        logger.debug("Creating game entities")
        self.paddle1 = Paddle(PADDLE_OFFSET, WINDOW_HEIGHT // 2 - 50, 1)
        self.paddle2 = Paddle(WINDOW_WIDTH - PADDLE_OFFSET - 15, WINDOW_HEIGHT // 2 - 50, 2)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # Load sprites if asset_manager is available
        if self.asset_manager:
            # Try to load paddle sprites
            paddle1_sprite = self.asset_manager.get_image('paddle1')
            if paddle1_sprite:
                self.paddle1.set_sprite(paddle1_sprite)
                logger.debug("Set sprite for paddle 1")
            
            paddle2_sprite = self.asset_manager.get_image('paddle2')
            if paddle2_sprite:
                self.paddle2.set_sprite(paddle2_sprite)
                logger.debug("Set sprite for paddle 2")
            
            # Try to load ball sprite
            ball_sprite = self.asset_manager.get_image('ball')
            if ball_sprite:
                self.ball.set_sprite(ball_sprite)
                logger.debug("Set sprite for ball")
        
        # Initialize AI if enabled
        self.ai: Optional[PongAI] = None
        if self.ai_enabled:
            self.ai = PongAI(self.paddle2, self.ball, ai_difficulty)
            logger.debug("AI opponent initialized with difficulty '%s'", ai_difficulty)
        
        # Particle systems
        self.particles = ParticleSystem()  # For ball impacts
        self.fireworks = EnhancedParticleSystem()  # For victory celebration
        
        # Impact effects system
        self.impact_effects = ImpactEffectsSystem()
        
        # AI thinking indicator - style varies by difficulty level
        indicator_style = self._get_ai_indicator_style(ai_difficulty)
        is_persistent = (ai_difficulty == 'hard')  # Hard mode is always analyzing (adaptive)
        self.ai_indicator = AIThinkingIndicator(style=indicator_style, persistent=is_persistent)
        logger.debug("AI indicator style: '%s' (persistent=%s) for difficulty '%s'", 
                    indicator_style, is_persistent, ai_difficulty)
        
        # Fireworks state
        self.fireworks_timer = 0.0
        self.next_firework_time = 0.0
        
        # Game time tracking
        self.game_time = GameTime()
        
        # Score
        self.score1 = 0
        self.score2 = 0
        
        # Score animation state
        self.score1_scale = 1.0
        self.score1_anim_timer = 0.0
        self.score2_scale = 1.0
        self.score2_anim_timer = 0.0
        
        # Game state
        self.game_over = False
        self.winner = 0

        # Achievement tracking
        self._game_start_time: float = time.monotonic()
        self._consecutive_hits: int = 0
        self._consecutive_scored_by: int = 0  # which player scored last — local state only

        # Reset streak counters at the start of every game
        if self.achievement_manager:
            self.achievement_manager.reset_streaks()
        
        # Try to start game music
        self.audio_manager.play_music('game_music.ogg')
        logger.debug("Game scene created (paddle1: %.1f,%.1f, ball: %.1f,%.1f, ai_enabled: %s)", 
                    self.paddle1.x, self.paddle1.y, self.ball.x, self.ball.y, self.ai_enabled)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                # Pause game - pass screenshot manager for blurred background
                self.audio_manager.play_sound('pause')
                pause_scene = PauseScene(self.scene_manager, self.renderer, self.audio_manager, 
                                        self.screenshot_manager, self.achievement_manager)
                self.scene_manager.push_scene(pause_scene)
    
    def update(self, dt: float):
        # Update game time
        self.game_time.update(dt)
        
        if self.game_over:
            # Update fireworks during victory screen
            self.fireworks.update(dt)
            self.fireworks_timer += dt
            
            # Launch new fireworks periodically
            if self.fireworks_timer >= self.next_firework_time:
                self._launch_firework()
                # Random interval between fireworks (0.3 to 0.7 seconds)
                self.next_firework_time = self.fireworks_timer + random.uniform(0.3, 0.7)
            
            return
        
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Update paddles
        self.paddle1.handle_input(keys)
        
        if self.ai_enabled and self.ai:
            # AI controls paddle2
            self.ai.update(dt)
        else:
            # Human player controls paddle2
            self.paddle2.handle_input(keys)
        
        self.paddle1.update(dt)
        self.paddle2.update(dt)
        
        # Update ball
        collision = self.ball.update(dt)
        
        # Update impact effects
        self.impact_effects.update(dt)
        
        # Update AI thinking indicator
        if self.ai_enabled and self.ai:
            # Set indicator active when AI is thinking (not reacting)
            self.ai_indicator.set_active(not self.ai.is_reacting)
            self.ai_indicator.update(dt)
        
        # Update score animations
        if self.score1_anim_timer > 0:
            self.score1_anim_timer -= dt
            # Elastic ease out: scale from 1.5 to 1.0
            progress = 1.0 - (self.score1_anim_timer / 0.3)  # 0.3s animation
            self.score1_scale = 1.0 + 0.5 * (1.0 - progress) ** 2
        else:
            self.score1_scale = 1.0
        
        if self.score2_anim_timer > 0:
            self.score2_anim_timer -= dt
            progress = 1.0 - (self.score2_anim_timer / 0.3)
            self.score2_scale = 1.0 + 0.5 * (1.0 - progress) ** 2
        else:
            self.score2_scale = 1.0
        
        # Handle wall collision
        if collision == 'wall':
            self.audio_manager.play_sound('wall_hit')
            ball_center_x = self.ball.x + self.ball.size / 2
            ball_center_y = self.ball.y + self.ball.size / 2
            
            # Particles
            self.particles.emit(
                ball_center_x, ball_center_y,
                COLOR_YELLOW,
                PARTICLE_COUNT,
                PARTICLE_LIFETIME
            )
            
            # Screen shake (light)
            self.renderer.add_screen_shake(3.0, 0.15)
            
            # Impact flash
            self.impact_effects.add_flash(ball_center_x, ball_center_y, COLOR_YELLOW, size=20, duration=0.1)
        
        # Check paddle collisions
        if self.ball.bounds.intersects(self.paddle1.bounds):
            self.ball.last_hit_by = 1  # Track player 1 hit
            self.ball.bounce_paddle(self.paddle1)
            self.paddle1.on_hit()
            self.audio_manager.play_sound('paddle_hit', pitch_variation=True)
            
            ball_center_x = self.ball.x + self.ball.size / 2
            ball_center_y = self.ball.y + self.ball.size / 2
            
            # Particles
            self.particles.emit(
                ball_center_x, ball_center_y,
                COLOR_CYAN,
                PARTICLE_COUNT,
                PARTICLE_LIFETIME
            )
            
            # Screen shake (based on ball speed)
            shake_intensity = min(self.ball.speed / 100.0, 12.0)
            self.renderer.add_screen_shake(shake_intensity, 0.2)
            
            # Impact ring
            self.impact_effects.add_ring(ball_center_x, ball_center_y, COLOR_CYAN, max_radius=40, duration=0.3)
            
            self._on_paddle_hit()
        
        if self.ball.bounds.intersects(self.paddle2.bounds):
            self.ball.last_hit_by = 2  # Track player 2 hit
            self.ball.bounce_paddle(self.paddle2)
            self.paddle2.on_hit()
            self.audio_manager.play_sound('paddle_hit', pitch_variation=True)
            
            ball_center_x = self.ball.x + self.ball.size / 2
            ball_center_y = self.ball.y + self.ball.size / 2
            
            # Particles
            self.particles.emit(
                ball_center_x, ball_center_y,
                COLOR_PINK,
                PARTICLE_COUNT,
                PARTICLE_LIFETIME
            )
            
            # Screen shake (based on ball speed)
            shake_intensity = min(self.ball.speed / 100.0, 12.0)
            self.renderer.add_screen_shake(shake_intensity, 0.2)
            
            # Impact ring
            self.impact_effects.add_ring(ball_center_x, ball_center_y, COLOR_PINK, max_radius=40, duration=0.3)
            
            self._on_paddle_hit()
        
        # Check scoring
        scorer = self.ball.is_out_of_bounds()
        if scorer:
            # Determine scoring side position for effects
            if scorer == 1:
                # Player 1 scored (ball went out on right)
                score_x = WINDOW_WIDTH - 50
                score_y = self.ball.y + self.ball.size / 2
                score_color = COLOR_CYAN
                self.score1 += 1
                # Trigger score animation
                self.score1_scale = 1.5
                self.score1_anim_timer = 0.3
                
                # In 1P mode, player scored - add particles
                # In 2P mode, player 1 scored - add particles
                self.particles.emit(
                    score_x, score_y,
                    score_color,
                    count=30,
                    lifetime=1.0
                )
                self.impact_effects.add_ring(score_x, score_y, score_color, max_radius=80, duration=0.6)
                
            else:
                # Player 2/AI scored (ball went out on left)
                score_x = 50
                score_y = self.ball.y + self.ball.size / 2
                score_color = COLOR_PINK
                self.score2 += 1
                # Trigger score animation
                self.score2_scale = 1.5
                self.score2_anim_timer = 0.3
                
                if self.ai_enabled:
                    # 1P mode: AI scored, add dramatic screen shake instead of particles
                    self.renderer.add_screen_shake(15.0, 0.4)
                else:
                    # 2P mode: player 2 scored, add particles
                    self.particles.emit(
                        score_x, score_y,
                        score_color,
                        count=30,
                        lifetime=1.0
                    )
                    self.impact_effects.add_ring(score_x, score_y, score_color, max_radius=80, duration=0.6)

            # Achievement: first point ever scored
            self._check_score_achievements(scorer)

            # Play contextual score sound based on game mode
            if self.ai_enabled:
                # 1P mode: Score sound for player scoring, miss sound for AI scoring
                if scorer == 1:
                    self.audio_manager.play_sound('score')  # Player scored!
                else:
                    self.audio_manager.play_sound('ball-miss')  # AI scored :(
            else:
                # 2P mode: Always use score sound (someone scored)
                self.audio_manager.play_sound('score')
            
            self.ball.reset()
            self.particles.clear()

            # Reset consecutive rally counter on any point scored
            self._consecutive_hits = 0
            if self.achievement_manager:
                self.achievement_manager.reset_stat('consecutive_hits')
            
            # Reset AI state when ball resets
            if self.ai:
                self.ai.reset()
            
            # Adjust AI difficulty adaptively if enabled
            if self.ai:
                self.ai.adjust_difficulty_adaptive(self.score1, self.score2)
            
            # Check win condition
            if self.score1 >= WINNING_SCORE:
                self.game_over = True
                self.winner = 1
                self.audio_manager.play_sound('win')  # Player won the game!
                self._check_win_achievements(winner=1)
            elif self.score2 >= WINNING_SCORE:
                self.game_over = True
                self.winner = 2
                # Play lose sound if AI won in 1P mode, win sound in 2P mode
                if self.ai_enabled:
                    self.audio_manager.play_sound('lose')  # AI won :(
                else:
                    self.audio_manager.play_sound('win')  # Player 2 won!
                self._check_win_achievements(winner=2)
        
        # Update particles
        self.particles.update(dt)
    
    def _get_ai_indicator_style(self, difficulty: str) -> str:
        """
        Get the appropriate thinking indicator style for AI difficulty level.
        
        Args:
            difficulty: AI difficulty ('easy', 'normal', 'hard')
            
        Returns:
            Indicator style name
        """
        difficulty_styles = {
            'easy': 'spinner',      # Simple circular animation for basic AI
            'normal': 'pulse_ring', # Active scanning for moderate AI
            'hard': 'brainwave'     # Complex neural activity for adaptive AI
        }
        return difficulty_styles.get(difficulty, 'spinner')
    
    def _launch_firework(self):
        """Launch a firework at a random location"""
        # Random position in upper 2/3 of screen
        x = random.uniform(WINDOW_WIDTH * 0.2, WINDOW_WIDTH * 0.8)
        y = random.uniform(WINDOW_HEIGHT * 0.2, WINDOW_HEIGHT * 0.6)
        
        # Choose random neon color for this firework
        colors = [COLOR_CYAN, COLOR_PINK, COLOR_YELLOW, COLOR_PURPLE, COLOR_MINT]
        color = random.choice(colors)
        
        # Launch the firework
        self.fireworks.emit_firework(x, y, color, count=random.randint(40, 60), speed=random.uniform(150, 250))

    # ------------------------------------------------------------------ #
    # Achievement helper methods                                          #
    # ------------------------------------------------------------------ #

    def _on_paddle_hit(self):
        """Called whenever a paddle-ball collision occurs."""
        if not self.achievement_manager:
            return
        self._consecutive_hits += 1
        self.achievement_manager.increment('consecutive_hits')

        # speed_demon: report current ball speed; manager checks THRESHOLD achievements
        self.achievement_manager.observe('ball_speed', self.ball.speed)

    def _check_score_achievements(self, scorer: int):
        """Called immediately after a point is scored."""
        if not self.achievement_manager:
            return

        am = self.achievement_manager

        # Fire point_scored event — manager resolves all MILESTONE achievements
        am.trigger('point_scored', {'scorer': scorer})

        # Lifetime totals
        am.increment('total_points')

        # Hat Trick: STREAK achievement — increment when same player scores again, reset on change
        if scorer == self._consecutive_scored_by:
            am.increment('consecutive_scored')
        else:
            self._consecutive_scored_by = scorer
            am.reset_stat('consecutive_scored')
            am.increment('consecutive_scored')  # this point starts the new streak

    def _check_win_achievements(self, winner: int):
        """Called when the game ends.  winner is 1 or 2."""
        if not self.achievement_manager:
            return

        am = self.achievement_manager
        elapsed = time.monotonic() - self._game_start_time
        opponent_score = self.score2 if winner == 1 else self.score1

        # Fire game_won event — manager resolves all MILESTONE achievements
        am.trigger('game_won', {
            'winner':         winner,
            'opponent_score': opponent_score,
            'ai_enabled':     self.ai_enabled,
            'ai_difficulty':  self.ai_difficulty,
            'elapsed':        elapsed,
        })

        # Increment lifetime accumulators (ACCUMULATOR type, not MILESTONE)
        am.increment('wins')
        am.increment('total_games')

        # SESSION_STREAK: track consecutive AI wins within this session
        if self.ai_enabled:
            if winner == 2:
                am.increment('consecutive_ai_wins')
            else:
                am.reset_stat('consecutive_ai_wins')

    def render(self):
        self.renderer.begin_frame()

        # Draw dust overlay (rendered into scene FBO, gets bloom)
        self.renderer.draw_dust_overlay()

        # Draw animated center line with alternating neon colors
        line_segments = 20
        segment_height = WINDOW_HEIGHT / (line_segments * 2)
        for i in range(line_segments):
            y = i * segment_height * 2
            
            # Alternate between cyan and pink
            color_index = (i + int(self.game_time.elapsed * 2)) % 2
            base_color = COLOR_CYAN if color_index == 0 else COLOR_PINK
            
            # Pulsing alpha for shimmer effect
            pulse = 0.6 + 0.4 * math.sin(self.game_time.elapsed * 3 + i * 0.3)
            
            # Use bright colors (will trigger bloom effect)
            color = (base_color[0] * pulse, base_color[1] * pulse, base_color[2] * pulse, 0.9)
            
            self.renderer.draw_rect(
                WINDOW_WIDTH // 2 - 3,
                y,
                6,
                segment_height,
                color
            )
        
        # Draw paddles
        if self.paddle1.sprite:
            self.renderer.draw_sprite(
                self.paddle1.sprite,
                self.paddle1.x,
                self.paddle1.y,
                self.paddle1.width,
                self.paddle1.height,
                self.paddle1.get_color()
            )
        else:
            self.renderer.draw_rect(
                self.paddle1.x,
                self.paddle1.y,
                self.paddle1.width,
                self.paddle1.height,
                self.paddle1.get_color()
            )
        
        if self.paddle2.sprite:
            self.renderer.draw_sprite(
                self.paddle2.sprite,
                self.paddle2.x,
                self.paddle2.y,
                self.paddle2.width,
                self.paddle2.height,
                self.paddle2.get_color()
            )
        else:
            self.renderer.draw_rect(
                self.paddle2.x,
                self.paddle2.y,
                self.paddle2.width,
                self.paddle2.height,
                self.paddle2.get_color()
            )
        
        # Draw ball trail with dynamic color based on who last hit it
        for i, (x, y) in enumerate(self.ball.trail_positions):
            # Calculate alpha based on position in trail
            alpha = (i + 1) / len(self.ball.trail_positions) * 0.5
            
            # Get color from ball (interpolates based on last_hit_by and speed)
            color = self.ball.get_trail_color(alpha)
            
            # Size grows along trail
            size = self.ball.size * (i + 1) / len(self.ball.trail_positions)
            self.renderer.draw_circle(x, y, size / 2, color)
        
        # Draw ball
        if self.ball.sprite:
            self.renderer.draw_sprite(
                self.ball.sprite,
                self.ball.x,
                self.ball.y,
                self.ball.size,
                self.ball.size,
                self.ball.color
            )
        else:
            self.renderer.draw_circle(
                self.ball.x + self.ball.size / 2,
                self.ball.y + self.ball.size / 2,
                self.ball.size / 2,
                self.ball.color
            )
        
        # Draw particles
        for particle in self.particles.particles:
            alpha = particle.get_alpha()
            color = (*particle.color[:3], alpha)
            self.renderer.draw_circle(particle.x, particle.y, particle.size / 2, color)
        
        # Draw impact effects (rings and flashes)
        self.impact_effects.render(self.renderer)
        
        # Draw fireworks particles
        if self.fireworks:
            self.renderer.render_particles(self.fireworks)
        
        # Draw AI thinking indicator (minimum display time ensures visibility)
        if self.ai_enabled and self.ai_indicator.is_active:
            indicator_x = self.paddle2.x + self.paddle2.width / 2
            indicator_y = self.paddle2.y - 20
            
            # Apply intensity to color (persistent mode uses variable intensity)
            base_color = COLOR_YELLOW
            indicator_color = (*base_color[:3], base_color[3] * self.ai_indicator.intensity)
            
            if self.ai_indicator.style == "spinner":
                # Draw spinner particles
                particles = self.ai_indicator.get_spinner_particles(
                    indicator_x, indicator_y, indicator_color
                )
                for x, y, size, color in particles:
                    self.renderer.draw_circle(x, y, size, color)
            
            elif self.ai_indicator.style == "brainwave":
                # Draw brainwave line
                points = self.ai_indicator.get_brainwave_points(
                    indicator_x, indicator_y, indicator_color
                )
                # Draw line segments connecting points
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    # Draw small circles to form a line
                    steps = 3
                    for step in range(steps + 1):
                        t = step / steps
                        x = x1 + (x2 - x1) * t
                        y = y1 + (y2 - y1) * t
                        self.renderer.draw_circle(x, y, 1.5, indicator_color)
            
            elif self.ai_indicator.style == "pulse_ring":
                # Draw pulsing rings
                rings = self.ai_indicator.get_pulse_rings(
                    indicator_x, indicator_y, indicator_color
                )
                for x, y, radius, alpha in rings:
                    ring_color = (*indicator_color[:3], alpha * self.ai_indicator.intensity)
                    # Draw ring as small circles around circumference
                    num_points = 16
                    for i in range(num_points):
                        angle = (i / num_points) * math.pi * 2
                        px = x + math.cos(angle) * radius
                        py = y + math.sin(angle) * radius
                        self.renderer.draw_circle(px, py, 1.5, ring_color)
        
        # Draw scores with animation
        score_y = 50
        score_effects = TextEffects(
            stroke_width=3.0,  # Surface-level outline (no atlas artifacts)
            stroke_color=(0.0, 0.0, 0.0, 1.0)
        )
        
        # Apply scale to font size for animation
        score1_size = int(FONT_SIZE_LARGE * self.score1_scale)
        score2_size = int(FONT_SIZE_LARGE * self.score2_scale)
        
        self.renderer.draw_text(str(self.score1), WINDOW_WIDTH // 4, score_y, score1_size, COLOR_CYAN, centered=True, effects=score_effects)
        self.renderer.draw_text(str(self.score2), WINDOW_WIDTH * 3 // 4, score_y, score2_size, COLOR_PINK, centered=True, effects=score_effects)
        
        # Draw game over message
        if self.game_over:
            msg_y = WINDOW_HEIGHT // 2 - 50
            color = COLOR_CYAN if self.winner == 1 else COLOR_PINK
            winner_text = f"PLAYER {self.winner} WINS!"
            self.renderer.draw_text(winner_text, WINDOW_WIDTH // 2, msg_y, FONT_SIZE_LARGE, color, centered=True)
            self.renderer.draw_text("Press ESC for Menu", WINDOW_WIDTH // 2, msg_y + 100, FONT_SIZE_DEFAULT, COLOR_YELLOW, centered=True)
        
        self.renderer.end_frame()