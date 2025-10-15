"""
Main gameplay scene
"""
import logging
import pygame
import random
from typing import Optional
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.entities.paddle import Paddle
from src.entities.ball import Ball
from src.entities.particle import ParticleSystem
from src.entities.enhanced_particles import EnhancedParticleSystem
from src.scenes.pause_scene import PauseScene
from src.ai.pong_ai import PongAI
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PADDLE_OFFSET,
    WINNING_SCORE, PARTICLE_COUNT, PARTICLE_LIFETIME,
    COLOR_CYAN, COLOR_PINK, COLOR_YELLOW, COLOR_PURPLE, COLOR_MINT,
    FONT_SIZE_LARGE, FONT_SIZE_DEFAULT
)

logger = logging.getLogger(__name__)


class GameScene(Scene):
    """Main game scene"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager, 
                 ai_enabled: bool = False, ai_difficulty: str = 'normal'):
        logger.debug("Creating game scene")
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.ai_enabled = ai_enabled
        self.ai_difficulty = ai_difficulty
        
        # Create entities
        logger.debug("Creating game entities")
        self.paddle1 = Paddle(PADDLE_OFFSET, WINDOW_HEIGHT // 2 - 50, 1)
        self.paddle2 = Paddle(WINDOW_WIDTH - PADDLE_OFFSET - 15, WINDOW_HEIGHT // 2 - 50, 2)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # Initialize AI if enabled
        self.ai: Optional[PongAI] = None
        if self.ai_enabled:
            self.ai = PongAI(self.paddle2, self.ball, ai_difficulty)
            logger.debug("AI opponent initialized with difficulty '%s'", ai_difficulty)
        
        # Particle systems
        self.particles = ParticleSystem()  # For ball impacts
        self.fireworks = EnhancedParticleSystem()  # For victory celebration
        
        # Fireworks state
        self.fireworks_timer = 0.0
        self.next_firework_time = 0.0
        
        # Score
        self.score1 = 0
        self.score2 = 0
        
        # Game state
        self.game_over = False
        self.winner = 0
        
        # Try to start game music
        # self.audio_manager.play_music('game_music.ogg')
        logger.debug("Game scene created (paddle1: %.1f,%.1f, ball: %.1f,%.1f, ai_enabled: %s)", 
                    self.paddle1.x, self.paddle1.y, self.ball.x, self.ball.y, self.ai_enabled)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                # Pause game
                pause_scene = PauseScene(self.scene_manager, self.renderer, self.audio_manager)
                self.scene_manager.push_scene(pause_scene)
    
    def update(self, dt: float):
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
        
        # Handle wall collision
        if collision == 'wall':
            self.audio_manager.play_sound('wall_hit')
            self.particles.emit(
                self.ball.x + self.ball.size / 2,
                self.ball.y + self.ball.size / 2,
                COLOR_YELLOW,
                PARTICLE_COUNT,
                PARTICLE_LIFETIME
            )
        
        # Check paddle collisions
        if self.ball.bounds.intersects(self.paddle1.bounds):
            self.ball.bounce_paddle(self.paddle1)
            self.paddle1.on_hit()
            self.audio_manager.play_sound('paddle_hit', pitch_variation=True)
            self.particles.emit(
                self.ball.x + self.ball.size / 2,
                self.ball.y + self.ball.size / 2,
                COLOR_CYAN,
                PARTICLE_COUNT,
                PARTICLE_LIFETIME
            )
        
        if self.ball.bounds.intersects(self.paddle2.bounds):
            self.ball.bounce_paddle(self.paddle2)
            self.paddle2.on_hit()
            self.audio_manager.play_sound('paddle_hit', pitch_variation=True)
            self.particles.emit(
                self.ball.x + self.ball.size / 2,
                self.ball.y + self.ball.size / 2,
                COLOR_PINK,
                PARTICLE_COUNT,
                PARTICLE_LIFETIME
            )
        
        # Check scoring
        scorer = self.ball.is_out_of_bounds()
        if scorer:
            if scorer == 1:
                self.score1 += 1
            else:
                self.score2 += 1
            
            self.audio_manager.play_sound('score')
            self.ball.reset()
            self.particles.clear()
            
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
                self.audio_manager.play_sound('win')
            elif self.score2 >= WINNING_SCORE:
                self.game_over = True
                self.winner = 2
                self.audio_manager.play_sound('win')
        
        # Update particles
        self.particles.update(dt)
    
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
    
    def render(self):
        self.renderer.begin_frame()
        
        # Draw center line
        line_segments = 20
        segment_height = WINDOW_HEIGHT / (line_segments * 2)
        for i in range(line_segments):
            y = i * segment_height * 2
            self.renderer.draw_rect(
                WINDOW_WIDTH // 2 - 2,
                y,
                4,
                segment_height,
                (0.5, 0.5, 0.5, 0.5)
            )
        
        # Draw paddles
        self.renderer.draw_rect(
            self.paddle1.x,
            self.paddle1.y,
            self.paddle1.width,
            self.paddle1.height,
            self.paddle1.get_color()
        )
        
        self.renderer.draw_rect(
            self.paddle2.x,
            self.paddle2.y,
            self.paddle2.width,
            self.paddle2.height,
            self.paddle2.get_color()
        )
        
        # Draw ball trail
        for i, (x, y) in enumerate(self.ball.trail_positions):
            alpha = (i + 1) / len(self.ball.trail_positions) * 0.5
            color = (*self.ball.color[:3], alpha)
            size = self.ball.size * (i + 1) / len(self.ball.trail_positions)
            self.renderer.draw_circle(x, y, size / 2, color)
        
        # Draw ball
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
        
        # Draw fireworks particles
        if self.fireworks:
            self.renderer.render_particles(self.fireworks)
        
        # Draw AI thinking indicator (if AI is in reaction delay)
        if self.ai and not self.ai.is_reacting:
            # Pulsing indicator above AI paddle during reaction delay
            import math
            pulse = 0.5 + 0.5 * math.sin(self.ai.reaction_timer * 10.0)
            indicator_size = 4 + pulse * 3
            indicator_alpha = 0.6 + pulse * 0.4
            indicator_color = (*COLOR_YELLOW[:3], indicator_alpha)
            
            self.renderer.draw_circle(
                self.paddle2.x + self.paddle2.width / 2,
                self.paddle2.y - 15,
                indicator_size,
                indicator_color
            )
        
        # Draw scores
        score_y = 50
        self.renderer.draw_text(str(self.score1), WINDOW_WIDTH // 4, score_y, FONT_SIZE_LARGE, COLOR_CYAN, centered=True)
        self.renderer.draw_text(str(self.score2), WINDOW_WIDTH * 3 // 4, score_y, FONT_SIZE_LARGE, COLOR_PINK, centered=True)
        
        # Draw game over message
        if self.game_over:
            msg_y = WINDOW_HEIGHT // 2 - 50
            color = COLOR_CYAN if self.winner == 1 else COLOR_PINK
            winner_text = f"PLAYER {self.winner} WINS!"
            self.renderer.draw_text(winner_text, WINDOW_WIDTH // 2, msg_y, FONT_SIZE_LARGE, color, centered=True)
            self.renderer.draw_text("Press ESC for Menu", WINDOW_WIDTH // 2, msg_y + 100, FONT_SIZE_DEFAULT, COLOR_YELLOW, centered=True)
        
        self.renderer.end_frame()