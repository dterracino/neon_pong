#!/usr/bin/env python3
"""
Test script to validate post-processing style effect shaders
"""
import os
import sys

def test_shader_syntax():
    """Test that shader files exist and have basic valid syntax"""
    shader_dir = os.path.join(os.path.dirname(__file__), '..', 'shaders')
    
    tests_passed = True
    
    # Check scanlines shader
    scanlines_path = os.path.join(shader_dir, 'scanlines.frag')
    if os.path.exists(scanlines_path):
        with open(scanlines_path, 'r') as f:
            content = f.read()
            if '#version 330' in content and 'void main()' in content:
                print("✓ Scanlines shader file is valid")
            else:
                print("✗ Scanlines shader file has syntax issues")
                tests_passed = False
    else:
        print("✗ Scanlines shader file not found")
        tests_passed = False
    
    # Check CRT shader
    crt_path = os.path.join(shader_dir, 'crt.frag')
    if os.path.exists(crt_path):
        with open(crt_path, 'r') as f:
            content = f.read()
            if '#version 330' in content and 'void main()' in content:
                print("✓ CRT shader file is valid")
            else:
                print("✗ CRT shader file has syntax issues")
                tests_passed = False
    else:
        print("✗ CRT shader file not found")
        tests_passed = False
    
    # Check VHS shader
    vhs_path = os.path.join(shader_dir, 'vhs.frag')
    if os.path.exists(vhs_path):
        with open(vhs_path, 'r') as f:
            content = f.read()
            if '#version 330' in content and 'void main()' in content:
                print("✓ VHS shader file is valid")
            else:
                print("✗ VHS shader file has syntax issues")
                tests_passed = False
    else:
        print("✗ VHS shader file not found")
        tests_passed = False
    
    # Check that they have the required uniforms
    with open(scanlines_path, 'r') as f:
        content = f.read()
        has_tex = 'uniform sampler2D tex' in content
        has_time = 'uniform float time' in content
        has_resolution = 'uniform vec2 resolution' in content
        if has_tex and has_time and has_resolution:
            print("✓ Scanlines shader has required uniforms")
        else:
            print("✗ Scanlines shader missing required uniforms")
            if not has_tex:
                print("  - Missing: uniform sampler2D tex")
            if not has_time:
                print("  - Missing: uniform float time")
            if not has_resolution:
                print("  - Missing: uniform vec2 resolution")
            tests_passed = False
    
    with open(crt_path, 'r') as f:
        content = f.read()
        has_tex = 'uniform sampler2D tex' in content
        has_time = 'uniform float time' in content
        has_resolution = 'uniform vec2 resolution' in content
        if has_tex and has_time and has_resolution:
            print("✓ CRT shader has required uniforms")
        else:
            print("✗ CRT shader missing required uniforms")
            if not has_tex:
                print("  - Missing: uniform sampler2D tex")
            if not has_time:
                print("  - Missing: uniform float time")
            if not has_resolution:
                print("  - Missing: uniform vec2 resolution")
            tests_passed = False
    
    with open(vhs_path, 'r') as f:
        content = f.read()
        has_tex = 'uniform sampler2D tex' in content
        has_time = 'uniform float time' in content
        has_resolution = 'uniform vec2 resolution' in content
        if has_tex and has_time and has_resolution:
            print("✓ VHS shader has required uniforms")
        else:
            print("✗ VHS shader missing required uniforms")
            if not has_tex:
                print("  - Missing: uniform sampler2D tex")
            if not has_time:
                print("  - Missing: uniform float time")
            if not has_resolution:
                print("  - Missing: uniform vec2 resolution")
            tests_passed = False
    
    return tests_passed

def test_constants_updated():
    """Test that constants file has post effect type setting"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        from src.utils.constants import POST_EFFECT_TYPE
        print(f"✓ POST_EFFECT_TYPE constant found: {POST_EFFECT_TYPE}")
        if POST_EFFECT_TYPE in ["none", "scanlines", "crt", "vhs"]:
            print(f"✓ POST_EFFECT_TYPE has valid value")
            return True
        else:
            print(f"✗ POST_EFFECT_TYPE has invalid value")
            return False
    except ImportError as e:
        print(f"✗ Failed to import POST_EFFECT_TYPE: {e}")
        return False

def test_post_processor_integration():
    """Test that PostProcessor has been updated to support style effects"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        # Read the post_process.py file to check for new methods
        post_process_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'rendering', 'post_process.py')
        with open(post_process_path, 'r') as f:
            content = f.read()
            
        has_style_effect_method = 'def apply_style_effect' in content
        has_update_time = 'def update_time' in content
        has_post_effect_import = 'POST_EFFECT_TYPE' in content
        
        if has_style_effect_method:
            print("✓ PostProcessor has apply_style_effect method")
        else:
            print("✗ PostProcessor missing apply_style_effect method")
            
        if has_update_time:
            print("✓ PostProcessor has update_time method")
        else:
            print("✗ PostProcessor missing update_time method")
            
        if has_post_effect_import:
            print("✓ PostProcessor imports POST_EFFECT_TYPE")
        else:
            print("✗ PostProcessor doesn't import POST_EFFECT_TYPE")
        
        return has_style_effect_method and has_update_time and has_post_effect_import
    except Exception as e:
        print(f"✗ Failed to check PostProcessor integration: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Post-Processing Style Effects Test")
    print("=" * 60)
    print()
    
    test1 = test_shader_syntax()
    print()
    test2 = test_constants_updated()
    print()
    test3 = test_post_processor_integration()
    
    print()
    print("=" * 60)
    if test1 and test2 and test3:
        print("✓ All tests PASSED!")
        print()
        print("Post-processing style effects are ready to use.")
        print()
        print("Available effects:")
        print("  - none: No effect (default)")
        print("  - scanlines: Horizontal scanlines effect")
        print("  - crt: CRT monitor effect with curvature and scanlines")
        print("  - vhs: VHS tape effect with distortion and noise")
        print()
        print("To enable an effect, set POST_EFFECT_TYPE in constants.py")
        sys.exit(0)
    else:
        print("✗ Some tests FAILED!")
        sys.exit(1)
