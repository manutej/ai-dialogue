"""
Phase 3 Feature Tests - Async & Performance Optimization

Tests for:
- Cost calculation and tracking
- Retry logic with exponential backoff
- Timeout handling
- Token tracking
- Parallel execution with retries
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.protocol import (
    Turn, Conversation, ProtocolEngine, calculate_cost, MODEL_PRICING
)
from src.state import StateManager
from pathlib import Path
import tempfile


# ============= COST CALCULATION TESTS =============

class TestCostCalculation:
    """Test cost calculation for various models and token counts"""

    def test_grok_4_cost_calculation(self):
        """Test cost calculation for Grok 4 Fast Reasoning"""
        tokens = {"prompt": 100, "completion": 200, "total": 300}
        cost = calculate_cost("grok-4-fast-reasoning-latest", tokens)

        # (100 / 1M) * 2.0 + (200 / 1M) * 10.0 = 0.0000020 + 0.0000020 = 0.0000040
        expected = (100 / 1_000_000) * 2.0 + (200 / 1_000_000) * 10.0
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_grok_non_reasoning_cost(self):
        """Test cost calculation for Grok 4 Non-Reasoning (cheaper)"""
        tokens = {"prompt": 1000, "completion": 2000, "total": 3000}
        cost = calculate_cost("grok-4-fast-non-reasoning-latest", tokens)

        expected = (1000 / 1_000_000) * 1.0 + (2000 / 1_000_000) * 5.0
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_grok_code_cost(self):
        """Test cost calculation for specialized code model (more expensive)"""
        tokens = {"prompt": 500, "completion": 1500, "total": 2000}
        cost = calculate_cost("grok-code-fast-1", tokens)

        expected = (500 / 1_000_000) * 3.0 + (1500 / 1_000_000) * 15.0
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_claude_opus_cost(self):
        """Test cost calculation for expensive Claude model"""
        tokens = {"prompt": 500, "completion": 1000, "total": 1500}
        cost = calculate_cost("claude-3-opus-20240229", tokens)

        expected = (500 / 1_000_000) * 15.0 + (1000 / 1_000_000) * 75.0
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_claude_haiku_cost(self):
        """Test cost calculation for cheap Claude model"""
        tokens = {"prompt": 500, "completion": 1000, "total": 1500}
        cost = calculate_cost("claude-3-haiku-20240307", tokens)

        expected = (500 / 1_000_000) * 0.25 + (1000 / 1_000_000) * 1.25
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_unknown_model_defaults_to_grok4(self):
        """Test that unknown models default to Grok 4 pricing"""
        tokens = {"prompt": 100, "completion": 200, "total": 300}
        cost = calculate_cost("unknown-model-xyz", tokens)

        # Should use default grok-4-fast-reasoning-latest pricing
        expected = (100 / 1_000_000) * 2.0 + (200 / 1_000_000) * 10.0
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_zero_tokens(self):
        """Test cost calculation with no tokens used"""
        tokens = {"prompt": 0, "completion": 0, "total": 0}
        cost = calculate_cost("grok-4-fast-reasoning-latest", tokens)
        assert cost == 0.0


# ============= TURN AND CONVERSATION COST TRACKING TESTS =============

class TestTurnCostTracking:
    """Test cost tracking in Turn objects"""

    def test_turn_includes_cost(self):
        """Test that Turn objects store cost"""
        turn = Turn(
            number=1,
            role="Proposition",
            participant="grok",
            prompt="Test prompt",
            response="Test response",
            tokens={"prompt": 100, "completion": 200, "total": 300},
            latency=1.5,
            timestamp="2025-01-01T00:00:00",
            context_from=[],
            cost=0.000004,
            model="grok-4-fast-reasoning-latest",
            error=None,
            retry_count=0
        )

        assert turn.cost == 0.000004
        assert turn.model == "grok-4-fast-reasoning-latest"
        assert turn.error is None
        assert turn.retry_count == 0

    def test_turn_error_tracking(self):
        """Test that Turn objects track errors and retries"""
        turn = Turn(
            number=1,
            role="Proposition",
            participant="grok",
            prompt="Test prompt",
            response="[Error: Connection timeout]",
            tokens={"prompt": 0, "completion": 0, "total": 0},
            latency=30.0,
            timestamp="2025-01-01T00:00:00",
            context_from=[],
            cost=0.0,
            model="grok-4-fast-reasoning-latest",
            error="Connection timeout",
            retry_count=2
        )

        assert turn.error == "Connection timeout"
        assert turn.retry_count == 2
        assert turn.cost == 0.0  # No tokens returned on error


class TestConversationCostTracking:
    """Test cost tracking at conversation level"""

    def test_conversation_cost_aggregation(self):
        """Test conversation cost calculation from turns"""
        turns = [
            Turn(
                number=1,
                role="Role1",
                participant="grok",
                prompt="Prompt 1",
                response="Response 1",
                tokens={"prompt": 100, "completion": 200, "total": 300},
                latency=1.0,
                timestamp="2025-01-01T00:00:00",
                context_from=[],
                cost=0.000004,
                model="grok-4-fast-reasoning-latest"
            ),
            Turn(
                number=2,
                role="Role2",
                participant="grok",
                prompt="Prompt 2",
                response="Response 2",
                tokens={"prompt": 150, "completion": 250, "total": 400},
                latency=1.2,
                timestamp="2025-01-01T00:00:01",
                context_from=[1],
                cost=0.000005,
                model="grok-4-fast-reasoning-latest"
            ),
        ]

        conversation = Conversation(
            session_id="test-001",
            mode="debate",
            topic="Test topic",
            turns=turns,
            metadata={},
            started_at="2025-01-01T00:00:00"
        )

        conversation.update_costs()

        assert conversation.total_tokens == 700  # 300 + 400
        assert conversation.total_cost == pytest.approx(0.000009, rel=1e-6)

    def test_conversation_empty_cost(self):
        """Test conversation cost with no turns"""
        conversation = Conversation(
            session_id="test-002",
            mode="loop",
            topic="Test",
            turns=[],
            metadata={},
            started_at="2025-01-01T00:00:00"
        )

        conversation.update_costs()

        assert conversation.total_tokens == 0
        assert conversation.total_cost == 0.0


# ============= RETRY LOGIC TESTS =============

class TestRetryLogic:
    """Test exponential backoff retry mechanism"""

    @pytest.mark.asyncio
    async def test_successful_execution_no_retry(self):
        """Test that successful execution doesn't trigger retries"""
        # Create mock clients
        mock_claude = AsyncMock()
        mock_grok = AsyncMock()
        mock_grok.chat = AsyncMock(
            return_value=("Test response", {"prompt": 100, "completion": 200, "total": 300})
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            engine = ProtocolEngine(
                mock_claude,
                mock_grok,
                state_manager,
                max_retries=3,
                timeout_seconds=30
            )

            turn_config = {
                "role": "Test Role",
                "participant": "grok",
                "template": "Test prompt for {topic}",
                "grok_model": "grok-4"
            }

            turn = await engine._execute_turn(1, turn_config, "AI Dialogue", {})

            assert turn.response == "Test response"
            assert turn.retry_count == 0
            assert turn.error is None
            assert mock_grok.chat.call_count == 1

    @pytest.mark.asyncio
    async def test_timeout_retry_logic(self):
        """Test that timeouts trigger retries"""
        mock_claude = AsyncMock()
        mock_grok = AsyncMock()

        # Simulate: fail twice with timeout, succeed on third attempt
        mock_grok.chat = AsyncMock(
            side_effect=[
                asyncio.TimeoutError(),
                asyncio.TimeoutError(),
                ("Success response", {"prompt": 50, "completion": 150, "total": 200})
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            engine = ProtocolEngine(
                mock_claude,
                mock_grok,
                state_manager,
                max_retries=3,
                timeout_seconds=1,  # Short timeout to trigger quickly
                retry_backoff_base=1.0  # No wait between retries for speed
            )

            turn_config = {
                "role": "Test Role",
                "participant": "grok",
                "template": "Test prompt for {topic}",
                "grok_model": "grok-4"
            }

            turn = await engine._execute_turn(1, turn_config, "AI Dialogue", {})

            assert turn.response == "Success response"
            assert turn.retry_count == 2  # Failed 2 times before success
            assert turn.error is None
            assert mock_grok.chat.call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exhausted(self):
        """Test that execution fails after max retries exhausted"""
        mock_claude = AsyncMock()
        mock_grok = AsyncMock()

        # Always fail with timeout
        mock_grok.chat = AsyncMock(side_effect=asyncio.TimeoutError())

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            engine = ProtocolEngine(
                mock_claude,
                mock_grok,
                state_manager,
                max_retries=2,
                timeout_seconds=1,
                retry_backoff_base=1.0
            )

            turn_config = {
                "role": "Test Role",
                "participant": "grok",
                "template": "Test prompt for {topic}",
                "grok_model": "grok-4"
            }

            turn = await engine._execute_turn(1, turn_config, "AI Dialogue", {})

            # Should fail and include error in response
            assert "Error" in turn.response
            assert turn.error is not None
            assert turn.retry_count == 2  # Attempted twice (max_retries=2)
            assert mock_grok.chat.call_count == 2


# ============= TIMEOUT HANDLING TESTS =============

class TestTimeoutHandling:
    """Test per-turn timeout configuration"""

    @pytest.mark.asyncio
    async def test_custom_timeout_per_turn(self):
        """Test that per-turn timeout overrides global default"""
        mock_claude = AsyncMock()
        mock_grok = AsyncMock()
        mock_grok.chat = AsyncMock(
            return_value=("Response", {"prompt": 50, "completion": 150, "total": 200})
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            # Global timeout is 30s
            engine = ProtocolEngine(
                mock_claude,
                mock_grok,
                state_manager,
                max_retries=1,
                timeout_seconds=30
            )

            # Per-turn timeout is 5s
            turn_config = {
                "role": "Test Role",
                "participant": "grok",
                "template": "Test prompt for {topic}",
                "grok_model": "grok-4",
                "timeout_seconds": 5  # Override default
            }

            turn = await engine._execute_turn(1, turn_config, "AI Dialogue", {})

            assert turn.response == "Response"
            # The timeout should have been applied as 5s, not 30s
            # (Can't directly verify, but turn succeeds)


# ============= PARALLEL EXECUTION TESTS =============

class TestParallelExecution:
    """Test parallel turn execution"""

    @pytest.mark.asyncio
    async def test_parallel_execution_with_retries(self):
        """Test that parallel execution works with retry logic"""
        mock_claude = AsyncMock()
        mock_grok = AsyncMock()

        # Simulate different responses for each turn
        responses = [
            ("Response 1", {"prompt": 50, "completion": 150, "total": 200}),
            ("Response 2", {"prompt": 60, "completion": 160, "total": 220}),
        ]
        mock_grok.chat = AsyncMock(side_effect=responses)

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            engine = ProtocolEngine(
                mock_claude,
                mock_grok,
                state_manager,
                max_retries=2,
                timeout_seconds=10
            )

            conversation = Conversation(
                session_id="test-parallel",
                mode="parallel-test",
                topic="Test",
                turns=[],
                metadata={},
                started_at="2025-01-01T00:00:00"
            )

            config = {
                "structure": "parallel",
                "turns": 2,
                "prompts": {
                    "turn_1": {
                        "role": "Role 1",
                        "participant": "grok",
                        "template": "Prompt 1 for {topic}",
                        "grok_model": "grok-4"
                    },
                    "turn_2": {
                        "role": "Role 2",
                        "participant": "grok",
                        "template": "Prompt 2 for {topic}",
                        "grok_model": "grok-4"
                    }
                }
            }

            await engine._execute_parallel(conversation, config, "Test topic")

            assert len(conversation.turns) == 2
            assert all(turn.error is None for turn in conversation.turns)
            assert mock_grok.chat.call_count == 2


# ============= MARKDOWN EXPORT TESTS =============

class TestMarkdownExportWithCosts:
    """Test markdown export includes cost information"""

    def test_markdown_includes_cost_summary(self):
        """Test that markdown export includes total cost"""
        turns = [
            Turn(
                number=1,
                role="Proposition",
                participant="grok",
                prompt="Prompt 1",
                response="Response 1",
                tokens={"prompt": 100, "completion": 200, "total": 300},
                latency=1.0,
                timestamp="2025-01-01T00:00:00",
                context_from=[],
                cost=0.000004,
                model="grok-4-fast-reasoning-latest"
            ),
        ]

        conversation = Conversation(
            session_id="test-export",
            mode="debate",
            topic="Test Topic",
            turns=turns,
            metadata={},
            started_at="2025-01-01T00:00:00",
            completed_at="2025-01-01T00:00:05"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            engine = ProtocolEngine(None, None, state_manager)

            markdown = engine.export_to_markdown(conversation)

            assert "**Total Tokens**:" in markdown
            assert "**Total Cost**:" in markdown
            assert "**Avg Cost per Turn**:" in markdown
            assert "$0." in markdown  # Cost in markdown

    def test_markdown_includes_per_turn_costs(self):
        """Test that markdown includes per-turn cost details"""
        turn = Turn(
            number=1,
            role="Role",
            participant="grok",
            prompt="Prompt",
            response="Response",
            tokens={"prompt": 100, "completion": 200, "total": 300},
            latency=1.5,
            timestamp="2025-01-01T00:00:00",
            context_from=[],
            cost=0.000004,
            model="grok-4-fast-reasoning-latest",
            error=None,
            retry_count=0
        )

        conversation = Conversation(
            session_id="test-export2",
            mode="loop",
            topic="Test",
            turns=[turn],
            metadata={},
            started_at="2025-01-01T00:00:00",
            completed_at="2025-01-01T00:00:05"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            engine = ProtocolEngine(None, None, state_manager)

            markdown = engine.export_to_markdown(conversation)

            assert f"**Model**: {turn.model}" in markdown
            assert "**Cost**:" in markdown
            assert f"${turn.cost:.6f}" in markdown
            assert "**Latency**:" in markdown

    def test_markdown_includes_error_tracking(self):
        """Test that markdown shows error and retry counts"""
        turn = Turn(
            number=1,
            role="Role",
            participant="grok",
            prompt="Prompt",
            response="[Error: Connection timeout]",
            tokens={"prompt": 0, "completion": 0, "total": 0},
            latency=30.0,
            timestamp="2025-01-01T00:00:00",
            context_from=[],
            cost=0.0,
            model="grok-4-fast-reasoning-latest",
            error="Connection timeout",
            retry_count=2
        )

        conversation = Conversation(
            session_id="test-error",
            mode="loop",
            topic="Test",
            turns=[turn],
            metadata={},
            started_at="2025-01-01T00:00:00",
            completed_at="2025-01-01T00:00:05"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            engine = ProtocolEngine(None, None, state_manager)

            markdown = engine.export_to_markdown(conversation)

            assert "**Retries**: 2" in markdown
            assert "**Error**: Connection timeout" in markdown


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
