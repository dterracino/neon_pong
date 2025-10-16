# Post-Processing Style Effects - Usage Examples

This guide shows how to use the different post-processing style effects.

## Quick Start

Edit `src/utils/constants.py` and change the `POST_EFFECT_TYPE` setting:

```python
# No effect (default)
POST_EFFECT_TYPE = "none"

# Scanlines effect
POST_EFFECT_TYPE = "scanlines"

# CRT monitor effect
POST_EFFECT_TYPE = "crt"

# VHS tape effect
POST_EFFECT_TYPE = "vhs"
```

Then run the game:
```bash
python main.py
```

## Effect Comparison

### None (Default)
```python
POST_EFFECT_TYPE = "none"
```
- Clean, modern look
- Just bloom post-processing
- Best for maximum clarity
- Recommended for competitive play

### Scanlines
```python
POST_EFFECT_TYPE = "scanlines"
```
- Horizontal line pattern across screen
- Subtle retro feel
- Minimal performance impact
- Good balance between clarity and style

### CRT Monitor
```python
POST_EFFECT_TYPE = "crt"
```
- Screen curvature (barrel distortion)
- Scanlines with phosphor glow
- Vignette (darker edges)
- RGB color separation
- Subtle flicker
- Most authentic retro look
- Slight performance cost

### VHS Tape
```python
POST_EFFECT_TYPE = "vhs"
```
- Horizontal tracking distortion
- Random glitch bands
- Chromatic aberration
- Film grain and noise
- Color bleeding/ghosting
- Degraded colors
- Bottom edge artifacts
- Most "lo-fi" aesthetic
- Moderate performance cost

## Testing Different Effects

### Method 1: Manual Configuration
1. Edit `src/utils/constants.py`
2. Change `POST_EFFECT_TYPE` value
3. Save and run the game
4. Restart to see changes

### Method 2: Visual Test Script
Run the visual test to cycle through all effects:
```bash
python tests/test_style_effects_visual.py
```
- Press SPACE to cycle through effects
- Press ESC to quit

## Performance Notes

All effects run at 60+ FPS on modern hardware:
- **none**: Baseline performance
- **scanlines**: +0.1ms per frame
- **crt**: +0.3ms per frame
- **vhs**: +0.4ms per frame

## Combining with Background Effects

Style effects work with all background types. Try different combinations:

```python
# Starfield background with CRT effect (retro space arcade)
BACKGROUND_TYPE = "starfield"
POST_EFFECT_TYPE = "crt"

# Plasma background with VHS effect (vaporwave aesthetic)
BACKGROUND_TYPE = "plasma"
POST_EFFECT_TYPE = "vhs"

# Waves background with scanlines (classic arcade)
BACKGROUND_TYPE = "waves"
POST_EFFECT_TYPE = "scanlines"

# Clean modern look
BACKGROUND_TYPE = "starfield"
POST_EFFECT_TYPE = "none"
```

## Troubleshooting

### Effect not visible
- Check that `POST_EFFECT_TYPE` is spelled correctly in constants.py
- Verify the value is one of: "none", "scanlines", "crt", "vhs"
- Restart the game after changing the constant

### Shader compilation errors
Run the test suite to verify shaders:
```bash
python tests/test_style_effects.py
```

### Performance issues
- Try a simpler effect (scanlines instead of VHS)
- Set `POST_EFFECT_TYPE = "none"` for maximum performance
- Reduce bloom blur passes in constants.py

## Technical Details

See [POST_PROCESSING_EFFECTS.md](POST_PROCESSING_EFFECTS.md) for:
- Detailed effect descriptions
- Architecture documentation
- How to create custom effects
- Shader uniform specifications
