"""
Simple Integration Test (no dependencies required)

Tests core components without requiring pytest
"""

import sys
sys.path.insert(0, '.')

from src.clients.grok import GrokClient, MODEL_IDS


def test_model_id_mapping():
    """Test that model ID mapping works correctly"""
    print("Testing model ID mapping...")
    assert MODEL_IDS["grok-4"] == "grok-4-0709", "grok-4 should map to grok-4-0709"
    assert MODEL_IDS["grok-3"] == "grok-3", "grok-3 should map to grok-3"
    assert MODEL_IDS["grok-vision"] == "grok-2-vision-1212", "grok-vision should map to grok-2-vision-1212"
    print("✓ Model ID mapping correct")


def test_model_resolution():
    """Test model ID resolution"""
    print("\nTesting model resolution...")
    client = GrokClient(api_key="test-key", model="grok-4")

    # Test known models
    assert client._resolve_model("grok-4") == "grok-4-0709"
    assert client._resolve_model("grok-3") == "grok-3"
    assert client._resolve_model("grok-vision") == "grok-2-vision-1212"

    # Test already-resolved model
    assert client._resolve_model("grok-4-0709") == "grok-4-0709"

    print("✓ Model resolution works correctly")


if __name__ == "__main__":
    print("=" * 60)
    print("AI Dialogue - Quick Integration Test")
    print("=" * 60)

    try:
        test_model_id_mapping()
        test_model_resolution()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nCore components are working correctly:")
        print("  ✓ GrokClient model ID mapping")
        print("  ✓ Model resolution logic")
        print("  ✓ Client initialization")
        print("\nNext step: Run with XAI_API_KEY to test API connection")
        sys.exit(0)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
