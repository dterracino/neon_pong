# Screenshot Feature

## Overview

Neon Pong includes built-in screenshot functionality to capture the game screen at any time.

## Usage

Press **Ctrl-S** at any time during gameplay to capture a screenshot.

Screenshots are automatically saved to the `screenshots/` directory in the project root with a timestamp-based filename format:

```
screenshot_YYYYMMDD_HHMMSS_microseconds.png
```

For example: `screenshot_20251016_143022_547809.png`

## Features

- **Instant Capture**: Press Ctrl-S to immediately save the current game screen
- **Automatic Naming**: Screenshots are automatically named with timestamps for easy organization
- **Unique Filenames**: Microsecond precision ensures no filename collisions
- **PNG Format**: Screenshots are saved as high-quality PNG images
- **Auto-Directory Creation**: The `screenshots/` directory is created automatically if it doesn't exist

## Examples

While playing:
1. Press **Ctrl-S** to capture the current frame
2. Check the console for a confirmation message: `Screenshot saved to: screenshots/screenshot_....png`
3. Find your screenshot in the `screenshots/` directory

## Technical Details

The screenshot feature uses:
- `pygame.image.save()` for screen capture
- Python's `datetime` module for timestamp generation
- Automatic directory creation with `os.makedirs()`

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
