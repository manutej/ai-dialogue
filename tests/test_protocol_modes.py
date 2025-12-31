"""
Comprehensive Mode Integration Tests - Phase 4A

Tests for all 6 orchestration modes: loop, debate, podcast, pipeline, research-enhanced, dynamic.
Tests end-to-end execution with mock clients to verify orchestration logic.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from pathlib import Path
from src.protocol import ProtocolEngine, Conversation, Turn
from src.state import StateManager
from datetime import datetime


# ============= FIXTURES =============

@pytest.fixture
def temp_sessions_dir(tmp_path):
    """Create temporary sessions directory"""
    return tmp_path / "sessions"


@pytest.fixture
def mock_claude_client():
    """Mock Claude client for testing"""
    class MockClaude:
        async def chat(self, prompt):
            return f"Claude response to: {prompt[:50]}...", {
                "prompt": 100,
                "completion": 200,
                "total": 300
            }
    return MockClaude()


@pytest.fixture
def mock_grok_client():
    """Mock Grok client for testing"""
    class MockGrok:
        async def chat(self, prompt, model="grok-4-fast-reasoning-latest", **kwargs):
            return f"Grok response ({model}) to: {prompt[:50]}...", {
                "prompt": 150,
                "completion": 250,
                "total": 400
            }

        async def close(self):
            pass
    return MockGrok()


@pytest.fixture
def state_manager(temp_sessions_dir):
    """StateManager with temporary directory"""
    return StateManager(sessions_dir=str(temp_sessions_dir))


@pytest.fixture
def protocol_engine(mock_claude_client, mock_grok_client, state_manager):
    """ProtocolEngine with mock clients"""
    return ProtocolEngine(
        mock_claude_client,
        mock_grok_client,
        state_manager,
        max_retries=1,  # Faster tests
        timeout_seconds=5  # Shorter timeout for tests
    )


# ============= LOOP MODE TESTS =============

class TestLoopMode:
    """Test loop mode (8 turns, sequential knowledge building)"""

    def test_loop_mode_configuration(self, protocol_engine):
        """Test that loop mode loads correctly"""
        config = protocol_engine.load_mode("loop")

        assert config["name"] == "loop"
        assert config["structure"] == "sequential"
        assert config["turns"] == 8
        assert len(config["participants"]) == 2
        assert "claude" in config["participants"]
        assert "grok" in config["participants"]

    def test_loop_mode_turn_structure(self, protocol_engine):
        """Test loop mode turn structure and roles"""
        config = protocol_engine.load_mode("loop")
        prompts = config["prompts"]

        # Verify all 8 turns exist
        assert len(prompts) == 8

        # Verify expected roles
        assert prompts["turn_1"]["role"] == "foundation"
        assert prompts["turn_2"]["role"] == "critical_analysis"
        assert prompts["turn_4"]["role"] == "synthesis"
        assert prompts["turn_8"]["role"] == "final_integration"

        # Verify participants alternate appropriately
        assert prompts["turn_1"]["participant"] == "grok"
        assert prompts["turn_2"]["participant"] == "claude"

    @pytest.mark.asyncio
    async def test_loop_mode_context_chain(self, protocol_engine):
        """Test loop mode context chaining across turns"""
        config = protocol_engine.load_mode("loop")

        # Verify context dependencies
        assert config["prompts"]["turn_1"]["context_from"] == []  # Foundation, no deps
        assert config["prompts"]["turn_2"]["context_from"] == [1]  # Builds on turn 1
        assert config["prompts"]["turn_4"]["context_from"] == [1, 2, 3]  # Synthesis of 3 turns
        assert config["prompts"]["turn_8"]["context_from"] == [1, 2, 3, 4, 5, 6, 7]  # All previous


# ============= DEBATE MODE TESTS =============

class TestDebateMode:
    """Test debate mode (6 turns, adversarial analysis)"""

    def test_debate_mode_configuration(self, protocol_engine):
        """Test that debate mode loads correctly"""
        config = protocol_engine.load_mode("debate")

        assert config["name"] == "debate"
        assert config["structure"] == "sequential"
        assert config["turns"] == 6
        assert "participants" in config

    def test_debate_mode_adversarial_structure(self, protocol_engine):
        """Test debate mode adversarial structure"""
        config = protocol_engine.load_mode("debate")
        prompts = config["prompts"]

        # Verify debate structure
        assert len(prompts) == 6

        # Check for adversarial roles
        roles = [prompts[f"turn_{i}"]["role"] for i in range(1, 7)]
        assert "proposition" in roles or "opening_case" in [r.lower() for r in roles]
        assert "verdict" in roles or "synthesis" in roles

    @pytest.mark.asyncio
    async def test_debate_mode_mock_execution(self, protocol_engine):
        """Test debate mode execution with mock clients"""
        # Execute debate mode with limited turns
        conversation = await protocol_engine.run_protocol(
            mode="debate",
            topic="Test debate topic",
            turns=3  # Limit to 3 turns for testing
        )

        assert isinstance(conversation, Conversation)
        assert conversation.mode == "debate"
        assert len(conversation.turns) == 3
        assert all(isinstance(turn, Turn) for turn in conversation.turns)


# ============= PODCAST MODE TESTS =============

class TestPodcastMode:
    """Test podcast mode (10 turns, conversational teaching)"""

    def test_podcast_mode_configuration(self, protocol_engine):
        """Test that podcast mode loads correctly"""
        config = protocol_engine.load_mode("podcast")

        assert config["name"] == "podcast"
        assert config["turns"] == 10
        assert "participants" in config

    def test_podcast_mode_conversational_flow(self, protocol_engine):
        """Test podcast mode conversational flow"""
        config = protocol_engine.load_mode("podcast")
        prompts = config["prompts"]

        # Verify 10 turns
        assert len(prompts) == 10

        # Check for conversational structure
        roles = [prompts[f"turn_{i}"]["role"] for i in range(1, 11)]
        assert any("intro" in r.lower() or "opening" in r.lower() for r in roles)
        assert any("closing" in r.lower() or "takeaway" in r.lower() for r in roles)

    @pytest.mark.asyncio
    async def test_podcast_mode_context_accumulation(self, protocol_engine):
        """Test that podcast mode accumulates context appropriately"""
        config = protocol_engine.load_mode("podcast")

        # Verify context builds up through conversation
        turn_5_context = config["prompts"]["turn_5"]["context_from"]
        turn_10_context = config["prompts"]["turn_10"]["context_from"]

        assert len(turn_10_context) >= len(turn_5_context)


# ============= PIPELINE MODE TESTS =============

class TestPipelineMode:
    """Test pipeline mode (7 stages, workflow execution)"""

    def test_pipeline_mode_configuration(self, protocol_engine):
        """Test that pipeline mode loads correctly"""
        config = protocol_engine.load_mode("pipeline")

        assert config["name"] == "pipeline"
        assert "structure" in config
        assert "turns" in config

    def test_pipeline_mode_linear_flow(self, protocol_engine):
        """Test pipeline mode linear flow structure"""
        config = protocol_engine.load_mode("pipeline")
        prompts = config["prompts"]

        # Verify linear dependency structure
        for i in range(2, len(prompts) + 1):
            turn_key = f"turn_{i}"
            if turn_key in prompts:
                context_from = prompts[turn_key]["context_from"]
                # Pipeline should generally reference previous turn
                assert len(context_from) > 0

    @pytest.mark.asyncio
    async def test_pipeline_mode_execution(self, protocol_engine):
        """Test pipeline mode execution"""
        # Execute pipeline mode with limited turns
        conversation = await protocol_engine.run_protocol(
            mode="pipeline",
            topic="Test pipeline",
            turns=4  # Limit to 4 stages for testing
        )

        assert conversation.mode == "pipeline"
        assert len(conversation.turns) == 4


# ============= RESEARCH-ENHANCED MODE TESTS =============

class TestResearchEnhancedMode:
    """Test research-enhanced mode (6 turns, tools integration)"""

    def test_research_enhanced_mode_configuration(self, protocol_engine):
        """Test that research-enhanced mode loads correctly"""
        config = protocol_engine.load_mode("research-enhanced")

        assert config["name"] == "research-enhanced"
        assert config["turns"] == 6
        assert "participants" in config
        assert config["participants"] == ["claude", "grok"]

    def test_research_enhanced_mode_features(self, protocol_engine):
        """Test research-enhanced mode special features"""
        config = protocol_engine.load_mode("research-enhanced")

        # Check metadata for features
        metadata = config.get("metadata", {})
        features = metadata.get("features", [])

        # Should mention advanced features
        assert len(features) > 0 or "research" in config["description"].lower()

    @pytest.mark.asyncio
    async def test_research_enhanced_mode_with_tools(self, protocol_engine):
        """Test research-enhanced mode acknowledges tools"""
        config = protocol_engine.load_mode("research-enhanced")
        prompts = config["prompts"]

        # Check if any turns reference tools/collections/files
        has_tool_references = False
        for turn_key, turn_config in prompts.items():
            if any(key in turn_config for key in ["server_side_tools", "collections", "files"]):
                has_tool_references = True
                break

        assert has_tool_references


# ============= DYNAMIC MODE TESTS =============

class TestDynamicMode:
    """Test dynamic mode (adaptive, mixed structure)"""

    def test_dynamic_mode_configuration(self, protocol_engine):
        """Test that dynamic mode loads correctly"""
        config = protocol_engine.load_mode("dynamic")

        assert config["name"] == "dynamic"
        assert "description" in config

    def test_dynamic_mode_mixed_structure(self, protocol_engine):
        """Test dynamic mode has mixed/adaptive structure"""
        config = protocol_engine.load_mode("dynamic")

        # Dynamic mode should have flexible structure
        structure = config.get("structure")

        # Should be "mixed" or have dynamic_generation flag
        assert structure == "mixed" or config.get("dynamic_generation") == True

    @pytest.mark.asyncio
    async def test_dynamic_mode_phases(self, protocol_engine):
        """Test dynamic mode phase structure"""
        config = protocol_engine.load_mode("dynamic")

        # Dynamic mode uses phases instead of simple turns
        has_phases = "phases" in config
        has_prompts = "prompts" in config

        # Should have one or the other
        assert has_phases or has_prompts


# ============= CROSS-MODE TESTS =============

class TestCrossModeIntegration:
    """Test features that should work across all modes"""

    @pytest.mark.asyncio
    async def test_all_modes_load_successfully(self, protocol_engine):
        """Test that all 6 modes load without errors"""
        modes = ["loop", "debate", "podcast", "pipeline", "research-enhanced", "dynamic"]

        for mode_name in modes:
            config = protocol_engine.load_mode(mode_name)
            assert config is not None
            assert "name" in config
            assert config["name"] == mode_name

    @pytest.mark.asyncio
    async def test_all_modes_have_required_fields(self, protocol_engine):
        """Test that all modes have required configuration fields"""
        modes = ["loop", "debate", "podcast", "pipeline", "research-enhanced", "dynamic"]

        for mode_name in modes:
            config = protocol_engine.load_mode(mode_name)

            # Required fields
            assert "name" in config
            assert "description" in config
            assert "structure" in config
            assert "participants" in config

    @pytest.mark.asyncio
    async def test_cost_tracking_across_modes(self, protocol_engine):
        """Test that cost tracking works for different modes"""
        # Execute partial conversations in different modes
        for mode_name in ["loop", "debate"]:
            conversation = await protocol_engine.run_protocol(
                mode=mode_name,
                topic=f"Test {mode_name}",
                turns=2  # Limit to 2 turns for speed
            )

            # Should have cost information
            assert hasattr(conversation, 'total_cost')
            assert conversation.total_cost >= 0

            # Each turn should have cost
            for turn in conversation.turns:
                assert hasattr(turn, 'cost')
                assert turn.cost >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
