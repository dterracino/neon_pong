"""
Simple game time tracking utility
"""
import logging

logger = logging.getLogger(__name__)


class GameTime:
    """Tracks elapsed time for a scene or game session"""
    
    def __init__(self):
        """Initialize game time at zero"""
        self.elapsed = 0.0
        logger.debug("GameTime initialized")
    
    def update(self, dt: float):
        """Update elapsed time
        
        Args:
            dt: Delta time in seconds since last frame
        """
        self.elapsed += dt
    
    def reset(self):
        """Reset time back to zero"""
        self.elapsed = 0.0
        logger.debug("GameTime reset")
    
    def get_elapsed(self) -> float:
        """Get elapsed time in seconds
        
        Returns:
            Elapsed time in seconds
        """
        return self.elapsed
    
    def __float__(self):
        """Allow using GameTime directly as a float"""
        return self.elapsed
