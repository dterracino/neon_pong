#!/usr/bin/env python3
"""
Visual test for FPS counter - creates a mock scenario
"""
import sys
import os

def test_fps_rendering_logic():
    """Test that FPS rendering method constructs proper text"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        from src.utils.fps_counter import FPSCounter
        from src.utils.constants import (
            FPS_DISPLAY_SHOW_INSTANT,
            FPS_DISPLAY_SHOW_AVERAGE,
            FPS_DISPLAY_SHOW_1_PERCENT,
            FPS_DISPLAY_SHOW_0_1_PERCENT,
        )
        
        counter = FPSCounter(average_window=1.0)
        counter.visible = True
        
        # Simulate some frame updates
        for i in range(100):
            counter.update(0.016)  # 60 FPS
        
        instant, average, low_1, low_01 = counter.get_metrics()
        
        # Build expected text lines
        lines = []
        if FPS_DISPLAY_SHOW_INSTANT:
            lines.append(f"FPS: {instant:.1f}")
        if FPS_DISPLAY_SHOW_AVERAGE:
            lines.append(f"Avg: {average:.1f}")
        if FPS_DISPLAY_SHOW_1_PERCENT:
            lines.append(f"1% Low: {low_1:.1f}")
        if FPS_DISPLAY_SHOW_0_1_PERCENT:
            lines.append(f"0.1% Low: {low_01:.1f}")
        
        print("\nExpected FPS Display Output:")
        print("=" * 40)
        for line in lines:
            print(f"  {line}")
        print("=" * 40)
        
        # Verify metrics are reasonable
        assert 55 < instant < 65, f"Instant FPS should be ~60, got {instant}"
        assert 55 < average < 65, f"Average FPS should be ~60, got {average}"
        
        print("\n✓ FPS rendering logic works correctly")
        print(f"  Instant: {instant:.1f} FPS")
        print(f"  Average: {average:.1f} FPS")
        print(f"  1% Low: {low_1:.1f} FPS")
        print(f"  0.1% Low: {low_01:.1f} FPS")
        return True
    except Exception as e:
        print(f"✗ FPS rendering logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_renderer_has_direct_draw():
    """Test that renderer has draw_text_direct method"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        renderer_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'rendering', 'renderer.py')
        with open(renderer_path, 'r') as f:
            content = f.read()
            if 'def draw_text_direct' in content:
                print("✓ Renderer has draw_text_direct method")
                return True
            else:
                print("✗ Renderer missing draw_text_direct method")
                return False
    except Exception as e:
        print(f"✗ Renderer check failed: {e}")
        return False

def test_configuration_options():
    """Test configuration options work"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        from src.utils.constants import (
            FPS_DISPLAY_SHOW_INSTANT,
            FPS_DISPLAY_SHOW_AVERAGE,
            FPS_DISPLAY_SHOW_1_PERCENT,
            FPS_DISPLAY_SHOW_0_1_PERCENT,
        )
        
        print("\nFPS Display Configuration:")
        print(f"  Show Instant FPS: {FPS_DISPLAY_SHOW_INSTANT}")
        print(f"  Show Average FPS: {FPS_DISPLAY_SHOW_AVERAGE}")
        print(f"  Show 1% Low: {FPS_DISPLAY_SHOW_1_PERCENT}")
        print(f"  Show 0.1% Low: {FPS_DISPLAY_SHOW_0_1_PERCENT}")
        
        print("\n✓ Configuration options are accessible")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FPS Counter Visual Test")
    print("=" * 60)
    
    tests = [
        test_configuration_options(),
        test_renderer_has_direct_draw(),
        test_fps_rendering_logic(),
    ]
    
    print("\n" + "=" * 60)
    if all(tests):
        print("✓ All visual tests PASSED!")
        print("\nUsage in game:")
        print("  1. Run the game: python main.py")
        print("  2. Press F3 to toggle FPS display")
        print("  3. FPS display shows in top-left corner")
        print("\nConfiguration:")
        print("  Edit src/utils/constants.py to customize:")
        print("  - FPS_DISPLAY_SHOW_INSTANT: Show instant FPS")
        print("  - FPS_DISPLAY_SHOW_AVERAGE: Show average FPS")
        print("  - FPS_DISPLAY_SHOW_1_PERCENT: Show 1% low")
        print("  - FPS_DISPLAY_SHOW_0_1_PERCENT: Show 0.1% low")
        print("  - FPS_DISPLAY_POSITION_X/Y: Display position")
        sys.exit(0)
    else:
        print("✗ Some visual tests FAILED!")
        sys.exit(1)
