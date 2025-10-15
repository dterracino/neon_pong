"""
Main game class handling initialization and game loop
"""
import logging
import pygame
import moderngl
from src.managers.scene_manager import SceneManager
from src.managers.asset_manager import AssetManager
from src.managers.shader_manager import ShaderManager
from src.rendering.renderer import Renderer
from src.audio.audio_manager import AudioManager
from src.scenes.menu_scene import MenuScene
from src.utils.fps_counter import FPSCounter
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE,
    FPS_DISPLAY_SHOW_INSTANT, FPS_DISPLAY_SHOW_AVERAGE,
    FPS_DISPLAY_SHOW_1_PERCENT, FPS_DISPLAY_SHOW_0_1_PERCENT,
    FPS_DISPLAY_AVERAGE_WINDOW, FPS_DISPLAY_POSITION_X, FPS_DISPLAY_POSITION_Y,
    FONT_SIZE_SMALL, COLOR_YELLOW
)

logger = logging.getLogger(__name__)


class Game:
    """Main game class"""
    
    def __init__(self):
        """Initialize the game"""
        logger.debug("Starting game initialization")
        
        # Initialize Pygame
        logger.debug("Initializing pygame")
        pygame.init()
        logger.debug("Initializing pygame.mixer")
        try:
            pygame.mixer.init()
            logger.debug("pygame.mixer initialized successfully")
        except Exception as e:
            logger.warning("Failed to initialize pygame.mixer: %s", e)
            logger.warning("Continuing without audio")
        
        # Create window with OpenGL context
        logger.debug("Setting OpenGL attributes")
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE
        )
        # Disable VSync for maximum frame rate
        pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 0)
        
        logger.debug("Creating window (%dx%d)", WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_caption(WINDOW_TITLE)
        logger.debug("Window created successfully")
        
        # Create ModernGL context
        logger.debug("Creating ModernGL context")
        self.ctx = moderngl.create_context()
        logger.debug("ModernGL context created: %s", self.ctx)
        logger.debug("Enabling blending")
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Initialize managers (singleton pattern)
        logger.debug("Initializing asset manager")
        self.asset_manager = AssetManager()
        
        # Preload all assets
        logger.debug("Preloading assets")
        
        def on_assets_loaded(sounds: int, music: int, fonts: int):
            """Called when asset loading completes"""
            logger.info("Asset loading complete: %d sounds, %d music, %d fonts", sounds, music, fonts)
        
        sounds, music, fonts = self.asset_manager.preload_assets(on_complete=on_assets_loaded)
        logger.debug("Assets preloaded successfully")
        
        logger.debug("Initializing shader manager")
        self.shader_manager = ShaderManager(self.ctx)
        logger.debug("Initializing audio manager")
        self.audio_manager = AudioManager(self.asset_manager)
        
        # Initialize renderer
        logger.debug("Initializing renderer")
        self.renderer = Renderer(self.ctx, self.shader_manager)
        logger.debug("Renderer initialized successfully")
        
        # Initialize scene manager
        logger.debug("Initializing scene manager")
        self.scene_manager = SceneManager()
        
        # Start with menu scene
        logger.debug("Creating initial menu scene")
        initial_scene = MenuScene(self.scene_manager, self.renderer, self.audio_manager)
        logger.debug("Pushing menu scene to scene manager")
        self.scene_manager.push_scene(initial_scene)
        
        # Game loop variables
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        # Initialize FPS counter
        logger.debug("Initializing FPS counter")
        self.fps_counter = FPSCounter(average_window=FPS_DISPLAY_AVERAGE_WINDOW)
        logger.debug("FPS counter initialized")
        
        logger.debug("Game initialization complete")
        
    def run(self):
        """Main game loop"""
        logger.debug("Starting main game loop")
        frame_count = 0
        while self.running:
            # Calculate delta time
            self.dt = self.clock.tick(FPS) / 1000.0
            
            # Update FPS counter
            self.fps_counter.update(self.dt)
            
            if frame_count < 5:  # Only log first 5 frames to avoid spam
                logger.debug("Frame %d, dt=%.4f", frame_count, self.dt)
            
            # Handle events
            self._handle_events()
            
            # Update renderer time for animated backgrounds
            self.renderer.update_time(self.dt)
            
            # Update current scene
            if self.scene_manager.current_scene:
                if frame_count < 5:
                    logger.debug("Updating scene: %s", type(self.scene_manager.current_scene).__name__)
                self.scene_manager.current_scene.update(self.dt)
            
            # Render current scene
            if self.scene_manager.current_scene:
                if frame_count < 5:
                    logger.debug("Rendering scene: %s", type(self.scene_manager.current_scene).__name__)
                self.scene_manager.current_scene.render()
            
            # Render FPS display if enabled
            if self.fps_counter.is_visible():
                self._render_fps_display()
                
            # Swap buffers
            pygame.display.flip()
            
            if frame_count < 5:
                logger.debug("Frame %d complete", frame_count)
            
            frame_count += 1
            
            # Check if we should quit
            if not self.scene_manager.current_scene:
                self.running = False
                logger.debug("No current scene, exiting game loop")
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.debug("QUIT event received")
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    # Toggle FPS display
                    self.fps_counter.toggle_visibility()
                    status = "enabled" if self.fps_counter.is_visible() else "disabled"
                    logger.debug("FPS display %s", status)
                elif self.scene_manager.current_scene:
                    self.scene_manager.current_scene.handle_event(event)
            elif self.scene_manager.current_scene:
                self.scene_manager.current_scene.handle_event(event)
    
    def _render_fps_display(self):
        """Render the FPS display overlay directly to screen"""
        instant, average, one_percent, point_one_percent = self.fps_counter.get_metrics()
        
        x = FPS_DISPLAY_POSITION_X
        y = FPS_DISPLAY_POSITION_Y
        line_height = FONT_SIZE_SMALL + 5
        
        # We need to render directly after end_frame() has been called
        # Use the renderer's direct text rendering capability
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Render each metric if enabled in configuration
        lines = []
        if FPS_DISPLAY_SHOW_INSTANT:
            lines.append(f"FPS: {instant:.1f}")
        if FPS_DISPLAY_SHOW_AVERAGE:
            lines.append(f"Avg: {average:.1f}")
        if FPS_DISPLAY_SHOW_1_PERCENT:
            lines.append(f"1% Low: {one_percent:.1f}")
        if FPS_DISPLAY_SHOW_0_1_PERCENT:
            lines.append(f"0.1% Low: {point_one_percent:.1f}")
        
        # Render all lines
        for i, line in enumerate(lines):
            self.renderer.draw_text_direct(
                line, x, y + i * line_height, 
                FONT_SIZE_SMALL, COLOR_YELLOW
            )
        
        self.ctx.disable(moderngl.BLEND)