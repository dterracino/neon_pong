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
        # Simple approach: Just render pause screen
        # (In a real implementation, you might want to snapshot the previous frame)
        self.renderer.begin_frame()
        
        # Draw pause text
        self.renderer.draw_text("PAUSED", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40, 72, COLOR_YELLOW, centered=True)
        self.renderer.draw_text("Press P or ESC to Resume", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50, 32, COLOR_YELLOW, centered=True)
        
        self.renderer.end_frame()