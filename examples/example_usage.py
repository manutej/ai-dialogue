#!/usr/bin/env python3
"""
Example usage of AI Dialogue Protocol

Demonstrates both CLI and programmatic usage
"""

import asyncio
from src import (
    ProtocolEngine,
    DynamicProtocolEngine,
    ClaudeClient,
    GrokClient,
    StateManager,
    CycleConfig
)


async def example_loop_mode():
    """Example: Deep research using loop mode"""
    print("\n=== Example 1: Loop Mode ===")

    claude = ClaudeClient()
    grok = GrokClient()
    state = StateManager()

    engine = ProtocolEngine(claude, grok, state)

    conversation = await engine.run_protocol(
        mode="loop",
        topic="Quantum error correction techniques",
        turns=8
    )

    print(f"Completed {len(conversation.turns)} turns")
    state.save_conversation(conversation)
    state.export_markdown(conversation)
    print(f"Session saved: {conversation.session_id}")


async def example_debate_mode():
    """Example: Explore tradeoffs using debate mode"""
    print("\n=== Example 2: Debate Mode ===")

    claude = ClaudeClient()
    grok = GrokClient()
    state = StateManager()

    engine = ProtocolEngine(claude, grok, state)

    conversation = await engine.run_protocol(
        mode="debate",
        topic="Microservices vs Monolithic Architecture for Startups"
    )

    print(f"Debate completed with {len(conversation.turns)} turns")
    state.export_markdown(conversation)


async def example_pipeline_mode():
    """Example: Systematic task completion using pipeline mode"""
    print("\n=== Example 3: Pipeline Mode ===")

    claude = ClaudeClient()
    grok = GrokClient()
    state = StateManager()

    engine = ProtocolEngine(claude, grok, state)

    conversation = await engine.run_protocol(
        mode="pipeline",
        topic="Build a Python CLI tool for JSON data transformation"
    )

    print(f"Pipeline completed: {len(conversation.turns)} stages")
    state.export_markdown(conversation)


async def example_dynamic_mode():
    """Example: Intelligent decomposition using dynamic mode"""
    print("\n=== Example 4: Dynamic Mode ===")

    claude = ClaudeClient()
    grok = GrokClient()
    state = StateManager()

    engine = DynamicProtocolEngine(claude, grok, state)

    conversation = await engine.run_dynamic_protocol(
        mode="dynamic",
        task="Design and implement a distributed rate limiting system",
        variables={
            "DOMAIN": "API gateway",
            "SCALE": "100K requests/second"
        }
    )

    print(f"Dynamic workflow completed: {len(conversation.turns)} turns (generated dynamically)")
    state.export_markdown(conversation)


async def example_pipeline_with_cycles():
    """Example: Iterative refinement with cycles"""
    print("\n=== Example 5: Pipeline with Cycles ===")

    claude = ClaudeClient()
    grok = GrokClient()
    state = StateManager()

    engine = DynamicProtocolEngine(claude, grok, state)

    conversation = await engine.run_dynamic_protocol(
        mode="pipeline",
        task="Design RESTful API for e-commerce platform",
        cycle_config=CycleConfig(
            max_cycles=3,
            convergence_threshold=0.85
        )
    )

    print(f"Cycles completed: {conversation.metadata.get('cycles', 0)}")
    print(f"Total turns: {len(conversation.turns)}")
    state.export_markdown(conversation)


async def example_custom_workflow():
    """Example: Programmatic custom workflow"""
    print("\n=== Example 6: Custom Programmatic Workflow ===")

    from src.intelligent_orchestrator import IntelligentOrchestrator

    # Create orchestrator
    orchestrator = IntelligentOrchestrator()

    # Simulate decomposition response
    decomposition = """
    SUBTASKS:
    1. Research existing solutions - Complexity: simple
       Description: Survey existing rate limiting algorithms
       Dependencies: none

    2. Design algorithm - Complexity: complex
       Description: Design distributed rate limiting algorithm
       Dependencies: Research existing solutions

    3. Implement prototype - Complexity: moderate
       Description: Implement prototype in Python
       Dependencies: Design algorithm

    4. Write tests - Complexity: simple
       Description: Write unit and integration tests
       Dependencies: Implement prototype

    LOOP_STRATEGY: mixed

    REASONING: Research and tests are simple, design needs dedicated loop, implementation is moderate
    """

    # Parse decomposition
    subtasks, strategy = orchestrator.parse_decomposition(decomposition)

    print(f"Decomposed into {len(subtasks)} subtasks")
    print(f"Strategy: {strategy.strategy_type}")
    print(f"Estimated turns: {strategy.total_estimated_turns}")

    # Generate execution prompts
    prompts = orchestrator.generate_execution_prompts()
    print(f"Generated {len(prompts)} dynamic prompts for execution")

    for i, prompt_config in enumerate(prompts[:3]):  # Show first 3
        print(f"\nPrompt {i+1}: {prompt_config['role']}")
        print(f"  Participant: {prompt_config['participant']}")


def cli_examples():
    """Show CLI usage examples"""
    print("\n=== CLI Usage Examples ===\n")

    examples = [
        ("Loop Mode", "ai-dialogue run --mode loop --topic 'quantum computing' --turns 8"),
        ("Debate Mode", "ai-dialogue run --mode debate --topic 'Cloud vs On-Premise'"),
        ("Podcast Mode", "ai-dialogue run --mode podcast --topic 'AI safety explained'"),
        ("Pipeline Mode", "ai-dialogue run --mode pipeline --topic 'Build auth service'"),
        ("Dynamic Mode", "ai-dialogue run --mode dynamic --topic 'Design distributed system'"),
        ("With Cycles", "ai-dialogue run --mode pipeline --topic 'API design' --cycles 3"),
        ("List Sessions", "ai-dialogue list"),
        ("Export Session", "ai-dialogue export 20250109-143052 --output report.md"),
        ("List Modes", "ai-dialogue modes"),
    ]

    for name, command in examples:
        print(f"{name}:")
        print(f"  {command}\n")


if __name__ == "__main__":
    print("AI Dialogue Protocol - Usage Examples")
    print("=" * 50)

    # Show CLI examples
    cli_examples()

    # Ask if user wants to run programmatic examples
    print("\nProgrammatic examples require API keys and will execute real calls.")
    response = input("Run programmatic examples? (y/n): ")

    if response.lower() == 'y':
        # Run async examples
        asyncio.run(example_custom_workflow())

        # Uncomment to run full examples (will use API credits)
        # asyncio.run(example_loop_mode())
        # asyncio.run(example_debate_mode())
        # asyncio.run(example_pipeline_mode())
        # asyncio.run(example_dynamic_mode())
        # asyncio.run(example_pipeline_with_cycles())

    print("\n✅ Examples complete!")
