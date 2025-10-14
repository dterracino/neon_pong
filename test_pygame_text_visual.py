#!/usr/bin/env python3
"""
Test script to verify pygame text rendering produces visible output
This creates a simple image file to visually verify text is being rendered
"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import sys

def test_pygame_text_rendering():
    """Test that pygame can render text to a surface"""
    print("Initializing pygame...")
    pygame.init()
    
    # Create a surface
    width, height = 800, 600
    surface = pygame.Surface((width, height))
    
    # Fill with dark purple background (like the game)
    surface.fill((13, 5, 38))  # 0.05, 0.02, 0.15 * 255
    
    print("Rendering text...")
    
    # Create font
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 24)
    
    # Define colors (0-255 range for pygame)
    COLOR_PINK = (255, 0, 255)
    COLOR_CYAN = (0, 255, 255)
    COLOR_YELLOW = (255, 255, 0)
    
    # Render text surfaces
    texts = [
        (font_large.render("NEON PONG", True, COLOR_PINK), (width // 2, 100)),
        (font_medium.render("Start Game", True, COLOR_YELLOW), (width // 2, 300)),
        (font_medium.render("Quit", True, COLOR_CYAN), (width // 2, 380)),
        (font_small.render("Player 1: W/S", True, COLOR_CYAN), (100, 550)),
        (font_small.render("Player 2: UP/DOWN", True, COLOR_PINK), (width - 300, 550)),
        (font_large.render("0", True, COLOR_CYAN), (width // 4, 50)),
        (font_large.render("0", True, COLOR_PINK), (width * 3 // 4, 50)),
    ]
    
    # Blit text to surface
    for text_surface, pos in texts:
        # Center text
        text_rect = text_surface.get_rect()
        text_rect.center = pos
        surface.blit(text_surface, text_rect)
    
    # Save to file
    import tempfile
    output_path = os.path.join(tempfile.gettempdir(), "pygame_text_test.png")
    pygame.image.save(surface, output_path)
    print(f"✓ Saved test image to {output_path}")
    
    # Check if any non-background pixels exist
    import numpy as np
    pixel_data = pygame.surfarray.array3d(surface)
    background_color = np.array([13, 5, 38])
    
    # Count non-background pixels (efficient numpy operation)
    non_bg_mask = np.any(pixel_data != background_color, axis=2)
    non_bg_pixels = np.count_nonzero(non_bg_mask)
    total_pixels = width * height
    
    print(f"\nPixel analysis:")
    print(f"  Total pixels: {total_pixels}")
    print(f"  Non-background pixels: {non_bg_pixels}")
    print(f"  Coverage: {non_bg_pixels / total_pixels * 100:.2f}%")
    
    if non_bg_pixels > 0:
        print("\n✓ Text is being rendered by pygame!")
        print(f"  The image should show colored text on a dark purple background.")
    else:
        print("\n✗ No text pixels found - pygame rendering may be broken!")
        return False
    
    pygame.quit()
    return True

if __name__ == "__main__":
    success = test_pygame_text_rendering()
    sys.exit(0 if success else 1)
