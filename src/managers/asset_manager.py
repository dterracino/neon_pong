"""
Asset manager for loading and caching game assets
"""
import os
import pygame
from typing import Dict, Optional


class AssetManager:
    """Singleton asset manager for fonts, sounds, and music"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.fonts: Dict[tuple, pygame.font.Font] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_path: Optional[str] = None
        
        # Base paths
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.assets_path = os.path.join(self.base_path, 'assets')
        self.fonts_path = os.path.join(self.assets_path, 'fonts')
        self.sounds_path = os.path.join(self.assets_path, 'sounds')
        self.music_path_dir = os.path.join(self.assets_path, 'music')
        
        print(f"[DEBUG] AssetManager.__init__: Initializing asset manager")
        print(f"[DEBUG] AssetManager.__init__: Base path: {self.base_path}")
        print(f"[DEBUG] AssetManager.__init__: Assets path: {self.assets_path}")
        print(f"[DEBUG] AssetManager.__init__: Fonts path: {self.fonts_path}")
        
        # Create directories if they don't exist
        os.makedirs(self.fonts_path, exist_ok=True)
        os.makedirs(self.sounds_path, exist_ok=True)
        os.makedirs(self.music_path_dir, exist_ok=True)
    
    def get_font(self, name: Optional[str] = None, size: int = 32) -> pygame.font.Font:
        """Get a font, creating it if not cached"""
        key = (name, size)
        
        if key not in self.fonts:
            try:
                if name and os.path.exists(os.path.join(self.fonts_path, name)):
                    font_path = os.path.join(self.fonts_path, name)
                    self.fonts[key] = pygame.font.Font(font_path, size)
                    print(f"[DEBUG] AssetManager.get_font: Loaded font '{name}' at size {size}")
                else:
                    # Use default font
                    self.fonts[key] = pygame.font.Font(None, size)
                    print(f"[DEBUG] AssetManager.get_font: Using default pygame font at size {size}")
            except Exception as e:
                print(f"[ERROR] AssetManager.get_font: Error loading font {name}: {e}")
                self.fonts[key] = pygame.font.Font(None, size)
        
        return self.fonts[key]
    
    def load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound effect"""
        if filename in self.sounds:
            return self.sounds[filename]
        
        sound_path = os.path.join(self.sounds_path, filename)
        
        if not os.path.exists(sound_path):
            print(f"Sound not found: {sound_path}")
            return None
        
        try:
            sound = pygame.mixer.Sound(sound_path)
            self.sounds[filename] = sound
            return sound
        except Exception as e:
            print(f"Error loading sound {filename}: {e}")
            return None
    
    def load_music(self, filename: str) -> bool:
        """Load background music"""
        music_path = os.path.join(self.music_path_dir, filename)
        
        if not os.path.exists(music_path):
            print(f"Music not found: {music_path}")
            return False
        
        try:
            pygame.mixer.music.load(music_path)
            self.music_path = music_path
            return True
        except Exception as e:
            print(f"Error loading music {filename}: {e}")
            return False
    
    def preload_sounds(self, filenames: list):
        """Preload multiple sounds"""
        for filename in filenames:
            self.load_sound(filename)
    
    def preload_fonts_from_directory(self, sizes: list = None):
        """Preload all fonts from the fonts directory
        
        Args:
            sizes: List of font sizes to preload for each font. 
                   If None, uses default sizes [24, 32, 48, 64, 72]
        """
        if sizes is None:
            sizes = [24, 32, 48, 64, 72]  # Default sizes
        
        if not os.path.exists(self.fonts_path):
            print(f"[DEBUG] AssetManager.preload_fonts_from_directory: Fonts path does not exist: {self.fonts_path}")
            return
        
        # Get all font files in the fonts directory
        font_files = [f for f in os.listdir(self.fonts_path) 
                     if f.endswith(('.ttf', '.otf', '.fon'))]
        
        if not font_files:
            print(f"[DEBUG] AssetManager.preload_fonts_from_directory: No fonts found in {self.fonts_path}")
            return
        
        print(f"[DEBUG] AssetManager.preload_fonts_from_directory: Preloading {len(font_files)} fonts at {len(sizes)} sizes...")
        
        for font_file in font_files:
            for size in sizes:
                try:
                    self.get_font(font_file, size)
                    print(f"[DEBUG] AssetManager.preload_fonts_from_directory: Preloaded {font_file} at size {size}")
                except Exception as e:
                    print(f"[ERROR] AssetManager.preload_fonts_from_directory: Failed to preload {font_file} at size {size}: {e}")
        
        print(f"[DEBUG] AssetManager.preload_fonts_from_directory: Preloaded {len(self.fonts)} font/size combinations")