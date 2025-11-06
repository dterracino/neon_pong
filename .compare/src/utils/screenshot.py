"""
Screenshot utility for capturing game screen
"""
import os
import logging
from datetime import datetime
from typing import Optional, Literal
from enum import Enum
import pygame
import numpy as np

logger = logging.getLogger(__name__)


class CaptureMethod(Enum):
    """Enum for screenshot capture methods"""
    AUTO = "auto"  # Auto-detect based on available context
    OPENGL = "opengl"  # Use OpenGL framebuffer reading
    PYGAME = "pygame"  # Use pygame surface copy


class ScreenshotManager:
    """Handles screenshot capture and saving"""
    
    def __init__(self, screenshots_dir: str = "screenshots", ctx=None, 
                 capture_method: CaptureMethod = CaptureMethod.AUTO):
        """
        Initialize screenshot manager
        
        Args:
            screenshots_dir: Directory to save screenshots (relative to project root)
            ctx: ModernGL context for reading OpenGL framebuffer (optional)
            capture_method: Method to use for capturing screenshots (AUTO, OPENGL, or PYGAME)
        """
        self.screenshots_dir = screenshots_dir
        self.ctx = ctx
        self.capture_method = capture_method
        self.last_screenshot: Optional[pygame.Surface] = None
        self._detected_method: Optional[CaptureMethod] = None
        logger.debug("ScreenshotManager initialized with directory: %s, method: %s", 
                    screenshots_dir, capture_method.value)
    
    def set_context(self, ctx):
        """
        Set the ModernGL context for reading OpenGL framebuffer
        
        Args:
            ctx: ModernGL context
        """
        self.ctx = ctx
        self._detected_method = None  # Reset detection on context change
        logger.debug("ModernGL context set for screenshot manager")
    
    def _detect_capture_method(self, screen: pygame.Surface) -> CaptureMethod:
        """
        Auto-detect the appropriate capture method
        
        Args:
            screen: Pygame surface
            
        Returns:
            Detected capture method (OPENGL or PYGAME)
        """
        if self._detected_method is not None:
            return self._detected_method
        
        # Check if we have OpenGL context and if the window is using OpenGL
        if self.ctx is not None:
            try:
                # Try to check if screen was created with OPENGL flag
                # pygame doesn't expose this directly, so we check if context works
                _ = self.ctx.screen
                self._detected_method = CaptureMethod.OPENGL
                logger.debug("Auto-detected capture method: OPENGL")
                return CaptureMethod.OPENGL
            except Exception as e:
                logger.debug("OpenGL context check failed: %s, using pygame", e)
        
        self._detected_method = CaptureMethod.PYGAME
        logger.debug("Auto-detected capture method: PYGAME")
        return CaptureMethod.PYGAME
    
    def _get_effective_method(self, screen: pygame.Surface) -> CaptureMethod:
        """
        Get the effective capture method to use
        
        Args:
            screen: Pygame surface
            
        Returns:
            The capture method to actually use
        """
        if self.capture_method == CaptureMethod.AUTO:
            return self._detect_capture_method(screen)
        return self.capture_method
    
    def capture_to_memory(self, screen: pygame.Surface) -> pygame.Surface:
        """
        Capture screenshot to memory without saving to disk
        
        Args:
            screen: Pygame surface to capture
            
        Returns:
            Copy of the screen surface with content
        """
        method = self._get_effective_method(screen)
        
        if method == CaptureMethod.OPENGL:
            screenshot = self._capture_opengl(screen)
        else:
            screenshot = self._capture_pygame(screen)
        
        self.last_screenshot = screenshot
        logger.debug("Screenshot captured to memory using %s method", method.value)
        return screenshot
    
    def _capture_opengl(self, screen: pygame.Surface) -> pygame.Surface:
        """
        Capture screenshot from OpenGL framebuffer
        
        Args:
            screen: Pygame surface (used for size info)
            
        Returns:
            Screenshot surface with OpenGL content
        """
        if self.ctx is None:
            logger.warning("OpenGL capture requested but no context available, falling back to pygame")
            return self._capture_pygame(screen)
        
        try:
            # Read from OpenGL framebuffer
            width, height = screen.get_size()
            
            # Read RGBA data from OpenGL framebuffer
            buffer = self.ctx.screen.read(components=4)
            
            # Convert to numpy array and flip vertically (OpenGL origin is bottom-left)
            pixels = np.frombuffer(buffer, dtype='u1').reshape((height, width, 4))
            pixels = np.flipud(pixels)  # Flip vertically
            
            # Create pygame surface from the flipped data
            screenshot = pygame.image.frombuffer(pixels.tobytes(), (width, height), 'RGBA')
            screenshot = screenshot.convert_alpha()
            return screenshot
        except Exception as e:
            logger.error("OpenGL capture failed: %s, falling back to pygame", e)
            return self._capture_pygame(screen)
    
    def _capture_pygame(self, screen: pygame.Surface) -> pygame.Surface:
        """
        Capture screenshot from pygame surface
        
        Args:
            screen: Pygame surface to capture
            
        Returns:
            Copy of the pygame surface
        """
        return screen.copy()
    
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
