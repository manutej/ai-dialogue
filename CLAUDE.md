# CLAUDE.md - AI Assistant Guide

**Last Updated:** 2025-11-14
**Project:** AI Dialogue Protocol v1.0.0
**Purpose:** Guide for AI assistants working on this codebase

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Development Workflows](#development-workflows)
4. [Key Conventions](#key-conventions)
5. [Common Tasks](#common-tasks)
6. [Testing Guidelines](#testing-guidelines)
7. [Important Files Reference](#important-files-reference)
8. [Pitfalls to Avoid](#pitfalls-to-avoid)
9. [Git Workflow](#git-workflow)

---

## Project Overview

### What This Project Does

**AI Dialogue Protocol** is a universal asynchronous AI orchestration system that enables sophisticated multi-turn conversations between Claude (via CLI) and Grok (via xAI API).

**Core Capabilities:**
- 5 built-in interaction modes (loop, debate, podcast, pipeline, dynamic)
- Async Python implementation with proper context management
- Dynamic task decomposition and adaptive loop generation
- Session persistence (JSON) and markdown export
- Token tracking and latency measurement

**Technology Stack:**
- Python 3.10+ with asyncio
- xAI Grok API (via OpenAI SDK)
- Claude CLI wrapper
- Click for CLI
- LangChain for model abstraction (planned)

**Current Status:**
- Core implementation: 100% complete ✓
- Testing: Basic tests only (~10% coverage)
- Documentation: Excellent (90% accurate)
- Ready for internal testing

### Key Design Principles

1. **Async-First:** All I/O operations are async, no blocking calls
2. **Separation of Concerns:** Clients, protocols, state, and CLI are decoupled
3. **Extensibility:** JSON-based mode configurations for easy customization
4. **Persistence:** Sessions are saved incrementally for resumability
5. **Model Agnostic:** Designed to support multiple AI providers (future)

---

## Codebase Architecture

### Directory Structure

```
/home/user/ai-dialogue/
├── src/                          # Core source code (~1,465 lines)
│   ├── protocol.py              # Core orchestration engine (339 lines)
│   ├── dynamic_protocol.py      # Dynamic workflows with cycles (281 lines)
│   ├── intelligent_orchestrator.py # Claude-side intelligence (445 lines)
│   ├── state.py                 # Session persistence (208 lines)
│   ├── clients/                 # AI client implementations
│   │   ├── grok.py             # Grok API client (201 lines)
│   │   ├── claude.py           # Claude CLI wrapper (122 lines)
│   │   └── grok_enhanced.py    # Enhanced features (aspirational)
│   ├── adapters/               # LangChain model adapters
│   │   ├── base.py            # Base adapter interface
│   │   └── grok_adapter.py    # Grok LangChain adapter
│   └── modes/                  # Mode configurations (JSON)
│       ├── loop.json          # Sequential knowledge building
│       ├── debate.json        # Adversarial exploration
│       ├── podcast.json       # Conversational dialogue
│       ├── pipeline.json      # Static workflow
│       └── dynamic.json       # Adaptive decomposition
├── cli.py                      # CLI interface (246 lines)
├── tests/                      # Test suite
├── docs/                       # Documentation
├── specs/                      # Specifications (GitHub Spec-Kit)
└── examples/                   # Usage examples
```

### Core Modules

#### 1. `src/protocol.py` - Core Orchestration Engine

**Purpose:** Main protocol engine that orchestrates multi-turn conversations

**Key Classes:**
- `ProtocolEngine` - Main orchestration class
- `Conversation` - Dataclass for complete conversation sessions
- `Turn` - Dataclass for individual turns

**Key Methods:**
```python
async def run_protocol(mode, topic, turns, custom_config) -> Conversation
async def _execute_sequential(conversation, config, topic)
async def _execute_parallel(conversation, config, topic)
async def _execute_mixed(conversation, config, topic)
async def _execute_turn(turn_num, turn_config, topic, context) -> Turn
def export_to_markdown(conversation) -> str
```

**When to modify:**
- Adding new execution strategies
- Changing context building logic
- Modifying markdown export format
- Adding new metadata tracking

---

#### 2. `src/dynamic_protocol.py` - Dynamic Workflows

**Purpose:** Enhanced protocol with template substitution and cycle support

**Key Features:**
- Template variable substitution (`<TASK>`, `<RESULT>`, etc.)
- Cycle execution (loops of loops)
- Conditional step execution
- Adaptive workflows

**Template Variables:**
- `<TASK>` - Primary task description
- `<CYCLE>` - Current cycle number
- `<PREVIOUS_CYCLE_SUMMARY>` - Summary of previous cycle
- `<TURN_N_RESULT>` - Result from turn N
- `<LAST_{ROLE}>` - Last response from specific role

**When to modify:**
- Adding new template variables
- Implementing convergence detection
- Adding conditional execution logic
- Modifying cycle behavior

---

#### 3. `src/intelligent_orchestrator.py` - Claude-Side Intelligence

**Purpose:** Dynamic task decomposition and intelligent workflow generation

**Key Classes:**
- `IntelligentOrchestrator` - Orchestration intelligence
- `Subtask` - Decomposed subtask representation
- `ExecutionStrategy` - Strategy enum (single_loop, one_loop_per_task, mixed)

**Execution Strategies:**
- **single_loop:** All tasks in one loop (for simple tasks)
- **one_loop_per_task:** Dedicated loop per complex task
- **mixed:** Batch simple tasks, loop complex ones

**When to modify:**
- Changing decomposition prompts
- Adding new execution strategies
- Modifying subtask parsing logic
- Implementing adaptive refinement

---

#### 4. `src/state.py` - Session Persistence

**Purpose:** Save/load conversations and manage session state

**Key Features:**
- JSON-based session storage in `sessions/` directory
- Incremental turn saving (for resumability)
- Markdown export
- Session listing and deletion

**File Naming:**
- Sessions: `sessions/{session_id}.json`
- Exports: `sessions/{session_id}.md`

**When to modify:**
- Adding new export formats
- Implementing session resume logic
- Adding session search/filtering
- Modifying storage location

---

#### 5. `src/clients/grok.py` - Grok API Client

**Purpose:** Async wrapper for xAI Grok API

**Key Features:**
- Chat completions via OpenAI-compatible API
- Streaming responses (planned)
- Model ID resolution (friendly names → API IDs)
- Token usage tracking

**Supported Models:**
```python
# Text Generation (Grok 4)
"grok-4-fast-reasoning"
"grok-4-fast-non-reasoning"
"grok-code-fast-1"

# Multimodal (Grok 2)
"grok-2-vision-latest"
"grok-2-image-latest"

# Aliases
"grok-4", "grok-fast", "grok-code"
```

**API Details:**
- Base URL: `https://api.x.ai/v1`
- Auth: `XAI_API_KEY` environment variable
- SDK: AsyncOpenAI from openai package

**When to modify:**
- Adding new Grok models
- Implementing streaming
- Adding error retry logic
- Modifying token counting

---

#### 6. `src/clients/claude.py` - Claude CLI Wrapper

**Purpose:** Async wrapper for Claude CLI

**Key Features:**
- Executes Claude CLI commands via subprocess
- Token estimation (~4 chars per token)
- 5-minute timeout per request

**Implementation Details:**
- Uses `asyncio.create_subprocess_exec()`
- Invokes `claude` command with `--no-browser` flag
- Streams output and captures responses

**When to modify:**
- Switching to direct API instead of CLI
- Changing timeout values
- Improving token estimation
- Adding streaming support

---

#### 7. `cli.py` - Command-Line Interface

**Purpose:** User-facing CLI built with Click

**Available Commands:**
```bash
ai-dialogue run --mode <mode> --topic <topic> [--turns N]
ai-dialogue list [--limit N]
ai-dialogue export <session_id> [--output path]
ai-dialogue delete <session_id>
ai-dialogue modes
```

**When to modify:**
- Adding new CLI commands
- Changing command arguments
- Adding interactive prompts
- Implementing session resume command

---

### Mode Configuration System

**Location:** `src/modes/*.json`

**JSON Structure:**
```json
{
  "name": "mode_name",
  "description": "Brief description",
  "structure": "sequential|parallel|mixed",
  "turns": 8,
  "participants": ["claude", "grok"],
  "metadata": {
    "use_case": "Description",
    "pattern": "Pattern description"
  },
  "prompts": {
    "turn_1": {
      "role": "role_name",
      "participant": "grok|claude",
      "template": "Prompt template with {topic} and {context}",
      "context_from": [1, 2],  // Previous turn numbers to include
      "grok_model": "grok-4-fast"  // Optional model override
    }
  }
}
```

**Available Template Variables:**
- `{topic}` - Main discussion topic
- `{turn_N}` - Content from turn N
- `{turn_N_participant}` - Participant of turn N
- Dynamic variables in templates: `<TASK>`, `<RESULT>`, etc.

**When to create new modes:**
- New conversation patterns emerge
- Specific use cases require specialized flows
- Experimenting with different turn structures

**Best Practices:**
- Keep modes focused on single use case
- Provide clear role descriptions
- Use context_from to build on previous turns
- Test with multiple topics to ensure generality

---

## Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo-url>
cd ai-dialogue

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .           # Production dependencies
pip install -e ".[dev]"   # Development dependencies

# Or use requirements files
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Verify setup
python3 test_live_api.py  # If you have API key
pytest tests/simple_test.py -v
```

### Code Quality Workflow

```bash
# Format code (always run before committing)
black src/ cli.py tests/

# Lint code
ruff check src/ cli.py tests/

# Fix auto-fixable linting issues
ruff check --fix src/ cli.py tests/

# Type checking (optional)
mypy src/ cli.py

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Testing Workflow

**Test Hierarchy:**

1. **Unit Tests** (no external dependencies)
   - Test individual functions and classes
   - Mock external API calls
   - Fast and reliable

2. **Integration Tests** (requires API keys)
   - Test client integrations
   - Test protocol engine with real clients
   - Mark with `@pytest.mark.integration`

3. **E2E Tests** (full system)
   - Test complete workflows
   - Test CLI commands
   - Mark with `@pytest.mark.e2e`

**Running Tests:**

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests (skip integration)
pytest -m "not integration" -v

# Run specific test file
pytest tests/test_protocol.py -v

# Run specific test function
pytest tests/test_protocol.py::test_sequential_execution -v

# Run with verbose output
pytest tests/ -vv

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Writing Tests:**

```python
import pytest
import asyncio
from src.protocol import ProtocolEngine
from src.clients.grok import GrokClient
from src.clients.claude import ClaudeClient

class TestProtocolEngine:
    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test sequential turn execution"""
        # Arrange
        claude = ClaudeClient()
        grok = GrokClient()
        engine = ProtocolEngine(claude, grok)

        # Act
        conversation = await engine.run_protocol(
            mode="loop",
            topic="test topic",
            turns=2
        )

        # Assert
        assert conversation.total_turns == 2
        assert conversation.topic == "test topic"
```

---

## Key Conventions

### Code Style

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `ProtocolEngine`)
- Functions/methods: `snake_case` (e.g., `run_protocol`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MODEL_IDS`)
- Private methods: `_leading_underscore` (e.g., `_execute_turn`)
- Async functions: Always prefix with `async def`

**Type Hints:**
- Use type hints for all function parameters and return values
- Import from `typing` module
- Use dataclasses for structured data

```python
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Turn:
    number: int
    role: str
    participant: str
    content: str
    metadata: Dict[str, Any]

async def execute_turn(
    turn_num: int,
    config: Dict[str, Any],
    topic: str
) -> Tuple[Turn, Dict[str, int]]:
    """Execute a single turn in the conversation."""
    # Implementation
    pass
```

**Docstrings:**

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed, explaining what the function does,
    any important details, and edge cases.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
        APIError: When API call fails

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
    pass
```

### Async Conventions

**Always use async/await:**

```python
# Good - async/await
async def fetch_data():
    response = await client.chat("prompt")
    return response

# Bad - blocking call in async function
async def fetch_data():
    response = requests.get(url)  # Don't do this!
    return response
```

**Parallel execution with gather:**

```python
# Execute multiple tasks in parallel
results = await asyncio.gather(
    client1.chat("prompt1"),
    client2.chat("prompt2"),
    client3.chat("prompt3")
)

# With error handling
results = await asyncio.gather(
    client1.chat("prompt1"),
    client2.chat("prompt2"),
    return_exceptions=True  # Don't fail entire batch on one error
)
```

**Sequential execution:**

```python
# Execute tasks sequentially when order matters
result1 = await client.chat("prompt1")
result2 = await client.chat(f"prompt2 based on {result1}")
result3 = await client.chat(f"prompt3 based on {result2}")
```

### Error Handling

**Use specific exceptions:**

```python
# Good
try:
    result = await client.chat(prompt)
except APIError as e:
    logger.error(f"API call failed: {e}")
    raise
except TimeoutError as e:
    logger.warning(f"Request timed out: {e}")
    # Implement retry logic
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# Bad
try:
    result = await client.chat(prompt)
except Exception as e:  # Too broad!
    pass  # Silent failure is worse!
```

**Provide helpful error messages:**

```python
# Good
if not api_key:
    raise ValueError(
        "XAI_API_KEY environment variable is required. "
        "Please set it in your .env file. "
        "See .env.example for reference."
    )

# Bad
if not api_key:
    raise ValueError("Missing API key")
```

### Logging Conventions

**Use appropriate log levels:**

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG - Detailed debugging information
logger.debug(f"Executing turn {turn_num} with config: {config}")

# INFO - General information about program execution
logger.info(f"Starting {mode} mode conversation: {topic}")

# WARNING - Warning messages (recoverable issues)
logger.warning(f"API rate limit approaching: {remaining} requests left")

# ERROR - Error messages (serious issues)
logger.error(f"Failed to execute turn {turn_num}: {error}")

# CRITICAL - Critical errors (program cannot continue)
logger.critical(f"Database connection lost, shutting down")
```

**Include context in log messages:**

```python
# Good - includes context
logger.info(f"Turn {turn_num} completed in {duration:.2f}s with {tokens} tokens")

# Bad - lacks context
logger.info("Turn completed")
```

---

## Common Tasks

### Task 1: Adding a New Conversation Mode

**Steps:**

1. Create new JSON file in `src/modes/`:

```json
{
  "name": "brainstorm",
  "description": "Rapid idea generation and evaluation",
  "structure": "mixed",
  "turns": 6,
  "participants": ["claude", "grok"],
  "metadata": {
    "use_case": "Creative brainstorming sessions",
    "pattern": "Diverge → Converge → Refine"
  },
  "prompts": {
    "turn_1": {
      "role": "idea_generator",
      "participant": "grok",
      "template": "Generate 10 creative ideas for: {topic}. Be bold and unconventional.",
      "context_from": []
    },
    "turn_2": {
      "role": "idea_evaluator",
      "participant": "claude",
      "template": "Evaluate these ideas: {turn_1}\n\nSelect the top 3 most promising ideas and explain why.",
      "context_from": [1]
    }
  }
}
```

2. Test the new mode:

```bash
ai-dialogue run --mode brainstorm --topic "sustainable energy"
```

3. Add tests in `tests/test_modes.py`:

```python
@pytest.mark.asyncio
async def test_brainstorm_mode():
    """Test brainstorm mode execution"""
    engine = ProtocolEngine(claude_client, grok_client, state_manager)
    conversation = await engine.run_protocol(
        mode="brainstorm",
        topic="AI safety"
    )
    assert conversation.mode == "brainstorm"
    assert conversation.total_turns == 6
```

4. Document in README.md and update mode list

---

### Task 2: Adding a New Grok Model

**Steps:**

1. Update `src/clients/grok.py`:

```python
MODEL_IDS = {
    # Existing models...

    # New model
    "grok-5-ultra": "grok-5-ultra-latest",
    "grok-5": "grok-5-ultra-latest",  # Alias
}
```

2. Add tests in `tests/test_grok_client.py`:

```python
@pytest.mark.asyncio
async def test_new_model_resolution():
    """Test new model ID resolution"""
    client = GrokClient(api_key="test")
    assert client._resolve_model("grok-5") == "grok-5-ultra-latest"
```

3. Update documentation in docs/ if needed

---

### Task 3: Implementing Session Resume

**Steps:**

1. Add resume method to `src/state.py`:

```python
def get_incomplete_turns(self, session_id: str) -> List[int]:
    """
    Get list of incomplete turn numbers for a session.

    Args:
        session_id: Session identifier

    Returns:
        List of turn numbers that were not completed
    """
    conversation = self.load_conversation(session_id)
    total_expected = conversation.config.get("turns", 0)
    completed = conversation.total_turns
    return list(range(completed + 1, total_expected + 1))
```

2. Add resume capability to `src/protocol.py`:

```python
async def resume_protocol(
    self,
    session_id: str
) -> Conversation:
    """
    Resume an incomplete conversation session.

    Args:
        session_id: Session identifier to resume

    Returns:
        Updated conversation with additional turns
    """
    # Load existing conversation
    conversation = self.state_manager.load_conversation(session_id)

    # Get incomplete turns
    incomplete = self.state_manager.get_incomplete_turns(session_id)

    # Continue execution from where it stopped
    # ... implementation
```

3. Add CLI command in `cli.py`:

```python
@cli.command()
@click.argument("session_id")
def resume(session_id: str):
    """Resume an incomplete conversation session."""
    # Implementation
```

4. Add tests for resume functionality

---

### Task 4: Adding Streaming Support

**Steps:**

1. Implement streaming in `src/clients/grok.py`:

```python
async def chat_stream(
    self,
    prompt: str,
    model: str = "grok-fast",
    temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """
    Stream chat completion responses.

    Args:
        prompt: User prompt
        model: Model identifier
        temperature: Sampling temperature

    Yields:
        Response chunks as they arrive
    """
    model_id = self._resolve_model(model)

    stream = await self.client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

2. Update protocol engine to support streaming

3. Add CLI flag for streaming mode

4. Add tests for streaming functionality

---

### Task 5: Improving Error Handling and Retry Logic

**Steps:**

1. Create retry decorator in `src/utils.py`:

```python
import asyncio
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry async function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
```

2. Apply to API calls:

```python
from src.utils import retry_async
from openai import APIError, RateLimitError

@retry_async(
    max_attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(APIError, RateLimitError)
)
async def chat(self, prompt: str, **kwargs) -> Tuple[str, Dict]:
    """Chat with retry logic for transient errors."""
    # Implementation
```

---

## Testing Guidelines

### Writing Good Tests

**Test Structure (AAA Pattern):**

```python
@pytest.mark.asyncio
async def test_feature_name():
    """Test description explaining what is being tested."""
    # Arrange - Set up test data and dependencies
    client = GrokClient(api_key="test-key")
    prompt = "test prompt"

    # Act - Execute the code being tested
    result = await client.chat(prompt)

    # Assert - Verify the results
    assert result is not None
    assert isinstance(result, tuple)
    assert len(result) == 2
```

**Test Naming:**
- Use descriptive names: `test_sequential_execution_with_context`
- Include edge cases: `test_empty_topic_raises_error`
- Include happy path: `test_successful_conversation_completion`

**Test Coverage Goals:**
- Unit tests: Aim for 80%+ coverage
- Integration tests: Cover all client integrations
- E2E tests: Cover main user workflows

### Mocking External Dependencies

**Mock Grok API:**

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_protocol_with_mocked_grok():
    """Test protocol engine with mocked Grok client."""
    # Create mock client
    mock_grok = AsyncMock()
    mock_grok.chat.return_value = ("Mocked response", {"usage": {"total_tokens": 100}})

    # Use mock in test
    engine = ProtocolEngine(claude_client, mock_grok, state_manager)
    conversation = await engine.run_protocol(mode="loop", topic="test")

    # Verify mock was called
    assert mock_grok.chat.called
    assert mock_grok.chat.call_count == 4  # If mode has 4 Grok turns
```

**Mock Claude CLI:**

```python
@patch('asyncio.create_subprocess_exec')
@pytest.mark.asyncio
async def test_claude_client_with_mock(mock_subprocess):
    """Test Claude client with mocked subprocess."""
    # Configure mock
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"Mocked response", b"")
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process

    # Test
    client = ClaudeClient()
    response, metadata = await client.chat("test prompt")

    assert response == "Mocked response"
    assert mock_subprocess.called
```

### Running Tests in CI/CD

**GitHub Actions Example:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements-dev.txt
      - run: black --check src/ cli.py tests/
      - run: ruff check src/ cli.py tests/
      - run: pytest tests/ -v --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

---

## Important Files Reference

### Essential Reading (Start Here)

1. **START-HERE.md** - Quick start guide for new contributors
2. **HANDOFF.md** - Team handoff guide with project context
3. **README.md** - Main project documentation
4. **docs/SPEC-UPDATED.md** - Accurate technical specification

### Documentation Files

- **FINAL-SUMMARY.md** - Project completion summary
- **SPEC-COMPLETION-SUMMARY.md** - Specification completion report
- **READY-FOR-TESTING.md** - Testing readiness checklist
- **TESTING-README.md** - Testing quickstart guide
- **BILLING_TROUBLESHOOTING.md** - xAI API billing setup guide

### Specification Files (specs/)

- **CONSTITUTION.md** - Governing principles and design philosophy
- **CORE-ARCHITECTURE-SPEC.md** - Foundation architecture
- **ADVANCED-CAPABILITIES-SPEC.md** - Advanced features specification
- **TECHNICAL-PLAN.md** - Implementation plan
- **VALIDATION-CHECKLIST.md** - Quality assurance checklist

### Configuration Files

- **pyproject.toml** - Modern Python project configuration
- **requirements.txt** - Production dependencies
- **requirements-dev.txt** - Development dependencies
- **.env.example** - Environment variables template
- **.gitignore** - Git ignore patterns

### Code Entry Points

- **cli.py:246** - CLI entry point and commands
- **src/protocol.py:339** - Main protocol engine
- **src/dynamic_protocol.py:281** - Dynamic workflows
- **src/intelligent_orchestrator.py:445** - Task decomposition
- **src/state.py:208** - Session persistence
- **src/clients/grok.py:201** - Grok API client
- **src/clients/claude.py:122** - Claude CLI wrapper

### Mode Configurations

- **src/modes/loop.json** - Sequential knowledge building (8 turns)
- **src/modes/debate.json** - Adversarial exploration (6 turns)
- **src/modes/podcast.json** - Conversational dialogue (10 turns)
- **src/modes/pipeline.json** - Static workflow (7 stages)
- **src/modes/dynamic.json** - Adaptive decomposition (variable)

---

## Pitfalls to Avoid

### 1. Blocking Calls in Async Functions

**Don't:**
```python
async def fetch_data():
    response = requests.get(url)  # Blocking call!
    return response.json()
```

**Do:**
```python
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### 2. Not Handling API Errors

**Don't:**
```python
async def call_api():
    response = await client.chat(prompt)
    return response  # What if API fails?
```

**Do:**
```python
async def call_api():
    try:
        response = await client.chat(prompt)
        return response
    except APIError as e:
        logger.error(f"API call failed: {e}")
        raise
    except TimeoutError as e:
        logger.warning(f"Request timed out: {e}")
        # Implement retry or fallback
```

### 3. Hardcoding API Keys

**Don't:**
```python
client = GrokClient(api_key="xai-1234567890")  # Never!
```

**Do:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY environment variable is required")
client = GrokClient(api_key=api_key)
```

### 4. Not Preserving Session State

**Don't:**
```python
# Lose all progress if execution fails mid-conversation
conversation = await engine.run_protocol(mode="loop", topic="AI")
state_manager.save_conversation(conversation)  # Only saves at end!
```

**Do:**
```python
# Save incrementally for resumability
async def _execute_turn(self, ...):
    turn = await self._perform_turn(...)
    self.state_manager.save_turn(session_id, turn)  # Save each turn
    return turn
```

### 5. Ignoring Context Building

**Don't:**
```python
# Each turn starts fresh, no continuity
for turn in turns:
    result = await client.chat(turn.prompt)
```

**Do:**
```python
# Build context from previous turns
context = ""
for turn in turns:
    if turn.context_from:
        context = self._build_context(conversation, turn.context_from)
    prompt = turn.template.format(topic=topic, context=context)
    result = await client.chat(prompt)
```

### 6. Not Using Type Hints

**Don't:**
```python
def process_data(data):
    return data["result"]
```

**Do:**
```python
from typing import Dict, Any

def process_data(data: Dict[str, Any]) -> str:
    return data["result"]
```

### 7. Creating Modes Without Testing

**Don't:**
- Create complex mode configurations without testing
- Assume prompts will work without validation

**Do:**
- Test new modes with multiple topics
- Validate prompt templates with variable substitution
- Check context building logic
- Ensure turn dependencies are correct

### 8. Not Following Git Workflow

**Don't:**
- Commit directly to main branch
- Push without running tests
- Use vague commit messages

**Do:**
- Create feature branches
- Run tests before committing
- Write descriptive commit messages
- Follow branch naming conventions

---

## Git Workflow

### Branch Naming Conventions

```bash
# Feature branches
git checkout -b feature/add-streaming-support
git checkout -b feature/session-resume

# Bug fixes
git checkout -b fix/grok-timeout-handling
git checkout -b fix/context-building-error

# Documentation
git checkout -b docs/update-testing-guide
git checkout -b docs/add-api-reference

# Tests
git checkout -b test/add-integration-tests
git checkout -b test/improve-coverage
```

### Commit Message Format

**Structure:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting)
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

**Examples:**

```bash
# Good commit messages
git commit -m "feat: Add streaming support to Grok client

Implements async streaming for chat completions using OpenAI SDK's
streaming API. Includes error handling and proper cleanup.

Closes #123"

git commit -m "fix: Handle timeout errors in Claude client

Increase timeout from 2 minutes to 5 minutes and add proper
error handling for subprocess timeouts.

Fixes #456"

git commit -m "test: Add integration tests for protocol engine

Adds comprehensive integration tests covering sequential,
parallel, and mixed execution modes."

git commit -m "docs: Update CLAUDE.md with testing guidelines"
```

**Bad Examples:**
```bash
# Too vague
git commit -m "fix stuff"
git commit -m "updates"
git commit -m "changes"

# Missing context
git commit -m "fix bug"
git commit -m "add feature"
```

### Development Workflow

**Standard Workflow:**

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/my-feature

# 2. Make changes and commit
# ... make changes ...
black src/ cli.py tests/
ruff check --fix src/ cli.py tests/
pytest tests/ -v

git add .
git commit -m "feat: Add my feature

Detailed description of what was added and why."

# 3. Push to remote
git push origin feature/my-feature

# 4. Create pull request on GitHub

# 5. After review and approval, merge to main
```

**Branch-Specific Workflow (This Repository):**

Based on git status, this repository uses branches like:
- `claude/claude-md-mhydduzva371wvp8-01UQpzaGnBtFw5Tn1Jk7MrgS`

**Current workflow:**

```bash
# Working on designated branch
git checkout claude/claude-md-mhydduzva371wvp8-01UQpzaGnBtFw5Tn1Jk7MrgS

# Make changes
# ... development work ...

# Commit changes
git add .
git commit -m "feat: Add CLAUDE.md comprehensive guide"

# Push to remote
git push -u origin claude/claude-md-mhydduzva371wvp8-01UQpzaGnBtFw5Tn1Jk7MrgS
```

### Pre-Commit Checklist

Before committing, always:

- [ ] Run code formatter: `black src/ cli.py tests/`
- [ ] Run linter: `ruff check src/ cli.py tests/`
- [ ] Run tests: `pytest tests/ -v`
- [ ] Update documentation if needed
- [ ] Review changes: `git diff`
- [ ] Write descriptive commit message
- [ ] Check for sensitive data (API keys, secrets)

### Pull Request Guidelines

**PR Title:**
- Use same format as commit messages
- Example: `feat: Add session resume capability`

**PR Description:**
```markdown
## Summary
Brief description of changes

## Changes
- Added session resume functionality
- Updated CLI with resume command
- Added tests for resume logic

## Testing
- Ran all unit tests: ✓
- Tested resume with incomplete sessions: ✓
- Verified backward compatibility: ✓

## Documentation
- Updated README.md
- Updated CLAUDE.md
- Added inline documentation

## Related Issues
Closes #123
Related to #456
```

---

## Quick Reference

### Common Commands

```bash
# Development
pip install -e ".[dev]"           # Install with dev dependencies
black src/ cli.py tests/          # Format code
ruff check --fix src/             # Lint and fix
pytest tests/ -v                  # Run tests
pytest tests/ --cov=src           # Run with coverage

# Usage
ai-dialogue run --mode loop --topic "AI ethics"
ai-dialogue list --limit 10
ai-dialogue export session-id
ai-dialogue modes

# Testing
python3 test_live_api.py          # Test Grok API
pytest tests/simple_test.py -v    # Run simple test
pytest -m "not integration" -v    # Skip integration tests

# Git
git checkout -b feature/name      # Create feature branch
git add .                         # Stage changes
git commit -m "type: message"     # Commit with message
git push origin branch-name       # Push to remote
```

### File Locations

```bash
# Core code
src/protocol.py                   # Main protocol engine
src/clients/grok.py              # Grok API client
src/clients/claude.py            # Claude CLI wrapper
cli.py                           # CLI interface

# Configurations
src/modes/*.json                 # Mode configurations
.env                            # Environment variables
pyproject.toml                  # Project configuration

# Documentation
README.md                       # Main docs
HANDOFF.md                      # Team handoff
docs/SPEC-UPDATED.md           # Technical spec

# Testing
tests/                          # Test suite
test_live_api.py               # Live API test
```

### Environment Variables

```bash
# Required
XAI_API_KEY=xai-...             # xAI Grok API key

# Optional
ANTHROPIC_API_KEY=sk-ant-...    # If using Claude API
DEFAULT_GROK_MODEL=grok-4       # Default Grok model
DEBUG=1                         # Enable debug mode
LOG_LEVEL=INFO                  # Logging level
```

---

## Getting Help

### Internal Resources

1. **START-HERE.md** - Quick start for new contributors
2. **HANDOFF.md** - Detailed project context
3. **docs/SPEC-UPDATED.md** - Technical specification
4. **examples/example_usage.py** - Code examples

### External Resources

1. **xAI API Docs:** https://docs.x.ai/api
2. **OpenAI SDK Docs:** https://github.com/openai/openai-python
3. **Click Documentation:** https://click.palletsprojects.com/
4. **asyncio Documentation:** https://docs.python.org/3/library/asyncio.html

### Troubleshooting

**Common Issues:**

1. **"XAI_API_KEY not found"**
   - Solution: Copy `.env.example` to `.env` and add your API key

2. **"claude: command not found"**
   - Solution: Install Claude CLI or switch to using Claude API directly

3. **Tests failing with API errors**
   - Solution: Use `pytest -m "not integration"` to skip integration tests

4. **Import errors**
   - Solution: Install with `pip install -e .` to make package importable

---

## Version History

- **v1.0.0** (2025-11-14) - Initial CLAUDE.md creation
  - Comprehensive codebase documentation
  - Development workflows
  - Testing guidelines
  - Git workflow
  - Common tasks and examples

---

## Maintenance

**This file should be updated when:**
- New features are added
- Architecture changes significantly
- New conventions are adopted
- Common pitfalls are discovered
- Workflows are modified

**Update process:**
1. Make changes to CLAUDE.md
2. Commit with: `docs: Update CLAUDE.md with [change description]`
3. Ensure changes are accurate and helpful
4. Keep formatting consistent
5. Update version history

---

**End of CLAUDE.md**
