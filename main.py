"""
Neon Pong - Main entry point
A Pong game with ModernGL shaders and bloom effects
"""
import sys
import pygame
from src.game import Game


def main():
    """Initialize and run the game"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()