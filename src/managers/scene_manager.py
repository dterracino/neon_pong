"""
Scene manager for handling different game states
"""
from typing import Optional, List


class Scene:
    """Base scene class"""
    
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
    
    def handle_event(self, event):
        """Handle pygame events"""
        pass
    
    def update(self, dt: float):
        """Update scene logic"""
        pass
    
    def render(self):
        """Render scene"""
        pass
    
    def on_enter(self):
        """Called when scene becomes active"""
        pass
    
    def on_exit(self):
        """Called when scene is removed"""
        pass


class SceneManager:
    """Manages game scenes/states"""
    
    def __init__(self):
        self.scenes: List[Scene] = []
    
    @property
    def current_scene(self) -> Optional[Scene]:
        """Get the current active scene"""
        return self.scenes[-1] if self.scenes else None
    
    def push_scene(self, scene: Scene):
        """Push a new scene onto the stack"""
        print(f"[DEBUG] SceneManager.push_scene: Pushing scene: {type(scene).__name__}")
        if self.current_scene:
            print(f"[DEBUG] SceneManager.push_scene: Calling on_exit on current scene: {type(self.current_scene).__name__}")
            self.current_scene.on_exit()
        
        self.scenes.append(scene)
        print(f"[DEBUG] SceneManager.push_scene: Calling on_enter on new scene: {type(scene).__name__}")
        scene.on_enter()
        print(f"[DEBUG] SceneManager.push_scene: Scene stack size: {len(self.scenes)}")
    
    def pop_scene(self):
        """Pop the current scene"""
        if self.scenes:
            scene = self.scenes.pop()
            scene.on_exit()
            
            if self.current_scene:
                self.current_scene.on_enter()
    
    def change_scene(self, scene: Scene):
        """Replace current scene with new scene"""
        print(f"[DEBUG] SceneManager.change_scene: Changing to scene: {type(scene).__name__}")
        if self.scenes:
            self.pop_scene()
        self.push_scene(scene)
    
    def clear_scenes(self):
        """Clear all scenes (quit game)"""
        while self.scenes:
            self.pop_scene()