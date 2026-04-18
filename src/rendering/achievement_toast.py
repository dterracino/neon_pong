"""
Achievement toast notification overlay.

State machine: IDLE -> FADE_IN -> HOLD -> FADE_OUT -> DONE
The toast is drawn after end_frame() via draw_text_direct / draw_rounded_rect,
exactly like the FPS display.
"""
import logging
from collections import deque
from enum import Enum, auto

from src.managers.achievement_manager import Achievement

logger = logging.getLogger(__name__)

# Layout constants
_TOAST_W   = 360
_TOAST_H   = 80
_MARGIN    = 16          # from right / top edges
_RADIUS    = 10
_FONT_TITLE  = 22
_FONT_DESC   = 16

# Timing (seconds)
_DUR_FADE_IN  = 0.3
_DUR_HOLD     = 3.0
_DUR_FADE_OUT = 0.5

# Colours (RGBA 0-1)
_COL_PANEL   = (0.05, 0.05, 0.15)   # dark navy base
_COL_BORDER  = (0.0, 0.8, 0.996)    # cyan
_COL_TITLE   = (1.0, 0.9, 0.2)      # yellow
_COL_DESC    = (0.8, 0.8, 0.8)      # light grey
_COL_HEADER  = (0.0, 0.8, 0.996)    # cyan header label


class ToastState(Enum):
    IDLE     = auto()
    FADE_IN  = auto()
    HOLD     = auto()
    FADE_OUT = auto()
    DONE     = auto()


class AchievementToast:
    """Renders queued achievement unlock notifications as a corner toast."""

    def __init__(self, screen_width: int, screen_height: int):
        self._screen_w = screen_width
        self._screen_h = screen_height
        self._queue: deque[Achievement] = deque()
        self._current: Achievement | None = None
        self._state   = ToastState.IDLE
        self._timer   = 0.0
        self._opacity = 0.0   # 0.0 … 1.0

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def push(self, achievement: Achievement) -> None:
        """Enqueue an achievement to display."""
        self._queue.append(achievement)
        logger.debug("Toast queued: %s", achievement.id)

    def update(self, dt: float) -> None:
        """Advance the toast state machine."""
        if self._state == ToastState.IDLE:
            if self._queue:
                self._current = self._queue.popleft()
                self._state   = ToastState.FADE_IN
                self._timer   = 0.0
                self._opacity = 0.0
            return

        self._timer += dt

        if self._state == ToastState.FADE_IN:
            self._opacity = min(self._timer / _DUR_FADE_IN, 1.0)
            if self._timer >= _DUR_FADE_IN:
                self._opacity = 1.0
                self._state   = ToastState.HOLD
                self._timer   = 0.0

        elif self._state == ToastState.HOLD:
            if self._timer >= _DUR_HOLD:
                self._state = ToastState.FADE_OUT
                self._timer = 0.0

        elif self._state == ToastState.FADE_OUT:
            self._opacity = max(1.0 - self._timer / _DUR_FADE_OUT, 0.0)
            if self._timer >= _DUR_FADE_OUT:
                self._opacity = 0.0
                self._state   = ToastState.DONE
                self._timer   = 0.0

        elif self._state == ToastState.DONE:
            self._current = None
            self._state   = ToastState.IDLE

    def render(self, renderer) -> None:
        """Draw the current toast if one is active.  Call after end_frame()."""
        if self._state in (ToastState.IDLE, ToastState.DONE) or self._current is None:
            return
        if self._opacity <= 0.0:
            return

        # Enable blending for proper text rendering
        import moderngl
        ctx = renderer.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        a   = self._opacity
        x   = self._screen_w - _TOAST_W - _MARGIN
        y   = _MARGIN

        # Background panel
        panel_col = (*_COL_PANEL, 0.88 * a)
        renderer.draw_rounded_rect(x, y, _TOAST_W, _TOAST_H, _RADIUS, panel_col)

        # Border (4 thin rects drawn just inside the rounded rect edges)
        border_col = (*_COL_BORDER, a)
        _thickness = 2
        renderer.draw_rect(x + _RADIUS,          y,                              _TOAST_W - 2*_RADIUS, _thickness,  border_col)
        renderer.draw_rect(x + _RADIUS,          y + _TOAST_H - _thickness,      _TOAST_W - 2*_RADIUS, _thickness,  border_col)
        renderer.draw_rect(x,                    y + _RADIUS,                    _thickness,            _TOAST_H - 2*_RADIUS, border_col)
        renderer.draw_rect(x + _TOAST_W - _thickness, y + _RADIUS,              _thickness,            _TOAST_H - 2*_RADIUS, border_col)

        # "ACHIEVEMENT" header label
        header_col = (*_COL_HEADER, a)
        renderer.draw_text_direct(
            "ACHIEVEMENT UNLOCKED",
            x + 14, y + 8,
            _FONT_DESC,
            header_col,
            font_name="sys:arial"
        )

        # Achievement name
        ach = self._current
        display_name = ach.name if ach.unlocked else "???"
        title_col = (*_COL_TITLE, a)
        renderer.draw_text_direct(
            display_name,
            x + 14, y + 28,
            _FONT_TITLE,
            title_col,
            font_name="sys:arial"
        )

        # Description
        desc_col = (*_COL_DESC, a)
        description = ach.description if not ach.hidden or ach.unlocked else "???"
        renderer.draw_text_direct(
            description,
            x + 14, y + 54,
            _FONT_DESC,
            desc_col,
            font_name="sys:arial"
        )

        # Disable blending after rendering
        ctx.disable(moderngl.BLEND)
