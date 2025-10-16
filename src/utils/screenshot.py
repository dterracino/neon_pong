"""
Screenshot utility for capturing game screen
"""
import os
import logging
from datetime import datetime
from typing import Optional
import pygame
import numpy as np

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Handles screenshot capture and saving"""
    
    def __init__(self, screenshots_dir: str = "screenshots", ctx=None):
        """
        Initialize screenshot manager
        
        Args:
            screenshots_dir: Directory to save screenshots (relative to project root)
            ctx: ModernGL context for reading OpenGL framebuffer
        """
        self.screenshots_dir = screenshots_dir
        self.ctx = ctx
        self.last_screenshot: Optional[pygame.Surface] = None
        logger.debug("ScreenshotManager initialized with directory: %s", screenshots_dir)
    
    def set_context(self, ctx):
        """
        Set the ModernGL context for reading OpenGL framebuffer
        
        Args:
            ctx: ModernGL context
        """
        self.ctx = ctx
        logger.debug("ModernGL context set for screenshot manager")
    
    def capture_to_memory(self, screen: pygame.Surface) -> pygame.Surface:
        """
        Capture screenshot to memory without saving to disk
        
        Args:
            screen: Pygame surface to capture (used for size info)
            
        Returns:
            Copy of the screen surface with OpenGL content
        """
        if self.ctx is None:
            logger.warning("No ModernGL context available, capturing empty surface")
            screenshot = screen.copy()
        else:
            # Read from OpenGL framebuffer instead of pygame surface
            width, height = screen.get_size()
            
            # Read RGBA data from OpenGL framebuffer
            buffer = self.ctx.screen.read(components=4)
            
            # Convert to numpy array and flip vertically (OpenGL origin is bottom-left)
            pixels = np.frombuffer(buffer, dtype='u1').reshape((height, width, 4))
            pixels = np.flipud(pixels)  # Flip vertically
            
            # Create pygame surface from the flipped data
            screenshot = pygame.image.frombuffer(pixels.tobytes(), (width, height), 'RGBA')
            screenshot = screenshot.convert_alpha()
        
        self.last_screenshot = screenshot
        logger.debug("Screenshot captured to memory from OpenGL framebuffer")
        return screenshot
    
    def capture(self, screen: pygame.Surface, save_to_disk: bool = True) -> str:
        """
        Capture and save a screenshot
        
        Args:
            screen: Pygame surface to capture (used for size info)
            save_to_disk: If True, saves to disk. If False, only captures to memory.
            
        Returns:
            Path to saved screenshot file (or empty string if not saved to disk)
        """
        # Always capture to memory (which reads from OpenGL framebuffer)
        screenshot = self.capture_to_memory(screen)
        
        if not save_to_disk:
            return ""
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Generate filename with timestamp including microseconds for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        # Save screenshot
        try:
            pygame.image.save(screenshot, filepath)
            logger.info("Screenshot saved to: %s", filepath)
            return filepath
        except Exception as e:
            logger.error("Failed to save screenshot: %s", e)
            raise
    
    def get_last_screenshot(self) -> Optional[pygame.Surface]:
        """
        Get the last captured screenshot from memory
        
        Returns:
            Last screenshot surface or None if no screenshot has been captured
        """
        return self.last_screenshot
