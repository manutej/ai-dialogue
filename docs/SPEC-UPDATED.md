# AI Dialogue Protocol - Updated Specification

**Version**: 1.1.0
**Status**: Beta
**Philosophy**: Simple, pragmatic, reality-based
**Last Updated**: 2025-01-11

---

## Executive Summary

Universal asynchronous AI orchestration protocol enabling multi-turn conversations between Claude (via CLI) and Grok (via API). This specification has been updated to reflect actual xAI API capabilities as of January 2025, separating implemented features from aspirational ones.

**Key Changes from v1.0**:
- Corrected model IDs (grok-4-0709, grok-3, grok-2-vision-1212)
- Removed aspirational features not yet available
- Added clear distinction between implemented and planned features
- Updated success criteria to be measurable and realistic

---

## Core Principles (Unchanged)

1. **Simplicity First**: ~500 lines of Python, no complex frameworks
2. **Async Where It Matters**: asyncio for non-blocking I/O, not message queues
3. **Config Over Code**: Modes defined in JSON, not hardcoded
4. **File-Based State**: JSON or SQLite, no databases
5. **Pragmatic Observability**: Logs + markdown output, no Prometheus

---

## Available xAI API Features (Verified)

### Models (Actually Available)
- **grok-4-0709**: Latest reasoning model (note the version suffix)
- **grok-4-fast**: Fast variant (availability TBD)
- **grok-3**: Previous generation model
- **grok-2-vision-1212**: Multimodal model for image understanding
- **grok-2-image**: Image generation model

### Confirmed API Endpoints
1. **Chat Completions**: `POST /v1/chat/completions`
   - Standard OpenAI-compatible format
   - Streaming support
   - System/user/assistant messages
   - Usage statistics with token details

2. **Deferred Completions**:
   - `POST /v1/chat/deferred-completion` (initiate)
   - `GET /v1/chat/deferred-completion/{request_id}` (retrieve)

3. **Models Information**:
   - `GET /v1/language-models` (list all)
   - `GET /v1/language-models/{model_id}` (specific model)

4. **Live Search** (via search_parameters):
   - Modes: off, auto, on
   - Return citations
   - Date range filtering
   - Source specification

5. **Legacy Endpoints**:
   - `POST /v1/completions` (text completion)
   - `POST /v1/complete` (Anthropic-compatible)

### Features Requiring Verification
- **Function Calling**: Documentation shows client-side tool support
- **Image Understanding**: Via image_url content type (for vision models)
- **Server-Side Tools**: Mentioned but not confirmed (web_search, x_search, code_execution)
- **Collections API**: Documented extensively but no endpoints confirmed
- **Files API**: Documented but implementation unclear

---

## Current Implementation Status

### ✅ Implemented & Working
1. **Basic GrokClient** (`src/clients/grok.py`)
   - AsyncOpenAI wrapper with XAI endpoint
   - Chat completion (non-streaming)
   - Streaming responses
   - Token usage tracking
   - Model selection (but needs ID updates)

2. **Project Structure**
   - Clean separation of clients, protocol, state
   - Mode configurations in JSON
   - CLI scaffolding

### ⚠️ Needs Update
1. **Model IDs**: Update from "grok-4" to "grok-4-0709"
2. **Error Handling**: Add retry logic for API failures
3. **Tests**: No test coverage yet

### ❌ Not Implemented
1. **Protocol Engine**: Core orchestration logic
2. **Claude Client**: CLI wrapper
3. **State Management**: Session persistence
4. **Mode Execution**: Turn-based dialogue logic
5. **CLI Commands**: Run, resume, export functionality

---

## Realistic Success Criteria

### Phase 1: Core Functionality (Current Sprint)
- ✅ Project structure created
- ⚠️ Grok client works with correct model IDs
- ❌ Claude CLI wrapper implemented
- ❌ Basic loop mode executes successfully
- ❌ Session state persists to JSON

### Phase 2: Essential Features (Next Sprint)
- All 5 modes execute successfully
- Async execution for parallel turns
- Export to markdown works
- Basic error handling and retries
- Unit tests for core components

### Phase 3: Enhanced Features (Future)
- Streaming output to terminal
- Cost tracking
- Image understanding (if vision models accessible)
- Function calling (if confirmed working)

---

## Architecture (Simplified)

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

## Updated Grok Client Interface

```python
class GrokClient:
    """Async client for Grok API with corrected model IDs"""

    # Correct model IDs as of January 2025
    MODELS = {
        "grok-4": "grok-4-0709",  # Map alias to actual ID
        "grok-3": "grok-3",
        "vision": "grok-2-vision-1212",
        "image": "grok-2-image"
    }

    def __init__(self, api_key: str = None, model: str = "grok-4-0709"):
        """Initialize with correct model ID"""
        self.api_key = api_key or os.environ.get("XAI_API_KEY")
        self.default_model = self.MODELS.get(model, model)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )

    async def chat(self, prompt: str, model: str = None, **kwargs):
        """Chat with model ID validation"""
        use_model = self.MODELS.get(model, model) if model else self.default_model
        # ... rest of implementation
```

---

## Testing Strategy (Updated)

### Unit Tests (Priority 1)
```python
def test_model_id_mapping():
    """Test that model aliases map to correct IDs"""
    assert GrokClient.MODELS["grok-4"] == "grok-4-0709"

async def test_grok_client_initialization():
    """Test client initializes with correct endpoint"""

async def test_basic_chat_completion():
    """Test chat completion with mocked response"""
```

### Integration Tests (Priority 2)
```python
@pytest.mark.skipif(not os.getenv("XAI_API_KEY"), reason="No API key")
async def test_real_grok_api():
    """Test actual API call with minimal prompt"""

async def test_claude_cli_execution():
    """Test Claude CLI subprocess wrapper"""
```

### E2E Tests (Priority 3)
```python
async def test_single_turn_dialogue():
    """Test one complete turn of dialogue"""

async def test_loop_mode_execution():
    """Test full loop mode with 3 turns"""
```

---

## Implementation Roadmap (Revised)

### Week 1: Stabilization
- [x] Review and update specification
- [ ] Fix model IDs in GrokClient
- [ ] Implement basic Claude wrapper
- [ ] Create minimal protocol engine
- [ ] Test with single turn

### Week 2: Core Features
- [ ] Implement state management
- [ ] Build all 5 mode configs
- [ ] Add turn orchestration
- [ ] Create CLI interface
- [ ] Write unit tests

### Week 3: Polish & Handoff
- [ ] Add error handling
- [ ] Implement markdown export
- [ ] Write documentation
- [ ] Create example sessions
- [ ] Prepare handoff package

---

## Non-Goals (Maintained)

We explicitly avoid over-engineering:

❌ **Message Queues**: No Kafka, RabbitMQ, Redis
❌ **Microservices**: Single Python process only
❌ **Complex Features**: No Collections API, Files API (until confirmed)
❌ **Heavy Observability**: No Prometheus, Grafana
❌ **Unverified Features**: No server-side tools until confirmed

---

## Configuration Files

### Updated Mode Config Example
```json
{
  "name": "loop",
  "description": "Sequential knowledge building",
  "turns": 8,
  "models": {
    "claude": "default",
    "grok": "grok-4-0709"  // Correct model ID
  },
  "structure": "sequential",
  "participants": ["claude", "grok"],
  "prompts": {
    "turn_1": {
      "role": "foundation",
      "template": "Establish foundational concepts for {topic}...",
      "participant": "grok",
      "model": "grok-4-0709",  // Explicit model ID
      "context_from": []
    }
  }
}
```

---

## Summary of Changes

### What's Real (Keep)
- OpenAI-compatible API at https://api.x.ai/v1
- Basic chat completions with streaming
- Models: grok-4-0709, grok-3, grok-2-vision-1212
- AsyncOpenAI SDK compatibility
- Token usage tracking

### What's Aspirational (Remove/Defer)
- Collections API (no confirmed endpoints)
- Files API (implementation unclear)
- Server-side tools (unverified)
- Enhanced features from GROK-NEW-FEATURES.md

### What Needs Fixing
- Model IDs (add version suffixes)
- Error handling
- Test coverage
- Documentation accuracy

---

## Definition of Done

The project is ready for handoff when:

1. ✅ GrokClient uses correct model IDs
2. ✅ ClaudeClient wraps CLI successfully
3. ✅ At least one mode (loop) executes end-to-end
4. ✅ State persists and resumes correctly
5. ✅ Markdown export produces readable output
6. ✅ Unit tests cover core components
7. ✅ README accurately describes what works
8. ✅ Known limitations are documented

---

**Philosophy**: Ship what works. Document what's real. Build incrementally.

**Status**: Specification updated for reality
**Next Step**: Fix model IDs in implementation