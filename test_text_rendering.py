#!/usr/bin/env python3
"""
Test script for text rendering functionality
"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import moderngl
from src.managers.shader_manager import ShaderManager
from src.rendering.renderer import Renderer
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_PINK, COLOR_CYAN, COLOR_YELLOW

def test_text_rendering():
    """Test the text rendering functionality"""
    print("Initializing pygame...")
    pygame.init()
    
    print("Creating OpenGL context...")
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    ctx = moderngl.create_context()
    
    print("Creating renderer...")
    shader_manager = ShaderManager(ctx)
    renderer = Renderer(ctx, shader_manager)
    
    print("Testing text rendering...")
    renderer.begin_frame()
    
    # Test various text sizes and colors
    renderer.draw_text("NEON PONG", WINDOW_WIDTH // 2, 100, 72, COLOR_PINK, centered=True)
    renderer.draw_text("Start Game", WINDOW_WIDTH // 2, 300, 48, COLOR_YELLOW, centered=True)
    renderer.draw_text("Quit", WINDOW_WIDTH // 2, 380, 48, COLOR_CYAN, centered=True)
    renderer.draw_text("Player 1: W/S", 100, 550, 24, COLOR_CYAN)
    renderer.draw_text("Player 2: UP/DOWN", WINDOW_WIDTH - 300, 550, 24, COLOR_PINK)
    
    # Test score rendering
    renderer.draw_text("0", WINDOW_WIDTH // 4, 50, 64, COLOR_CYAN, centered=True)
    renderer.draw_text("0", WINDOW_WIDTH * 3 // 4, 50, 64, COLOR_PINK, centered=True)
    
    renderer.end_frame()
    
    # Save a screenshot
    print("Saving screenshot...")
    pygame.image.save(screen, "/tmp/text_rendering_test.png")
    
    print("Text rendering test completed successfully!")
    print("Textures cached:", len(renderer.text_texture_cache))
    
    pygame.quit()

if __name__ == "__main__":
    test_text_rendering()
