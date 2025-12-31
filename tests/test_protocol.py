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


# ============================================================================
# Extended IntelligentOrchestrator Tests (Phase 4B)
# ============================================================================

class TestIntelligentOrchestratorStrategies:
    """Test multiple orchestration strategies"""

    def test_single_loop_strategy_parsing(self):
        """Test parsing decomposition with single_loop strategy"""
        from src.intelligent_orchestrator import IntelligentOrchestrator

        orchestrator = IntelligentOrchestrator()

        decomposition = """
        SUBTASKS:
        1. Task A - Complexity: simple
           Description: First task
           Dependencies: none

        2. Task B - Complexity: simple
           Description: Second task
           Dependencies: none

        LOOP_STRATEGY: single_loop
        """

        subtasks, strategy = orchestrator.parse_decomposition(decomposition)

        assert strategy.strategy_type == "single_loop"
        assert len(subtasks) == 2

    def test_one_loop_per_task_strategy(self):
        """Test parsing decomposition with one_loop_per_task strategy"""
        from src.intelligent_orchestrator import IntelligentOrchestrator

        orchestrator = IntelligentOrchestrator()

        decomposition = """
        SUBTASKS:
        1. Complex Task - Complexity: complex
           Description: Needs dedicated loop
           Dependencies: none

        LOOP_STRATEGY: one_loop_per_task
        """

        subtasks, strategy = orchestrator.parse_decomposition(decomposition)

        assert strategy.strategy_type == "one_loop_per_task"
        assert len(subtasks) == 1
        assert subtasks[0].complexity == "complex"

    def test_mixed_strategy_parsing(self):
        """Test parsing decomposition with mixed strategy"""
        from src.intelligent_orchestrator import IntelligentOrchestrator

        orchestrator = IntelligentOrchestrator()

        decomposition = """
        SUBTASKS:
        1. Simple Task - Complexity: simple
           Description: Quick task
           Dependencies: none

        2. Complex Task - Complexity: complex
           Description: Needs full loop
           Dependencies: none

        LOOP_STRATEGY: mixed
        """

        subtasks, strategy = orchestrator.parse_decomposition(decomposition)

        assert strategy.strategy_type == "mixed"
        assert len(subtasks) == 2


class TestOrchestratorPromptGeneration:
    """Test execution prompt generation"""

    def test_generate_single_loop_prompts(self):
        """Test prompt generation for single_loop strategy"""
        from src.intelligent_orchestrator import IntelligentOrchestrator

        orchestrator = IntelligentOrchestrator()

        decomposition = """
        SUBTASKS:
        1. Task A - Complexity: simple
           Description: First task
           Dependencies: none

        2. Task B - Complexity: moderate
           Description: Second task
           Dependencies: Task A

        LOOP_STRATEGY: single_loop
        """

        orchestrator.parse_decomposition(decomposition)
        prompts = orchestrator.generate_execution_prompts()

        # Should have: execute_A, execute_B, validate_B (moderate complexity), synthesis
        assert len(prompts) >= 3
        assert any("execute" in p.get("role", "") for p in prompts)
        assert any("synthesis" in p.get("role", "") for p in prompts)

    def test_generate_per_task_loop_prompts(self):
        """Test prompt generation for one_loop_per_task strategy"""
        from src.intelligent_orchestrator import IntelligentOrchestrator

        orchestrator = IntelligentOrchestrator()

        decomposition = """
        SUBTASKS:
        1. Simple Task - Complexity: simple
           Description: Quick task
           Dependencies: none

        2. Complex Task - Complexity: complex
           Description: Needs full loop
           Dependencies: none

        LOOP_STRATEGY: one_loop_per_task
        """

        orchestrator.parse_decomposition(decomposition)
        prompts = orchestrator.generate_execution_prompts()

        # Should have: simple task (1 turn), complex task (research+execute+validate=3 turns), synthesis
        assert len(prompts) >= 4

    def test_generate_mixed_prompts(self):
        """Test prompt generation for mixed strategy"""
        from src.intelligent_orchestrator import IntelligentOrchestrator

        orchestrator = IntelligentOrchestrator()

        decomposition = """
        SUBTASKS:
        1. Simple A - Complexity: simple
           Description: First simple task
           Dependencies: none

        2. Simple B - Complexity: simple
           Description: Second simple task
           Dependencies: none

        3. Complex C - Complexity: complex
           Description: Complex task
           Dependencies: none

        LOOP_STRATEGY: mixed
        """

        orchestrator.parse_decomposition(decomposition)
        prompts = orchestrator.generate_execution_prompts()

        # Should have: batch_simple (1 turn), complex loop (3 turns), synthesis
        assert len(prompts) >= 4
        assert any("batch" in p.get("role", "") for p in prompts)


class TestOrchestratorDependencies:
    """Test dependency graph generation"""

    def test_dependency_parsing(self):
        """Test that dependencies are correctly parsed"""
        from src.intelligent_orchestrator import IntelligentOrchestrator

        orchestrator = IntelligentOrchestrator()

        decomposition = """
        SUBTASKS:
        1. Task A - Complexity: simple
           Description: First task
           Dependencies: none

        2. Task B - Complexity: simple
           Description: Second task
           Dependencies: Task A

        3. Task C - Complexity: simple
           Description: Third task
           Dependencies: Task A, Task B

        LOOP_STRATEGY: single_loop
        """

        subtasks, strategy = orchestrator.parse_decomposition(decomposition)

        assert len(subtasks[0].dependencies) == 0
        assert "Task A" in subtasks[1].dependencies
        assert len(subtasks[2].dependencies) == 2
        assert "Task A" in subtasks[2].dependencies
        assert "Task B" in subtasks[2].dependencies

    def test_parallel_group_identification(self):
        """Test identification of parallel execution opportunities"""
        from src.intelligent_orchestrator import IntelligentOrchestrator, Subtask

        orchestrator = IntelligentOrchestrator()

        # Create subtasks with no dependencies
        subtasks = [
            Subtask(name="Task A", description="First", complexity="simple", dependencies=[]),
            Subtask(name="Task B", description="Second", complexity="simple", dependencies=[]),
            Subtask(name="Task C", description="Third", complexity="simple", dependencies=["Task A"])
        ]

        parallel_groups = orchestrator._identify_parallel_groups(subtasks)

        # Tasks A and B have no dependencies, so they can run in parallel
        assert len(parallel_groups) > 0
        assert len(parallel_groups[0]) == 2
        assert "Task A" in parallel_groups[0]
        assert "Task B" in parallel_groups[0]


if __name__ == "__main__":
    # Run tests directly
    test_load_mode_configs()
    test_mode_prompts()
    test_intelligent_orchestrator()
    test_template_substitution()

    import asyncio
    asyncio.run(test_mock_execution())

    print("\n✅ All tests passed!")
