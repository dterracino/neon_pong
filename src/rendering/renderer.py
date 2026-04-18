"""
ModernGL renderer for game graphics
"""
import logging
import moderngl
import numpy as np
import pygame
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass
from src.managers.shader_manager import ShaderManager
from src.rendering.post_process import PostProcessor
from src.managers.asset_manager import AssetManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_TYPE

logger = logging.getLogger(__name__)

@dataclass
class TextEffects:
    """Text rendering effects configuration"""
    stroke_width: float = 0.0
    stroke_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    shadow_offset: Tuple[float, float] = (0.0, 0.0)
    shadow_blur: float = 0.0
    shadow_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.5)
    gradient_enabled: bool = False
    gradient_color_top: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    gradient_color_bottom: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)

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
    effects: Optional[TextEffects] = None
    render_before_bloom: bool = False  # If True, render to scene_fbo (with bloom)

class Renderer:
    """Handles all ModernGL rendering"""

    def __init__(self, ctx: moderngl.Context, shader_manager: ShaderManager):
        logger.debug("Initializing renderer")
        self.ctx = ctx
        self.shader_manager = shader_manager

        # Load basic shader
        logger.debug("Loading basic shader")
        basic_program_maybe = shader_manager.load_shader('basic', 'basic.vert', 'basic.frag')
        assert basic_program_maybe is not None, "Failed to load basic shader!"
        self.basic_program = basic_program_maybe
        logger.debug("Basic shader loaded successfully")

        # Load sprite shader
        logger.debug("Loading sprite shader")
        sprite_program_maybe = shader_manager.load_shader('sprite', 'sprite.vert', 'sprite.frag')
        assert sprite_program_maybe is not None, "Failed to load sprite shader!"
        self.sprite_program = sprite_program_maybe
        logger.debug("Sprite shader loaded successfully")

        # Load text shader
        logger.debug("Loading text shader")
        text_program_maybe = shader_manager.load_shader('text', 'text.vert', 'text.frag')
        assert text_program_maybe is not None, "Failed to load text shader!"
        self.text_program = text_program_maybe
        logger.debug("Text shader loaded successfully")
        
        # Load text effects shader
        logger.debug("Loading text effects shader")
        text_effects_program_maybe = shader_manager.load_shader('text_effects', 'text_effects.vert', 'text_effects.frag')
        assert text_effects_program_maybe is not None, "Failed to load text effects shader!"
        self.text_effects_program = text_effects_program_maybe
        logger.debug("Text effects shader loaded successfully")

        # Create post processor
        logger.debug("Creating post processor")
        self.post_processor = PostProcessor(ctx, shader_manager)

        # --- Batching setup for Text ---
        self.text_batch: List[TextDrawCall] = []
        # Create a dynamic VBO with a large-ish reserve size
        # Extended vertex format: position(2) + uv(2) + color(4) + stroke_width(1) + stroke_color(4) + 
        #                         shadow_offset(2) + shadow_blur(1) + shadow_color(4) + 
        #                         gradient_enabled(1) + gradient_top(4) + gradient_bottom(4) = 29 floats per vertex
        # 1024 text calls * 6 vertices per call * 29 floats per vertex * 4 bytes per float
        self.text_vbo = self.ctx.buffer(reserve=1024 * 6 * 29 * 4, dynamic=True)
        self.text_vao = self.ctx.vertex_array(
            self.text_program,
            [(self.text_vbo, '2f 2f', 'in_position', 'in_uv')]
        )
        # VAO for effects shader with extended vertex format
        self.text_effects_vao = self.ctx.vertex_array(
            self.text_effects_program,
            [(self.text_vbo, '2f 2f 4f 1f 4f 2f 1f 4f 1f 4f 4f', 
              'in_position', 'in_uv', 'in_color', 
              'in_stroke_width', 'in_stroke_color',
              'in_shadow_offset', 'in_shadow_blur', 'in_shadow_color',
              'in_gradient_enabled', 'in_gradient_top', 'in_gradient_bottom')]
        )
        logger.debug("Text batching VBO/VAO created")

        # Create vertex buffer for a quad
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')

        self.quad_vbo = ctx.buffer(vertices.tobytes())
        self.quad_vao = ctx.simple_vertex_array(self.basic_program, self.quad_vbo, 'in_position')
        logger.debug("Quad VAO created")

        # Create a white 1x1 texture for solid color rendering
        WHITE_PIXEL = np.array([255, 255, 255, 255], dtype='u1')
        self.white_texture = ctx.texture((1, 1), 4, WHITE_PIXEL.tobytes())
        logger.debug("White texture created")

        # Create framebuffer for scene rendering
        logger.debug("Creating scene framebuffer (%dx%d)", WINDOW_WIDTH, WINDOW_HEIGHT)
        self.scene_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.scene_fbo = ctx.framebuffer(color_attachments=[self.scene_texture])

        # Initialize asset manager for fonts
        self.asset_manager = AssetManager()

        # Text surface cache for performance optimization
        # Key: (text, size, pygame_color, font_name), Value: pygame.Surface
        self.text_surface_cache: Dict[tuple, pygame.Surface] = {}
        
        # Text texture cache for performance optimization
        # Key: (text, size, pygame_color, font_name), Value: (moderngl.Texture, width, height)
        self.text_texture_cache: Dict[tuple, Tuple[moderngl.Texture, int, int]] = {}

        # UI overlay texture for text (rendered after bloom)
        self.ui_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.ui_fbo = ctx.framebuffer(color_attachments=[self.ui_texture])

        # Load background shader based on configuration
        logger.debug("Loading background shader (%s)", BACKGROUND_TYPE)
        self.background_program = None
        self.background_enabled = BACKGROUND_TYPE != "solid"
        if BACKGROUND_TYPE == "starfield":
            self.background_program = shader_manager.load_shader(
                'background_starfield', 'basic.vert', 'background_starfield.frag'
            )
        elif BACKGROUND_TYPE == "parallaxstarfield":
            self.background_program = shader_manager.load_shader(
                'background_parallaxstarfield', 'basic.vert', 'background_parallaxstarfield.frag'
            )
        elif BACKGROUND_TYPE == "galaxytrip":
            self.background_program = shader_manager.load_shader(
                'background_galaxytrip', 'basic.vert', 'background_galaxytrip.frag'
            )
        elif BACKGROUND_TYPE == "plasma":
            self.background_program = shader_manager.load_shader(
                'background_plasma', 'basic.vert', 'background_plasma.frag'
            )
        elif BACKGROUND_TYPE == "waves":
            self.background_program = shader_manager.load_shader(
                'background_waves', 'basic.vert', 'background_waves.frag'
            )
        elif BACKGROUND_TYPE == "retrowave":
            self.background_program = shader_manager.load_shader(
                'background_retrowave', 'basic.vert', 'background_retrowave.frag'
            )
        elif BACKGROUND_TYPE == "retro":
            self.background_program = shader_manager.load_shader(
                'background_retro', 'basic.vert', 'background_retro.frag'
            )
        
        if self.background_program:
            self.background_vao = ctx.simple_vertex_array(
                self.background_program, self.quad_vbo, 'in_position'
            )
            logger.debug("Background shader loaded successfully")
        else:
            self.background_enabled = False
            logger.debug("Using solid background")
        
        # Load dust overlay shader
        logger.debug("Loading dust overlay shader")
        self.dust_overlay_program = shader_manager.load_shader(
            'dust_overlay', 'basic.vert', 'dust_overlay.frag'
        )
        if self.dust_overlay_program:
            self.dust_overlay_vao = ctx.simple_vertex_array(
                self.dust_overlay_program, self.quad_vbo, 'in_position'
            )
            logger.debug("Dust overlay shader loaded successfully")
        else:
            logger.warning("Dust overlay shader failed to load")
        
        # Time tracking for animated backgrounds
        self.time = 0.0
        
        # Cache management
        self.max_cache_size = 100  # Maximum number of cached text items
        self.cache_access_count: Dict[tuple, int] = {}  # Track access frequency

        logger.debug("Renderer initialization complete")

    def update_time(self, dt: float):
        """Update time for animated backgrounds and post-processing effects"""
        self.time += dt
        self.post_processor.update_time(dt)

    def toggle_scanlines(self) -> bool:
        """Toggle scanlines post-processing on/off. Returns new state."""
        return self.post_processor.toggle_scanlines()

    def reload_background_shader(self):
        """Reload the background shader based on current BACKGROUND_TYPE setting."""
        from src.utils.constants import BACKGROUND_TYPE
        
        logger.debug("Reloading background shader (%s)", BACKGROUND_TYPE)
        
        # Release old VAO if it exists
        if hasattr(self, 'background_vao') and self.background_vao:
            self.background_vao.release()
            self.background_vao = None
        
        # Clear old program reference
        self.background_program = None
        self.background_enabled = BACKGROUND_TYPE != "solid"
        
        # Load new background shader
        if BACKGROUND_TYPE == "starfield":
            self.background_program = self.shader_manager.load_shader(
                'background_starfield', 'basic.vert', 'background_starfield.frag'
            )
        elif BACKGROUND_TYPE == "parallaxstarfield":
            self.background_program = self.shader_manager.load_shader(
                'background_parallaxstarfield', 'basic.vert', 'background_parallaxstarfield.frag'
            )
        elif BACKGROUND_TYPE == "galaxytrip":
            self.background_program = self.shader_manager.load_shader(
                'background_galaxytrip', 'basic.vert', 'background_galaxytrip.frag'
            )
        elif BACKGROUND_TYPE == "ftl":
            self.background_program = self.shader_manager.load_shader(
                'background_ftl', 'basic.vert', 'background_ftl.frag'
            )
        elif BACKGROUND_TYPE == "plasma":
            self.background_program = self.shader_manager.load_shader(
                'background_plasma', 'basic.vert', 'background_plasma.frag'
            )
        elif BACKGROUND_TYPE == "waves":
            self.background_program = self.shader_manager.load_shader(
                'background_waves', 'basic.vert', 'background_waves.frag'
            )
        elif BACKGROUND_TYPE == "retrowave":
            self.background_program = self.shader_manager.load_shader(
                'background_retrowave', 'basic.vert', 'background_retrowave.frag'
            )
        elif BACKGROUND_TYPE == "retro":
            self.background_program = self.shader_manager.load_shader(
                'background_retro', 'basic.vert', 'background_retro.frag'
            )
        
        # Create new VAO if we have a program
        if self.background_program:
            self.background_vao = self.ctx.simple_vertex_array(
                self.background_program, self.quad_vbo, 'in_position'
            )
            logger.debug("Background shader reloaded successfully")
        else:
            self.background_enabled = False
            logger.debug("Using solid background")

    def _manage_text_cache(self):
        """Manage text cache size by removing least frequently used items"""
        if len(self.text_surface_cache) <= self.max_cache_size:
            return
        
        # Sort by access count and remove least frequently used items
        sorted_items = sorted(self.cache_access_count.items(), key=lambda x: x[1])
        items_to_remove = len(self.text_surface_cache) - self.max_cache_size + 10  # Remove 10 extra for headroom
        
        for cache_key, _ in sorted_items[:items_to_remove]:
            # Remove from surface cache
            if cache_key in self.text_surface_cache:
                del self.text_surface_cache[cache_key]
            
            # Remove from texture cache and release GPU texture
            if cache_key in self.text_texture_cache:
                texture, _, _ = self.text_texture_cache[cache_key]
                texture.release()
                del self.text_texture_cache[cache_key]
            
            # Remove from access count
            if cache_key in self.cache_access_count:
                del self.cache_access_count[cache_key]
        
        logger.debug("Cache cleanup: removed %d items, now at %d items", 
                    items_to_remove, len(self.text_surface_cache))
    
    def get_text_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the text rendering cache
        
        Returns:
            Dictionary with cache statistics including size and hit counts
        """
        return {
            'surface_cache_size': len(self.text_surface_cache),
            'texture_cache_size': len(self.text_texture_cache),
            'max_cache_size': self.max_cache_size,
            'total_accesses': sum(self.cache_access_count.values())
        }
    
    def begin_frame(self):
        """Begin rendering a frame"""
        # Clear the text batch for the new frame
        self.text_batch.clear()

        # Render to scene framebuffer
        self.scene_fbo.use()
        
        if self.background_enabled and self.background_program:
            # Render animated background
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.background_program['time'] = self.time
            self.background_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
            self.background_vao.render(moderngl.TRIANGLE_STRIP)
        else:
            # Clear with solid color
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
        bloomed_texture = self.post_processor.apply_bloom(self.scene_texture)
        
        # Apply style effect (scanlines, CRT, VHS, or none) to bloomed result
        final_texture = self.post_processor.apply_style_effect(bloomed_texture)

        # Render to screen
        self.ctx.screen.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)

        # Draw final processed scene to screen
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

    def draw_sprite(self, sprite: pygame.Surface, x: float, y: float, 
                    width: Optional[float] = None, height: Optional[float] = None,
                    color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)):
        """Draw a pygame Surface as a textured sprite
        
        Args:
            sprite: pygame Surface to render
            x: X position (top-left corner in screen coordinates)
            y: Y position (top-left corner in screen coordinates)
            width: Width to render (None = use sprite width)
            height: Height to render (None = use sprite height)
            color: Color tint (RGBA 0-1 range, default white = no tint)
        """
        # Use sprite dimensions if not specified
        if width is None:
            width = sprite.get_width()
        if height is None:
            height = sprite.get_height()
        
        # Convert to NDC coordinates
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_width = (width / WINDOW_WIDTH) * 2
        ndc_height = (height / WINDOW_HEIGHT) * 2

        # Create vertices with UV coordinates
        vertices = np.array([
            # pos_x, pos_y, uv_u, uv_v
            ndc_x,              ndc_y - ndc_height, 0.0, 1.0,  # Bottom-left
            ndc_x + ndc_width,  ndc_y - ndc_height, 1.0, 1.0,  # Bottom-right
            ndc_x,              ndc_y,              0.0, 0.0,  # Top-left
            ndc_x + ndc_width,  ndc_y,              1.0, 0.0,  # Top-right
        ], dtype='f4')

        # Create texture from pygame surface
        texture_data = pygame.image.tostring(sprite, 'RGBA', True)
        texture = self.ctx.texture(
            (sprite.get_width(), sprite.get_height()),
            4,  # RGBA components
            texture_data
        )
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)  # Pixel-perfect for retro look

        # Create VBO and VAO
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.vertex_array(
            self.sprite_program,
            [(vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )

        # Render
        texture.use(0)
        self.sprite_program['tex'] = 0
        self.sprite_program['color'] = color
        vao.render(moderngl.TRIANGLE_STRIP)
        
        # Cleanup
        vao.release()
        vbo.release()
        texture.release()

    def draw_rounded_rect(self, x: float, y: float, width: float, height: float,
                          radius: float, color: Tuple[float, float, float, float]):
        """Draw a filled rounded rectangle using rects + corner circles"""
        r = min(radius, width / 2, height / 2)
        # Centre body
        self.draw_rect(x, y + r, width, height - 2 * r, color)
        # Top and bottom strips (between corners)
        self.draw_rect(x + r, y, width - 2 * r, r, color)
        self.draw_rect(x + r, y + height - r, width - 2 * r, r, color)
        # Four corner circles
        self.draw_circle(x + r,         y + r,          r, color)
        self.draw_circle(x + width - r, y + r,          r, color)
        self.draw_circle(x + r,         y + height - r, r, color)
        self.draw_circle(x + width - r, y + height - r, r, color)

    def render_particles(self, particle_system):
        """Render enhanced particle system to current framebuffer
        
        This should be called when scene_fbo is active to get bloom effect.
        
        Args:
            particle_system: EnhancedParticleSystem instance
        """
        from src.entities.enhanced_particles import EnhancedParticle
        
        for particle in particle_system.particles:
            alpha = particle.get_alpha()
            color = (*particle.color[:3], alpha)
            self.draw_circle(particle.x, particle.y, particle.size / 2, color)
    
    def draw_dust_overlay(self):
        """Draw dust overlay effect on current framebuffer
        
        This creates a transparent layer of meandering dust particles with glinting.
        Should be called after background but before other scene elements.
        Requires alpha blending to be enabled.
        """
        if not self.dust_overlay_program:
            return
        
        # Enable alpha blending for transparent overlay
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Render dust overlay
        self.dust_overlay_program['time'] = self.time
        self.dust_overlay_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.dust_overlay_vao.render(moderngl.TRIANGLE_STRIP)
        
        # Disable blending
        self.ctx.disable(moderngl.BLEND)

    def draw_text(self, text: str, x: float, y: float, size: int, color: Tuple[float, float, float, float],
                  font_name: Optional[str] = None, centered: bool = False, effects: Optional[TextEffects] = None,
                  render_before_bloom: bool = False):
        """Queues text to be drawn in a batch at the end of the frame.
        
        Args:
            text: Text to render
            x, y: Screen position
            size: Font size in pixels
            color: RGBA color (normalized 0-1)
            font_name: Font to use. Three forms are supported:
                - None / omitted      → default font (ARCADECLASSIC.TTF)
                - "MyFont.ttf"        → file in assets/fonts/
                - "sys:fontname"      → system font via pygame.font.SysFont.
                                        Use the normalised name from pygame.font.get_fonts()
                                        (lowercase, no spaces/punctuation), e.g.
                                        "sys:arial", "sys:gillsans", "sys:calibri".
                                        Add "bold" and/or "italic" keywords for styles:
                                        "sys:arial bold", "sys:arial italic", "sys:arial bold italic".
            centered: Center text at x position
            effects: Optional TextEffects for stroke, shadow, gradient
            render_before_bloom: If True, renders to scene (with bloom). If False, renders to UI overlay (no bloom)
        """
        pygame_color = (
            int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
        )
        
        draw_call = TextDrawCall(
            text, x, y, size, color, pygame_color, font_name, centered, effects, render_before_bloom
        )
        self.text_batch.append(draw_call)

    def _flush_text_batch(self):
        """Renders all queued text, separating bloom and no-bloom batches."""
        if not self.text_batch:
            return
        
        # Separate text into bloom and no-bloom batches
        bloom_batch = [call for call in self.text_batch if call.render_before_bloom]
        no_bloom_batch = [call for call in self.text_batch if not call.render_before_bloom]
        
        # Render bloom batch to scene_fbo (will get bloom effect)
        if bloom_batch:
            self._render_text_batch(bloom_batch, self.scene_fbo)
        
        # Render no-bloom batch to ui_fbo (no bloom effect)
        if no_bloom_batch:
            self._render_text_batch(no_bloom_batch, self.ui_fbo)
    
    def _render_text_batch(self, batch: List[TextDrawCall], target_fbo):
        """Renders a batch of text to the specified framebuffer with single draw call."""
        # --- Stage 1: Render all text surfaces and calculate atlas size ---
        rendered_surfaces = []
        total_width = 0
        max_height = 0
        
        for call in batch:
            # Create cache key from text properties
            cache_key = (call.text, call.size, call.pygame_color, call.font_name)
            
            # Track cache access for LRU management
            self.cache_access_count[cache_key] = self.cache_access_count.get(cache_key, 0) + 1
            
            # Check if we have this text surface cached
            if cache_key in self.text_surface_cache:
                surface = self.text_surface_cache[cache_key]
            else:
                # Render new surface and cache it
                font = self.asset_manager.get_font(call.font_name, call.size)
                surface = font.render(call.text, True, call.pygame_color).convert_alpha()
                self.text_surface_cache[cache_key] = surface
            
            rendered_surfaces.append(surface)
            total_width += surface.get_width()
            max_height = max(max_height, surface.get_height())
        
        # Periodically clean up cache if it gets too large
        if len(self.text_surface_cache) > self.max_cache_size:
            self._manage_text_cache()

        # --- Stage 2: Create texture atlas and generate vertex data with effect parameters ---
        if total_width == 0 or max_height == 0:
            return

        atlas_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
        
        all_vertices = []
        current_x = 0
        
        for i, surface in enumerate(rendered_surfaces):
            call = batch[i]
            
            # Blit surface onto the atlas, aligned to the BOTTOM
            blit_y = max_height - surface.get_height()
            atlas_surface.blit(surface, (current_x, blit_y))
            
            # Calculate UVs for this text in the atlas
            u1 = current_x / total_width
            v1 = blit_y / max_height  # This is the BOTTOM of the UV range
            u2 = (current_x + surface.get_width()) / total_width
            v2 = (blit_y + surface.get_height()) / max_height  # This is the TOP of the UV range

            # Calculate screen position in NDC
            draw_x = call.x
            if call.centered:
                draw_x -= surface.get_width() / 2
            
            ndc_x = (draw_x / WINDOW_WIDTH) * 2 - 1
            ndc_y = 1 - (call.y / WINDOW_HEIGHT) * 2
            ndc_w = (surface.get_width() / WINDOW_WIDTH) * 2
            ndc_h = (surface.get_height() / WINDOW_HEIGHT) * 2
            
            # Get effect parameters (or defaults if no effects)
            effects = call.effects or TextEffects()
            
            # Pack effect data for this text (same for all 6 vertices of the quad)
            effect_data = [
                *call.color,  # color (4 floats)
                effects.stroke_width,  # stroke_width (1 float)
                *effects.stroke_color,  # stroke_color (4 floats)
                *effects.shadow_offset,  # shadow_offset (2 floats)
                effects.shadow_blur,  # shadow_blur (1 float)
                *effects.shadow_color,  # shadow_color (4 floats)
                1.0 if effects.gradient_enabled else 0.0,  # gradient_enabled (1 float)
                *effects.gradient_color_top,  # gradient_top (4 floats)
                *effects.gradient_color_bottom,  # gradient_bottom (4 floats)
            ]  # Total: 25 floats of effect data per vertex
            
            # Create vertices for two triangles (a quad)
            # Each vertex: position(2) + uv(2) + effect_data(25) = 29 floats
            v_bl = (ndc_x,       ndc_y - ndc_h, u1, v2, *effect_data)  # Bottom-left
            v_br = (ndc_x + ndc_w, ndc_y - ndc_h, u2, v2, *effect_data)  # Bottom-right
            v_tl = (ndc_x,       ndc_y,       u1, v1, *effect_data)  # Top-left
            v_tr = (ndc_x + ndc_w, ndc_y,       u2, v1, *effect_data)  # Top-right

            # Two triangles forming a quad
            all_vertices.extend([*v_tl, *v_bl, *v_tr, *v_bl, *v_br, *v_tr])
            
            current_x += surface.get_width()

        # --- Stage 3: Upload data to GPU and render with SINGLE draw call ---
        atlas_data = pygame.image.tostring(atlas_surface, 'RGBA')
        atlas_texture = self.ctx.texture(atlas_surface.get_size(), 4, atlas_data)
        
        atlas_texture.repeat_x = False
        atlas_texture.repeat_y = False
        atlas_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Write ALL vertex data to VBO at once
        vertex_np = np.array(all_vertices, dtype='f4')
        self.text_vbo.write(vertex_np.tobytes())

        # Switch to target framebuffer
        target_fbo.use()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        atlas_texture.use(0)
        self.text_effects_program['tex'] = 0
        
        # SINGLE render call for all text with per-vertex effect parameters
        self.text_effects_vao.render(moderngl.TRIANGLES, vertices=len(all_vertices) // 29)

        self.ctx.disable(moderngl.BLEND)
        atlas_texture.release()

    def draw_text_direct(self, text: str, x: float, y: float, size: int, 
                        color: Tuple[float, float, float, float],
                        font_name: Optional[str] = None):
        """
        Render text immediately to the current framebuffer without batching.
        Useful for rendering after end_frame() has been called.

        Args:
            text: Text to render
            x, y: Screen position
            size: Font size in pixels
            color: RGBA color (normalized 0-1)
            font_name: Font to use. Three forms are supported:
                - None / omitted      → default font (ARCADECLASSIC.TTF)
                - "MyFont.ttf"        → file in assets/fonts/
                - "sys:fontname"      → system font via pygame.font.SysFont.
                                        Use the normalised name from pygame.font.get_fonts()
                                        (lowercase, no spaces/punctuation), e.g.
                                        "sys:arial", "sys:gillsans", "sys:calibri".
                                        Add "bold" and/or "italic" keywords for styles:
                                        "sys:arial bold", "sys:arial italic", "sys:arial bold italic".
        """
        # Render text to pygame surface
        pygame_color = (
            int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
        )
        font = self.asset_manager.get_font(font_name, size)
        surface = font.render(text, True, pygame_color).convert_alpha()
        
        # Convert to texture (flip vertically for OpenGL)
        text_data = pygame.image.tostring(surface, 'RGBA', True)
        text_texture = self.ctx.texture(surface.get_size(), 4, text_data)
        text_texture.repeat_x = False
        text_texture.repeat_y = False
        text_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        
        # Calculate NDC coordinates
        ndc_x = (x / WINDOW_WIDTH) * 2 - 1
        ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
        ndc_w = (surface.get_width() / WINDOW_WIDTH) * 2
        ndc_h = (surface.get_height() / WINDOW_HEIGHT) * 2
        
        # Create vertices (UV flipped because texture is flipped)
        vertices = np.array([
            # pos.x, pos.y, uv.x, uv.y
            ndc_x,       ndc_y,       0.0, 1.0,  # Top-left
            ndc_x,       ndc_y - ndc_h, 0.0, 0.0,  # Bottom-left
            ndc_x + ndc_w, ndc_y,       1.0, 1.0,  # Top-right
            ndc_x,       ndc_y - ndc_h, 0.0, 0.0,  # Bottom-left
            ndc_x + ndc_w, ndc_y - ndc_h, 1.0, 0.0,  # Bottom-right
            ndc_x + ndc_w, ndc_y,       1.0, 1.0,  # Top-right
        ], dtype='f4')
        
        # Create temporary VBO and VAO
        temp_vbo = self.ctx.buffer(vertices.tobytes())
        temp_vao = self.ctx.vertex_array(
            self.text_program,
            [(temp_vbo, '2f 2f', 'in_position', 'in_uv')]
        )
        
        # Render
        text_texture.use(0)
        self.text_program['tex'] = 0
        self.text_program['color'] = (1.0, 1.0, 1.0, color[3])  # Preserve text color, apply alpha
        temp_vao.render(moderngl.TRIANGLES)
        
        # Cleanup
        temp_vao.release()
        temp_vbo.release()
        text_texture.release()

