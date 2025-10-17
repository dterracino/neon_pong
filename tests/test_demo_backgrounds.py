#!/usr/bin/env python3
"""
Test that the demo backgrounds app is properly structured
"""
import os
import sys

def test_demo_structure():
    """Test that demo app has correct structure"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    # Import the module
    import demo_backgrounds
    
    # Check that SHADERS dict exists
    assert hasattr(demo_backgrounds, 'SHADERS'), "SHADERS dict not found"
    assert len(demo_backgrounds.SHADERS) == 5, "Should have 5 shaders defined"
    
    # Check that all required shaders are present
    expected_shaders = ['starfield', 'plasma', 'waves', 'retrowave', 'retro']
    for shader in expected_shaders:
        assert shader in demo_backgrounds.SHADERS, f"Shader '{shader}' not found in SHADERS"
    
    # Check that BackgroundShaderDemo class exists
    assert hasattr(demo_backgrounds, 'BackgroundShaderDemo'), "BackgroundShaderDemo class not found"
    
    # Verify each shader has required fields
    for shader_id, config in demo_backgrounds.SHADERS.items():
        assert 'name' in config, f"Shader {shader_id} missing 'name' field"
        assert 'vertex' in config, f"Shader {shader_id} missing 'vertex' field"
        assert 'fragment' in config, f"Shader {shader_id} missing 'fragment' field"
        assert 'key' in config, f"Shader {shader_id} missing 'key' field"
        assert 'description' in config, f"Shader {shader_id} missing 'description' field"
        
        # Verify shader files exist
        shader_dir = os.path.join(os.path.dirname(__file__), '..', 'shaders')
        vertex_path = os.path.join(shader_dir, config['vertex'])
        fragment_path = os.path.join(shader_dir, config['fragment'])
        
        assert os.path.exists(vertex_path), f"Vertex shader not found: {vertex_path}"
        assert os.path.exists(fragment_path), f"Fragment shader not found: {fragment_path}"
    
    print("✓ Demo app structure is correct")
    print(f"✓ All {len(demo_backgrounds.SHADERS)} shaders are configured")
    print("✓ All shader files exist")
    print("✓ BackgroundShaderDemo class is defined")
    
    return True

if __name__ == "__main__":
    try:
        if test_demo_structure():
            print("\n✓ All demo app tests PASSED!")
            sys.exit(0)
        else:
            print("\n✗ Demo app tests FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error testing demo app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
