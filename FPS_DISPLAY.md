# FPS Display System

## Overview

The FPS (Frames Per Second) display system provides real-time performance monitoring for the game. It tracks multiple frame rate metrics and can be toggled on/off during gameplay.

## Features

### Metrics Tracked

1. **Instant FPS** - Current frame rate (1/frame_time)
2. **Average FPS** - Average frame rate over a time window (default: 1 second)
3. **1% Low** - Average of the worst 1% of frame times (useful for detecting stutters)
4. **0.1% Low** - Average of the worst 0.1% of frame times (detects severe stutters)

### Usage

- **Toggle Display**: Press `F3` during gameplay to show/hide the FPS display
- **Location**: Top-left corner of the screen (configurable)
- **Color**: Yellow text (COLOR_YELLOW from constants)

## Configuration

All FPS display settings are configurable in `src/utils/constants.py`:

```python
# FPS Display settings
FPS_DISPLAY_SHOW_INSTANT = True     # Show instant frame rate
FPS_DISPLAY_SHOW_AVERAGE = True     # Show average frame rate
FPS_DISPLAY_SHOW_1_PERCENT = True   # Show 1% low
FPS_DISPLAY_SHOW_0_1_PERCENT = True # Show 0.1% low
FPS_DISPLAY_AVERAGE_WINDOW = 1.0    # Window size for average calculation (seconds)
FPS_DISPLAY_POSITION_X = 10         # X position for FPS display
FPS_DISPLAY_POSITION_Y = 10         # Y position for FPS display
```

### Customization Options

#### Show/Hide Specific Metrics

Set any of the `FPS_DISPLAY_SHOW_*` constants to `False` to hide that metric:

```python
# Example: Only show instant and average FPS
FPS_DISPLAY_SHOW_INSTANT = True
FPS_DISPLAY_SHOW_AVERAGE = True
FPS_DISPLAY_SHOW_1_PERCENT = False
FPS_DISPLAY_SHOW_0_1_PERCENT = False
```

#### Adjust Average Window

Change `FPS_DISPLAY_AVERAGE_WINDOW` to adjust how many seconds of data are used for calculating averages:

```python
# Use 2 seconds of data for smoother averages
FPS_DISPLAY_AVERAGE_WINDOW = 2.0
```

#### Change Display Position

Modify `FPS_DISPLAY_POSITION_X` and `FPS_DISPLAY_POSITION_Y` to move the display:

```python
# Position in top-right corner
FPS_DISPLAY_POSITION_X = 1100
FPS_DISPLAY_POSITION_Y = 10
```

## Implementation Details

### Architecture

The FPS display system consists of three main components:

#### 1. FPSCounter Class (`src/utils/fps_counter.py`)

Tracks frame times and calculates metrics:
- Maintains a rolling window of frame times
- Calculates instant FPS from delta time
- Computes average FPS over the window
- Calculates percentile lows by sorting frame times

```python
counter = FPSCounter(average_window=1.0)
counter.update(dt)  # Update with each frame's delta time
instant, avg, low_1, low_01 = counter.get_metrics()
```

#### 2. Game Integration (`src/game.py`)

The `Game` class integrates the FPS counter:
- Creates FPS counter instance during initialization
- Updates counter each frame with delta time
- Handles F3 key press to toggle visibility
- Renders FPS display after scene rendering

```python
# In Game.__init__()
self.fps_counter = FPSCounter(average_window=FPS_DISPLAY_AVERAGE_WINDOW)

# In Game.run()
self.fps_counter.update(self.dt)
if self.fps_counter.is_visible():
    self._render_fps_display()

# In Game._handle_events()
if event.key == pygame.K_F3:
    self.fps_counter.toggle_visibility()
```

#### 3. Renderer Support (`src/rendering/renderer.py`)

The `Renderer` class provides direct text rendering:
- `draw_text_direct()` method renders text immediately to screen
- Bypasses the text batching system used by scenes
- Allows rendering FPS display after `end_frame()` has been called

```python
renderer.draw_text_direct(
    "FPS: 60.0", 
    x, y, 
    FONT_SIZE_SMALL, 
    COLOR_YELLOW
)
```

### Percentile Low Calculations

The 1% and 0.1% low metrics are calculated as follows:

1. Collect frame times in the rolling window
2. Sort frame times from slowest to fastest (highest to lowest)
3. Take the worst 1% (or 0.1%) of frame times
4. Calculate the average of those worst frame times
5. Convert average frame time to FPS (1/time)

This provides a more accurate picture of performance issues than just looking at minimum FPS, as it averages the worst frames rather than reporting a single outlier.

**Example:**
- If you have 100 frames in the window
- 1% low uses the 1 worst frame time
- 0.1% low uses the 1 worst frame time (minimum 1)
- For 1000 frames: 1% = 10 worst, 0.1% = 1 worst

## Rendering Pipeline

The FPS display is rendered using a special direct rendering path:

1. Scene calls `renderer.begin_frame()` and renders game objects
2. Scene calls `renderer.end_frame()` which:
   - Flushes batched text to UI layer
   - Applies bloom post-processing
   - Renders final image to screen
3. If FPS display is visible, `Game._render_fps_display()` is called:
   - Uses `renderer.draw_text_direct()` for each line
   - Renders directly to screen buffer (after bloom and UI)
4. `pygame.display.flip()` swaps buffers

This ensures the FPS display appears on top of all other content and isn't affected by bloom effects.

## Performance Considerations

- **Minimal Overhead**: FPS tracking uses a deque for efficient rolling window
- **Direct Rendering**: FPS text is rendered directly without texture caching
- **Configurable**: Disable metrics you don't need to reduce rendering cost
- **No Impact When Hidden**: When toggled off, only a boolean check is performed

## Testing

Run the test suite to verify FPS display functionality:

```bash
# Test FPS counter logic and integration
python test_fps_counter.py

# Test visual output and configuration
python test_fps_visual.py
```

## Troubleshooting

### FPS display not showing

- Make sure you pressed F3 to toggle it on
- Check that at least one `FPS_DISPLAY_SHOW_*` constant is `True`

### FPS values seem incorrect

- Check that delta time calculation is correct in game loop
- Ensure `clock.tick(FPS)` is being called each frame
- Verify no artificial delays are added to the game loop

### Display position is wrong

- Adjust `FPS_DISPLAY_POSITION_X` and `FPS_DISPLAY_POSITION_Y` in constants
- Coordinates are in screen space (0,0 = top-left)

### Text is cut off

- Move the display position away from screen edges
- Check that `FONT_SIZE_SMALL` is appropriate for your resolution

## Future Enhancements

Possible improvements for the FPS display system:

- Frame time graph visualization
- GPU usage metrics
- Memory usage tracking
- Configurable colors per metric
- Background panel for better readability
- Export performance data to file
- Per-scene performance breakdown
- Detailed frame timing histogram
