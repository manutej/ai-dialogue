"""
Basic tests for AI Dialogue Protocol
"""

import pytest
import json
from pathlib import Path

# Test mode config loading
def test_load_mode_configs():
    """Test that all mode configs are valid JSON"""
    modes_dir = Path(__file__).parent.parent / "src" / "modes"

    for mode_file in modes_dir.glob("*.json"):
        with open(mode_file) as f:
            config = json.load(f)

        assert "name" in config
        assert "description" in config
        assert "structure" in config
        assert "participants" in config

        print(f"✓ {mode_file.name} is valid")


def test_mode_prompts():
    """Test that mode prompts are properly structured"""
    modes_dir = Path(__file__).parent.parent / "src" / "modes"

    for mode_file in modes_dir.glob("*.json"):
        with open(mode_file) as f:
            config = json.load(f)

        # Skip dynamic mode (has different structure)
        if config.get("dynamic_generation"):
            continue

        if "prompts" in config:
            for turn_key, turn_config in config["prompts"].items():
                assert "role" in turn_config
                assert "participant" in turn_config
                assert "template" in turn_config

        print(f"✓ {config['name']} prompts are valid")


def test_intelligent_orchestrator():
    """Test IntelligentOrchestrator parsing"""
    from src.intelligent_orchestrator import IntelligentOrchestrator

    orchestrator = IntelligentOrchestrator()

    # Test decomposition parsing
    sample_decomposition = """
    SUBTASKS:
    1. Design API - Complexity: complex
       Description: Create REST API design
       Dependencies: none

    2. Implement handlers - Complexity: moderate
       Description: Implement HTTP handlers
       Dependencies: Design API

    3. Add tests - Complexity: simple
       Description: Write unit tests
       Dependencies: Implement handlers

    LOOP_STRATEGY: one_loop_per_task

    REASONING: Complex API design needs dedicated loop, others are straightforward
    """

    subtasks, strategy = orchestrator.parse_decomposition(sample_decomposition)

    assert len(subtasks) == 3
    assert subtasks[0].name == "Design API"
    assert subtasks[0].complexity == "complex"
    assert strategy.strategy_type == "one_loop_per_task"

    print("✓ IntelligentOrchestrator parsing works")


def test_template_substitution():
    """Test template variable substitution"""
    from src.dynamic_protocol import DynamicProtocolEngine

    engine = DynamicProtocolEngine(None, None, None)

    template = "Analyze <TASK> and build on <PREVIOUS_RESULT>"
    engine.context_store = {
        "TASK": "quantum computing",
        "PREVIOUS_RESULT": "foundational concepts"
    }

    result = engine._substitute_variables(template, engine.context_store)

    assert "quantum computing" in result
    assert "foundational concepts" in result
    assert "<TASK>" not in result
    assert "<PREVIOUS_RESULT>" not in result

    print("✓ Template substitution works")


@pytest.mark.asyncio
async def test_mock_execution():
    """Test protocol execution with mocked clients"""

    class MockClaudeClient:
        async def chat(self, prompt):
            return "Mock Claude response", {"prompt": 10, "completion": 20, "total": 30}

    class MockGrokClient:
        async def chat(self, prompt, model="grok-4-fast"):
            return "Mock Grok response", {"prompt": 15, "completion": 25, "total": 40}

        async def close(self):
            pass

    class MockStateManager:
        def save_turn(self, session_id, turn):
            pass

        def save_conversation(self, conversation):
            pass

    from src.protocol import ProtocolEngine

    claude = MockClaudeClient()
    grok = MockGrokClient()
    state = MockStateManager()

    engine = ProtocolEngine(claude, grok, state)

    # Test that we can load a mode
    config = engine.load_mode("loop")
    assert config["name"] == "loop"

    print("✓ Mock execution works")


if __name__ == "__main__":
    # Run tests directly
    test_load_mode_configs()
    test_mode_prompts()
    test_intelligent_orchestrator()
    test_template_substitution()

    import asyncio
    asyncio.run(test_mock_execution())

    print("\n✅ All tests passed!")
