"""
Scene transition effects system
"""
import logging
from typing import Optional, Callable
from src.utils.tweening import ease_cubic_in_out
from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT

logger = logging.getLogger(__name__)


class Transition:
    """Base class for scene transitions"""
    
    def __init__(self, duration: float = 0.5):
        """
        Initialize transition.
        
        Args:
            duration: Total duration of transition in seconds
        """
        self.duration = duration
        self.elapsed = 0.0
        self.is_complete = False
        self.phase = "out"  # "out" or "in"
        self.on_mid_transition: Optional[Callable] = None  # Called when switching scenes
    
    def update(self, dt: float) -> bool:
        """
        Update transition state.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            True if transition is complete
        """
        self.elapsed += dt
        
        if self.elapsed >= self.duration:
            self.is_complete = True
            return True
        
        return False
    
    def get_progress(self) -> float:
        """Get transition progress (0.0 to 1.0)"""
        return min(1.0, self.elapsed / self.duration)
    
    def render_overlay(self, renderer):
        """
        Render transition overlay effect.
        
        Args:
            renderer: Renderer instance
        """
        pass
    
    def should_switch_scene(self) -> bool:
        """
        Check if it's time to switch scenes (for two-phase transitions).
        
        Returns:
            True if scene should be switched now
        """
        return False


class FadeToBlackTransition(Transition):
    """Two-phase fade: fade to black, switch scene, fade from black"""
    
    def __init__(self, fade_out_duration: float = 0.5, fade_in_duration: float = 0.5):
        """
        Initialize fade to black transition.
        
        Args:
            fade_out_duration: Duration of fade to black (seconds)
            fade_in_duration: Duration of fade from black (seconds)
        """
        super().__init__(fade_out_duration + fade_in_duration)
        self.fade_out_duration = fade_out_duration
        self.fade_in_duration = fade_in_duration
        self.scene_switched = False
    
    def update(self, dt: float) -> bool:
        """Update transition and check for scene switch"""
        self.elapsed += dt
        
        # Check if we should switch scenes (at end of fade-out)
        if not self.scene_switched and self.elapsed >= self.fade_out_duration:
            logger.debug("Fade-out complete (%.3fs), invoking mid-transition callback", self.elapsed)
            self.scene_switched = True
            self.phase = "in"
            if self.on_mid_transition:
                self.on_mid_transition()
        
        if self.elapsed >= self.duration:
            self.is_complete = True
            return True
        
        return False
    
    def get_alpha(self) -> float:
        """Get current overlay alpha (0.0 = transparent, 1.0 = opaque)"""
        if self.phase == "out":
            # Fade to black: 0.0 -> 1.0
            progress = self.elapsed / self.fade_out_duration
            eased = ease_cubic_in_out(min(1.0, progress))
            return eased
        else:
            # Fade from black: 1.0 -> 0.0
            progress = (self.elapsed - self.fade_out_duration) / self.fade_in_duration
            eased = ease_cubic_in_out(min(1.0, progress))
            return 1.0 - eased
    
    def render_overlay(self, renderer):
        """Render black overlay with current alpha"""
        alpha = self.get_alpha()
        if alpha > 0.0:
            # Draw full-screen black overlay
            renderer.draw_fullscreen_overlay((0.0, 0.0, 0.0, alpha))


class CrossfadeTransition(Transition):
    """Single-phase crossfade: blend old scene into new scene"""
    
    def __init__(self, duration: float = 0.5):
        """
        Initialize crossfade transition.
        
        Args:
            duration: Duration of crossfade (seconds)
        """
        super().__init__(duration)
        self.old_scene_alpha = 1.0
        self.new_scene_alpha = 0.0
        self.scene_switched = False
    
    def update(self, dt: float) -> bool:
        """Update crossfade progress"""
        # Switch scene immediately at start
        if not self.scene_switched:
            self.scene_switched = True
            if self.on_mid_transition:
                self.on_mid_transition()
        
        self.elapsed += dt
        progress = self.get_progress()
        
        # Ease the alpha transition
        eased = ease_cubic_in_out(progress)
        self.old_scene_alpha = 1.0 - eased
        self.new_scene_alpha = eased
        
        if self.elapsed >= self.duration:
            self.is_complete = True
            return True
        
        return False
    
    def get_old_scene_alpha(self) -> float:
        """Get alpha for old scene"""
        return self.old_scene_alpha
    
    def get_new_scene_alpha(self) -> float:
        """Get alpha for new scene"""
        return self.new_scene_alpha


class ImmediateTransition(Transition):
    """Instant transition with no animation"""
    
    def __init__(self):
        """Initialize immediate transition"""
        super().__init__(0.0)
        self.is_complete = True
    
    def update(self, dt: float) -> bool:
        """Immediate transition is always complete"""
        if not self.is_complete:
            if self.on_mid_transition:
                self.on_mid_transition()
            self.is_complete = True
        return True


# Transition registry
TRANSITIONS = {
    "fade_to_black": FadeToBlackTransition,
    "crossfade": CrossfadeTransition,
    "immediate": ImmediateTransition,
    None: ImmediateTransition,  # Default: no transition
}


def create_transition(transition_type: Optional[str] = None, **kwargs) -> Transition:
    """
    Create a transition instance.
    
    Args:
        transition_type: Type of transition ("fade_to_black", "crossfade", etc.)
        **kwargs: Additional arguments for transition constructor
        
    Returns:
        Transition instance
    """
    transition_class = TRANSITIONS.get(transition_type, ImmediateTransition)
    return transition_class(**kwargs)
