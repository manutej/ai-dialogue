# /grok Commands - Step-by-Step Testing Guide

**Created**: 2025-11-13
**Purpose**: Execute and document testing of all /grok commands and flags
**Estimated Time**: 15-20 minutes (quick mode: 5 minutes)

---

## Overview

This guide provides a systematic approach to testing all /grok commands with documented results.

**Two Testing Methods**:
1. **Automated** - Run script to execute all tests automatically
2. **Manual** - Follow step-by-step instructions below

---

## Method 1: Automated Testing (Recommended)

### Prerequisites

```bash
# 1. Restart Claude Code to reload commands
# (Or start a new conversation)

# 2. Verify API key
echo $XAI_API_KEY
# Should show your API key

# 3. Navigate to project
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
```

### Run Tests

```bash
# Make script executable (first time only)
chmod +x test-grok-commands.sh

# Quick test (10 critical tests, ~2 minutes)
./test-grok-commands.sh --quick

# Full test (40 tests, ~15 minutes)
./test-grok-commands.sh --full
```

### Review Results

```bash
# Results are saved in test-outputs/YYYYMMDD-HHMMSS/
ls -lh test-outputs/

# View latest results
cat test-outputs/*/test-results.md

# View detailed logs
cat test-outputs/*/test-execution.log
```

**That's it!** The script will:
- ✅ Run all tests systematically
- ✅ Capture formatted output
- ✅ Generate comprehensive results document
- ✅ Show success/failure summary

---

## Method 2: Manual Testing (Step-by-Step)

### Phase 1: Environment Preparation

**Step 1.1** - Restart Claude Code
```
Close and reopen Claude Code completely
OR
Start a new conversation
```

**Step 1.2** - Verify Commands Loaded
```bash
# In Claude Code, run:
/grok --help

# Expected output should include:
# "Multi-model orchestration for complex queries"
# NOT the old simple XAI wrapper
```

**Step 1.3** - Set Environment
```bash
# Check API key
echo $XAI_API_KEY

# If not set:
export XAI_API_KEY='your-key-here'

# Set project path (optional, auto-detection usually works)
export GROK_PROJECT_PATH="$HOME/Documents/LUXOR/PROJECTS/ai-dialogue"
```

**Step 1.4** - Create Test Directory
```bash
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
mkdir -p test-outputs
cd test-outputs
```

---

### Phase 2: Critical Tests (Must Pass)

#### Test 1: Help Command

**Command**:
```bash
/grok --help
```

**Expected Output**:
```
/grok - Multi-model orchestration for complex queries

Usage:
  /grok [FLAGS] <query>
  /grok --mode <mode> [FLAGS] <query>

Quick Mode (95% of users):
  /grok --quick "your question"  # Single-turn, fast response

[... more help text ...]
```

**Document**: Copy output to test results

**Status**: [ ] PASS [ ] FAIL

---

#### Test 2: List Available Models

**Command**:
```bash
/grok --list-models
```

**Expected Output**:
```
Available Grok Models:

- grok-beta (default)
- grok-vision-beta
[... etc ...]
```

**Document**: Copy output to test results

**Status**: [ ] PASS [ ] FAIL

---

#### Test 3: List Orchestration Modes

**Command**:
```bash
/grok --list-modes
```

**Expected Output**:
```
Available Orchestration Modes:

loop (default)
  Sequential knowledge building through iterative queries
  [... details ...]

debate
  Adversarial exploration with thesis/antithesis
  [... details ...]

[... more modes ...]
```

**Document**: Copy output to test results

**Status**: [ ] PASS [ ] FAIL

---

#### Test 4: Quick Mode - Simple Query

**Command**:
```bash
/grok --quick "What is 2+2?"
```

**Expected Output**:
```
[Should show Grok's response: "4" or explanation]
```

**Document**: Copy full output

**Status**: [ ] PASS [ ] FAIL

**Notes**:
- This makes an actual API call
- Should complete in ~2-5 seconds
- Verifies end-to-end functionality

---

#### Test 5: Quick Mode with Custom Model

**Command**:
```bash
/grok --quick --model grok-beta "Explain recursion in one sentence"
```

**Expected Output**:
```
[Grok's explanation of recursion]
```

**Document**: Copy output

**Status**: [ ] PASS [ ] FAIL

---

#### Test 6: Quick Mode with Output File

**Command**:
```bash
/grok --quick --output test-output-1.txt "List 3 programming languages"
```

**Expected Output**:
```
[Response about programming languages]
Saved to: test-output-1.txt
```

**Verify**:
```bash
cat test-output-1.txt
# Should contain the dialogue session
```

**Document**: Copy both console output and file contents

**Status**: [ ] PASS [ ] FAIL

---

#### Test 7: Loop Mode (2 turns)

**Command**:
```bash
/grok --mode loop --turns 2 "Explain quantum computing"
```

**Expected Output**:
```
Turn 1/2: [Grok's initial explanation]
Turn 2/2: [Grok builds on previous turn]

Final synthesis:
[Combined understanding]
```

**Document**: Copy full output (may be long)

**Status**: [ ] PASS [ ] FAIL

**Notes**:
- Makes multiple API calls (2 in this case)
- Should show progression of understanding
- May take 10-20 seconds

---

#### Test 8: List Sessions

**Command**:
```bash
/grok-list
```

**Expected Output**:
```
Grok Dialogue Sessions:

Session ID: 20251113-123456
  Created: 2025-11-13 12:34:56
  Turns: 2
  Mode: loop
  Query: Explain quantum computing

[... more sessions if any ...]

Total sessions: X
```

**Document**: Copy output

**Status**: [ ] PASS [ ] FAIL

---

#### Test 9: Error Handling - Invalid Mode

**Command**:
```bash
/grok --mode invalid-mode "test"
```

**Expected Output**:
```
Error: Invalid mode 'invalid-mode'

Available modes: loop, debate, podcast, pipeline, dynamic, research-enhanced

Use /grok --list-modes for details
```

**Document**: Copy error message

**Status**: [ ] PASS [ ] FAIL

---

#### Test 10: Error Handling - Invalid Model

**Command**:
```bash
/grok --quick --model invalid-model "test"
```

**Expected Output**:
```
Error: Invalid model 'invalid-model'

Available models:
  - grok-beta
  - grok-vision-beta
  [... etc ...]

Use /grok --list-models for full list
```

**Document**: Copy error message

**Status**: [ ] PASS [ ] FAIL

---

### Phase 3: Extended Tests (Optional - If Time Permits)

#### Test 11: Debate Mode

**Command**:
```bash
/grok --mode debate --turns 2 "Is AI beneficial or harmful?"
```

**Expected**: Thesis/antithesis dialogue

**Status**: [ ] PASS [ ] FAIL

---

#### Test 12: Podcast Mode

**Command**:
```bash
/grok --mode podcast --turns 2 "Future of space exploration"
```

**Expected**: Conversational dialogue format

**Status**: [ ] PASS [ ] FAIL

---

#### Test 13: Pipeline Mode

**Command**:
```bash
/grok --mode pipeline "Analyze: The quick brown fox"
```

**Expected**: Static workflow execution

**Status**: [ ] PASS [ ] FAIL

---

#### Test 14: Custom Temperature

**Command**:
```bash
/grok --quick --temperature 0.1 "Say the word 'test'"
```

**Expected**: Very deterministic output

**Status**: [ ] PASS [ ] FAIL

---

#### Test 15: Verbose Output

**Command**:
```bash
/grok --quick --verbose "What is AI?"
```

**Expected**: Detailed execution info + response

**Status**: [ ] PASS [ ] FAIL

---

#### Test 16: Export Session (Markdown)

**Command**:
```bash
# First, get a session ID from /grok-list
SESSION_ID="20251113-123456"  # Replace with actual ID

/grok-export $SESSION_ID
```

**Expected**: Formatted markdown output

**Status**: [ ] PASS [ ] FAIL

---

#### Test 17: Export Session (JSON)

**Command**:
```bash
/grok-export --format json $SESSION_ID
```

**Expected**: Valid JSON output

**Status**: [ ] PASS [ ] FAIL

---

#### Test 18: Export to File

**Command**:
```bash
/grok-export --output exported-session.md $SESSION_ID
```

**Expected**: File created with session contents

**Verify**:
```bash
cat exported-session.md
```

**Status**: [ ] PASS [ ] FAIL

---

### Phase 4: Document Results

#### Create Results Summary

Create a file `test-results-manual.md` with the following format:

```markdown
# /grok Commands - Manual Test Results

**Date**: 2025-11-13
**Tester**: [Your name]
**Environment**: [Claude Code version, OS]

---

## Test Results Summary

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1 | Help Command | ✓ PASS | Showed new orchestration help |
| 2 | List Models | ✓ PASS | 6 models listed |
| 3 | List Modes | ✓ PASS | 6 modes listed |
| 4 | Quick Mode | ✓ PASS | Got "4" as expected |
| 5 | Custom Model | ✓ PASS | Recursion explained |
| ... | ... | ... | ... |

**Total Tests**: 18
**Passed**: X
**Failed**: Y
**Success Rate**: Z%

---

## Detailed Results

### Test 1: Help Command

**Command**:
```
/grok --help
```

**Output**:
```
[Paste full output here]
```

**Status**: ✓ PASS

**Notes**: Output matches expected format. New orchestration system loaded correctly.

---

[Continue for each test...]
```

---

## Troubleshooting

### Commands Show Old Behavior

**Problem**: `/grok --help` shows old simple XAI wrapper, not new orchestration

**Solution**:
1. Completely restart Claude Code (not just new conversation)
2. Or wait for cache to clear naturally (~5 minutes)
3. Verify file updated: `cat ~/.claude/commands/grok.md | head -20`

---

### Path Detection Fails

**Problem**: "Project not found" error

**Solution**:
```bash
# Option 1: Set environment variable
export GROK_PROJECT_PATH="$HOME/Documents/LUXOR/PROJECTS/ai-dialogue"

# Option 2: Add to settings.json
# Edit ~/.claude/settings.json:
{
  "grok": {
    "project_path": "/Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue"
  }
}

# Option 3: Run from project directory
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
```

---

### API Errors

**Problem**: "API key not found" or authentication errors

**Solution**:
```bash
# Verify key is set
echo $XAI_API_KEY

# Set if needed
export XAI_API_KEY='your-key-here'

# Test with simple curl
curl https://api.x.ai/v1/models \
  -H "Authorization: Bearer $XAI_API_KEY"
```

---

### Python Import Errors

**Problem**: "ModuleNotFoundError: No module named 'click'" or similar

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

## Quick Reference

### Minimum Viable Test (1 minute)

Just want to verify it works? Run these 3 commands:

```bash
# 1. Check commands loaded
/grok --help | head -5

# 2. Test API connectivity
/grok --quick "What is 2+2?"

# 3. Verify session saved
/grok-list
```

If all three work, you're good!

---

### Test Data Locations

```bash
# Test outputs
~/Documents/LUXOR/PROJECTS/ai-dialogue/test-outputs/

# Session storage
~/Documents/LUXOR/PROJECTS/ai-dialogue/.grok/sessions/

# Command definitions
~/.claude/commands/grok*.md
```

---

## Next Steps After Testing

### If All Tests Pass ✓

1. **Document success** in validation report
2. **Archive test results** for reference
3. **Start using in production** with confidence
4. **Share feedback** if you find the tool useful

### If Some Tests Fail ✗

1. **Document failures** with exact error messages
2. **Check troubleshooting** section above
3. **Review logs** in test-outputs/
4. **Report issues** with:
   - Test ID that failed
   - Full error output
   - Environment details (OS, Python version, etc.)

---

## Test Results Template

Use this template to document your results:

```markdown
# /grok Commands - Test Results

**Date**: [YYYY-MM-DD]
**Time**: [HH:MM]
**Tester**: [Name]
**Test Type**: [Automated | Manual]

---

## Environment

- **OS**: macOS 14.1 (or your OS)
- **Claude Code**: [version]
- **Python**: 3.11.x
- **XAI API**: Connected ✓

---

## Test Summary

| Metric | Value |
|--------|-------|
| Total Tests | X |
| Passed | Y |
| Failed | Z |
| Success Rate | W% |

---

## Critical Tests (Must Pass)

- [ ] Help command shows orchestration options
- [ ] Models list displays correctly
- [ ] Modes list displays correctly
- [ ] Quick mode executes successfully
- [ ] API connectivity verified
- [ ] Sessions are saved and listable
- [ ] Error handling works correctly

---

## Detailed Results

[Copy full output from automated script or manual testing]

---

## Issues Found

[List any problems encountered]

---

## Recommendations

[Suggestions for improvements]

---

**Overall Assessment**: [READY FOR PRODUCTION | NEEDS FIXES | BLOCKED]
```

---

## Conclusion

After completing testing, you should have:

1. ✅ Verified all commands load correctly
2. ✅ Tested critical functionality (quick mode, orchestration)
3. ✅ Validated error handling
4. ✅ Documented results with formatted output
5. ✅ Confirmed API connectivity and session management

**Time Investment**: 5-20 minutes
**Value**: Confidence in production-ready tool
**Documentation**: Comprehensive test results for future reference

---

**Happy Testing!** 🚀
