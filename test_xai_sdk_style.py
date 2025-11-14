#!/usr/bin/env python3
"""Test using OpenAI-compatible client (like xai_sdk)"""

import asyncio
from openai import AsyncOpenAI

async def test_with_openai_client():
    """Test using OpenAI client configured for xAI"""

    import os
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("❌ ERROR: XAI_API_KEY environment variable not set")
        print("   Usage: export XAI_API_KEY='your-key-here'")
        return False

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
        timeout=60.0
    )

    models_to_test = [
        "grok-3-mini",
        "grok-4-latest",
        "grok-4-fast-reasoning-latest"
    ]

    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing model: {model}")
        print(f"{'='*60}")

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Say 'Hello World' and nothing else."}
                ],
                temperature=0
            )

            print(f"✅ SUCCESS!")
            print(f"Response: {response.choices[0].message.content}")
            print(f"Usage: {response.usage}")
            return True

        except Exception as e:
            print(f"❌ FAILED: {type(e).__name__}")
            print(f"   Error: {str(e)}")
            if hasattr(e, 'response'):
                print(f"   Status: {e.response.status_code if hasattr(e.response, 'status_code') else 'unknown'}")

    return False

if __name__ == "__main__":
    success = asyncio.run(test_with_openai_client())
    exit(0 if success else 1)
