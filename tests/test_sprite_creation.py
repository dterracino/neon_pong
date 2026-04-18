"""
Test script to generate simple test sprites and verify sprite loading
"""
import os
import sys
import pygame

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def create_test_sprites():
    """Create simple test sprites for paddles and ball"""
    pygame.init()
    
    # Ensure images directory exists
    images_dir = os.path.join('assets', 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Create paddle sprites (20x100 pixels)
    print("Creating paddle sprites...")
    
    # Player 1 paddle (cyan)
    paddle1 = pygame.Surface((20, 100), pygame.SRCALPHA)
    # Add a gradient effect for visual interest
    for y in range(100):
        intensity = 1.0 - (y / 100.0) * 0.3  # Brightest at top
        color = (int(0 * intensity), int(205 * intensity), int(254 * intensity), 255)
        pygame.draw.line(paddle1, color, (0, y), (20, y))
    # Add bright edge highlights
    pygame.draw.line(paddle1, (100, 255, 255, 255), (0, 0), (0, 100), 2)  # Left edge
    pygame.draw.line(paddle1, (100, 255, 255, 255), (19, 0), (19, 100), 2)  # Right edge
    
    paddle1_path = os.path.join(images_dir, 'paddle1.png')
    pygame.image.save(paddle1, paddle1_path)
    print(f"  Created: {paddle1_path}")
    
    # Player 2 paddle (pink/magenta)
    paddle2 = pygame.Surface((20, 100), pygame.SRCALPHA)
    for y in range(100):
        intensity = 1.0 - (y / 100.0) * 0.3
        color = (int(255 * intensity), int(112 * intensity), int(206 * intensity), 255)
        pygame.draw.line(paddle2, color, (0, y), (20, y))
    # Add bright edge highlights
    pygame.draw.line(paddle2, (255, 150, 255, 255), (0, 0), (0, 100), 2)  # Left edge
    pygame.draw.line(paddle2, (255, 150, 255, 255), (19, 0), (19, 100), 2)  # Right edge
    
    paddle2_path = os.path.join(images_dir, 'paddle2.png')
    pygame.image.save(paddle2, paddle2_path)
    print(f"  Created: {paddle2_path}")
    
    # Create ball sprite (20x20 pixels)
    print("Creating ball sprite...")
    ball = pygame.Surface((20, 20), pygame.SRCALPHA)
    
    # Draw a glowing circle effect
    # Outer glow
    pygame.draw.circle(ball, (255, 234, 0, 100), (10, 10), 10)
    # Mid layer
    pygame.draw.circle(ball, (255, 244, 100, 200), (10, 10), 7)
    # Core
    pygame.draw.circle(ball, (255, 255, 200, 255), (10, 10), 4)
    # Highlight
    pygame.draw.circle(ball, (255, 255, 255, 255), (8, 8), 2)
    
    ball_path = os.path.join(images_dir, 'ball.png')
    pygame.image.save(ball, ball_path)
    print(f"  Created: {ball_path}")
    
    print("\nTest sprites created successfully!")
    print(f"\nSprites are located in: {images_dir}")
    print("\nTo test in-game:")
    print("1. The sprites will be automatically loaded if present")
    print("2. Run the game normally: python main.py")
    print("3. The game will use sprites if found, or fall back to procedural rendering")
    
    pygame.quit()

def test_sprite_loading():
    """Test that AssetManager can load the sprites"""
    print("\nTesting sprite loading...")
    
    # Initialize pygame (required for image loading)
    pygame.init()
    
    from src.managers.asset_manager import AssetManager
    
    asset_manager = AssetManager()
    count = asset_manager.preload_images()
    
    print(f"Loaded {count} images")
    
    # Try to get specific sprites
    paddle1 = asset_manager.get_image('paddle1')
    paddle2 = asset_manager.get_image('paddle2')
    ball = asset_manager.get_image('ball')
    
    if paddle1:
        print(f"  ✓ paddle1.png loaded ({paddle1.get_width()}x{paddle1.get_height()})")
    else:
        print("  ✗ paddle1.png not found")
    
    if paddle2:
        print(f"  ✓ paddle2.png loaded ({paddle2.get_width()}x{paddle2.get_height()})")
    else:
        print("  ✗ paddle2.png not found")
    
    if ball:
        print(f"  ✓ ball.png loaded ({ball.get_width()}x{ball.get_height()})")
    else:
        print("  ✗ ball.png not found")
    
    pygame.quit()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test-only':
        test_sprite_loading()
    else:
        create_test_sprites()
        test_sprite_loading()
