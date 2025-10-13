"""
Shader manager for loading and compiling GLSL shaders
"""
import os
from typing import Dict, Optional
import moderngl


class ShaderManager:
    """Manages shader loading and compilation"""
    
    def __init__(self, ctx: moderngl.Context):
        print("[DEBUG] ShaderManager.__init__: Initializing shader manager...")
        self.ctx = ctx
        self.programs: Dict[str, moderngl.Program] = {}
        
        # Base paths
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.shaders_path = os.path.join(self.base_path, 'shaders')
        print(f"[DEBUG] ShaderManager.__init__: Shaders path: {self.shaders_path}")
        
        # Create shaders directory if it doesn't exist
        os.makedirs(self.shaders_path, exist_ok=True)
        print("[DEBUG] ShaderManager.__init__: Shader manager initialized")
    
    def load_shader(self, name: str, vertex_file: str, fragment_file: str) -> Optional[moderngl.Program]:
        """Load and compile a shader program"""
        print(f"[DEBUG] ShaderManager.load_shader: Loading shader '{name}' (vert: {vertex_file}, frag: {fragment_file})...")
        
        if name in self.programs:
            print(f"[DEBUG] ShaderManager.load_shader: Shader '{name}' already loaded, returning cached version")
            return self.programs[name]
        
        try:
            # Read shader files
            vertex_path = os.path.join(self.shaders_path, vertex_file)
            fragment_path = os.path.join(self.shaders_path, fragment_file)
            
            print(f"[DEBUG] ShaderManager.load_shader: Reading vertex shader from: {vertex_path}")
            with open(vertex_path, 'r') as f:
                vertex_source = f.read()
            print(f"[DEBUG] ShaderManager.load_shader: Vertex shader read successfully ({len(vertex_source)} chars)")
            
            print(f"[DEBUG] ShaderManager.load_shader: Reading fragment shader from: {fragment_path}")
            with open(fragment_path, 'r') as f:
                fragment_source = f.read()
            print(f"[DEBUG] ShaderManager.load_shader: Fragment shader read successfully ({len(fragment_source)} chars)")
            
            # Compile and link program
            print(f"[DEBUG] ShaderManager.load_shader: Compiling shader program '{name}'...")
            program = self.ctx.program(
                vertex_shader=vertex_source,
                fragment_shader=fragment_source
            )
            
            self.programs[name] = program
            print(f"[DEBUG] ShaderManager.load_shader: Shader '{name}' compiled and loaded successfully!")
            return program
            
        except FileNotFoundError as e:
            print(f"[ERROR] ShaderManager.load_shader: Shader file not found: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] ShaderManager.load_shader: Error compiling shader {name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_program(self, name: str) -> Optional[moderngl.Program]:
        """Get a compiled shader program"""
        return self.programs.get(name)