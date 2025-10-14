#!/usr/bin/env python3
"""
Test the FPS counter implementation
"""
import sys
import os

def test_fps_counter_imports():
    """Test that FPS counter can be imported"""
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from src.utils.fps_counter import FPSCounter
        print("✓ FPSCounter imports successfully")
        return True
    except Exception as e:
        print(f"✗ FPSCounter import failed: {e}")
        return False

def test_fps_counter_basic():
    """Test basic FPS counter functionality"""
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from src.utils.fps_counter import FPSCounter
        
        counter = FPSCounter(average_window=1.0)
        
        # Test initial state
        assert not counter.is_visible(), "Counter should start invisible"
        
        # Test toggle
        counter.toggle_visibility()
        assert counter.is_visible(), "Counter should be visible after toggle"
        
        counter.toggle_visibility()
        assert not counter.is_visible(), "Counter should be invisible after second toggle"
        
        # Test update with frame time
        counter.update(0.016)  # ~60 FPS
        instant, average, low_1, low_01 = counter.get_metrics()
        
        # Instant FPS should be around 60 (1/0.016)
        assert 55 < instant < 65, f"Instant FPS should be ~60, got {instant}"
        
        print("✓ FPSCounter basic functionality works")
        return True
    except Exception as e:
        print(f"✗ FPSCounter basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fps_constants():
    """Test that FPS display constants are defined"""
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from src.utils.constants import (
            FPS_DISPLAY_SHOW_INSTANT,
            FPS_DISPLAY_SHOW_AVERAGE,
            FPS_DISPLAY_SHOW_1_PERCENT,
            FPS_DISPLAY_SHOW_0_1_PERCENT,
            FPS_DISPLAY_AVERAGE_WINDOW,
            FPS_DISPLAY_POSITION_X,
            FPS_DISPLAY_POSITION_Y
        )
        print("✓ FPS display constants are defined")
        return True
    except Exception as e:
        print(f"✗ FPS constants import failed: {e}")
        return False

def test_game_integration():
    """Test that Game class has FPS counter integration"""
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        game_path = os.path.join(os.path.dirname(__file__), 'src', 'game.py')
        with open(game_path, 'r') as f:
            content = f.read()
            checks = [
                ('from src.utils.fps_counter import FPSCounter' in content, "FPSCounter import"),
                ('self.fps_counter = FPSCounter' in content, "FPS counter initialization"),
                ('self.fps_counter.update' in content, "FPS counter update call"),
                ('self.fps_counter.is_visible' in content, "FPS visibility check"),
                ('self.fps_counter.toggle_visibility' in content, "FPS toggle call"),
                ('K_F3' in content, "F3 key handler"),
                ('_render_fps_display' in content, "FPS render method"),
            ]
            
            all_passed = True
            for check, name in checks:
                if check:
                    print(f"✓ Game has {name}")
                else:
                    print(f"✗ Game missing {name}")
                    all_passed = False
            
            return all_passed
    except Exception as e:
        print(f"✗ Game integration test failed: {e}")
        return False

def test_fps_percentile_calculation():
    """Test that percentile calculations work correctly"""
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from src.utils.fps_counter import FPSCounter
        
        counter = FPSCounter(average_window=10.0)
        
        # Add many frame times to build up statistics
        # Simulate mostly 60 FPS with some drops
        for i in range(100):
            if i % 20 == 0:
                # Simulate frame drops (30 FPS)
                counter.update(0.033)
            else:
                # Normal 60 FPS
                counter.update(0.016)
        
        instant, average, low_1, low_01 = counter.get_metrics()
        
        # Average should be between the good and bad frame rates
        assert 45 < average < 65, f"Average FPS should be reasonable, got {average}"
        
        # 1% low should be lower than average (capturing the drops)
        assert low_1 < average, f"1% low ({low_1}) should be less than average ({average})"
        
        print("✓ FPSCounter percentile calculations work")
        return True
    except Exception as e:
        print(f"✗ FPSCounter percentile test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FPS Counter Test")
    print("=" * 60)
    print()
    
    tests = [
        test_fps_constants(),
        test_fps_counter_imports(),
        test_fps_counter_basic(),
        test_fps_percentile_calculation(),
        test_game_integration(),
    ]
    
    print()
    print("=" * 60)
    if all(tests):
        print("✓ All FPS counter tests PASSED!")
        print()
        print("The FPS counter is properly implemented and integrated.")
        print("Press F3 in-game to toggle the FPS display.")
        sys.exit(0)
    else:
        print("✗ Some FPS counter tests FAILED!")
        sys.exit(1)
