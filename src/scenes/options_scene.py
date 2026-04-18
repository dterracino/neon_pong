"""
Options menu scene (opened with F4).

Allows configuration of game settings including:
- AI Difficulty
- Background shader
- Post-processing effects
- Music and SFX volumes
- FPS display toggle
- Bloom settings

Navigate with UP/DOWN arrows, change values with LEFT/RIGHT arrows.
Press ESC to close and save settings.
"""
import logging
import pygame
import moderngl
from typing import Optional, List, Tuple, Any

from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.managers.audio_manager import AudioManager
from src.managers.options_manager import OptionsManager
from src.utils.screenshot import ScreenshotManager
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_CYAN, COLOR_PINK, COLOR_YELLOW, COLOR_MINT,
    FONT_SIZE_LARGE, FONT_SIZE_DEFAULT, FONT_SIZE_SMALL,
    MUSIC_VOLUME, SFX_VOLUME,
)

logger = logging.getLogger(__name__)

# Font for this scene
SCENE_FONT = "sys:arial bold"

# Available options
BACKGROUND_OPTIONS = [
    "starfield",
    "parallaxstarfield",
    "galaxytrip",
    "plasma",
    "waves",
    "retrowave",
    "retro",
    "solid"
]

POST_EFFECT_OPTIONS = [
    "none",
    "scanlines",
    "crt",
    "vhs"
]

AI_DIFFICULTY_OPTIONS = [
    "easy",
    "normal",
    "hard"
]


class OptionsScene(Scene):
    """Full-screen options menu overlay."""

    def __init__(
        self,
        scene_manager,
        renderer: Renderer,
        audio_manager: AudioManager,
        screenshot_manager: Optional[ScreenshotManager] = None,
        fps_counter = None,
    ):
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.screenshot_manager = screenshot_manager
        self.fps_counter = fps_counter

        # Blur resources
        self.blur_texture: Optional[moderngl.Texture] = None
        self.blur_fbo: Optional[moderngl.Framebuffer] = None

        # Menu state
        self.selected_index = 0
        self.menu_items: List[Tuple[str, str, Any]] = []
        self._init_menu_items()

        self._create_blurred_background()

    def _init_menu_items(self):
        """Initialize menu items with current settings."""
        # Get options manager instance
        self.options_manager = OptionsManager.get_instance()
        
        # Store initial music/sfx states based on volume
        initial_music_enabled = self.audio_manager.music_volume > 0
        initial_sfx_enabled = self.audio_manager.sfx_volume > 0
        
        # Store backup volumes for restoration if currently muted
        self._music_volume_backup = getattr(self.audio_manager, '_music_volume_before_mute', 
                                            self.audio_manager.music_volume if initial_music_enabled else MUSIC_VOLUME)
        self._sfx_volume_backup = getattr(self.audio_manager, '_sfx_volume_before_mute',
                                          self.audio_manager.sfx_volume if initial_sfx_enabled else SFX_VOLUME)
        
        # Read all settings from OptionsManager
        self.settings = {
            'ai_difficulty': self.options_manager.get_ai_difficulty(),
            'background': self.options_manager.get_background(),
            'post_effect': self.options_manager.get_post_effect(),
            'music_enabled': initial_music_enabled,
            'music_volume': self.audio_manager.music_volume if initial_music_enabled else self._music_volume_backup,
            'sfx_enabled': initial_sfx_enabled,
            'sfx_volume': self.audio_manager.sfx_volume if initial_sfx_enabled else self._sfx_volume_backup,
            'fps_display': self.fps_counter.is_visible() if self.fps_counter else False,
            'bloom_threshold': self.options_manager.get_bloom_threshold(),
            'bloom_intensity': self.options_manager.get_bloom_intensity(),
        }

        # Define menu structure: (label, type, key)
        # Types: 'choice', 'toggle', 'slider'
        self.menu_items = [
            ("AI Difficulty", "choice", "ai_difficulty", AI_DIFFICULTY_OPTIONS),
            ("Background", "choice", "background", BACKGROUND_OPTIONS),
            ("Post-Processing", "choice", "post_effect", POST_EFFECT_OPTIONS),
            ("Music", "toggle", "music_enabled", None),
            ("Music Volume", "slider", "music_volume", (0.0, 1.0, 0.05)),
            ("Sound Effects", "toggle", "sfx_enabled", None),
            ("SFX Volume", "slider", "sfx_volume", (0.0, 1.0, 0.05)),
            ("FPS Display", "toggle", "fps_display", None),
            ("Bloom Threshold", "slider", "bloom_threshold", (0.0, 1.0, 0.05)),
            ("Bloom Intensity", "slider", "bloom_intensity", (0.0, 3.0, 0.1)),
        ]

    def _create_blurred_background(self):
        """Create blurred background from last screenshot."""
        if not self.screenshot_manager:
            return
        last_screenshot = self.screenshot_manager.get_last_screenshot()
        if not last_screenshot:
            return
        try:
            ctx = self.renderer.ctx
            screenshot_data = pygame.image.tostring(last_screenshot, 'RGBA', True)

            source_texture = ctx.texture(last_screenshot.get_size(), 4, screenshot_data)
            source_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

            self.blur_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4)
            self.blur_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.blur_fbo = ctx.framebuffer(color_attachments=[self.blur_texture])

            temp_texture = ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4)
            temp_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            temp_fbo = ctx.framebuffer(color_attachments=[temp_texture])

            blur_program = self.renderer.shader_manager.load_shader(
                'blur', 'basic.vert', 'bloom_blur.frag'
            )
            if not blur_program:
                logger.warning("Could not load blur shader for options screen")
                source_texture.release()
                return

            for i in range(3):
                temp_fbo.use()
                ctx.clear(0.0, 0.0, 0.0, 1.0)
                (source_texture if i == 0 else self.blur_texture).use(0)
                blur_program['tex'] = 0
                blur_program['horizontal'] = True
                blur_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
                self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)

                self.blur_fbo.use()
                ctx.clear(0.0, 0.0, 0.0, 1.0)
                temp_texture.use(0)
                blur_program['horizontal'] = False
                self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)

            temp_texture.release()
            temp_fbo.release()
            source_texture.release()

        except Exception as e:
            logger.error("Failed to create blurred background for options: %s", e)

    def on_enter(self):
        self.audio_manager.duck_music()

    def on_exit(self):
        self.audio_manager.unduck_music()
        if self.blur_texture:
            self.blur_texture.release()
            self.blur_texture = None
        if self.blur_fbo:
            self.blur_fbo.release()
            self.blur_fbo = None
        
        # Apply settings on exit
        self._apply_settings()

    def _apply_settings(self):
        """Apply all settings to the game."""
        # Check if we need to reload shaders
        need_background_reload = self.settings['background'] != self.options_manager.get_background()
        need_effect_reload = self.settings['post_effect'] != self.options_manager.get_post_effect()
        need_bloom_update = (
            self.settings['bloom_threshold'] != self.options_manager.get_bloom_threshold() or
            self.settings['bloom_intensity'] != self.options_manager.get_bloom_intensity()
        )
        
        # Update OptionsManager with all settings
        self.options_manager.set_background(self.settings['background'])
        self.options_manager.set_post_effect(self.settings['post_effect'])
        self.options_manager.set_bloom_threshold(self.settings['bloom_threshold'])
        self.options_manager.set_bloom_intensity(self.settings['bloom_intensity'])
        self.options_manager.set_ai_difficulty(self.settings['ai_difficulty'])
        self.options_manager.set_fps_display(self.settings['fps_display'])
        
        # Update constants for backwards compatibility
        from src.utils import constants
        constants.BACKGROUND_TYPE = self.settings['background']
        constants.POST_EFFECT_TYPE = self.settings['post_effect']
        constants.BLOOM_THRESHOLD = self.settings['bloom_threshold']
        constants.BLOOM_INTENSITY = self.settings['bloom_intensity']
        if not hasattr(constants, 'AI_CURRENT_DIFFICULTY'):
            constants.AI_CURRENT_DIFFICULTY = 'normal'
        constants.AI_CURRENT_DIFFICULTY = self.settings['ai_difficulty']
        
        # Update audio settings
        # For music: if enabled in settings, use the volume; if disabled, set to 0
        if self.settings['music_enabled']:
            self.audio_manager.set_music_volume(self.settings['music_volume'])
            self.options_manager.set_music_volume(self.settings['music_volume'])
        else:
            # Store current volume before muting if it's not already stored
            if not hasattr(self.audio_manager, '_music_volume_before_mute'):
                self.audio_manager._music_volume_before_mute = self.settings['music_volume']
            self.audio_manager.set_music_volume(0.0)
            self.options_manager.set_music_volume(0.0)
        
        # For SFX: if enabled in settings, use the volume; if disabled, set to 0
        if self.settings['sfx_enabled']:
            self.audio_manager.set_sfx_volume(self.settings['sfx_volume'])
            self.options_manager.set_sfx_volume(self.settings['sfx_volume'])
        else:
            # Store current volume before muting if it's not already stored
            if not hasattr(self.audio_manager, '_sfx_volume_before_mute'):
                self.audio_manager._sfx_volume_before_mute = self.settings['sfx_volume']
            self.audio_manager.set_sfx_volume(0.0)
            self.options_manager.set_sfx_volume(0.0)
        
        # Update FPS display
        if self.fps_counter:
            current_visible = self.fps_counter.is_visible()
            if self.settings['fps_display'] != current_visible:
                self.fps_counter.toggle_visibility()
        
        # Reload shaders if needed
        if need_background_reload:
            self.renderer.reload_background_shader()
        
        if need_effect_reload:
            self.renderer.post_processor.reload_effect_shader()
        
        # Update bloom settings in post-processor
        if need_bloom_update:
            # The post-processor will read from constants next frame
            logger.debug("Bloom settings updated - will take effect on next frame")
        
        logger.info("Settings applied: %s", self.settings)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.scene_manager.pop_scene()
            
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                self.audio_manager.play_sound('menu_move')
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                self.audio_manager.play_sound('menu_move')
            
            elif event.key == pygame.K_LEFT:
                self._change_value(-1)
                self.audio_manager.play_sound('menu_select')
            
            elif event.key == pygame.K_RIGHT:
                self._change_value(1)
                self.audio_manager.play_sound('menu_select')
            
            elif event.key == pygame.K_RETURN:
                # For toggles, enter also toggles
                item = self.menu_items[self.selected_index]
                if item[1] == 'toggle':
                    self._change_value(1)
                    self.audio_manager.play_sound('menu_select')

    def _change_value(self, direction: int):
        """Change the value of the currently selected option."""
        item = self.menu_items[self.selected_index]
        label, item_type, key, extra = item[0], item[1], item[2], item[3] if len(item) > 3 else None
        
        if item_type == 'choice':
            # Cycle through choices
            options = extra
            current = self.settings[key]
            try:
                current_index = options.index(current)
            except ValueError:
                current_index = 0
            new_index = (current_index + direction) % len(options)
            self.settings[key] = options[new_index]
        
        elif item_type == 'toggle':
            # Toggle boolean
            self.settings[key] = not self.settings[key]
        
        elif item_type == 'slider':
            # Adjust slider value
            min_val, max_val, step = extra
            current = self.settings[key]
            new_value = current + (direction * step)
            self.settings[key] = max(min_val, min(max_val, new_value))

    def update(self, dt: float):
        pass

    def render(self):
        self.renderer.begin_frame()

        ctx = self.renderer.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        # Draw blurred background
        if self.blur_texture and self.blur_fbo:
            self.renderer.scene_fbo.use()
            ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.blur_texture.use(0)
            basic_program = self.renderer.shader_manager.get_program('basic')
            if basic_program:
                basic_program['tex'] = 0
                self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)
        else:
            self.renderer.scene_fbo.use()
            ctx.clear(0.02, 0.01, 0.05, 1.0)

        # Draw semi-transparent panel
        panel_x = WINDOW_WIDTH // 4
        panel_y = 60
        panel_w = WINDOW_WIDTH // 2
        panel_h = WINDOW_HEIGHT - 120
        self.renderer.draw_rect(panel_x, panel_y, panel_w, panel_h, (0.05, 0.02, 0.1, 0.85))

        # Draw panel border
        border_color = COLOR_CYAN
        border_thickness = 3
        self.renderer.draw_rect(panel_x, panel_y, panel_w, border_thickness, border_color)
        self.renderer.draw_rect(panel_x, panel_y + panel_h - border_thickness, panel_w, border_thickness, border_color)
        self.renderer.draw_rect(panel_x, panel_y, border_thickness, panel_h, border_color)
        self.renderer.draw_rect(panel_x + panel_w - border_thickness, panel_y, border_thickness, panel_h, border_color)

        ctx.disable(moderngl.BLEND)

        # Title
        self.renderer.draw_text(
            "OPTIONS",
            WINDOW_WIDTH // 2, 100,
            FONT_SIZE_LARGE, COLOR_YELLOW, font_name=SCENE_FONT, centered=True
        )

        # Draw menu items
        self._draw_menu_items()

        # Instructions
        self.renderer.draw_text(
            "UP/DOWN: Navigate  |  LEFT/RIGHT: Change  |  ESC: Save & Close",
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80,
            FONT_SIZE_SMALL, COLOR_MINT, font_name=SCENE_FONT, centered=True
        )

        self.renderer.end_frame()

    def _draw_menu_items(self):
        """Draw all menu items with current values."""
        start_y = 180
        item_height = 45
        
        for i, item in enumerate(self.menu_items):
            label, item_type, key = item[0], item[1], item[2]
            y = start_y + i * item_height
            
            # Highlight selected item
            is_selected = (i == self.selected_index)
            label_color = COLOR_YELLOW if is_selected else COLOR_CYAN
            value_color = COLOR_PINK if is_selected else (0.8, 0.8, 0.8, 1.0)
            
            # Draw selection indicator
            if is_selected:
                indicator_x = WINDOW_WIDTH // 4 + 30
                self.renderer.draw_text(
                    ">",
                    indicator_x, y,
                    FONT_SIZE_DEFAULT, COLOR_PINK, font_name=SCENE_FONT
                )
            
            # Draw label
            label_x = WINDOW_WIDTH // 4 + 60
            self.renderer.draw_text(
                label,
                label_x, y,
                FONT_SIZE_DEFAULT, label_color, font_name=SCENE_FONT
            )
            
            # Draw value
            value_x = WINDOW_WIDTH // 2 + 60
            value_str = self._format_value(key, item_type)
            self.renderer.draw_text(
                value_str,
                value_x, y,
                FONT_SIZE_DEFAULT, value_color, font_name=SCENE_FONT
            )
            
            # Draw slider bar if applicable
            if item_type == 'slider':
                self._draw_slider(value_x + 120, y, key, item[3])

    def _format_value(self, key: str, item_type: str) -> str:
        """Format the current value for display."""
        value = self.settings[key]
        
        if item_type == 'toggle':
            return "ON" if value else "OFF"
        elif item_type == 'choice':
            return str(value).upper()
        elif item_type == 'slider':
            return f"{value:.2f}"
        return str(value)

    def _draw_slider(self, x: float, y: float, key: str, range_info: Tuple[float, float, float]):
        """Draw a slider bar for the given setting."""
        min_val, max_val, _ = range_info
        current = self.settings[key]
        
        bar_width = 150
        bar_height = 8
        
        # Background bar
        self.renderer.draw_rect(x, y + 4, bar_width, bar_height, (0.2, 0.2, 0.2, 1.0))
        
        # Filled portion
        fill_ratio = (current - min_val) / (max_val - min_val)
        fill_width = int(bar_width * fill_ratio)
        if fill_width > 0:
            self.renderer.draw_rect(x, y + 4, fill_width, bar_height, COLOR_CYAN)
