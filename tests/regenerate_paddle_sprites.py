"""Regenerate paddle sprites as solid colors without gradients"""
import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1))

# Paddle dimensions
WIDTH = 20
HEIGHT = 100

# Create paddle 1 (cyan - solid color)
paddle1 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
paddle1.fill((0, 204, 254, 255))  # Solid cyan

# Create paddle 2 (pink - solid color)  
paddle2 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
paddle2.fill((255, 113, 206, 255))  # Solid pink

# Save
os.makedirs('assets/images', exist_ok=True)
pygame.image.save(paddle1, 'assets/images/paddle1.png')
pygame.image.save(paddle2, 'assets/images/paddle2.png')

print("✓ Generated solid paddle sprites (20x100)")
print("  paddle1.png: Solid cyan RGB(0, 204, 254)")
print("  paddle2.png: Solid pink RGB(255, 113, 206)")
