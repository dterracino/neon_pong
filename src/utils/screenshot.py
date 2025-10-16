"""
Screenshot utility for capturing game screen
"""
import os
import logging
from datetime import datetime
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
        logger.debug("ScreenshotManager initialized with directory: %s", screenshots_dir)
    
    def capture(self, screen: pygame.Surface) -> str:
        """
        Capture and save a screenshot
        
        Args:
            screen: Pygame surface to capture
            
        Returns:
            Path to saved screenshot file
        """
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
