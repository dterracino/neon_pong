"""
Easing functions for smooth animations and transitions.

Provides various easing functions for interpolation between values.
Supports linear, quadratic, cubic, quartic, quintic, sine, exponential,
circular, elastic, back, and bounce easing types, each with in, out, and in-out variations.

The individual easing functions are private (_ease_*). Use EASING_FUNCTIONS or
get_easing_function() to access them by EaseType.
"""
import math
from typing import Callable
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

    # Smooth (perlin-style, no in/out variants — symmetric by nature)
    SMOOTH_STEP   = "smooth_step"    # 3t² - 2t³  — zero velocity at both endpoints
    SMOOTHER_STEP = "smoother_step"  # 6t⁵ - 15t⁴ + 10t³ — zero velocity AND acceleration at both endpoints


# ==================== LINEAR ====================
def _ease_linear(t: float) -> float:
    return t


# ==================== QUADRATIC ====================
def _ease_quad_in(t: float) -> float:
    return t * t


def _ease_quad_out(t: float) -> float:
    return t * (2 - t)


def _ease_quad_in_out(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t


# ==================== CUBIC ====================
def _ease_cubic_in(t: float) -> float:
    return t * t * t


def _ease_cubic_out(t: float) -> float:
    t -= 1
    return t * t * t + 1


def _ease_cubic_in_out(t: float) -> float:
    if t < 0.5:
        return 4 * t * t * t
    t = 2 * t - 2
    return 0.5 * t * t * t + 1


# ==================== QUARTIC ====================
def _ease_quart_in(t: float) -> float:
    return t * t * t * t


def _ease_quart_out(t: float) -> float:
    t -= 1
    return 1 - t * t * t * t


def _ease_quart_in_out(t: float) -> float:
    if t < 0.5:
        return 8 * t * t * t * t
    t -= 1
    return 1 - 8 * t * t * t * t


# ==================== QUINTIC ====================
def _ease_quint_in(t: float) -> float:
    return t * t * t * t * t


def _ease_quint_out(t: float) -> float:
    t -= 1
    return t * t * t * t * t + 1


def _ease_quint_in_out(t: float) -> float:
    if t < 0.5:
        return 16 * t * t * t * t * t
    t = 2 * t - 2
    return 0.5 * t * t * t * t * t + 1


# ==================== SINE ====================
def _ease_sine_in(t: float) -> float:
    return 1 - math.cos(t * math.pi / 2)


def _ease_sine_out(t: float) -> float:
    return math.sin(t * math.pi / 2)


def _ease_sine_in_out(t: float) -> float:
    return 0.5 * (1 - math.cos(math.pi * t))


# ==================== EXPONENTIAL ====================
def _ease_expo_in(t: float) -> float:
    return 0 if t == 0 else math.pow(2, 10 * (t - 1))


def _ease_expo_out(t: float) -> float:
    return 1 if t == 1 else 1 - math.pow(2, -10 * t)


def _ease_expo_in_out(t: float) -> float:
    if t == 0 or t == 1:
        return t
    if t < 0.5:
        return 0.5 * math.pow(2, 20 * t - 10)
    return 1 - 0.5 * math.pow(2, -20 * t + 10)


# ==================== CIRCULAR ====================
def _ease_circ_in(t: float) -> float:
    return 1 - math.sqrt(1 - t * t)


def _ease_circ_out(t: float) -> float:
    t -= 1
    return math.sqrt(1 - t * t)


def _ease_circ_in_out(t: float) -> float:
    t *= 2
    if t < 1:
        return -0.5 * (math.sqrt(1 - t * t) - 1)
    t -= 2
    return 0.5 * (math.sqrt(1 - t * t) + 1)


# ==================== ELASTIC ====================
def _ease_elastic_in(t: float) -> float:
    if t == 0 or t == 1:
        return t
    return -math.pow(2, 10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi)


def _ease_elastic_out(t: float) -> float:
    if t == 0 or t == 1:
        return t
    return math.pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1


def _ease_elastic_in_out(t: float) -> float:
    if t == 0 or t == 1:
        return t
    t *= 2
    if t < 1:
        return -0.5 * math.pow(2, 10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi)
    return 0.5 * math.pow(2, -10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi) + 1


# ==================== BACK ====================
def _ease_back_in(t: float) -> float:
    s = 1.70158
    return t * t * ((s + 1) * t - s)


def _ease_back_out(t: float) -> float:
    s = 1.70158
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def _ease_back_in_out(t: float) -> float:
    s = 1.70158 * 1.525
    t *= 2
    if t < 1:
        return 0.5 * (t * t * ((s + 1) * t - s))
    t -= 2
    return 0.5 * (t * t * ((s + 1) * t + s) + 2)


# ==================== BOUNCE ====================
def _ease_bounce_out(t: float) -> float:
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


def _ease_bounce_in(t: float) -> float:
    return 1 - _ease_bounce_out(1 - t)


def _ease_bounce_in_out(t: float) -> float:
    if t < 0.5:
        return _ease_bounce_in(t * 2) * 0.5
    return _ease_bounce_out(t * 2 - 1) * 0.5 + 0.5


# ==================== SMOOTH ====================
def _ease_smooth_step(t: float) -> float:
    """Ken Perlin's smoothstep: 3t² - 2t³. Zero first derivative at t=0 and t=1."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _ease_smoother_step(t: float) -> float:
    """Ken Perlin's smootherstep: 6t⁵ - 15t⁴ + 10t³. Zero first and second derivative at t=0 and t=1."""
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


# Map easing types to functions — the public interface for accessing easing functions
EASING_FUNCTIONS: dict[EaseType, Callable[[float], float]] = {
    EaseType.LINEAR: _ease_linear,

    EaseType.QUAD_IN: _ease_quad_in,
    EaseType.QUAD_OUT: _ease_quad_out,
    EaseType.QUAD_IN_OUT: _ease_quad_in_out,

    EaseType.CUBIC_IN: _ease_cubic_in,
    EaseType.CUBIC_OUT: _ease_cubic_out,
    EaseType.CUBIC_IN_OUT: _ease_cubic_in_out,

    EaseType.QUART_IN: _ease_quart_in,
    EaseType.QUART_OUT: _ease_quart_out,
    EaseType.QUART_IN_OUT: _ease_quart_in_out,

    EaseType.QUINT_IN: _ease_quint_in,
    EaseType.QUINT_OUT: _ease_quint_out,
    EaseType.QUINT_IN_OUT: _ease_quint_in_out,

    EaseType.SINE_IN: _ease_sine_in,
    EaseType.SINE_OUT: _ease_sine_out,
    EaseType.SINE_IN_OUT: _ease_sine_in_out,

    EaseType.EXPO_IN: _ease_expo_in,
    EaseType.EXPO_OUT: _ease_expo_out,
    EaseType.EXPO_IN_OUT: _ease_expo_in_out,

    EaseType.CIRC_IN: _ease_circ_in,
    EaseType.CIRC_OUT: _ease_circ_out,
    EaseType.CIRC_IN_OUT: _ease_circ_in_out,

    EaseType.ELASTIC_IN: _ease_elastic_in,
    EaseType.ELASTIC_OUT: _ease_elastic_out,
    EaseType.ELASTIC_IN_OUT: _ease_elastic_in_out,

    EaseType.BACK_IN: _ease_back_in,
    EaseType.BACK_OUT: _ease_back_out,
    EaseType.BACK_IN_OUT: _ease_back_in_out,

    EaseType.BOUNCE_IN: _ease_bounce_in,
    EaseType.BOUNCE_OUT: _ease_bounce_out,
    EaseType.BOUNCE_IN_OUT: _ease_bounce_in_out,

    EaseType.SMOOTH_STEP:   _ease_smooth_step,
    EaseType.SMOOTHER_STEP: _ease_smoother_step,
}


def get_easing_function(ease_type: EaseType) -> Callable[[float], float]:
    """Get the easing function for the specified EaseType"""
    return EASING_FUNCTIONS[ease_type]
