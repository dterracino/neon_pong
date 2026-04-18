"""Options Manager - Centralized game settings management."""

import logging
from typing import Optional
from src.utils.constants import (
    BACKGROUND_TYPE, POST_EFFECT_TYPE, BLOOM_THRESHOLD, BLOOM_INTENSITY,
    MUSIC_VOLUME, SFX_VOLUME
)

logger = logging.getLogger(__name__)


class OptionsManager:
    """Manages all game options/settings in a centralized location."""
    
    _instance: Optional['OptionsManager'] = None
    
    def __init__(self):
        """Initialize options with defaults from constants."""
        # Graphics settings
        self.background_type = BACKGROUND_TYPE
        self.post_effect_type = POST_EFFECT_TYPE
        self.bloom_threshold = BLOOM_THRESHOLD
        self.bloom_intensity = BLOOM_INTENSITY
        
        # Audio settings
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        
        # Gameplay settings
        self.ai_difficulty = 'normal'
        
        # Display settings
        self.fps_display_enabled = False
        
        logger.debug("OptionsManager initialized with defaults")
    
    @classmethod
    def get_instance(cls) -> 'OptionsManager':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (for testing)."""
        cls._instance = None
    
    # Background settings
    def set_background(self, background_type: str) -> None:
        """Set background shader type."""
        self.background_type = background_type
        logger.debug("Background set to: %s", background_type)
    
    def get_background(self) -> str:
        """Get current background type."""
        return self.background_type
    
    # Post-processing settings
    def set_post_effect(self, effect_type: str) -> None:
        """Set post-processing effect type."""
        self.post_effect_type = effect_type
        logger.debug("Post-processing effect set to: %s", effect_type)
    
    def get_post_effect(self) -> str:
        """Get current post-processing effect type."""
        return self.post_effect_type
    
    # Bloom settings
    def set_bloom_threshold(self, threshold: float) -> None:
        """Set bloom threshold (0.0-1.0)."""
        self.bloom_threshold = max(0.0, min(1.0, threshold))
        logger.debug("Bloom threshold set to: %.2f", self.bloom_threshold)
    
    def get_bloom_threshold(self) -> float:
        """Get current bloom threshold."""
        return self.bloom_threshold
    
    def set_bloom_intensity(self, intensity: float) -> None:
        """Set bloom intensity (0.0-3.0)."""
        self.bloom_intensity = max(0.0, min(3.0, intensity))
        logger.debug("Bloom intensity set to: %.2f", self.bloom_intensity)
    
    def get_bloom_intensity(self) -> float:
        """Get current bloom intensity."""
        return self.bloom_intensity
    
    # Audio settings
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0-1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        logger.debug("Music volume set to: %.2f", self.music_volume)
    
    def get_music_volume(self) -> float:
        """Get current music volume."""
        return self.music_volume
    
    def is_music_enabled(self) -> bool:
        """Check if music is enabled (volume > 0)."""
        return self.music_volume > 0.0
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume (0.0-1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        logger.debug("SFX volume set to: %.2f", self.sfx_volume)
    
    def get_sfx_volume(self) -> float:
        """Get current SFX volume."""
        return self.sfx_volume
    
    def is_sfx_enabled(self) -> bool:
        """Check if SFX is enabled (volume > 0)."""
        return self.sfx_volume > 0.0
    
    # AI settings
    def set_ai_difficulty(self, difficulty: str) -> None:
        """Set AI difficulty (easy, normal, hard)."""
        if difficulty in ['easy', 'normal', 'hard']:
            self.ai_difficulty = difficulty
            logger.debug("AI difficulty set to: %s", difficulty)
        else:
            logger.warning("Invalid AI difficulty: %s", difficulty)
    
    def get_ai_difficulty(self) -> str:
        """Get current AI difficulty."""
        return self.ai_difficulty
    
    # Display settings
    def set_fps_display(self, enabled: bool) -> None:
        """Set FPS display enabled state."""
        self.fps_display_enabled = enabled
        logger.debug("FPS display %s", "enabled" if enabled else "disabled")
    
    def is_fps_display_enabled(self) -> bool:
        """Check if FPS display is enabled."""
        return self.fps_display_enabled
    
    def toggle_fps_display(self) -> bool:
        """Toggle FPS display. Returns new state."""
        self.fps_display_enabled = not self.fps_display_enabled
        logger.debug("FPS display toggled to: %s", self.fps_display_enabled)
        return self.fps_display_enabled
    
    # Utility methods
    def get_all_settings(self) -> dict:
        """Get all settings as a dictionary."""
        return {
            'background': self.background_type,
            'post_effect': self.post_effect_type,
            'bloom_threshold': self.bloom_threshold,
            'bloom_intensity': self.bloom_intensity,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'ai_difficulty': self.ai_difficulty,
            'fps_display': self.fps_display_enabled,
        }
    
    def apply_settings(self, settings: dict) -> None:
        """Apply multiple settings at once."""
        if 'background' in settings:
            self.set_background(settings['background'])
        if 'post_effect' in settings:
            self.set_post_effect(settings['post_effect'])
        if 'bloom_threshold' in settings:
            self.set_bloom_threshold(settings['bloom_threshold'])
        if 'bloom_intensity' in settings:
            self.set_bloom_intensity(settings['bloom_intensity'])
        if 'music_volume' in settings:
            self.set_music_volume(settings['music_volume'])
        if 'sfx_volume' in settings:
            self.set_sfx_volume(settings['sfx_volume'])
        if 'ai_difficulty' in settings:
            self.set_ai_difficulty(settings['ai_difficulty'])
        if 'fps_display' in settings:
            self.set_fps_display(settings['fps_display'])
        
        logger.info("Applied settings: %s", self.get_all_settings())
