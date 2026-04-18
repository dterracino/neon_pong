"""
Post-processing effects using ModernGL
"""
import logging
import moderngl
from src.managers.shader_manager import ShaderManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, BLOOM_BLUR_PASSES, BLOOM_THRESHOLD, BLOOM_INTENSITY, POST_EFFECT_TYPE, SCANLINE_THICKNESS
import numpy as np

logger = logging.getLogger(__name__)


class PostProcessor:
    """Handles post-processing effects like bloom"""
    
    def __init__(self, ctx: moderngl.Context, shader_manager: ShaderManager):
        logger.debug("Initializing post processor")
        self.ctx = ctx
        self.shader_manager = shader_manager
        
        # Load shaders
        logger.debug("Loading bloom shaders")
        self.bloom_extract_program = shader_manager.load_shader(
            'bloom_extract', 'basic.vert', 'bloom_extract.frag'
        )
        self.bloom_blur_program = shader_manager.load_shader(
            'bloom_blur', 'basic.vert', 'bloom_blur.frag'
        )
        self.bloom_combine_program = shader_manager.load_shader(
            'bloom_combine', 'basic.vert', 'bloom_combine.frag'
        )
        
        if all([self.bloom_extract_program, self.bloom_blur_program, self.bloom_combine_program]):
            logger.debug("All bloom shaders loaded successfully")
        else:
            logger.warning("Some bloom shaders failed to load")
        
        # Create fullscreen quad
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        
        self.quad_vbo = ctx.buffer(vertices.tobytes())
        
        # Create VAOs for each shader
        if self.bloom_extract_program:
            self.extract_vao = ctx.simple_vertex_array(
                self.bloom_extract_program, self.quad_vbo, 'in_position'
            )
        
        if self.bloom_blur_program:
            self.blur_vao = ctx.simple_vertex_array(
                self.bloom_blur_program, self.quad_vbo, 'in_position'
            )
        
        if self.bloom_combine_program:
            self.combine_vao = ctx.simple_vertex_array(
                self.bloom_combine_program, self.quad_vbo, 'in_position'
            )
        
        # Create textures and framebuffers for bloom
        self.bright_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.bright_fbo = ctx.framebuffer(color_attachments=[self.bright_texture])
        
        self.blur_texture1 = ctx.texture((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), 4, dtype='f4')
        self.blur_fbo1 = ctx.framebuffer(color_attachments=[self.blur_texture1])
        
        self.blur_texture2 = ctx.texture((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), 4, dtype='f4')
        self.blur_fbo2 = ctx.framebuffer(color_attachments=[self.blur_texture2])
        
        self.final_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
        self.final_fbo = ctx.framebuffer(color_attachments=[self.final_texture])
        
        # Load style effect shader based on configuration
        logger.debug("Loading style effect shader (%s)", POST_EFFECT_TYPE)
        self.style_effect_program = None
        self.style_effect_enabled = POST_EFFECT_TYPE != "none"
        
        if POST_EFFECT_TYPE == "scanlines":
            self.style_effect_program = shader_manager.load_shader(
                'style_scanlines', 'basic.vert', 'scanlines.frag'
            )
        elif POST_EFFECT_TYPE == "crt":
            self.style_effect_program = shader_manager.load_shader(
                'style_crt', 'basic.vert', 'crt.frag'
            )
        elif POST_EFFECT_TYPE == "vhs":
            self.style_effect_program = shader_manager.load_shader(
                'style_vhs', 'basic.vert', 'vhs.frag'
            )
        
        if self.style_effect_program:
            self.style_effect_vao = ctx.simple_vertex_array(
                self.style_effect_program, self.quad_vbo, 'in_position'
            )
            # Create output texture for style effect
            self.style_effect_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
            self.style_effect_fbo = ctx.framebuffer(color_attachments=[self.style_effect_texture])
            logger.debug("Style effect shader loaded successfully")
        else:
            self.style_effect_enabled = False
            logger.debug("No style effect enabled")

        # Scanlines — always loaded so it can be toggled at runtime with = key
        self.scanlines_enabled = False
        self.scanlines_program = shader_manager.load_shader(
            'scanlines', 'basic.vert', 'scanlines.frag'
        )
        if self.scanlines_program:
            self.scanlines_vao = ctx.simple_vertex_array(
                self.scanlines_program, self.quad_vbo, 'in_position'
            )
            self.scanlines_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype='f4')
            self.scanlines_fbo = ctx.framebuffer(color_attachments=[self.scanlines_texture])
            logger.debug("Scanlines shader loaded (toggle with = key)")
        else:
            self.scanlines_vao = None
            logger.warning("Scanlines shader failed to load")
        
        # Time tracking for animated effects
        self.time = 0.0
        
        logger.debug("Post processor initialization complete")
    
    def apply_bloom(self, source_texture: moderngl.Texture) -> moderngl.Texture:
        """Apply bloom effect to source texture"""
        # If shaders aren't loaded, return original
        if not all([self.bloom_extract_program, self.bloom_blur_program, self.bloom_combine_program]):
            logger.warning("Bloom shaders not loaded, returning original texture")
            return source_texture
        
        # Step 1: Extract bright pixels
        self.bright_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        source_texture.use(0)
        if self.bloom_extract_program and 'tex' in self.bloom_extract_program:
            self.bloom_extract_program['tex'] = 0
        if self.bloom_extract_program and 'threshold' in self.bloom_extract_program:
            self.bloom_extract_program['threshold'] = BLOOM_THRESHOLD
        self.extract_vao.render(moderngl.TRIANGLE_STRIP)
        
        # Step 2: Blur bright pixels (ping-pong between two buffers)
        current_source = self.bright_texture
        current_target_fbo = self.blur_fbo1
        current_target_texture = self.blur_texture1
        
        for i in range(BLOOM_BLUR_PASSES * 2):
            current_target_fbo.use()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            current_source.use(0)
            if self.bloom_blur_program and 'tex' in self.bloom_blur_program:
                self.bloom_blur_program['tex'] = 0
            if self.bloom_blur_program and 'horizontal' in self.bloom_blur_program:
                self.bloom_blur_program['horizontal'] = (i % 2 == 0)
            if self.bloom_blur_program and 'resolution' in self.bloom_blur_program:
                self.bloom_blur_program['resolution'] = (
                    current_target_texture.width,
                    current_target_texture.height
                )
            self.blur_vao.render(moderngl.TRIANGLE_STRIP)
            
            # Swap buffers
            if current_target_fbo == self.blur_fbo1:
                current_source = self.blur_texture1
                current_target_fbo = self.blur_fbo2
                current_target_texture = self.blur_texture2
            else:
                current_source = self.blur_texture2
                current_target_fbo = self.blur_fbo1
                current_target_texture = self.blur_texture1
        
        # Step 3: Combine original with blurred bright pixels
        self.final_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        source_texture.use(0)
        current_source.use(1)
        if self.bloom_combine_program and 'scene' in self.bloom_combine_program:
            self.bloom_combine_program['scene'] = 0
        if self.bloom_combine_program and 'bloom' in self.bloom_combine_program:
            self.bloom_combine_program['bloom'] = 1
        if self.bloom_combine_program and 'bloom_intensity' in self.bloom_combine_program:
            self.bloom_combine_program['bloom_intensity'] = BLOOM_INTENSITY
        self.combine_vao.render(moderngl.TRIANGLE_STRIP)
        
        return self.final_texture
    
    def update_time(self, dt: float):
        """Update time for animated effects"""
        self.time += dt
    
    def apply_style_effect(self, source_texture: moderngl.Texture) -> moderngl.Texture:
        """Apply style effect (scanlines, CRT, VHS) to source texture
        
        Args:
            source_texture: The texture to apply the effect to (typically after bloom)
            
        Returns:
            The texture with the style effect applied, or the original if no effect is enabled
        """
        if not self.style_effect_enabled or not self.style_effect_program:
            return self._apply_scanlines(source_texture)
        
        # Render style effect to output framebuffer
        self.style_effect_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        source_texture.use(0)
        
        if 'tex' in self.style_effect_program:
            self.style_effect_program['tex'] = 0
        if 'time' in self.style_effect_program:
            self.style_effect_program['time'] = self.time
        if 'resolution' in self.style_effect_program:
            self.style_effect_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.style_effect_vao.render(moderngl.TRIANGLE_STRIP)

        return self._apply_scanlines(self.style_effect_texture)

    def _apply_scanlines(self, source_texture: moderngl.Texture) -> moderngl.Texture:
        """Apply scanlines on top of source_texture if enabled"""
        if not self.scanlines_enabled or not self.scanlines_program or not self.scanlines_vao:
            return source_texture

        self.scanlines_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        source_texture.use(0)
        if 'tex' in self.scanlines_program:
            self.scanlines_program['tex'] = 0
        if 'time' in self.scanlines_program:
            self.scanlines_program['time'] = self.time
        if 'resolution' in self.scanlines_program:
            self.scanlines_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
        if 'scanlineThickness' in self.scanlines_program:
            self.scanlines_program['scanlineThickness'] = float(SCANLINE_THICKNESS)
        self.scanlines_vao.render(moderngl.TRIANGLE_STRIP)
        return self.scanlines_texture

    def toggle_scanlines(self) -> bool:
        """Toggle scanlines on/off. Returns new state."""
        if not self.scanlines_program:
            logger.warning("Scanlines shader not loaded, cannot toggle")
            return False
        self.scanlines_enabled = not self.scanlines_enabled
        logger.debug("Scanlines %s", "enabled" if self.scanlines_enabled else "disabled")
        return self.scanlines_enabled