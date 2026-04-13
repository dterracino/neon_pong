"""
Game constants and configuration
"""
import logging

# Logging settings
LOG_LEVEL = logging.DEBUG  # Change to logging.INFO to reduce verbosity

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Neon Pong"

# Game settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 400
PADDLE_OFFSET = 50

BALL_SIZE = 15
BALL_SPEED_INITIAL = 400
BALL_SPEED_INCREMENT = 20
BALL_MAX_SPEED = 800

WINNING_SCORE = 10

# Neon-Vaporwave colors (RGB normalized to 0-1)
COLOR_PINK = (1.0, 0.44, 0.81, 1.0)      # #FF71CE
COLOR_CYAN = (0.0, 0.8, 0.996, 1.0)      # #01CDFE
COLOR_PURPLE = (0.725, 0.4, 1.0, 1.0)    # #B967FF
COLOR_YELLOW = (0.992, 1.0, 0.42, 1.0)   # #FDFF6A
COLOR_MINT = (0.02, 1.0, 0.63, 1.0)      # #05FFA1
COLOR_DARK_BG = (0.05, 0.02, 0.15, 1.0)  # Dark purple background

# Bloom settings
BLOOM_THRESHOLD = 0.7
BLOOM_INTENSITY = 1.5
BLOOM_BLUR_PASSES = 2

# Particle settings
PARTICLE_COUNT = 10
PARTICLE_LIFETIME = 0.5
PARTICLE_SPEED = 100

# Audio settings
MUSIC_VOLUME = 0.3
SFX_VOLUME = 0.5

# Font sizes
FONT_SIZE_LARGE = 72   # For titles and big messages
FONT_SIZE_MEDIUM = 48  # For menu options
FONT_SIZE_DEFAULT = 32 # Default text size
FONT_SIZE_SMALL = 24   # For small text like controls

# AI Difficulty Settings
AI_DIFFICULTIES = {
    'easy': {
        'reaction_time': 0.3,        # Delay before reacting (seconds)
        'speed_multiplier': 0.6,     # Move at 60% of max speed
        'prediction_error': 80,      # Pixels of random error in prediction
        'update_frequency': 0.2,     # How often AI recalculates target (seconds)
        'dead_zone': 20,             # Don't move if within this many pixels of target
        'adaptive': False,           # Don't adjust difficulty based on score
        'spin_factor': 0.0,          # No spin influence
    },
    'normal': {
        'reaction_time': 0.15,       # Faster reaction
        'speed_multiplier': 0.8,     # Move at 80% of max speed
        'prediction_error': 40,      # Less error in prediction
        'update_frequency': 0.1,     # Update more frequently
        'dead_zone': 15,             # Smaller dead zone
        'adaptive': False,           # Don't adjust difficulty
        'spin_factor': 0.25,         # Same spin as human player
    },
    'hard': {
        'reaction_time': 0.05,       # Very fast reaction
        'speed_multiplier': 1.0,     # Full speed
        'prediction_error': 15,      # Minimal error
        'update_frequency': 0.05,    # Update very frequently
        'dead_zone': 10,             # Very small dead zone
        'adaptive': True,            # Adjust difficulty based on score
        'spin_factor': 0.5,          # Double spin influence
    },
}

# Background settings
BACKGROUND_TYPE = "starfield"  # Options: "starfield", "plasma", "waves", "retrowave", "retro", "solid"

# Post-processing style effect settings
POST_EFFECT_TYPE = "none"  # Options: "none", "scanlines", "crt", "vhs"

# FPS Display settings
FPS_DISPLAY_SHOW_INSTANT = True     # Show instant frame rate
FPS_DISPLAY_SHOW_AVERAGE = True     # Show average frame rate
FPS_DISPLAY_SHOW_1_PERCENT = True   # Show 1% low
FPS_DISPLAY_SHOW_0_1_PERCENT = True # Show 0.1% low
FPS_DISPLAY_AVERAGE_WINDOW = 1.0    # Window size for average calculation (seconds)
FPS_DISPLAY_POSITION_X = 10         # X position for FPS display
FPS_DISPLAY_POSITION_Y = 10         # Y position for FPS display