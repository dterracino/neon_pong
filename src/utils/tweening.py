"""
Tweening library for smooth animations and transitions.

Provides various easing functions for interpolation between values.
Supports linear, quadratic, cubic, quartic, quintic, sine, exponential,
circular, elastic, back, and bounce easing types, each with in, out, and in-out variations.
"""
import math
from typing import Callable, Any, Optional
from enum import Enum


class EaseType(Enum):
    """Enumeration of available easing types"""
    # Linear
    LINEAR = "linear"
    
    # Quadratic
    QUAD_IN = "quad_in"
    QUAD_OUT = "quad_out"
    QUAD_IN_OUT = "quad_in_out"
    
    # Cubic
    CUBIC_IN = "cubic_in"
    CUBIC_OUT = "cubic_out"
    CUBIC_IN_OUT = "cubic_in_out"
    
    # Quartic
    QUART_IN = "quart_in"
    QUART_OUT = "quart_out"
    QUART_IN_OUT = "quart_in_out"
    
    # Quintic
    QUINT_IN = "quint_in"
    QUINT_OUT = "quint_out"
    QUINT_IN_OUT = "quint_in_out"
    
    # Sine
    SINE_IN = "sine_in"
    SINE_OUT = "sine_out"
    SINE_IN_OUT = "sine_in_out"
    
    # Exponential
    EXPO_IN = "expo_in"
    EXPO_OUT = "expo_out"
    EXPO_IN_OUT = "expo_in_out"
    
    # Circular
    CIRC_IN = "circ_in"
    CIRC_OUT = "circ_out"
    CIRC_IN_OUT = "circ_in_out"
    
    # Elastic
    ELASTIC_IN = "elastic_in"
    ELASTIC_OUT = "elastic_out"
    ELASTIC_IN_OUT = "elastic_in_out"
    
    # Back
    BACK_IN = "back_in"
    BACK_OUT = "back_out"
    BACK_IN_OUT = "back_in_out"
    
    # Bounce
    BOUNCE_IN = "bounce_in"
    BOUNCE_OUT = "bounce_out"
    BOUNCE_IN_OUT = "bounce_in_out"


# ==================== LINEAR ====================
def ease_linear(t: float) -> float:
    """Linear easing (no acceleration)"""
    return t


# ==================== QUADRATIC ====================
def ease_quad_in(t: float) -> float:
    """Quadratic easing in - accelerating from zero velocity"""
    return t * t


def ease_quad_out(t: float) -> float:
    """Quadratic easing out - decelerating to zero velocity"""
    return t * (2 - t)


def ease_quad_in_out(t: float) -> float:
    """Quadratic easing in/out - acceleration until halfway, then deceleration"""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t


# ==================== CUBIC ====================
def ease_cubic_in(t: float) -> float:
    """Cubic easing in - accelerating from zero velocity"""
    return t * t * t


def ease_cubic_out(t: float) -> float:
    """Cubic easing out - decelerating to zero velocity"""
    t -= 1
    return t * t * t + 1


def ease_cubic_in_out(t: float) -> float:
    """Cubic easing in/out - acceleration until halfway, then deceleration"""
    if t < 0.5:
        return 4 * t * t * t
    t = 2 * t - 2
    return 0.5 * t * t * t + 1


# ==================== QUARTIC ====================
def ease_quart_in(t: float) -> float:
    """Quartic easing in - accelerating from zero velocity"""
    return t * t * t * t


def ease_quart_out(t: float) -> float:
    """Quartic easing out - decelerating to zero velocity"""
    t -= 1
    return 1 - t * t * t * t


def ease_quart_in_out(t: float) -> float:
    """Quartic easing in/out - acceleration until halfway, then deceleration"""
    if t < 0.5:
        return 8 * t * t * t * t
    t -= 1
    return 1 - 8 * t * t * t * t


# ==================== QUINTIC ====================
def ease_quint_in(t: float) -> float:
    """Quintic easing in - accelerating from zero velocity"""
    return t * t * t * t * t


def ease_quint_out(t: float) -> float:
    """Quintic easing out - decelerating to zero velocity"""
    t -= 1
    return t * t * t * t * t + 1


def ease_quint_in_out(t: float) -> float:
    """Quintic easing in/out - acceleration until halfway, then deceleration"""
    if t < 0.5:
        return 16 * t * t * t * t * t
    t = 2 * t - 2
    return 0.5 * t * t * t * t * t + 1


# ==================== SINE ====================
def ease_sine_in(t: float) -> float:
    """Sinusoidal easing in - accelerating from zero velocity"""
    return 1 - math.cos(t * math.pi / 2)


def ease_sine_out(t: float) -> float:
    """Sinusoidal easing out - decelerating to zero velocity"""
    return math.sin(t * math.pi / 2)


def ease_sine_in_out(t: float) -> float:
    """Sinusoidal easing in/out - acceleration until halfway, then deceleration"""
    return 0.5 * (1 - math.cos(math.pi * t))


# ==================== EXPONENTIAL ====================
def ease_expo_in(t: float) -> float:
    """Exponential easing in - accelerating from zero velocity"""
    return 0 if t == 0 else math.pow(2, 10 * (t - 1))


def ease_expo_out(t: float) -> float:
    """Exponential easing out - decelerating to zero velocity"""
    return 1 if t == 1 else 1 - math.pow(2, -10 * t)


def ease_expo_in_out(t: float) -> float:
    """Exponential easing in/out - acceleration until halfway, then deceleration"""
    if t == 0 or t == 1:
        return t
    if t < 0.5:
        return 0.5 * math.pow(2, 20 * t - 10)
    return 1 - 0.5 * math.pow(2, -20 * t + 10)


# ==================== CIRCULAR ====================
def ease_circ_in(t: float) -> float:
    """Circular easing in - accelerating from zero velocity"""
    return 1 - math.sqrt(1 - t * t)


def ease_circ_out(t: float) -> float:
    """Circular easing out - decelerating to zero velocity"""
    t -= 1
    return math.sqrt(1 - t * t)


def ease_circ_in_out(t: float) -> float:
    """Circular easing in/out - acceleration until halfway, then deceleration"""
    t *= 2
    if t < 1:
        return -0.5 * (math.sqrt(1 - t * t) - 1)
    t -= 2
    return 0.5 * (math.sqrt(1 - t * t) + 1)


# ==================== ELASTIC ====================
def ease_elastic_in(t: float) -> float:
    """Elastic easing in - exponentially decaying sine wave"""
    if t == 0 or t == 1:
        return t
    return -math.pow(2, 10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi)


def ease_elastic_out(t: float) -> float:
    """Elastic easing out - exponentially decaying sine wave"""
    if t == 0 or t == 1:
        return t
    return math.pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1


def ease_elastic_in_out(t: float) -> float:
    """Elastic easing in/out - exponentially decaying sine wave"""
    if t == 0 or t == 1:
        return t
    t *= 2
    if t < 1:
        return -0.5 * math.pow(2, 10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi)
    return 0.5 * math.pow(2, -10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi) + 1


# ==================== BACK ====================
def ease_back_in(t: float) -> float:
    """Back easing in - backing up before going forward"""
    s = 1.70158
    return t * t * ((s + 1) * t - s)


def ease_back_out(t: float) -> float:
    """Back easing out - overshooting then coming back"""
    s = 1.70158
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def ease_back_in_out(t: float) -> float:
    """Back easing in/out - backing up before going forward, then overshooting"""
    s = 1.70158 * 1.525
    t *= 2
    if t < 1:
        return 0.5 * (t * t * ((s + 1) * t - s))
    t -= 2
    return 0.5 * (t * t * ((s + 1) * t + s) + 2)


# ==================== BOUNCE ====================
def ease_bounce_out(t: float) -> float:
    """Bounce easing out - bouncing to rest"""
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def ease_bounce_in(t: float) -> float:
    """Bounce easing in - bouncing from zero"""
    return 1 - ease_bounce_out(1 - t)


def ease_bounce_in_out(t: float) -> float:
    """Bounce easing in/out - bouncing in then bouncing out"""
    if t < 0.5:
        return ease_bounce_in(t * 2) * 0.5
    return ease_bounce_out(t * 2 - 1) * 0.5 + 0.5


# Map easing types to functions
EASING_FUNCTIONS: dict[EaseType, Callable[[float], float]] = {
    EaseType.LINEAR: ease_linear,
    
    EaseType.QUAD_IN: ease_quad_in,
    EaseType.QUAD_OUT: ease_quad_out,
    EaseType.QUAD_IN_OUT: ease_quad_in_out,
    
    EaseType.CUBIC_IN: ease_cubic_in,
    EaseType.CUBIC_OUT: ease_cubic_out,
    EaseType.CUBIC_IN_OUT: ease_cubic_in_out,
    
    EaseType.QUART_IN: ease_quart_in,
    EaseType.QUART_OUT: ease_quart_out,
    EaseType.QUART_IN_OUT: ease_quart_in_out,
    
    EaseType.QUINT_IN: ease_quint_in,
    EaseType.QUINT_OUT: ease_quint_out,
    EaseType.QUINT_IN_OUT: ease_quint_in_out,
    
    EaseType.SINE_IN: ease_sine_in,
    EaseType.SINE_OUT: ease_sine_out,
    EaseType.SINE_IN_OUT: ease_sine_in_out,
    
    EaseType.EXPO_IN: ease_expo_in,
    EaseType.EXPO_OUT: ease_expo_out,
    EaseType.EXPO_IN_OUT: ease_expo_in_out,
    
    EaseType.CIRC_IN: ease_circ_in,
    EaseType.CIRC_OUT: ease_circ_out,
    EaseType.CIRC_IN_OUT: ease_circ_in_out,
    
    EaseType.ELASTIC_IN: ease_elastic_in,
    EaseType.ELASTIC_OUT: ease_elastic_out,
    EaseType.ELASTIC_IN_OUT: ease_elastic_in_out,
    
    EaseType.BACK_IN: ease_back_in,
    EaseType.BACK_OUT: ease_back_out,
    EaseType.BACK_IN_OUT: ease_back_in_out,
    
    EaseType.BOUNCE_IN: ease_bounce_in,
    EaseType.BOUNCE_OUT: ease_bounce_out,
    EaseType.BOUNCE_IN_OUT: ease_bounce_in_out,
}


def get_easing_function(ease_type: EaseType) -> Callable[[float], float]:
    """Get the easing function for the specified type"""
    return EASING_FUNCTIONS[ease_type]


class Tween:
    """
    A tween that interpolates a value over time using an easing function.
    
    Example:
        # Create a tween that goes from 0 to 100 over 2 seconds with quad easing
        tween = Tween(0, 100, 2.0, EaseType.QUAD_IN_OUT)
        
        # Update and get current value
        tween.update(dt)
        current_value = tween.value
    """
    
    def __init__(self, start: float, end: float, duration: float, 
                 ease_type: EaseType = EaseType.LINEAR,
                 on_complete: Optional[Callable[[], None]] = None):
        """
        Initialize a tween.
        
        Args:
            start: Starting value
            end: Ending value
            duration: Duration in seconds
            ease_type: Type of easing to use
            on_complete: Optional callback when tween completes
        """
        self.start = start
        self.end = end
        self.duration = duration
        self.ease_type = ease_type
        self.on_complete = on_complete
        
        self.elapsed = 0.0
        self.is_complete = False
        self.easing_func = get_easing_function(ease_type)
    
    def update(self, dt: float) -> None:
        """Update the tween by the given delta time"""
        if self.is_complete:
            return
        
        self.elapsed += dt
        
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.is_complete = True
            if self.on_complete:
                self.on_complete()
    
    @property
    def value(self) -> float:
        """Get the current interpolated value"""
        if self.duration == 0:
            return self.end
        
        # Calculate normalized time (0 to 1)
        t = min(self.elapsed / self.duration, 1.0)
        
        # Apply easing function
        eased_t = self.easing_func(t)
        
        # Interpolate between start and end
        return self.start + (self.end - self.start) * eased_t
    
    @property
    def progress(self) -> float:
        """Get the progress as a value from 0 to 1"""
        if self.duration == 0:
            return 1.0
        return min(self.elapsed / self.duration, 1.0)
    
    def reset(self) -> None:
        """Reset the tween to the beginning"""
        self.elapsed = 0.0
        self.is_complete = False


class TweenManager:
    """
    Manages multiple tweens, allowing you to run many animations simultaneously.
    
    Example:
        manager = TweenManager()
        
        # Add tweens
        tween1 = manager.add_tween(0, 100, 1.0, EaseType.QUAD_OUT)
        tween2 = manager.add_tween(50, 200, 2.0, EaseType.ELASTIC_OUT)
        
        # Update all tweens
        manager.update(dt)
        
        # Get values
        value1 = tween1.value
        value2 = tween2.value
    """
    
    def __init__(self):
        """Initialize the tween manager"""
        self.tweens: list[Tween] = []
    
    def add_tween(self, start: float, end: float, duration: float,
                  ease_type: EaseType = EaseType.LINEAR,
                  on_complete: Optional[Callable[[], None]] = None) -> Tween:
        """
        Create and add a tween to the manager.
        
        Args:
            start: Starting value
            end: Ending value
            duration: Duration in seconds
            ease_type: Type of easing to use
            on_complete: Optional callback when tween completes
            
        Returns:
            The created tween
        """
        tween = Tween(start, end, duration, ease_type, on_complete)
        self.tweens.append(tween)
        return tween
    
    def update(self, dt: float) -> None:
        """Update all tweens"""
        for tween in self.tweens:
            tween.update(dt)
        
        # Remove completed tweens
        self.tweens = [t for t in self.tweens if not t.is_complete]
    
    def clear(self) -> None:
        """Remove all tweens"""
        self.tweens.clear()
    
    @property
    def active_count(self) -> int:
        """Get the number of active tweens"""
        return len(self.tweens)
