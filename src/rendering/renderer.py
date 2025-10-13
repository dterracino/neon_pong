"""
ModernGL renderer for game graphics
"""
import moderngl
import numpy as np
import pygame
from typing import Tuple
from src.managers.shader_manager import ShaderManager
from src.rendering.post_process import PostProcessor
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT


class Renderer:
    """Handles all ModernGL rendering"""
    
    def __init__(self, ctx: moderngl.Context, shader_manager: ShaderManager):
        self.ctx = ctx
        self.shader_manager = shader_manager
        
        # Load basic shader
        self.basic_program = shader_manager.load_shader('basic', 'basic.vert', 'basic.frag')
        
        # Create post processor
        self.post_processor = PostProcessor(ctx, shader_manager)
        
        # Create vertex buffer for a quad
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        
        self.quad_vbo = ctx.buffer(vertices.tobytes())
        self.quad_vao = ctx.simple_vertex_array(self.basic_program, self.quad_vbo, 'in_position')
        
        # Create framebuffer for scene rendering
        self.scene_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.scene_fbo = ctx.framebuffer(color_attachments=[self.scene_texture])
        
    def begin_frame(self):
        """Begin rendering a frame"""
        # Render to scene framebuffer
        self.scene_fbo.use()
        self.ctx.clear(0.05, 0.02, 0.15, 1.0)  # Dark purple background
    
    def end_frame(self):
        """End rendering and apply post-processing"""
        # Apply bloom post-processing
        final_texture = self.post_processor.apply_bloom(self.scene_texture)
        
        # Render to screen
        self.ctx.screen.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Draw final texture to screen
        final_texture.use(0)
        if self.basic_program:
            self.basic_program['tex'].value = 0
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)
    
    def draw_rect(self, x: float, y: float, width: float, height: float, color: Tuple[float, float, float, float]):
        """Draw a filled rectangle"""
        if not self.basic_program:
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
        
        # Set color uniform
        self.basic_program['color'].value = color
        
        # Draw
        vao.render(moderngl.TRIANGLE_STRIP)
        
        # Cleanup
        vao.release()
        vbo.release()
    
    def draw_circle(self, x: float, y: float, radius: float, color: Tuple[float, float, float, float], segments: int = 32):
        """Draw a filled circle"""
        if not self.basic_program:
            return
        
        # Convert to NDC
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_radius_x = (radius / WINDOW_WIDTH) * 2
        ndc_radius_y = (radius / WINDOW_HEIGHT) * 2
        
        # Create vertices for circle (triangle fan)
        vertices = [ndc_x, ndc_y]  # Center point
        
        for i in range(segments + 1):
            angle = (i / segments) * 2 * np.pi
            vx = ndc_x + np.cos(angle) * ndc_radius_x
            vy = ndc_y + np.sin(angle) * ndc_radius_y
            vertices.extend([vx, vy])
        
        vertices = np.array(vertices, dtype='f4')
        
        # Create temporary VBO and VAO
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(self.basic_program, vbo, 'in_position')
        
        # Set color uniform
        self.basic_program['color'].value = color
        
        # Draw
        vao.render(moderngl.TRIANGLE_FAN)
        
        # Cleanup
        vao.release()
        vbo.release()