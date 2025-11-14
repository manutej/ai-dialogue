# Grok Commands - Test Suite

**Version**: 1.0.0
**Test Coverage**: 40 comprehensive tests
**Estimated Time**: 1-20 minutes (depending on mode)

---

## Overview

Comprehensive test suite for `/grok` slash commands with automated execution and formatted result documentation.

**What's Tested**:
- ✅ All 3 commands (`/grok`, `/grok-list`, `/grok-export`)
- ✅ All 14 flags
- ✅ All 6 orchestration modes
- ✅ Error handling and edge cases
- ✅ Path detection (5 levels)
- ✅ API integration
- ✅ Session management

---

## Quick Start

### 1. Prerequisites

```bash
# Ensure commands are installed
ls -lh .claude/commands/grok*.md

# If not installed:
./utils/grok-commands/install.sh

# Set API key
export XAI_API_KEY='your-key-here'

# Restart Claude Code (important!)
```

### 2. Run Tests

**Quick Test** (5 critical tests, ~1 minute):
```bash
./tests/grok-commands/scripts/run-quick-tests.sh
```

**Full Test Suite** (40 tests, ~15 minutes):
```bash
# Quick mode (10 tests, ~2 minutes)
./tests/grok-commands/scripts/test-grok-commands.sh --quick

# Full mode (40 tests, ~15 minutes)
./tests/grok-commands/scripts/test-grok-commands.sh --full
```

### 3. Review Results

```bash
# Results are saved with timestamps
ls -lh tests/grok-commands/results/

# View latest results
cat tests/grok-commands/results/*/test-results.md

# View detailed logs
cat tests/grok-commands/results/*/test-execution.log
```

---

## Directory Structure

```
tests/grok-commands/
├── README.md                       # This file
├── scripts/                        # Test execution scripts
│   ├── run-quick-tests.sh          # Quick 5-test runner (1 min)
│   └── test-grok-commands.sh       # Full 40-test suite (15 min)
├── docs/                           # Test documentation
│   ├── TESTING-SUMMARY.md          # Quick reference
│   ├── GROK-TESTING-GUIDE.md       # Manual testing guide
│   └── GROK-COMMANDS-TEST-PLAN.md  # Comprehensive test plan
└── results/                        # Test results (auto-generated)
    └── YYYYMMDD-HHMMSS/
        ├── test-results.md         # Formatted results
        ├── test-execution.log      # Detailed logs
        └── test-XX.txt             # Individual test outputs
```

---

## Test Suites

### Suite A: Path Detection (4 tests)
- Environment variable detection
- Auto-detection from current directory
- Settings file configuration
- Fallback to common locations

### Suite B: Information Flags (4 tests)
- `--help` output
- `--list-models` functionality
- `--list-modes` functionality
- `--test` adapter verification

### Suite C: Quick Mode (3 tests)
- Basic quick query
- Custom model selection
- Output to file

### Suite D: Orchestration Modes (6 tests)
- Loop mode (knowledge building)
- Debate mode (adversarial)
- Podcast mode (conversational)
- Pipeline mode (static workflow)
- Dynamic mode (adaptive)
- Research-enhanced mode (deep research)

### Suite E: Advanced Flags (6 tests)
- Custom temperature
- Custom max tokens
- Custom turn count
- Verbose output
- Multiple flags combined

### Suite F: Session Listing (2 tests)
- `/grok-list` basic functionality
- Session metadata validation

### Suite G: Session Export (5 tests)
- Export to markdown (default)
- Export to JSON
- Export to text
- Export to file
- Export with custom formatting

### Suite H: Error Handling (5 tests)
- Invalid mode
- Invalid model
- Missing query
- API errors
- Path detection failures

**Total**: 40 tests across 8 suites

---

## Test Output Format

### Console Output
```
═══════════════════════════════════════════════════════
TEST SUITE A: Path Detection
═══════════════════════════════════════════════════════

[12:34:56] Running Test A1: Environment Variable Path Detection
[12:34:56] Command: /grok --help | head -5
✓ Test A1 passed

[12:34:57] Running Test A2: Auto-Detection from Current Directory
[12:34:57] Command: cd ~/Documents/LUXOR/PROJECTS/ai-dialogue && /grok --help
✓ Test A2 passed

...

═══════════════════════════════════════════════════════
TEST SUMMARY
═══════════════════════════════════════════════════════

[12:45:23] Tests Run:    40
✓ Passed:       40
Failed:       0

Success Rate: 100.0%

Results saved to: tests/grok-commands/results/20251113-123456/test-results.md
```

### Markdown Results File

```markdown
# /grok Commands - Test Execution Results

**Date**: 2025-11-13
**Time**: 12:34:56

---

## Test Results

### Test A1: Environment Variable Path Detection

**Command**:
```bash
/grok --help | head -5
```

**Output**:
```
/grok - Multi-model orchestration for complex queries

Usage:
  /grok [FLAGS] <query>
```

**Status**: ✓ PASSED

---

[... more test results ...]

## Summary

| Metric | Count |
|--------|-------|
| Tests Run | 40 |
| Tests Passed | 40 |
| Tests Failed | 0 |
| Success Rate | 100.0% |
```

---

## Usage Examples

### Quick Verification

Just want to verify commands work?

```bash
./tests/grok-commands/scripts/run-quick-tests.sh
```

**Output**:
```
🧪 /grok Commands - Quick Test Runner
=======================================

Pre-flight checks:
-----------------
✓ XAI_API_KEY is set
✓ Commands installed

Running tests:
--------------
Testing: Help Command... ✓ PASS
Testing: List Models... ✓ PASS
Testing: List Modes... ✓ PASS
Testing: Quick Mode (API call)... ✓ PASS
Testing: List Sessions... ✓ PASS

Summary:
--------
Passed: 5/5
Failed: 0/5

✓ All tests passed! Your /grok commands are working correctly.
```

---

### Comprehensive Testing

Before deploying or after major changes:

```bash
./tests/grok-commands/scripts/test-grok-commands.sh --full
```

**Output**: Detailed test results saved to `results/` directory

---

### Manual Testing

For learning or troubleshooting specific features:

```bash
# Follow step-by-step guide
cat tests/grok-commands/docs/GROK-TESTING-GUIDE.md

# Execute tests manually
# Document specific use cases
# Understand each feature in depth
```

---

## Interpreting Results

### All Tests Pass ✓

```
Success Rate: 100.0%
```

**Meaning**: All features working correctly
**Action**: Ready for production use

### Some Tests Fail ✗

```
Success Rate: 85.0% (34/40 passed)
```

**Meaning**: Issues detected
**Action**:
1. Check which tests failed
2. Review error messages in logs
3. Consult troubleshooting guide
4. Verify prerequisites (API key, paths, etc.)

---

## Troubleshooting

### Tests Show "Command Not Found"

**Problem**: `/grok` shows "command not found" during tests

**Solution**:
```bash
# Verify installation
ls -lh .claude/commands/grok*.md

# Reinstall if needed
./utils/grok-commands/install.sh

# IMPORTANT: Restart Claude Code completely
# (Commands are cached)
```

---

### API Tests Fail

**Problem**: Quick mode test fails with API errors

**Solution**:
```bash
# Verify API key
echo $XAI_API_KEY

# Test API connectivity
curl https://api.x.ai/v1/models \
  -H "Authorization: Bearer $XAI_API_KEY"

# Check API credits/quota
```

---

### Path Detection Tests Fail

**Problem**: "Could not locate ai-dialogue project"

**Solution**:
```bash
# Run tests from project directory
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
./tests/grok-commands/scripts/run-quick-tests.sh

# Or set environment variable
export GROK_PROJECT_PATH="$(pwd)"
```

---

### Python Import Errors

**Problem**: Tests fail with "ModuleNotFoundError"

**Solution**:
```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Verify
python -c "from src.clients.grok import GrokClient; print('OK')"
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Grok Commands

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -e .

      - name: Install Grok commands
        run: ./utils/grok-commands/install.sh --project

      - name: Run quick tests
        env:
          XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
          GROK_PROJECT_PATH: ${{ github.workspace }}
        run: ./tests/grok-commands/scripts/run-quick-tests.sh
```

---

## Contributing

When adding new tests:

1. **Update test scripts** in `scripts/`
2. **Add test cases** to test plan in `docs/GROK-COMMANDS-TEST-PLAN.md`
3. **Document expected behavior** in test guide
4. **Run full test suite** to verify
5. **Update this README** with new test coverage

### Test Naming Convention

```
Suite[A-H][1-9]: Test Name

Examples:
- A1: Environment Variable Path Detection
- B3: List Modes Flag
- D2: Debate Mode Orchestration
```

---

## Performance

**Quick Tests** (5 tests):
- Time: ~1 minute
- API Calls: 1
- Cost: ~$0.01

**Quick Mode** (10 tests):
- Time: ~2 minutes
- API Calls: 3-5
- Cost: ~$0.05

**Full Mode** (40 tests):
- Time: ~15 minutes
- API Calls: 15-20
- Cost: ~$0.50

*Costs estimated based on typical API pricing*

---

## Test Data

Tests generate the following artifacts:

```
tests/grok-commands/results/
└── YYYYMMDD-HHMMSS/
    ├── test-results.md           # Human-readable results
    ├── test-execution.log        # Detailed execution log
    ├── test-01.txt               # Test A1 output
    ├── test-02.txt               # Test A2 output
    └── ...                       # Individual test outputs
```

**Retention**: Keep latest 10 test runs, archive older results

---

## Documentation

- **Testing Summary**: `docs/TESTING-SUMMARY.md` - Quick reference
- **Testing Guide**: `docs/GROK-TESTING-GUIDE.md` - Manual testing
- **Test Plan**: `docs/GROK-COMMANDS-TEST-PLAN.md` - All 40 tests detailed
- **Command Docs**: `../utils/grok-commands/README.md` - Installation and usage

---

## Support

**Issues**: Report test failures with:
- Test ID (e.g., "Test A1 failed")
- Full error output
- Environment details (OS, Python version, Claude Code version)
- Test logs from `results/` directory

**Questions**: See documentation in `docs/` or command README

---

**Comprehensive testing for production-ready commands!** ✅
