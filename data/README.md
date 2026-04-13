# data/ — Achievement Definitions Reference

This folder contains two JSON files:

| File | Purpose |
| ------ | --------- |
| `achievement_definitions.json` | Static definitions for every achievement (read-only at runtime) |
| `achievements.json` | Persisted player progress and unlock state (written by the game) |

---

## achievement_definitions.json

The file is a JSON array of achievement objects. Each object defines one achievement.

### Required fields

| Field | Type | Description |
| ------- | ------ | ------------- |
| `id` | string | Unique identifier used in code. Must be a valid Python identifier style (lowercase, underscores). |
| `name` | string | Human-readable display name shown in the achievement list and unlock toast. |
| `description` | string | One-sentence description shown beneath the name. Hidden achievements show `???` instead until unlocked. |
| `type` | string | Achievement mechanic — see **Types** below. |

### Optional fields

| Field | Type | Default | Description |
| ------- | ------ | --------- | ------------- |
| `target` | integer | `1` | Goal value for ACCUMULATOR, STREAK, and THRESHOLD types. Ignored for MILESTONE. |
| `stat_key` | string | `""` | Internal stat name used by ACCUMULATOR, STREAK, and THRESHOLD. Must match the key passed to `increment()` or `observe()` in game code. |
| `hidden` | boolean | `false` | If `true`, the achievement name, description, and progress are hidden (`???`) in the achievement screen until unlocked. Works on any type. |
| `trigger` | string | `""` | **MILESTONE only.** The game event name that can award this achievement (e.g. `"game_won"`). See **Triggers** below. |
| `conditions` | object | `{}` | **MILESTONE only.** Key/value constraints the event payload must satisfy for the achievement to be awarded. See **Conditions** below. |

---

## Types

### `MILESTONE`

A one-time event-driven achievement. Awarded when a named game event fires and all conditions are met.

- Requires `trigger` to be set.
- Use `conditions` to constrain which events qualify (optional — omit to award on every matching event).
- Progress is binary: locked or unlocked. No progress bar is shown.
- **Not** accumulative — firing the event multiple times does not change anything once unlocked.

```json
{ "id": "winner", "name": "Winner", "description": "Win a game.", "type": "MILESTONE", "trigger": "game_won" }
```

---

### `ACCUMULATOR`

Counts a lifetime running total across all sessions and unlocks when it reaches `target`.

- Requires `stat_key` and `target`.
- Progress persists between sessions.
- A progress bar is shown in the achievement screen while locked.

```json
{ "id": "century", "name": "Century", "description": "Score 100 total points.", "type": "ACCUMULATOR", "target": 100, "stat_key": "total_points" }
```

See **[Stat Keys](#stat-keys)** below for all valid `stat_key` values.

---

### `STREAK`

Counts consecutive occurrences of a single event within **one game**. Unlocks at `target`. The counter resets to 0 either when `reset_stat(stat_key)` is called or when a new game starts (`reset_streaks()` is called in `GameScene.__init__`).

- Requires `stat_key` and `target`.
- **Counter does not persist** between sessions or between matches.
- A progress bar is shown while locked.
- Best combined with `"hidden": true` since the player may not know the mechanic.

```json
{ "id": "hat_trick", "name": "Hat Trick", "description": "Score 3 consecutive points.", "type": "STREAK", "target": 3, "stat_key": "consecutive_scored", "hidden": true }
```

See **[Stat Keys](#stat-keys)** below for all valid `stat_key` values.

---

### `SESSION_STREAK`

Like STREAK, but **survives across multiple matches within the same app session**. The counter is only reset by an explicit `reset_stat()` call in game code — it is not wiped when a new game starts. Still excluded from disk persistence, so it resets to 0 on app restart.

- Requires `stat_key` and `target`.
- Use when the achievement spans multiple consecutive games rather than a single game.
- **Counter does not persist** to disk — must be earned within one app session.
- A progress bar is shown while locked.

```json
{ "id": "hat_trickless", "name": "Hat Trickless", "description": "Lose 3 games in a row to the AI.", "type": "SESSION_STREAK", "target": 3, "stat_key": "consecutive_ai_wins", "hidden": true }
```

See **[Stat Keys](#stat-keys)** below for all valid `stat_key` values.

---

### `THRESHOLD`

Unlocks when a measured value is observed at or above `target` in a single observation. Does not accumulate — the value must reach the threshold in one moment.

- Requires `stat_key` and `target`.
- Values are not persisted; the threshold must be crossed in-session.
- No progress bar is shown (the value is momentary, not cumulative).

```json
{ "id": "speed_demon", "name": "Speed Demon", "description": "Push the ball to its maximum speed.", "type": "THRESHOLD", "stat_key": "ball_speed", "target": 800 }
```

See **[Stat Keys](#stat-keys)** below for all valid `stat_key` values.

---

### `TIMED`

Reserved for achievements that require a condition to be met within a time window. Currently handled ad-hoc in game code rather than through the definitions file. No additional JSON fields are required beyond the base set.

---

### `COMBO` *(planned, not yet implemented)*

Groups multiple sub-conditions into a single award. Two flavours are planned:

- **SEQUENCE** — all listed achievement IDs must be unlocked.
- **INLINE** — embedded sub-definitions (type + stat_key + target) must all be satisfied.

A `session_only` flag will optionally require all conditions to occur within the same game. See the design comment in `src/managers/achievement_manager.py` for the planned JSON shape.

---

## Stat Keys

Stat keys are named counters that connect achievement definitions to game events in the running game. Use these in the `stat_key` field for ACCUMULATOR, STREAK, and THRESHOLD types.

### Increment keys *(ACCUMULATOR and STREAK)*

These keys are updated via `am.increment(stat_key)`. ACCUMULATOR keys accumulate a lifetime total across all sessions; STREAK keys track consecutive occurrences and are zeroed on a break event. A key can be shared by both types at the same time (e.g. `consecutive_scored` drives both the ACCUMULATOR for lifetime count and the STREAK for consecutive runs — add two separate achievement entries pointing at the same key).

| stat_key | Incremented when | Reset when | Persists across sessions |
| ---------- | ----------------- | ----------- | ------------------------- |
| `total_points` | Any player scores a point | never | yes |
| `wins` | Any game ends (either player winning) | never | yes |
| `total_games` | Any game ends | never | yes |
| `consecutive_hits` | A paddle returns the ball | Any player scores a point | no (STREAK) |
| `consecutive_scored` | The same player scores consecutively again | The other player scores | no (STREAK) |
| `consecutive_ai_wins` | AI wins a match (single-player mode only) | Player wins a match | no (SESSION_STREAK) |

> `wins` increments for any winner, including the AI in single-player mode. Use `"winner": 1` in a `game_won` MILESTONE condition if you want to restrict to player-1 wins only.
> **STREAK vs SESSION_STREAK**: Use `STREAK` for within-game streaks (reset on new game). Use `SESSION_STREAK` for cross-game streaks (survive new game, reset on app restart or explicit break).

### Observed values *(THRESHOLD)*

These values are sampled via `am.observe(stat_key, value)` at the moment the measurement is taken. A THRESHOLD achievement unlocks the frame the observed value first meets or exceeds `target`. Values are not accumulated and are not persisted.

| stat_key | What is measured | Checked | Units | Useful range |
| ---------- | ----------------- | ------- | ----- | ------------ |
| `ball_speed` | Ball speed at moment of paddle contact | Every paddle hit | px/s | 400 (initial) → 800 (`BALL_MAX_SPEED`) |

---

## Triggers

Triggers are string event names fired by game code. Each MILESTONE achievement listens for one trigger name.

| Trigger | Fired when | Payload keys |
| --------- | ----------- | -------------- |
| `point_scored` | Any player scores a point | `scorer` (int: `1` or `2`) |
| `game_won` | A game ends with a winner | `winner` (int: `1` or `2`), `opponent_score` (int), `ai_enabled` (bool), `ai_difficulty` (str), `elapsed` (float, seconds) |

---

## Conditions

The `conditions` object specifies constraints that a trigger's payload must satisfy. All conditions must pass for the achievement to be awarded.

### Plain equality

```json
"conditions": { "winner": 1, "ai_enabled": true, "ai_difficulty": "hard" }
```

Checks that `payload["winner"] == 1`, `payload["ai_enabled"] == True`, and `payload["ai_difficulty"] == "hard"`.

### Comparison operators

Append a suffix to the key to use a comparison instead of equality:

| Suffix | Operator | Example |
| -------- | ---------- | --------- |
| `__lt` | `<` | `"elapsed__lt": 90` → `payload["elapsed"] < 90` |
| `__lte` | `<=` | `"elapsed__lte": 90` → `payload["elapsed"] <= 90` |
| `__gt` | `>` | `"score__gt": 5` → `payload["score"] > 5` |
| `__gte` | `>=` | `"score__gte": 5` → `payload["score"] >= 5` |
| `__ne` | `!=` | `"winner__ne": 2` → `payload["winner"] != 2` |

### Empty conditions

Omit `conditions` entirely (or set it to `{}`) to award the achievement whenever the trigger fires, with no further constraints.

---

## Adding a new achievement

1. Choose a type and add your entry to `achievement_definitions.json`.
2. For **ACCUMULATOR / STREAK**: call `am.increment('your_stat_key')` at the right moment in game code (and `am.reset_stat('your_stat_key')` to break a streak).
3. For **THRESHOLD**: call `am.observe('your_stat_key', value)` when a measurement is taken.
4. For **MILESTONE**: either reuse an existing trigger or add a new `am.trigger('event_name', {...})` call in game code, then reference that event name in `"trigger"`.
5. No Python changes are needed if you reuse an existing stat key or trigger.
