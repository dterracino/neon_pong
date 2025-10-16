#!/usr/bin/env python3
"""
Background Shader Demo Application
Interactive viewer for all background shaders in the Neon Pong game
Use number keys 1-4 to switch between different shaders
"""
import os
import sys
import pygame
import moderngl

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.managers.shader_manager import ShaderManager
import numpy as np

# Shader configurations
SHADERS = {
    'starfield': {
        'name': 'Starfield',
        'vertex': 'basic.vert',
        'fragment': 'background_starfield.frag',
        'key': pygame.K_1,
        'description': 'Parallax starfield with twinkling stars'
    },
    'plasma': {
        'name': 'Plasma',
        'vertex': 'basic.vert',
        'fragment': 'background_plasma.frag',
        'key': pygame.K_2,
        'description': 'Flowing plasma effect with neon colors'
    },
    'waves': {
        'name': 'Waves',
        'vertex': 'basic.vert',
        'fragment': 'background_waves.frag',
        'key': pygame.K_3,
        'description': 'Animated wave patterns with retro grid'
    },
    'retrowave': {
        'name': 'Retrowave',
        'vertex': 'basic.vert',
        'fragment': 'background_retrowave.frag',
        'key': pygame.K_4,
        'description': 'Classic synthwave with mountains, sun, and grid'
    }
}

class BackgroundShaderDemo:
    """Interactive demo application for background shaders"""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Neon Pong - Background Shader Demo")
        
        # Create ModernGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Create shader manager
        self.shader_manager = ShaderManager(self.ctx)
        
        # Load all shaders
        self.loaded_shaders = {}
        self.current_shader = None
        self.current_shader_name = None
        
        print("=" * 80)
        print("NEON PONG - BACKGROUND SHADER DEMO")
        print("=" * 80)
        print("\nLoading shaders...")
        
        for shader_id, config in SHADERS.items():
            print(f"  Loading {config['name']}...", end=" ")
            shader_program = self.shader_manager.load_shader(
                shader_id, config['vertex'], config['fragment']
            )
            if shader_program:
                self.loaded_shaders[shader_id] = {
                    'program': shader_program,
                    'config': config
                }
                print("✓")
            else:
                print(f"✗ Failed!")
        
        # Create fullscreen quad
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        
        self.quad_vbo = self.ctx.buffer(vertices.tobytes())
        
        # Create VAOs for each shader
        self.vaos = {}
        for shader_id, shader_data in self.loaded_shaders.items():
            self.vaos[shader_id] = self.ctx.simple_vertex_array(
                shader_data['program'], self.quad_vbo, 'in_position'
            )
        
        # Set initial shader (starfield)
        self.switch_shader('starfield')
        
        print("\n" + "=" * 80)
        print("CONTROLS:")
        print("  1 - Starfield")
        print("  2 - Plasma")
        print("  3 - Waves")
        print("  4 - Retrowave")
        print("  H - Show current shader info")
        print("  ESC - Exit")
        print("=" * 80 + "\n")
    
    def switch_shader(self, shader_id):
        """Switch to a different shader"""
        if shader_id in self.loaded_shaders:
            self.current_shader = self.loaded_shaders[shader_id]['program']
            self.current_shader_name = shader_id
            config = self.loaded_shaders[shader_id]['config']
            print(f"\n→ Switched to: {config['name']}")
            print(f"  {config['description']}")
    
    def run(self):
        """Main demo loop"""
        clock = pygame.time.Clock()
        time = 0.0
        running = True
        
        # Print current shader info
        self.print_current_shader_info()
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_h:
                        self.print_current_shader_info()
                    else:
                        # Check if it's a shader switch key
                        for shader_id, shader_data in self.loaded_shaders.items():
                            if event.key == shader_data['config']['key']:
                                self.switch_shader(shader_id)
                                break
            
            # Update time
            dt = clock.tick(60) / 1000.0
            time += dt
            
            # Clear screen
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            
            # Render current shader
            if self.current_shader and self.current_shader_name:
                self.current_shader['time'] = time
                self.current_shader['resolution'] = (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
                self.vaos[self.current_shader_name].render(moderngl.TRIANGLE_STRIP)
            
            # Swap buffers
            pygame.display.flip()
        
        pygame.quit()
        print("\nDemo closed. Thank you!")
    
    def print_current_shader_info(self):
        """Print current shader information to console"""
        config = self.loaded_shaders[self.current_shader_name]['config']
        print("\n" + "=" * 80)
        print(f"CURRENT SHADER: {config['name']}")
        print(f"Description: {config['description']}")
        print("=" * 80)
    
    def render_help_overlay(self):
        """Render help text overlay using pygame's 2D rendering"""
        # Removed - using console output instead for simplicity
        pass

def main():
    """Entry point for the demo application"""
    try:
        demo = BackgroundShaderDemo()
        demo.run()
        return 0
    except Exception as e:
        print(f"\n✗ Error running demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
