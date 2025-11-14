# /grok Commands - Testing Summary & Instructions

**Created**: 2025-11-13
**Status**: Ready for Execution
**Purpose**: Quick reference for testing all /grok command functionality

---

## Quick Start (1 Minute)

The fastest way to verify everything works:

```bash
# 1. Restart Claude Code (important!)
#    Close and reopen completely, or start new conversation

# 2. Navigate to project
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue

# 3. Run quick tests
./run-quick-tests.sh
```

**That's it!** This runs 5 critical tests in ~1 minute.

---

## Testing Options

### Option 1: Quick Tests (Recommended First)

**What**: 5 critical tests to verify basic functionality
**Time**: 1-2 minutes
**Command**:
```bash
./run-quick-tests.sh
```

**Tests**:
1. ✓ Help command loads
2. ✓ Models list works
3. ✓ Modes list works
4. ✓ Quick mode API call succeeds
5. ✓ Session listing works

---

### Option 2: Automated Full Test Suite

**What**: 40 comprehensive tests covering all features
**Time**: 15-20 minutes
**Command**:
```bash
# Quick mode (10 tests, ~2 minutes)
./test-grok-commands.sh --quick

# Full mode (40 tests, ~15 minutes)
./test-grok-commands.sh --full
```

**Outputs**:
- `test-outputs/YYYYMMDD-HHMMSS/test-results.md` - Formatted results
- `test-outputs/YYYYMMDD-HHMMSS/test-execution.log` - Detailed log
- `test-outputs/YYYYMMDD-HHMMSS/test-XX.txt` - Individual test outputs

---

### Option 3: Manual Testing

**What**: Step-by-step guided testing with documentation
**Time**: 20-30 minutes
**Guide**: See `docs/GROK-TESTING-GUIDE.md`

**Best for**:
- Understanding each feature in depth
- Documenting specific use cases
- Troubleshooting specific issues
- Learning the tool

---

## Prerequisites

### Before Running Any Tests

1. **Restart Claude Code**
   - ⚠️ CRITICAL: Commands are cached!
   - Close and reopen Claude Code completely
   - OR start a new conversation

2. **Set API Key**
   ```bash
   export XAI_API_KEY='your-key-here'

   # Verify
   echo $XAI_API_KEY
   ```

3. **Optional: Set Project Path**
   ```bash
   # Usually auto-detected, but can set explicitly:
   export GROK_PROJECT_PATH="$HOME/Documents/LUXOR/PROJECTS/ai-dialogue"
   ```

4. **Navigate to Project**
   ```bash
   cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
   ```

---

## Expected Results

### If Everything Works ✓

You should see:

**Quick Tests**:
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

**Full Tests**:
```
═══════════════════════════════════════════════════════
TEST SUMMARY
═══════════════════════════════════════════════════════

Tests Run:    40
✓ Passed:     40
Failed:       0

Success Rate: 100.0%

Results saved to: test-outputs/.../test-results.md
```

---

## Troubleshooting

### Issue: Commands Show Old Behavior

**Symptom**: `/grok --help` shows old simple wrapper, not orchestration

**Solution**:
```bash
# Verify command file is updated
cat ~/.claude/commands/grok.md | head -20

# Should show:
# "Multi-model orchestration for complex queries"

# If correct but still shows old version:
# 1. Completely restart Claude Code (not just new chat)
# 2. Wait 5 minutes for cache to clear
# 3. Try new conversation
```

---

### Issue: API Key Error

**Symptom**: "API key not found" or authentication errors

**Solution**:
```bash
# Check if set
echo $XAI_API_KEY

# Set it
export XAI_API_KEY='xai-...'

# Make permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export XAI_API_KEY="xai-..."' >> ~/.zshrc
source ~/.zshrc
```

---

### Issue: Project Not Found

**Symptom**: "Could not locate ai-dialogue project"

**Solution**:
```bash
# Option 1: Set environment variable
export GROK_PROJECT_PATH="$HOME/Documents/LUXOR/PROJECTS/ai-dialogue"

# Option 2: Run from project directory
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue

# Option 3: Add to settings.json
# Edit ~/.claude/settings.json:
{
  "grok": {
    "project_path": "/Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue"
  }
}
```

---

### Issue: Python/Dependency Errors

**Symptom**: "ModuleNotFoundError" or import errors

**Solution**:
```bash
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue

# Activate venv
source venv/bin/activate

# Verify dependencies
pip list | grep -E "(click|anthropic|openai)"

# Reinstall if needed
pip install -e .
```

---

## Test Coverage

### What Gets Tested

**Commands** (3):
- ✓ `/grok` - Main orchestration command
- ✓ `/grok-list` - Session listing
- ✓ `/grok-export` - Session export

**Flags** (14):
- ✓ `--help` - Help documentation
- ✓ `--quick` - Fast single-turn queries
- ✓ `--mode` - Orchestration mode selection
- ✓ `--turns` - Custom turn count
- ✓ `--model` - Model selection
- ✓ `--temperature` - Sampling parameter
- ✓ `--max-tokens` - Token limit
- ✓ `--output` - File output
- ✓ `--verbose` - Detailed logging
- ✓ `--test` - Adapter testing
- ✓ `--list-models` - Available models
- ✓ `--list-modes` - Available modes
- ✓ `--format` - Export format (grok-export)

**Modes** (6):
- ✓ loop - Sequential knowledge building
- ✓ debate - Adversarial exploration
- ✓ podcast - Conversational dialogue
- ✓ pipeline - Static workflow
- ✓ dynamic - Adaptive decomposition
- ✓ research-enhanced - Deep research

**Error Handling**:
- ✓ Invalid mode
- ✓ Invalid model
- ✓ Missing query
- ✓ API errors
- ✓ Path detection failures

---

## After Testing

### If Tests Pass ✓

1. **Archive Results**
   ```bash
   cp test-outputs/latest/test-results.md docs/FINAL-TEST-RESULTS.md
   ```

2. **Update Validation Report**
   ```bash
   # Edit docs/GROK-COMMANDS-VALIDATION-REPORT.md
   # Change status to "Runtime Testing Complete ✅"
   ```

3. **Ready for Production**
   - All features validated
   - Error handling confirmed
   - API connectivity verified
   - Session management working

---

### If Tests Fail ✗

1. **Document Failures**
   - Note which tests failed
   - Copy full error messages
   - Check environment details

2. **Check Troubleshooting**
   - Review issues above
   - Verify prerequisites
   - Check logs in `test-outputs/`

3. **Report Issues**
   Include:
   - Test ID that failed
   - Full error output
   - Environment (OS, Python version)
   - XAI API status

---

## Test Files Reference

```
ai-dialogue/
├── run-quick-tests.sh              # Quick 5-test runner (1 min)
├── test-grok-commands.sh           # Full 40-test suite (15 min)
├── test-outputs/                   # Test results (auto-created)
│   └── YYYYMMDD-HHMMSS/
│       ├── test-results.md         # Formatted results
│       ├── test-execution.log      # Detailed log
│       └── test-XX.txt             # Individual outputs
└── docs/
    ├── TESTING-SUMMARY.md          # This file
    ├── GROK-TESTING-GUIDE.md       # Manual testing guide
    ├── GROK-COMMANDS-TEST-PLAN.md  # Comprehensive test plan
    └── GROK-COMMANDS-VALIDATION-REPORT.md  # Static validation
```

---

## Recommended Testing Workflow

### First Time Testing

```bash
# 1. Restart Claude Code
#    (Close completely and reopen)

# 2. Setup
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
export XAI_API_KEY='your-key-here'

# 3. Quick verification
./run-quick-tests.sh

# 4. If passed, run full suite
./test-grok-commands.sh --full

# 5. Review results
cat test-outputs/*/test-results.md
```

**Total Time**: ~20 minutes
**Confidence**: Production-ready

---

### Quick Verification (Periodic)

```bash
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
./run-quick-tests.sh
```

**Total Time**: 1 minute
**Use Case**: Verify after updates

---

### Deep Testing (Before Major Use)

```bash
# Follow manual guide
open docs/GROK-TESTING-GUIDE.md

# Run each test manually
# Document edge cases
# Verify specific use cases
```

**Total Time**: 30 minutes
**Use Case**: Learning, troubleshooting, documentation

---

## Success Criteria

Tests are considered successful if:

- ✅ All quick tests pass (5/5)
- ✅ API connectivity verified
- ✅ Sessions are saved correctly
- ✅ Error handling works as expected
- ✅ No Python/dependency errors
- ✅ Output formatting is correct

**Minimum**: Quick tests must pass
**Recommended**: Full automated tests pass
**Ideal**: Manual testing completed with documentation

---

## Next Steps After Successful Testing

1. **Production Use**
   - Start using `/grok` for real queries
   - Try different orchestration modes
   - Explore advanced flags

2. **Documentation**
   - Refer to `GROK-COMMANDS-QUICK-REFERENCE.md`
   - Check examples in test results
   - Review orchestration mode details

3. **Optimization**
   - Find your most-used patterns
   - Create aliases for common queries
   - Adjust default settings if needed

4. **Feedback**
   - Note any issues or suggestions
   - Document useful patterns
   - Share findings

---

## Quick Command Reference

```bash
# Information
/grok --help
/grok --list-models
/grok --list-modes

# Quick queries (95% use case)
/grok --quick "your question"
/grok --quick --model grok-beta "question"
/grok --quick --output results.txt "question"

# Orchestration modes
/grok --mode loop "complex topic"
/grok --mode debate "controversial question"
/grok --mode podcast "interesting subject"

# Session management
/grok-list
/grok-export SESSION_ID
/grok-export --format json SESSION_ID

# Testing
./run-quick-tests.sh
./test-grok-commands.sh --quick
./test-grok-commands.sh --full
```

---

## Support

**Documentation**:
- Testing Guide: `docs/GROK-TESTING-GUIDE.md`
- Quick Reference: `docs/GROK-COMMANDS-QUICK-REFERENCE.md`
- Test Plan: `docs/GROK-COMMANDS-TEST-PLAN.md`
- Validation: `docs/GROK-COMMANDS-VALIDATION-REPORT.md`

**Files**:
- Commands: `~/.claude/commands/grok*.md`
- Project: `~/Documents/LUXOR/PROJECTS/ai-dialogue`
- Sessions: `~/Documents/LUXOR/PROJECTS/ai-dialogue/.grok/sessions/`

---

**Good luck with testing!** 🚀

The testing infrastructure is comprehensive and production-ready.
All you need to do is restart Claude Code and run the tests.
