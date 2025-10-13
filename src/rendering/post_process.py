"""
Post-processing effects using ModernGL
"""
import moderngl
from src.managers.shader_manager import ShaderManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, BLOOM_BLUR_PASSES
import numpy as np


class PostProcessor:
    """Handles post-processing effects like bloom"""
    
    def __init__(self, ctx: moderngl.Context, shader_manager: ShaderManager):
        print("[DEBUG] PostProcessor.__init__: Initializing post processor...")
        self.ctx = ctx
        self.shader_manager = shader_manager
        
        # Load shaders
        print("[DEBUG] PostProcessor.__init__: Loading bloom shaders...")
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
            print("[DEBUG] PostProcessor.__init__: All bloom shaders loaded successfully")
        else:
            print("[WARNING] PostProcessor.__init__: Some bloom shaders failed to load")
        
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
        print("[DEBUG] PostProcessor.__init__: Post processor initialization complete!")
    
    def apply_bloom(self, source_texture: moderngl.Texture) -> moderngl.Texture:
        """Apply bloom effect to source texture"""
        # If shaders aren't loaded, return original
        if not all([self.bloom_extract_program, self.bloom_blur_program, self.bloom_combine_program]):
            print("[WARNING] PostProcessor.apply_bloom: Bloom shaders not loaded, returning original texture")
            return source_texture
        
        # Step 1: Extract bright pixels
        self.bright_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        source_texture.use(0)
        if self.bloom_extract_program and 'tex' in self.bloom_extract_program:
            self.bloom_extract_program['tex'].value = 0  # type: ignore[union-attr]
        if self.bloom_extract_program and 'threshold' in self.bloom_extract_program:
            self.bloom_extract_program['threshold'].value = 0.7  # type: ignore[union-attr]
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
                self.bloom_blur_program['tex'].value = 0  # type: ignore[union-attr]
            if self.bloom_blur_program and 'horizontal' in self.bloom_blur_program:
                self.bloom_blur_program['horizontal'].value = (i % 2 == 0)  # type: ignore[union-attr]
            if self.bloom_blur_program and 'resolution' in self.bloom_blur_program:
                self.bloom_blur_program['resolution'].value = (  # type: ignore[union-attr]
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
            self.bloom_combine_program['scene'].value = 0  # type: ignore[union-attr]
        if self.bloom_combine_program and 'bloom' in self.bloom_combine_program:
            self.bloom_combine_program['bloom'].value = 1  # type: ignore[union-attr]
        if self.bloom_combine_program and 'bloom_intensity' in self.bloom_combine_program:
            self.bloom_combine_program['bloom_intensity'].value = 1.5  # type: ignore[union-attr]
        self.combine_vao.render(moderngl.TRIANGLE_STRIP)
        
        return self.final_texture