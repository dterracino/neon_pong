"""
Audio manager for sound effects and music
"""
import pygame
import random
from src.managers.asset_manager import AssetManager
from src.utils.constants import MUSIC_VOLUME, SFX_VOLUME


class AudioManager:
    """Manages game audio"""
    
    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        
        # Try to load default sounds (will fail gracefully if not found)
        self.sounds = {
            'paddle_hit': asset_manager.load_sound('paddle_hit.wav'),
            'wall_hit': asset_manager.load_sound('wall_hit.wav'),
            'score': asset_manager.load_sound('score.wav'),
            'win': asset_manager.load_sound('win.wav'),
        }
    
    def play_sound(self, sound_name: str, pitch_variation: bool = False):
        """Play a sound effect"""
        sound = self.sounds.get(sound_name)
        
        if sound:
            volume = self.sfx_volume
            
            # Pitch variation not directly supported in pygame, but we can adjust volume slightly
            if pitch_variation:
                volume = max(0.0, min(1.0, self.sfx_volume * random.uniform(0.8, 1.2)))
            
            sound.set_volume(volume)
            sound.play()
    
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
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))