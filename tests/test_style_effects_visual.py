#!/usr/bin/env python3
"""
Visual test for post-processing style effects.
Displays a test pattern with each effect to verify they work correctly.
Press SPACE to cycle through effects, ESC to quit.
"""
import sys
import os
import pygame
import moderngl
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.managers.shader_manager import ShaderManager
from src.rendering.post_process import PostProcessor
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT

def create_test_pattern(ctx):
    """Create a colorful test pattern texture"""
    # Create a test pattern with gradient and some bright spots
    width, height = WINDOW_WIDTH, WINDOW_HEIGHT
    data = np.zeros((height, width, 4), dtype=np.float32)
    
    for y in range(height):
        for x in range(width):
            # Gradient background
            data[y, x, 0] = x / width * 0.5  # Red gradient
            data[y, x, 1] = y / height * 0.5  # Green gradient
            data[y, x, 2] = 0.3  # Blue constant
            data[y, x, 3] = 1.0  # Alpha
            
            # Add some bright spots for bloom
            spot1_dist = ((x - width * 0.3)**2 + (y - height * 0.3)**2) ** 0.5
            if spot1_dist < 50:
                intensity = (50 - spot1_dist) / 50
                data[y, x, 0] += intensity * 0.8  # Bright pink
                data[y, x, 1] += intensity * 0.2
                data[y, x, 2] += intensity * 0.5
                
            spot2_dist = ((x - width * 0.7)**2 + (y - height * 0.5)**2) ** 0.5
            if spot2_dist < 40:
                intensity = (40 - spot2_dist) / 40
                data[y, x, 0] += intensity * 0.2
                data[y, x, 1] += intensity * 0.8  # Bright cyan
                data[y, x, 2] += intensity * 0.9
                
            spot3_dist = ((x - width * 0.5)**2 + (y - height * 0.7)**2) ** 0.5
            if spot3_dist < 60:
                intensity = (60 - spot3_dist) / 60
                data[y, x, 0] += intensity * 0.7  # Bright purple
                data[y, x, 1] += intensity * 0.3
                data[y, x, 2] += intensity * 0.9
    
    # Clamp values
    data = np.clip(data, 0.0, 1.0)
    
    # Create texture
    texture = ctx.texture((width, height), 4, data.tobytes(), dtype='f4')
    return texture

def main():
    """Run the visual test"""
    print("Post-Processing Style Effects Visual Test")
    print("=========================================")
    print("Press SPACE to cycle through effects")
    print("Press ESC to quit")
    print()
    
    # Initialize Pygame
    pygame.init()
    
    # Create OpenGL window
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.OPENGL | pygame.DOUBLEBUF
    )
    pygame.display.set_caption("Style Effects Visual Test")
    
    # Create ModernGL context
    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    
    # Initialize shader manager and post processor
    shader_manager = ShaderManager(ctx)
    
    # Create test pattern
    test_texture = create_test_pattern(ctx)
    
    # Load basic shader for displaying textures
    basic_program = shader_manager.load_shader('basic', 'basic.vert', 'basic.frag')
    if not basic_program:
        print("Failed to load basic shader!")
        return
    
    # Create fullscreen quad
    vertices = np.array([
        -1.0, -1.0,
         1.0, -1.0,
        -1.0,  1.0,
         1.0,  1.0,
    ], dtype='f4')
    quad_vbo = ctx.buffer(vertices.tobytes())
    quad_vao = ctx.simple_vertex_array(basic_program, quad_vbo, 'in_position')
    
    # Effects to cycle through
    effects = ["none", "scanlines", "crt", "vhs"]
    current_effect_idx = 0
    
    # We'll manually create post processors for each effect
    effect_processors = {}
    
    for effect in effects:
        # Temporarily set the constant
        import src.utils.constants as constants
        original_effect = constants.POST_EFFECT_TYPE
        constants.POST_EFFECT_TYPE = effect
        
        # Create post processor
        processor = PostProcessor(ctx, shader_manager)
        effect_processors[effect] = processor
        
        # Restore original
        constants.POST_EFFECT_TYPE = original_effect
    
    clock = pygame.time.Clock()
    running = True
    time = 0.0
    
    print(f"\nCurrent effect: {effects[current_effect_idx]}")
    
    while running:
        dt = clock.tick(60) / 1000.0
        time += dt
        
        # Update all processors' time
        for processor in effect_processors.values():
            processor.update_time(dt)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Cycle to next effect
                    current_effect_idx = (current_effect_idx + 1) % len(effects)
                    print(f"Current effect: {effects[current_effect_idx]}")
        
        # Get current effect processor
        current_effect = effects[current_effect_idx]
        processor = effect_processors[current_effect]
        
        # Apply bloom to test pattern
        bloomed = processor.apply_bloom(test_texture)
        
        # Apply style effect
        final = processor.apply_style_effect(bloomed)
        
        # Render to screen
        ctx.screen.use()
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        final.use(0)
        basic_program['tex'] = 0
        basic_program['color'] = (1.0, 1.0, 1.0, 1.0)
        quad_vao.render(moderngl.TRIANGLE_STRIP)
        
        pygame.display.flip()
    
    # Cleanup
    test_texture.release()
    quad_vao.release()
    quad_vbo.release()
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
