"""
Pause menu scene
"""
import logging
import pygame
import moderngl
import numpy as np
from typing import Optional
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.utils.screenshot import ScreenshotManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_YELLOW, FONT_SIZE_LARGE, FONT_SIZE_DEFAULT

logger = logging.getLogger(__name__)


class PauseScene(Scene):
    """Pause menu overlay"""
    
    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager, 
                 screenshot_manager: Optional[ScreenshotManager] = None):
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.screenshot_manager = screenshot_manager
        self.selected_option = 0
        self.options = ["Resume", "Quit to Menu"]
        
        # Blurred background texture
        self.blur_texture: Optional[moderngl.Texture] = None
        self.blur_fbo: Optional[moderngl.Framebuffer] = None
        self.temp_fbo: Optional[moderngl.Framebuffer] = None
        
        # Create blurred background from last screenshot
        self._create_blurred_background()
    
    def _create_blurred_background(self):
        """Create a blurred texture from the last screenshot"""
        if not self.screenshot_manager:
            logger.debug("No screenshot manager available, skipping blurred background")
            return
        
        last_screenshot = self.screenshot_manager.get_last_screenshot()
        if not last_screenshot:
            logger.debug("No screenshot available, skipping blurred background")
            return
        
        try:
            # Convert pygame surface to texture
            ctx = self.renderer.ctx
            screenshot_data = pygame.image.tostring(last_screenshot, 'RGBA', True)
            
            # Create texture from screenshot
            source_texture = ctx.texture(last_screenshot.get_size(), 4, screenshot_data)
            source_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            
            # Create framebuffers for blur passes
            self.blur_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4)
            self.blur_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.blur_fbo = ctx.framebuffer(color_attachments=[self.blur_texture])
            
            temp_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4)
            temp_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.temp_fbo = ctx.framebuffer(color_attachments=[temp_texture])
            
            # Load blur shader
            blur_program = self.renderer.shader_manager.load_shader('blur', 'basic.vert', 'bloom_blur.frag')
            if not blur_program:
                logger.warning("Could not load blur shader")
                source_texture.release()
                return
            
            # Apply multiple blur passes for stronger effect
            blur_passes = 3
            for i in range(blur_passes):
                # Horizontal blur pass
                self.temp_fbo.use()
                ctx.clear(0.0, 0.0, 0.0, 1.0)
                
                if i == 0:
                    source_texture.use(0)
                else:
                    self.blur_texture.use(0)
                
                blur_program['tex'] = 0
                blur_program['horizontal'] = True
                blur_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
                self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)
                
                # Vertical blur pass
                self.blur_fbo.use()
                ctx.clear(0.0, 0.0, 0.0, 1.0)
                
                temp_texture.use(0)
                blur_program['tex'] = 0
                blur_program['horizontal'] = False
                blur_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
                self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)
            
            # Clean up
            source_texture.release()
            temp_texture.release()
            self.temp_fbo.release()
            self.temp_fbo = None
            
            logger.debug("Blurred background created successfully")
            
        except Exception as e:
            logger.error("Failed to create blurred background: %s", e)
    
    def on_enter(self):
        # Duck music to 50% volume instead of pausing
        self.audio_manager.duck_music(0.5)
    
    def on_exit(self):
<<<<<<< HEAD
        # Restore music to normal volume
        self.audio_manager.unduck_music()
=======
        self.audio_manager.resume_music()
        # Clean up blur resources
        if self.blur_texture:
            self.blur_texture.release()
            self.blur_texture = None
        if self.blur_fbo:
            self.blur_fbo.release()
            self.blur_fbo = None
>>>>>>> 9ebc79b77bf4f3eeeba98a93c9675350072c582b
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                # Resume game
                self.audio_manager.play_sound('pause')
                self.scene_manager.pop_scene()
            elif event.key == pygame.K_UP:
                self.audio_manager.play_sound('menu-move')
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.audio_manager.play_sound('menu-move')
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.audio_manager.play_sound('menu-select')
                if self.selected_option == 0:  # Resume
                    self.scene_manager.pop_scene()
                elif self.selected_option == 1:  # Quit to Menu
                    # Import here to avoid circular dependency
                    from src.scenes.menu_scene import MenuScene
                    # Pop pause scene, then change game scene to menu scene
                    self.scene_manager.pop_scene()  # Pop pause
                    # Now game scene is active, change it to menu
                    menu_scene = MenuScene(self.scene_manager, self.renderer, self.audio_manager,
                                          self.screenshot_manager)
                    self.scene_manager.change_scene(menu_scene)
    
    def update(self, dt: float):
        pass
    
    def render(self):
        from src.utils.constants import COLOR_CYAN, FONT_SIZE_MEDIUM
        
        self.renderer.begin_frame()
        
        # Draw blurred background if available
        if self.blur_texture:
            ctx = self.renderer.ctx
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            
            # Darken the blur slightly for better text readability
            self.blur_texture.use(0)
            self.renderer.basic_program['tex'] = 0
            self.renderer.basic_program['color'] = (0.5, 0.5, 0.5, 1.0)  # Darken to 50%
            self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)
            
            ctx.disable(moderngl.BLEND)
        
        # Draw pause text
        self.renderer.draw_text("PAUSED", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100, FONT_SIZE_LARGE, COLOR_YELLOW, centered=True)
        
        # Draw menu options
        option_y = WINDOW_HEIGHT // 2
        for i, option in enumerate(self.options):
            color = COLOR_YELLOW if i == self.selected_option else COLOR_CYAN
            y = option_y + i * 60
            self.renderer.draw_text(option, WINDOW_WIDTH // 2, y, FONT_SIZE_MEDIUM, color, centered=True)
        
        self.renderer.end_frame()