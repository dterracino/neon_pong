"""
Quick test of draw_text_direct to verify text rendering
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import moderngl
import time

def test_text_direct():
    """Test draw_text_direct rendering"""
    pygame.init()
    
    # Create minimal OpenGL context
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )
    
    screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Text Rendering Test")
    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    
    from src.managers.asset_manager import AssetManager
    from src.managers.shader_manager import ShaderManager
    from src.rendering.renderer import Renderer
    
    asset_manager = AssetManager()
    shader_manager = ShaderManager(ctx)
    renderer = Renderer(ctx, shader_manager, asset_manager)
    
    print("\n" + "="*60)
    print("Text Rendering Test")
    print("="*60)
    print("\nRendering text with draw_text_direct...")
    print("Press ESC to exit")
    print("="*60 + "\n")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        ctx.clear(0.1, 0.1, 0.2, 1.0)
        
        # Test various text rendering
        # White text
        renderer.draw_text_direct(
            "White Text (Default)",
            50, 50, 24,
            (1.0, 1.0, 1.0, 1.0)
        )
        
        # Yellow text
        renderer.draw_text_direct(
            "Yellow Text",
            50, 100, 24,
            (1.0, 1.0, 0.0, 1.0)
        )
        
        # Cyan text with sys font
        renderer.draw_text_direct(
            "Cyan Text (Arial)",
            50, 150, 24,
            (0.0, 0.8, 0.996, 1.0),
            font_name="sys:arial"
        )
        
        # Pink text with semi-transparency
        renderer.draw_text_direct(
            "Pink Semi-Transparent",
            50, 200, 24,
            (1.0, 0.44, 0.81, 0.7)
        )
        
        # Simulated achievement toast
        renderer.draw_text_direct(
            "ACHIEVEMENT UNLOCKED",
            50, 300, 16,
            (0.0, 0.8, 0.996, 1.0),
            font_name="sys:arial"
        )
        renderer.draw_text_direct(
            "Test Achievement",
            50, 330, 22,
            (1.0, 0.9, 0.2, 1.0),
            font_name="sys:arial"
        )
        renderer.draw_text_direct(
            "This is a test description",
            50, 360, 16,
            (0.8, 0.8, 0.8, 1.0),
            font_name="sys:arial"
        )
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\nTest completed")

if __name__ == '__main__':
    test_text_direct()
