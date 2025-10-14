#!/usr/bin/env python3
"""
Unit test for text rendering API
"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

def test_font_loading():
    """Test that pygame fonts can be loaded"""
    pygame.init()
    
    # Test default font
    font = pygame.font.Font(None, 32)
    assert font is not None, "Failed to load default font"
    print("✓ Default font loaded successfully")
    
    # Test various sizes
    for size in [24, 32, 48, 64, 72]:
        font = pygame.font.Font(None, size)
        assert font is not None, f"Failed to load font size {size}"
        print(f"✓ Font size {size} loaded successfully")
    
    # Test rendering text
    font = pygame.font.Font(None, 48)
    text_surface = font.render("Test Text", True, (255, 255, 255))
    assert text_surface is not None, "Failed to render text"
    assert text_surface.get_width() > 0, "Text surface has no width"
    assert text_surface.get_height() > 0, "Text surface has no height"
    print(f"✓ Text rendered successfully: {text_surface.get_size()}")
    
    # Test converting to string format for texture
    text_data = pygame.image.tostring(text_surface, 'RGBA', True)
    assert len(text_data) > 0, "Failed to convert text to texture data"
    print(f"✓ Text converted to texture data: {len(text_data)} bytes")
    
    pygame.quit()
    print("\n✓ All font loading tests passed!")

if __name__ == "__main__":
    test_font_loading()
