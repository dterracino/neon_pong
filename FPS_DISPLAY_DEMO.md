# FPS Display Demo

## Visual Preview

The FPS display appears in the top-left corner when toggled on with F3:

```
┌─────────────────────────────────────────────────────────┐
│ FPS: 60.0                                                │
│ Avg: 59.8                                                │
│ 1% Low: 55.2                                             │
│ 0.1% Low: 52.1                                           │
│                                                          │
│                                                          │
│                          NEON PONG                       │
│                                                          │
│                                                          │
│                         Start Game                       │
│                            Quit                          │
│                                                          │
│                                                          │
│ Player 1: W/S              Player 2: UP/DOWN            │
└─────────────────────────────────────────────────────────┘
```

## In-Game Example

During gameplay, the FPS display shows real-time performance:

```
┌─────────────────────────────────────────────────────────┐
│ FPS: 58.3         Player 1: 5    Player 2: 3           │
│ Avg: 59.2              ┊                                 │
│ 1% Low: 52.8           ┊                                 │
│ 0.1% Low: 48.1         ┊                                 │
│                        ┊                                 │
│                        ┊          ║                      │
│                        ┊                                 │
│          ║             ┊          ║                      │
│          ║             ┊          ║                      │
│          ║         ●   ┊                                 │
│                        ┊          ║                      │
│                        ┊                                 │
│                        ┊                                 │
└─────────────────────────────────────────────────────────┘
```

## Compact Mode Example

If you disable some metrics in configuration:

```python
# In constants.py
FPS_DISPLAY_SHOW_INSTANT = True
FPS_DISPLAY_SHOW_AVERAGE = True
FPS_DISPLAY_SHOW_1_PERCENT = False
FPS_DISPLAY_SHOW_0_1_PERCENT = False
```

The display becomes more compact:

```
┌─────────────────────────────────────────────────────────┐
│ FPS: 60.1                                                │
│ Avg: 59.8                                                │
│                                                          │
│                          NEON PONG                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Understanding the Metrics

### Instant FPS (Frame Rate)
- Shows the current frame rate: 1 / frame_time
- Updates every frame
- Most volatile metric, shows immediate performance
- **Example**: `FPS: 60.0` means the last frame took 16.67ms

### Average FPS
- Average frame rate over the last second (configurable)
- Smoother than instant FPS
- Good for understanding overall performance
- **Example**: `Avg: 59.8` means slightly below 60 FPS on average

### 1% Low
- Average of the worst 1% of frame times
- Indicates performance during stutters
- More meaningful than minimum FPS
- **Example**: `1% Low: 55.2` means worst 1% of frames run at 55 FPS

### 0.1% Low
- Average of the worst 0.1% of frame times
- Captures severe performance drops
- Useful for detecting major hitches
- **Example**: `0.1% Low: 52.1` means worst 0.1% run at 52 FPS

## Performance Impact

The FPS display has minimal performance impact:

- **When Hidden** (F3 off): Negligible (just a boolean check)
- **When Visible** (F3 on): <0.1ms per frame (text rendering, conservative estimate)
- **Memory**: ~1KB for 1 second window at 60 FPS

## Color Scheme

The FPS display uses yellow text (COLOR_YELLOW from constants) which provides good contrast against the dark purple background and neon game elements.

## Toggle Behavior

- **Initial State**: Hidden (off by default)
- **Press F3**: Display toggles between visible/hidden
- **Console Output**: "[DEBUG] Game._handle_events: FPS display enabled/disabled"
- **State Persists**: FPS display state maintained across scenes

## Example Session

```
Game Start
  │
  ├─ FPS display: OFF (default)
  │
  ├─ User presses F3
  │  └─ FPS display: ON
  │
  ├─ User plays game, monitors performance
  │  ├─ FPS: 60.0
  │  ├─ Avg: 59.8
  │  ├─ 1% Low: 55.2
  │  └─ 0.1% Low: 52.1
  │
  ├─ User presses F3
  │  └─ FPS display: OFF
  │
  └─ Game continues normally
```

## Advanced Usage

### Positioning

Change position in `constants.py`:

```python
# Top-right corner
FPS_DISPLAY_POSITION_X = 1100
FPS_DISPLAY_POSITION_Y = 10

# Bottom-left corner
FPS_DISPLAY_POSITION_X = 10
FPS_DISPLAY_POSITION_Y = 650
```

### Custom Metrics

Show only what you need:

```python
# Performance monitoring (instant + lows)
FPS_DISPLAY_SHOW_INSTANT = True
FPS_DISPLAY_SHOW_AVERAGE = False
FPS_DISPLAY_SHOW_1_PERCENT = True
FPS_DISPLAY_SHOW_0_1_PERCENT = True

# Simple monitoring (instant only)
FPS_DISPLAY_SHOW_INSTANT = True
FPS_DISPLAY_SHOW_AVERAGE = False
FPS_DISPLAY_SHOW_1_PERCENT = False
FPS_DISPLAY_SHOW_0_1_PERCENT = False
```

### Averaging Window

Adjust smoothing:

```python
# Quick response (0.5 seconds)
FPS_DISPLAY_AVERAGE_WINDOW = 0.5

# Smooth average (2 seconds)
FPS_DISPLAY_AVERAGE_WINDOW = 2.0
```

## Technical Implementation

The FPS display uses a direct rendering path that bypasses the normal text batching:

1. Frame time is measured by `pygame.Clock.tick()`
2. `FPSCounter.update(dt)` processes the frame time
3. Metrics are calculated from rolling window of frame times
4. If visible, `Game._render_fps_display()` calls `Renderer.draw_text_direct()`
5. Text is rendered directly to screen buffer
6. Display appears on top of all game content

This ensures the FPS display is always visible and not affected by bloom or other post-processing effects.
