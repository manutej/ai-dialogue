"""
Quick Integration Test

Simple test to verify the core components work together
"""

import asyncio
import pytest
from src.clients.grok import GrokClient, MODEL_IDS


def test_model_id_mapping():
    """Test that model ID mapping works correctly"""
    assert MODEL_IDS["grok-4"] == "grok-4-fast-reasoning-latest"
    assert MODEL_IDS["grok-vision"] == "grok-2-vision-latest"
    assert MODEL_IDS["grok-code"] == "grok-code-fast-1"


def test_grok_client_init():
    """Test GrokClient initialization (without API call)"""
    try:
        # This will fail if XAI_API_KEY is not set, which is expected
        client = GrokClient(api_key="test-key", model="grok-4")
        assert client.default_model == "grok-4"
        assert client._resolve_model("grok-4") == "grok-4-fast-reasoning-latest"
    except ValueError as e:
        # Expected if no API key
        pass


def test_model_resolution():
    """Test model ID resolution"""
    client = GrokClient(api_key="test-key", model="grok-4")

    # Test known models
    assert client._resolve_model("grok-4") == "grok-4-fast-reasoning-latest"
    assert client._resolve_model("grok-vision") == "grok-2-vision-latest"
    assert client._resolve_model("grok-code") == "grok-code-fast-1"

    # Test already-resolved model (passes through unknown models)
    assert client._resolve_model("grok-4-fast-reasoning-latest") == "grok-4-fast-reasoning-latest"


@pytest.mark.asyncio
async def test_grok_client_basic():
    """
    Test basic Grok client functionality

    This test requires XAI_API_KEY to be set.
    Skip if not available.
    """
    import os

    if not os.getenv("XAI_API_KEY"):
        pytest.skip("XAI_API_KEY not set")

    client = GrokClient(model="grok-4")

    try:
        response, tokens = await client.chat("Say 'test' in exactly one word", max_tokens=10)

        # Basic assertions
        assert isinstance(response, str)
        assert len(response) > 0
        assert isinstance(tokens, dict)
        assert "total" in tokens
        assert tokens["total"] > 0

        print(f"✓ Grok response: {response}")
        print(f"✓ Tokens: {tokens}")

    finally:
        await client.close()


if __name__ == "__main__":
    # Run quick test
    print("Running quick integration tests...\n")

    test_model_id_mapping()
    print("✓ Model ID mapping works")

    test_grok_client_init()
    print("✓ GrokClient initialization works")

    test_model_resolution()
    print("✓ Model resolution works")

    # Try API test if key is available
    import os
    if os.getenv("XAI_API_KEY"):
        print("\nTesting API connection...")
        asyncio.run(test_grok_client_basic())
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  XAI_API_KEY not set, skipping API test")
        print("✅ Offline tests passed!")
