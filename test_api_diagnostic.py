#!/usr/bin/env python3
"""Comprehensive API diagnostic"""

import requests
import json

def test_api_comprehensive():
    """Test API with detailed diagnostics"""

    import os
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("❌ ERROR: XAI_API_KEY environment variable not set")
        print("   Usage: export XAI_API_KEY='your-key-here'")
        return

    print("=" * 70)
    print("xAI API Comprehensive Diagnostic")
    print("=" * 70)

    # Test 1: Check if API endpoint is reachable
    print("\n1. Testing API endpoint reachability...")
    try:
        response = requests.get("https://api.x.ai/", timeout=10)
        print(f"   ✅ Endpoint reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Endpoint not reachable: {e}")

    # Test 2: Try to list models (if endpoint exists)
    print("\n2. Attempting to list available models...")
    try:
        response = requests.get(
            "https://api.x.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Models: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Simple chat completion with minimal payload
    print("\n3. Testing minimal chat completion...")
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": "Hi"}]
            },
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 200:
            print(f"   ✅ SUCCESS!")
            data = response.json()
            print(f"   Message: {data['choices'][0]['message']['content']}")
        else:
            print(f"   ❌ FAILED")
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass

    except Exception as e:
        print(f"   ❌ Exception: {e}")

    # Test 4: Check headers in response
    print("\n4. Checking response headers...")
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": "Hi"}]
            },
            timeout=30
        )
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("=" * 70)
    print("If all tests return 403, the API key does not have access.")
    print("Possible reasons:")
    print("1. Billing not set up or not active")
    print("2. API key created before billing was activated")
    print("3. Account requires verification or approval")
    print("4. API access not enabled for this account")
    print("\nAction: Check console.x.ai for account status and billing")
    print("=" * 70)

if __name__ == "__main__":
    test_api_comprehensive()
