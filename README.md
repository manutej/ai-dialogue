# AI Dialogue Protocol

**Multi-Model Orchestration for Technical Research and Development**

Enable sophisticated multi-turn conversations between AI models (Claude + Grok) with configurable interaction modes, dynamic workflows, and comprehensive cost tracking.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

---

## 🎯 What is This?

A production-ready system for orchestrating conversations between multiple AI models, designed for:
- **Technical Research**: Deep exploration of complex topics (HKT, category theory, system architecture, etc.)
- **Decision Analysis**: Structured debate and evaluation of tradeoffs
- **Code Generation**: Multi-turn development with context accumulation
- **Knowledge Building**: Sequential synthesis from foundational concepts to practical applications

---

## ✨ Features

### `/grok` Command System

Three powerful Claude Code slash commands for Grok API integration:

#### `/grok` - Multi-Model Orchestration
```bash
/grok "Research Higher Kinded Types" --mode loop
/grok "Compare microservices vs monolith" --mode debate
/grok "Explain async/await" --mode podcast
```

**Supported Modes**:
- `loop` (8 turns): Sequential knowledge building
- `debate` (6 turns): Adversarial exploration
- `podcast` (10 turns): Conversational teaching
- `pipeline` (7 stages): Static workflow
- `dynamic`: Adaptive task decomposition

**Flags**:
- `--mode <mode>`: Orchestration pattern
- `--turns <n>`: Number of dialogue turns
- `--model <id>`: Specific Grok model (grok-4-fast-reasoning, grok-code-fast-1, etc.)
- `--temperature <f>`: Sampling temperature (0.0-2.0)
- `--max-tokens <n>`: Response length limit
- `--output <file>`: Save transcript
- `--verbose`: Show detailed execution info
- `--quick`: Single query bypass (no orchestration)

#### `/grok-list` - Session Management
```bash
/grok-list                    # List all sessions
/grok-list --recent 10        # Last 10 sessions
```

#### `/grok-export` - Export Sessions
```bash
/grok-export <session-id>                     # Export to markdown
/grok-export <session-id> --format json       # Export to JSON
/grok-export <session-id> --output results.md # Save to file
```

### Core Features

🔄 **Async Execution**
- Non-blocking I/O with Python asyncio
- Parallel execution where possible
- No heavy infrastructure required

🧠 **Intelligent Orchestration**
- Claude-side workflow management
- Dynamic task decomposition
- Context-aware prompts
- Adaptive loops based on results

💰 **Cost Tracking**
- Token usage monitoring
- Per-query cost calculation
- Session-level cost summaries
- Optimization recommendations

📊 **Observable**
- Session persistence (JSON)
- Markdown export
- Execution logs
- Performance metrics

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- XAI API key (get from [x.ai](https://x.ai))
- Claude Code (optional, for `/grok` commands)

### Installation

```bash
# Clone the repository
git clone https://github.com/manutej/ai-dialogue.git
cd ai-dialogue

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env and add your XAI_API_KEY
```

### For Claude Code Users

Install the `/grok` commands:

```bash
./utils/grok-commands/install.sh
```

Restart Claude Code, then use:

```bash
/grok "What is category theory?" --quick
/grok "Research microservices architecture" --mode loop --output research.md
```

---

## 📖 Usage

### Command Line Interface

```python
# Run a loop mode session
python cli.py --mode loop --topic "Distributed systems architecture" --turns 6

# Run debate mode
python cli.py --mode debate --topic "GraphQL vs REST APIs"

# Quick single query
python cli.py --quick "Explain monads in functional programming"
```

### Programmatic Usage

```python
import asyncio
from src.clients.grok import GrokClient

async def example():
    client = GrokClient()

    # Simple query
    response, tokens = await client.chat("What is a functor?")
    print(f"Response: {response}")
    print(f"Tokens: {tokens['total']} (Cost: ~${tokens['total'] * 0.00002:.6f})")

    # With parameters
    response, tokens = await client.chat(
        prompt="Explain category theory",
        model="grok-code-fast-1",
        temperature=0.7,
        max_tokens=500
    )

    await client.close()

asyncio.run(example())
```

### Orchestration Modes

#### Loop Mode: Sequential Knowledge Building
```bash
/grok "Higher Kinded Types in TypeScript" --mode loop --turns 8
```

**Pattern**: Foundation → Analysis → Evidence → Synthesis → Applications → Future → Reflection → Integration

**Cost**: ~$0.14 for 8 turns
**Best For**: Research, deep exploration, systematic learning

#### Debate Mode: Adversarial Analysis
```bash
/grok "Should we use microservices?" --mode debate --turns 6
```

**Pattern**: Proposition → Opposition → Defense → Rebuttal → Synthesis → Verdict

**Cost**: ~$0.12 for 6 turns
**Best For**: Decision-making, tradeoff analysis, critical evaluation

#### Podcast Mode: Conversational Teaching
```bash
/grok "Quantum computing for beginners" --mode podcast --turns 10
```

**Pattern**: Intro → Overview → Questions → Deep Dive → Insights → Implications → Challenge → Balance → Takeaways → Closing

**Cost**: ~$0.20 for 10 turns
**Best For**: Learning, teaching, accessible explanations

---

## 💰 Cost Analysis

Based on comprehensive testing with real queries:

### Per-Query Costs

| Query Type | Tokens | Cost | Use Case |
|------------|--------|------|----------|
| Simple fact | ~230 | $0.0046 | Quick answers |
| Code snippet | ~270 | $0.0054 | Small code examples |
| Explanation | ~350-500 | $0.007-0.01 | Technical concepts |
| Detailed analysis | ~800-1000 | $0.016-0.02 | Deep dives |

### Orchestration Session Costs

| Mode | Turns | Avg Tokens | Est. Cost | Duration |
|------|-------|------------|-----------|----------|
| Loop | 8 | ~7,000 | $0.14 | ~60s |
| Debate | 6 | ~5,000 | $0.10 | ~45s |
| Podcast | 10 | ~8,500 | $0.17 | ~75s |
| Dynamic | 4-8 | ~5,000 | $0.10 | ~40-60s |

### Monthly Cost Projections

| Usage Level | Queries/Day | Sessions/Month | Est. Cost/Month |
|-------------|-------------|----------------|-----------------|
| **Light** (Solo dev) | 10 | 10 | **$1.80** |
| **Moderate** (Active dev) | 50 | 20 | **$15.45** |
| **Heavy** (Small team) | 100 | 50 | **$57.60** |
| **Enterprise** | 500 | 100 | **$288.00** |

**Note**: Based on $0.02 per 1K tokens. Actual costs may vary.

---

## 🧪 Testing

### Comprehensive Test Suite

The project includes extensive testing with cost tracking:

```bash
# Activate virtual environment
source venv/bin/activate

# Set API key
export XAI_API_KEY='your-key-here'

# Run basic functionality tests (10 tests, ~6¢)
python3 tests/grok-commands/test_grok_with_costs.py

# Run advanced features tests (4 tests, ~22¢)
# Includes: Loop mode, Debate mode, Streaming, Specific use cases
python3 tests/grok-commands/test_advanced_features.py

# Run all existing tests
pytest tests/
```

### Test Results

✅ **14/14 tests passed** (100% success rate)
- Basic API functionality: 10 tests
- Orchestration modes: 2 tests
- Streaming: 1 test
- Real-world use cases: 1 test

**Total testing cost**: $0.28 (~28 cents)

**Test Reports**: See `tests/grok-commands/results/` for detailed cost analysis and performance metrics.

---

## 📁 Project Structure

```
ai-dialogue/
├── README.md                      # This file
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
│
├── src/                           # Source code
│   ├── clients/                   # API clients
│   │   ├── grok.py                # Grok API client
│   │   ├── claude.py              # Claude CLI wrapper
│   │   └── grok_enhanced.py       # Enhanced Grok with features
│   ├── adapters/                  # Protocol adapters
│   │   ├── base.py                # Base adapter interface
│   │   └── grok_adapter.py        # Grok adapter with token tracking
│   ├── modes/                     # Orchestration mode configs
│   │   ├── loop.json              # Loop mode (8 turns)
│   │   ├── debate.json            # Debate mode (6 turns)
│   │   ├── podcast.json           # Podcast mode (10 turns)
│   │   ├── pipeline.json          # Pipeline mode
│   │   └── dynamic.json           # Dynamic mode
│   ├── protocol.py                # Core protocol engine
│   ├── dynamic_protocol.py        # Dynamic orchestration
│   ├── intelligent_orchestrator.py # Claude-side intelligence
│   └── state.py                   # Session state management
│
├── tests/                         # Test suite
│   ├── test_adapters.py           # Adapter tests
│   ├── test_protocol.py           # Protocol tests
│   ├── test_grok_enhanced.py      # Enhanced client tests
│   └── grok-commands/             # /grok command tests
│       ├── test_grok_with_costs.py        # Basic tests + cost tracking
│       ├── test_advanced_features.py      # Orchestration + streaming tests
│       ├── results/                       # Test reports and logs
│       │   ├── FINAL-COMPREHENSIVE-REPORT-20251114.md
│       │   ├── COMPREHENSIVE-TEST-REPORT-20251114.md
│       │   └── TEST-SUMMARY.md
│       └── docs/                          # Test documentation
│
├── utils/                         # Utilities
│   └── grok-commands/             # /grok command installation
│       ├── install.sh             # Install script
│       ├── commands/              # Command definitions
│       │   ├── grok.md            # Main /grok command
│       │   ├── grok-list.md       # Session listing
│       │   └── grok-export.md     # Export functionality
│       └── README.md              # Command documentation
│
├── docs/                          # Documentation
│   ├── API.md                     # API reference
│   ├── MODES.md                   # Orchestration modes guide
│   ├── COST-OPTIMIZATION.md       # Cost optimization strategies
│   └── project-history/           # Historical documentation
│
├── examples/                      # Usage examples
│   └── research_hkt.py            # HKT research example
│
├── specs/                         # Technical specifications
│   └── grok-consult.md            # Original Grok consultation spec
│
├── sessions/                      # Session storage (gitignored)
├── logs/                          # Execution logs (gitignored)
└── cli.py                         # Command-line interface
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
XAI_API_KEY=your-xai-api-key

# Optional
GROK_MODEL=grok-4-fast-reasoning-latest  # Default model
GROK_TEMPERATURE=0.7                      # Default temperature
GROK_MAX_TOKENS=4096                      # Default max tokens
```

### Model Options

```
Text Generation (Grok 4):
- grok-4-fast-reasoning-latest (recommended - best balance)
- grok-4-fast-non-reasoning-latest (faster, simpler tasks)
- grok-code-fast-1 (code-specialized, 43% more expensive)

Vision (Grok 2):
- grok-2-vision-latest (multimodal - images + text)
- grok-2-image-latest (image generation)
```

**Recommendation**: Use default model (`grok-4-fast-reasoning`) for most tasks. Only use code model for code-heavy work due to higher cost.

---

## 📚 Documentation

- **[Command Reference](utils/grok-commands/README.md)**: `/grok` command documentation and usage guide
- **[Test Reports](tests/grok-commands/results/)**: Comprehensive test results with cost analysis
- **[Testing Guide](docs/TESTING-GUIDE.md)**: Testing strategies and guidelines
- **[Grok Quick Reference](docs/GROK-QUICK-REFERENCE.md)**: Quick reference for Grok API features
- **[Migration Guide](docs/MIGRATION-GUIDE.md)**: Upgrading and migration instructions
- **[Roadmap](docs/ROADMAP.md)**: Project roadmap and future plans

**In This README:**
- Orchestration Modes: See [Usage](#-usage) section above
- Cost Analysis: See [Cost Analysis](#-cost-analysis) section above
- API Examples: See [Usage](#-usage) and [Quick Start](#-quick-start) sections

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit with clear messages
6. Push to your branch
7. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run type checking (if using mypy)
mypy src/

# Format code (if using black)
black src/ tests/
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "XAI_API_KEY not set"
```bash
# Solution: Set environment variable
export XAI_API_KEY='your-key-here'
# Or add to .env file
```

**Issue**: "/grok command not found"
```bash
# Solution: Install commands and restart Claude Code
./utils/grok-commands/install.sh
# Then completely restart Claude Code
```

**Issue**: "ModuleNotFoundError"
```bash
# Solution: Install in development mode
pip install -e .
```

**Issue**: High API costs
```bash
# Solution: Use max_tokens to control costs
/grok "query" --max-tokens 200
# See docs/COST-OPTIMIZATION.md for more strategies
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for Claude and Claude Code
- **xAI** for Grok API
- **OpenAI** for SDK compatibility layer
- The functional programming community for inspiration

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/manutej/ai-dialogue/issues)
- **Discussions**: [GitHub Discussions](https://github.com/manutej/ai-dialogue/discussions)
- **Documentation**: [Project Docs](docs/)

---

## 🗺️ Roadmap

- [ ] Add more orchestration modes (Socratic, Tutorial, etc.)
- [ ] Implement cost budgeting and alerts
- [ ] Add Claude API integration (when available)
- [ ] Build web UI for session management
- [ ] Support additional AI providers
- [ ] Implement caching for repeated queries
- [ ] Add collaborative multi-user sessions

---

**Built with ❤️ for technical research and AI-assisted development**

*Last Updated: 2025-11-14*
