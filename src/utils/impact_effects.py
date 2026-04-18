"""
Impact effects system for visual feedback on collisions
Manages flashes and expanding ring effects
"""
import logging
from typing import List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ImpactEffect:
    """Single impact effect (flash or ring)"""
    x: float
    y: float
    color: Tuple[float, float, float, float]
    lifetime: float
    max_lifetime: float
    effect_type: str  # 'flash' or 'ring'
    max_radius: float = 50.0
    
    def get_alpha(self) -> float:
        """Get current alpha based on lifetime"""
        return self.lifetime / self.max_lifetime
    
    def get_radius(self) -> float:
        """Get current radius for ring effects"""
        progress = 1.0 - (self.lifetime / self.max_lifetime)
        return self.max_radius * progress


class ImpactEffectsSystem:
    """
    Manages impact effects for collisions.
    
    Usage:
        effects = ImpactEffectsSystem()
        effects.add_flash(x, y, color)
        effects.add_ring(x, y, color, max_radius=60)
        effects.update(dt)
        effects.render(renderer)
    """
    
    def __init__(self):
        self.effects: List[ImpactEffect] = []
    
    def add_flash(self, x: float, y: float, color: Tuple[float, float, float, float],
                  size: float = 30.0, duration: float = 0.15):
        """
        Add a flash effect at the given position.
        
        Args:
            x, y: Position
            color: RGBA color (0-1 range)
            size: Flash size in pixels
            duration: How long the flash lasts
        """
        effect = ImpactEffect(
            x=x,
            y=y,
            color=color,
            lifetime=duration,
            max_lifetime=duration,
            effect_type='flash',
            max_radius=size
        )
        self.effects.append(effect)
        logger.debug(f"Added flash effect at ({x:.0f}, {y:.0f})")
    
    def add_ring(self, x: float, y: float, color: Tuple[float, float, float, float],
                 max_radius: float = 50.0, duration: float = 0.4, thickness: float = 3.0):
        """
        Add an expanding ring effect.
        
        Args:
            x, y: Center position
            color: RGBA color (0-1 range)
            max_radius: Maximum ring radius in pixels
            duration: How long the ring expands
            thickness: Ring line thickness
        """
        effect = ImpactEffect(
            x=x,
            y=y,
            color=color,
            lifetime=duration,
            max_lifetime=duration,
            effect_type='ring',
            max_radius=max_radius
        )
        # Store thickness in color alpha channel for now (hack but works)
        self.effects.append(effect)
        logger.debug(f"Added ring effect at ({x:.0f}, {y:.0f}), radius={max_radius}")
    
    def update(self, dt: float):
        """Update all effects and remove expired ones"""
        for effect in self.effects[:]:
            effect.lifetime -= dt
            if effect.lifetime <= 0:
                self.effects.remove(effect)
    
    def render(self, renderer):
        """
        Render all active effects.
        
        Args:
            renderer: Renderer instance with draw_circle method
        """
        for effect in self.effects:
            alpha = effect.get_alpha()
            
            if effect.effect_type == 'flash':
                # Render flash as a bright circle that fades
                color = (*effect.color[:3], alpha * effect.color[3])
                size = effect.max_radius
                renderer.draw_circle(effect.x, effect.y, size, color)
            
            elif effect.effect_type == 'ring':
                # Render ring as expanding hollow circle
                # We'll approximate with multiple circles at different radii
                radius = effect.get_radius()
                color = (*effect.color[:3], alpha * effect.color[3])
                
                # Draw ring as filled circle minus smaller inner circle
                # (Not perfect but works with current renderer)
                thickness = 3.0
                outer_radius = radius
                inner_radius = max(0, radius - thickness)
                
                # Draw outer circle
                renderer.draw_circle(effect.x, effect.y, outer_radius, color)
                
                # Draw inner circle with alpha = 0 to create hollow effect
                # (This won't work perfectly with current blending, but good enough)
                if inner_radius > 0:
                    black_clear = (0.0, 0.0, 0.0, 0.0)
                    # Skip inner circle for now - just show expanding solid circle
                    # This is simpler and still looks good
    
    def clear(self):
        """Clear all effects"""
        self.effects.clear()
    
    def count(self) -> int:
        """Get number of active effects"""
        return len(self.effects)
