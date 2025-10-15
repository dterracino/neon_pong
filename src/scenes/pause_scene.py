"""
Pause menu scene
"""
import pygame
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_YELLOW, FONT_SIZE_LARGE, FONT_SIZE_DEFAULT


class PauseScene(Scene):
    """Pause menu overlay"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager):
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.selected_option = 0
        self.options = ["Resume", "Quit to Menu"]
    
    def on_enter(self):
        self.audio_manager.pause_music()
    
    def on_exit(self):
        self.audio_manager.resume_music()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                # Resume game
                self.scene_manager.pop_scene()
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:  # Resume
                    self.scene_manager.pop_scene()
                elif self.selected_option == 1:  # Quit to Menu
                    # Import here to avoid circular dependency
                    from src.scenes.menu_scene import MenuScene
                    # Pop pause scene, then change game scene to menu scene
                    self.scene_manager.pop_scene()  # Pop pause
                    # Now game scene is active, change it to menu
                    menu_scene = MenuScene(self.scene_manager, self.renderer, self.audio_manager)
                    self.scene_manager.change_scene(menu_scene)
    
    def update(self, dt: float):
        pass
    
    def render(self):
        from src.utils.constants import COLOR_CYAN, FONT_SIZE_MEDIUM
        
        # Simple approach: Just render pause screen
        # (In a real implementation, you might want to snapshot the previous frame)
        self.renderer.begin_frame()
        
        # Draw pause text
        self.renderer.draw_text("PAUSED", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100, FONT_SIZE_LARGE, COLOR_YELLOW, centered=True)
        
        # Draw menu options
        option_y = WINDOW_HEIGHT // 2
        for i, option in enumerate(self.options):
            color = COLOR_YELLOW if i == self.selected_option else COLOR_CYAN
            y = option_y + i * 60
            self.renderer.draw_text(option, WINDOW_WIDTH // 2, y, FONT_SIZE_MEDIUM, color, centered=True)
        
        self.renderer.end_frame()