#!/usr/bin/env python3
"""
Test script for text rendering cache functionality
"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
import moderngl
from src.managers.shader_manager import ShaderManager
from src.rendering.renderer import Renderer
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_PINK, COLOR_CYAN

def test_text_cache():
    """Test the text rendering cache functionality"""
    print("Initializing pygame...")
    pygame.init()

    print("Creating OpenGL context...")
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )
    
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN)
        ctx = moderngl.create_context()
    except Exception as e:
        print(f"Could not create display (expected in headless environment): {e}")
        print("Creating headless context...")
        ctx = moderngl.create_standalone_context()
    
    print("Creating renderer...")
    shader_manager = ShaderManager(ctx)
    renderer = Renderer(ctx, shader_manager)

    print("\n=== Testing text cache ===")
    
    # Initial state - cache should be empty
    stats = renderer.get_text_cache_stats()
    print(f"Initial cache size: {stats['surface_cache_size']}")
    assert stats['surface_cache_size'] == 0, "Cache should be empty initially"
    assert stats['texture_cache_size'] == 0, "Texture cache should be empty initially"
    
    # Render some text for the first time
    print("\n1. Rendering text first time...")
    renderer.begin_frame()
    renderer.draw_text("Hello World", 100, 100, 32, COLOR_CYAN)
    renderer.draw_text("Test Text", 200, 200, 48, COLOR_PINK)
    renderer.end_frame()
    
    stats = renderer.get_text_cache_stats()
    print(f"   After first render - Surface cache: {stats['surface_cache_size']} items")
    print(f"   Total accesses: {stats['total_accesses']}")
    assert stats['surface_cache_size'] == 2, f"Expected 2 cached items, got {stats['surface_cache_size']}"
    assert stats['total_accesses'] == 2, f"Expected 2 accesses, got {stats['total_accesses']}"
    
    # Render the same text again - should use cache
    print("\n2. Rendering same text again (should use cache)...")
    renderer.begin_frame()
    renderer.draw_text("Hello World", 100, 100, 32, COLOR_CYAN)
    renderer.draw_text("Test Text", 200, 200, 48, COLOR_PINK)
    renderer.end_frame()
    
    stats = renderer.get_text_cache_stats()
    print(f"   After second render - Surface cache: {stats['surface_cache_size']} items")
    print(f"   Total accesses: {stats['total_accesses']}")
    assert stats['surface_cache_size'] == 2, f"Expected 2 cached items, got {stats['surface_cache_size']}"
    assert stats['total_accesses'] == 4, f"Expected 4 accesses, got {stats['total_accesses']}"
    
    # Render different text
    print("\n3. Rendering different text...")
    renderer.begin_frame()
    renderer.draw_text("New Text", 300, 300, 32, COLOR_CYAN)
    renderer.end_frame()
    
    stats = renderer.get_text_cache_stats()
    print(f"   After new text - Surface cache: {stats['surface_cache_size']} items")
    print(f"   Total accesses: {stats['total_accesses']}")
    assert stats['surface_cache_size'] == 3, f"Expected 3 cached items, got {stats['surface_cache_size']}"
    assert stats['total_accesses'] == 5, f"Expected 5 accesses, got {stats['total_accesses']}"
    
    # Test cache with different colors (should create new entry)
    print("\n4. Testing same text with different color...")
    renderer.begin_frame()
    renderer.draw_text("Hello World", 100, 100, 32, COLOR_PINK)  # Different color
    renderer.end_frame()
    
    stats = renderer.get_text_cache_stats()
    print(f"   After color change - Surface cache: {stats['surface_cache_size']} items")
    print(f"   Total accesses: {stats['total_accesses']}")
    assert stats['surface_cache_size'] == 4, f"Expected 4 cached items (color is part of key), got {stats['surface_cache_size']}"
    
    # Test cache with different sizes (should create new entry)
    print("\n5. Testing same text with different size...")
    renderer.begin_frame()
    renderer.draw_text("Hello World", 100, 100, 64, COLOR_CYAN)  # Different size
    renderer.end_frame()
    
    stats = renderer.get_text_cache_stats()
    print(f"   After size change - Surface cache: {stats['surface_cache_size']} items")
    print(f"   Total accesses: {stats['total_accesses']}")
    assert stats['surface_cache_size'] == 5, f"Expected 5 cached items (size is part of key), got {stats['surface_cache_size']}"
    
    # Test cache management - add many items to trigger cleanup
    print("\n6. Testing cache cleanup (adding many items)...")
    initial_size = stats['surface_cache_size']
    renderer.max_cache_size = 10  # Set low limit for testing
    
    for i in range(20):
        renderer.begin_frame()
        renderer.draw_text(f"Item {i}", 100, 100, 32, COLOR_CYAN)
        renderer.end_frame()
    
    stats = renderer.get_text_cache_stats()
    print(f"   After adding many items - Surface cache: {stats['surface_cache_size']} items")
    print(f"   Max cache size: {stats['max_cache_size']}")
    assert stats['surface_cache_size'] <= renderer.max_cache_size, \
        f"Cache size {stats['surface_cache_size']} exceeds max {renderer.max_cache_size}"
    
    print("\n✓ All cache tests passed!")
    print("\nFinal cache statistics:")
    print(f"  Surface cache: {stats['surface_cache_size']} items")
    print(f"  Texture cache: {stats['texture_cache_size']} items")
    print(f"  Max size: {stats['max_cache_size']}")
    print(f"  Total accesses: {stats['total_accesses']}")
    
    pygame.quit()

if __name__ == "__main__":
    test_text_cache()
