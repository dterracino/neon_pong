#!/usr/bin/env python3
"""
Test script for font preloading functionality
"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from src.managers.asset_manager import AssetManager

def test_font_preloading():
    """Test the font preloading functionality"""
    print("Initializing pygame...")
    pygame.init()
    
    print("\nTesting font preloading...")
    asset_manager = AssetManager()
    
    # Test preloading with empty fonts directory
    print("\n1. Testing with empty fonts directory:")
    initial_font_count = len(asset_manager.fonts)
    print(f"   Initial cached fonts: {initial_font_count}")
    
    asset_manager.preload_fonts_from_directory()
    
    post_preload_count = len(asset_manager.fonts)
    print(f"   Fonts after preload: {post_preload_count}")
    
    # Test that default font can still be loaded
    print("\n2. Testing default font loading:")
    font = asset_manager.get_font(None, 48)
    print(f"   ✓ Default font loaded at size 48")
    
    # Test specific sizes
    print("\n3. Testing multiple sizes of default font:")
    for size in [24, 32, 48, 64, 72]:
        font = asset_manager.get_font(None, size)
        assert font is not None
        print(f"   ✓ Default font size {size} loaded")
    
    print(f"\n   Total cached fonts: {len(asset_manager.fonts)}")
    
    pygame.quit()
    print("\n✓ Font preloading test completed successfully!")

if __name__ == "__main__":
    test_font_preloading()
