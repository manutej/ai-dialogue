# Core Architecture Specification

**Version**: 1.0
**Created**: 2025-01-13
**Status**: Implementation Ready
**Priority**: CRITICAL (Foundation for all features)

---

## 🎯 Purpose

Define the foundational architecture for **model-agnostic, asynchronous, multi-agent dialogue orchestration** that enables mixture-of-experts patterns in a task-agnostic framework.

---

## 📋 Overview

The AI Dialogue system orchestrates conversations between multiple AI models using configurable interaction patterns. The architecture prioritizes:

1. **Model Agnosticism** - Works with any LLM via abstraction layers
2. **Async Excellence** - Non-blocking I/O enables parallel execution
3. **Mixture of Experts** - Route tasks to optimal models
4. **Flexible Modes** - Declarative configuration, not imperative code
5. **Production Ready** - Observable, testable, maintainable

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    CLI / API Interface                   │
│                  (User-facing entry points)              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Orchestration Engine                    │
│   • Protocol execution (sequential/parallel/mixed)      │
│   • Mode configuration loader                           │
│   • Context management                                  │
│   • Turn coordination                                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Model Abstraction Layer                │
│   • LangChain integration (v0.3+)                       │
│   • Model registry & capabilities                       │
│   • Routing logic (task → optimal model)                │
│   • Unified async interface                             │
└─────────────────────────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
┌─────────────────────┐   ┌─────────────────────┐
│   Model Adapters    │   │   Model Adapters    │
│   • Grok (XAI)      │   │   • Claude (API)    │
│   • OpenAI          │   │   • Gemini          │
│   • Anthropic       │   │   • Custom Models   │
└─────────────────────┘   └─────────────────────┘
                │                     │
                ▼                     ▼
┌─────────────────────────────────────────────────────────┐
│                     External APIs                        │
│         (Grok, Claude, OpenAI, Gemini, etc.)            │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Feature 1: Model Abstraction Layer

### User Scenario

> "As a developer, I want to add support for GPT-5 without modifying core orchestration code, so the system remains maintainable and extensible."

### Success Criteria

#### SC1.1: LangChain Integration ✅

**Requirement**: Use LangChain v0.3+ as primary abstraction layer

**Measurable**:
- All model interactions go through LangChain `BaseChatModel` interface
- Zero direct API client usage in orchestration code
- Custom models require only adapter implementation

**Test**:
```python
# Can create dialogue using any LangChain-compatible model
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

dialogue = Dialogue(models={
    "reasoner": ChatOpenAI(model="gpt-4"),
    "critic": ChatAnthropic(model="claude-3-opus"),
    "synthesizer": ChatGoogleGenerativeAI(model="gemini-pro")
})
```

**Acceptance**: Adding new model requires ≤50 lines adapter code, 0 core changes

---

#### SC1.2: Model Registry ✅

**Requirement**: Central registry of available models and their capabilities

**Measurable**:
- Registry stores: name, capabilities, cost, latency, context limits
- Models self-describe capabilities (reasoning, vision, code, etc.)
- Orchestrator queries registry for routing decisions

**Test**:
```python
registry = ModelRegistry()

# Query capabilities
best_reasoner = registry.get_best_model(capability="reasoning")
assert best_reasoner.name == "grok-4"

# Cost-aware selection
cheapest = registry.get_cheapest_model(capability="analysis")
assert cheapest.cost_per_million < 5.0
```

**Acceptance**: Can select optimal model based on capability + constraints

---

#### SC1.3: Unified Async Interface ✅

**Requirement**: All models expose consistent async chat interface

**Measurable**:
- Single `async def chat(prompt, context, **kwargs)` method
- Streaming support via `async def stream(prompt, context, **kwargs)`
- Token usage tracking built-in

**Test**:
```python
# Any model works with same interface
for model in [grok, claude, gpt4]:
    response, tokens = await model.chat(
        prompt="Explain quantum entanglement",
        context=conversation.history,
        temperature=0.7
    )
    assert isinstance(response, str)
    assert "prompt" in tokens and "completion" in tokens
```

**Acceptance**: Swapping models requires changing 1 line of config, 0 code changes

---

#### SC1.4: Graceful Fallbacks ✅

**Requirement**: System continues when primary model unavailable

**Measurable**:
- Define fallback chain per capability
- Automatic retry with fallback on failure
- User notified of model substitution

**Test**:
```python
config = ModelConfig(
    primary="grok-4",
    fallbacks=["grok-3", "claude-sonnet", "gpt-4"]
)

# Simulate primary failure
with mock_grok_failure():
    response = await orchestrator.execute_turn(config)
    # Should succeed using fallback
    assert response.model_used == "grok-3"
```

**Acceptance**: 0 dialogue failures due to single model outage

---

## 🎯 Feature 2: Async Orchestration Engine

### User Scenario

> "As a researcher, I want parallel execution of independent analysis tasks, so a 10-turn dialogue completes in 30 seconds instead of 5 minutes."

### Success Criteria

#### SC2.1: Non-Blocking I/O ✅

**Requirement**: Zero blocking calls in critical paths

**Measurable**:
- All I/O uses asyncio primitives
- No `time.sleep()`, `requests.get()`, or blocking subprocess calls
- Event loop never blocks >100ms

**Test**:
```python
# Instrument event loop
with event_loop_monitor() as monitor:
    await orchestrator.run_dialogue(mode="loop", turns=8)

    assert monitor.max_block_time < 0.1  # 100ms
    assert monitor.total_blocked_time < 1.0  # <1s total
```

**Acceptance**: Event loop responsiveness <100ms p99

---

#### SC2.2: Parallel Execution ✅

**Requirement**: Independent turns execute concurrently

**Measurable**:
- Sequential mode: turns run one-by-one (with dependencies)
- Parallel mode: independent turns run concurrently
- Mixed mode: some phases parallel, others sequential

**Test**:
```python
# 3 independent analysis tasks
config = ParallelMode(turns=[
    {"role": "technical", "participant": "grok"},
    {"role": "ethical", "participant": "claude"},
    {"role": "economic", "participant": "gpt4"}
])

# Should complete in ~10s (single call time), not ~30s (3x)
start = time.time()
await orchestrator.run(config)
duration = time.time() - start

assert duration < 15  # Much closer to 10s than 30s
```

**Acceptance**: 3 parallel turns complete in ≤1.5x single turn time

---

#### SC2.3: Dynamic Task Decomposition ✅

**Requirement**: System can spawn sub-dialogues dynamically

**Measurable**:
- Turn can trigger sub-dialogue based on response
- Sub-dialogues inherit context but run independently
- Results merge back into main dialogue

**Test**:
```python
# Turn identifies 3 subtopics requiring deeper exploration
dialogue = await orchestrator.run("Explain AGI risks")

# System automatically spawns 3 sub-dialogues
assert len(dialogue.subdialogues) == 3
assert all(sub.depth == dialogue.depth + 1 for sub in dialogue.subdialogues)

# Main dialogue waits for all subdialogues
assert dialogue.status == "completed"
assert all(sub.status == "completed" for sub in dialogue.subdialogues)
```

**Acceptance**: Can spawn and coordinate N sub-dialogues without manual orchestration

---

#### SC2.4: Context Management ✅

**Requirement**: Efficient context passing between turns

**Measurable**:
- Context includes: full history, relevant turns, metadata
- Context compressed for token efficiency
- Context caching for repeated patterns

**Test**:
```python
# Turn 5 references turns 1, 2, 4
turn_5_config = {
    "context_from": [1, 2, 4],
    "context_compression": "relevant_only"
}

context = orchestrator.build_context(conversation, turn_5_config)

# Should include only specified turns, compressed
assert len(context.turns) == 3
assert context.token_count < conversation.total_tokens * 0.3  # <30% of full
```

**Acceptance**: Context overhead <30% of full conversation tokens

---

## 🎯 Feature 3: Mixture of Experts Pattern

### User Scenario

> "As a researcher, I want Grok to handle hypothesis generation (reasoning) and Claude to handle validation (analysis), automatically routing each task to the optimal model."

### Success Criteria

#### SC3.1: Capability-Based Routing ✅

**Requirement**: System routes tasks based on model capabilities

**Measurable**:
- Models advertise capabilities: reasoning, analysis, coding, vision, etc.
- Modes specify required capabilities per turn
- Router selects optimal model automatically

**Test**:
```python
mode = LoopMode()
mode.turns = [
    {"role": "hypothesis", "requires": ["reasoning"], "prefer": "grok"},
    {"role": "validation", "requires": ["analysis"], "prefer": "claude"},
    {"role": "synthesis", "requires": ["reasoning", "analysis"]}
]

dialogue = await orchestrator.run(mode)

# Verify routing
assert dialogue.turns[0].model == "grok-4"  # Best at reasoning
assert dialogue.turns[1].model == "claude-sonnet"  # Best at analysis
assert dialogue.turns[2].model in ["grok-4", "claude-opus"]  # Either works
```

**Acceptance**: 90%+ tasks routed to declared optimal model

---

#### SC3.2: Performance-Based Learning ✅

**Requirement**: System learns which models perform best for which tasks

**Measurable**:
- Track quality metrics per (model, task_type) pair
- Update routing preferences based on performance
- Periodic A/B testing of routing decisions

**Test**:
```python
# Initially equal routing
stats = orchestrator.routing_stats()
assert stats["grok"]["synthesis"] == stats["claude"]["synthesis"]

# After 100 dialogues
await orchestrator.run_dialogues(count=100)

# System learned which model is better
updated_stats = orchestrator.routing_stats()
best = max(updated_stats, key=lambda m: updated_stats[m]["synthesis"]["quality"])

# Future dialogues prefer the best
config = {"role": "synthesis"}
model = orchestrator.select_model(config)
assert model == best
```

**Acceptance**: Routing quality improves >10% over first 100 dialogues

---

#### SC3.3: Cost-Aware Orchestration ✅

**Requirement**: Balance quality and cost based on user preferences

**Measurable**:
- Track token usage and cost per dialogue
- Support cost constraints: "max $1 per dialogue"
- Optimize model selection for cost/quality tradeoff

**Test**:
```python
# High quality, cost no object
dialogue_1 = await orchestrator.run(
    topic="quantum computing",
    mode="loop",
    constraints={"quality": "maximum"}
)

# Budget-constrained
dialogue_2 = await orchestrator.run(
    topic="quantum computing",
    mode="loop",
    constraints={"max_cost": 0.50}  # 50 cents
)

# Quality/cost tradeoff
assert dialogue_1.quality_score > dialogue_2.quality_score
assert dialogue_1.cost > 0.50
assert dialogue_2.cost <= 0.50
```

**Acceptance**: Can complete useful dialogue within any cost constraint >$0.10

---

## 🎯 Feature 4: Mode Configuration System

### User Scenario

> "As a non-developer researcher, I want to create a custom 'Detective Mode' by editing JSON, without touching Python code."

### Success Criteria

#### SC4.1: Declarative Mode Definition ✅

**Requirement**: Modes are JSON/YAML configs, not Python code

**Measurable**:
- Mode defines: turns, roles, participants, prompts, structure
- No custom code required for standard patterns
- Schema validation prevents invalid configurations

**Test**:
```json
{
  "name": "detective",
  "structure": "sequential",
  "turns": 5,
  "prompts": {
    "turn_1": {
      "role": "hypothesis",
      "participant": "grok",
      "requires": ["reasoning"],
      "template": "Generate 3 hypotheses for: {topic}"
    },
    "turn_2": {
      "role": "evidence",
      "participant": "claude",
      "requires": ["analysis"],
      "template": "For each hypothesis, what evidence would support or refute it?\n\n{turn_1}"
    }
  }
}
```

```python
# Load and run
mode = ModeLoader.from_file("detective.json")
dialogue = await orchestrator.run(mode, topic="Who wrote Shakespeare?")

assert len(dialogue.turns) == 5
assert dialogue.turns[0].role == "hypothesis"
```

**Acceptance**: Non-developer can create functional mode in <15 minutes

---

#### SC4.2: Mode Composition ✅

**Requirement**: Modes can inherit and extend other modes

**Measurable**:
- Base modes define reusable patterns
- Custom modes extend via inheritance
- Override specific turns without duplicating all config

**Test**:
```json
{
  "name": "detective-deep",
  "extends": "detective",
  "turns": 8,
  "overrides": {
    "turn_1": {
      "template": "Generate 5 hypotheses (not 3) for: {topic}"
    }
  },
  "additional_turns": {
    "turn_6": {"role": "refinement", ...},
    "turn_7": {"role": "meta-analysis", ...}
  }
}
```

**Acceptance**: Can create mode variants by changing <10% of config

---

#### SC4.3: Runtime Mode Modification ✅

**Requirement**: Modes can adapt based on intermediate results

**Measurable**:
- Turns can conditionally spawn additional turns
- Convergence detection can terminate early
- Quality assessment can trigger refinement loops

**Test**:
```python
mode = AdaptiveMode(base="loop")
mode.convergence_threshold = 0.85
mode.max_turns = 10

dialogue = await orchestrator.run(mode)

# If converged at turn 6, stopped early
if dialogue.convergence_detected_at == 6:
    assert len(dialogue.turns) == 6
    assert dialogue.status == "converged"
else:
    assert len(dialogue.turns) <= 10
```

**Acceptance**: Adaptive modes reduce unnecessary turns by >30%

---

## 🎯 Feature 5: Observability & Debugging

### User Scenario

> "As a developer debugging slow dialogues, I want detailed traces showing which model took how long and why, so I can optimize performance."

### Success Criteria

#### SC5.1: Structured Logging ✅

**Requirement**: All operations emit structured logs

**Measurable**:
- JSON-formatted logs with standard fields
- Correlation IDs trace requests across async operations
- Log levels: DEBUG, INFO, WARNING, ERROR

**Test**:
```python
with log_capture() as logs:
    await orchestrator.run(mode="loop", turns=3)

# Verify structured output
for log in logs:
    assert "timestamp" in log
    assert "correlation_id" in log
    assert "level" in log
    assert log["level"] in ["DEBUG", "INFO", "WARNING", "ERROR"]
```

**Acceptance**: Can trace any request through system using correlation ID

---

#### SC5.2: Performance Metrics ✅

**Requirement**: Track latency, token usage, costs per dialogue

**Measurable**:
- Per-turn: latency, tokens, cost, model used
- Per-dialogue: total time, total tokens, total cost
- Exportable to monitoring systems (Prometheus, etc.)

**Test**:
```python
dialogue = await orchestrator.run(mode="debate", turns=6)

metrics = dialogue.metrics
assert metrics.total_latency_seconds > 0
assert metrics.total_tokens > 0
assert metrics.total_cost_usd > 0

# Per-turn breakdown
for turn in dialogue.turns:
    assert turn.latency_seconds > 0
    assert turn.tokens.prompt + turn.tokens.completion == turn.tokens.total
```

**Acceptance**: Can identify performance bottlenecks within 5 minutes of investigation

---

#### SC5.3: State Persistence ✅

**Requirement**: Conversations survive crashes and can resume

**Measurable**:
- Auto-save after each turn completion
- Resume from last completed turn
- Export to multiple formats (JSON, Markdown, PDF)

**Test**:
```python
# Start dialogue
dialogue = orchestrator.start(mode="loop", turns=10)
await dialogue.execute_turns(5)

# Simulate crash
dialogue_id = dialogue.id
del dialogue

# Resume later
resumed = orchestrator.resume(dialogue_id)
assert resumed.turns_completed == 5
await resumed.execute_turns(5)
assert resumed.turns_completed == 10
```

**Acceptance**: 0 data loss on crash, resume time <5 seconds

---

## 📊 System-Wide Success Criteria

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Orchestration Overhead** | <500ms per dialogue | Time from CLI to first API call |
| **Parallel Efficiency** | ≥80% | 3 parallel turns in ≤1.5x serial time |
| **Memory Usage** | <100MB per conversation | Peak RSS during 10-turn dialogue |
| **Throughput** | ≥10 concurrent dialogues | Load test with 10 parallel sessions |

### Reliability

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Single Model Failure** | 0 dialogue failures | 100 dialogues with 10% random model failures |
| **Crash Recovery** | 100% state recovery | Kill process at random turn, resume successfully |
| **API Retry Success** | ≥95% | Transient failures recovered automatically |

### Maintainability

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Add New Model** | <1 hour | Time from "want GPT-5" to "GPT-5 working" |
| **Create New Mode** | <15 minutes | Non-developer creates JSON mode |
| **Test Coverage** | ≥80% | Core modules (orchestration, routing, execution) |

---

## 🧪 Validation Tests

### V1: End-to-End Integration Test

```python
async def test_e2e_multi_model_dialogue():
    """Verify complete dialogue orchestration with multiple models"""

    # Setup
    orchestrator = Orchestrator(
        models={
            "grok": GrokAdapter(model="grok-4"),
            "claude": ClaudeAdapter(model="claude-sonnet"),
        }
    )

    # Execute
    dialogue = await orchestrator.run(
        mode="loop",
        topic="quantum computing applications",
        turns=6
    )

    # Validate
    assert dialogue.status == "completed"
    assert len(dialogue.turns) == 6
    assert dialogue.turns[0].model == "grok"  # Reasoning task
    assert dialogue.turns[1].model == "claude"  # Analysis task
    assert dialogue.total_tokens > 1000
    assert dialogue.total_cost_usd > 0

    # Export works
    json_path = dialogue.export("json")
    md_path = dialogue.export("markdown")
    assert json_path.exists()
    assert md_path.exists()
```

### V2: Parallel Execution Test

```python
async def test_parallel_execution_performance():
    """Verify parallel turns execute concurrently, not serially"""

    mode = ParallelMode(turns=[
        {"role": "analysis_1", "participant": "grok"},
        {"role": "analysis_2", "participant": "claude"},
        {"role": "analysis_3", "participant": "gpt4"}
    ])

    start = time.time()
    dialogue = await orchestrator.run(mode)
    duration = time.time() - start

    # Should be ~10s (single call), not ~30s (3 serial calls)
    assert duration < 15
    assert len(dialogue.turns) == 3

    # All turns started within 1 second of each other
    start_times = [t.started_at for t in dialogue.turns]
    assert max(start_times) - min(start_times) < 1.0
```

### V3: Model Fallback Test

```python
async def test_model_fallback_on_failure():
    """Verify graceful fallback when primary model fails"""

    config = ModelConfig(
        primary="grok-4",
        fallbacks=["grok-3", "claude-sonnet"]
    )

    # Simulate grok-4 outage
    with mock_model_failure("grok-4"):
        dialogue = await orchestrator.run(
            mode="loop",
            turns=3,
            model_config=config
        )

        # Should succeed using fallback
        assert dialogue.status == "completed"
        assert all(t.model != "grok-4" for t in dialogue.turns)
        assert any(t.model == "grok-3" for t in dialogue.turns)
```

### V4: Cost Constraint Test

```python
async def test_cost_constrained_execution():
    """Verify system respects cost constraints"""

    dialogue = await orchestrator.run(
        mode="loop",
        topic="AI safety",
        turns=10,
        constraints={"max_cost": 0.50}
    )

    assert dialogue.total_cost_usd <= 0.50
    assert dialogue.status in ["completed", "cost_limited"]

    # Should have completed some turns
    assert len(dialogue.turns) >= 3
```

---

## 🔄 Migration Path

### Phase 1: LangChain Integration (Week 1)
- Replace direct API clients with LangChain adapters
- Implement model registry
- Add capability-based routing
- **Test**: Existing modes work unchanged

### Phase 2: Enhanced Orchestration (Week 2)
- Optimize async patterns for parallelism
- Implement dynamic task decomposition
- Add context compression
- **Test**: 3x speedup on parallel workloads

### Phase 3: Observability (Week 3)
- Structured logging with correlation IDs
- Metrics collection and export
- Performance dashboards
- **Test**: Can debug any issue in <5 minutes

### Phase 4: Production Hardening (Week 4)
- Graceful fallbacks
- Crash recovery
- Load testing
- **Test**: Passes all reliability targets

---

## 📚 References

- **CONSTITUTION.md** - Governing principles this architecture honors
- **ADVANCED-CAPABILITIES-SPEC.md** - Features built on this foundation
- **TECHNICAL-PLAN.md** - Detailed implementation approach
- LangChain Documentation: https://python.langchain.com/docs/

---

**Status**: Ready for Implementation
**Dependencies**: None (foundational)
**Estimated Effort**: 4 weeks (2 engineers)
**Risk**: Low (proven patterns, mature libraries)

---

*"Architecture is the art of making the complex simple, and the rigid flexible."*
