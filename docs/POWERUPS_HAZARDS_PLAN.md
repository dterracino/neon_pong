# Powerups and Hazards System - Implementation Plan

**Status**: Planning Phase  
**Created**: 2026-04-18  
**Target**: Add powerups and hazards to enhance gameplay with optional toggles

## Table of Contents

1. [Overview](#overview)
2. [Architecture Design](#architecture-design)
3. [Data Structures](#data-structures)
4. [Integration Points](#integration-points)
5. [Implementation Phases](#implementation-phases)
6. [Testing Strategy](#testing-strategy)
7. [Design Decisions & Rationale](#design-decisions-&amp;-rationale)
8. [Risks & Mitigation](#risks--mitigation)

---

## Overview

### Feature Requirements

**Powerups:**

- Blocks that appear in the game field
- When ball hits powerup, the player who last hit the ball receives the effect
- Examples: Speed Up, Slow Down, Grow/Shrink Paddle, Fast/Slow Ball, Grow/Shrink Ball, Multi Ball
- Global toggle: `powerups_enabled` option

**Hazards:**

- Objects that appear on playfield and affect gameplay (primarily ball)
- Examples: Gravity, Antigravity, Wind, Reflect, Portal, Hyperspace, Redirect, Boost, Slow
- Global toggle: `hazards_enabled` option

### Design Goals

- **Clean Architecture**: Follow existing singleton pattern for managers
- **Maintainability**: Clear separation of concerns, minimal coupling
- **Extensibility**: Easy to add new powerup/hazard types
- **Performance**: No frame drops with multiple balls and effects active
- **Balance**: Configurable spawn rates and effect strengths

---

## Architecture Design

### High-Level Structure

```text
┌─────────────────────────────────────────────────────────────┐
│                         GameScene                            │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────┐       │
│  │   Balls    │  │   Paddles    │  │  Particles    │       │
│  │ (list)     │  │ (player 1+2) │  │               │       │
│  └────────────┘  └──────────────┘  └───────────────┘       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             EffectManager (Singleton)                │   │
│  │  - Tracks active effects on entities                 │   │
│  │  - Applies modifications each frame                  │   │
│  │  - Handles duration countdown and expiration         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  PowerupManager      │  │   HazardManager      │        │
│  │  - Spawn powerups    │  │   - Spawn hazards    │        │
│  │  - Collision checks  │  │   - Apply effects    │        │
│  │  - Effect triggers   │  │   - Force physics    │        │
│  └──────────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Manager Responsibilities

**EffectManager** (Core system - all effects route through here)

- Tracks all active effects with durations
- Applies effect modifications to entity attributes each frame
- Handles effect stacking/replacement logic
- Cleans up expired effects

**PowerupManager** (If `powerups_enabled`)

- Spawns powerups at random intervals and positions
- Detects ball-powerup collisions
- Determines which player receives effect (via `ball.last_hit_by`)
- Triggers visual/audio feedback
- Delegates effect application to EffectManager

**HazardManager** (If `hazards_enabled`)

- Spawns hazards at random intervals and positions
- Applies proximity-based effects (gravity, wind)
- Detects ball-hazard collisions (reflect, teleport)
- Triggers visual/audio feedback
- Delegates effect application to EffectManager

### Key Architectural Decisions

1. **Managers, Not Entity Classes**: Powerups/hazards are lightweight dataclasses, fully managed by their respective managers
2. **Status Effect System**: Effects are reversible, duration-tracked, and managed centrally
3. **Multi-Ball via List**: `GameScene.balls: list[Ball]` replaces `GameScene.ball: Ball`
4. **Player Attribution**: `Ball.last_hit_by: int` tracks which player gets powerup benefits
5. **Time-Based Spawning**: Random intervals with max active limits

---

## Data Structures

### Effect System

```python
# src/managers/effect_manager.py

from enum import Enum
from dataclasses import dataclass

class EffectType(Enum):
    PADDLE_SPEED_MOD = "paddle_speed_mod"
    PADDLE_SIZE_MOD = "paddle_size_mod"
    BALL_SPEED_MOD = "ball_speed_mod"
    BALL_SIZE_MOD = "ball_size_mod"

@dataclass
class ActiveEffect:
    effect_type: EffectType
    target: object  # Paddle or Ball instance
    multiplier: float  # 0.5 = half, 2.0 = double
    duration: float  # Seconds remaining, -1 = permanent
    source: str  # "powerup" or "hazard" (for debug)

class EffectManager:
    _instance = None
    
    def __init__(self):
        self.active_effects: list[ActiveEffect] = []
        # Store original values for reversal
        self.original_values: dict[object, dict] = {}
    
    @classmethod
    def get_instance(cls) -> 'EffectManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def add_effect(self, effect_type: EffectType, target: object, 
                   multiplier: float, duration: float, source: str = "unknown"):
        """Add or replace an effect on a target entity"""
        # Remove any existing effect of same type on same target
        self.active_effects = [e for e in self.active_effects 
                               if not (e.target == target and e.effect_type == effect_type)]
        
        # Store original value if not already stored
        if target not in self.original_values:
            self.original_values[target] = self._capture_original_values(target)
        
        # Add new effect
        effect = ActiveEffect(effect_type, target, multiplier, duration, source)
        self.active_effects.append(effect)
        logger.debug(f"Added effect: {effect_type.value} on {target} (x{multiplier}, {duration}s)")
    
    def update(self, dt: float):
        """Update all active effects - apply modifications and decrement durations"""
        # Apply all effects
        for effect in self.active_effects:
            self._apply_effect(effect)
        
        # Decrement durations
        for effect in self.active_effects:
            if effect.duration > 0:
                effect.duration -= dt
        
        # Remove expired effects
        expired = [e for e in self.active_effects if e.duration <= 0 and e.duration != -1]
        for effect in expired:
            self._remove_effect(effect)
    
    def _apply_effect(self, effect: ActiveEffect):
        """Apply an effect's modification to its target"""
        target = effect.target
        multiplier = effect.multiplier
        
        if effect.effect_type == EffectType.PADDLE_SPEED_MOD:
            original_speed = self.original_values[target].get('speed', 300.0)
            target.speed = original_speed * multiplier
        
        elif effect.effect_type == EffectType.PADDLE_SIZE_MOD:
            original_height = self.original_values[target].get('height', 100.0)
            target.height = original_height * multiplier
        
        elif effect.effect_type == EffectType.BALL_SPEED_MOD:
            # Modify velocity magnitude, preserve direction
            import math
            vx, vy = target.velocity_x, target.velocity_y
            current_speed = math.sqrt(vx*vx + vy*vy)
            if current_speed > 0:
                original_speed = self.original_values[target].get('speed', 300.0)
                new_speed = original_speed * multiplier
                scale = new_speed / current_speed
                target.velocity_x *= scale
                target.velocity_y *= scale
        
        elif effect.effect_type == EffectType.BALL_SIZE_MOD:
            original_size = self.original_values[target].get('size', 15.0)
            target.size = original_size * multiplier
    
    def _remove_effect(self, effect: ActiveEffect):
        """Remove an expired effect and restore original value"""
        self.active_effects.remove(effect)
        
        # Check if any other effects of same type on same target
        same_effects = [e for e in self.active_effects 
                       if e.target == effect.target and e.effect_type == effect.effect_type]
        
        if not same_effects:
            # No more effects of this type - restore original
            self._restore_original_value(effect.target, effect.effect_type)
    
    def _capture_original_values(self, target: object) -> dict:
        """Capture original values from an entity"""
        values = {}
        if hasattr(target, 'speed'):
            values['speed'] = target.speed
        if hasattr(target, 'height'):
            values['height'] = target.height
        if hasattr(target, 'width'):
            values['width'] = target.width
        if hasattr(target, 'size'):
            values['size'] = target.size
        return values
    
    def _restore_original_value(self, target: object, effect_type: EffectType):
        """Restore an entity's original value for a specific effect type"""
        if target not in self.original_values:
            return
        
        originals = self.original_values[target]
        
        if effect_type == EffectType.PADDLE_SPEED_MOD and 'speed' in originals:
            target.speed = originals['speed']
        elif effect_type == EffectType.PADDLE_SIZE_MOD and 'height' in originals:
            target.height = originals['height']
        elif effect_type == EffectType.BALL_SIZE_MOD and 'size' in originals:
            target.size = originals['size']
        # BALL_SPEED_MOD doesn't restore - permanent until next ball reset
    
    def clear_effects(self, target: object = None):
        """Clear all effects, or all effects on a specific target"""
        if target:
            self.active_effects = [e for e in self.active_effects if e.target != target]
            if target in self.original_values:
                del self.original_values[target]
        else:
            self.active_effects.clear()
            self.original_values.clear()
    
    def render_ui(self, renderer):
        """Render UI indicators for active effects"""
        # TODO: Phase 5.1 - Show effect icons near affected entities
        pass
```

### Powerup System

```python
# src/managers/powerup_manager.py

from enum import Enum
from dataclasses import dataclass
import random
import logging

logger = logging.getLogger(__name__)

class PowerupType(Enum):
    SPEED_UP = "speed_up"           # Increase player paddle speed
    SLOW_DOWN = "slow_down"         # Decrease opponent paddle speed
    GROW_PADDLE = "grow_paddle"     # Increase player paddle height
    SHRINK_PADDLE = "shrink_paddle" # Decrease opponent paddle height
    GROW_BALL = "grow_ball"         # Increase ball size
    SHRINK_BALL = "shrink_ball"     # Decrease ball size
    FAST_BALL = "fast_ball"         # Increase ball speed
    SLOW_BALL = "slow_ball"         # Decrease ball speed
    MULTI_BALL = "multi_ball"       # Split into 3 balls

@dataclass
class Powerup:
    x: float
    y: float
    powerup_type: PowerupType
    size: float = 30.0
    lifetime: float = 10.0  # Despawn after 10s if not collected
    sprite: object = None
    
    @property
    def bounds(self):
        from src.utils.constants import AABB
        return AABB(self.x, self.y, self.size, self.size)

class PowerupManager:
    _instance = None
    
    def __init__(self):
        self.powerups: list[Powerup] = []
        self.spawn_timer: float = 0.0
        self.next_spawn_time: float = 0.0
        
        # Dependencies (set via initialize())
        self.balls = None
        self.paddles = None
        self.effect_manager = None
        self.audio_manager = None
        self.asset_manager = None
        self.particle_system = None
    
    @classmethod
    def get_instance(cls) -> 'PowerupManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, balls, paddles, effect_manager, audio_manager, 
                   asset_manager, particle_system):
        """Initialize with dependencies"""
        self.balls = balls
        self.paddles = paddles
        self.effect_manager = effect_manager
        self.audio_manager = audio_manager
        self.asset_manager = asset_manager
        self.particle_system = particle_system
        self._schedule_next_spawn()
        logger.debug("PowerupManager initialized")
    
    def update(self, dt: float):
        """Update powerups - spawn, lifetime, collision"""
        from src.utils.constants import (
            POWERUP_MAX_ACTIVE, POWERUP_SPAWN_MIN_INTERVAL, 
            POWERUP_SPAWN_MAX_INTERVAL
        )
        
        # Update spawn timer
        self.spawn_timer += dt
        
        # Spawn new powerup if ready and under limit
        if (self.spawn_timer >= self.next_spawn_time and 
            len(self.powerups) < POWERUP_MAX_ACTIVE):
            self._spawn_powerup()
            self._schedule_next_spawn()
        
        # Update lifetime and remove expired
        for powerup in self.powerups[:]:
            powerup.lifetime -= dt
            if powerup.lifetime <= 0:
                self.powerups.remove(powerup)
                logger.debug(f"Powerup {powerup.powerup_type.value} expired")
        
        # Check collisions with balls
        self._check_collisions()
    
    def _schedule_next_spawn(self):
        """Schedule next powerup spawn"""
        from src.utils.constants import (
            POWERUP_SPAWN_MIN_INTERVAL, POWERUP_SPAWN_MAX_INTERVAL
        )
        from src.managers.options_manager import OptionsManager
        
        options = OptionsManager.get_instance()
        rate_multiplier = options.get_powerup_spawn_rate()
        
        interval = random.uniform(POWERUP_SPAWN_MIN_INTERVAL, 
                                 POWERUP_SPAWN_MAX_INTERVAL)
        interval /= rate_multiplier  # Higher rate = shorter interval
        
        self.spawn_timer = 0.0
        self.next_spawn_time = interval
    
    def _spawn_powerup(self):
        """Spawn a random powerup at a valid position"""
        from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, POWERUP_SIZE
        
        # Random type
        powerup_type = random.choice(list(PowerupType))
        
        # Random position in center area (avoid edges)
        margin = 100
        x = random.uniform(WINDOW_WIDTH * 0.3, WINDOW_WIDTH * 0.7)
        y = random.uniform(margin, WINDOW_HEIGHT - margin)
        
        # Load sprite if available
        sprite = None
        if self.asset_manager:
            sprite_name = f"powerup_{powerup_type.value}"
            sprite = self.asset_manager.get_image(sprite_name)
        
        powerup = Powerup(x, y, powerup_type, POWERUP_SIZE, 10.0, sprite)
        self.powerups.append(powerup)
        
        # Play spawn sound
        if self.audio_manager:
            self.audio_manager.play_sound('powerup_spawn')
        
        logger.debug(f"Spawned powerup: {powerup_type.value} at ({x:.0f}, {y:.0f})")
    
    def _check_collisions(self):
        """Check for ball-powerup collisions"""
        for ball in self.balls:
            for powerup in self.powerups[:]:
                if ball.bounds.intersects(powerup.bounds):
                    self._collect_powerup(powerup, ball)
                    self.powerups.remove(powerup)
    
    def _collect_powerup(self, powerup: Powerup, ball):
        """Apply powerup effect to the player who last hit the ball"""
        from src.utils.constants import (
            POWERUP_EFFECT_DURATION, COLOR_CYAN, COLOR_PINK
        )
        
        # Determine which player gets the effect
        if ball.last_hit_by == 1:
            player_paddle = self.paddles[0]
            opponent_paddle = self.paddles[1]
            player_color = COLOR_CYAN
        elif ball.last_hit_by == 2:
            player_paddle = self.paddles[1]
            opponent_paddle = self.paddles[0]
            player_color = COLOR_PINK
        else:
            # Ball hasn't been hit yet - give to random player
            player_paddle = random.choice(self.paddles)
            opponent_paddle = self.paddles[1] if player_paddle == self.paddles[0] else self.paddles[0]
            player_color = COLOR_CYAN
        
        # Apply effect based on powerup type
        self._apply_powerup_effect(powerup.powerup_type, player_paddle, 
                                   opponent_paddle, ball)
        
        # Visual feedback
        if self.particle_system:
            self.particle_system.emit(
                powerup.x + powerup.size / 2,
                powerup.y + powerup.size / 2,
                player_color,
                30, 1.0
            )
        
        # Audio feedback
        if self.audio_manager:
            self.audio_manager.play_sound('powerup_collect')
        
        logger.debug(f"Player {ball.last_hit_by} collected {powerup.powerup_type.value}")
    
    def _apply_powerup_effect(self, powerup_type: PowerupType, 
                             player_paddle, opponent_paddle, ball):
        """Apply the specific powerup effect"""
        from src.managers.effect_manager import EffectType
        from src.utils.constants import POWERUP_EFFECT_DURATION
        
        duration = POWERUP_EFFECT_DURATION
        
        if powerup_type == PowerupType.SPEED_UP:
            self.effect_manager.add_effect(
                EffectType.PADDLE_SPEED_MOD, player_paddle, 1.5, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.SLOW_DOWN:
            self.effect_manager.add_effect(
                EffectType.PADDLE_SPEED_MOD, opponent_paddle, 0.6, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.GROW_PADDLE:
            self.effect_manager.add_effect(
                EffectType.PADDLE_SIZE_MOD, player_paddle, 1.4, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.SHRINK_PADDLE:
            self.effect_manager.add_effect(
                EffectType.PADDLE_SIZE_MOD, opponent_paddle, 0.7, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.GROW_BALL:
            self.effect_manager.add_effect(
                EffectType.BALL_SIZE_MOD, ball, 1.5, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.SHRINK_BALL:
            self.effect_manager.add_effect(
                EffectType.BALL_SIZE_MOD, ball, 0.7, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.FAST_BALL:
            self.effect_manager.add_effect(
                EffectType.BALL_SPEED_MOD, ball, 1.3, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.SLOW_BALL:
            self.effect_manager.add_effect(
                EffectType.BALL_SPEED_MOD, ball, 0.7, duration, "powerup"
            )
        
        elif powerup_type == PowerupType.MULTI_BALL:
            # Phase 3 - Multi-ball implementation
            self._split_ball(ball)
    
    def _split_ball(self, ball):
        """Split ball into 3 balls (Phase 3 implementation)"""
        # TODO: Implement in Phase 3.2
        logger.warning("Multi-ball not yet implemented")
    
    def render(self, renderer):
        """Render all active powerups"""
        from src.utils.constants import COLOR_YELLOW
        
        for powerup in self.powerups:
            if powerup.sprite:
                renderer.draw_sprite(
                    powerup.sprite,
                    powerup.x, powerup.y,
                    powerup.size, powerup.size,
                    COLOR_YELLOW
                )
            else:
                # Fallback: colored square
                renderer.draw_rect(
                    powerup.x, powerup.y,
                    powerup.size, powerup.size,
                    COLOR_YELLOW
                )
    
    def clear(self):
        """Clear all powerups (game over, reset, etc.)"""
        self.powerups.clear()
        self.spawn_timer = 0.0
        self._schedule_next_spawn()
```

### Hazard System

```python
# src/managers/hazard_manager.py

from enum import Enum
from dataclasses import dataclass, field
import random
import math
import logging

logger = logging.getLogger(__name__)

class HazardType(Enum):
    GRAVITY = "gravity"           # Pull ball toward hazard
    ANTIGRAVITY = "antigravity"   # Push ball away from hazard
    WIND = "wind"                 # Apply velocity nudge
    REFLECT = "reflect"           # Bounce ball like wall
    PORTAL = "portal"             # Teleport ball (paired)
    HYPERSPACE = "hyperspace"     # Random teleport
    REDIRECT = "redirect"         # Change trajectory
    BOOST = "boost"               # Increase speed
    SLOW = "slow"                 # Decrease speed

@dataclass
class Hazard:
    x: float
    y: float
    hazard_type: HazardType
    size: float = 40.0
    lifetime: float = 15.0
    active: bool = True
    sprite: object = None
    data: dict = field(default_factory=dict)  # Hazard-specific data
    
    @property
    def bounds(self):
        from src.utils.constants import AABB
        return AABB(self.x, self.y, self.size, self.size)

class HazardManager:
    _instance = None
    
    def __init__(self):
        self.hazards: list[Hazard] = []
        self.spawn_timer: float = 0.0
        self.next_spawn_time: float = 0.0
        
        # Dependencies
        self.balls = None
        self.effect_manager = None
        self.audio_manager = None
        self.asset_manager = None
    
    @classmethod
    def get_instance(cls) -> 'HazardManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, balls, effect_manager, audio_manager, asset_manager):
        """Initialize with dependencies"""
        self.balls = balls
        self.effect_manager = effect_manager
        self.audio_manager = audio_manager
        self.asset_manager = asset_manager
        self._schedule_next_spawn()
        logger.debug("HazardManager initialized")
    
    def update(self, dt: float):
        """Update hazards - spawn, lifetime, effects"""
        from src.utils.constants import HAZARD_MAX_ACTIVE
        
        # Update spawn timer
        self.spawn_timer += dt
        
        # Spawn new hazard if ready
        if (self.spawn_timer >= self.next_spawn_time and 
            len(self.hazards) < HAZARD_MAX_ACTIVE):
            self._spawn_hazard()
            self._schedule_next_spawn()
        
        # Update lifetime
        for hazard in self.hazards[:]:
            hazard.lifetime -= dt
            if hazard.lifetime <= 0:
                self.hazards.remove(hazard)
                logger.debug(f"Hazard {hazard.hazard_type.value} expired")
        
        # Apply hazard effects
        self._apply_hazard_effects(dt)
    
    def _schedule_next_spawn(self):
        """Schedule next hazard spawn"""
        from src.utils.constants import (
            HAZARD_SPAWN_MIN_INTERVAL, HAZARD_SPAWN_MAX_INTERVAL
        )
        from src.managers.options_manager import OptionsManager
        
        options = OptionsManager.get_instance()
        rate_multiplier = options.get_hazard_spawn_rate()
        
        interval = random.uniform(HAZARD_SPAWN_MIN_INTERVAL, 
                                 HAZARD_SPAWN_MAX_INTERVAL)
        interval /= rate_multiplier
        
        self.spawn_timer = 0.0
        self.next_spawn_time = interval
    
    def _spawn_hazard(self):
        """Spawn a random hazard"""
        from src.utils.constants import (
            WINDOW_WIDTH, WINDOW_HEIGHT, HAZARD_SIZE
        )
        
        # Random type (excluding portal for now - needs pairing logic)
        hazard_types = [t for t in HazardType if t != HazardType.PORTAL]
        hazard_type = random.choice(hazard_types)
        
        # Random position
        margin = 150
        x = random.uniform(margin, WINDOW_WIDTH - margin)
        y = random.uniform(margin, WINDOW_HEIGHT - margin)
        
        # Load sprite
        sprite = None
        if self.asset_manager:
            sprite_name = f"hazard_{hazard_type.value}"
            sprite = self.asset_manager.get_image(sprite_name)
        
        # Create hazard with type-specific data
        data = {}
        if hazard_type == HazardType.WIND:
            # Random wind direction
            angle = random.uniform(0, 2 * math.pi)
            data['direction'] = (math.cos(angle), math.sin(angle))
        
        hazard = Hazard(x, y, hazard_type, HAZARD_SIZE, 15.0, True, sprite, data)
        self.hazards.append(hazard)
        
        logger.debug(f"Spawned hazard: {hazard_type.value} at ({x:.0f}, {y:.0f})")
    
    def _apply_hazard_effects(self, dt: float):
        """Apply hazard effects to balls"""
        for ball in self.balls:
            for hazard in self.hazards:
                if not hazard.active:
                    continue
                
                # Check collision for collision-based hazards
                colliding = ball.bounds.intersects(hazard.bounds)
                
                # Apply effects based on type
                if hazard.hazard_type == HazardType.GRAVITY:
                    self._apply_gravity(ball, hazard, dt)
                
                elif hazard.hazard_type == HazardType.ANTIGRAVITY:
                    self._apply_antigravity(ball, hazard, dt)
                
                elif hazard.hazard_type == HazardType.WIND:
                    self._apply_wind(ball, hazard, dt)
                
                elif colliding:
                    # Collision-based effects
                    if hazard.hazard_type == HazardType.REFLECT:
                        self._apply_reflect(ball, hazard)
                    
                    elif hazard.hazard_type == HazardType.REDIRECT:
                        self._apply_redirect(ball, hazard)
                    
                    elif hazard.hazard_type == HazardType.BOOST:
                        self._apply_boost(ball, hazard)
                    
                    elif hazard.hazard_type == HazardType.SLOW:
                        self._apply_slow(ball, hazard)
                    
                    elif hazard.hazard_type == HazardType.HYPERSPACE:
                        self._apply_hyperspace(ball, hazard)
    
    def _apply_gravity(self, ball, hazard, dt):
        """Pull ball toward hazard"""
        from src.utils.constants import HAZARD_EFFECT_STRENGTH
        
        # Calculate direction and distance
        dx = (hazard.x + hazard.size/2) - (ball.x + ball.size/2)
        dy = (hazard.y + hazard.size/2) - (ball.y + ball.size/2)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 200:  # Effect radius
            # Force decreases with distance
            force = HAZARD_EFFECT_STRENGTH * (200 - distance) / 200
            
            # Normalize direction and apply force
            if distance > 0:
                ball.velocity_x += (dx / distance) * force * dt * 500
                ball.velocity_y += (dy / distance) * force * dt * 500
    
    def _apply_antigravity(self, ball, hazard, dt):
        """Push ball away from hazard"""
        from src.utils.constants import HAZARD_EFFECT_STRENGTH
        
        dx = (ball.x + ball.size/2) - (hazard.x + hazard.size/2)
        dy = (ball.y + ball.size/2) - (hazard.y + hazard.size/2)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 200:
            force = HAZARD_EFFECT_STRENGTH * (200 - distance) / 200
            
            if distance > 0:
                ball.velocity_x += (dx / distance) * force * dt * 500
                ball.velocity_y += (dy / distance) * force * dt * 500
    
    def _apply_wind(self, ball, hazard, dt):
        """Apply constant wind force"""
        from src.utils.constants import HAZARD_EFFECT_STRENGTH
        
        direction = hazard.data.get('direction', (1, 0))
        ball.velocity_x += direction[0] * HAZARD_EFFECT_STRENGTH * dt * 300
        ball.velocity_y += direction[1] * HAZARD_EFFECT_STRENGTH * dt * 300
    
    def _apply_reflect(self, ball, hazard):
        """Bounce ball off hazard like a wall"""
        # Simple reflection - reverse velocity
        ball.velocity_x *= -1
        ball.velocity_y *= -1
        
        if self.audio_manager:
            self.audio_manager.play_sound('wall_hit')
    
    def _apply_redirect(self, ball, hazard):
        """Change ball trajectory to random angle"""
        import math
        
        # Get current speed
        speed = math.sqrt(ball.velocity_x**2 + ball.velocity_y**2)
        
        # Random new angle
        angle = random.uniform(0, 2 * math.pi)
        ball.velocity_x = math.cos(angle) * speed
        ball.velocity_y = math.sin(angle) * speed
        
        if self.audio_manager:
            self.audio_manager.play_sound('hazard_activate')
        
        # Deactivate hazard after use
        hazard.active = False
    
    def _apply_boost(self, ball, hazard):
        """Increase ball speed"""
        ball.velocity_x *= 1.3
        ball.velocity_y *= 1.3
        
        if self.audio_manager:
            self.audio_manager.play_sound('hazard_activate')
        
        hazard.active = False
    
    def _apply_slow(self, ball, hazard):
        """Decrease ball speed"""
        ball.velocity_x *= 0.7
        ball.velocity_y *= 0.7
        
        if self.audio_manager:
            self.audio_manager.play_sound('hazard_activate')
        
        hazard.active = False
    
    def _apply_hyperspace(self, ball, hazard):
        """Teleport ball to random location"""
        from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT
        
        margin = 100
        ball.x = random.uniform(margin, WINDOW_WIDTH - margin)
        ball.y = random.uniform(margin, WINDOW_HEIGHT - margin)
        
        if self.audio_manager:
            self.audio_manager.play_sound('portal')
        
        hazard.active = False
    
    def render(self, renderer):
        """Render all active hazards"""
        from src.utils.constants import COLOR_PURPLE
        
        for hazard in self.hazards:
            if hazard.sprite:
                renderer.draw_sprite(
                    hazard.sprite,
                    hazard.x, hazard.y,
                    hazard.size, hazard.size,
                    COLOR_PURPLE
                )
            else:
                # Fallback: colored square
                renderer.draw_rect(
                    hazard.x, hazard.y,
                    hazard.size, hazard.size,
                    COLOR_PURPLE
                )
    
    def clear(self):
        """Clear all hazards"""
        self.hazards.clear()
        self.spawn_timer = 0.0
        self._schedule_next_spawn()
```

### Constants

```python
# Add to src/utils/constants.py

# Powerup constants
POWERUP_SIZE = 30
POWERUP_SPAWN_MIN_INTERVAL = 5.0
POWERUP_SPAWN_MAX_INTERVAL = 12.0
POWERUP_MAX_ACTIVE = 2
POWERUP_LIFETIME = 10.0
POWERUP_EFFECT_DURATION = 8.0

# Hazard constants
HAZARD_SIZE = 40
HAZARD_SPAWN_MIN_INTERVAL = 8.0
HAZARD_SPAWN_MAX_INTERVAL = 15.0
HAZARD_MAX_ACTIVE = 3
HAZARD_LIFETIME = 15.0
HAZARD_EFFECT_STRENGTH = 0.3
```

---

## Integration Points

### 1. Ball Modifications

```python
# In src/entities/ball.py

class Ball:
    def __init__(self, x: float, y: float):
        # ... existing code ...
        self.last_hit_by: int = 0  # 0=neutral, 1=player1, 2=player2
```

**In GameScene paddle collision:**

```python
if self.ball.bounds.intersects(self.paddle1.bounds):
    self.ball.last_hit_by = 1
    # ... existing bounce code ...

if self.ball.bounds.intersects(self.paddle2.bounds):
    self.ball.last_hit_by = 2
    # ... existing bounce code ...
```

### 2. OptionsManager Additions

```python
# In src/managers/options_manager.py

def __init__(self):
    # ... existing settings ...
    self.powerups_enabled = False
    self.hazards_enabled = False
    self.powerup_spawn_rate = 1.0
    self.hazard_spawn_rate = 1.0

def set_powerups_enabled(self, enabled: bool) -> None:
    self.powerups_enabled = enabled
    logger.debug("Powerups %s", "enabled" if enabled else "disabled")

def is_powerups_enabled(self) -> bool:
    return self.powerups_enabled

def set_powerup_spawn_rate(self, rate: float) -> None:
    self.powerup_spawn_rate = max(0.5, min(2.0, rate))

def get_powerup_spawn_rate(self) -> float:
    return self.powerup_spawn_rate

# Similar getters/setters for hazards...
```

### 3. GameScene Integration

```python
# In src/scenes/game_scene.py

def __init__(self, ...):
    # ... existing entity creation ...
    
    # Initialize effect manager
    self.effect_manager = EffectManager.get_instance()
    
    # Initialize powerup manager if enabled
    options = OptionsManager.get_instance()
    if options.is_powerups_enabled():
        self.powerup_manager = PowerupManager.get_instance()
        self.powerup_manager.initialize(
            [self.ball],  # Will become self.balls in Phase 3
            [self.paddle1, self.paddle2],
            self.effect_manager,
            self.audio_manager,
            self.asset_manager,
            self.particles
        )
    else:
        self.powerup_manager = None
    
    # Initialize hazard manager if enabled
    if options.is_hazards_enabled():
        self.hazard_manager = HazardManager.get_instance()
        self.hazard_manager.initialize(
            [self.ball],
            self.effect_manager,
            self.audio_manager,
            self.asset_manager
        )
    else:
        self.hazard_manager = None

def update(self, dt: float):
    # ... existing entity updates ...
    
    # Update effect manager (applies active effects)
    self.effect_manager.update(dt)
    
    # Update powerups
    if self.powerup_manager:
        self.powerup_manager.update(dt)
    
    # Update hazards
    if self.hazard_manager:
        self.hazard_manager.update(dt)

def render(self):
    self.renderer.begin_frame()
    
    # ... existing rendering ...
    
    # Render powerups
    if self.powerup_manager:
        self.powerup_manager.render(self.renderer)
    
    # Render hazards
    if self.hazard_manager:
        self.hazard_manager.render(self.renderer)
    
    # Render effect UI
    self.effect_manager.render_ui(self.renderer)
    
    # ... existing rendering ...
    
    self.renderer.end_frame()
```

---

## Implementation Phases

### Phase 1: Foundation ⬅️ START HERE

**Status**: Not Started  
**Estimated Time**: 1 day

#### Tasks

- [ ] **1.1** Create `src/managers/effect_manager.py` with EffectManager singleton
  - `EffectType` enum
  - `ActiveEffect` dataclass
  - `add_effect()`, `update()`, `clear_effects()` methods
  - Effect application logic for paddle/ball modifications

- [ ] **1.2** Add Ball player tracking
  - Add `last_hit_by: int = 0` to `Ball.__init__`
  - Set `ball.last_hit_by` in GameScene paddle collisions

- [ ] **1.3** Add constants to `src/utils/constants.py`
  - All POWERUP_* constants
  - All HAZARD_* constants

- [ ] **1.4** Update OptionsManager
  - Add `powerups_enabled`, `hazards_enabled` settings
  - Add `powerup_spawn_rate`, `hazard_spawn_rate` settings
  - Add getters/setters following existing pattern

**Validation**: Unit tests for EffectManager, Ball.last_hit_by tracking works

---

### Phase 2: Powerup System (MVP)

**Status**: Not Started  
**Estimated Time**: 2 days  
**Dependencies**: Phase 1 complete

#### Tasks

- [ ] **2.1** Create `src/managers/powerup_manager.py`
  - `PowerupType` enum
  - `Powerup` dataclass
  - `PowerupManager` singleton with spawn/collision/collection logic

- [ ] **2.2** Implement simple powerup effects
  - Speed Up, Slow Down (paddle speed)
  - Grow Paddle, Shrink Paddle (paddle size)

- [ ] **2.3** Implement ball powerup effects
  - Grow Ball, Shrink Ball (ball size)
  - Fast Ball, Slow Ball (ball speed)

- [ ] **2.4** Integrate into GameScene
  - Initialize PowerupManager if enabled
  - Update and render in game loop

- [ ] **2.5** Add powerup assets (manual)
  - Create/acquire 9 powerup sprites
  - Add sound effects
  - Place in `assets/images/` and `assets/sounds/`

**Validation**: Powerups spawn, can be collected, effects apply correctly

---

### Phase 3: Multi-Ball System

**Status**: Not Started  
**Estimated Time**: 2-3 days  
**Dependencies**: Phase 2 complete

#### Tasks

- [ ] **3.1** Refactor GameScene to multi-ball
  - Change `self.ball` to `self.balls: list[Ball]`
  - Update all ball update/collision code to loop
  - Modify scoring: remove scored ball, reset if last
  - Update rendering for multiple balls
  - Update AI to track nearest/primary ball

- [ ] **3.2** Implement Multi-Ball powerup
  - Add ball splitting logic (±30° angles)
  - Preserve speed and last_hit_by
  - Limit to 5 balls max

- [ ] **3.3** Test multi-ball interactions
  - Multi-ball + grow ball
  - Multi-ball + fast ball
  - Multi-ball scoring
  - AI behavior with multiple balls

**Validation**: Multi-ball powerup creates 3 balls, all balls interact correctly, no crashes

---

### Phase 4: Hazard System

**Status**: Not Started  
**Estimated Time**: 2-3 days  
**Dependencies**: Phase 1 complete (can parallel with Phase 2)

#### Tasks

- [ ] **4.1** Create `src/managers/hazard_manager.py`
  - `HazardType` enum
  - `Hazard` dataclass
  - `HazardManager` singleton with spawn/effects logic

- [ ] **4.2** Implement force-based hazards
  - Gravity (pull toward)
  - Antigravity (push away)
  - Wind (constant nudge)

- [ ] **4.3** Implement collision-based hazards
  - Reflect (bounce like wall)
  - Redirect (random trajectory)
  - Boost/Slow (speed modification)

- [ ] **4.4** Implement teleport hazards
  - Hyperspace (random teleport)
  - Portal (paired teleport) - optional, complex

- [ ] **4.5** Integrate into GameScene
  - Initialize HazardManager if enabled
  - Update and render in game loop

- [ ] **4.6** Add hazard assets (manual)
  - Create/acquire 9 hazard sprites
  - Add sound effects

**Validation**: Hazards spawn, effects apply to balls, physics feel correct

---

### Phase 5: UI & Polish

**Status**: Not Started  
**Estimated Time**: 1-2 days  
**Dependencies**: Phases 2 and 4 complete

#### Tasks

- [ ] **5.1** Create effect UI indicators
  - Display active effects as icons near paddles
  - Show timer countdowns
  - Color-code by effect type

- [ ] **5.2** Enhance visual effects
  - Particle bursts on powerup collect
  - Particle bursts on hazard activation
  - Glow effects on powerups/hazards
  - Pulse animation on spawn

- [ ] **5.3** Balance tuning (manual playtesting)
  - Adjust spawn rates
  - Tune effect durations and intensities
  - Adjust lifetimes
  - Document final values

**Validation**: UI is clear and helpful, effects look polished, gameplay feels balanced

---

### Phase 6: Testing & Documentation

**Status**: Not Started  
**Estimated Time**: 1-2 days  
**Dependencies**: All phases 1-5 complete

#### Tasks

- [ ] **6.1** Unit tests
  - `tests/test_effect_manager.py`
  - `tests/test_powerup_manager.py`
  - `tests/test_hazard_manager.py`
  - `tests/test_multi_ball.py`

- [ ] **6.2** Integration tests
  - `tests/test_powerups_hazards_integration.py`
  - Test with both systems enabled
  - Test AI reactions
  - Performance testing

- [ ] **6.3** Update documentation
  - Add to README.md
  - Create POWERUPS_HAZARDS.md with effect descriptions
  - Update controls/options docs
  - Add screenshots/GIFs

**Validation**: >80% test coverage, all tests pass, documentation complete

---

## Testing Strategy

### Unit Tests

**EffectManager** (`tests/test_effect_manager.py`)

- Effect application modifies attributes correctly
- Effect stacking replaces same type
- Duration countdown and expiration
- clear_effects removes all effects

**PowerupManager** (`tests/test_powerup_manager.py`)

- Spawn respects max limits and intervals
- Collision detection triggers effects
- Player attribution via last_hit_by
- Powerup lifetime despawning

**HazardManager** (`tests/test_hazard_manager.py`)

- Spawn respects max limits and intervals
- Force calculations (gravity, wind)
- Collision hazards trigger correctly
- Teleport logic works

**Multi-Ball** (`tests/test_multi_ball.py`)

- Ball splitting creates correct angles
- Scoring removes individual balls
- Last ball reset works
- All balls interact with powerups/hazards

### Integration Tests

**Full System** (`tests/test_powerups_hazards_integration.py`)

- Run GameScene with both enabled
- Simulate powerup collection
- Simulate hazard interactions
- Test AI with multi-ball

### Edge Cases

- [ ] Multi-ball + grow ball → all balls grow
- [ ] Speed up + slow down on same paddle → last effect wins
- [ ] Powerup spawn during game over → handled gracefully
- [ ] Hazard teleport out of bounds → re-teleport or score
- [ ] Multi-ball all out simultaneously → proper reset
- [ ] Max powerups reached → no more spawns
- [ ] Conflicting effects resolved by last effect

---

## Design Decisions & Rationale

### Decision 1: Managers vs Entity Classes

**Chosen**: Managers handle everything  
**Alternative**: Full entity classes for Powerup/Hazard

**Rationale**:

- Matches existing pattern (AudioManager, AssetManager, etc.)
- Powerups/hazards are simple data, not complex behavior
- Manager centralizes spawning logic
- Easier to balance and tune

### Decision 2: Status Effect System

**Chosen**: EffectManager with ActiveEffect tracking  
**Alternative**: Direct permanent modification

**Rationale**:

- Effects need durations and reversal
- Multiple effects can stack/conflict
- Clean separation of concerns
- Extensible and testable

### Decision 3: Multi-Ball Implementation

**Chosen**: List of Ball instances  
**Alternative**: Ball.split() method

**Rationale**:

- Simple, clear ownership
- Easy iteration for collisions
- Natural removal on scoring
- Minimal refactoring needed

### Decision 4: Hazard Trigger Mechanisms

**Chosen**: Proximity-based for forces, collision for instant effects  
**Alternative**: All collision-based

**Rationale**:

- Gravity/wind feel better with area of effect
- Instant effects need precise collision
- Mirrors real physics
- Allows varied gameplay

### Decision 5: Spawn System

**Chosen**: Time-based with random intervals  
**Alternative**: Score-based spawning

**Rationale**:

- Maintains constant pressure
- Prevents predictability
- Max limits prevent clutter
- Easy to tune
- Avoids snowball effect

---

## Risks & Mitigation

### Risk 1: Multi-Ball Refactor Breaks Gameplay

**Impact**: High  
**Mitigation**:

- Separate branch for development
- Extensive regression testing
- Keep `balls[0]` as primary for AI
- Test early with automated tests

### Risk 2: Performance Degradation

**Impact**: Medium  
**Mitigation**:

- Limit max active powerups/hazards
- Profile worst-case (5 balls + max effects)
- Optimize particle counts
- Use spatial partitioning if needed

### Risk 3: Effect Stacking Imbalance

**Impact**: Medium  
**Mitigation**:

- Effect replacement (same type overwrites)
- Cap multipliers (min 0.4x, max 3.0x)
- Extensive playtesting
- All values in constants.py

### Risk 4: AI Can't Handle Multi-Ball

**Impact**: Medium  
**Mitigation**:

- AI tracks nearest ball
- Reduce reaction time for multi-ball
- Difficulty modifier for multi-ball
- Test with adaptive difficulty

### Risk 5: Spawn RNG Creates Unfairness

**Impact**: Low-Medium  
**Mitigation**:

- Spawn in center third of field
- Spawn away from paddles
- Track which player benefits
- Adjust logic if biased

---

## Success Criteria

- [ ] All 9 powerup types functional
- [ ] All 9 hazard types functional (Portal optional)
- [ ] Multi-ball works with up to 5 balls
- [ ] Independent toggle options
- [ ] Visual and audio feedback for all events
- [ ] UI shows active effects with timers
- [ ] AI adapts to multi-ball
- [ ] 60 FPS in worst-case scenario
- [ ] >80% test coverage
- [ ] Complete documentation
- [ ] Balanced gameplay confirmed by playtesting

---

## Progress Tracking

### Current Phase: Phase 1 (Foundation)

**Started**: Not yet  
**Completed Tasks**: 0/4

### Overall Progress

- [ ] Phase 1: Foundation (0%)
- [ ] Phase 2: Powerup System (0%)
- [ ] Phase 3: Multi-Ball (0%)
- [ ] Phase 4: Hazard System (0%)
- [ ] Phase 5: UI & Polish (0%)
- [ ] Phase 6: Testing & Docs (0%)

---

## Next Steps

1. **Review this plan** - Confirm architecture and approach
2. **Begin Phase 1** - Start with EffectManager implementation
3. **Create test branch** - `feature/powerups-hazards`
4. **Implement foundation** - Complete Phase 1 tasks
5. **Validate** - Test EffectManager before proceeding

---

## Future Enhancements

Post-launch ideas for future iterations:

- More powerup types (Shield, Freeze, Reverse Controls)
- More hazard types (Black Hole, Lightning, Fog)
- Powerup combos (3x same type = mega effect)
- Custom game modes ("Powerup Frenzy", "Hazard Hell")
- Achievement integration
- Powerup that clears all hazards
- Replay system with powerups/hazards
- Plugin system for custom types

---

**Last Updated**: 2026-04-18  
**Document Version**: 1.0
