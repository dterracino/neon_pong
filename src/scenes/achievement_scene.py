"""
Achievement browser scene (opened with F2).

Pattern: same blur-overlay + duck-music as HelpScene / PauseScene.
Dismiss with F2 or ESC.
"""
import logging
import pygame
import moderngl
from typing import Optional

from src.managers.scene_manager import Scene
from src.rendering.renderer import Renderer
from src.managers.audio_manager import AudioManager
from src.managers.achievement_manager import AchievementManager, AchievementType
from src.utils.screenshot import ScreenshotManager
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_CYAN, COLOR_PINK, COLOR_YELLOW, COLOR_MINT,
    FONT_SIZE_LARGE, FONT_SIZE_DEFAULT, FONT_SIZE_SMALL,
)

logger = logging.getLogger(__name__)

# Colours for locked / unlocked entries
_COL_UNLOCKED_NAME = COLOR_YELLOW
_COL_UNLOCKED_DESC = (0.75, 0.75, 0.75, 1.0)
_COL_LOCKED_NAME   = (0.35, 0.35, 0.35, 1.0)
_COL_LOCKED_DESC   = (0.25, 0.25, 0.25, 1.0)
_COL_BAR_BG        = (0.15, 0.15, 0.25, 1.0)
_COL_BAR_FG        = COLOR_CYAN
_COL_HEADER        = COLOR_CYAN


class AchievementScene(Scene):
    """Full-screen achievement browser overlay."""

    def __init__(
        self,
        scene_manager,
        renderer: Renderer,
        audio_manager: AudioManager,
        achievement_manager: AchievementManager,
        screenshot_manager: Optional[ScreenshotManager] = None,
    ):
        super().__init__(scene_manager)
        self.renderer = renderer
        self.audio_manager = audio_manager
        self.achievement_manager = achievement_manager
        self.screenshot_manager = screenshot_manager

        # Blur resources
        self.blur_texture: Optional[moderngl.Texture] = None
        self.blur_fbo: Optional[moderngl.Framebuffer] = None

        self._create_blurred_background()

    # ------------------------------------------------------------------ #
    # Blur (identical pattern to HelpScene)                               #
    # ------------------------------------------------------------------ #

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

            blur_program = self.renderer.shader_manager.load_shader(
                'blur', 'basic.vert', 'bloom_blur.frag'
            )
            if not blur_program:
                logger.warning("Could not load blur shader for achievement screen")
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
            logger.debug("Achievement screen blurred background created")
        except Exception as exc:
            logger.error("Failed to create blurred background for achievement screen: %s", exc)

    # ------------------------------------------------------------------ #
    # Scene lifecycle                                                      #
    # ------------------------------------------------------------------ #

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
            if event.key in (pygame.K_F2, pygame.K_ESCAPE):
                self.scene_manager.pop_scene()

    def update(self, dt: float):
        pass

    # ------------------------------------------------------------------ #
    # Rendering                                                            #
    # ------------------------------------------------------------------ #

    def render(self):
        self.renderer.begin_frame()

        ctx = self.renderer.ctx

        # --- Blurred + darkened background ---
        if self.blur_texture:
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            self.blur_texture.use(0)
            self.renderer.basic_program['tex'] = 0
            self.renderer.basic_program['color'] = (0.4, 0.4, 0.4, 1.0)
            self.renderer.quad_vao.render(moderngl.TRIANGLE_STRIP)
            ctx.disable(moderngl.BLEND)

        # --- Panel ---
        PAD    = 20
        RADIUS = 16
        px, py = PAD, PAD
        pw, ph = WINDOW_WIDTH - 2 * PAD, WINDOW_HEIGHT - 2 * PAD

        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        border = 3
        self.renderer.draw_rounded_rect(
            px - border, py - border,
            pw + 2 * border, ph + 2 * border,
            RADIUS + border, (*COLOR_PINK[:3], 0.45)
        )
        self.renderer.draw_rounded_rect(px, py, pw, ph, RADIUS, (0.04, 0.01, 0.12, 0.88))
        ctx.disable(moderngl.BLEND)

        # --- Title ---
        self.renderer.draw_text(
            "ACHIEVEMENTS",
            WINDOW_WIDTH // 2, 38,
            FONT_SIZE_DEFAULT, COLOR_YELLOW, font_name="sys:calibri", centered=True
        )

        # --- Achievement list ---
        achievements = self.achievement_manager.all_achievements()
        self._draw_achievement_list(achievements)

        # --- Footer ---
        self.renderer.draw_text(
            "Press  F2  or  ESC  to close",
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - 36,
            FONT_SIZE_SMALL, COLOR_MINT, font_name="sys:calibri", centered=True
        )

        self.renderer.end_frame()

    # ------------------------------------------------------------------ #
    # Achievement list layout                                             #
    # ------------------------------------------------------------------ #

    def _draw_achievement_list(self, achievements):
        """Lay out achievements in a 2-column grid."""
        ctx = self.renderer.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        COLS       = 2
        ITEM_H     = 80   # height per entry (taller to fit unlock date)
        ITEM_PAD_X = 40   # horizontal padding from panel edge
        ITEM_PAD_Y = 80   # Y start (below title)
        ITEM_GAP_Y = 6    # vertical gap between rows
        BAR_H      = 8
        FONT_NAME  = FONT_SIZE_SMALL
        FONT_DESC  = FONT_SIZE_SMALL - 6
        FONT_DATE  = FONT_SIZE_SMALL - 8

        col_w = (WINDOW_WIDTH - 2 * (ITEM_PAD_X + 20)) // COLS
        start_x = ITEM_PAD_X + 20

        for idx, ach in enumerate(achievements):
            col  = idx % COLS
            row  = idx // COLS
            x    = start_x + col * col_w
            y    = ITEM_PAD_Y + row * (ITEM_H + ITEM_GAP_Y)

            is_hidden_locked = (ach.hidden and not ach.unlocked)
            show_progress = (
                ach.type in (AchievementType.ACCUMULATOR, AchievementType.STREAK)
                and not is_hidden_locked
                and not ach.unlocked
            )

            # Pick colours
            if ach.unlocked:
                name_col = _COL_UNLOCKED_NAME
                desc_col = _COL_UNLOCKED_DESC
            else:
                name_col = _COL_LOCKED_NAME
                desc_col = _COL_LOCKED_DESC

            # Name line
            display_name = "???" if is_hidden_locked else ach.name
            self.renderer.draw_text(
                display_name,
                x, y,
                FONT_NAME, name_col, font_name="sys:calibri"
            )

            # Description line
            display_desc = "???" if is_hidden_locked else ach.description
            self.renderer.draw_text(
                display_desc,
                x, y + FONT_NAME + 4,
                FONT_DESC, desc_col, font_name="sys:calibri"
            )

            cursor_y = y + FONT_NAME + 4 + FONT_DESC + 6

            if show_progress:
                # Progress bar (ACCUMULATOR and STREAK while still locked)
                bar_w  = col_w - 20
                prog, tgt = self.achievement_manager.get_progress(ach.id)
                pct    = min(prog / max(tgt, 1), 1.0)
                fill_w = int(bar_w * pct)

                self.renderer.draw_rect(x, cursor_y, bar_w, BAR_H, _COL_BAR_BG)
                if fill_w > 0:
                    self.renderer.draw_rect(x, cursor_y, fill_w, BAR_H, (*_COL_BAR_FG[:3], 0.9))

                prog_text = f"{prog} / {tgt}  ({pct * 100:.0f}%)"
                self.renderer.draw_text(
                    prog_text,
                    x, cursor_y + BAR_H + 2,
                    FONT_DATE, desc_col, font_name="sys:calibri"
                )

            elif ach.unlocked and ach.unlocked_at:
                # Unlock date/time for completed achievements
                self.renderer.draw_text(
                    f"Unlocked: {ach.unlocked_at}",
                    x, cursor_y,
                    FONT_DATE, (0.45, 0.65, 0.45, 1.0), font_name="sys:calibri"
                )

        ctx.disable(moderngl.BLEND)
