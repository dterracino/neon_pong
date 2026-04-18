"""
Visual demo of sprite rendering - shows sprites with and without fallback
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import moderngl
from src.managers.asset_manager import AssetManager
from src.managers.shader_manager import ShaderManager
from src.rendering.renderer import Renderer
from src.entities.paddle import Paddle
from src.entities.ball import Ball
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT

def main():
    """Visual demo showing sprite rendering"""
    pygame.init()
    
    # Create OpenGL context
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )
    
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.OPENGL | pygame.DOUBLEBUF
    )
    pygame.display.set_caption("Sprite Rendering Demo")
    
    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    
    # Initialize managers
    asset_manager = AssetManager()
    asset_manager.preload_images()
    
    shader_manager = ShaderManager(ctx)
    renderer = Renderer(ctx, shader_manager)
    
    # Create entities
    # Left side - with sprites
    paddle1_sprite = Paddle(100, WINDOW_HEIGHT // 2 - 50, 1)
    paddle1_sprite.set_sprite(asset_manager.get_image('paddle1'))
    
    ball_sprite = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    ball_sprite.set_sprite(asset_manager.get_image('ball'))
    
    paddle2_sprite = Paddle(WINDOW_WIDTH - 140, WINDOW_HEIGHT // 2 - 50, 2)
    paddle2_sprite.set_sprite(asset_manager.get_image('paddle2'))
    
    # Right side - without sprites (procedural)
    paddle1_proc = Paddle(250, WINDOW_HEIGHT // 2 - 50, 1)
    ball_proc = Ball(WINDOW_WIDTH // 2 + 150, WINDOW_HEIGHT // 2)
    paddle2_proc = Paddle(WINDOW_WIDTH - 280, WINDOW_HEIGHT // 2 - 50, 2)
    
    clock = pygame.time.Clock()
    running = True
    
    print("\n" + "="*60)
    print("Sprite Rendering Demo")
    print("="*60)
    print("\nLeft side: Sprite-based rendering")
    print("Right side: Procedural rendering (fallback)")
    print("\nPress ESC to exit")
    print("="*60 + "\n")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Left side - SPRITE RENDERING
        # Draw label
        # Note: We'd need text rendering here, but for now just draw the sprites
        
        # Draw paddle1 with sprite
        if paddle1_sprite.sprite:
            renderer.draw_sprite(
                paddle1_sprite.sprite,
                paddle1_sprite.x,
                paddle1_sprite.y,
                paddle1_sprite.width,
                paddle1_sprite.height,
                paddle1_sprite.get_color()
            )
        
        # Draw ball with sprite (with simple "trail" effect)
        for i in range(3):
            alpha = (i + 1) / 3 * 0.5
            color = (*ball_sprite.color[:3], alpha)
            offset = i * 15
            if ball_sprite.sprite:
                renderer.draw_sprite(
                    ball_sprite.sprite,
                    ball_sprite.x - offset,
                    ball_sprite.y,
                    ball_sprite.size * (i + 1) / 3,
                    ball_sprite.size * (i + 1) / 3,
                    color
                )
        
        # Draw ball main sprite
        if ball_sprite.sprite:
            renderer.draw_sprite(
                ball_sprite.sprite,
                ball_sprite.x,
                ball_sprite.y,
                ball_sprite.size,
                ball_sprite.size,
                ball_sprite.color
            )
        
        # Draw paddle2 with sprite
        if paddle2_sprite.sprite:
            renderer.draw_sprite(
                paddle2_sprite.sprite,
                paddle2_sprite.x,
                paddle2_sprite.y,
                paddle2_sprite.width,
                paddle2_sprite.height,
                paddle2_sprite.get_color()
            )
        
        # Right side - PROCEDURAL RENDERING (fallback)
        # Draw paddle1 procedural
        renderer.draw_rect(
            paddle1_proc.x,
            paddle1_proc.y,
            paddle1_proc.width,
            paddle1_proc.height,
            paddle1_proc.get_color()
        )
        
        # Draw ball trail procedural
        for i in range(3):
            alpha = (i + 1) / 3 * 0.5
            color = (*ball_proc.color[:3], alpha)
            offset = i * 15
            size = ball_proc.size * (i + 1) / 3
            renderer.draw_circle(
                ball_proc.x + ball_proc.size/2 - offset,
                ball_proc.y + ball_proc.size/2,
                size / 2,
                color
            )
        
        # Draw ball main procedural
        renderer.draw_circle(
            ball_proc.x + ball_proc.size / 2,
            ball_proc.y + ball_proc.size / 2,
            ball_proc.size / 2,
            ball_proc.color
        )
        
        # Draw paddle2 procedural
        renderer.draw_rect(
            paddle2_proc.x,
            paddle2_proc.y,
            paddle2_proc.width,
            paddle2_proc.height,
            paddle2_proc.get_color()
        )
        
        # Swap buffers
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == '__main__':
    main()
