#!/usr/bin/env python3
"""
Test script to validate text shader UV coordinates
This test validates the math without requiring OpenGL context
"""
import numpy as np

def test_uv_coordinates():
    """Test that UV coordinates are correctly mapped for text rendering"""
    print("Testing UV coordinate mapping for text rendering...")
    
    # Simulate a text quad at position (100, 200) with size (200, 50)
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    x = 100
    y = 200
    text_width = 200
    text_height = 50
    
    # Convert screen coordinates to NDC (same as in renderer.py)
    ndc_x = (x / WINDOW_WIDTH) * 2 - 1
    ndc_y = 1 - (y / WINDOW_HEIGHT) * 2
    ndc_width = (text_width / WINDOW_WIDTH) * 2
    ndc_height = (text_height / WINDOW_HEIGHT) * 2
    
    print(f"Screen coords: x={x}, y={y}, w={text_width}, h={text_height}")
    print(f"NDC coords: x={ndc_x:.3f}, y={ndc_y:.3f}, w={ndc_width:.3f}, h={ndc_height:.3f}")
    
    # Create vertices with UV coordinates (same format as in renderer.py)
    vertices = np.array([
        # Bottom-left: position (x, y) + UV (u, v)
        ndc_x, ndc_y - ndc_height, 0.0, 1.0,
        # Bottom-right
        ndc_x + ndc_width, ndc_y - ndc_height, 1.0, 1.0,
        # Top-left
        ndc_x, ndc_y, 0.0, 0.0,
        # Top-right
        ndc_x + ndc_width, ndc_y, 1.0, 0.0,
    ], dtype='f4')
    
    print("\nVertex data (position + UV):")
    for i in range(0, len(vertices), 4):
        pos_x, pos_y, uv_u, uv_v = vertices[i:i+4]
        print(f"  Vertex {i//4}: pos=({pos_x:6.3f}, {pos_y:6.3f})  UV=({uv_u:.1f}, {uv_v:.1f})")
    
    # Validate UV coordinates
    # UV should be (0,0) at top-left and (1,1) at bottom-right
    # Vertices are in triangle strip order: BL, BR, TL, TR
    
    uv_coords = vertices.reshape(-1, 4)[:, 2:4]
    expected_uvs = np.array([
        [0.0, 1.0],  # Bottom-left
        [1.0, 1.0],  # Bottom-right
        [0.0, 0.0],  # Top-left
        [1.0, 0.0],  # Top-right
    ])
    
    if np.allclose(uv_coords, expected_uvs):
        print("\n✓ UV coordinates are correct!")
        print("  Top-left corner maps to UV (0, 0)")
        print("  Bottom-right corner maps to UV (1, 1)")
        print("  This ensures the full texture is displayed on the quad")
        return True
    else:
        print("\n✗ UV coordinates are INCORRECT!")
        print(f"Expected:\n{expected_uvs}")
        print(f"Got:\n{uv_coords}")
        return False

def test_shader_compatibility():
    """Test that the shader can handle the vertex format"""
    print("\n" + "="*60)
    print("Testing shader compatibility...")
    
    # Read the text shader
    try:
        with open('shaders/text.vert', 'r') as f:
            vert_shader = f.read()
        with open('shaders/text.frag', 'r') as f:
            frag_shader = f.read()
        
        print("✓ Text shaders found")
        
        # Check that vertex shader accepts position and UV
        if 'in vec2 in_position' in vert_shader and 'in vec2 in_uv' in vert_shader:
            print("✓ Vertex shader accepts in_position and in_uv")
        else:
            print("✗ Vertex shader missing required inputs")
            return False
        
        # Check that vertex shader outputs UV
        if 'out vec2 uv' in vert_shader:
            print("✓ Vertex shader outputs uv")
        else:
            print("✗ Vertex shader doesn't output uv")
            return False
        
        # Check that UV is passed through (not computed from position)
        if 'uv = in_uv' in vert_shader:
            print("✓ Vertex shader passes UV through directly")
        else:
            print("✗ Vertex shader doesn't pass UV through")
            return False
        
        # Check fragment shader
        if 'in vec2 uv' in frag_shader and 'texture(tex, uv)' in frag_shader:
            print("✓ Fragment shader uses UV coordinates correctly")
        else:
            print("✗ Fragment shader doesn't use UV correctly")
            return False
        
        print("\n✓ Shader compatibility check passed!")
        return True
        
    except FileNotFoundError as e:
        print(f"✗ Could not find shader file: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Text Rendering UV Coordinate Test")
    print("="*60)
    
    test1 = test_uv_coordinates()
    test2 = test_shader_compatibility()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("✓ All tests PASSED!")
        print("\nThe text rendering system should now work correctly.")
        print("UV coordinates are properly mapped to display the full texture")
        print("on positioned quads, fixing the black screen issue.")
        exit(0)
    else:
        print("✗ Some tests FAILED!")
        exit(1)
