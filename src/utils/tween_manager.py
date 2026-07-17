"""
TweenManager — runs multiple Tweens simultaneously, handling updates and cleanup.
"""
from typing import Callable, Optional

from src.utils.easings import EaseType
from src.utils.tween import Tween, TweenStatus


class TweenManager:
    """
    Manages multiple tweens running simultaneously.

    Tweens are automatically removed when complete or cancelled. Use on_update
    and on_complete callbacks for fully fire-and-forget usage, or hold the
    returned Tween reference to read .value directly each frame.

    Tags let you pause, resume, or cancel groups of tweens by name.

    Example:
        manager = TweenManager()

        # Fire-and-forget cascade with staggered delay
        for i, row in enumerate(rows):
            manager.add_tween(
                -200, 0, 0.4, EaseType.QUAD_OUT,
                delay=i * 0.06,
                tag="slide_in",
                on_update=lambda v, idx=i: offsets.__setitem__(idx, v)
            )

        # Pause / resume / cancel a group
        manager.pause_tag("slide_in")
        manager.resume_tag("slide_in")
        manager.cancel_tag("slide_in")

        # In update loop:
        manager.update(dt)
    """

    def __init__(self):
        self.tweens: list[Tween] = []

    def add_tween(self, start: float, end: float, duration: float,
                  ease_type: EaseType = EaseType.LINEAR,
                  on_complete: Optional[Callable[[], None]] = None,
                  on_update: Optional[Callable[[float], None]] = None,
                  on_start: Optional[Callable[[], None]] = None,
                  delay: float = 0.0,
                  tag: str = "") -> Tween:
        """
        Create and add a tween to the manager.

        Args:
            start: Starting value
            end: Ending value
            duration: Duration in seconds
            ease_type: Type of easing to use
            on_complete: Optional callback when tween completes
            on_update: Optional callback called each frame with the current value
            on_start: Optional callback fired once when interpolation begins (after delay)
            delay: Seconds to wait before the tween starts moving
            tag: Optional label for grouping (used with pause/resume/cancel_tag)

        Returns:
            The created Tween
        """
        tween = Tween(start, end, duration, ease_type, on_complete, on_update, on_start, delay, tag)
        self.tweens.append(tween)
        return tween

    def update(self, dt: float) -> None:
        """Update all non-paused tweens and call on_update for running ones"""
        for tween in self.tweens:
            tween.update(dt)
            if tween.on_update and tween.status == TweenStatus.RUNNING:
                tween.on_update(tween.value)

        # Remove finished tweens
        self.tweens = [
            t for t in self.tweens
            if t.status not in (TweenStatus.COMPLETE, TweenStatus.CANCELLED)
        ]

    # ------------------------------------------------------------------
    # Bulk controls
    # ------------------------------------------------------------------

    def pause_all(self) -> None:
        """Pause all active tweens"""
        for tween in self.tweens:
            tween.pause()

    def resume_all(self) -> None:
        """Resume all paused tweens"""
        for tween in self.tweens:
            tween.resume()

    # ------------------------------------------------------------------
    # Tag-based controls
    # ------------------------------------------------------------------

    def pause_tag(self, tag: str) -> None:
        """Pause all tweens with the given tag"""
        for tween in self.tweens:
            if tween.tag == tag:
                tween.pause()

    def resume_tag(self, tag: str) -> None:
        """Resume all paused tweens with the given tag"""
        for tween in self.tweens:
            if tween.tag == tag:
                tween.resume()

    def cancel_tag(self, tag: str) -> None:
        """Cancel all tweens with the given tag (removes them next update)"""
        for tween in self.tweens:
            if tween.tag == tag:
                tween.cancel()

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Cancel and remove all tweens"""
        for tween in self.tweens:
            tween.cancel()
        self.tweens.clear()

    @property
    def active_count(self) -> int:
        """Number of tweens that are pending or running"""
        return sum(
            1 for t in self.tweens
            if t.status in (TweenStatus.PENDING, TweenStatus.RUNNING)
        )
