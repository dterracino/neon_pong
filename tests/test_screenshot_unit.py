#!/usr/bin/env python3
"""
Unit test for screenshot manager (no OpenGL required)
"""
import os
import sys
import tempfile
import shutil

# Disable audio for testing
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from src.utils.screenshot import ScreenshotManager


def test_screenshot_manager():
    """Test screenshot manager functionality"""
    print("Testing ScreenshotManager...")
    
    # Create a temporary directory for screenshots
    temp_dir = tempfile.mkdtemp(prefix="test_screenshots_")
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        # Initialize pygame
        pygame.init()
        
        # Create a simple surface (no OpenGL needed)
        width, height = 800, 600
        screen = pygame.Surface((width, height))
        
        # Draw something on the surface
        screen.fill((10, 5, 30))  # Dark background
        pygame.draw.circle(screen, (255, 113, 206), (width//2, height//2), 100)  # Pink circle
        pygame.draw.rect(screen, (1, 205, 254), (50, 50, 100, 100))  # Cyan rectangle
        
        # Create screenshot manager
        screenshot_manager = ScreenshotManager(temp_dir)
        
        # Capture screenshot
        print("Capturing screenshot...")
        filepath = screenshot_manager.capture(screen)
        
        # Verify screenshot was created
        assert os.path.exists(filepath), f"Screenshot file not found: {filepath}"
        print(f"✓ Screenshot saved: {filepath}")
        
        # Verify file is not empty
        file_size = os.path.getsize(filepath)
        assert file_size > 0, "Screenshot file is empty"
        print(f"✓ Screenshot file size: {file_size} bytes")
        
        # Verify filename format
        filename = os.path.basename(filepath)
        assert filename.startswith("screenshot_"), "Filename doesn't have correct prefix"
        assert filename.endswith(".png"), "Filename doesn't have .png extension"
        print(f"✓ Filename format correct: {filename}")
        
        # Test multiple screenshots
        print("\nTesting multiple screenshots...")
        filepath2 = screenshot_manager.capture(screen)
        assert filepath != filepath2, "Multiple screenshots should have different filenames"
        print(f"✓ Second screenshot saved: {os.path.basename(filepath2)}")
        
        # Verify both files exist
        screenshots = [f for f in os.listdir(temp_dir) if f.endswith('.png')]
        assert len(screenshots) == 2, f"Expected 2 screenshots, found {len(screenshots)}"
        print(f"✓ Both screenshots exist in directory")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        pygame.quit()
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary directory: {temp_dir}")


if __name__ == "__main__":
    success = test_screenshot_manager()
    sys.exit(0 if success else 1)
