"""
Neon Pong - Main entry point
A Pong game with ModernGL shaders and bloom effects
"""
import sys
import logging
import pygame
from src.utils.logging_config import setup_logging
from src.game import Game

# Initialize logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Initialize and run the game"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        logger.exception("Error running game: %s", e)
        sys.exit(1)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()