"""
Screenshot utility for capturing game screen
"""
import os
import logging
from datetime import datetime
from typing import Optional
import pygame

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Handles screenshot capture and saving"""
    
    def __init__(self, screenshots_dir: str = "screenshots"):
        """
        Initialize screenshot manager
        
        Args:
            screenshots_dir: Directory to save screenshots (relative to project root)
        """
        self.screenshots_dir = screenshots_dir
        self.last_screenshot: Optional[pygame.Surface] = None
        logger.debug("ScreenshotManager initialized with directory: %s", screenshots_dir)
    
    def capture_to_memory(self, screen: pygame.Surface) -> pygame.Surface:
        """
        Capture screenshot to memory without saving to disk
        
        Args:
            screen: Pygame surface to capture
            
        Returns:
            Copy of the screen surface
        """
        # Create a copy of the screen
        screenshot = screen.copy()
        self.last_screenshot = screenshot
        logger.debug("Screenshot captured to memory")
        return screenshot
    
    def capture(self, screen: pygame.Surface, save_to_disk: bool = True) -> str:
        """
        Capture and save a screenshot
        
        Args:
            screen: Pygame surface to capture
            save_to_disk: If True, saves to disk. If False, only captures to memory.
            
        Returns:
            Path to saved screenshot file (or empty string if not saved to disk)
        """
        # Always capture to memory
        self.capture_to_memory(screen)
        
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
            pygame.image.save(screen, filepath)
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
