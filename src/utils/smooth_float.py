"""
SmoothFloat — framerate-independent exponential approach to a target value.

Unlike Tween, SmoothFloat has no fixed duration: it asymptotically chases
a target that can be changed at any time. Use it for camera follow, cursor
tracking, smooth numeric displays, or any "stick to" behaviour.

The `speed` parameter controls how quickly the gap closes. It is measured
in half-lives per second (base-2 exponential decay):
    speed=1  → ~50 % of the gap closes per second  (very slow)
    speed=5  → ~97 % of the gap closes per second  (moderate)
    speed=10 → gap is essentially closed in ~0.1 s  (fast)
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SmoothFloat:
    """
    A float value that smoothly follows a target using exponential decay.

    Example:
        sf = SmoothFloat(value=0.0, speed=8.0)
        sf.target = 100.0

        # each frame:
        sf.update(dt)
        current = sf.value
    """
    value: float
    speed: float
    _target: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.speed <= 0.0:
            raise ValueError("SmoothFloat speed must be greater than zero.")
        self._target = self.value

    # ------------------------------------------------------------------
    # Target property — the live destination
    # ------------------------------------------------------------------

    @property
    def target(self) -> float:
        return self._target

    @target.setter
    def target(self, value: float) -> None:
        self._target = value

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def snap_to_target(self) -> None:
        """Immediately set value to target with no smoothing."""
        self.value = self._target

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """Advance the smooth follow by dt seconds."""
        if dt <= 0.0:
            return
        blend = 1.0 - pow(2.0, -self.speed * dt)
        self.value += (self._target - self.value) * blend
