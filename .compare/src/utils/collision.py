"""
Collision detection utilities
"""
from typing import Tuple


class AABB:
    """Axis-Aligned Bounding Box for collision detection"""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    @property
    def left(self) -> float:
        return self.x
    
    @property
    def right(self) -> float:
        return self.x + self.width
    
    @property
    def top(self) -> float:
        return self.y
    
    @property
    def bottom(self) -> float:
        return self.y + self.height
    
    @property
    def center_x(self) -> float:
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        return self.y + self.height / 2
    
    def intersects(self, other: 'AABB') -> bool:
        """Check if this AABB intersects with another"""
        return (
            self.left < other.right and
            self.right > other.left and
            self.top < other.bottom and
            self.bottom > other.top
        )
    
    def get_overlap(self, other: 'AABB') -> Tuple[float, float]:
        """Get the overlap amount on each axis"""
        overlap_x = min(self.right, other.right) - max(self.left, other.left)
        overlap_y = min(self.bottom, other.bottom) - max(self.top, other.top)
        return overlap_x, overlap_y