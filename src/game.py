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
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Create window with OpenGL context
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE
        )
        
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Create ModernGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Initialize managers (singleton pattern)
        self.asset_manager = AssetManager()
        self.shader_manager = ShaderManager(self.ctx)
        self.audio_manager = AudioManager(self.asset_manager)
        
        # Initialize renderer
        self.renderer = Renderer(self.ctx, self.shader_manager)
        
        # Initialize scene manager
        self.scene_manager = SceneManager()
        
        # Start with menu scene
        initial_scene = MenuScene(self.scene_manager, self.renderer, self.audio_manager)
        self.scene_manager.push_scene(initial_scene)
        
        # Game loop variables
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time
            self.dt = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            self._handle_events()
            
            # Update current scene
            if self.scene_manager.current_scene:
                self.scene_manager.current_scene.update(self.dt)
            
            # Render current scene
            if self.scene_manager.current_scene:
                self.scene_manager.current_scene.render()
                
            # Swap buffers
            pygame.display.flip()
            
            # Check if we should quit
            if not self.scene_manager.current_scene:
                self.running = False
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.scene_manager.current_scene:
                self.scene_manager.current_scene.handle_event(event)