"""
Grok Code Analysis Tool for ai-dialogue Phase 3

This script uses Grok to analyze the codebase for:
- Bugs and potential issues
- Performance problems
- Security vulnerabilities
- Async/await correctness
- Error handling gaps

Usage:
    python tools/grok_code_analysis.py

Environment:
    XAI_API_KEY - Your xAI API key (required)
"""

import asyncio
import os
from pathlib import Path
from src.clients.grok import GrokClient


async def analyze_protocol_engine():
    """Analyze protocol.py with Grok for bugs and issues"""

    # Read the protocol.py file
    protocol_path = Path(__file__).parent.parent / "src" / "protocol.py"
    with open(protocol_path) as f:
        protocol_code = f.read()

    # Initialize Grok client
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("❌ XAI_API_KEY not set. Cannot run analysis.")
        print("   Set it with: export XAI_API_KEY=your-key-here")
        return

    grok = GrokClient(api_key=api_key)

    print("=" * 80)
    print("GROK CODE ANALYSIS: Phase 3 Protocol Engine")
    print("=" * 80)
    print()

    # Analysis 1: Bug Detection
    print("🔍 ANALYSIS 1: Bug Detection & Correctness")
    print("-" * 80)

    analysis_prompt_1 = f"""
Analyze this Python code for potential bugs, logical errors, and edge cases.
Focus on:
1. Off-by-one errors or boundary conditions
2. State management issues
3. Race conditions or async problems
4. Resource leaks
5. Error handling gaps
6. Type mismatches

Code to analyze:
```python
{protocol_code}
```

Provide:
- List of potential bugs found (if any)
- Severity level (Critical/High/Medium/Low)
- How to reproduce or trigger the bug
- Suggested fix
"""

    try:
        response1, tokens1 = await grok.chat(
            analysis_prompt_1,
            model="grok-4-fast-reasoning-latest",
            max_tokens=2000
        )
        print(response1)
        print()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        await grok.close()
        return

    # Analysis 2: Async/Await Correctness
    print()
    print("⚙️  ANALYSIS 2: Async/Await Pattern Review")
    print("-" * 80)

    analysis_prompt_2 = f"""
Review this code specifically for async/await patterns and concurrency issues.
Check for:
1. Proper use of await (all async calls awaited)
2. Correct asyncio usage (gather, wait_for, sleep)
3. Resource cleanup (close() calls)
4. Event loop issues
5. Deadlocks or race conditions
6. Proper exception handling in async code

Code:
```python
{protocol_code}
```

Specifically look at:
- _execute_turn() method
- _execute_sequential(), _execute_parallel(), _execute_mixed()
- Retry logic with exponential backoff
- asyncio.wait_for() usage

Provide severity level for each issue found.
"""

    try:
        response2, tokens2 = await grok.chat(
            analysis_prompt_2,
            model="grok-4-fast-reasoning-latest",
            max_tokens=2000
        )
        print(response2)
        print()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        await grok.close()
        return

    # Analysis 3: Security Review
    print()
    print("🔒 ANALYSIS 3: Security & Safety Review")
    print("-" * 80)

    analysis_prompt_3 = f"""
Review this code for security vulnerabilities and safety issues.
Check for:
1. Input validation issues
2. Injection vulnerabilities
3. Unsafe use of eval/exec
4. Hardcoded secrets
5. Proper error message handling (no sensitive data leaks)
6. Resource exhaustion possibilities
7. Unsafe type conversions

Code:
```python
{protocol_code}
```

List any security concerns with severity level.
"""

    try:
        response3, tokens3 = await grok.chat(
            analysis_prompt_3,
            model="grok-4-fast-reasoning-latest",
            max_tokens=1500
        )
        print(response3)
        print()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        await grok.close()
        return

    # Analysis 4: Performance Review
    print()
    print("⚡ ANALYSIS 4: Performance & Efficiency Review")
    print("-" * 80)

    analysis_prompt_4 = f"""
Review this code for performance issues and optimization opportunities.
Check for:
1. Inefficient loops or algorithms
2. Unnecessary object creation
3. Duplicate computations
4. Memory leaks or unbounded growth
5. CPU-intensive operations that could be optimized
6. I/O blocking that should be async
7. Unnecessary retries or exponential backoff configuration

Code:
```python
{protocol_code}
```

For each issue, provide:
- Description
- Performance impact (Negligible/Minor/Moderate/Significant)
- Optimization suggestion
"""

    try:
        response4, tokens4 = await grok.chat(
            analysis_prompt_4,
            model="grok-4-fast-reasoning-latest",
            max_tokens=1500
        )
        print(response4)
        print()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        await grok.close()
        return

    # Analysis 5: Test Coverage Evaluation
    print()
    print("🧪 ANALYSIS 5: Test Coverage & Edge Cases")
    print("-" * 80)

    analysis_prompt_5 = f"""
Based on this implementation code, evaluate if the tests would catch bugs.

Code:
```python
{protocol_code}
```

For the major functions:
1. calculate_cost()
2. _execute_turn()
3. _execute_sequential/parallel/mixed()
4. export_to_markdown()

Identify:
- Critical edge cases that MUST be tested
- Common bugs that would occur without proper testing
- Scenarios that would break the code
- What tests would effectively catch these bugs

This helps verify if the 19-test suite is sufficient.
"""

    try:
        response5, tokens5 = await grok.chat(
            analysis_prompt_5,
            model="grok-4-fast-reasoning-latest",
            max_tokens=1500
        )
        print(response5)
        print()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        await grok.close()
        return

    # Summary
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Token usage summary:")
    try:
        total_tokens = tokens1.get('total', 0) + tokens2.get('total', 0) + tokens3.get('total', 0) + tokens4.get('total', 0) + tokens5.get('total', 0)
        print(f"  Total tokens used: {total_tokens:,}")

        # Estimate cost
        from src.protocol import calculate_cost
        estimated_cost = calculate_cost("grok-4-fast-reasoning-latest", {
            "prompt": total_tokens // 2,
            "completion": total_tokens // 2,
            "total": total_tokens
        })
        print(f"  Estimated cost: ${estimated_cost:.6f}")
    except:
        pass

    await grok.close()


async def analyze_test_quality():
    """Analyze if tests are deep enough"""

    test_path = Path(__file__).parent.parent / "tests" / "test_phase3_features.py"
    with open(test_path) as f:
        test_code = f.read()

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        return

    grok = GrokClient(api_key=api_key)

    print()
    print("=" * 80)
    print("TEST QUALITY ANALYSIS: Verifying Tests Are NOT Shallow")
    print("=" * 80)
    print()

    analysis_prompt = f"""
Evaluate if this test suite is "deep" (tests real bugs) or "shallow" (just confirms happy path).

Test code:
```python
{test_code[:5000]}
... (truncated for length)
```

Analyze:
1. Do tests verify exact math or just "doesn't crash"?
2. Do tests check state mutations (cost, error, retry_count)?
3. Do tests include failure scenarios (timeouts, retries)?
4. Do tests cover edge cases (zero tokens, unknown models)?
5. Are assertions specific or vague?

For each major test class:
- TestCostCalculation
- TestRetryLogic
- TestMarkdownExportWithCosts

Explain why they ARE deep (not shallow).

Conclude: Are these tests designed to catch REAL bugs?
"""

    try:
        response, tokens = await grok.chat(
            analysis_prompt,
            model="grok-4-fast-reasoning-latest",
            max_tokens=2000
        )
        print(response)
    except Exception as e:
        print(f"❌ Error: {e}")

    await grok.close()


async def main():
    """Run all analyses"""
    print("\n")
    print("🤖 GROK CODE ANALYSIS SUITE")
    print("=" * 80)
    print()

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("⚠️  WARNING: XAI_API_KEY not set")
        print()
        print("To run Grok analysis, set your API key:")
        print("  export XAI_API_KEY=your-key-here")
        print()
        print("Then run:")
        print("  python tools/grok_code_analysis.py")
        print()
        return

    print(f"✅ API Key found (length: {len(api_key)} chars)")
    print()

    # Run protocol analysis
    await analyze_protocol_engine()

    # Run test quality analysis
    await analyze_test_quality()


if __name__ == "__main__":
    asyncio.run(main())
