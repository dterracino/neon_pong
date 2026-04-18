"""
Scene manager for handling different game states
"""
import logging
from typing import Optional, List
from src.utils.transitions import Transition, create_transition

logger = logging.getLogger(__name__)


class Scene:
    """Base scene class"""
    
    # Class-level transition hints (can be overridden per instance or per call)
    preferred_transition_in: Optional[str] = None
    preferred_transition_out: Optional[str] = None
    
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
        self.current_transition: Optional[Transition] = None
        self.pending_scene: Optional[Scene] = None  # Scene waiting for transition to complete
        self.pending_action: Optional[str] = None  # "push" or "change"
        self.old_scene: Optional[Scene] = None  # For crossfade rendering
    
    @property
    def current_scene(self) -> Optional[Scene]:
        """Get the current active scene"""
        return self.scenes[-1] if self.scenes else None
    
    def update(self, dt: float):
        """
        Update scene manager (handles transitions).
        
        Args:
            dt: Delta time in seconds
        """
        if self.current_transition:
            self.current_transition.update(dt)
            
            if self.current_transition.is_complete:
                # Transition finished
                logger.debug("Transition complete")
                self.current_transition = None
                self.old_scene = None
    
    def is_transitioning(self) -> bool:
        """Check if a transition is currently active"""
        return self.current_transition is not None
    
    def push_scene(self, scene: Scene, transition: Optional[str] = None):
        """
        Push a new scene onto the stack with optional transition.
        
        Args:
            scene: Scene to push
            transition: Transition type (overrides scene hints if provided)
        """
        logger.debug("Pushing scene: %s", type(scene).__name__)
        
        # If no current scene (first scene), push immediately without transition
        if not self.current_scene:
            logger.debug("No current scene, pushing immediately")
            self._push_scene_immediate(scene)
            return
        
        # Determine transition type
        if transition is None:
            # Use scene's preferred transition in, or immediate if none
            transition = scene.preferred_transition_in
        
        logger.debug("Using transition: %s", transition)
        
        # If no transition or immediate, do it synchronously
        if transition is None or transition == "immediate":
            self._push_scene_immediate(scene)
        else:
            # Create transition
            self.current_transition = create_transition(transition)
            self.pending_scene = scene
            self.pending_action = "push"
            
            # Set up callback to actually switch scenes mid-transition
            def switch_scene():
                self._push_scene_immediate(self.pending_scene)
                self.pending_scene = None
                self.pending_action = None
            
            self.current_transition.on_mid_transition = switch_scene
            
            # For crossfade, we need the old scene
            if transition == "crossfade":
                self.old_scene = self.current_scene
    
    def _push_scene_immediate(self, scene: Scene):
        """Push a scene immediately without transition"""
        if self.current_scene:
            logger.debug("Calling on_exit on current scene: %s", type(self.current_scene).__name__)
            self.current_scene.on_exit()
        
        self.scenes.append(scene)
        logger.debug("Calling on_enter on new scene: %s", type(scene).__name__)
        scene.on_enter()
        logger.debug("Scene stack size: %d", len(self.scenes))
    
    def pop_scene(self):
        """Pop the current scene"""
        if self.scenes:
            scene = self.scenes.pop()
            scene.on_exit()
            
            if self.current_scene:
                self.current_scene.on_enter()
    
    def change_scene(self, scene: Scene, transition: Optional[str] = None):
        """
        Replace current scene with new scene, with optional transition.
        
        Args:
            scene: New scene to display
            transition: Transition type (overrides scene hints if provided)
        """
        logger.debug("Changing to scene: %s", type(scene).__name__)
        
        # Determine transition type
        if transition is None:
            # Try outgoing scene's preferred out, then incoming scene's preferred in
            if self.current_scene and self.current_scene.preferred_transition_out:
                transition = self.current_scene.preferred_transition_out
            else:
                transition = scene.preferred_transition_in
        
        logger.debug("Using transition: %s", transition)
        
        # If no transition or immediate, do it synchronously
        if transition is None or transition == "immediate":
            logger.debug("No transition, changing scene immediately")
            if self.scenes:
                self.pop_scene()
            self._push_scene_immediate(scene)
        else:
            # Create transition
            logger.debug("Creating transition: %s", transition)
            self.current_transition = create_transition(transition)
            self.pending_scene = scene
            self.pending_action = "change"
            
            # Set up callback to actually switch scenes mid-transition
            def switch_scene():
                logger.debug("Transition callback invoked - switching scenes")
                if self.scenes:
                    self.pop_scene()
                self._push_scene_immediate(self.pending_scene)
                self.pending_scene = None
                self.pending_action = None
            
            self.current_transition.on_mid_transition = switch_scene
            logger.debug("Transition setup complete, callback registered")
            
            # For crossfade, we need the old scene
            if transition == "crossfade":
                self.old_scene = self.current_scene
    
    def render_transition(self, renderer):
        """
        Render transition effect overlay.
        
        This should be called AFTER the scene has been rendered.
        
        Args:
            renderer: Renderer instance
        """
        if self.current_transition:
            self.current_transition.render_overlay(renderer)
    
    def clear_scenes(self):
        """Clear all scenes (quit game)"""
        while self.scenes:
            self.pop_scene()