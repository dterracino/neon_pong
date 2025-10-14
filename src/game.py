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
from src.utils.fps_counter import FPSCounter
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE,
    FPS_DISPLAY_SHOW_INSTANT, FPS_DISPLAY_SHOW_AVERAGE,
    FPS_DISPLAY_SHOW_1_PERCENT, FPS_DISPLAY_SHOW_0_1_PERCENT,
    FPS_DISPLAY_AVERAGE_WINDOW, FPS_DISPLAY_POSITION_X, FPS_DISPLAY_POSITION_Y,
    FONT_SIZE_SMALL, COLOR_YELLOW
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
        
        # Initialize FPS counter
        print("[DEBUG] Game.__init__: Initializing FPS counter...")
        self.fps_counter = FPSCounter(average_window=FPS_DISPLAY_AVERAGE_WINDOW)
        print("[DEBUG] Game.__init__: FPS counter initialized")
        
        print("[DEBUG] Game.__init__: Game initialization complete!")
        
    def run(self):
        """Main game loop"""
        print("[DEBUG] Game.run: Starting main game loop...")
        frame_count = 0
        while self.running:
            # Calculate delta time
            self.dt = self.clock.tick(FPS) / 1000.0
            
            # Update FPS counter
            self.fps_counter.update(self.dt)
            
            if frame_count < 5:  # Only log first 5 frames to avoid spam
                print(f"[DEBUG] Game.run: Frame {frame_count}, dt={self.dt:.4f}")
            
            # Handle events
            self._handle_events()
            
            # Update renderer time for animated backgrounds
            self.renderer.update_time(self.dt)
            
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
            
            # Render FPS display if enabled
            if self.fps_counter.is_visible():
                self._render_fps_display()
                
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    # Toggle FPS display
                    self.fps_counter.toggle_visibility()
                    status = "enabled" if self.fps_counter.is_visible() else "disabled"
                    print(f"[DEBUG] Game._handle_events: FPS display {status}")
                elif self.scene_manager.current_scene:
                    self.scene_manager.current_scene.handle_event(event)
            elif self.scene_manager.current_scene:
                self.scene_manager.current_scene.handle_event(event)
    
    def _render_fps_display(self):
        """Render the FPS display overlay"""
        instant, average, one_percent, point_one_percent = self.fps_counter.get_metrics()
        
        x = FPS_DISPLAY_POSITION_X
        y = FPS_DISPLAY_POSITION_Y
        line_height = FONT_SIZE_SMALL + 5
        
        # Render each metric if enabled in configuration
        if FPS_DISPLAY_SHOW_INSTANT:
            self.renderer.draw_text(
                f"FPS: {instant:.1f}",
                x, y, FONT_SIZE_SMALL, COLOR_YELLOW
            )
            y += line_height
        
        if FPS_DISPLAY_SHOW_AVERAGE:
            self.renderer.draw_text(
                f"Avg: {average:.1f}",
                x, y, FONT_SIZE_SMALL, COLOR_YELLOW
            )
            y += line_height
        
        if FPS_DISPLAY_SHOW_1_PERCENT:
            self.renderer.draw_text(
                f"1% Low: {one_percent:.1f}",
                x, y, FONT_SIZE_SMALL, COLOR_YELLOW
            )
            y += line_height
        
        if FPS_DISPLAY_SHOW_0_1_PERCENT:
            self.renderer.draw_text(
                f"0.1% Low: {point_one_percent:.1f}",
                x, y, FONT_SIZE_SMALL, COLOR_YELLOW
            )