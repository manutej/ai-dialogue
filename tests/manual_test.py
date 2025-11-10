#!/usr/bin/env python3
"""
Manual Test Script for Enhanced Grok Client

Run this script to validate all functionality:
    python3 tests/manual_test.py

Requires:
- XAI_API_KEY environment variable
- openai package
"""

import asyncio
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clients.grok_enhanced import EnhancedGrokClient


class TestRunner:
    """Test runner with progress tracking"""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def test(self, name, func):
        """Run a test and track results"""
        self.tests_run += 1
        print(f"\n{'='*60}")
        print(f"Test {self.tests_run}: {name}")
        print(f"{'='*60}")

        try:
            result = func()
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)

            self.tests_passed += 1
            self.results.append((name, "✅ PASSED", None))
            print(f"\n✅ PASSED: {name}")
            return True

        except Exception as e:
            self.tests_failed += 1
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.results.append((name, "❌ FAILED", error_msg))
            print(f"\n❌ FAILED: {name}")
            print(f"Error: {error_msg}")
            traceback.print_exc()
            return False

    def summary(self):
        """Print test summary"""
        print(f"\n\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")

        for name, status, error in self.results:
            print(f"{status} {name}")
            if error:
                print(f"    {error}")

        print(f"\n{'='*60}")
        print(f"Total: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"{'='*60}")

        return self.tests_failed == 0


async def test_basic_chat(client):
    """Test 1: Basic chat functionality"""
    response, tokens = await client.chat(
        "Say 'Hello from Grok!' and nothing else.",
        max_tokens=50
    )

    assert isinstance(response, str), "Response should be string"
    assert len(response) > 0, "Response should not be empty"
    assert isinstance(tokens, dict), "Tokens should be dict"
    assert tokens["total"] > 0, "Should use some tokens"

    print(f"Response: {response}")
    print(f"Tokens: {tokens}")


async def test_system_prompt(client):
    """Test 2: Chat with system prompt"""
    response, tokens = await client.chat(
        "What is 2+2?",
        system_prompt="You are a math tutor. Be concise.",
        max_tokens=50
    )

    assert "4" in response or "four" in response.lower(), "Should answer 4"
    print(f"Response: {response}")


async def test_temperature(client):
    """Test 3: Temperature parameter"""
    response_low, _ = await client.chat(
        "Say exactly: Test",
        temperature=0.1,
        max_tokens=20
    )

    response_high, _ = await client.chat(
        "Say exactly: Test",
        temperature=1.5,
        max_tokens=20
    )

    assert isinstance(response_low, str)
    assert isinstance(response_high, str)

    print(f"Low temp (0.1): {response_low}")
    print(f"High temp (1.5): {response_high}")


async def test_file_analysis(client, test_file):
    """Test 4: Analyze single file"""
    response, tokens = await client.analyze_file(
        test_file,
        "Summarize this document in one sentence.",
        model="grok-4-fast"
    )

    assert isinstance(response, str)
    assert len(response) > 0
    assert tokens["total"] > 0

    print(f"File: {test_file}")
    print(f"Analysis: {response[:200]}")
    print(f"Tokens: {tokens}")


async def test_multiple_files(client, test_file, test_md):
    """Test 5: Analyze multiple files"""
    response, tokens = await client.analyze_files(
        [test_file, test_md],
        "List the files and their content types.",
        model="grok-4-fast"
    )

    assert isinstance(response, str)
    assert len(response) > 0

    print(f"Files: {[test_file, test_md]}")
    print(f"Analysis: {response[:200]}")


async def test_web_search(client):
    """Test 6: Web search tool"""
    response, tokens = await client.research_query(
        "What is the capital of France? Just state the city name.",
        use_web=True,
        use_x=False,
        use_code=False,
        model="grok-4-fast"
    )

    assert isinstance(response, str)
    assert "Paris" in response or "paris" in response.lower(), "Should mention Paris"

    print(f"Query: Capital of France")
    print(f"Response: {response[:200]}")
    print(f"Tokens: {tokens}")


async def test_code_execution(client):
    """Test 7: Code execution tool"""
    response, tokens = await client.research_query(
        "Calculate 123 * 456 using Python. Show the result.",
        use_web=False,
        use_x=False,
        use_code=True,
        model="grok-4-fast"
    )

    result = 123 * 456  # 56088
    assert isinstance(response, str)
    assert str(result) in response, f"Should contain {result}"

    print(f"Calculation: 123 * 456")
    print(f"Response: {response[:200]}")


async def test_concurrent_requests(client):
    """Test 8: Concurrent async requests"""
    tasks = [
        client.chat(f"Say 'Request {i}'", max_tokens=20)
        for i in range(3)
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 3, "Should complete 3 requests"

    for i, (response, tokens) in enumerate(results):
        assert isinstance(response, str)
        assert tokens["total"] > 0
        print(f"Request {i+1}: {response[:50]} ({tokens['total']} tokens)")


async def test_streaming(client):
    """Test 9: Streaming chat"""
    chunks = []

    async for chunk in client.chat_stream(
        "Count: 1, 2, 3",
        max_tokens=50
    ):
        chunks.append(chunk)

    full_response = "".join(chunks)

    assert len(chunks) > 0, "Should receive chunks"
    assert isinstance(full_response, str)
    assert len(full_response) > 0

    print(f"Received {len(chunks)} chunks")
    print(f"Full response: {full_response}")


async def test_error_handling(client):
    """Test 10: Error handling"""

    # Test non-existent file
    try:
        await client.analyze_file("/nonexistent/file.txt", "Test")
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        print("✓ FileNotFoundError correctly raised for non-existent file")

    # Test too many files
    try:
        await client.analyze_files(["file.txt"] * 11, "Test")
        assert False, "Should raise ValueError for >10 files"
    except ValueError as e:
        assert "10 files" in str(e)
        print("✓ ValueError correctly raised for too many files")

    # Test no tools enabled - should fall back to regular chat
    response, tokens = await client.research_query(
        "Say 'Test response'",
        use_web=False,
        use_x=False,
        use_code=False
    )
    assert isinstance(response, str)
    assert len(response) > 0
    print("✓ No tools enabled correctly falls back to regular chat")


def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("ENHANCED GROK CLIENT - MANUAL TEST SUITE")
    print("="*60)

    # Check API key
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: XAI_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export XAI_API_KEY='your-api-key-here'")
        print("\nThen run this script again:")
        print("  python3 tests/manual_test.py")
        return 1

    print(f"\n✓ XAI_API_KEY found")

    # Initialize client
    print(f"✓ Initializing EnhancedGrokClient...")
    client = EnhancedGrokClient(api_key=api_key, model="grok-4-fast")
    print(f"✓ Client initialized with model: grok-4-fast")

    # Create test files
    print(f"✓ Creating test files...")
    tmp_dir = TemporaryDirectory()
    tmp_path = Path(tmp_dir.name)

    test_file = tmp_path / "test.txt"
    test_file.write_text("This is a test document for Grok API testing.\n\nIt contains multiple lines.\n\nAnd some more content.")

    test_md = tmp_path / "test.md"
    test_md.write_text("""# Test Document

This is a test markdown file.

## Section 1
Some important information here.

## Section 2
More details in this section.

## Conclusion
Final thoughts.
""")

    print(f"✓ Test files created: {test_file}, {test_md}")

    # Run tests
    runner = TestRunner()

    async def run_tests():
        """Run all async tests"""
        try:
            # Test 1: Basic chat
            await test_basic_chat(client)

            # Test 2: System prompt
            await test_system_prompt(client)

            # Test 3: Temperature
            await test_temperature(client)

            # Test 4: Single file
            await test_file_analysis(client, str(test_file))

            # Test 5: Multiple files
            await test_multiple_files(client, str(test_file), str(test_md))

            # Test 6: Web search
            await test_web_search(client)

            # Test 7: Code execution
            await test_code_execution(client)

            # Test 8: Concurrent requests
            await test_concurrent_requests(client)

            # Test 9: Streaming
            await test_streaming(client)

            # Test 10: Error handling
            await test_error_handling(client)

        finally:
            # Cleanup
            await client.close()
            tmp_dir.cleanup()

    # Execute tests
    try:
        runner.test("Basic Chat", lambda: asyncio.run(test_basic_chat(EnhancedGrokClient(api_key=api_key))))
        runner.test("System Prompt", lambda: asyncio.run(test_system_prompt(EnhancedGrokClient(api_key=api_key))))
        runner.test("Temperature Control", lambda: asyncio.run(test_temperature(EnhancedGrokClient(api_key=api_key))))
        runner.test("File Analysis", lambda: asyncio.run(test_file_analysis(EnhancedGrokClient(api_key=api_key), str(test_file))))
        runner.test("Multiple Files", lambda: asyncio.run(test_multiple_files(EnhancedGrokClient(api_key=api_key), str(test_file), str(test_md))))
        runner.test("Web Search", lambda: asyncio.run(test_web_search(EnhancedGrokClient(api_key=api_key))))
        runner.test("Code Execution", lambda: asyncio.run(test_code_execution(EnhancedGrokClient(api_key=api_key))))
        runner.test("Concurrent Requests", lambda: asyncio.run(test_concurrent_requests(EnhancedGrokClient(api_key=api_key))))
        runner.test("Streaming Chat", lambda: asyncio.run(test_streaming(EnhancedGrokClient(api_key=api_key))))
        runner.test("Error Handling", lambda: asyncio.run(test_error_handling(EnhancedGrokClient(api_key=api_key))))

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1

    finally:
        # Always cleanup
        tmp_dir.cleanup()

    # Print summary
    success = runner.summary()

    if success:
        print("\n🎉 All tests passed! Implementation is stable.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
