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
    COLOR_PINK, COLOR_CYAN, COLOR_YELLOW,
    FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL
)


class MenuScene(Scene):
    """Main menu scene"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager):
        print("[DEBUG] MenuScene.__init__: Creating menu scene...")
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        
        self.selected_option = 0
        self.options = ["Start Game", "Quit"]
        
        # Try to start menu music
        # self.audio_manager.play_music('menu_music.ogg')
        print("[DEBUG] MenuScene.__init__: Menu scene created")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._select_option()
    
    def _select_option(self):
        print(f"[DEBUG] MenuScene._select_option: Selected option {self.selected_option}")
        if self.selected_option == 0:  # Start Game
            print("[DEBUG] MenuScene._select_option: Creating game scene...")
            game_scene = GameScene(self.scene_manager, self.renderer, self.audio_manager)
            print("[DEBUG] MenuScene._select_option: Changing to game scene...")
            self.scene_manager.change_scene(game_scene)
        elif self.selected_option == 1:  # Quit
            print("[DEBUG] MenuScene._select_option: Clearing scenes (quit)...")
            self.scene_manager.clear_scenes()
    
    def update(self, dt: float):
        pass
    
    def render(self):
        self.renderer.begin_frame()
        
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
        self.renderer.draw_text("Player 2: UP/DOWN", WINDOW_WIDTH - 300, controls_y, FONT_SIZE_SMALL, COLOR_PINK)
        
        self.renderer.end_frame()