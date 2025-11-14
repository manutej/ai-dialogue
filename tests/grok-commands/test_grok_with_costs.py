#!/usr/bin/env python3
"""
Grok Commands - Comprehensive Test Suite with Cost Tracking
Tests the underlying Python functionality used by /grok commands
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.clients.grok import GrokClient, MODEL_IDS
from src.adapters.grok_adapter import GrokAdapter


class CostTracker:
    """Track API costs across multiple test runs"""

    def __init__(self, cost_per_1k_tokens=0.02):
        """
        Initialize cost tracker

        Args:
            cost_per_1k_tokens: Cost per 1000 tokens (adjust based on actual pricing)
        """
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.tests = []
        self.total_tokens = 0
        self.total_cost = 0.0

    def record(self, test_name, tokens, response_length):
        """Record a test result"""
        cost = (tokens['total'] / 1000) * self.cost_per_1k_tokens
        self.tests.append({
            'name': test_name,
            'tokens': tokens,
            'cost': cost,
            'response_length': response_length
        })
        self.total_tokens += tokens['total']
        self.total_cost += cost

    def print_summary(self):
        """Print cost summary"""
        print()
        print("=" * 70)
        print("COST SUMMARY")
        print("=" * 70)
        print()

        for i, test in enumerate(self.tests, 1):
            print(f"{i}. {test['name']}")
            print(f"   Prompt: {test['tokens']['prompt']:,} tokens")
            print(f"   Completion: {test['tokens']['completion']:,} tokens")
            print(f"   Total: {test['tokens']['total']:,} tokens")
            print(f"   Response: {test['response_length']:,} chars")
            print(f"   Cost: ${test['cost']:.6f}")
            print()

        print("-" * 70)
        print(f"Total Tokens: {self.total_tokens:,}")
        print(f"Total Cost: ${self.total_cost:.6f}")
        print(f"Average Cost per Test: ${self.total_cost / len(self.tests):.6f}")
        print("=" * 70)


async def test_suite():
    """Run comprehensive test suite"""

    print("🧪 Grok Commands - Comprehensive Test Suite")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Initialize cost tracker
    tracker = CostTracker(cost_per_1k_tokens=0.02)  # Adjust based on actual pricing

    # Test counters
    passed = 0
    failed = 0

    # =========================================================================
    # TEST SUITE A: Model Information
    # =========================================================================

    print("─" * 70)
    print("TEST SUITE A: Model Information")
    print("─" * 70)
    print()

    # A1: List available models
    print("A1: List Available Models")
    try:
        models = list(MODEL_IDS.keys())
        print(f"✓ Found {len(models)} models:")
        for model in models[:5]:  # Show first 5
            print(f"   - {model}")
        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # =========================================================================
    # TEST SUITE B: Basic Queries
    # =========================================================================

    print("─" * 70)
    print("TEST SUITE B: Basic Queries with Cost Tracking")
    print("─" * 70)
    print()

    client = GrokClient()

    # B1: Simple math query
    print("B1: Simple Math Query (What is 2+2?)")
    try:
        response, tokens = await client.chat("What is 2+2? Answer with just the number.")
        print(f"Response: {response}")
        tracker.record("Simple math query", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # B2: Short factual query
    print("B2: Short Factual Query (Capital of France)")
    try:
        response, tokens = await client.chat("What is the capital of France? Answer in one word.")
        print(f"Response: {response}")
        tracker.record("Capital query", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # B3: Code generation query
    print("B3: Code Generation Query (Python hello world)")
    try:
        response, tokens = await client.chat(
            "Write a Python hello world function. Be concise."
        )
        print(f"Response length: {len(response)} chars")
        print(f"Response preview: {response[:100]}...")
        tracker.record("Code generation", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # =========================================================================
    # TEST SUITE C: Model Variations
    # =========================================================================

    print("─" * 70)
    print("TEST SUITE C: Different Models with Cost Comparison")
    print("─" * 70)
    print()

    test_prompt = "Explain async/await in one sentence."

    # C1: Default model (grok-4-fast-reasoning)
    print("C1: Default Model (grok-4-fast-reasoning)")
    try:
        client_default = GrokClient(model="grok-4-fast-reasoning")
        response, tokens = await client_default.chat(test_prompt)
        print(f"Response: {response[:150]}...")
        tracker.record("Default model", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        await client_default.close()
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # C2: Code model
    print("C2: Code Model (grok-code-fast-1)")
    try:
        client_code = GrokClient(model="grok-code-fast-1")
        response, tokens = await client_code.chat(test_prompt)
        print(f"Response: {response[:150]}...")
        tracker.record("Code model", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        await client_code.close()
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # =========================================================================
    # TEST SUITE D: Parameter Variations
    # =========================================================================

    print("─" * 70)
    print("TEST SUITE D: Temperature & Max Tokens Impact on Cost")
    print("─" * 70)
    print()

    # D1: Low temperature (more focused)
    print("D1: Low Temperature (0.3) - More Focused Response")
    try:
        response, tokens = await client.chat(
            "Explain REST APIs briefly.",
            temperature=0.3,
            max_tokens=100
        )
        print(f"Response: {response[:150]}...")
        tracker.record("Low temp (0.3)", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # D2: High temperature (more creative)
    print("D2: High Temperature (1.2) - More Creative Response")
    try:
        response, tokens = await client.chat(
            "Explain REST APIs briefly.",
            temperature=1.2,
            max_tokens=100
        )
        print(f"Response: {response[:150]}...")
        tracker.record("High temp (1.2)", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # D3: Max tokens constraint
    print("D3: Max Tokens Constraint (50 tokens)")
    try:
        response, tokens = await client.chat(
            "Write a detailed explanation of microservices architecture.",
            max_tokens=50
        )
        print(f"Response: {response}")
        tracker.record("Max tokens 50", tokens, len(response))
        print(f"📊 Tokens: {tokens['total']} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()

    # =========================================================================
    # TEST SUITE E: Adapter Testing
    # =========================================================================

    print("─" * 70)
    print("TEST SUITE E: Grok Adapter (Used by /grok commands)")
    print("─" * 70)
    print()

    # E1: Adapter basic query
    print("E1: Adapter Basic Query")
    try:
        adapter = GrokAdapter()
        response, tokens = await adapter.chat(
            prompt="What is Docker? One sentence."
        )
        print(f"Response: {response}")
        # Convert dataclass to dict for tracker
        tokens_dict = {
            'prompt': tokens.prompt,
            'completion': tokens.completion,
            'total': tokens.total
        }
        tracker.record("Adapter query", tokens_dict, len(response))
        print(f"📊 Tokens: {tokens.total} | Cost: ${tracker.tests[-1]['cost']:.6f}")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        failed += 1
    print()

    # Close client
    await client.close()

    # =========================================================================
    # SUMMARY
    # =========================================================================

    print()
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")

    # Print cost summary
    tracker.print_summary()

    print()
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    return passed, failed, tracker


if __name__ == "__main__":
    try:
        passed, failed, tracker = asyncio.run(test_suite())

        # Exit with appropriate code
        sys.exit(0 if failed == 0 else 1)

    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
