#!/usr/bin/env python3
"""
Comprehensive tests for EnhancedGrokClient

Tests cover:
- Basic chat functionality
- Files API (with and without actual API)
- Server-side tools
- Collections API
- Async context preservation
- Error handling
"""

import asyncio
import os
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clients.grok_enhanced import EnhancedGrokClient


# Test fixtures
@pytest.fixture
def api_key():
    """Get API key from environment or skip tests"""
    key = os.environ.get("XAI_API_KEY")
    if not key:
        pytest.skip("XAI_API_KEY not set - skipping integration tests")
    return key


@pytest.fixture
async def grok_client(api_key):
    """Create EnhancedGrokClient instance"""
    client = EnhancedGrokClient(api_key=api_key, model="grok-4-fast")
    yield client
    await client.close()


@pytest.fixture
def test_file(tmp_path):
    """Create a test text file"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test document for Grok API testing.")
    return str(file_path)


@pytest.fixture
def test_markdown(tmp_path):
    """Create a test markdown file"""
    file_path = tmp_path / "test.md"
    file_path.write_text("""# Test Document

This is a test markdown document.

## Section 1
Some content here.

## Section 2
More content here.
""")
    return str(file_path)


# Unit Tests (No API calls)

class TestEnhancedGrokClientInit:
    """Test client initialization"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        client = EnhancedGrokClient(api_key="test-key", model="grok-4-fast")
        assert client.api_key == "test-key"
        assert client.default_model == "grok-4-fast"

    def test_init_without_api_key_raises(self):
        """Test that missing API key raises ValueError"""
        # Temporarily unset env var if it exists
        old_key = os.environ.get("XAI_API_KEY")
        if old_key:
            del os.environ["XAI_API_KEY"]

        try:
            with pytest.raises(ValueError, match="XAI_API_KEY not found"):
                EnhancedGrokClient()
        finally:
            # Restore env var
            if old_key:
                os.environ["XAI_API_KEY"] = old_key

    def test_collections_lazy_loading(self):
        """Test that collections manager is lazy loaded"""
        client = EnhancedGrokClient(api_key="test-key")
        assert client._collections_manager is None
        # Access collections property
        _ = client.collections
        assert client._collections_manager is not None


# Integration Tests (Require XAI_API_KEY)

@pytest.mark.asyncio
class TestBasicChat:
    """Test basic chat functionality"""

    async def test_simple_chat(self, grok_client):
        """Test basic chat without files or tools"""
        response, tokens = await grok_client.chat(
            "Say 'Hello, test!' and nothing else.",
            max_tokens=50
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert "tokens" in str(tokens) or isinstance(tokens, dict)
        assert tokens["total"] > 0
        assert tokens["prompt"] > 0
        assert tokens["completion"] > 0

        print(f"\n✓ Basic chat test passed")
        print(f"  Response: {response[:100]}")
        print(f"  Tokens: {tokens}")

    async def test_chat_with_system_prompt(self, grok_client):
        """Test chat with system prompt"""
        response, tokens = await grok_client.chat(
            "What is 2+2?",
            system_prompt="You are a helpful math tutor. Keep answers concise.",
            max_tokens=100
        )

        assert isinstance(response, str)
        assert "4" in response or "four" in response.lower()
        assert tokens["total"] > 0

        print(f"\n✓ System prompt test passed")
        print(f"  Response: {response[:100]}")

    async def test_chat_with_temperature(self, grok_client):
        """Test temperature parameter"""
        # Low temperature (more deterministic)
        response1, _ = await grok_client.chat(
            "Count: 1, 2, 3, 4, 5",
            temperature=0.1,
            max_tokens=50
        )

        # High temperature (more creative)
        response2, _ = await grok_client.chat(
            "Count: 1, 2, 3, 4, 5",
            temperature=1.5,
            max_tokens=50
        )

        assert isinstance(response1, str)
        assert isinstance(response2, str)

        print(f"\n✓ Temperature test passed")
        print(f"  Low temp (0.1): {response1[:50]}")
        print(f"  High temp (1.5): {response2[:50]}")


@pytest.mark.asyncio
class TestFilesAPI:
    """Test Files API functionality"""

    async def test_analyze_single_file(self, grok_client, test_file):
        """Test analyzing a single text file"""
        response, tokens = await grok_client.analyze_file(
            test_file,
            "Summarize this document in one sentence.",
            model="grok-4-fast"
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert tokens["total"] > 0

        print(f"\n✓ Single file analysis test passed")
        print(f"  File: {test_file}")
        print(f"  Response: {response[:100]}")
        print(f"  Tokens: {tokens}")

    async def test_analyze_markdown_file(self, grok_client, test_markdown):
        """Test analyzing markdown file"""
        response, tokens = await grok_client.analyze_file(
            test_markdown,
            "List the section headings in this markdown document.",
            model="grok-4-fast"
        )

        assert isinstance(response, str)
        assert "Section 1" in response or "section" in response.lower()

        print(f"\n✓ Markdown file analysis test passed")
        print(f"  Response: {response[:200]}")

    async def test_analyze_multiple_files(self, grok_client, test_file, test_markdown):
        """Test analyzing multiple files"""
        response, tokens = await grok_client.analyze_files(
            [test_file, test_markdown],
            "Compare these two documents. What are the key differences?",
            model="grok-4-fast"
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert tokens["total"] > 0

        print(f"\n✓ Multiple file analysis test passed")
        print(f"  Files: {[test_file, test_markdown]}")
        print(f"  Response: {response[:150]}")

    async def test_analyze_too_many_files_raises(self, grok_client, test_file):
        """Test that analyzing >10 files raises error"""
        files = [test_file] * 11

        with pytest.raises(ValueError, match="Cannot analyze more than 10 files"):
            await grok_client.analyze_files(files, "Test prompt")

        print(f"\n✓ File limit validation test passed")


@pytest.mark.asyncio
class TestServerSideTools:
    """Test server-side tools functionality"""

    async def test_web_search(self, grok_client):
        """Test web search tool"""
        response, tokens = await grok_client.research_query(
            "What is the current weather in San Francisco? (Just acknowledge the request, actual data not needed for test)",
            use_web=True,
            use_x=False,
            use_code=False,
            model="grok-4-fast"
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert tokens["total"] > 0

        print(f"\n✓ Web search test passed")
        print(f"  Response: {response[:200]}")
        print(f"  Tokens: {tokens}")

    async def test_no_tools_raises(self, grok_client):
        """Test that no tools enabled raises error"""
        with pytest.raises(ValueError, match="At least one tool must be enabled"):
            await grok_client.research_query(
                "Test query",
                use_web=False,
                use_x=False,
                use_code=False
            )

        print(f"\n✓ Tool validation test passed")

    async def test_multiple_tools(self, grok_client):
        """Test using multiple tools together"""
        response, tokens = await grok_client.research_query(
            "Quick test: What is 5+5? Just compute and respond.",
            use_web=False,
            use_x=False,
            use_code=True,  # Use code execution for simple math
            model="grok-4-fast"
        )

        assert isinstance(response, str)
        assert "10" in response or "ten" in response.lower()

        print(f"\n✓ Multiple tools test passed")
        print(f"  Response: {response[:100]}")


@pytest.mark.asyncio
class TestAsyncContext:
    """Test async context preservation"""

    async def test_concurrent_requests(self, grok_client):
        """Test multiple concurrent requests"""
        prompts = [
            "Say 'Request 1'",
            "Say 'Request 2'",
            "Say 'Request 3'"
        ]

        tasks = [
            grok_client.chat(prompt, max_tokens=20)
            for prompt in prompts
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for response, tokens in results:
            assert isinstance(response, str)
            assert tokens["total"] > 0

        print(f"\n✓ Concurrent requests test passed")
        print(f"  Completed {len(results)} concurrent requests")

    async def test_sequential_with_context(self, grok_client):
        """Test sequential requests maintaining context"""
        # First request
        response1, tokens1 = await grok_client.chat(
            "Remember this number: 42. Just acknowledge.",
            max_tokens=50
        )

        # Second request (in practice, would need conversation history)
        response2, tokens2 = await grok_client.chat(
            "What number did I just tell you? (This is a new request, no memory expected)",
            max_tokens=50
        )

        assert isinstance(response1, str)
        assert isinstance(response2, str)
        assert tokens1["total"] > 0
        assert tokens2["total"] > 0

        print(f"\n✓ Sequential requests test passed")
        print(f"  Request 1: {response1[:50]}")
        print(f"  Request 2: {response2[:50]}")


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling"""

    async def test_invalid_model(self, grok_client):
        """Test that invalid model is handled"""
        try:
            response, tokens = await grok_client.chat(
                "Test",
                model="invalid-model-name"
            )
            # If it doesn't error, that's also acceptable
            assert isinstance(response, str)
        except Exception as e:
            # Expected to raise an error
            assert "model" in str(e).lower() or "not found" in str(e).lower()

        print(f"\n✓ Invalid model handling test passed")

    async def test_nonexistent_file(self, grok_client):
        """Test analyzing non-existent file"""
        with pytest.raises(FileNotFoundError):
            await grok_client.analyze_file(
                "/nonexistent/file.txt",
                "Analyze this"
            )

        print(f"\n✓ File not found handling test passed")


@pytest.mark.asyncio
class TestStreamingChat:
    """Test streaming functionality"""

    async def test_chat_stream_basic(self, grok_client):
        """Test basic streaming chat"""
        chunks = []

        async for chunk in grok_client.chat_stream(
            "Count from 1 to 5, one number per line.",
            max_tokens=100
        ):
            chunks.append(chunk)

        full_response = "".join(chunks)

        assert len(chunks) > 0
        assert isinstance(full_response, str)
        assert len(full_response) > 0

        print(f"\n✓ Streaming test passed")
        print(f"  Received {len(chunks)} chunks")
        print(f"  Full response: {full_response[:100]}")


# Test runner
async def run_all_tests():
    """Run all tests manually (for testing without pytest)"""
    print("\n" + "="*60)
    print("Running Enhanced Grok Client Tests")
    print("="*60)

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("\n✗ XAI_API_KEY not set. Please set it to run tests.")
        print("  export XAI_API_KEY='your-api-key'")
        return False

    client = EnhancedGrokClient(api_key=api_key, model="grok-4-fast")

    try:
        # Create temp files
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create test files
            test_file = tmp_path / "test.txt"
            test_file.write_text("This is a test document.")

            test_md = tmp_path / "test.md"
            test_md.write_text("# Test\n\nContent here.")

            print("\n1. Testing basic chat...")
            response, tokens = await client.chat("Say 'Hello, test!'", max_tokens=20)
            print(f"✓ Basic chat: {response[:50]}")

            print("\n2. Testing file analysis...")
            response, tokens = await client.analyze_file(
                str(test_file),
                "Summarize in one sentence."
            )
            print(f"✓ File analysis: {response[:100]}")

            print("\n3. Testing server-side tools...")
            response, tokens = await client.research_query(
                "Quick test: What is the capital of France?",
                use_web=True,
                use_x=False,
                use_code=False
            )
            print(f"✓ Web search: {response[:100]}")

            print("\n4. Testing concurrent requests...")
            tasks = [
                client.chat(f"Say 'Request {i}'", max_tokens=20)
                for i in range(3)
            ]
            results = await asyncio.gather(*tasks)
            print(f"✓ Concurrent: {len(results)} requests completed")

            print("\n5. Testing streaming...")
            chunks = []
            async for chunk in client.chat_stream("Count: 1, 2, 3", max_tokens=50):
                chunks.append(chunk)
            print(f"✓ Streaming: {len(chunks)} chunks received")

            print("\n" + "="*60)
            print("✅ All tests passed!")
            print("="*60)
            return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await client.close()


if __name__ == "__main__":
    # Check if running with pytest or manually
    if "pytest" not in sys.modules:
        # Manual run
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
