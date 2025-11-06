"""
Shader manager for loading and compiling GLSL shaders
"""
import logging
import os
from typing import Dict, Optional
import moderngl

logger = logging.getLogger(__name__)


class ShaderManager:
    """Manages shader loading and compilation"""
    
    def __init__(self, ctx: moderngl.Context):
        logger.debug("Initializing shader manager")
        self.ctx = ctx
        self.programs: Dict[str, moderngl.Program] = {}
        
        # Base paths
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.shaders_path = os.path.join(self.base_path, 'shaders')
        logger.debug("Shaders path: %s", self.shaders_path)
        
        # Create shaders directory if it doesn't exist
        os.makedirs(self.shaders_path, exist_ok=True)
        logger.debug("Shader manager initialized")
    
    def load_shader(self, name: str, vertex_file: str, fragment_file: str) -> Optional[moderngl.Program]:
        """Load and compile a shader program"""
        logger.debug("Loading shader '%s' (vert: %s, frag: %s)", name, vertex_file, fragment_file)
        
        if name in self.programs:
            logger.debug("Shader '%s' already loaded, returning cached version", name)
            return self.programs[name]
        
        try:
            # Read shader files
            vertex_path = os.path.join(self.shaders_path, vertex_file)
            fragment_path = os.path.join(self.shaders_path, fragment_file)
            
            logger.debug("Reading vertex shader from: %s", vertex_path)
            with open(vertex_path, 'r') as f:
                vertex_source = f.read()
            logger.debug("Vertex shader read successfully (%d chars)", len(vertex_source))
            
            logger.debug("Reading fragment shader from: %s", fragment_path)
            with open(fragment_path, 'r') as f:
                fragment_source = f.read()
            logger.debug("Fragment shader read successfully (%d chars)", len(fragment_source))
            
            # Compile and link program
            logger.debug("Compiling shader program '%s'", name)
            program = self.ctx.program(
                vertex_shader=vertex_source,
                fragment_shader=fragment_source
            )
            
            self.programs[name] = program
            logger.debug("Shader '%s' compiled and loaded successfully", name)
            return program
            
        except FileNotFoundError as e:
            logger.error("Shader file not found: %s", e)
            return None
        except Exception as e:
            logger.exception("Error compiling shader %s: %s", name, e)
            return None
    
    def get_program(self, name: str) -> Optional[moderngl.Program]:
        """Get a compiled shader program"""
        return self.programs.get(name)