"""
Asset manager for loading and caching game assets
"""
import os
import logging
import pygame
from typing import Dict, Optional, Callable, Tuple
from src.utils.constants import FONT_SIZE_SMALL, FONT_SIZE_DEFAULT, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE

logger = logging.getLogger(__name__)


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
        self.music_files: Dict[str, str] = {}  # name -> filepath
        self.current_music_path: Optional[str] = None  # Currently loaded music file
        self._is_preloading: bool = False  # Flag to indicate if assets are currently being loaded
        
        # Base paths
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.assets_path = os.path.join(self.base_path, 'assets')
        self.fonts_path = os.path.join(self.assets_path, 'fonts')
        self.sounds_path = os.path.join(self.assets_path, 'sounds')
        self.music_path = os.path.join(self.assets_path, 'music')
        
        logger.debug("Initializing asset manager")
        logger.debug("Base path: %s", self.base_path)
        logger.debug("Assets path: %s", self.assets_path)
        logger.debug("Fonts path: %s", self.fonts_path)
        logger.debug("Sounds path: %s", self.sounds_path)
        logger.debug("Music path: %s", self.music_path)
        
        # Create directories if they don't exist
        os.makedirs(self.assets_path, exist_ok=True)
        os.makedirs(self.fonts_path, exist_ok=True)
        os.makedirs(self.sounds_path, exist_ok=True)
        os.makedirs(self.music_path, exist_ok=True)
    
    def get_font(self, name: Optional[str] = None, size: int = 32) -> pygame.font.Font:
        """Get a font, creating it if not cached"""
        key = (name, size)
        
        if key not in self.fonts:
            try:
                if name and os.path.exists(os.path.join(self.fonts_path, name)):
                    font_path = os.path.join(self.fonts_path, name)
                    self.fonts[key] = pygame.font.Font(font_path, size)
                    logger.debug("Loaded font '%s' at size %d", name, size)
                else:
                    # Use default font
                    self.fonts[key] = pygame.font.Font(None, size)
                    logger.debug("Using default pygame font at size %d", size)
            except Exception as e:
                logger.error("Error loading font %s: %s", name, e)
                self.fonts[key] = pygame.font.Font(None, size)
        
        return self.fonts[key]
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a sound by name (without extension)"""
        return self.sounds.get(name.lower())
    
    def load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """Load a single sound effect by filename"""
        sound_path = os.path.join(self.sounds_path, filename)
        
        if not os.path.exists(sound_path):
            logger.warning("Sound not found: %s", sound_path)
            return None
        
        try:
            # Get name without extension
            name = os.path.splitext(filename)[0].lower()
            sound = pygame.mixer.Sound(sound_path)
            self.sounds[name] = sound
            logger.debug("Loaded sound '%s' from %s", name, filename)
            return sound
        except Exception as e:
            logger.error("Error loading sound %s: %s", filename, e)
            return None
    
    def get_music_path(self, name: str) -> Optional[str]:
        """Get music file path by name (without extension)"""
        return self.music_files.get(name.lower())
    
    def load_music(self, name_or_filename: str) -> bool:
        """Load background music by name (without extension) or filename"""
        # Try to get from preloaded music files first
        music_file_path = self.get_music_path(name_or_filename)
        
        # If not found, try as direct filename
        if music_file_path is None:
            music_file_path = os.path.join(self.music_path, name_or_filename)
        
        if not os.path.exists(music_file_path):
            logger.warning("Music not found: %s", music_file_path)
            return False
        
        try:
            pygame.mixer.music.load(music_file_path)
            self.current_music_path = music_file_path  # Track currently loaded music
            logger.debug("Loaded music from %s", music_file_path)
            return True
        except Exception as e:
            logger.error("Error loading music %s: %s", name_or_filename, e)
            return False
    
    def preload_music(self) -> int:
        """Discover all music files in the music directory
        Returns:
            Number of music files registered
        """
        if not os.path.exists(self.music_path):
            logger.debug("Music path does not exist: %s", self.music_path)
            return 0
        music_extensions = ('.wav', '.ogg', '.mp3', '.flac', '.mid', '.midi', '.mod', '.xm')
        music_files = [f for f in os.listdir(self.music_path)
                      if f.lower().endswith(music_extensions)]
        if not music_files:
            logger.debug("No music files found in %s", self.music_path)
            return 0
        logger.debug("Found %d music files", len(music_files))
        registered = 0
        for music_file in music_files:
            try:
                name = os.path.splitext(music_file)[0].lower()
                file_path = os.path.join(self.music_path, music_file)
                self.music_files[name] = file_path
                logger.debug("Registered music '%s' -> %s", name, music_file)
                registered += 1
            except Exception as e:
                logger.error("Failed to register music %s: %s", music_file, e)
        logger.debug("Registered %d music files", registered)
        return registered
    
    def preload_sounds(self) -> int:
        """Automatically load all sound files from the sounds directory
        Returns:
            Number of sounds loaded
        """
        if not os.path.exists(self.sounds_path):
            logger.debug("Sounds path does not exist: %s", self.sounds_path)
            return 0
        sound_extensions = ('.wav', '.ogg', '.mp3', '.flac')
        sound_files = [f for f in os.listdir(self.sounds_path)
                      if f.lower().endswith(sound_extensions)]
        if not sound_files:
            logger.debug("No sound files found in %s", self.sounds_path)
            return 0
        logger.debug("Loading %d sound files", len(sound_files))
        loaded = 0
        for sound_file in sound_files:
            try:
                self.load_sound(sound_file)
                loaded += 1
            except Exception as e:
                logger.error("Failed to load sound %s: %s", sound_file, e)
        logger.debug("Loaded %d sounds", loaded)
        return loaded
    
    def preload_fonts(self, sizes: Optional[list] = None) -> int:
        """Preload all fonts from the fonts directory
        Args:
            sizes: List of font sizes to preload for each font. 
                   If None, uses default sizes from constants (SMALL, DEFAULT, MEDIUM, LARGE)
        Returns:
            Number of font/size combinations loaded
        """
        if sizes is None:
            sizes = [FONT_SIZE_SMALL, FONT_SIZE_DEFAULT, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE]
        if not os.path.exists(self.fonts_path):
            logger.debug("Fonts path does not exist: %s", self.fonts_path)
            return 0
        font_files = [f for f in os.listdir(self.fonts_path)
                     if f.lower().endswith(('.ttf', '.otf', '.fon'))]
        if not font_files:
            logger.debug("No fonts found in %s", self.fonts_path)
            return 0
        logger.debug("Preloading %d fonts at %d sizes", len(font_files), len(sizes))
        loaded = 0
        for font_file in font_files:
            for size in sizes:
                try:
                    self.get_font(font_file, size)
                    logger.debug("Preloaded %s at size %d", font_file, size)
                    loaded += 1
                except Exception as e:
                    logger.error("Failed to preload %s at size %d: %s", font_file, size, e)
        logger.debug("Preloaded %d font/size combinations", loaded)
        return loaded
    
    def log_loaded_assets(self):
        logger.info("Currently loaded assets: %d sounds, %d music, %d fonts", len(self.sounds), len(self.music_files), len(self.fonts)) 
        logger.info("--- Loaded Sounds ---")
        for key, value in self.sounds.items():
            logger.info("Sound: %s => <pygame.mixer.Sound object>", key)
        logger.info("--- Loaded Music Files ---")
        for key, value in self.music_files.items():
            logger.info("Music: %s => %s", key, value)
        logger.info("--- Loaded Fonts ---")
        for key, value in self.fonts.items():
            logger.info("Font: %s => <pygame.font.Font object>", key)  
        logger.info("Finished logging all assets")
    
    @property
    def is_preloading(self) -> bool:
        """Check if assets are currently being loaded"""
        return self._is_preloading
    
    def preload_assets(self, 
                       font_sizes: Optional[list] = None,
                       on_complete: Optional[Callable[[int, int, int], None]] = None) -> Tuple[int, int, int]:
        """Preload all assets (sounds, music, fonts)
        Args:
            font_sizes: List of font sizes to preload. If None, uses defaults from constants.
            on_complete: Optional callback(sounds, music, fonts) called when loading completes.
        Returns:
            Tuple of (sounds_loaded, music_registered, fonts_loaded)
        """
        logger.debug("Starting asset preloading")
        self._is_preloading = True
        sounds_loaded = music_registered = fonts_loaded = 0
        try:
            logger.debug("Loading sounds...")
            sounds_loaded = self.preload_sounds()
            logger.debug("Registering music...")
            music_registered = self.preload_music()
            logger.debug("Loading fonts...")
            fonts_loaded = self.preload_fonts(sizes=font_sizes)
            logger.debug("Asset preloading complete")
            logger.debug("Loaded %d sounds, %d music, %d font combinations", 
                        sounds_loaded, music_registered, fonts_loaded)
        except Exception as e:
            logger.error("Error during asset preloading: %s", e)
        finally:
            self._is_preloading = False
            if on_complete:
                logger.debug("Calling on_complete callback")
                on_complete(sounds_loaded, music_registered, fonts_loaded)

        return (sounds_loaded, music_registered, fonts_loaded)