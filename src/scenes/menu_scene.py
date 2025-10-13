"""
Main menu scene
"""
import pygame
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.scenes.game_scene import GameScene
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_PINK, COLOR_CYAN, COLOR_YELLOW
)


class MenuScene(Scene):
    """Main menu scene"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager):
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        
        self.selected_option = 0
        self.options = ["Start Game", "Quit"]
        
        # Try to start menu music
        # self.audio_manager.play_music('menu_music.ogg')
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._select_option()
    
    def _select_option(self):
        if self.selected_option == 0:  # Start Game
            game_scene = GameScene(self.scene_manager, self.renderer, self.audio_manager)
            self.scene_manager.change_scene(game_scene)
        elif self.selected_option == 1:  # Quit
            self.scene_manager.clear_scenes()
    
    def update(self, dt: float):
        pass
    
    def render(self):
        self.renderer.begin_frame()
        
        # Draw title
        title_y = 150
        self._draw_text("NEON PONG", WINDOW_WIDTH // 2 - 200, title_y, 72, COLOR_PINK)
        
        # Draw menu options
        option_y = 350
        for i, option in enumerate(self.options):
            color = COLOR_YELLOW if i == self.selected_option else COLOR_CYAN
            y = option_y + i * 80
            self._draw_text(option, WINDOW_WIDTH // 2 - 100, y, 48, color)
        
        # Draw controls
        controls_y = 550
        self._draw_text("Player 1: W/S", 100, controls_y, 24, COLOR_CYAN)
        self._draw_text("Player 2: UP/DOWN", WINDOW_WIDTH - 300, controls_y, 24, COLOR_PINK)
        
        self.renderer.end_frame()
    
    def _draw_text(self, text: str, x: float, y: float, size: int, color: tuple):
        """Draw text using pygame (rendered to surface then to OpenGL)"""
        # This is a simplified version - in a real implementation,
        # you'd want to render text to a texture and use shaders
        # For now, we'll draw rectangles as placeholders for text
        
        # Draw a background rectangle for text visibility
        char_width = size * 0.6
        text_width = len(text) * char_width
        self.renderer.draw_rect(x - 5, y - 5, text_width + 10, size + 10, color)