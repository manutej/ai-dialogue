# AI Dialogue Protocol

**Universal Asynchronous AI Orchestration**

Enable multi-turn conversations between Claude (via CLI) and Grok (via API) with configurable interaction modes, dynamic workflows, and intelligent task decomposition.

---

## Features

✨ **Multiple Interaction Modes**
- **Loop**: Sequential knowledge building (8 turns)
- **Debate**: Adversarial exploration (6 turns)
- **Podcast**: Conversational dialogue (10 turns)
- **Pipeline**: Static process workflow (7 stages)
- **Dynamic**: Adaptive task decomposition (variable turns)

🔄 **Async Execution**
- Non-blocking I/O with Python asyncio
- Parallel execution where possible
- No heavy infrastructure (no Kafka, no Redis)

🧠 **Intelligent Orchestration**
- Claude-side intelligence for workflow management
- Dynamic task decomposition
- Adaptive loop generation
- Self-modifying prompts based on results

🔁 **Cycle Support**
- Repeat loops to create cycles
- Convergence detection
- Iterative refinement

📊 **Observable**
- Session persistence (JSON)
- Markdown export
- Token tracking
- Execution logs

---

## Quick Start

### Installation

```bash
cd ai-dialogue
pip install -e .
```

### Set API Keys

```bash
export XAI_API_KEY="your-grok-api-key"
# Claude CLI should already be configured
```

### Run Your First Dialogue

```bash
# Loop mode: Deep exploration
ai-dialogue run --mode loop --topic "quantum computing applications" --turns 8

# Debate mode: Explore tradeoffs
ai-dialogue run --mode debate --topic "Microservices vs Monolith"

# Podcast mode: Accessible explanation
ai-dialogue run --mode podcast --topic "AI safety for beginners"

# Pipeline mode: Systematic task completion
ai-dialogue run --mode pipeline --topic "Build a CLI tool for data analysis"

# Dynamic mode: Intelligent decomposition
ai-dialogue run --mode dynamic --topic "Design a distributed caching system"
```

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│              CLI Interface (click)                  │
│         ai-dialogue run --mode X --topic Y         │
└───────────────────┬────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────┐
│         Protocol Engine (async orchestration)      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Modes: loop, debate, podcast, pipeline,    │  │
│  │         dynamic                               │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Dynamic Protocol Engine                     │  │
│  │  - Template substitution (<TASK>, <RESULT>)  │  │
│  │  - Cycle support                             │  │
│  │  - Adaptive workflows                        │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Intelligent Orchestrator (Claude-side)      │  │
│  │  - Task decomposition                        │  │
│  │  - Dynamic loop generation                   │  │
│  │  - Adaptive decision making                  │  │
│  └──────────────────────────────────────────────┘  │
└─────┬──────────────────────────────────┬───────────┘
      │                                   │
      ▼                                   ▼
┌─────────────────┐              ┌─────────────────┐
│  Claude Client  │              │  Grok Client    │
│  (CLI wrapper)  │              │  (OpenAI SDK)   │
└─────────────────┘              └─────────────────┘
```

---

## Modes Explained

### 1. Loop Mode
**Pattern**: Foundation → Analysis → Evidence → Synthesis → Applications → Future → Reflection → Integration

**Use Case**: Deep research, systematic knowledge building

**Example**:
```bash
ai-dialogue run --mode loop --topic "Category theory for AI" --turns 8
```

Produces structured exploration with each turn building on previous insights.

---

### 2. Debate Mode
**Pattern**: Proposition → Opposition → Defense → Rebuttal → Synthesis → Verdict

**Use Case**: Exploring tradeoffs, evaluating competing approaches

**Example**:
```bash
ai-dialogue run --mode debate --topic "Serverless vs Traditional Infrastructure"
```

Claude and Grok take opposing positions, then synthesize findings.

---

### 3. Podcast Mode
**Pattern**: Introduction → Overview → Questions → Deep Dive → Insight → Implications → Challenge → Response → Takeaways → Closing

**Use Case**: Accessible explanations, teaching, conversational exploration

**Example**:
```bash
ai-dialogue run --mode podcast --topic "Machine learning for beginners" --turns 10
```

Natural dialogue format, like a real podcast conversation.

---

### 4. Pipeline Mode (NEW!)
**Pattern**: Research → Synthesize → Extract → Distill → Explore → Spec → Plan

**Use Case**: Systematic task completion through defined stages

**Example**:
```bash
ai-dialogue run --mode pipeline --topic "Build authentication microservice"
```

**Supports cycles**:
```bash
# Run 3 cycles for iterative refinement
ai-dialogue run --mode pipeline --topic "Design API architecture" --cycles 3
```

**Dynamic template variables**:
- `<TASK>`: Primary task description
- `<CYCLE>`: Current cycle number
- `<PREVIOUS_CYCLE_SUMMARY>`: Summary of previous cycle
- `<TURN_N_RESULT>`: Result from turn N

---

### 5. Dynamic Mode (NEW!) 🧠
**Pattern**: Decompose → Assess → Generate Loops → Execute → Synthesize

**Use Case**: Complex tasks requiring intelligent decomposition

**How it works**:
1. **Claude decomposes** the task into subtasks
2. **Grok assesses** complexity and validates approach
3. **System generates** appropriate loops:
   - Simple tasks → Single loop
   - Complex tasks → One loop per task
   - Mixed complexity → Hybrid approach
4. **Execute** dynamically generated workflow
5. **Synthesize** results

**Example**:
```bash
ai-dialogue run --mode dynamic --topic "Design and implement rate limiting system"
```

**What happens**:
```
Turn 1 (Claude): Decompose task
  → Subtasks: API design (complex), Algorithm implementation (complex),
              Testing (moderate), Documentation (simple)

Turn 2 (Grok): Validate decomposition
  → Strategy: one_loop_per_task (complex tasks need loops)
  → Estimated: ~15 turns

Turns 3-5: API design loop (Research → Execute → Validate)
Turns 6-8: Algorithm loop (Research → Execute → Validate)
Turns 9-10: Testing execution + validation
Turn 11: Documentation (simple, one turn)
Turn 12: Final synthesis
```

**Adaptive features**:
- Agents can modify workflow based on results
- Failed subtasks trigger refinement loops
- Complexity reassessment mid-execution
- Dynamic context passing between subtasks

---

## Dynamic Workflow Examples

### Simple Task (Single Loop)
```bash
ai-dialogue run --mode dynamic --topic "Write a Python CLI tool for JSON formatting"
```

Claude decomposes → All simple subtasks → Single loop execution → Done in ~5 turns

### Complex Task (Multiple Loops)
```bash
ai-dialogue run --mode dynamic --topic "Design distributed consensus algorithm"
```

Claude decomposes → Multiple complex subtasks → Each gets dedicated loop → ~20-30 turns

### Mixed Complexity
```bash
ai-dialogue run --mode dynamic --topic "Optimize database query performance"
```

- Profile bottlenecks (moderate) → 2-3 turns
- Implement optimizations (complex) → Dedicated loop
- Add caching (simple) → 1 turn
- Benchmark (simple) → 1 turn

---

## Template Variables

All modes support dynamic template substitution:

```
<TASK>              → Primary task description
<CYCLE>             → Current cycle number (if using cycles)
<PREVIOUS_CYCLE_SUMMARY> → Summary of previous cycle
<TURN_N_RESULT>     → Result from specific turn N
<LAST_RESEARCH>     → Last research phase result
<LAST_SYNTHESIS>    → Last synthesis phase result
```

**Example prompt template**:
```
Analyze <TASK> based on previous research:

<LAST_RESEARCH>

Now synthesize findings considering cycle <CYCLE> insights.
```

---

## Cycles

Run multiple loops for iterative refinement:

```bash
# Run pipeline 3 times, refining each cycle
ai-dialogue run --mode pipeline --topic "API design" --cycles 3 --convergence 0.8
```

**Cycle behavior**:
- Each cycle runs complete mode workflow
- Context from previous cycles passed forward
- Convergence detection stops early if threshold met
- Useful for iterative design, research, refinement

---

## CLI Reference

### Run Protocol
```bash
ai-dialogue run [OPTIONS]

Options:
  --mode, -m          Mode (loop|debate|podcast|pipeline|dynamic)
  --topic, -t         Topic to discuss
  --turns, -n         Override default turn count
  --cycles            Number of cycles (for cyclic modes)
  --convergence       Convergence threshold (0.0-1.0)
  --output, -o        Output markdown path
  --claude-model      Claude model (sonnet|opus|haiku)
  --grok-model        Grok model (grok-4|grok-4-fast|grok-3)
  --debug             Enable debug logging
```

### List Sessions
```bash
ai-dialogue list [--limit N]
```

### Export to Markdown
```bash
ai-dialogue export SESSION_ID [--output path.md]
```

### Delete Session
```bash
ai-dialogue delete SESSION_ID
```

### List Available Modes
```bash
ai-dialogue modes
```

---

## Output

### Session Files
```
sessions/
├── 20250109-143052.json    # Session data
└── 20250109-143052.md      # Markdown export
```

### Markdown Format
```markdown
# AI Dialogue: Quantum Computing (Loop Mode)

**Session**: 20250109-143052
**Turns**: 8
**Participants**: Claude (Sonnet 4.5), Grok (grok-4-fast)

---

## Turn 1: Foundation (Grok)
**Tokens**: 156 prompt, 423 completion
**Latency**: 1.2s

[Response...]

---

## Turn 2: Critical Analysis (Claude)
**Context**: Turn 1

[Response...]
```

---

## Integration with Claude Code

The protocol integrates seamlessly with Claude Code skills and agents:

```python
# In your code or via CLI
from src import ProtocolEngine, ClaudeClient, GrokClient, StateManager

# Use with Claude Code skills
claude = ClaudeClient()
# Claude can invoke skills: deep-researcher, mcp-integration-wizard, etc.

# Run protocol
engine = ProtocolEngine(claude, grok, state)
conversation = await engine.run_protocol(
    mode="loop",
    topic="Your research topic"
)
```

**Commonly used skills in protocols**:
- `deep-researcher`: For research-heavy turns
- `mcp-integration-wizard`: For MCP-related topics
- `spec-driven-development-expert`: For specification phases
- `test-engineer`: For testing and validation phases
- `cc-observe`: For observability and monitoring
- `cc-understand`: For comprehension and analysis
- `cc-learn`: For knowledge acquisition

---

## Advanced Usage

### Custom Mode
```bash
# Create custom mode config
cat > my-mode.json <<EOF
{
  "name": "custom",
  "structure": "sequential",
  "turns": 5,
  "prompts": {
    "turn_1": {
      "role": "custom_step",
      "participant": "grok",
      "template": "Your custom prompt with <TASK>..."
    }
  }
}
EOF

# Use custom mode
ai-dialogue run --mode custom --config my-mode.json --topic "My task"
```

### Programmatic Usage
```python
import asyncio
from src import DynamicProtocolEngine, ClaudeClient, GrokClient, StateManager, CycleConfig

async def main():
    claude = ClaudeClient()
    grok = GrokClient()
    state = StateManager()

    engine = DynamicProtocolEngine(claude, grok, state)

    # Run with cycles
    conversation = await engine.run_dynamic_protocol(
        mode="pipeline",
        task="Design authentication system",
        cycle_config=CycleConfig(
            max_cycles=3,
            convergence_threshold=0.85
        )
    )

    # Export
    state.save_conversation(conversation)
    state.export_markdown(conversation)

asyncio.run(main())
```

---

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Format Code
```bash
black src/ cli.py tests/
ruff check src/ cli.py tests/
```

### Install Dev Dependencies
```bash
pip install -e ".[dev]"
```

---

## Philosophy

**Simple > Complex**
- ~500 lines of core code
- 5 dependencies (asyncio, openai, click, aiohttp)
- No message queues, no microservices, no databases

**Async Where It Matters**
- Python asyncio for non-blocking I/O
- Parallel execution when independent
- Sequential when context required

**Config Over Code**
- Modes defined in JSON
- Easy to add new modes
- No code changes for customization

**Observable**
- Every turn logged
- Token usage tracked
- Markdown export built-in

---

## Use Cases

### Research
```bash
ai-dialogue run --mode loop --topic "Quantum error correction" --turns 8
```

### Decision Making
```bash
ai-dialogue run --mode debate --topic "Build vs Buy for ML infrastructure"
```

### Learning
```bash
ai-dialogue run --mode podcast --topic "Distributed systems explained"
```

### Task Execution
```bash
ai-dialogue run --mode pipeline --topic "Implement OAuth2 flow"
```

### Complex Projects
```bash
ai-dialogue run --mode dynamic --topic "Design microservices architecture for e-commerce platform"
```

---

## Roadmap

### Phase 1 (Current)
- ✅ Core protocol engine
- ✅ 5 interaction modes
- ✅ Dynamic workflows
- ✅ Intelligent orchestration
- ✅ Cycle support
- ✅ CLI interface

### Phase 2 (Next)
- [ ] Web UI for session management
- [ ] Streaming output to terminal
- [ ] Resume incomplete sessions
- [ ] Cost tracking dashboard
- [ ] Export to more formats (PDF, HTML)

### Phase 3 (Future)
- [ ] Plugin system for custom modes
- [ ] Multi-language support (TypeScript client)
- [ ] Cloud deployment templates
- [ ] API server mode

---

## Contributing

This is a pragmatic, minimal implementation. Contributions welcome, but keep it simple:

1. No complex frameworks
2. Keep dependencies minimal
3. Maintain async-first approach
4. Document everything
5. Test thoroughly

---

## License

MIT

---

## Acknowledgments

**Abstracted from**: grok-consult categorical AI research protocol
**Philosophy**: Pragmatic, minimal, functional
**Approach**: Build the simplest thing that works

---

**Status**: Production Ready
**Version**: 1.0.0
**Lines of Code**: ~500 core + ~800 extensions

---

For questions, issues, or contributions, see SPEC.md for detailed architecture and design decisions.
