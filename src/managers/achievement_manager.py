"""
Achievement system — definitions, unlock logic, and JSON persistence.
"""
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_DATA_DIR = "data"
_DEFS_FILE = os.path.join(_DATA_DIR, "achievement_definitions.json")
_SAVE_FILE = os.path.join(_DATA_DIR, "achievements.json")


class AchievementType(Enum):
    MILESTONE   = auto()   # One-time event; data-driven via trigger + conditions fields,
                            # awarded by trigger(event_name, payload) — see below
    ACCUMULATOR = auto()   # Running total; persists across sessions, unlocks at target
    THRESHOLD   = auto()   # Unlocks when a measured value is observed at or above target;
                            # data-driven via stat_key + target, triggered by observe()
    STREAK         = auto()   # N consecutive occurrences without reset; counter does NOT persist
                              # and resets at every new GameScene (within-game streaks only)
    SESSION_STREAK = auto()   # Like STREAK but survives GameScene re-init; only reset by an
                              # explicit reset_stat() call or on app restart. Not persisted to disk.
    TIMED          = auto()   # Complete a condition within a time window (handled ad-hoc in game)
    # -------------------------------------------------------------------------
    # PLANNED: COMBO
    # -------------------------------------------------------------------------
    # A COMBO achievement groups two or more sub-conditions into a single award.
    # Two distinct flavours are intended:
    #
    #   1. SEQUENCE COMBO — existing achievement IDs chained together.
    #      When a specific set of already-defined achievements have ALL been
    #      unlocked (in any order), the COMBO is awarded automatically.
    #      Example: unlock achievements 'winner', 'shutout', 'hard_mode',
    #               'speed_run', and 'speed_demon' → award 'silver_trophy'.
    #
    #   2. INLINE COMBO — a list of self-contained sub-achievement definitions
    #      embedded directly inside the COMBO entry in the JSON.  Each
    #      sub-definition is a miniature achievement (type + target/stat_key)
    #      that must all be satisfied within the same game session (or lifetime,
    #      depending on a 'session_only' flag) before the COMBO fires.
    #      Example: score 5 points AND achieve a 10-hit rally AND win → award
    #               'triple_threat'.
    #
    #   3. MIXED — a combination of references to existing achievement IDs and
    #      inline sub-definitions within the same COMBO entry.
    #
    # Planned JSON shape (not yet loaded):
    #
    #   {
    #     "id": "silver_trophy",
    #     "name": "Silver Trophy",
    #     "description": "Complete five core challenges.",
    #     "type": "COMBO",
    #     "combo": {
    #       "requires": ["winner", "shutout", "hard_mode"],   <- existing IDs
    #       "inline": [                                         <- new sub-defs
    #         { "type": "STREAK", "stat_key": "consecutive_scored", "target": 5 },
    #         { "type": "ACCUMULATOR", "stat_key": "total_points", "target": 500 }
    #       ],
    #       "session_only": false   <- if true, all conditions must occur in one game
    #     }
    #   }
    #
    # Implementation notes:
    #   - AchievementManager._check_combos() will be called from award() and
    #     increment() after each unlock / threshold crossing.
    #   - Inline sub-defs are tracked with ephemeral counters keyed by
    #     "<combo_id>.<stat_key>" so they don’t collide with global stats.
    #   - session_only combos have their inline counters reset by reset_streaks().
    # -------------------------------------------------------------------------


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    type: AchievementType
    target: int = 1        # For ACCUMULATOR / THRESHOLD / STREAK
    stat_key: str = ""     # Stat key for ACCUMULATOR / STREAK / THRESHOLD
    hidden: bool = False   # If True, displayed as ??? until unlocked (any type can be hidden)
    trigger: str = ""      # MILESTONE: game event name that can award this achievement
    conditions: Dict[str, Any] = field(default_factory=dict)  # MILESTONE: payload conditions
    unlocked: bool = field(default=False, repr=False)
    progress: int = field(default=0, repr=False)
    unlocked_at: Optional[str] = field(default=None, repr=False)  # ISO-8601 UTC timestamp


def _load_definitions() -> "List[Achievement]":
    """
    Load achievement definitions from data/achievement_definitions.json.

    Supported keys per entry:
      id, name, description, type  (required)
      target      int   default 1
      stat_key    str   default ""
      hidden      bool  default false
      trigger     str   MILESTONE only — game event name (e.g. "point_scored")
      conditions  dict  MILESTONE only — payload key/value constraints; supports
                        Django-style suffixes: __lt, __lte, __gt, __gte, __ne
                        e.g. {"winner": 1, "elapsed__lt": 90, "ai_difficulty": "hard"}
    """
    if not os.path.exists(_DEFS_FILE):
        logger.warning("Achievement definitions file not found: %s", _DEFS_FILE)
        return []
    try:
        with open(_DEFS_FILE, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        result = []
        for entry in raw:
            type_str = entry.get("type", "")
            try:
                ach_type = AchievementType[type_str]
            except KeyError:
                logger.error(
                    "Unknown achievement type %r for id %r — skipping",
                    type_str, entry.get("id")
                )
                continue
            result.append(Achievement(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                type=ach_type,
                target=int(entry.get("target", 1)),
                stat_key=entry.get("stat_key", ""),
                hidden=bool(entry.get("hidden", False)),
                trigger=entry.get("trigger", ""),
                conditions=entry.get("conditions", {}),
            ))
        logger.debug("Loaded %d achievement definitions from %s", len(result), _DEFS_FILE)
        return result
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        logger.error("Could not load achievement definitions: %s", exc)
        return []


class AchievementManager:
    """Manages achievement state, persistence, and unlock notifications."""

    def __init__(self):
        # Load definitions and build a dict for O(1) lookup
        self._achievements: Dict[str, Achievement] = {a.id: a for a in _load_definitions()}
        # Stats store for accumulator / threshold checks
        self._stats: Dict[str, int] = {}
        # Registered callbacks for unlock events
        self._callbacks: List[Callable[[Achievement], None]] = []
        self.load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def award(self, achievement_id: str) -> bool:
        """
        Attempt to unlock an achievement.

        Returns True if newly unlocked, False if already unlocked or unknown.
        """
        ach = self._achievements.get(achievement_id)
        if ach is None:
            logger.warning("Unknown achievement id: %s", achievement_id)
            return False
        if ach.unlocked:
            return False
        ach.unlocked = True
        ach.progress = ach.target
        ach.unlocked_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.info("Achievement unlocked: %s (%s)", ach.id, ach.name)
        self._fire_callbacks(ach)
        self.save()
        return True

    def increment(self, stat_key: str, amount: int = 1) -> None:
        """
        Increment a stat counter and unlock any ACCUMULATOR or STREAK achievements
        whose stat_key matches and whose target has been reached.
        """
        self._stats[stat_key] = self._stats.get(stat_key, 0) + amount

        for ach in self._achievements.values():
            if ach.type in (AchievementType.ACCUMULATOR, AchievementType.STREAK,
                            AchievementType.SESSION_STREAK) \
                    and ach.stat_key == stat_key:
                ach.progress = min(self._stats[stat_key], ach.target)
                if not ach.unlocked and self._stats[stat_key] >= ach.target:
                    ach.unlocked = True
                    ach.unlocked_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    logger.info("Achievement unlocked: %s (%s)", ach.id, ach.name)
                    self._fire_callbacks(ach)
                    self.save()

    def observe(self, stat_key: str, value: float) -> None:
        """
        Report a measured value (e.g. ball speed, reaction time) and unlock
        any THRESHOLD achievements whose stat_key matches and whose target
        the value meets or exceeds.

        Unlike increment(), this does not accumulate — it simply checks whether
        the observed value crosses the defined threshold.  Values are not
        persisted; the condition must be met in-session.
        """
        for ach in self._achievements.values():
            if ach.type == AchievementType.THRESHOLD and ach.stat_key == stat_key:
                if not ach.unlocked and value >= ach.target:
                    ach.unlocked = True
                    ach.progress = ach.target
                    ach.unlocked_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    logger.info("Achievement unlocked: %s (%s)", ach.id, ach.name)
                    self._fire_callbacks(ach)
                    self.save()

    def trigger(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Fire a named game event and award any MILESTONE achievements whose
        ``trigger`` matches and whose ``conditions`` are satisfied by ``payload``.

        Game code fires generic events (e.g. ``"game_won"``) with a data
        payload; which achievements unlock is determined entirely by the JSON
        definitions — no achievement IDs need to appear in game code.

        Condition keys support Django-style comparison suffixes:
          key__lt, key__lte, key__gt, key__gte, key__ne  — comparisons
          key (no suffix)                                 — equality
        """
        if payload is None:
            payload = {}
        for ach in self._achievements.values():
            if ach.type == AchievementType.MILESTONE and ach.trigger == event_name:
                if not ach.unlocked and self._evaluate_conditions(ach.conditions, payload):
                    ach.unlocked = True
                    ach.progress = ach.target
                    ach.unlocked_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    logger.info("Achievement unlocked: %s (%s)", ach.id, ach.name)
                    self._fire_callbacks(ach)
                    self.save()

    def reset_stat(self, stat_key: str) -> None:
        """Reset a stat counter to zero (e.g. on rally break or scoring change)."""
        self._stats[stat_key] = 0
        for ach in self._achievements.values():
            if ach.type in (AchievementType.ACCUMULATOR, AchievementType.STREAK,
                            AchievementType.SESSION_STREAK) \
                    and ach.stat_key == stat_key:
                if not ach.unlocked:
                    ach.progress = 0

    def reset_streaks(self) -> None:
        """Reset all STREAK counters.  Call at the start of every new game."""
        for ach in self._achievements.values():
            if ach.type == AchievementType.STREAK and ach.stat_key:
                self._stats[ach.stat_key] = 0
                if not ach.unlocked:
                    ach.progress = 0
        logger.debug("Streak counters reset")

    def get_progress(self, achievement_id: str) -> Tuple[int, int]:
        """Return (current, target) for an achievement."""
        ach = self._achievements.get(achievement_id)
        if ach is None:
            return (0, 1)
        return (ach.progress, ach.target)

    def is_unlocked(self, achievement_id: str) -> bool:
        ach = self._achievements.get(achievement_id)
        return ach.unlocked if ach else False

    def all_achievements(self) -> List[Achievement]:
        return list(self._achievements.values())

    def on_unlock(self, callback: Callable[[Achievement], None]) -> None:
        """Register a listener that is called whenever an achievement is unlocked."""
        self._callbacks.append(callback)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _evaluate_conditions(self, conditions: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """
        Return True if all conditions are satisfied by the payload.

        Plain keys test equality.  Keys with a double-underscore suffix use
        the corresponding comparison operator:
          __lt  <     __lte  <=    __gt  >     __gte  >=    __ne  !=
        """
        _OPS = {
            'lt':  lambda a, b: a <  b,
            'lte': lambda a, b: a <= b,
            'gt':  lambda a, b: a >  b,
            'gte': lambda a, b: a >= b,
            'ne':  lambda a, b: a != b,
        }
        for key, expected in conditions.items():
            if '__' in key:
                field, op = key.rsplit('__', 1)
                actual = payload.get(field)
                fn = _OPS.get(op)
                if fn is None:
                    logger.warning("Unknown condition operator %r in key %r", op, key)
                    return False
                if actual is None or not fn(actual, expected):
                    return False
            else:
                if payload.get(key) != expected:
                    return False
        return True

    def _streak_stat_keys(self) -> set:
        """Return stat_keys for STREAK and SESSION_STREAK achievements (excluded from persistence)."""
        return {
            a.stat_key for a in self._achievements.values()
            if a.type in (AchievementType.STREAK, AchievementType.SESSION_STREAK) and a.stat_key
        }

    def save(self) -> None:
        """Persist unlocked state and stats to data/achievements.json.

        STREAK progress/stats are intentionally excluded — they reset each run.
        """
        os.makedirs(_DATA_DIR, exist_ok=True)
        streak_keys = self._streak_stat_keys()
        data = {
            "unlocked": {aid: a.unlocked for aid, a in self._achievements.items()},
            "unlocked_at": {aid: a.unlocked_at for aid, a in self._achievements.items() if a.unlocked_at},
            "progress": {
                aid: a.progress for aid, a in self._achievements.items()
                if a.type not in (AchievementType.STREAK, AchievementType.SESSION_STREAK)
            },
            "stats": {k: v for k, v in self._stats.items() if k not in streak_keys},
        }
        try:
            with open(_SAVE_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            logger.debug("Achievements saved to %s", _SAVE_FILE)
        except OSError as exc:
            logger.error("Could not save achievements: %s", exc)

    def load(self) -> None:
        """Load saved state from data/achievements.json if it exists."""
        if not os.path.exists(_SAVE_FILE):
            logger.debug("No achievement save file found — starting fresh")
            return
        try:
            with open(_SAVE_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            unlocked = data.get("unlocked", {})
            unlocked_at = data.get("unlocked_at", {})
            progress = data.get("progress", {})
            self._stats  = data.get("stats", {})
            for aid, ach in self._achievements.items():
                ach.unlocked = bool(unlocked.get(aid, False))
                ach.unlocked_at = unlocked_at.get(aid, None)
                # STREAK and SESSION_STREAK progress is never persisted; leave at 0 on load
                if ach.type not in (AchievementType.STREAK, AchievementType.SESSION_STREAK):
                    ach.progress = int(progress.get(aid, 0))
            logger.debug("Achievements loaded from %s", _SAVE_FILE)
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            logger.error("Could not load achievements: %s", exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fire_callbacks(self, achievement: Achievement) -> None:
        for cb in self._callbacks:
            try:
                cb(achievement)
            except Exception as exc:
                logger.error("Achievement callback error: %s", exc)
