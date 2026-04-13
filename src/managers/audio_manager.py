"""
Audio manager for sound effects and music
"""
import logging
import pygame
import random
from src.managers.asset_manager import AssetManager
from src.utils.constants import MUSIC_VOLUME, SFX_VOLUME

logger = logging.getLogger(__name__)


class AudioManager:
    """Manages game audio"""
    
    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        self._is_ducked = False  # Track if music is currently ducked
    
    def play_sound(self, sound_name: str, pitch_variation: bool = False):
        """Play a sound effect by name (without extension)"""
        sound = self.asset_manager.get_sound(sound_name)
        
        if sound:
            volume = self.sfx_volume
            
            # Pitch variation not directly supported in pygame, but we can adjust volume slightly
            if pitch_variation:
                volume = max(0.0, min(1.0, self.sfx_volume * random.uniform(0.8, 1.2)))
            
            sound.set_volume(volume)
            sound.play()
            logger.debug("play_sound: '%s' (volume=%.2f, pitch_variation=%s)", sound_name, volume, pitch_variation)
        else:
            logger.warning("play_sound: '%s' not found (not loaded or wrong name)", sound_name)
    
    def play_music(self, filename: str, loops: int = -1):
        """Play background music"""
        if self.asset_manager.load_music(filename):
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
    
    def duck_music(self, duck_amount: float = 0.5):
        """Lower music volume (audio ducking)
        
        Args:
            duck_amount: Multiplier for volume reduction (0.5 = 50% volume)
        """
        if not self._is_ducked:
            self._is_ducked = True
            ducked_volume = self.music_volume * duck_amount
            pygame.mixer.music.set_volume(ducked_volume)
    
    def unduck_music(self):
        """Restore music to normal volume"""
        if self._is_ducked:
            self._is_ducked = False
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        # Apply volume immediately, respecting duck state
        if self._is_ducked:
            pygame.mixer.music.set_volume(self.music_volume * 0.5)
        else:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))