#!/usr/bin/env python3
"""
Grok Commands - Advanced Features Test Suite
Tests orchestration modes, streaming, and specific use cases with cost tracking

Focus: Technical research/analysis (HKT and category theory)
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.clients.grok import GrokClient
from src.adapters.grok_adapter import GrokAdapter


class AdvancedCostTracker:
    """Track costs for advanced features including orchestration modes"""

    def __init__(self, cost_per_1k_tokens=0.02):
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.sessions = []
        self.total_tokens = 0
        self.total_cost = 0.0

    def record_session(self, session_name, turns_data, session_type="orchestration"):
        """Record a multi-turn orchestration session"""
        total_turns = len(turns_data)
        session_tokens = sum(turn['tokens']['total'] for turn in turns_data)
        session_cost = (session_tokens / 1000) * self.cost_per_1k_tokens

        self.sessions.append({
            'name': session_name,
            'type': session_type,
            'turns': total_turns,
            'turns_data': turns_data,
            'total_tokens': session_tokens,
            'cost': session_cost
        })

        self.total_tokens += session_tokens
        self.total_cost += session_cost

    def record_single(self, test_name, tokens, metadata=None):
        """Record a single test (like streaming)"""
        cost = (tokens['total'] / 1000) * self.cost_per_1k_tokens

        self.sessions.append({
            'name': test_name,
            'type': 'single',
            'turns': 1,
            'turns_data': [{'tokens': tokens, 'metadata': metadata or {}}],
            'total_tokens': tokens['total'],
            'cost': cost
        })

        self.total_tokens += tokens['total']
        self.total_cost += cost

    def print_summary(self):
        """Print comprehensive cost summary"""
        print()
        print("=" * 80)
        print("ADVANCED FEATURES - COST SUMMARY")
        print("=" * 80)
        print()

        # Group by type
        orchestration_sessions = [s for s in self.sessions if s['type'] == 'orchestration']
        single_tests = [s for s in self.sessions if s['type'] == 'single']

        # Orchestration sessions
        if orchestration_sessions:
            print("ORCHESTRATION MODES:")
            print("-" * 80)
            for session in orchestration_sessions:
                print(f"\n{session['name']}")
                print(f"  Turns: {session['turns']}")
                print(f"  Total tokens: {session['total_tokens']:,}")
                print(f"  Cost: ${session['cost']:.6f}")
                print(f"  Avg tokens/turn: {session['total_tokens'] // session['turns']:,}")
                print(f"  Avg cost/turn: ${session['cost'] / session['turns']:.6f}")

                # Show per-turn breakdown
                print(f"\n  Turn-by-turn breakdown:")
                for i, turn in enumerate(session['turns_data'], 1):
                    tokens = turn['tokens']
                    turn_cost = (tokens['total'] / 1000) * self.cost_per_1k_tokens
                    print(f"    Turn {i}: {tokens['total']:,} tokens (${turn_cost:.6f})")

        # Single tests
        if single_tests:
            print("\n" + "=" * 80)
            print("SINGLE TESTS (Streaming, etc.):")
            print("-" * 80)
            for test in single_tests:
                print(f"\n{test['name']}")
                print(f"  Tokens: {test['total_tokens']:,}")
                print(f"  Cost: ${test['cost']:.6f}")

        # Overall summary
        print("\n" + "=" * 80)
        print("OVERALL SUMMARY")
        print("-" * 80)
        print(f"Total Sessions: {len(self.sessions)}")
        print(f"Total Turns: {sum(s['turns'] for s in self.sessions)}")
        print(f"Total Tokens: {self.total_tokens:,}")
        print(f"Total Cost: ${self.total_cost:.6f}")
        print(f"Average Cost per Session: ${self.total_cost / len(self.sessions):.6f}")
        print("=" * 80)


async def simulate_loop_mode(topic: str, tracker: AdvancedCostTracker):
    """
    Simulate loop mode orchestration for technical research

    Loop mode: 8 turns of sequential knowledge building
    """
    print("=" * 80)
    print("ORCHESTRATION TEST: Loop Mode (8 turns)")
    print(f"Topic: {topic}")
    print("=" * 80)
    print()

    client = GrokClient()
    turns_data = []

    # Simplified prompts based on loop.json structure
    prompts = [
        # Turn 1: Foundation
        f"You are establishing foundational concepts for: {topic}\n\n"
        "Provide a comprehensive foundation covering:\n"
        "1. Core definitions and concepts\n"
        "2. Historical context\n"
        "3. Fundamental principles\n"
        "Keep it thorough but concise (2-3 paragraphs).",

        # Turn 2: Critical Analysis (using Turn 1 context)
        "Based on the foundation, provide critical analysis:\n"
        "1. Key assumptions and their validity\n"
        "2. Strengths and limitations\n"
        "3. Areas of uncertainty\n"
        "Be rigorous. (2-3 paragraphs)",

        # Turn 3: Practical Applications
        "Explore practical applications:\n"
        "1. Real-world use cases\n"
        "2. Tools and frameworks\n"
        "3. Implementation patterns\n"
        "Be specific. (2-3 paragraphs)",

        # Turn 4: Integration (shortened to save costs)
        "Synthesize the exploration:\n"
        "1. Key patterns\n"
        "2. Current consensus\n"
        "3. Open questions\n"
        "Provide integrated understanding. (2 paragraphs)",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"Turn {i}/{len(prompts)}: ", end="", flush=True)

        try:
            # Use lower max_tokens to control costs during testing
            response, tokens = await client.chat(
                prompt=prompt,
                temperature=0.7,
                max_tokens=300  # Limit for testing
            )

            turn_cost = (tokens['total'] / 1000) * tracker.cost_per_1k_tokens

            print(f"{tokens['total']:,} tokens (${turn_cost:.6f})")
            print(f"  Response preview: {response[:100]}...")
            print()

            turns_data.append({
                'turn': i,
                'prompt_length': len(prompt),
                'response_length': len(response),
                'tokens': tokens
            })

        except Exception as e:
            print(f"✗ FAILED: {e}")
            break

    await client.close()

    # Record session
    tracker.record_session("Loop Mode: HKT Research", turns_data, "orchestration")

    return len(turns_data) == len(prompts)


async def simulate_debate_mode(topic: str, tracker: AdvancedCostTracker):
    """
    Simulate debate mode for technical tradeoff analysis

    Debate mode: 6 turns of adversarial exploration
    """
    print("=" * 80)
    print("ORCHESTRATION TEST: Debate Mode (4 turns, shortened)")
    print(f"Topic: {topic}")
    print("=" * 80)
    print()

    client = GrokClient()
    turns_data = []

    # Shortened debate for cost control
    prompts = [
        # Turn 1: Proposition FOR
        f"Topic: {topic}\n\n"
        "Present a compelling argument FOR this approach:\n"
        "1. Core thesis\n"
        "2. Strongest supporting arguments (2-3 points)\n"
        "3. Key evidence\n"
        "Be persuasive. (2 paragraphs)",

        # Turn 2: Opposition AGAINST
        "Present counterarguments AGAINST the proposition:\n"
        "1. Core weaknesses\n"
        "2. Alternative perspectives\n"
        "3. Challenges to assumptions\n"
        "Be rigorous. (2 paragraphs)",

        # Turn 3: Synthesis
        "Synthesize both positions objectively:\n"
        "1. Strongest points on each side\n"
        "2. Common ground\n"
        "3. Key tradeoffs\n"
        "Be balanced. (2 paragraphs)",

        # Turn 4: Verdict
        "Render verdict:\n"
        "1. Which case is stronger?\n"
        "2. Recommended position\n"
        "3. Remaining uncertainties\n"
        "Be clear. (1-2 paragraphs)",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"Turn {i}/{len(prompts)}: ", end="", flush=True)

        try:
            response, tokens = await client.chat(
                prompt=prompt,
                temperature=0.8,  # Slightly higher for debate
                max_tokens=250
            )

            turn_cost = (tokens['total'] / 1000) * tracker.cost_per_1k_tokens

            print(f"{tokens['total']:,} tokens (${turn_cost:.6f})")
            print(f"  Response preview: {response[:100]}...")
            print()

            turns_data.append({
                'turn': i,
                'prompt_length': len(prompt),
                'response_length': len(response),
                'tokens': tokens
            })

        except Exception as e:
            print(f"✗ FAILED: {e}")
            break

    await client.close()

    tracker.record_session("Debate Mode: HKT Tradeoffs", turns_data, "orchestration")

    return len(turns_data) == len(prompts)


async def test_streaming(tracker: AdvancedCostTracker):
    """
    Test streaming responses for long-form content
    """
    print("=" * 80)
    print("STREAMING TEST: Long-form Technical Explanation")
    print("=" * 80)
    print()

    client = GrokClient()

    prompt = (
        "Explain Higher Kinded Types (HKT) in TypeScript and their relationship "
        "to category theory. Include practical examples with fp-ts. "
        "Be comprehensive and technical. (Aim for 500-600 words)"
    )

    print("Streaming response...")
    print("-" * 80)

    # Track streaming
    chunks_received = 0
    total_response = ""

    try:
        async for chunk in client.chat_stream(
            prompt=prompt,
            temperature=0.7,
            max_tokens=800
        ):
            print(chunk, end="", flush=True)
            chunks_received += 1
            total_response += chunk

        print()
        print("-" * 80)
        print(f"\nStreaming complete!")
        print(f"  Chunks received: {chunks_received}")
        print(f"  Response length: {len(total_response):,} chars")

        # For streaming, we don't get token usage directly
        # Estimate based on response length (rough: ~4 chars per token)
        estimated_tokens = {
            'prompt': len(prompt) // 4,  # Rough estimate
            'completion': len(total_response) // 4,
            'total': (len(prompt) + len(total_response)) // 4
        }

        print(f"  Estimated tokens: ~{estimated_tokens['total']:,}")

        tracker.record_single(
            "Streaming: HKT Explanation",
            estimated_tokens,
            {'chunks': chunks_received, 'is_estimate': True}
        )

        await client.close()
        return True

    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        await client.close()
        return False


async def test_specific_use_case(tracker: AdvancedCostTracker):
    """
    Test specific technical research use case:
    HKT research with fp-ts implementation examples
    """
    print("=" * 80)
    print("SPECIFIC USE CASE: HKT Implementation Research")
    print("=" * 80)
    print()

    client = GrokClient()
    turns_data = []

    # Multi-turn research scenario
    prompts = [
        # Turn 1: Conceptual foundation
        (
            "Explain the relationship between Higher Kinded Types (HKT) and "
            "category theory. What categorical concepts do HKTs represent? "
            "Be precise and technical. (2-3 paragraphs)"
        ),

        # Turn 2: TypeScript challenges
        (
            "Why doesn't TypeScript natively support HKTs? What are the technical "
            "limitations, and how does fp-ts work around them? "
            "Include brief code example. (2-3 paragraphs)"
        ),

        # Turn 3: Practical implementation
        (
            "Show a practical fp-ts example implementing a Functor for a custom "
            "data type using HKT encoding. Explain each part. "
            "(Code + explanation, ~200 words)"
        ),
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\nResearch Turn {i}/{len(prompts)}:")
        print(f"Query: {prompt[:80]}...")
        print("Response: ", end="", flush=True)

        try:
            response, tokens = await client.chat(
                prompt=prompt,
                model="grok-code-fast-1",  # Use code model for implementation
                temperature=0.6,  # Lower for code
                max_tokens=400
            )

            turn_cost = (tokens['total'] / 1000) * tracker.cost_per_1k_tokens

            print(f"{tokens['total']:,} tokens (${turn_cost:.6f})")
            print(f"Preview: {response[:150]}...")
            print()

            turns_data.append({
                'turn': i,
                'query': prompt,
                'response_length': len(response),
                'tokens': tokens
            })

        except Exception as e:
            print(f"✗ FAILED: {e}")
            break

    await client.close()

    tracker.record_session(
        "Use Case: HKT Research with fp-ts",
        turns_data,
        "orchestration"
    )

    return len(turns_data) == len(prompts)


async def advanced_test_suite():
    """Run advanced features test suite"""

    print("🧪 Grok Commands - Advanced Features Test Suite")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Focus: Technical Research (HKT & Category Theory)")
    print("=" * 80)
    print()

    tracker = AdvancedCostTracker(cost_per_1k_tokens=0.02)

    results = {
        'passed': 0,
        'failed': 0
    }

    # Test 1: Loop Mode
    print("\n" + "━" * 80)
    print("TEST 1: Loop Mode Orchestration")
    print("━" * 80)
    topic = "Higher Kinded Types (HKT) in relation to category theory"
    if await simulate_loop_mode(topic, tracker):
        print("✓ Loop mode test PASSED")
        results['passed'] += 1
    else:
        print("✗ Loop mode test FAILED")
        results['failed'] += 1

    # Test 2: Debate Mode
    print("\n" + "━" * 80)
    print("TEST 2: Debate Mode Orchestration")
    print("━" * 80)
    debate_topic = "Using HKT encoding vs simple TypeScript generics for functional programming"
    if await simulate_debate_mode(debate_topic, tracker):
        print("✓ Debate mode test PASSED")
        results['passed'] += 1
    else:
        print("✗ Debate mode test FAILED")
        results['failed'] += 1

    # Test 3: Streaming
    print("\n" + "━" * 80)
    print("TEST 3: Streaming Responses")
    print("━" * 80)
    if await test_streaming(tracker):
        print("✓ Streaming test PASSED")
        results['passed'] += 1
    else:
        print("✗ Streaming test FAILED")
        results['failed'] += 1

    # Test 4: Specific Use Case
    print("\n" + "━" * 80)
    print("TEST 4: Specific Research Use Case")
    print("━" * 80)
    if await test_specific_use_case(tracker):
        print("✓ Use case test PASSED")
        results['passed'] += 1
    else:
        print("✗ Use case test FAILED")
        results['failed'] += 1

    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {results['passed']}")
    print(f"Tests Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed'] / (results['passed'] + results['failed']) * 100):.1f}%")

    # Cost summary
    tracker.print_summary()

    print()
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return results, tracker


if __name__ == "__main__":
    try:
        results, tracker = asyncio.run(advanced_test_suite())

        # Exit with appropriate code
        sys.exit(0 if results['failed'] == 0 else 1)

    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
