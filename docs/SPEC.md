# AI Dialogue Protocol - Specification

**Version**: 1.0
**Status**: Minimal Viable Product
**Philosophy**: Simple, pragmatic, no over-engineering

---

## Overview

Universal asynchronous AI orchestration protocol enabling multi-turn conversations between Claude (via CLI) and Grok (via API) in various interaction modes.

**Abstracted from**: grok-consult categorical AI research protocol
**Generalized to**: Any domain, any topic, configurable modes

---

## Core Principles

1. **Simplicity First**: ~500 lines of Python, no complex frameworks
2. **Async Where It Matters**: asyncio for non-blocking I/O, not message queues
3. **Config Over Code**: Modes defined in JSON, not hardcoded
4. **File-Based State**: JSON or SQLite, no databases
5. **Pragmatic Observability**: Logs + markdown output, no Prometheus

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              CLI Interface                      │
│         (python cli.py run --mode X)           │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         Protocol Engine (async)                 │
│  - Mode config loader                           │
│  - Turn orchestrator                            │
│  - State manager                                │
│  - Output formatter                             │
└─────┬───────────────────────────────────┬───────┘
      │                                   │
      ▼                                   ▼
┌─────────────────┐              ┌─────────────────┐
│  Claude Client  │              │  Grok Client    │
│  (CLI wrapper)  │              │  (API client)   │
└─────────────────┘              └─────────────────┘
```

---

## Components

### 1. Protocol Engine (`src/protocol.py`)

**Responsibility**: Orchestrate multi-turn conversations asynchronously

**Core Functions**:
```python
async def run_protocol(mode: str, topic: str, turns: int) -> Conversation:
    """Execute protocol with specified mode and parameters"""

async def execute_turn(turn: int, context: Context) -> Turn:
    """Execute single turn with appropriate participants"""

async def call_claude(prompt: str) -> Response:
    """Async Claude CLI invocation"""

async def call_grok(prompt: str, model: str) -> Response:
    """Async Grok API call"""
```

**Features**:
- Parallel execution when turns are independent
- Sequential when context required
- State persistence between turns
- Error handling with retries

---

### 2. Mode Configs (`src/modes/*.json`)

**Format**:
```json
{
  "name": "loop",
  "description": "Sequential knowledge building",
  "turns": 8,
  "structure": "sequential",
  "participants": ["claude", "grok"],
  "prompts": {
    "turn_1": {
      "role": "foundation",
      "template": "Establish foundational concepts for {topic}...",
      "participant": "grok",
      "context_from": []
    },
    "turn_2": {
      "role": "expansion",
      "template": "Build on previous foundation...",
      "participant": "claude",
      "context_from": ["turn_1"]
    }
  }
}
```

**Available Modes**:

#### Loop Mode
- Sequential knowledge building
- Each turn builds on previous
- Pattern: Foundation → Analysis → Synthesis → Integration
- Use case: Research, deep exploration

#### Debate Mode
- Adversarial positions
- Pattern: Proposition → Opposition → Defense → Rebuttal
- Use case: Exploring tradeoffs, evaluating options

#### Podcast Mode
- Conversational exploration
- Pattern: Introduce → Expand → Question → Clarify → Insight
- Use case: Accessible explanations, teaching

#### Dialogue Mode
- Free-form exchange
- Pattern: No predetermined structure
- Use case: Creative exploration, brainstorming

#### Synthesis Mode
- Multi-perspective integration
- Pattern: Expert 1 → Expert 2 → ... → Synthesis
- Use case: Complex decisions, comprehensive analysis

---

### 3. Claude Client (`src/clients/claude.py`)

**Thin wrapper around Claude CLI**:

```python
import asyncio
import subprocess

async def call_claude(prompt: str, context: dict = None) -> str:
    """
    Execute claude CLI command asynchronously
    """
    cmd = ["claude", "--prompt", prompt]
    if context:
        cmd.extend(["--context", json.dumps(context)])

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode()
```

**Features**:
- Async subprocess execution
- Error handling
- Token tracking
- Context passing

---

### 4. Grok Client (`src/clients/grok.py`)

**OpenAI-compatible async client**:

```python
import aiohttp
from openai import AsyncOpenAI

class GrokClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

    async def chat(self, prompt: str, model: str = "grok-4-fast") -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
```

**Features**:
- Async API calls
- Model selection (grok-4, grok-4-fast, grok-3)
- Streaming support (optional)
- Token usage tracking

---

### 5. State Management (`src/state.py`)

**Simple JSON-based state**:

```python
class ConversationState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turns = []
        self.metadata = {}

    def add_turn(self, turn: Turn):
        self.turns.append(turn)
        self.save()

    def save(self):
        with open(f"sessions/{self.session_id}.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, session_id: str):
        with open(f"sessions/{self.session_id}.json") as f:
            return cls.from_dict(json.load(f))
```

**Features**:
- Session persistence
- Resume capability
- Export to markdown
- Simple query interface

---

### 6. CLI Interface (`cli.py`)

```bash
# Run new protocol
ai-dialogue run --mode loop --topic "quantum computing" --turns 8

# Resume session
ai-dialogue resume <session-id>

# List sessions
ai-dialogue list

# Export to markdown
ai-dialogue export <session-id> --output report.md

# Custom mode
ai-dialogue run --mode custom --config my-mode.json --topic "topic"
```

---

## Async Patterns

### Pattern 1: Sequential Execution
```python
async def sequential_protocol(turns: int):
    context = {}
    for i in range(turns):
        # Turn depends on previous
        result = await execute_turn(i, context)
        context.update(result)
    return context
```

### Pattern 2: Parallel Execution
```python
async def parallel_protocol(prompts: list):
    # Independent turns, execute in parallel
    tasks = [execute_turn(i, prompt) for i, prompt in enumerate(prompts)]
    results = await asyncio.gather(*tasks)
    return results
```

### Pattern 3: Mixed Execution
```python
async def mixed_protocol():
    # Phase 1: Parallel exploration
    explorations = await asyncio.gather(
        explore_claude(topic),
        explore_grok(topic)
    )

    # Phase 2: Sequential synthesis (depends on Phase 1)
    synthesis = await synthesize(explorations)
    return synthesis
```

---

## Integration Points

### Claude Code Skills/Agents

Invoke via subprocess or programmatic API:

```python
# Via subprocess
result = await call_claude_skill("deep-researcher", topic="quantum")

# Skill mapping
SKILLS = {
    "research": "deep-researcher",
    "mcp": "mcp-integration-wizard",
    "observe": "cc-observe",
    "understand": "cc-understand",
    "learn": "cc-learn"
}
```

### Grok API

Direct async integration:

```python
grok = GrokClient(api_key=os.environ["XAI_API_KEY"])
response = await grok.chat(prompt, model="grok-4-fast")
```

---

## Observability

### Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/{session_id}.log'),
        logging.StreamHandler()
    ]
)
```

**Logged Events**:
- Turn start/end
- API calls (model, tokens, latency)
- Errors and retries
- State changes

### Output Format

**Markdown conversation**:
```markdown
# AI Dialogue: Quantum Computing (Loop Mode)

**Session**: 20250109-143052
**Mode**: loop
**Turns**: 8
**Participants**: Claude (Sonnet 4.5), Grok (grok-4-fast)

---

## Turn 1: Foundation (Grok)
**Timestamp**: 2025-01-09 14:30:52
**Tokens**: 156 prompt, 423 completion
**Latency**: 1.2s

[Grok's response...]

---

## Turn 2: Analysis (Claude)
**Timestamp**: 2025-01-09 14:31:15
**Tokens**: 245 prompt, 612 completion
**Context**: Turn 1

[Claude's response...]
```

---

## Success Criteria

### Functional
- ✅ All 5 modes execute successfully
- ✅ Async execution works (parallel when possible)
- ✅ State persists and resumes correctly
- ✅ Both Claude and Grok clients work reliably

### Non-Functional
- ✅ <500 lines of core code
- ✅ <5 dependencies (asyncio, openai, aiohttp, click)
- ✅ Logs are readable and useful
- ✅ Output markdown is well-formatted
- ✅ Tests cover core functionality

### Performance
- ✅ Parallel turns execute concurrently
- ✅ No blocking operations in async code
- ✅ Minimal memory footprint (<100MB)

---

## Testing Strategy

### Unit Tests
```python
def test_mode_config_loading():
    """Test mode configs parse correctly"""

async def test_async_execution():
    """Test async patterns work correctly"""

def test_state_persistence():
    """Test state saves and loads correctly"""
```

### Integration Tests
```python
async def test_claude_client_mock():
    """Test Claude client with mocked subprocess"""

async def test_grok_client_mock():
    """Test Grok client with mocked API"""
```

### E2E Tests
```python
@pytest.mark.skipif(not os.getenv("XAI_API_KEY"), reason="No API key")
async def test_full_loop_protocol():
    """Test complete loop mode execution"""
```

---

## Non-Goals (Avoiding Over-Engineering)

❌ **Message Queues**: Kafka, RabbitMQ, Redis - asyncio is enough
❌ **Microservices**: Single Python process is sufficient
❌ **Complex Orchestration**: No Airflow, Prefect, Temporal
❌ **Heavy Observability**: No Prometheus, Grafana, ELK stack
❌ **Custom DSLs**: JSON configs are enough
❌ **Database**: File-based state is fine for now

---

## Future Enhancements (If Needed)

### Phase 2 (Only if validated in Phase 1)
- Web UI for session management
- SQLite for better querying
- Streaming output to terminal
- Cost tracking dashboard

### Phase 3 (Only if widely adopted)
- Plugin system for custom modes
- Multi-language support (TypeScript client)
- Cloud deployment templates
- API server mode

---

## File Structure

```
ai-dialogue/
├── src/
│   ├── __init__.py
│   ├── protocol.py           # Core engine (~150 lines)
│   ├── state.py              # State management (~80 lines)
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── claude.py         # Claude wrapper (~60 lines)
│   │   └── grok.py           # Grok client (~60 lines)
│   └── modes/
│       ├── loop.json         # Loop mode config
│       ├── debate.json       # Debate mode config
│       ├── podcast.json      # Podcast mode config
│       ├── dialogue.json     # Dialogue mode config
│       └── synthesis.json    # Synthesis mode config
├── cli.py                    # CLI interface (~100 lines)
├── tests/
│   ├── test_protocol.py
│   ├── test_clients.py
│   └── test_state.py
├── examples/
│   ├── quantum_computing_loop.md
│   └── agi_safety_debate.md
├── sessions/                 # Runtime session data
├── logs/                     # Runtime logs
├── pyproject.toml
├── README.md
└── SPEC.md                   # This file
```

**Total Lines**: ~500 core code
**Dependencies**: 5 (asyncio, openai, aiohttp, click, pytest)
**Complexity**: Low

---

## Implementation Roadmap

### Day 1: Core
- [x] Create project structure
- [ ] Implement protocol.py
- [ ] Create mode configs
- [ ] Build clients

### Day 2: Integration
- [ ] Build CLI interface
- [ ] Add state management
- [ ] Write tests
- [ ] Documentation

### Day 3: Validation
- [ ] E2E testing with real APIs
- [ ] Example sessions
- [ ] Git repo + README
- [ ] First release

---

## Common Use Cases

### Research Deep Dive
```bash
ai-dialogue run \
  --mode loop \
  --topic "Category theory applications in ML" \
  --turns 8 \
  --output research.md
```

### Technical Decision
```bash
ai-dialogue run \
  --mode debate \
  --topic "Microservices vs Monolith for our scale" \
  --turns 6
```

### Educational Content
```bash
ai-dialogue run \
  --mode podcast \
  --topic "Quantum computing for beginners" \
  --turns 10
```

### Multi-Expert Synthesis
```bash
ai-dialogue run \
  --mode synthesis \
  --topic "AI safety approaches" \
  --turns 5
```

---

**Philosophy**: Build the simplest thing that works. Add complexity only when validated by real usage.

**Status**: Ready for implementation
**Next**: Build protocol.py
