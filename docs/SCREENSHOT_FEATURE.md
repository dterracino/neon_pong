# Screenshot Feature

## Overview

Neon Pong includes built-in screenshot functionality to capture the game screen at any time, with an enhanced blurred background effect on the pause screen.

## Usage

Press **Ctrl-S** at any time during gameplay to capture a screenshot.

Screenshots are automatically saved to the `screenshots/` directory in the project root with a timestamp-based filename format:

```
screenshot_YYYYMMDD_HHMMSS_microseconds.png
```

For example: `screenshot_20251016_143022_547809.png`

## Features

### Screenshot Capture
- **Instant Capture**: Press Ctrl-S to immediately save the current game screen
- **Post-Render Timing**: Screenshots are captured AFTER all rendering completes, ensuring post-processing and overlays are included
- **Automatic Naming**: Screenshots are automatically named with timestamps for easy organization
- **Unique Filenames**: Microsecond precision ensures no filename collisions
- **PNG Format**: Screenshots are saved as high-quality PNG images
- **Auto-Directory Creation**: The `screenshots/` directory is created automatically if it doesn't exist

### Blurred Pause Screen
- **Dynamic Background**: Pause screen shows a blurred version of the current game state
- **Gaussian Blur**: Uses multi-pass blur shader for smooth, professional effect
- **Optimized Performance**: Blur is applied once when pausing (not every frame)
- **Enhanced Readability**: Background is darkened to 50% for better text visibility
- **Automatic Capture**: Game continuously captures frames to memory for instant pause background

## Examples

While playing:
1. Press **Ctrl-S** to capture the current frame
2. Check the console for a confirmation message: `Screenshot saved to: screenshots/screenshot_....png`
3. Find your screenshot in the `screenshots/` directory

Pause screen:
1. Press **ESC** or **P** to pause the game
2. See a beautifully blurred version of the game in the background
3. The blur updates each time you pause to show the current game state

## Technical Details

### Screenshot Capture
The screenshot feature uses:
- `ctx.screen.read()` to read from the OpenGL framebuffer (ModernGL)
- `pygame.image.frombuffer()` to convert OpenGL pixel data to pygame surface
- `pygame.image.save()` to save the surface to disk
- Python's `datetime` module for timestamp generation
- Automatic directory creation with `os.makedirs()`
- Deferred capture mechanism to ensure all rendering is complete

**Important**: Since the game uses OpenGL rendering through ModernGL, screenshots are captured directly from the OpenGL framebuffer using `ctx.screen.read()` rather than from the pygame surface. This ensures that all OpenGL-rendered content (including post-processing effects, bloom, and shaders) is correctly captured.

### Capture Timing
Screenshots are captured in the following sequence:
1. User presses Ctrl-S (sets capture flag)
2. Frame renders completely to OpenGL framebuffer (scene + overlays)
3. `pygame.display.flip()` swaps buffers
4. Screenshot is captured from the OpenGL framebuffer using `ctx.screen.read()`
5. Pixel data is converted from OpenGL format (bottom-left origin) to pygame format (top-left origin)
6. Image is saved to disk

This ensures that all post-processing effects, bloom, and UI overlays are included in the screenshot. The timing after `flip()` is critical to ensure the OpenGL rendering pipeline has completed.

### Blur Effect
The pause screen blur uses:
- Existing Gaussian blur shader (`bloom_blur.frag`)
- 3-pass blur (horizontal → vertical → horizontal)
- In-memory frame capture from OpenGL framebuffer (~1-2ms overhead per frame)
- ModernGL texture creation and shader processing
- One-time blur computation when pause is triggered

### Performance Impact
- **In-memory capture**: ~1-2ms per frame (reads from OpenGL framebuffer)
- **Screenshot save**: Only when Ctrl-S is pressed (~10-50ms depending on disk speed)
- **Blur generation**: One-time on pause (~5-10ms)
- **Memory usage**: One screenshot surface (~5MB for 1280x720 resolution)

The `ScreenshotManager` class handles all screenshot operations and can be found in `src/utils/screenshot.py`.

## Troubleshooting

**Screenshot not saving?**
- Check console output for error messages
- Ensure you have write permissions in the project directory
- Verify pygame is properly initialized

**Can't find screenshots?**
- Look in the `screenshots/` directory relative to where you run `python main.py`
- Screenshots are not committed to git (they're in `.gitignore`)

## Testing

You can test the screenshot functionality with:

```bash
# Run the unit test (no OpenGL required)
python tests/test_screenshot_unit.py

# Run the visual test (requires display/OpenGL)
python tests/test_screenshot.py
```
