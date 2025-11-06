import pygame
import os

SOUNDS_TEST_PATH = "assets/sounds/test"
MUSIC_TEST_PATH = "assets/music/test"

def test_sound_effects():
    print("\n--- Testing Sound Effects ---")
    for filename in os.listdir(SOUNDS_TEST_PATH):
        path = os.path.join(SOUNDS_TEST_PATH, filename)
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if not os.path.isfile(path):
            continue
        try:
            sound = pygame.mixer.Sound(path)
            print(f"Sound | {ext.upper():5} | {filename:20} | SUCCESS | Playing 1s...")
            sound.play()
            pygame.time.wait(1000)
            sound.stop()
        except Exception as e:
            print(f"Sound | {ext.upper():5} | {filename:20} | FAIL    | {e}")

def test_music_streams():
    print("\n--- Testing Music Streaming ---")
    for filename in os.listdir(MUSIC_TEST_PATH):
        path = os.path.join(MUSIC_TEST_PATH, filename)
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if not os.path.isfile(path):
            continue
        try:
            pygame.mixer.music.load(path)
            print(f"Music | {ext.upper():5} | {filename:20} | SUCCESS | Playing 5s...")
            pygame.mixer.music.play()
            pygame.time.wait(3000)
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Music | {ext.upper():5} | {filename:20} | FAIL    | {e}")

def main():
    pygame.init()
    pygame.mixer.init()
    test_sound_effects()
    test_music_streams()
    pygame.quit()
    print("\nTest complete.")

if __name__ == "__main__":
    main()
