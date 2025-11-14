#!/usr/bin/env python3
"""Detailed API diagnostic test"""

import asyncio
import os
from langchain_openai import ChatOpenAI

async def test_direct_langchain():
    """Test LangChain directly to isolate the issue"""

    # Get API key from environment variable
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("❌ ERROR: XAI_API_KEY environment variable not set")
        print("   Usage: export XAI_API_KEY='your-key-here'")
        return False

    keys = [api_key]

    # Official models from docs.x.ai/docs/models
    models_to_test = [
        "grok-4-fast-reasoning-latest",  # Recommended reasoning model
        "grok-code-fast-1",              # Code-specialized
        "grok-4-fast-non-reasoning-latest"  # Faster, simpler tasks
    ]

    for idx, api_key in enumerate(keys, 1):
        print(f"\n{'='*60}")
        print(f"Testing API Key #{idx}: {api_key[:15]}...{api_key[-10:]}")
        print(f"{'='*60}\n")

        for model in models_to_test:
            print(f"🎯 Testing model: {model}")
            try:
                client = ChatOpenAI(
                    api_key=api_key,
                    base_url="https://api.x.ai/v1",
                    model=model,
                    temperature=0.7
                )

                response = await client.ainvoke("Say 'Hello from xAI!'")
                print(f"✅ SUCCESS with {model}")
                print(f"   Response: {response.content[:100]}")

                if hasattr(response, 'response_metadata'):
                    print(f"   Metadata: {response.response_metadata}")
                print()
                return True  # Success, no need to continue

            except Exception as e:
                print(f"❌ FAILED with {model}")
                print(f"   Error type: {type(e).__name__}")
                print(f"   Error message: {str(e)}")

                # Try to get more details
                if hasattr(e, '__cause__'):
                    print(f"   Cause: {e.__cause__}")
                if hasattr(e, 'response'):
                    print(f"   Response: {e.response}")
                print()

    print("\n⚠️  All tests failed. Possible issues:")
    print("   1. Billing credits not yet activated (wait 5-10 min)")
    print("   2. API keys need to be regenerated after billing setup")
    print("   3. Model names might not match actual API")
    print("   4. Regional restrictions or account issues")

    return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_langchain())
    exit(0 if success else 1)
