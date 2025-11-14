# Grok Commands for Claude Code

**Version**: 1.0.0
**Created**: 2025-11-13
**Author**: ai-dialogue project
**License**: MIT

---

## Overview

This package provides three powerful slash commands for Claude Code that enable multi-model orchestration with xAI's Grok models:

- **`/grok`** - Multi-model orchestration for complex queries
- **`/grok-list`** - List and manage dialogue sessions
- **`/grok-export`** - Export sessions to various formats

**Key Features**:
- 🎯 6 orchestration modes (loop, debate, podcast, pipeline, dynamic, research-enhanced)
- 🚀 Quick mode for 95% of use cases (single-turn queries)
- 🔧 14 configuration flags for fine-grained control
- 💾 Session management and export
- 🔄 5-level portable path detection (no hardcoded paths)
- 🏗️ Three-layer architecture (commands → orchestration → adapters)

---

## Quick Start

### Installation

**Option 1: Project-Level Installation** (Recommended for ai-dialogue users)

```bash
# From ai-dialogue project root:
./utils/grok-commands/install.sh

# This installs commands to:
# .claude/commands/grok.md
# .claude/commands/grok-list.md
# .claude/commands/grok-export.md
```

**Option 2: Global Installation** (Available everywhere)

```bash
# Copy commands to global Claude Code directory:
cp utils/grok-commands/commands/*.md ~/.claude/commands/

# Or use installer:
./utils/grok-commands/install.sh --global
```

**Option 3: Manual Installation**

```bash
# Copy individual commands:
cp utils/grok-commands/commands/grok.md ~/.claude/commands/
cp utils/grok-commands/commands/grok-list.md ~/.claude/commands/
cp utils/grok-commands/commands/grok-export.md ~/.claude/commands/

# Restart Claude Code to load new commands
```

---

### Prerequisites

1. **xAI API Key**
   ```bash
   export XAI_API_KEY='your-key-here'

   # Make permanent:
   echo 'export XAI_API_KEY="your-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **ai-dialogue Project** (or set path manually)
   ```bash
   # Option A: Run from ai-dialogue directory (auto-detected)
   cd ~/path/to/ai-dialogue

   # Option B: Set environment variable
   export GROK_PROJECT_PATH="/path/to/ai-dialogue"

   # Option C: Configure in settings.json
   # Add to ~/.claude/settings.json:
   {
     "grok": {
       "project_path": "/path/to/ai-dialogue"
     }
   }
   ```

3. **Python Dependencies** (if using ai-dialogue project)
   ```bash
   cd ai-dialogue
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

---

## Usage

### Quick Mode (95% of use cases)

```bash
# Simple question
/grok --quick "What is quantum computing?"

# With specific model
/grok --quick --model grok-beta "Explain recursion"

# Save to file
/grok --quick --output results.txt "List programming paradigms"
```

### Orchestration Modes

```bash
# Loop: Sequential knowledge building (8 turns)
/grok --mode loop "Explain category theory"

# Debate: Adversarial exploration (6 turns)
/grok --mode debate "Is AI beneficial or harmful?"

# Podcast: Conversational dialogue (10 turns)
/grok --mode podcast "Future of space exploration"

# Pipeline: Static workflow (7 turns)
/grok --mode pipeline "Analyze: The quick brown fox"

# Dynamic: Adaptive decomposition (variable turns)
/grok --mode dynamic "Complex multi-step problem"

# Research-enhanced: Deep research (variable turns)
/grok --mode research-enhanced "Recent advances in quantum computing"
```

### Session Management

```bash
# List all sessions
/grok-list

# Export session to markdown (default)
/grok-export 20251113-123456

# Export to JSON
/grok-export --format json 20251113-123456

# Export to file
/grok-export --output session.md 20251113-123456
```

### Advanced Flags

```bash
# Custom turn count
/grok --mode loop --turns 5 "Your query"

# Temperature control (0.0 = deterministic, 2.0 = creative)
/grok --quick --temperature 0.5 "Your query"

# Token limit
/grok --quick --max-tokens 1000 "Your query"

# Verbose output (detailed execution info)
/grok --quick --verbose "Your query"

# Test adapter (verify setup)
/grok --test

# Information commands
/grok --help
/grok --list-models
/grok --list-modes
```

---

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────┐
│  Layer 1: Slash Commands                │
│  (.claude/commands/grok*.md)             │
│  - User interface                        │
│  - Flag parsing                          │
│  - Path detection (5 levels)            │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Layer 2: Orchestration Engine           │
│  (src/orchestration/grok_orchestrator.py)│
│  - Mode selection (6 modes)              │
│  - Multi-turn dialogue                   │
│  - Session management                    │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Layer 3: Model Adapters                 │
│  (src/clients/grok.py)                   │
│  - xAI API integration                   │
│  - Model-specific handling               │
│  - Error handling & retries              │
└─────────────────────────────────────────┘
```

### 5-Level Path Detection

Commands automatically detect the ai-dialogue project location:

1. **Environment Variable**: `$GROK_PROJECT_PATH`
2. **Settings File**: `~/.claude/settings.json` → `grok.project_path`
3. **Current Directory**: Auto-detect if running from ai-dialogue
4. **Common Locations**: Check standard paths
5. **Fail with Instructions**: Clear setup guidance

**Result**: Zero hardcoded paths, works on any system!

---

## File Structure

```
utils/grok-commands/
├── README.md                     # This file
├── install.sh                    # Installation script
├── commands/                     # Slash command definitions
│   ├── grok.md                   # Main orchestration command
│   ├── grok-list.md              # Session listing
│   └── grok-export.md            # Session export
└── docs/                         # Documentation
    ├── GROK-COMMANDS-QUICK-REFERENCE.md
    └── GROK-COMMANDS-VALIDATION-REPORT.md
```

---

## Testing

Comprehensive test suite available in `tests/grok-commands/`:

```bash
# Quick test (5 critical tests, ~1 minute)
./tests/grok-commands/scripts/run-quick-tests.sh

# Full test suite (40 tests, ~15 minutes)
./tests/grok-commands/scripts/test-grok-commands.sh --full

# See test documentation
cat tests/grok-commands/docs/TESTING-SUMMARY.md
```

**Test Coverage**:
- ✅ All 3 commands
- ✅ All 14 flags
- ✅ All 6 orchestration modes
- ✅ Error handling
- ✅ Path detection
- ✅ API integration

---

## Configuration

### Environment Variables

```bash
# Required
export XAI_API_KEY='xai-...'

# Optional
export GROK_PROJECT_PATH='/path/to/ai-dialogue'
```

### Settings File

Add to `~/.claude/settings.json`:

```json
{
  "grok": {
    "project_path": "/Users/you/path/to/ai-dialogue",
    "default_model": "grok-beta",
    "default_mode": "loop",
    "default_temperature": 0.7,
    "session_storage": ".grok/sessions"
  }
}
```

---

## Orchestration Modes Explained

### Loop Mode (default)
- **Purpose**: Sequential knowledge building
- **Turns**: 8 (configurable)
- **Use Case**: Complex topics requiring progressive understanding
- **Example**: "Explain quantum field theory"

### Debate Mode
- **Purpose**: Adversarial exploration
- **Turns**: 6 (configurable)
- **Use Case**: Controversial topics, trade-off analysis
- **Example**: "Should we pursue AGI development?"

### Podcast Mode
- **Purpose**: Conversational dialogue
- **Turns**: 10 (configurable)
- **Use Case**: Engaging explanations, storytelling
- **Example**: "History of the internet"

### Pipeline Mode
- **Purpose**: Static multi-stage workflow
- **Turns**: 7 (fixed stages)
- **Use Case**: Structured analysis tasks
- **Example**: "Analyze this code snippet"

### Dynamic Mode
- **Purpose**: Adaptive query decomposition
- **Turns**: Variable (based on complexity)
- **Use Case**: Complex problems requiring sub-task breakdown
- **Example**: "Design a microservices architecture"

### Research-Enhanced Mode
- **Purpose**: Deep research with synthesis
- **Turns**: Variable (research + synthesis)
- **Use Case**: Topics requiring comprehensive research
- **Example**: "Latest developments in quantum computing"

---

## Available Models

```bash
# List all available models
/grok --list-models
```

**Current Models**:
- `grok-beta` (default) - Latest production model
- `grok-vision-beta` - Vision-enabled model
- `grok-3` - Third-generation model
- And more (see `--list-models`)

---

## Session Storage

Sessions are stored in: `.grok/sessions/`

**Format**: `YYYYMMDD-HHMMSS.json`

**Structure**:
```json
{
  "session_id": "20251113-123456",
  "created_at": "2025-11-13T12:34:56Z",
  "mode": "loop",
  "query": "Explain quantum computing",
  "model": "grok-beta",
  "turns": 8,
  "dialogue": [
    {"turn": 1, "query": "...", "response": "..."},
    {"turn": 2, "query": "...", "response": "..."}
  ],
  "metadata": {...}
}
```

---

## Troubleshooting

### Commands Not Found

**Problem**: `/grok` shows "command not found"

**Solution**:
```bash
# Verify installation
ls -lh .claude/commands/grok*.md

# Reinstall if needed
./utils/grok-commands/install.sh

# Restart Claude Code completely
```

---

### API Key Errors

**Problem**: "API key not found" or authentication failures

**Solution**:
```bash
# Check if set
echo $XAI_API_KEY

# Set and verify
export XAI_API_KEY='xai-...'
curl https://api.x.ai/v1/models -H "Authorization: Bearer $XAI_API_KEY"
```

---

### Path Detection Failures

**Problem**: "Could not locate ai-dialogue project"

**Solution**:
```bash
# Option 1: Use environment variable
export GROK_PROJECT_PATH='/full/path/to/ai-dialogue'

# Option 2: Run from project directory
cd /path/to/ai-dialogue
/grok --quick "test"

# Option 3: Add to settings.json (permanent)
```

---

### Python/Import Errors

**Problem**: "ModuleNotFoundError" or import failures

**Solution**:
```bash
cd ai-dialogue
source venv/bin/activate
pip install -e .

# Verify
python -c "from src.clients.grok import GrokClient; print('OK')"
```

---

## Examples

### Example 1: Quick Research

```bash
/grok --quick "What are the key principles of category theory?"
```

**Output**: Single concise response from Grok

---

### Example 2: Deep Exploration

```bash
/grok --mode loop --turns 10 "Explain monads in category theory"
```

**Output**: 10-turn dialogue progressively building understanding

---

### Example 3: Debate Analysis

```bash
/grok --mode debate --turns 6 "Functional vs Object-Oriented Programming"
```

**Output**: Thesis/antithesis exploration of both paradigms

---

### Example 4: Save and Export

```bash
# Create session
/grok --mode podcast --output session.txt "History of AI"

# List sessions
/grok-list

# Export to markdown
/grok-export 20251113-123456 > ai-history.md
```

---

## Contributing

If you enhance these commands or find issues:

1. **Test your changes**:
   ```bash
   ./tests/grok-commands/scripts/run-quick-tests.sh
   ```

2. **Update documentation** in `utils/grok-commands/docs/`

3. **Follow architecture**:
   - Commands: Flag parsing, path detection
   - Orchestration: Mode logic, session management
   - Adapters: API integration, error handling

4. **Maintain portability**: No hardcoded paths!

---

## Changelog

### v1.0.0 (2025-11-13)
- Initial release
- 3 slash commands (grok, grok-list, grok-export)
- 6 orchestration modes
- 14 configuration flags
- 5-level path detection
- Comprehensive test suite (40 tests)
- Full documentation

---

## License

MIT License - Free to use, modify, and distribute

---

## Support

**Documentation**:
- Quick Reference: `utils/grok-commands/docs/GROK-COMMANDS-QUICK-REFERENCE.md`
- Validation Report: `utils/grok-commands/docs/GROK-COMMANDS-VALIDATION-REPORT.md`
- Testing Guide: `tests/grok-commands/docs/TESTING-SUMMARY.md`

**Project**:
- Repository: `ai-dialogue/` (part of LUXOR/PROJECTS)
- Commands: `.claude/commands/grok*.md`
- Tests: `tests/grok-commands/`

---

**Enjoy orchestrating with Grok!** 🚀
