"""
ModernGL renderer for game graphics
"""
import moderngl
import numpy as np
import pygame
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass
from src.managers.shader_manager import ShaderManager
from src.rendering.post_process import PostProcessor
from src.managers.asset_manager import AssetManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT

@dataclass
class TextDrawCall:
    """A record to hold all the information for a single text draw call."""
    text: str
    x: float
    y: float
    size: int
    color: Tuple[float, float, float, float]
    pygame_color: Tuple[int, int, int]
    font_name: Optional[str]
    centered: bool

class Renderer:
    """Handles all ModernGL rendering"""

    def __init__(self, ctx: moderngl.Context, shader_manager: ShaderManager):
        print("[DEBUG] Renderer.__init__: Initializing renderer...")
        self.ctx = ctx
        self.shader_manager = shader_manager

        # Load basic shader
        print("[DEBUG] Renderer.__init__: Loading basic shader...")
        basic_program_maybe = shader_manager.load_shader('basic', 'basic.vert', 'basic.frag')
        assert basic_program_maybe is not None, "Failed to load basic shader!"
        self.basic_program = basic_program_maybe
        print(f"[DEBUG] Renderer.__init__: Basic shader loaded successfully")

        # Load text shader
        print("[DEBUG] Renderer.__init__: Loading text shader...")
        text_program_maybe = shader_manager.load_shader('text', 'text.vert', 'text.frag')
        assert text_program_maybe is not None, "Failed to load text shader!"
        self.text_program = text_program_maybe
        print(f"[DEBUG] Renderer.__init__: Text shader loaded successfully")

        # Create post processor
        print("[DEBUG] Renderer.__init__: Creating post processor...")
        self.post_processor = PostProcessor(ctx, shader_manager)

        # --- Batching setup for Text ---
        self.text_batch: List[TextDrawCall] = []
        # Create a dynamic VBO with a large-ish reserve size
        # 1024 text calls * 6 vertices per call * 4 floats per vertex * 4 bytes per float
        self.text_vbo = self.ctx.buffer(reserve=1024 * 6 * 4 * 4, dynamic=True)
        self.text_vao = self.ctx.vertex_array(
            self.text_program,
            [(self.text_vbo, '2f 2f', 'in_position', 'in_uv')]
        )
        print("[DEBUG] Renderer.__init__: Text batching VBO/VAO created")

        # Create vertex buffer for a quad
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')

        self.quad_vbo = ctx.buffer(vertices.tobytes())
        self.quad_vao = ctx.simple_vertex_array(self.basic_program, self.quad_vbo, 'in_position')
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

        # UI overlay texture for text (rendered after bloom)
        self.ui_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.ui_fbo = ctx.framebuffer(color_attachments=[self.ui_texture])

        print("[DEBUG] Renderer.__init__: Renderer initialization complete!")

    def begin_frame(self):
        """Begin rendering a frame"""
        # Clear the text batch for the new frame
        self.text_batch.clear()

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
        # --- Flush the text batch to the UI texture ---
        self._flush_text_batch()

        # Apply bloom post-processing to scene
        final_texture = self.post_processor.apply_bloom(self.scene_texture)

        # Render to screen
        self.ctx.screen.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)

        # Draw bloomed scene to screen
        final_texture.use(0)
        self.basic_program['tex'] = 0
        self.basic_program['color'] = (1.0, 1.0, 1.0, 1.0)
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)

        # Draw UI overlay (which now contains our batched text) on top
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.ui_texture.use(0)
        self.basic_program['tex'] = 0
        self.basic_program['color'] = (1.0, 1.0, 1.0, 1.0)
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)

        self.ctx.disable(moderngl.BLEND)

    def draw_rect(self, x: float, y: float, width: float, height: float, color: Tuple[float, float, float, float]):
        """Draw a filled rectangle"""
        # This remains an immediate-mode draw call for simplicity
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_width = (width / WINDOW_WIDTH) * 2
        ndc_height = (height / WINDOW_HEIGHT) * 2

        vertices = np.array([
            ndc_x, ndc_y - ndc_height,
            ndc_x + ndc_width, ndc_y - ndc_height,
            ndc_x, ndc_y,
            ndc_x + ndc_width, ndc_y,
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(self.basic_program, vbo, 'in_position')

        self.white_texture.use(0)
        self.basic_program['tex'] = 0
        self.basic_program['color'] = color
        
        vao.render(moderngl.TRIANGLE_STRIP)
        
        vao.release()
        vbo.release()

    def draw_circle(self, x: float, y: float, radius: float, color: Tuple[float, float, float, float], segments: int = 32):
        """Draw a filled circle"""
        # This remains an immediate-mode draw call for simplicity
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_radius_x = (radius / WINDOW_WIDTH) * 2
        ndc_radius_y = (radius / WINDOW_HEIGHT) * 2

        vertices_list = [ndc_x, ndc_y]
        for i in range(segments + 1):
            angle = (i / segments) * 2 * np.pi
            vx = ndc_x + np.cos(angle) * ndc_radius_x
            vy = ndc_y + np.sin(angle) * ndc_radius_y
            vertices_list.extend([vx, vy])
        vertices = np.array(vertices_list, dtype='f4')

        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(self.basic_program, vbo, 'in_position')

        self.white_texture.use(0)
        self.basic_program['tex'] = 0
        self.basic_program['color'] = color
        
        vao.render(moderngl.TRIANGLE_FAN)
        
        vao.release()
        vbo.release()

    def draw_text(self, text: str, x: float, y: float, size: int, color: Tuple[float, float, float, float],
                  font_name: Optional[str] = None, centered: bool = False):
        """Queues text to be drawn in a batch at the end of the frame."""
        pygame_color = (
            int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
        )
        
        draw_call = TextDrawCall(
            text, x, y, size, color, pygame_color, font_name, centered
        )
        self.text_batch.append(draw_call)

    def _flush_text_batch(self):
        """Renders all queued text in a single draw call."""
        if not self.text_batch:
            return

        # --- Stage 1: Render all text surfaces and calculate atlas size ---
        rendered_surfaces = []
        total_width = 0
        max_height = 0
        for call in self.text_batch:
            font = self.asset_manager.get_font(call.font_name, call.size)
            surface = font.render(call.text, True, call.pygame_color).convert_alpha()
            rendered_surfaces.append(surface)
            total_width += surface.get_width()
            max_height = max(max_height, surface.get_height())

        # --- Stage 2: Create texture atlas and generate vertex data ---
        if total_width == 0 or max_height == 0:
            return

        atlas_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
        
        all_vertices = []
        current_x = 0
        for i, surface in enumerate(rendered_surfaces):
            call = self.text_batch[i]
            
            # Blit surface onto the atlas, aligned to the BOTTOM
            blit_y = max_height - surface.get_height()
            atlas_surface.blit(surface, (current_x, blit_y))
            
            # Calculate UVs for this text in the atlas
            u1 = current_x / total_width
            v1 = blit_y / max_height  # This is the BOTTOM of the UV range
            u2 = (current_x + surface.get_width()) / total_width
            v2 = (blit_y + surface.get_height()) / max_height # This is the TOP of the UV range

            # Calculate screen position in NDC
            draw_x = call.x
            if call.centered:
                draw_x -= surface.get_width() / 2
            
            ndc_x = (draw_x / WINDOW_WIDTH) * 2 - 1
            ndc_y = 1 - (call.y / WINDOW_HEIGHT) * 2
            ndc_w = (surface.get_width() / WINDOW_WIDTH) * 2
            ndc_h = (surface.get_height() / WINDOW_HEIGHT) * 2
            
            # Vertices for two triangles (a quad), with UVs correctly flipped
            # pos.x, pos.y, uv.x, uv.y
            v_bl = (ndc_x,       ndc_y - ndc_h, u1, v2) # Bottom-left vertex uses TOP UV coord
            v_br = (ndc_x + ndc_w, ndc_y - ndc_h, u2, v2) # Bottom-right vertex uses TOP UV coord
            v_tl = (ndc_x,       ndc_y,       u1, v1) # Top-left vertex uses BOTTOM UV coord
            v_tr = (ndc_x + ndc_w, ndc_y,       u2, v1) # Top-right vertex uses BOTTOM UV coord

            all_vertices.extend([*v_tl, *v_bl, *v_tr, *v_bl, *v_br, *v_tr])
            
            current_x += surface.get_width()

        # --- Stage 3: Upload data to GPU and render ---
        # Create atlas texture. We pass the data raw (un-flipped) and handle the
        # vertical flip in our vertex UV coordinates.
        atlas_data = pygame.image.tostring(atlas_surface, 'RGBA')
        atlas_texture = self.ctx.texture(atlas_surface.get_size(), 4, atlas_data)
        
        atlas_texture.repeat_x = False
        atlas_texture.repeat_y = False
        
        atlas_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Write vertex data to dynamic VBO
        vertex_np = np.array(all_vertices, dtype='f4')
        self.text_vbo.write(vertex_np.tobytes())

        # Switch to UI framebuffer to draw
        self.ui_fbo.use()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        atlas_texture.use(0)
        self.text_program['tex'] = 0
        self.text_program['color'] = (1.0, 1.0, 1.0, 1.0) # Color is baked into texture

        # Render just the part of the VBO we used
        self.text_vao.render(moderngl.TRIANGLES, vertices=len(all_vertices) // 4)

        self.ctx.disable(moderngl.BLEND)
        atlas_texture.release()

