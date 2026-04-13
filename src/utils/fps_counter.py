"""
FPS Counter for tracking frame rate metrics
"""
from collections import deque
from typing import Tuple


class FPSCounter:
    """Tracks frame rate metrics including instant, average, and percentile lows"""
    
    def __init__(self, average_window: float = 1.0):
        """
        Initialize FPS counter
        
        Args:
            average_window: Time window in seconds for calculating averages
        """
        self.average_window = average_window
        
        # Frame time tracking
        self.frame_times = deque()  # Store (timestamp, frame_time) tuples
        self.current_time = 0.0
        
        # Cached metrics
        self.instant_fps = 0.0
        self.average_fps = 0.0
        self.one_percent_low = 0.0
        self.point_one_percent_low = 0.0
        
        # Visibility toggle
        self.visible = False
        
        # Current frame time in ms
        self.frame_ms = 0.0
    
    def update(self, dt: float):
        """
        Update FPS metrics with new frame time
        
        Args:
            dt: Delta time for this frame in seconds
        """
        self.current_time += dt
        
        # Store frame time
        if dt > 0:
            self.frame_times.append((self.current_time, dt))
        
        # Remove old frame times outside the window
        cutoff_time = self.current_time - self.average_window
        while self.frame_times and self.frame_times[0][0] < cutoff_time:
            self.frame_times.popleft()
        
        # Calculate instant FPS
        if dt > 0:
            self.instant_fps = 1.0 / dt
            self.frame_ms = dt * 1000.0
        
        # Calculate average FPS
        if len(self.frame_times) > 0:
            total_time = sum(ft[1] for ft in self.frame_times)
            if total_time > 0:
                self.average_fps = len(self.frame_times) / total_time
            else:
                self.average_fps = 0.0
        
        # Calculate percentile lows
        if len(self.frame_times) >= 10:  # Need minimum samples
            sorted_times = sorted([ft[1] for ft in self.frame_times], reverse=True)
            
            # 1% low: Average of worst 1% of frame times (slowest frames)
            one_percent_count = max(1, int(len(sorted_times) * 0.01))
            worst_1_percent = sorted_times[:one_percent_count]
            avg_worst_1_percent = sum(worst_1_percent) / len(worst_1_percent)
            if avg_worst_1_percent > 0:
                self.one_percent_low = 1.0 / avg_worst_1_percent
            
            # 0.1% low: Average of worst 0.1% of frame times
            point_one_percent_count = max(1, int(len(sorted_times) * 0.001))
            worst_0_1_percent = sorted_times[:point_one_percent_count]
            avg_worst_0_1_percent = sum(worst_0_1_percent) / len(worst_0_1_percent)
            if avg_worst_0_1_percent > 0:
                self.point_one_percent_low = 1.0 / avg_worst_0_1_percent
    
    def toggle_visibility(self):
        """Toggle FPS display visibility"""
        self.visible = not self.visible
    
    def get_metrics(self) -> Tuple[float, float, float, float, float]:
        """
        Get current FPS metrics
        
        Returns:
            Tuple of (instant_fps, average_fps, one_percent_low, point_one_percent_low, frame_ms)
        """
        return (
            self.instant_fps,
            self.average_fps,
            self.one_percent_low,
            self.point_one_percent_low,
            self.frame_ms
        )
    
    def is_visible(self) -> bool:
        """Check if FPS display should be shown"""
        return self.visible
