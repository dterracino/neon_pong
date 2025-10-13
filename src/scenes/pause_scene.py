"""
Pause menu scene
"""
import pygame
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_YELLOW


class PauseScene(Scene):
    """Pause menu overlay"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager):
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
    
    def on_enter(self):
        self.audio_manager.pause_music()
    
    def on_exit(self):
        self.audio_manager.resume_music()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                # Resume game
                self.scene_manager.pop_scene()
    
    def update(self, dt: float):
        pass
    
    def render(self):
        # Render previous scene first (game scene)
        if len(self.scene_manager.scenes) > 1:
            self.scene_manager.scenes[-2].render()
        
        # Draw semi-transparent overlay
        self.renderer.draw_rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (0, 0, 0, 0.7))
        
        # Draw pause text
        self.renderer.draw_rect(
            WINDOW_WIDTH // 2 - 150,
            WINDOW_HEIGHT // 2 - 50,
            300,
            100,
            COLOR_YELLOW
        )