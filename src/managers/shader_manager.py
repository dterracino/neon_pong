"""
Shader manager for loading and compiling GLSL shaders
"""
import os
from typing import Dict, Optional
import moderngl


class ShaderManager:
    """Manages shader loading and compilation"""
    
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        self.programs: Dict[str, moderngl.Program] = {}
        
        # Base paths
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.shaders_path = os.path.join(self.base_path, 'shaders')
        
        # Create shaders directory if it doesn't exist
        os.makedirs(self.shaders_path, exist_ok=True)
    
    def load_shader(self, name: str, vertex_file: str, fragment_file: str) -> Optional[moderngl.Program]:
        """Load and compile a shader program"""
        if name in self.programs:
            return self.programs[name]
        
        try:
            # Read shader files
            vertex_path = os.path.join(self.shaders_path, vertex_file)
            fragment_path = os.path.join(self.shaders_path, fragment_file)
            
            with open(vertex_path, 'r') as f:
                vertex_source = f.read()
            
            with open(fragment_path, 'r') as f:
                fragment_source = f.read()
            
            # Compile and link program
            program = self.ctx.program(
                vertex_shader=vertex_source,
                fragment_shader=fragment_source
            )
            
            self.programs[name] = program
            return program
            
        except FileNotFoundError as e:
            print(f"Shader file not found: {e}")
            return None
        except Exception as e:
            print(f"Error compiling shader {name}: {e}")
            return None
    
    def get_program(self, name: str) -> Optional[moderngl.Program]:
        """Get a compiled shader program"""
        return self.programs.get(name)