"""
Comprehensive GrokClient Tests - Phase 4A

Tests for GrokClient error handling, concurrency, and advanced features.
Covers gaps in current test suite to reach 80% coverage target.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from src.clients.grok import GrokClient, MODEL_IDS
from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError


# ============= ERROR HANDLING TESTS =============

class TestGrokClientErrorHandling:
    """Test robust error handling in GrokClient"""

    @pytest.mark.asyncio
    async def test_invalid_api_key(self):
        """Test that invalid API key raises appropriate error"""
        with pytest.raises(ValueError, match="XAI_API_KEY not found"):
            GrokClient(api_key=None)

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test rate limit error handling"""
        client = GrokClient(api_key="test-key")
        client.client.chat.completions.create = AsyncMock(
            side_effect=RateLimitError(
                message="Rate limit exceeded",
                response=Mock(status_code=429),
                body={}
            )
        )

        with pytest.raises(RateLimitError):
            await client.chat("Test prompt")

        await client.close()

    @pytest.mark.asyncio
    async def test_timeout_recovery(self):
        """Test timeout error handling"""
        client = GrokClient(api_key="test-key")
        client.client.chat.completions.create = AsyncMock(
            side_effect=asyncio.TimeoutError("Request timed out")
        )

        with pytest.raises(asyncio.TimeoutError):
            await client.chat("Test prompt")

        await client.close()

    @pytest.mark.asyncio
    async def test_api_connection_error(self):
        """Test API connection error handling"""
        client = GrokClient(api_key="test-key")
        client.client.chat.completions.create = AsyncMock(
            side_effect=APIConnectionError(message="Connection failed", request=Mock())
        )

        with pytest.raises(APIConnectionError):
            await client.chat("Test prompt")

        await client.close()

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses"""
        client = GrokClient(api_key="test-key")

        # Mock response with missing fields
        mock_response = Mock()
        mock_response.choices = []  # Empty choices

        client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        with pytest.raises((IndexError, AttributeError)):
            await client.chat("Test prompt")

        await client.close()


# ============= CONCURRENCY TESTS =============

class TestGrokClientConcurrency:
    """Test concurrent request handling"""

    @pytest.mark.asyncio
    async def test_parallel_requests(self):
        """Test multiple concurrent requests"""
        client = GrokClient(api_key="test-key")

        # Mock different responses for each request
        responses = [
            Mock(
                choices=[Mock(message=Mock(content=f"Response {i}"))],
                usage=Mock(prompt_tokens=50, completion_tokens=100, total_tokens=150)
            )
            for i in range(5)
        ]

        client.client.chat.completions.create = AsyncMock(side_effect=responses)

        # Execute 5 requests concurrently
        tasks = [
            client.chat(f"Prompt {i}")
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all requests completed
        assert len(results) == 5
        for i, (response, tokens) in enumerate(results):
            assert response == f"Response {i}"
            assert tokens["total"] == 150

        await client.close()

    @pytest.mark.asyncio
    async def test_sequential_with_state(self):
        """Test sequential requests maintain consistent state"""
        client = GrokClient(api_key="test-key")

        mock_response_1 = Mock(
            choices=[Mock(message=Mock(content="First response"))],
            usage=Mock(prompt_tokens=50, completion_tokens=100, total_tokens=150)
        )
        mock_response_2 = Mock(
            choices=[Mock(message=Mock(content="Second response"))],
            usage=Mock(prompt_tokens=60, completion_tokens=110, total_tokens=170)
        )

        client.client.chat.completions.create = AsyncMock(
            side_effect=[mock_response_1, mock_response_2]
        )

        # Execute sequential requests
        response1, tokens1 = await client.chat("First prompt")
        response2, tokens2 = await client.chat("Second prompt")

        assert response1 == "First response"
        assert response2 == "Second response"
        assert tokens1["total"] == 150
        assert tokens2["total"] == 170
        assert client.default_model == "grok-4"  # State preserved

        await client.close()

    @pytest.mark.asyncio
    async def test_connection_pooling(self):
        """Test that client reuses connection across requests"""
        client = GrokClient(api_key="test-key")

        # Verify client is initialized only once
        assert isinstance(client.client, AsyncOpenAI)
        client_instance = client.client

        # Multiple requests should use same client instance
        mock_response = Mock(
            choices=[Mock(message=Mock(content="Response"))],
            usage=Mock(prompt_tokens=50, completion_tokens=100, total_tokens=150)
        )

        client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        await client.chat("Request 1")
        await client.chat("Request 2")

        # Client instance should remain the same
        assert client.client is client_instance

        await client.close()


# ============= STREAMING TESTS =============

class TestGrokClientStreaming:
    """Test streaming response handling"""

    @pytest.mark.asyncio
    async def test_stream_complete_response(self):
        """Test streaming a complete response"""
        client = GrokClient(api_key="test-key")

        # Mock streaming chunks
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello "))]),
            Mock(choices=[Mock(delta=Mock(content="world"))]),
            Mock(choices=[Mock(delta=Mock(content="!"))]),
        ]

        async def mock_stream():
            for chunk in mock_chunks:
                yield chunk

        client.client.chat.completions.create = AsyncMock(return_value=mock_stream())

        chunks = []
        async for chunk in client.chat_stream("Test prompt"):
            chunks.append(chunk)

        assert chunks == ["Hello ", "world", "!"]
        assert "".join(chunks) == "Hello world!"

        await client.close()

    @pytest.mark.asyncio
    async def test_stream_empty_chunks_filtered(self):
        """Test that empty chunks are filtered out"""
        client = GrokClient(api_key="test-key")

        # Mock streaming with some empty chunks
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello "))]),
            Mock(choices=[Mock(delta=Mock(content=None))]),  # Empty
            Mock(choices=[Mock(delta=Mock(content="world"))]),
            Mock(choices=[Mock(delta=Mock(content=""))]),  # Empty
            Mock(choices=[Mock(delta=Mock(content="!"))]),
        ]

        async def mock_stream():
            for chunk in mock_chunks:
                yield chunk

        client.client.chat.completions.create = AsyncMock(return_value=mock_stream())

        chunks = []
        async for chunk in client.chat_stream("Test prompt"):
            chunks.append(chunk)

        # Only non-empty chunks should be yielded
        assert chunks == ["Hello ", "world", "!"]

        await client.close()

    @pytest.mark.asyncio
    async def test_stream_error_handling(self):
        """Test error handling during streaming"""
        client = GrokClient(api_key="test-key")

        async def failing_stream():
            yield Mock(choices=[Mock(delta=Mock(content="Hello "))])
            raise APIError(
                message="Stream interrupted",
                request=Mock(),
                body={}
            )

        client.client.chat.completions.create = AsyncMock(return_value=failing_stream())

        chunks = []
        with pytest.raises(APIError):
            async for chunk in client.chat_stream("Test prompt"):
                chunks.append(chunk)

        # Should have received first chunk before error
        assert chunks == ["Hello "]

        await client.close()


# ============= CONNECTION LIFECYCLE TESTS =============

class TestGrokClientLifecycle:
    """Test client initialization and cleanup"""

    def test_client_initialization_with_custom_model(self):
        """Test initialization with custom default model"""
        client = GrokClient(api_key="test-key", model="grok-code")

        assert client.default_model == "grok-code"
        assert client._resolve_model("grok-code") == "grok-code-fast-1"

    def test_client_initialization_with_invalid_model_warning(self):
        """Test that unknown models log warning but still work"""
        client = GrokClient(api_key="test-key", model="unknown-model")

        # Should accept unknown model but log warning
        assert client.default_model == "unknown-model"
        # Unknown model passes through as-is
        assert client._resolve_model("unknown-model") == "unknown-model"

    @pytest.mark.asyncio
    async def test_client_close_cleanup(self):
        """Test that close() properly cleans up resources"""
        client = GrokClient(api_key="test-key")

        # Mock the close method
        client.client.close = AsyncMock()

        await client.close()

        # Verify close was called
        client.client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_close_calls_safe(self):
        """Test that calling close() multiple times is safe"""
        client = GrokClient(api_key="test-key")
        client.client.close = AsyncMock()

        # Close multiple times
        await client.close()
        await client.close()
        await client.close()

        # Should handle gracefully (may be called 1 or 3 times depending on implementation)
        assert client.client.close.call_count >= 1


# ============= MODEL RESOLUTION TESTS =============

class TestGrokClientModelResolution:
    """Test model ID resolution logic"""

    def test_all_known_models_resolve(self):
        """Test that all models in MODEL_IDS resolve correctly"""
        client = GrokClient(api_key="test-key")

        for friendly_name, expected_id in MODEL_IDS.items():
            resolved = client._resolve_model(friendly_name)
            assert resolved == expected_id

    def test_model_resolution_case_sensitive(self):
        """Test that model resolution is case-sensitive"""
        client = GrokClient(api_key="test-key")

        # Correct case
        assert client._resolve_model("grok-4") == "grok-4-fast-reasoning-latest"

        # Incorrect case passes through (not in mapping)
        assert client._resolve_model("GROK-4") == "GROK-4"

    def test_already_resolved_model_passes_through(self):
        """Test that already-resolved model IDs pass through unchanged"""
        client = GrokClient(api_key="test-key")

        full_id = "grok-4-fast-reasoning-latest"
        assert client._resolve_model(full_id) == full_id


# ============= TOKEN TRACKING TESTS =============

class TestGrokClientTokenTracking:
    """Test token usage tracking across calls"""

    @pytest.mark.asyncio
    async def test_token_tracking_single_call(self):
        """Test token tracking for a single call"""
        client = GrokClient(api_key="test-key")

        mock_response = Mock(
            choices=[Mock(message=Mock(content="Response"))],
            usage=Mock(prompt_tokens=123, completion_tokens=456, total_tokens=579)
        )

        client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        response, tokens = await client.chat("Test prompt")

        assert tokens["prompt"] == 123
        assert tokens["completion"] == 456
        assert tokens["total"] == 579

        await client.close()

    @pytest.mark.asyncio
    async def test_token_tracking_multiple_calls(self):
        """Test token tracking across multiple calls"""
        client = GrokClient(api_key="test-key")

        # Different token counts for each call
        responses = [
            Mock(
                choices=[Mock(message=Mock(content=f"Response {i}"))],
                usage=Mock(prompt_tokens=100 + i, completion_tokens=200 + i, total_tokens=300 + i)
            )
            for i in range(3)
        ]

        client.client.chat.completions.create = AsyncMock(side_effect=responses)

        # Track tokens across calls
        all_tokens = []
        for i in range(3):
            _, tokens = await client.chat(f"Prompt {i}")
            all_tokens.append(tokens)

        # Verify each call tracked separately
        assert all_tokens[0]["total"] == 300
        assert all_tokens[1]["total"] == 301
        assert all_tokens[2]["total"] == 302

        # Verify total
        total_tokens = sum(t["total"] for t in all_tokens)
        assert total_tokens == 903

        await client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
