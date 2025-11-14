#!/usr/bin/env python3
"""Test GrokAdapter with live API call after billing setup"""

import asyncio
import os
from src.adapters.grok_adapter import GrokAdapter

async def test_live_api():
    """Test real API call with billing-enabled key"""

    # Use API key from environment variable
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("❌ ERROR: XAI_API_KEY environment variable not set")
        print("   Usage: export XAI_API_KEY='your-key-here'")
        return False

    print("🔧 Initializing GrokAdapter with grok-2-latest...")
    adapter = GrokAdapter(
        api_key=api_key,
        model="grok-2",  # Uses grok-2-latest per MODEL_IDS mapping
        temperature=0.7
    )

    print(f"📋 Adapter capabilities: {adapter.capabilities}")
    print(f"🎯 Resolved model: {adapter.resolved_model}")
    print(f"🌐 Base URL: https://api.x.ai/v1")
    print()

    print("🚀 Sending test prompt to Grok API...")
    test_prompt = "Respond with exactly: 'Hello from Grok! Billing is active.'"

    try:
        response, usage = await adapter.chat(test_prompt)

        print("✅ SUCCESS! API call completed.")
        print(f"\n📨 Response:\n{response}\n")
        print(f"📊 Token Usage:")
        print(f"   - Prompt tokens: {usage.prompt}")
        print(f"   - Completion tokens: {usage.completion}")
        print(f"   - Total tokens: {usage.total}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_live_api())
    exit(0 if success else 1)
