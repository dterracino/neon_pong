"""
AI thinking indicator visual effects
"""
import math
import random
from typing import Tuple


class AIThinkingIndicator:
    """Visual indicator for AI processing/thinking state"""
    
    def __init__(self, style: str = "spinner", min_display_time: float = 0.25, persistent: bool = False):
        """
        Initialize AI thinking indicator.
        
        Args:
            style: Visual style - "spinner", "brainwave", or "pulse_ring"
            min_display_time: Minimum time to show animation (seconds)
            persistent: If True, always show (for adaptive AI), with variable intensity
        """
        self.style = style
        self.timer = 0.0
        
        # Visibility control
        self.is_active = False
        self.active_duration = 0.0
        self.min_display_time = min_display_time
        self.pending_deactivation = False
        
        # Persistent mode for adaptive AI (always analyzing)
        self.persistent = persistent
        self.intensity = 0.3 if persistent else 1.0  # Base intensity when persistent
        
        # Spinner style settings
        self.spinner_particle_count = 6
        self.spinner_radius = 12.0
        self.spinner_speed = 8.0  # Radians per second
        
        # Brainwave style settings
        self.brainwave_points = 20
        self.brainwave_width = 30.0
        self.brainwave_height = 8.0
        self.brainwave_frequency = 5.0
        self.brainwave_values = [random.uniform(-1, 1) for _ in range(self.brainwave_points)]
        self.brainwave_update_timer = 0.0
        self.brainwave_update_rate = 0.05  # Update every 50ms for smooth animation
        
        # Pulse ring style settings
        self.pulse_ring_count = 3
        self.pulse_ring_max_radius = 15.0
        self.pulse_ring_speed = 2.0
    
    def set_active(self, active: bool):
        """
        Set indicator active state.
        
        For persistent mode: Changes intensity instead of visibility
        For normal mode: Shows/hides the indicator
        
        Args:
            active: True to activate/increase intensity, False to deactivate/decrease intensity
        """
        if self.persistent:
            # Persistent mode: Adjust intensity instead of visibility
            self.intensity = 1.0 if active else 0.3  # High when thinking, low when idle
            if not self.is_active:
                self.is_active = True  # Always active in persistent mode
        else:
            # Normal mode: Show/hide based on active state
            if active:
                if not self.is_active:
                    # Activating - reset timers
                    self.is_active = True
                    self.active_duration = 0.0
                    self.pending_deactivation = False
                    self.intensity = 1.0
            else:
                # Request deactivation - will deactivate after min_display_time
                if self.is_active:
                    self.pending_deactivation = True
    
    def update(self, dt: float):
        """Update animation timers and manage visibility"""
        self.timer += dt
        
        # Track how long we've been active
        if self.is_active:
            self.active_duration += dt
            
            # Check if we should deactivate (only for non-persistent mode)
            if not self.persistent and self.pending_deactivation and self.active_duration >= self.min_display_time:
                self.is_active = False
                self.pending_deactivation = False
                self.active_duration = 0.0
        
        # Update brainwave values for smooth random walk
        if self.style == "brainwave":
            self.brainwave_update_timer += dt
            if self.brainwave_update_timer >= self.brainwave_update_rate:
                self.brainwave_update_timer = 0.0
                # Shift values left and add new random value
                self.brainwave_values.pop(0)
                # Smooth random walk - new value influenced by previous value
                last_value = self.brainwave_values[-1]
                new_value = last_value + random.uniform(-0.3, 0.3)
                new_value = max(-1.0, min(1.0, new_value))  # Clamp to [-1, 1]
                self.brainwave_values.append(new_value)
    
    def get_spinner_particles(self, center_x: float, center_y: float, 
                            color: Tuple[float, float, float, float]) -> list:
        """
        Get particle positions for spinner animation.
        
        Returns:
            List of (x, y, size, color) tuples for each particle
        """
        particles = []
        
        for i in range(self.spinner_particle_count):
            # Each particle offset by equal angles
            base_angle = (i / self.spinner_particle_count) * math.pi * 2
            angle = base_angle + self.timer * self.spinner_speed
            
            # Position on circle
            x = center_x + math.cos(angle) * self.spinner_radius
            y = center_y + math.sin(angle) * self.spinner_radius
            
            # Size varies to create trailing effect
            progress = (i / self.spinner_particle_count)
            size = 2.0 + progress * 3.0
            
            # Alpha fades for trailing particles
            alpha = 0.3 + progress * 0.7
            particle_color = (*color[:3], alpha)
            
            particles.append((x, y, size, particle_color))
        
        return particles
    
    def get_brainwave_points(self, center_x: float, center_y: float,
                           color: Tuple[float, float, float, float]) -> list:
        """
        Get points for brainwave/EEG style line.
        
        Returns:
            List of (x, y) tuples for line segments
        """
        points = []
        
        for i, value in enumerate(self.brainwave_values):
            # X position spreads across width
            x = center_x - self.brainwave_width / 2 + (i / (self.brainwave_points - 1)) * self.brainwave_width
            # Y position based on value
            y = center_y + value * self.brainwave_height
            points.append((x, y))
        
        return points
    
    def get_pulse_rings(self, center_x: float, center_y: float,
                       color: Tuple[float, float, float, float]) -> list:
        """
        Get ring data for pulsing concentric rings.
        
        Returns:
            List of (x, y, radius, alpha) tuples for each ring
        """
        rings = []
        
        for i in range(self.pulse_ring_count):
            # Each ring offset in time
            phase = (i / self.pulse_ring_count) * math.pi * 2
            progress = (math.sin(self.timer * self.pulse_ring_speed + phase) + 1.0) / 2.0
            
            radius = 5.0 + progress * self.pulse_ring_max_radius
            alpha = 0.8 * (1.0 - progress)  # Fade out as it expands
            
            rings.append((center_x, center_y, radius, alpha))
        
        return rings
