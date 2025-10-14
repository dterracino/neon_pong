"""
Game constants and configuration
"""

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