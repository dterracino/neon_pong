"""
Main menu scene
"""
import logging
import pygame
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.scenes.game_scene import GameScene
from src.entities.enhanced_particles import EnhancedParticleSystem, MotionPattern
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_PINK, COLOR_CYAN, COLOR_YELLOW,
    FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL
)

logger = logging.getLogger(__name__)


class MenuScene(Scene):
    """Main menu scene"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager,
                 screenshot_manager=None):
        logger.debug("Creating menu scene")
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.screenshot_manager = screenshot_manager
        
        self.selected_option = 0
        self.previous_selection = 0
        self.options = [
            "1 Player (Easy)",
            "1 Player (Normal)", 
            "1 Player (Hard)",
            "2 Player",
            "Quit"
        ]
        
        # Create enhanced particle system for menu effects
        self.menu_particles = EnhancedParticleSystem()
        
        # Create continuous glow emitter around selected menu option (will be positioned per frame)
        self.glow_emitter = self.menu_particles.create_continuous_emitter(
            WINDOW_WIDTH // 2, 350,  # Initial position
            COLOR_YELLOW,
            rate=15.0,  # 15 particles per second
            lifetime=0.8,
            speed=30.0,
            spread=360.0,
            motion_pattern=MotionPattern.RADIAL
        )
        
        # Try to start menu music
        # self.audio_manager.play_music('menu_music.ogg')
        logger.debug("Menu scene created with particle effects")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.previous_selection = self.selected_option
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self._on_selection_change()
            elif event.key == pygame.K_DOWN:
                self.previous_selection = self.selected_option
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self._on_selection_change()
            elif event.key == pygame.K_RETURN:
                self._select_option()
    
    def _on_selection_change(self):
        """Called when menu selection changes - emit particles"""
        # Get positions of previous and current selections
        option_y_base = 350
        prev_x = WINDOW_WIDTH // 2
        prev_y = option_y_base + self.previous_selection * 80
        curr_x = WINDOW_WIDTH // 2
        curr_y = option_y_base + self.selected_option * 80
        
        # Emit burst at new selection
        self.menu_particles.emit_burst(
            curr_x, curr_y,
            COLOR_YELLOW,
            count=15,
            lifetime=0.6,
            speed=80.0,
            motion_pattern=MotionPattern.RADIAL
        )
        
        # Emit trail between previous and current
        if abs(self.selected_option - self.previous_selection) == 1:
            self.menu_particles.emit_trail(
                prev_x, prev_y,
                curr_x, curr_y,
                COLOR_CYAN,
                count=10,
                lifetime=0.5
            )
    
    def _select_option(self):
        logger.debug("Selected option %d", self.selected_option)
        if self.selected_option == 0:  # 1 Player (Easy)
            logger.debug("Creating game scene with AI opponent (Easy)")
            game_scene = GameScene(self.scene_manager, self.renderer, self.audio_manager, 
                                  ai_enabled=True, ai_difficulty='easy',
                                  screenshot_manager=self.screenshot_manager)
            logger.debug("Changing to game scene")
            self.scene_manager.change_scene(game_scene)
        elif self.selected_option == 1:  # 1 Player (Normal)
            logger.debug("Creating game scene with AI opponent (Normal)")
            game_scene = GameScene(self.scene_manager, self.renderer, self.audio_manager, 
                                  ai_enabled=True, ai_difficulty='normal',
                                  screenshot_manager=self.screenshot_manager)
            logger.debug("Changing to game scene")
            self.scene_manager.change_scene(game_scene)
        elif self.selected_option == 2:  # 1 Player (Hard)
            logger.debug("Creating game scene with AI opponent (Hard)")
            game_scene = GameScene(self.scene_manager, self.renderer, self.audio_manager, 
                                  ai_enabled=True, ai_difficulty='hard',
                                  screenshot_manager=self.screenshot_manager)
            logger.debug("Changing to game scene")
            self.scene_manager.change_scene(game_scene)
        elif self.selected_option == 3:  # 2 Player
            logger.debug("Creating game scene for 2 players")
            game_scene = GameScene(self.scene_manager, self.renderer, self.audio_manager, 
                                  ai_enabled=False, screenshot_manager=self.screenshot_manager)
            logger.debug("Changing to game scene")
            self.scene_manager.change_scene(game_scene)
        elif self.selected_option == 4:  # Quit
            logger.debug("Clearing scenes (quit)")
            self.scene_manager.clear_scenes()
    
    def update(self, dt: float):
        # Update particle system
        self.menu_particles.update(dt)
        
        # Update glow emitter position to follow selected option
        option_y_base = 350
        selected_y = option_y_base + self.selected_option * 80
        self.glow_emitter.x = WINDOW_WIDTH // 2
        self.glow_emitter.y = selected_y
    
    def render(self):
        self.renderer.begin_frame()
        
        # Render to scene FBO (will get bloom effect)
        self.renderer.scene_fbo.use()
        
        # Draw dust overlay on top of background
        self.renderer.draw_dust_overlay()
        
        # Render menu particles (will get bloom effect)
        self.renderer.render_particles(self.menu_particles)
        
        # Switch to UI FBO for text (crisp, no bloom)
        self.renderer.ui_fbo.use()
        
        # Draw title
        title_y = 150
        self.renderer.draw_text("NEON PONG", WINDOW_WIDTH // 2, title_y, FONT_SIZE_LARGE, COLOR_PINK, centered=True)
        
        # Draw menu options
        option_y = 350
        for i, option in enumerate(self.options):
            color = COLOR_YELLOW if i == self.selected_option else COLOR_CYAN
            y = option_y + i * 80
            self.renderer.draw_text(option, WINDOW_WIDTH // 2, y, FONT_SIZE_MEDIUM, color, centered=True)
        
        # Draw controls
        controls_y = 550
        self.renderer.draw_text("Player 1: W/S", 100, controls_y, FONT_SIZE_SMALL, COLOR_CYAN)
        
        # Show different text based on selected option
        if self.selected_option in [0, 1, 2]:  # 1 Player modes
            self.renderer.draw_text("Player 2: AI", WINDOW_WIDTH - 250, controls_y, FONT_SIZE_SMALL, COLOR_PINK)
        else:  # 2 Player mode or Quit
            self.renderer.draw_text("Player 2: UP/DOWN", WINDOW_WIDTH - 300, controls_y, FONT_SIZE_SMALL, COLOR_PINK)
        
        self.renderer.end_frame()