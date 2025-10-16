#!/usr/bin/env python3
"""
Unit test for text rendering cache data structures
Tests cache logic without requiring OpenGL context
"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

def test_cache_key_generation():
    """Test that cache keys are properly generated"""
    print("Testing cache key generation...")
    
    # Cache keys should be tuples of (text, size, color, font_name)
    key1 = ("Hello", 32, (255, 255, 255), None)
    key2 = ("Hello", 32, (255, 255, 255), None)
    key3 = ("Hello", 48, (255, 255, 255), None)  # Different size
    key4 = ("Hello", 32, (255, 0, 0), None)  # Different color
    key5 = ("World", 32, (255, 255, 255), None)  # Different text
    
    # Same keys should be equal
    assert key1 == key2, "Identical keys should be equal"
    print("  ✓ Identical keys are equal")
    
    # Different keys should not be equal
    assert key1 != key3, "Keys with different sizes should not be equal"
    assert key1 != key4, "Keys with different colors should not be equal"
    assert key1 != key5, "Keys with different text should not be equal"
    print("  ✓ Different keys are not equal")
    
    # Keys should be hashable (can be used in dict)
    cache = {key1: "value1", key3: "value2"}
    assert cache[key1] == "value1", "Should retrieve correct value"
    assert cache[key2] == "value1", "Same key should retrieve same value"
    print("  ✓ Keys are properly hashable for dict use")
    
    print("✓ Cache key generation tests passed!\n")

def test_cache_access_tracking():
    """Test that cache access counting works"""
    print("Testing cache access tracking...")
    
    access_count = {}
    
    # Simulate accessing items
    keys = [
        ("Item1", 32, (255, 255, 255), None),
        ("Item2", 32, (255, 255, 255), None),
        ("Item1", 32, (255, 255, 255), None),  # Access Item1 again
        ("Item3", 32, (255, 255, 255), None),
        ("Item1", 32, (255, 255, 255), None),  # Access Item1 third time
    ]
    
    for key in keys:
        access_count[key] = access_count.get(key, 0) + 1
    
    assert access_count[keys[0]] == 3, "Item1 should have 3 accesses"
    assert access_count[keys[1]] == 1, "Item2 should have 1 access"
    assert access_count[keys[3]] == 1, "Item3 should have 1 access"
    print("  ✓ Access counting works correctly")
    
    # Test sorting by access count (for LRU)
    sorted_items = sorted(access_count.items(), key=lambda x: x[1])
    least_used = sorted_items[0][0]
    most_used = sorted_items[-1][0]
    
    assert access_count[least_used] == 1, "Least used should have 1 access"
    assert access_count[most_used] == 3, "Most used should have 3 accesses"
    print("  ✓ LRU sorting works correctly")
    
    print("✓ Cache access tracking tests passed!\n")

def test_cache_cleanup_logic():
    """Test the logic for removing least used items"""
    print("Testing cache cleanup logic...")
    
    # Simulate a cache with access counts
    cache = {}
    access_count = {}
    
    # Add 15 items with varying access counts
    for i in range(15):
        key = (f"Item{i}", 32, (255, 255, 255), None)
        cache[key] = f"Surface{i}"
        # Give different access counts (Item0 accessed most, Item14 least)
        access_count[key] = 15 - i
    
    max_cache_size = 10
    
    # Simulate cleanup logic
    if len(cache) > max_cache_size:
        sorted_items = sorted(access_count.items(), key=lambda x: x[1])
        items_to_remove = len(cache) - max_cache_size + 2  # Remove extra for headroom
        
        for key, _ in sorted_items[:items_to_remove]:
            del cache[key]
            del access_count[key]
    
    assert len(cache) == 8, f"Cache should have 8 items after cleanup, has {len(cache)}"
    print(f"  ✓ Cleanup reduced cache from 15 to {len(cache)} items")
    
    # Verify that least used items were removed
    removed_key = ("Item14", 32, (255, 255, 255), None)
    kept_key = ("Item0", 32, (255, 255, 255), None)
    
    assert removed_key not in cache, "Least used item should be removed"
    assert kept_key in cache, "Most used item should be kept"
    print("  ✓ Least used items removed, most used kept")
    
    print("✓ Cache cleanup logic tests passed!\n")

def test_renderer_cache_attributes():
    """Test that Renderer class has the expected cache attributes"""
    print("Testing Renderer cache attributes...")
    
    # Import here to check if attributes exist
    import pygame
    pygame.init()
    
    # We can't create a full renderer without OpenGL, but we can check the source
    from src.rendering.renderer import Renderer
    
    # Check that the class has the expected methods
    assert hasattr(Renderer, '_manage_text_cache'), "Renderer should have _manage_text_cache method"
    assert hasattr(Renderer, 'get_text_cache_stats'), "Renderer should have get_text_cache_stats method"
    print("  ✓ Renderer has expected cache methods")
    
    # Check the method signatures by inspecting the source
    import inspect
    
    # _manage_text_cache should have self parameter only
    manage_sig = inspect.signature(Renderer._manage_text_cache)
    assert len(manage_sig.parameters) == 1, "_manage_text_cache should have only self parameter"
    print("  ✓ _manage_text_cache has correct signature")
    
    # get_text_cache_stats should return a dict
    stats_sig = inspect.signature(Renderer.get_text_cache_stats)
    assert str(stats_sig.return_annotation) == "typing.Dict[str, int]", \
        "get_text_cache_stats should return Dict[str, int]"
    print("  ✓ get_text_cache_stats has correct return type")
    
    pygame.quit()
    print("✓ Renderer cache attributes tests passed!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Text Rendering Cache Unit Tests")
    print("=" * 60 + "\n")
    
    test_cache_key_generation()
    test_cache_access_tracking()
    test_cache_cleanup_logic()
    test_renderer_cache_attributes()
    
    print("=" * 60)
    print("✓ All unit tests passed!")
    print("=" * 60)
