# AI Dialogue Protocol

**Multi-Model Orchestration for Technical Research and Development**

Enable sophisticated multi-turn conversations between AI models (Claude + Grok) with configurable interaction modes, dynamic workflows, and comprehensive cost tracking.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

---

## 📑 Table of Contents

- [What is This?](#-what-is-this)
- [Quick Start](#-quick-start)
- [Sample Queries](#-sample-queries)
- [Key Features](#-key-features)
- [Usage](#-usage)
- [Orchestration Modes](#-orchestration-modes-explained)
- [Cost Analysis](#-cost-analysis)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 What is This?

A production-ready system for orchestrating conversations between multiple AI models, designed for:

- **Technical Research**: Deep exploration of complex topics (HKT, category theory, system architecture)
- **Decision Analysis**: Structured debate and evaluation of tradeoffs
- **Code Generation**: Multi-turn development with context accumulation
- **Knowledge Building**: Sequential synthesis from foundational concepts to practical applications

<br>

## 🚀 Quick Start

### Installation (5 minutes)

```bash
# Clone and install
git clone https://github.com/manutej/ai-dialogue.git
cd ai-dialogue
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Set up API key
cp .env.example .env
# Edit .env and add your XAI_API_KEY from https://x.ai
```

### For Claude Code Users

```bash
# Install /grok commands
./utils/grok-commands/install.sh

# Restart Claude Code, then try:
/grok "What is category theory?" --quick
```

<br>

## 💡 Sample Queries

Get started with these example queries:

### Quick Answers (--quick mode)
```bash
/grok "Explain async/await in Python" --quick
/grok "What are the SOLID principles?" --quick
/grok "Compare REST vs GraphQL APIs" --quick
```

### Research Mode (--mode loop)
Deep exploration with 8-turn knowledge building:
```bash
/grok "Research Higher Kinded Types in TypeScript" --mode loop --output hkt-research.md
/grok "Explore category theory fundamentals" --mode loop
/grok "Deep dive into distributed systems patterns" --mode loop --turns 10
```

### Debate Mode (--mode debate)
Adversarial analysis for decision-making:
```bash
/grok "Should we use microservices or monolith?" --mode debate
/grok "Evaluate GraphQL vs REST for our API" --mode debate
/grok "TypeScript vs JavaScript for new projects" --mode debate
```

### Podcast Mode (--mode podcast)
Conversational teaching format:
```bash
/grok "Explain quantum computing for beginners" --mode podcast
/grok "Make functional programming accessible" --mode podcast
/grok "Teach Docker containerization" --mode podcast
```

### Cost-Conscious Queries
```bash
# Limit tokens to control costs
/grok "Explain monads" --quick --max-tokens 200

# Save expensive research sessions
/grok "Research event sourcing patterns" --mode loop --output saved-research.md
```

**💰 Cost**: Quick queries ~$0.005 each | Research sessions ~$0.14 | See [Cost Analysis](#-cost-analysis) for details

<br>

## ✨ Key Features

### `/grok` Command System

Three powerful Claude Code slash commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `/grok` | Multi-model orchestration | `/grok "Research HKT" --mode loop` |
| `/grok-list` | Session management | `/grok-list --recent 10` |
| `/grok-export` | Export sessions | `/grok-export <id> --format json` |

### Orchestration Modes

- **`loop`** (8 turns): Sequential knowledge building for research
- **`debate`** (6 turns): Adversarial analysis for decision-making
- **`podcast`** (10 turns): Conversational teaching format
- **`pipeline`** (7 stages): Static workflow execution
- **`dynamic`**: Adaptive task decomposition

### Core Capabilities

🔄 **Async Execution** - Non-blocking I/O, no heavy infrastructure
🧠 **Intelligent Orchestration** - Dynamic task decomposition, context-aware prompts
💰 **Cost Tracking** - Token monitoring, per-query costs, optimization tips
📊 **Observable** - Session persistence, markdown export, execution logs

<br>

## 📖 Usage

### Command Line

```bash
# Quick single query
python cli.py --quick "Explain monads in functional programming"

# Research mode
python cli.py --mode loop --topic "Distributed systems" --turns 6

# Debate mode
python cli.py --mode debate --topic "GraphQL vs REST APIs"
```

### Programmatic API

```python
import asyncio
from src.clients.grok import GrokClient

async def example():
    client = GrokClient()

    # Simple query
    response, tokens = await client.chat("What is a functor?")
    print(f"Response: {response}")
    print(f"Cost: ~${tokens['total'] * 0.00002:.6f}")

    await client.close()

asyncio.run(example())
```

### Advanced Usage

**Custom Parameters:**
```bash
/grok "Explain category theory" \
  --model grok-4-fast-reasoning \
  --temperature 0.7 \
  --max-tokens 1000 \
  --output theory.md \
  --verbose
```

**Session Management:**
```bash
# List recent sessions
/grok-list --recent 10

# Export session to markdown
/grok-export <session-id> --output research.md

# Export to JSON for processing
/grok-export <session-id> --format json
```

<br>

## 🎭 Orchestration Modes Explained

### Loop Mode: Sequential Knowledge Building

```bash
/grok "Higher Kinded Types in TypeScript" --mode loop --turns 8
```

**Flow**: Foundation → Analysis → Evidence → Synthesis → Applications → Future → Reflection → Integration
**Best For**: Research, deep exploration, systematic learning
**Cost**: ~$0.14 for 8 turns (~60 seconds)

### Debate Mode: Adversarial Analysis

```bash
/grok "Should we use microservices?" --mode debate --turns 6
```

**Flow**: Proposition → Opposition → Defense → Rebuttal → Synthesis → Verdict
**Best For**: Decision-making, tradeoff analysis, critical evaluation
**Cost**: ~$0.10 for 6 turns (~45 seconds)

### Podcast Mode: Conversational Teaching

```bash
/grok "Quantum computing for beginners" --mode podcast --turns 10
```

**Flow**: Intro → Overview → Questions → Deep Dive → Insights → Implications → Challenge → Balance → Takeaways → Closing
**Best For**: Learning, teaching, accessible explanations
**Cost**: ~$0.17 for 10 turns (~75 seconds)

<br>

## 💰 Cost Analysis

### Quick Reference

| Query Type | Tokens | Cost | Example |
|------------|--------|------|---------|
| Simple fact | ~230 | $0.005 | "What is REST?" |
| Code snippet | ~270 | $0.005 | "Show me a decorator" |
| Explanation | ~350-500 | $0.007-0.01 | "Explain async/await" |
| Deep analysis | ~800-1000 | $0.016-0.02 | Research sessions |

### Monthly Projections

| Usage Level | Queries/Day | Est. Cost/Month |
|-------------|-------------|-----------------|
| **Light** (Solo dev) | 10 queries | **$1.80** |
| **Moderate** (Active dev) | 50 queries | **$15.45** |
| **Heavy** (Small team) | 100 queries | **$57.60** |

**Note**: Based on $0.02 per 1K tokens. Actual costs may vary.

**Cost Control Tips:**
- Use `--quick` for simple queries (no orchestration overhead)
- Set `--max-tokens` to limit response length
- Save sessions with `--output` to avoid re-running expensive queries
- Use `--mode debate` (6 turns) instead of `--mode loop` (8 turns) when appropriate

<br>

## 🔧 Configuration

### Environment Variables

```bash
# Required
XAI_API_KEY=your-xai-api-key

# Optional (with defaults)
GROK_MODEL=grok-4-fast-reasoning-latest
GROK_TEMPERATURE=0.7
GROK_MAX_TOKENS=4096
```

### Model Options

```
Text Generation (Currently Available):
├─ grok-4-fast-reasoning-latest  ← Recommended (best balance)
├─ grok-4-fast-non-reasoning-latest (faster, simpler tasks)
└─ grok-code-fast-1 (code-specialized, 43% more expensive)

Vision (Grok 2):
├─ grok-2-vision-latest (multimodal - images + text)
└─ grok-2-image-latest (image generation)

🚀 Grok 4.1 Status (Released Nov 17-18, 2025):
   • Available on: grok.com, X platform, iOS/Android apps
   • NOT YET available via xAI API (awaiting official release)
   • System will auto-upgrade when API access opens
   • See: https://x.ai/news/grok-4-1
```

**Recommendation**: Use default `grok-4-fast-reasoning-latest` for most tasks.
**Status**: System is ready for automatic Grok 4.1 API upgrade when released by xAI.

<br>

## 🧪 Testing

### Run Tests

```bash
# Activate environment
source venv/bin/activate
export XAI_API_KEY='your-key-here'

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Results

✅ **14/14 tests passed** (100% success rate)
- Basic API functionality: 10 tests
- Orchestration modes: 2 tests
- Streaming: 1 test
- Real-world use cases: 1 test

**Total testing cost**: $0.28

See [Test Reports](tests/grok-commands/results/) for detailed cost analysis.

<br>

## 📚 Documentation

### Quick Links

- **[Command Reference](utils/grok-commands/README.md)** - `/grok` command documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Test Reports](tests/grok-commands/results/)** - Test results with cost analysis
- **[Testing Guide](docs/TESTING-GUIDE.md)** - Testing strategies
- **[Migration Guide](docs/MIGRATION-GUIDE.md)** - Upgrading instructions
- **[Roadmap](docs/ROADMAP.md)** - Project roadmap

### In This README

- **Orchestration Modes**: See [Orchestration Modes](#-orchestration-modes-explained)
- **Cost Analysis**: See [Cost Analysis](#-cost-analysis)
- **API Examples**: See [Usage](#-usage) and [Quick Start](#-quick-start)

<br>

## 📁 Project Structure

<details>
<summary>Click to expand full project structure</summary>

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
│       ├── test_grok_with_costs.py
│       ├── test_advanced_features.py
│       └── results/               # Test reports
│
├── utils/                         # Utilities
│   └── grok-commands/             # /grok command installation
│       ├── install.sh
│       ├── commands/
│       └── README.md
│
├── docs/                          # Documentation
├── examples/                      # Usage examples
├── specs/                         # Technical specifications
└── cli.py                         # Command-line interface
```

</details>

<br>

## 🤝 Contributing

Contributions welcome! See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

**Quick Start:**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit with clear messages
6. Open a Pull Request

<br>

## 🐛 Troubleshooting

### Common Issues

**"XAI_API_KEY not set"**
```bash
export XAI_API_KEY='your-key-here'
# Or add to .env file
```

**"/grok command not found"**
```bash
./utils/grok-commands/install.sh
# Then restart Claude Code completely
```

**"ModuleNotFoundError"**
```bash
pip install -e .
```

**High API costs**
```bash
/grok "query" --quick --max-tokens 200
```

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for more troubleshooting help.

<br>

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/manutej/ai-dialogue/issues)
- **Discussions**: [GitHub Discussions](https://github.com/manutej/ai-dialogue/discussions)
- **Documentation**: [Project Docs](docs/)

<br>

## 🗺️ Roadmap

- [ ] Add more orchestration modes (Socratic, Tutorial, etc.)
- [ ] Implement cost budgeting and alerts
- [ ] Add Claude API integration (when available)
- [ ] Build web UI for session management
- [ ] Support additional AI providers
- [ ] Implement caching for repeated queries
- [ ] Add collaborative multi-user sessions

<br>

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

<br>

## 🙏 Acknowledgments

- **Anthropic** for Claude and Claude Code
- **xAI** for Grok API
- **OpenAI** for SDK compatibility layer
- The functional programming community for inspiration

---

**Built with ❤️ for technical research and AI-assisted development**

*Last Updated: 2025-11-19 (xAI API documentation verified)*
