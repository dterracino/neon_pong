"""
Tween — interpolates a single value over time using an easing function.
"""
from enum import Enum
from typing import Callable, Optional

from src.utils.easings import EaseType, get_easing_function


class TweenStatus(Enum):
    """Lifecycle states for a Tween"""
    PENDING   = "pending"    # waiting in delay period, not yet interpolating
    RUNNING   = "running"    # actively interpolating
    PAUSED    = "paused"     # manually halted
    COMPLETE  = "complete"   # finished naturally
    CANCELLED = "cancelled"  # stopped early


class Tween:
    """
    Interpolates a value from start to end over a given duration.

    Example:
        tween = Tween(0, 100, 2.0, EaseType.QUAD_IN_OUT)

        tween.update(dt)
        current_value = tween.value

    Planned additions:
        loop (bool): When True, the tween repeats after completing. Controlled by repeat_count.
        ping_pong (bool): Modifier for loop=True — instead of restarting from start, the tween
            reverses direction on each repetition (start→end, end→start, start→end, ...).
        repeat_count (int): How many times to repeat when loop=True. -1 means infinite.
            Ignored when loop=False.
        on_repeat (Callable): Fired at the end of each repetition, before the next one begins.
            Fires for both loop and ping_pong modes. on_complete only fires when all repetitions
            are exhausted (or the tween is cancelled).
    """

    def __init__(self, start: float, end: float, duration: float,
                 ease_type: EaseType = EaseType.LINEAR,
                 on_complete: Optional[Callable[[], None]] = None,
                 on_update: Optional[Callable[[float], None]] = None,
                 on_start: Optional[Callable[[], None]] = None,
                 delay: float = 0.0,
                 tag: str = ""):
        """
        Initialize a tween.

        Args:
            start: Starting value
            end: Ending value
            duration: Duration in seconds
            ease_type: Type of easing to use
            on_complete: Optional callback when tween completes
            on_update: Optional callback called each frame with the current value
            on_start: Optional callback fired once when interpolation begins (after delay)
            delay: Seconds to wait before the tween starts moving
            tag: Optional label for grouping tweens (used by TweenManager)
        """
        self.start = start
        self.end = end
        self.duration = duration
        self.ease_type = ease_type
        self.on_complete = on_complete
        self.on_update = on_update
        self.on_start = on_start
        self.delay = delay
        self.tag = tag

        self.elapsed = 0.0
        self.status = TweenStatus.PENDING
        self.easing_func = get_easing_function(ease_type)

    # ------------------------------------------------------------------
    # Convenience properties (backward-compatible)
    # ------------------------------------------------------------------

    @property
    def is_complete(self) -> bool:
        """True if the tween has finished or been cancelled"""
        return self.status in (TweenStatus.COMPLETE, TweenStatus.CANCELLED)

    @property
    def is_paused(self) -> bool:
        """True if the tween is currently paused"""
        return self.status == TweenStatus.PAUSED

    # ------------------------------------------------------------------
    # Control methods
    # ------------------------------------------------------------------

    def pause(self) -> None:
        """Pause the tween. Has no effect if already complete or cancelled."""
        if self.status in (TweenStatus.PENDING, TweenStatus.RUNNING):
            self.status = TweenStatus.PAUSED

    def resume(self) -> None:
        """Resume a paused tween."""
        if self.status == TweenStatus.PAUSED:
            self.status = (
                TweenStatus.PENDING if self.elapsed <= self.delay
                else TweenStatus.RUNNING
            )

    def cancel(self) -> None:
        """Stop the tween immediately without firing on_complete."""
        if self.status not in (TweenStatus.COMPLETE, TweenStatus.CANCELLED):
            self.status = TweenStatus.CANCELLED

    def reset(self) -> None:
        """Reset the tween to the beginning."""
        self.elapsed = 0.0
        self.status = TweenStatus.PENDING

    # ------------------------------------------------------------------
    # Update / value
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """Update the tween by the given delta time"""
        if self.status in (TweenStatus.COMPLETE, TweenStatus.CANCELLED, TweenStatus.PAUSED):
            return

        self.elapsed += dt

        # Still in the delay period
        if self.elapsed <= self.delay:
            self.status = TweenStatus.PENDING
            return

        # Transition PENDING → RUNNING: fire on_start once
        was_pending = self.status == TweenStatus.PENDING
        self.status = TweenStatus.RUNNING
        if was_pending and self.on_start:
            self.on_start()

        active_elapsed = self.elapsed - self.delay

        if active_elapsed >= self.duration:
            self.status = TweenStatus.COMPLETE
            if self.on_update:
                self.on_update(self.end)
            if self.on_complete:
                self.on_complete()
        else:
            if self.on_update:
                self.on_update(self.value)

    @property
    def value(self) -> float:
        """Get the current interpolated value"""
        if self.status == TweenStatus.COMPLETE:
            return self.end
        if self.status == TweenStatus.CANCELLED:
            return self.start + (self.end - self.start) * self.progress

        active_elapsed = max(self.elapsed - self.delay, 0.0)

        if self.duration == 0:
            return self.end

        t = min(active_elapsed / self.duration, 1.0)
        eased_t = self.easing_func(t)
        return self.start + (self.end - self.start) * eased_t

    @property
    def progress(self) -> float:
        """Get the progress as a value from 0 to 1 (does not include delay)"""
        if self.status == TweenStatus.COMPLETE:
            return 1.0
        if self.duration == 0:
            return 1.0
        active_elapsed = max(self.elapsed - self.delay, 0.0)
        return min(active_elapsed / self.duration, 1.0)
