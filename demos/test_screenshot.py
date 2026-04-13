#!/usr/bin/env python3
"""
Test script for screenshot functionality
"""
import os
import sys

# Disable audio for testing
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import moderngl
from src.managers.shader_manager import ShaderManager
from src.rendering.renderer import Renderer
from src.utils.screenshot import ScreenshotManager
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_PINK, COLOR_CYAN, COLOR_YELLOW


def test_screenshot():
    """Test the screenshot functionality"""
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
    pygame.display.set_caption("Screenshot Test")
    ctx = moderngl.create_context()

    print("Creating renderer...")
    shader_manager = ShaderManager(ctx)
    renderer = Renderer(ctx, shader_manager)

    print("Creating screenshot manager...")
    screenshot_manager = ScreenshotManager("test_screenshots")

    print("Rendering test content...")
    renderer.begin_frame()
    
    # Draw some test content
    renderer.draw_text("Screenshot Test", WINDOW_WIDTH // 2, 100, 72, COLOR_PINK, centered=True)
    renderer.draw_text("Press Ctrl-S to capture", WINDOW_WIDTH // 2, 300, 48, COLOR_YELLOW, centered=True)
    renderer.draw_text("Test 1", 100, 400, 32, COLOR_CYAN)
    renderer.draw_text("Test 2", WINDOW_WIDTH - 200, 400, 32, COLOR_PINK)
    
    renderer.end_frame()
    pygame.display.flip()

    print("\n=== Instructions ===")
    print("1. You should see a window with colorful text")
    print("2. Press Ctrl-S to capture a screenshot")
    print("3. Press ESC to exit")
    print("4. Check the test_screenshots directory for saved images")
    print("====================\n")

    # Main loop
    clock = pygame.time.Clock()
    running = True
    screenshot_count = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                    # Test screenshot capture
                    try:
                        filepath = screenshot_manager.capture(screen)
                        screenshot_count += 1
                        print(f"Screenshot {screenshot_count} saved: {filepath}")
                    except Exception as e:
                        print(f"Failed to capture screenshot: {e}")
        
        clock.tick(60)
    
    print(f"\nTest completed. Total screenshots captured: {screenshot_count}")
    
    # Verify screenshots directory exists
    if os.path.exists("test_screenshots"):
        screenshots = [f for f in os.listdir("test_screenshots") if f.endswith('.png')]
        print(f"Screenshots in directory: {len(screenshots)}")
        if screenshots:
            print("Screenshot files:")
            for f in screenshots:
                print(f"  - {f}")
    else:
        print("No screenshots directory created")
    
    pygame.quit()
    print("Screenshot test completed successfully!")


if __name__ == "__main__":
    test_screenshot()
