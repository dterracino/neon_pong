"""
Help screen scene
"""
import logging
import pygame
import moderngl
from typing import Optional
from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.managers.audio_manager import AudioManager
from src.utils.screenshot import ScreenshotManager
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_PINK, COLOR_CYAN, COLOR_YELLOW, COLOR_MINT,
    FONT_SIZE_LARGE, FONT_SIZE_DEFAULT, FONT_SIZE_SMALL
)

logger = logging.getLogger(__name__)

# Key binding sections: (heading_color, heading, [(key, description), ...])
HELP_SECTIONS = [
    (COLOR_CYAN, "GAMEPLAY", [
        ("W / S",           "Player 1 — move up / down"),
        ("UP / DOWN",       "Player 2 — move up / down"),
        ("ESC  or  P",      "Pause / Resume"),
    ]),
    (COLOR_PINK, "AUDIO", [
        ("M",               "Toggle music on / off"),
        ("N",               "Toggle sound effects on / off"),
        ("[  /  ]",         "Music volume down / up"),
        (";  /  '",         "SFX volume down / up"),
    ]),
    (COLOR_MINT, "DISPLAY", [
        ("F1",              "Help screen (this screen)"),
        ("F3",              "Toggle FPS counter"),
        ("=",               "Toggle scanlines"),
        ("Ctrl + S",        "Save screenshot"),
    ]),
]


class HelpScene(Scene):
    """Help / key-bindings overlay"""

    def __init__(self, scene_manager, renderer: Renderer, audio_manager: AudioManager,
                 screenshot_manager: Optional[ScreenshotManager] = None):
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.screenshot_manager = screenshot_manager

        # Blurred background texture
        self.blur_texture: Optional[moderngl.Texture] = None
        self.blur_fbo: Optional[moderngl.Framebuffer] = None

        self._create_blurred_background()

    # ------------------------------------------------------------------
    # Blur helpers (shared pattern with PauseScene)
    # ------------------------------------------------------------------

    def _create_blurred_background(self):
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

            blur_program = self.renderer.shader_manager.load_shader('blur', 'basic.vert', 'bloom_blur.frag')
            if not blur_program:
                logger.warning("Could not load blur shader for help screen")
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
                blur_program['tex'] = 0
                blur_program['horizontal'] = False
                blur_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
                self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)

            source_texture.release()
            temp_texture.release()
            temp_fbo.release()
            logger.debug("Help screen blurred background created")
        except Exception as e:
            logger.error("Failed to create blurred background for help screen: %s", e)

    # ------------------------------------------------------------------
    # Scene lifecycle
    # ------------------------------------------------------------------

    def on_enter(self):
        self.audio_manager.duck_music(0.5)

    def on_exit(self):
        self.audio_manager.unduck_music()
        if self.blur_texture:
            self.blur_texture.release()
            self.blur_texture = None
        if self.blur_fbo:
            self.blur_fbo.release()
            self.blur_fbo = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_F1, pygame.K_ESCAPE):
                self.scene_manager.pop_scene()

    def update(self, dt: float):
        pass

    def render(self):
        self.renderer.begin_frame()

        # Draw blurred + darkened background
        if self.blur_texture:
            ctx = self.renderer.ctx
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            self.blur_texture.use(0)
            self.renderer.basic_program['tex'] = 0
            self.renderer.basic_program['color'] = (0.4, 0.4, 0.4, 1.0)
            self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)
            ctx.disable(moderngl.BLEND)

        # Panel constants
        PAD = 20
        RADIUS = 16
        px, py = PAD, PAD
        pw, ph = WINDOW_WIDTH - 2 * PAD, WINDOW_HEIGHT - 2 * PAD

        # Outer border glow (slightly larger, neon cyan at low alpha)
        ctx = self.renderer.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        border = 3
        self.renderer.draw_rounded_rect(px - border, py - border,
                                        pw + 2 * border, ph + 2 * border,
                                        RADIUS + border, (*COLOR_CYAN[:3], 0.45))
        # Filled dark panel
        self.renderer.draw_rounded_rect(px, py, pw, ph, RADIUS,
                                        (0.04, 0.01, 0.12, 0.88))
        ctx.disable(moderngl.BLEND)

        # Title
        self.renderer.draw_text(
            "HELP  —  KEY BINDINGS",
            WINDOW_WIDTH // 2, 40,
            FONT_SIZE_DEFAULT, COLOR_YELLOW, font_name="sys:calibri", centered=True
        )

        # Layout: three columns across the screen
        col_xs = [WINDOW_WIDTH // 6, WINDOW_WIDTH // 2, WINDOW_WIDTH * 5 // 6]
        section_y_start = 110

        for col_idx, (heading_color, heading, bindings) in enumerate(HELP_SECTIONS):
            x = col_xs[col_idx]
            y = section_y_start

            # Section heading
            self.renderer.draw_text(heading, x, y, FONT_SIZE_DEFAULT, heading_color, font_name="sys:calibri", centered=True)
            y += FONT_SIZE_DEFAULT + 12

            # Divider line (drawn as a thin rect)
            self.renderer.draw_rect(x - 160, y, 320, 2, (*heading_color[:3], 0.5))
            y += 14

            # Key / description pairs
            for key, desc in bindings:
                self.renderer.draw_text(
                    key, x - 10, y, FONT_SIZE_SMALL, COLOR_YELLOW, font_name="sys:calibri", centered=True
                )
                y += FONT_SIZE_SMALL + 4
                self.renderer.draw_text(
                    desc, x, y, FONT_SIZE_SMALL, COLOR_CYAN, font_name="sys:calibri", centered=True
                )
                y += FONT_SIZE_SMALL + 16

        # Footer
        self.renderer.draw_text(
            "Press  F1  or  ESC  to close",
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40,
            FONT_SIZE_SMALL, COLOR_MINT, font_name="sys:calibri", centered=True
        )

        self.renderer.end_frame()
