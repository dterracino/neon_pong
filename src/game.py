"""
Main game class handling initialization and game loop
"""
import pygame
import moderngl
from src.managers.scene_manager import SceneManager
from src.managers.asset_manager import AssetManager
from src.managers.shader_manager import ShaderManager
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.scenes.menu_scene import MenuScene
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE
)


class Game:
    """Main game class"""
    
    def __init__(self):
        """Initialize the game"""
        print("[DEBUG] Game.__init__: Starting game initialization...")
        
        # Initialize Pygame
        print("[DEBUG] Game.__init__: Initializing pygame...")
        pygame.init()
        print("[DEBUG] Game.__init__: Initializing pygame.mixer...")
        try:
            pygame.mixer.init()
            print("[DEBUG] Game.__init__: pygame.mixer initialized successfully")
        except Exception as e:
            print(f"[WARNING] Game.__init__: Failed to initialize pygame.mixer: {e}")
            print("[WARNING] Game.__init__: Continuing without audio...")
        
        # Create window with OpenGL context
        print("[DEBUG] Game.__init__: Setting OpenGL attributes...")
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE
        )
        
        print(f"[DEBUG] Game.__init__: Creating window ({WINDOW_WIDTH}x{WINDOW_HEIGHT})...")
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_caption(WINDOW_TITLE)
        print("[DEBUG] Game.__init__: Window created successfully")
        
        # Create ModernGL context
        print("[DEBUG] Game.__init__: Creating ModernGL context...")
        self.ctx = moderngl.create_context()
        print(f"[DEBUG] Game.__init__: ModernGL context created: {self.ctx}")
        print("[DEBUG] Game.__init__: Enabling blending...")
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Initialize managers (singleton pattern)
        print("[DEBUG] Game.__init__: Initializing asset manager...")
        self.asset_manager = AssetManager()
        print("[DEBUG] Game.__init__: Initializing shader manager...")
        self.shader_manager = ShaderManager(self.ctx)
        print("[DEBUG] Game.__init__: Initializing audio manager...")
        self.audio_manager = AudioManager(self.asset_manager)
        
        # Initialize renderer
        print("[DEBUG] Game.__init__: Initializing renderer...")
        self.renderer = Renderer(self.ctx, self.shader_manager)
        print("[DEBUG] Game.__init__: Renderer initialized successfully")
        
        # Initialize scene manager
        print("[DEBUG] Game.__init__: Initializing scene manager...")
        self.scene_manager = SceneManager()
        
        # Start with menu scene
        print("[DEBUG] Game.__init__: Creating initial menu scene...")
        initial_scene = MenuScene(self.scene_manager, self.renderer, self.audio_manager)
        print("[DEBUG] Game.__init__: Pushing menu scene to scene manager...")
        self.scene_manager.push_scene(initial_scene)
        
        # Game loop variables
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        print("[DEBUG] Game.__init__: Game initialization complete!")
        
    def run(self):
        """Main game loop"""
        print("[DEBUG] Game.run: Starting main game loop...")
        frame_count = 0
        while self.running:
            # Calculate delta time
            self.dt = self.clock.tick(FPS) / 1000.0
            
            if frame_count < 5:  # Only log first 5 frames to avoid spam
                print(f"[DEBUG] Game.run: Frame {frame_count}, dt={self.dt:.4f}")
            
            # Handle events
            self._handle_events()
            
            # Update current scene
            if self.scene_manager.current_scene:
                if frame_count < 5:
                    print(f"[DEBUG] Game.run: Updating scene: {type(self.scene_manager.current_scene).__name__}")
                self.scene_manager.current_scene.update(self.dt)
            
            # Render current scene
            if self.scene_manager.current_scene:
                if frame_count < 5:
                    print(f"[DEBUG] Game.run: Rendering scene: {type(self.scene_manager.current_scene).__name__}")
                self.scene_manager.current_scene.render()
                
            # Swap buffers
            pygame.display.flip()
            
            if frame_count < 5:
                print(f"[DEBUG] Game.run: Frame {frame_count} complete")
            
            frame_count += 1
            
            # Check if we should quit
            if not self.scene_manager.current_scene:
                self.running = False
                print("[DEBUG] Game.run: No current scene, exiting game loop")
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("[DEBUG] Game._handle_events: QUIT event received")
                self.running = False
            elif self.scene_manager.current_scene:
                self.scene_manager.current_scene.handle_event(event)