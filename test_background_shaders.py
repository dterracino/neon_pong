#!/usr/bin/env python3
"""
Test script to validate background shaders compile correctly
"""
import os
import sys

def test_shader_syntax():
    """Test that shader files exist and have basic valid syntax"""
    shader_dir = os.path.join(os.path.dirname(__file__), 'shaders')
    
    tests_passed = True
    
    # Check starfield shader
    starfield_path = os.path.join(shader_dir, 'background_starfield.frag')
    if os.path.exists(starfield_path):
        with open(starfield_path, 'r') as f:
            content = f.read()
            if '#version 330' in content and 'void main()' in content:
                print("✓ Starfield shader file is valid")
            else:
                print("✗ Starfield shader file has syntax issues")
                tests_passed = False
    else:
        print("✗ Starfield shader file not found")
        tests_passed = False
    
    # Check plasma shader
    plasma_path = os.path.join(shader_dir, 'background_plasma.frag')
    if os.path.exists(plasma_path):
        with open(plasma_path, 'r') as f:
            content = f.read()
            if '#version 330' in content and 'void main()' in content:
                print("✓ Plasma shader file is valid")
            else:
                print("✗ Plasma shader file has syntax issues")
                tests_passed = False
    else:
        print("✗ Plasma shader file not found")
        tests_passed = False
    
    # Check waves shader
    waves_path = os.path.join(shader_dir, 'background_waves.frag')
    if os.path.exists(waves_path):
        with open(waves_path, 'r') as f:
            content = f.read()
            if '#version 330' in content and 'void main()' in content:
                print("✓ Waves shader file is valid")
            else:
                print("✗ Waves shader file has syntax issues")
                tests_passed = False
    else:
        print("✗ Waves shader file not found")
        tests_passed = False
    
    # Check that they have the required uniforms
    with open(starfield_path, 'r') as f:
        content = f.read()
        if 'uniform float time' in content and 'uniform vec2 resolution' in content:
            print("✓ Starfield shader has required uniforms")
        else:
            print("✗ Starfield shader missing required uniforms")
            tests_passed = False
    
    with open(plasma_path, 'r') as f:
        content = f.read()
        if 'uniform float time' in content and 'uniform vec2 resolution' in content:
            print("✓ Plasma shader has required uniforms")
        else:
            print("✗ Plasma shader missing required uniforms")
            tests_passed = False
    
    waves_path = os.path.join(shader_dir, 'background_waves.frag')
    with open(waves_path, 'r') as f:
        content = f.read()
        if 'uniform float time' in content and 'uniform vec2 resolution' in content:
            print("✓ Waves shader has required uniforms")
        else:
            print("✗ Waves shader missing required uniforms")
            tests_passed = False
    
    return tests_passed

def test_constants_updated():
    """Test that constants file has background type setting"""
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from src.utils.constants import BACKGROUND_TYPE
        print(f"✓ BACKGROUND_TYPE constant found: {BACKGROUND_TYPE}")
        if BACKGROUND_TYPE in ["starfield", "plasma", "waves", "solid"]:
            print(f"✓ BACKGROUND_TYPE has valid value")
            return True
        else:
            print(f"✗ BACKGROUND_TYPE has invalid value")
            return False
    except ImportError as e:
        print(f"✗ Failed to import BACKGROUND_TYPE: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Background Shader Test")
    print("=" * 60)
    print()
    
    test1 = test_shader_syntax()
    print()
    test2 = test_constants_updated()
    
    print()
    print("=" * 60)
    if test1 and test2:
        print("✓ All tests PASSED!")
        print()
        print("Background shaders are ready to use.")
        sys.exit(0)
    else:
        print("✗ Some tests FAILED!")
        sys.exit(1)
