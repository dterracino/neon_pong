"""Test to inspect paddle sprite pixel data"""
import pygame
import sys
import os

# Initialize pygame
pygame.init()
pygame.display.set_mode((1, 1))  # Minimal display for image operations

# Load the paddle sprite
sprite_path = os.path.join('assets', 'images', 'paddle1.png')
sprite = pygame.image.load(sprite_path).convert_alpha()

print(f"Sprite size: {sprite.get_size()}")
print(f"Sprite format: {sprite.get_bitsize()} bits per pixel")

# Check a few pixels across the height
width, height = sprite.get_size()
print(f"\nPixel samples (x=10, varying y):")
for y in [0, 20, 40, 60, 80, 99]:
    pixel = sprite.get_at((10, y))
    print(f"  y={y:2d}: RGBA{pixel}")

# Check if all pixels are the same
print(f"\nChecking if all pixels are uniform...")
first_pixel = sprite.get_at((0, 0))
all_same = True
for y in range(height):
    for x in range(width):
        if sprite.get_at((x, y)) != first_pixel:
            print(f"  Difference found at ({x}, {y}): {sprite.get_at((x, y))} vs {first_pixel}")
            all_same = False
            break
    if not all_same:
        break

if all_same:
    print(f"  All pixels are identical: {first_pixel}")
