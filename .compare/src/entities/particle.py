"""
Particle system for visual effects
"""
import random
import math
from typing import List


class Particle:
    """Single particle"""
    
    def __init__(self, x: float, y: float, color: tuple, lifetime: float):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.uniform(3, 6)
    
    def update(self, dt: float) -> bool:
        """Update particle, return False if dead"""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        
        # Slow down
        self.velocity_x *= 0.98
        self.velocity_y *= 0.98
        
        return self.lifetime > 0
    
    def get_alpha(self) -> float:
        """Get alpha based on remaining lifetime"""
        return self.lifetime / self.max_lifetime


class ParticleSystem:
    """Manages multiple particles"""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def emit(self, x: float, y: float, color: tuple, count: int, lifetime: float):
        """Emit particles at position"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color, lifetime))
    
    def update(self, dt: float):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()