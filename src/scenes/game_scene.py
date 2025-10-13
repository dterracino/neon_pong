"""
Main gameplay scene
"""
import pygame
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.entities.paddle import Paddle
from src.entities.ball import Ball
from src.entities.particle import ParticleSystem
from src.scenes.pause_scene import PauseScene
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PADDLE_OFFSET,
    WINNING_SCORE, PARTICLE_COUNT, PARTICLE_LIFETIME,
    COLOR_CYAN, COLOR_PINK, COLOR_YELLOW
)


class GameScene(Scene):
    """Main game scene"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager):
        print("[DEBUG] GameScene.__init__: Creating game scene...")
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        
        # Create entities
        print("[DEBUG] GameScene.__init__: Creating game entities...")
        self.paddle1 = Paddle(PADDLE_OFFSET, WINDOW_HEIGHT // 2 - 50, 1)
        self.paddle2 = Paddle(WINDOW_WIDTH - PADDLE_OFFSET - 15, WINDOW_HEIGHT // 2 - 50, 2)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # Particle system
        self.particles = ParticleSystem()
        
        # Score
        self.score1 = 0
        self.score2 = 0
        
        # Game state
        self.game_over = False
        self.winner = 0
        
        # Try to start game music
        # self.audio_manager.play_music('game_music.ogg')
        print(f"[DEBUG] GameScene.__init__: Game scene created (paddle1: {self.paddle1.x},{self.paddle1.y}, ball: {self.ball.x},{self.ball.y})")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                # Pause game
                pause_scene = PauseScene(self.scene_manager, self.renderer, self.audio_manager)
                self.scene_manager.push_scene(pause_scene)
    
    def update(self, dt: float):
        if self.game_over:
            return
        
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Update paddles
        self.paddle1.handle_input(keys)
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
        
        # Draw scores (using rectangles as placeholder)
        score_y = 50
        self._draw_score(self.score1, WINDOW_WIDTH // 4, score_y, COLOR_CYAN)
        self._draw_score(self.score2, WINDOW_WIDTH * 3 // 4, score_y, COLOR_PINK)
        
        # Draw game over message
        if self.game_over:
            msg_y = WINDOW_HEIGHT // 2 - 50
            color = COLOR_CYAN if self.winner == 1 else COLOR_PINK
            self.renderer.draw_rect(
                WINDOW_WIDTH // 2 - 200,
                msg_y,
                400,
                100,
                color
            )
        
        self.renderer.end_frame()
    
    def _draw_score(self, score: int, x: float, y: float, color: tuple):
        """Draw score as blocks"""
        # Simple visual representation of score
        digit_width = 40
        digit_height = 60
        
        score_str = str(score)
        total_width = len(score_str) * (digit_width + 10)
        start_x = x - total_width // 2
        
        for i, digit in enumerate(score_str):
            digit_x = start_x + i * (digit_width + 10)
            self.renderer.draw_rect(digit_x, y, digit_width, digit_height, color)