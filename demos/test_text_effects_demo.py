#!/usr/bin/env python3
"""
Visual demonstration of text effects.
Shows various text rendering effects side-by-side.
"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import moderngl
from src.managers.shader_manager import ShaderManager
from src.rendering.renderer import Renderer, TextEffects
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_PINK, COLOR_CYAN, COLOR_YELLOW, COLOR_PURPLE, COLOR_MINT
)


def main():
    """Demonstrate text effects"""
    print("Initializing text effects demo...")
    pygame.init()
    
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )
    
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.OPENGL | pygame.DOUBLEBUF
    )
    pygame.display.set_caption("Neon Pong - Text Effects Demo")
    
    ctx = moderngl.create_context()
    shader_manager = ShaderManager(ctx)
    renderer = Renderer(ctx, shader_manager)
    
    clock = pygame.time.Clock()
    running = True
    
    print("\nText Effects Demo")
    print("="*60)
    print("This demo shows various text rendering effects:")
    print("  • Basic text (no effects)")
    print("  • Stroke effect")
    print("  • Drop shadow")
    print("  • Gradient overlay")
    print("  • Combined effects")
    print("  • Bloom effect")
    print("\nPress ESC to exit")
    print("="*60)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Render frame
        renderer.update_time(1.0 / 60.0)
        renderer.begin_frame()
        
        # Title
        renderer.draw_text("TEXT EFFECTS DEMONSTRATION", WINDOW_WIDTH // 2, 30,
                          48, COLOR_PINK, centered=True)
        
        y = 100
        spacing = 65
        
        # 1. Basic text
        renderer.draw_text("1. Basic Text (no effects)", 50, y, 40, COLOR_CYAN)
        
        # 2. Stroke effect
        y += spacing
        stroke_effects = TextEffects(
            stroke_width=2.5,
            stroke_color=(0.0, 0.0, 0.0, 1.0)
        )
        renderer.draw_text("2. Stroke Effect", 50, y, 40, COLOR_YELLOW,
                          effects=stroke_effects)
        
        # 3. Drop shadow
        y += spacing
        shadow_effects = TextEffects(
            shadow_offset=(2.0, 2.0),
            shadow_blur=3.0,
            shadow_color=(0.0, 0.0, 0.0, 0.8)
        )
        renderer.draw_text("3. Drop Shadow", 50, y, 40, COLOR_MINT,
                          effects=shadow_effects)
        
        # 4. Gradient
        y += spacing
        gradient_effects = TextEffects(
            gradient_enabled=True,
            gradient_color_top=COLOR_PINK,
            gradient_color_bottom=COLOR_PURPLE
        )
        renderer.draw_text("4. Gradient Overlay", 50, y, 40, (1.0, 1.0, 1.0, 1.0),
                          effects=gradient_effects)
        
        # 5. Combined effects
        y += spacing
        combined_effects = TextEffects(
            stroke_width=2.0,
            stroke_color=(0.0, 0.0, 0.0, 1.0),
            shadow_offset=(2.5, 2.5),
            shadow_blur=4.0,
            shadow_color=(0.0, 0.0, 0.0, 0.7)
        )
        renderer.draw_text("5. Stroke + Shadow", 50, y, 40, COLOR_YELLOW,
                          effects=combined_effects)
        
        # 6. With bloom (rendered to scene)
        y += spacing
        renderer.draw_text("6. With Bloom Glow", 50, y, 40, COLOR_CYAN,
                          render_before_bloom=True)
        
        # 7. All effects + bloom
        y += spacing
        all_effects = TextEffects(
            stroke_width=2.0,
            stroke_color=(0.0, 0.0, 0.0, 1.0),
            shadow_offset=(2.0, 2.0),
            shadow_blur=3.0,
            shadow_color=(0.0, 0.0, 0.0, 0.6),
            gradient_enabled=True,
            gradient_color_top=COLOR_YELLOW,
            gradient_color_bottom=COLOR_PINK
        )
        renderer.draw_text("7. All Effects + Bloom", 50, y, 40, (1.0, 1.0, 1.0, 1.0),
                          effects=all_effects, render_before_bloom=True)
        
        # Info text
        renderer.draw_text("Press ESC to exit", WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30,
                          24, (0.7, 0.7, 0.7, 1.0), centered=True)
        
        renderer.end_frame()
        
        pygame.display.flip()
        clock.tick(60)
    
    # Print cache statistics
    stats = renderer.get_text_cache_stats()
    print("\nCache Statistics:")
    print(f"  Surface cache: {stats['surface_cache_size']} items")
    print(f"  Total accesses: {stats['total_accesses']}")
    
    pygame.quit()
    print("\nDemo completed.")


if __name__ == "__main__":
    main()
