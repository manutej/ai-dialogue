# Contributing to AI Dialogue

Thank you for your interest in contributing to AI Dialogue! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

---

## Code of Conduct

This project adheres to a code of professional conduct. By participating, you are expected to:

- Be respectful and inclusive
- Focus on constructive criticism
- Accept responsibility for mistakes
- Prioritize what's best for the community

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- XAI API key (for testing with real API)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ai-dialogue.git
   cd ai-dialogue
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/manutej/ai-dialogue.git
   ```

---

## Development Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### 3. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# Note: Tests should use mocks, but integration tests may need real keys
```

### 4. Verify Setup

```bash
# Run tests to verify everything works
pytest tests/

# Check code style
black --check src/ tests/
ruff check src/ tests/
```

---

## Making Changes

### Branch Naming Convention

Create a descriptive branch name:

```bash
# For features
git checkout -b feature/add-streaming-support

# For bug fixes
git checkout -b fix/handle-timeout-errors

# For documentation
git checkout -b docs/improve-api-reference

# For tests
git checkout -b test/add-integration-tests
```

### Commit Message Guidelines

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build/tooling changes

**Examples:**
```
feat(grok): Add support for streaming responses

- Implement chat_stream() method
- Add streaming example in docs
- Include tests for stream handling

Closes #42
```

```
fix(protocol): Handle timeout errors gracefully

Added retry logic with exponential backoff for transient failures.

Fixes #38
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_adapters.py

# Run specific test
pytest tests/test_adapters.py::test_grok_adapter_chat
```

### Writing Tests

**Test Structure:**
```python
import pytest
from src.clients.grok import GrokClient

@pytest.mark.asyncio
async def test_grok_client_basic_query():
    """Test basic query functionality"""
    client = GrokClient()

    # Use mocks for API calls
    with pytest.mock.patch.object(client, 'chat') as mock_chat:
        mock_chat.return_value = ("Response", {"total": 100})

        response, tokens = await client.chat("Test query")

        assert response == "Response"
        assert tokens["total"] == 100

    await client.close()
```

**Test Guidelines:**
- Write unit tests for all new functions/methods
- Use mocks for external API calls (don't waste money on tests!)
- Test edge cases and error conditions
- Keep tests fast and independent
- Add integration tests for critical paths (sparingly)

### Cost-Conscious Testing

❌ **Don't:**
```python
# This costs real money!
async def test_real_api_call():
    client = GrokClient()
    response, tokens = await client.chat("Test")  # Real API call
```

✅ **Do:**
```python
# Free and fast!
async def test_mocked_api_call():
    client = GrokClient()
    with pytest.mock.patch.object(client, 'chat', return_value=("Test", {"total": 10})):
        response, tokens = await client.chat("Test")
```

---

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Formatting**: Use Black for automatic formatting
- **Linting**: Use Ruff for fast linting
- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings

### Formatting Code

```bash
# Format all code
black src/ tests/

# Check formatting without making changes
black --check src/ tests/

# Run linter
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/
```

### Example Code Style

```python
from typing import Dict, Optional, Tuple


async def chat(
    self,
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> Tuple[str, Dict[str, int]]:
    """
    Send chat request to Grok API.

    Args:
        prompt: User prompt to send
        model: Model to use (defaults to instance default)
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Tuple of (response_text, token_usage_dict)

    Raises:
        ValueError: If parameters are invalid
        APIError: If API request fails

    Example:
        >>> client = GrokClient()
        >>> response, tokens = await client.chat("What is 2+2?")
        >>> print(response)
        "4"
    """
    # Implementation...
```

---

## Submitting Changes

### Pull Request Process

1. **Update your branch:**
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **Run tests and linting:**
   ```bash
   pytest tests/
   black src/ tests/
   ruff check src/ tests/
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request:**
   - Go to GitHub and create a PR from your fork
   - Fill in the PR template (if provided)
   - Link any related issues

### PR Guidelines

**Title:**
```
feat: Add streaming support for Grok API
```

**Description Template:**
```markdown
## Summary
Brief description of changes

## Changes Made
- Bullet point list of changes
- Include file paths where relevant

## Testing
- How was this tested?
- Any new test cases added?

## Cost Impact
- Does this change API costs?
- Any performance implications?

## Checklist
- [ ] Tests pass locally
- [ ] Code formatted with Black
- [ ] Linting passes with Ruff
- [ ] Documentation updated (if needed)
- [ ] Changelog updated (if significant)

Closes #issue-number
```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge

---

## Reporting Bugs

### Before Submitting

1. Check if the bug has already been reported
2. Test with the latest version
3. Verify it's not a configuration issue

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what happened

**To Reproduce**
Steps to reproduce:
1. Step 1
2. Step 2
3. See error

**Expected behavior**
What should have happened

**Environment:**
- OS: [e.g., macOS 13.5]
- Python version: [e.g., 3.11.4]
- Package version: [e.g., 1.0.0]

**Additional context**
Any other relevant information

**Code snippet:**
```python
# Minimal code that reproduces the issue
```
```

---

## Suggesting Enhancements

### Enhancement Template

```markdown
**Feature Description**
Clear description of the enhancement

**Use Case**
Why is this needed? What problem does it solve?

**Proposed Solution**
How you envision it working

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Examples, mockups, references
```

---

## Development Tips

### Useful Commands

```bash
# Run quick syntax check
python -m py_compile src/**/*.py

# Check imports
python -c "from src.clients.grok import GrokClient; print('OK')"

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Find code that needs docstrings
ruff check src/ | grep "Missing docstring"
```

### Debugging

```python
# Use logging for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use debugger
import pdb; pdb.set_trace()
```

### Working with Async Code

```python
# Test async functions
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

---

## Getting Help

- **Questions?** Open a [GitHub Discussion](https://github.com/manutej/ai-dialogue/discussions)
- **Bugs?** Open an [Issue](https://github.com/manutej/ai-dialogue/issues)
- **Chat?** (Add Discord/Slack link if you create one)

---

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributors page

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to AI Dialogue!** 🎉

Every contribution, no matter how small, helps make this project better for everyone.
