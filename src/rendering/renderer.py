"""
ModernGL renderer for game graphics
"""
import moderngl
import numpy as np
import pygame
from typing import Tuple, Dict, Optional
from src.managers.shader_manager import ShaderManager
from src.rendering.post_process import PostProcessor
from src.managers.asset_manager import AssetManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT


class Renderer:
    """Handles all ModernGL rendering"""
    
    def __init__(self, ctx: moderngl.Context, shader_manager: ShaderManager):
        print("[DEBUG] Renderer.__init__: Initializing renderer...")
        self.ctx = ctx
        self.shader_manager = shader_manager
        
        # Load basic shader
        print("[DEBUG] Renderer.__init__: Loading basic shader...")
        self.basic_program = shader_manager.load_shader('basic', 'basic.vert', 'basic.frag')
        if self.basic_program:
            print(f"[DEBUG] Renderer.__init__: Basic shader loaded successfully")
        else:
            print(f"[ERROR] Renderer.__init__: Failed to load basic shader!")
        
        # Create post processor
        print("[DEBUG] Renderer.__init__: Creating post processor...")
        self.post_processor = PostProcessor(ctx, shader_manager)
        
        # Create vertex buffer for a quad
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        
        self.quad_vbo = ctx.buffer(vertices.tobytes())
        self.quad_vao = ctx.simple_vertex_array(self.basic_program, self.quad_vbo, 'in_position')  # type: ignore[arg-type]
        print("[DEBUG] Renderer.__init__: Quad VAO created")
        
        # Create a white 1x1 texture for solid color rendering
        WHITE_PIXEL = np.array([255, 255, 255, 255], dtype='u1')
        self.white_texture = ctx.texture((1, 1), 4, WHITE_PIXEL.tobytes())
        print("[DEBUG] Renderer.__init__: White texture created")
        
        # Create framebuffer for scene rendering
        print(f"[DEBUG] Renderer.__init__: Creating scene framebuffer ({WINDOW_WIDTH}x{WINDOW_HEIGHT})...")
        self.scene_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.scene_fbo = ctx.framebuffer(color_attachments=[self.scene_texture])
        
        # Initialize asset manager for fonts
        self.asset_manager = AssetManager()
        
        # Text texture cache
        self.text_texture_cache: Dict[tuple, moderngl.Texture] = {}
        
        # UI overlay texture for text (rendered after bloom)
        self.ui_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.ui_fbo = ctx.framebuffer(color_attachments=[self.ui_texture])
        
        print("[DEBUG] Renderer.__init__: Renderer initialization complete!")
        
    def begin_frame(self):
        """Begin rendering a frame"""
        # Render to scene framebuffer
        self.scene_fbo.use()
        self.ctx.clear(0.05, 0.02, 0.15, 1.0)  # Dark purple background
        
        # Clear UI overlay
        self.ui_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)  # Transparent
        
        # Switch back to scene framebuffer for main rendering
        self.scene_fbo.use()
    
    def end_frame(self):
        """End rendering and apply post-processing"""
        # Apply bloom post-processing to scene
        final_texture = self.post_processor.apply_bloom(self.scene_texture)
        
        # Render to screen
        self.ctx.screen.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Draw bloomed scene to screen
        final_texture.use(0)
        if self.basic_program and 'tex' in self.basic_program:
            self.basic_program['tex'].value = 0
            # Set color to white to render the texture as-is
            if 'color' in self.basic_program:
                self.basic_program['color'].value = (1.0, 1.0, 1.0, 1.0)
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)
        else:
            print("[ERROR] Renderer.end_frame: Cannot render - basic_program not loaded or 'tex' uniform missing!")
            return
        
        # Draw UI overlay (text) on top, with alpha blending
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        self.ui_texture.use(0)
        if self.basic_program and 'tex' in self.basic_program:
            self.basic_program['tex'].value = 0
            if 'color' in self.basic_program:
                self.basic_program['color'].value = (1.0, 1.0, 1.0, 1.0)
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)
        
        self.ctx.disable(moderngl.BLEND)
    
    def draw_rect(self, x: float, y: float, width: float, height: float, color: Tuple[float, float, float, float]):
        """Draw a filled rectangle"""
        if not self.basic_program:
            print("[ERROR] Renderer.draw_rect: Cannot draw - basic_program not loaded!")
            return
        
        # Convert screen coordinates to NDC
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_width = (width / WINDOW_WIDTH) * 2
        ndc_height = (height / WINDOW_HEIGHT) * 2
        
        # Create vertices for rectangle
        vertices = np.array([
            ndc_x, ndc_y - ndc_height,
            ndc_x + ndc_width, ndc_y - ndc_height,
            ndc_x, ndc_y,
            ndc_x + ndc_width, ndc_y,
        ], dtype='f4')
        
        # Create temporary VBO and VAO
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(self.basic_program, vbo, 'in_position')
        
        # Bind white texture and set color uniform
        self.white_texture.use(0)
        if self.basic_program and 'tex' in self.basic_program:
            self.basic_program['tex'].value = 0  # type: ignore[union-attr]
        if self.basic_program and 'color' in self.basic_program:
            self.basic_program['color'].value = color  # type: ignore[union-attr]
        
        # Draw
        vao.render(moderngl.TRIANGLE_STRIP)
        
        # Cleanup
        vao.release()
        vbo.release()
    
    def draw_circle(self, x: float, y: float, radius: float, color: Tuple[float, float, float, float], segments: int = 32):
        """Draw a filled circle"""
        if not self.basic_program:
            print("[ERROR] Renderer.draw_circle: Cannot draw - basic_program not loaded!")
            return
        
        # Convert to NDC
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_radius_x = (radius / WINDOW_WIDTH) * 2
        ndc_radius_y = (radius / WINDOW_HEIGHT) * 2
        
        # Create vertices for circle (triangle fan)
        vertices_list = [ndc_x, ndc_y]  # Center point
        
        for i in range(segments + 1):
            angle = (i / segments) * 2 * np.pi
            vx = ndc_x + np.cos(angle) * ndc_radius_x
            vy = ndc_y + np.sin(angle) * ndc_radius_y
            vertices_list.extend([vx, vy])
        
        vertices = np.array(vertices_list, dtype='f4')
        
        # Create temporary VBO and VAO
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(self.basic_program, vbo, 'in_position')
        
        # Bind white texture and set color uniform
        self.white_texture.use(0)
        if self.basic_program and 'tex' in self.basic_program:
            self.basic_program['tex'].value = 0  # type: ignore[union-attr]
        if self.basic_program and 'color' in self.basic_program:
            self.basic_program['color'].value = color  # type: ignore[union-attr]
        
        # Draw
        vao.render(moderngl.TRIANGLE_FAN)
        
        # Cleanup
        vao.release()
        vbo.release()
    
    def draw_text(self, text: str, x: float, y: float, size: int, color: Tuple[float, float, float, float], 
                  font_name: Optional[str] = None, centered: bool = False):
        """Draw text using pygame fonts and OpenGL textures
        
        This method renders text to a UI overlay that is drawn AFTER the bloom effect,
        ensuring text remains crisp and readable. Text is cached in textures for performance.
        
        Args:
            text: Text to render
            x: X position (left edge, or center if centered=True)
            y: Y position (top edge)
            size: Font size (use constants from src.utils.constants for consistency)
            color: RGBA color tuple (0-1 range)
            font_name: Font file name in assets/fonts/ (None for default pygame font)
            centered: If True, text is centered at x position
        
        Example:
            renderer.draw_text("HELLO", 400, 300, FONT_SIZE_LARGE, COLOR_PINK, centered=True)
        """
        if not self.basic_program:
            print("[ERROR] Renderer.draw_text: Cannot draw - basic_program not loaded!")
            return
        
        # Convert color from 0-1 to 0-255 for pygame
        pygame_color = (
            int(color[0] * 255),
            int(color[1] * 255),
            int(color[2] * 255)
        )
        
        # Create cache key
        cache_key = (text, size, pygame_color, font_name)
        
        # Check cache
        if cache_key not in self.text_texture_cache:
            # Get font from asset manager
            font = self.asset_manager.get_font(font_name, size)
            
            # Render text to pygame surface
            text_surface = font.render(text, True, pygame_color)
            text_width, text_height = text_surface.get_size()
            
            # Convert to RGBA
            text_data = pygame.image.tostring(text_surface, 'RGBA', True)
            
            # Create OpenGL texture
            text_texture = self.ctx.texture((text_width, text_height), 4, text_data)
            text_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            
            # Cache the texture
            self.text_texture_cache[cache_key] = text_texture
        else:
            text_texture = self.text_texture_cache[cache_key]
        
        text_width, text_height = text_texture.size
        
        # Adjust x position if centered
        if centered:
            x = x - text_width / 2
        
        # Convert screen coordinates to NDC
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_width = (text_width / WINDOW_WIDTH) * 2
        ndc_height = (text_height / WINDOW_HEIGHT) * 2
        
        # Create vertices for text rectangle
        vertices = np.array([
            ndc_x, ndc_y - ndc_height,
            ndc_x + ndc_width, ndc_y - ndc_height,
            ndc_x, ndc_y,
            ndc_x + ndc_width, ndc_y,
        ], dtype='f4')
        
        # Switch to UI framebuffer
        current_fbo = self.ctx.fbo
        self.ui_fbo.use()
        
        # Enable blending for text
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Create temporary VBO and VAO
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(self.basic_program, vbo, 'in_position')
        
        # Bind text texture and set color uniform
        text_texture.use(0)
        if self.basic_program and 'tex' in self.basic_program:
            self.basic_program['tex'].value = 0  # type: ignore[union-attr]
        if self.basic_program and 'color' in self.basic_program:
            # Use white color to render text texture as-is (text is already colored)
            self.basic_program['color'].value = (1.0, 1.0, 1.0, color[3])  # type: ignore[union-attr]
        
        # Draw
        vao.render(moderngl.TRIANGLE_STRIP)
        
        # Cleanup
        vao.release()
        vbo.release()
        self.ctx.disable(moderngl.BLEND)
        
        # Restore previous framebuffer
        if current_fbo:
            current_fbo.use()
        else:
            self.scene_fbo.use()