"""
Screen shake effect system
Provides camera shake on impacts for game juice
"""
import random
import math
from typing import Tuple


class ScreenShake:
    """
    Manages screen shake effects with intensity decay.
    
    Usage:
        shake = ScreenShake()
        shake.add_shake(10.0, 0.3)  # intensity, duration
        shake.update(dt)
        offset_x, offset_y = shake.get_offset()
    """
    
    def __init__(self):
        self.intensity: float = 0.0
        self.duration: float = 0.0
        self.elapsed: float = 0.0
    
    def add_shake(self, intensity: float, duration: float = 0.3):
        """
        Add screen shake effect.
        
        Args:
            intensity: Maximum shake displacement in pixels
            duration: How long the shake lasts in seconds
        """
        # If new shake is stronger, replace current shake
        if intensity > self.intensity:
            self.intensity = intensity
            self.duration = duration
            self.elapsed = 0.0
        # Otherwise, add to existing shake
        else:
            self.intensity = max(self.intensity, intensity)
            self.duration = max(self.duration, duration)
    
    def update(self, dt: float):
        """Update shake decay"""
        if self.duration > 0:
            self.elapsed += dt
            
            # Shake is over
            if self.elapsed >= self.duration:
                self.intensity = 0.0
                self.duration = 0.0
                self.elapsed = 0.0
    
    def get_offset(self) -> Tuple[float, float]:
        """
        Get current shake offset.
        
        Returns:
            (offset_x, offset_y) tuple
        """
        if self.intensity <= 0 or self.duration <= 0:
            return (0.0, 0.0)
        
        # Calculate decay factor (0 to 1, where 1 is start of shake)
        progress = self.elapsed / self.duration
        decay = 1.0 - progress
        
        # Exponential decay for more natural feel
        decay = decay ** 2
        
        # Current shake strength
        current_intensity = self.intensity * decay
        
        # Random offset with current intensity
        angle = random.uniform(0, 2 * math.pi)
        offset_x = math.cos(angle) * current_intensity
        offset_y = math.sin(angle) * current_intensity
        
        return (offset_x, offset_y)
    
    def is_shaking(self) -> bool:
        """Check if currently shaking"""
        return self.intensity > 0 and self.duration > 0
    
    def clear(self):
        """Stop all shaking immediately"""
        self.intensity = 0.0
        self.duration = 0.0
        self.elapsed = 0.0
