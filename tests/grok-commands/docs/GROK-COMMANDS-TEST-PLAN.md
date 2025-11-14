# /grok Commands - Comprehensive Test Plan

**Created**: 2025-11-13
**Status**: Ready for Execution
**Purpose**: Validate all /grok commands, flags, and features with documented results

---

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Pre-Test Checklist](#pre-test-checklist)
3. [Test Suite A: Path Detection](#test-suite-a-path-detection)
4. [Test Suite B: /grok Command - Information Flags](#test-suite-b-grok-command---information-flags)
5. [Test Suite C: /grok Command - Quick Mode](#test-suite-c-grok-command---quick-mode)
6. [Test Suite D: /grok Command - Orchestration Modes](#test-suite-d-grok-command---orchestration-modes)
7. [Test Suite E: /grok Command - Advanced Flags](#test-suite-e-grok-command---advanced-flags)
8. [Test Suite F: /grok-list Command](#test-suite-f-grok-list-command)
9. [Test Suite G: /grok-export Command](#test-suite-g-grok-export-command)
10. [Test Suite H: Error Handling](#test-suite-h-error-handling)
11. [Test Results Summary](#test-results-summary)

---

## Test Environment Setup

### Prerequisites

```bash
# 1. Verify API key is set
echo $XAI_API_KEY
# Expected: Your XAI API key (not empty)

# 2. Verify project path
echo $GROK_PROJECT_PATH
# Expected: /path/to/ai-dialogue (or can be empty if using auto-detection)

# 3. Verify commands exist
ls -lh ~/.claude/commands/grok*.md
# Expected: grok.md, grok-list.md, grok-export.md

# 4. Verify ai-dialogue project
cd $GROK_PROJECT_PATH || cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
ls pyproject.toml venv/bin/activate
# Expected: Both files exist

# 5. Verify virtual environment
source venv/bin/activate
python -c "import click; from src.clients.grok import GrokClient; print('✓ Dependencies OK')"
# Expected: ✓ Dependencies OK
```

### Test Data Preparation

```bash
# Create test directory for outputs
mkdir -p test-outputs
cd test-outputs

# Record start time
date > test-session-start.txt
```

---

## Pre-Test Checklist

- [ ] XAI_API_KEY environment variable set
- [ ] ai-dialogue project accessible (via path detection)
- [ ] Virtual environment activated and dependencies installed
- [ ] Test outputs directory created
- [ ] Sufficient API credits available (test will make ~20 API calls)

**Estimated Test Duration**: 15-20 minutes
**Estimated Cost**: ~$0.50 (depending on API pricing)

---

## Test Suite A: Path Detection

**Purpose**: Validate 5-level path detection works correctly

### A1: Level 1 - Environment Variable

**Test Command**:
```bash
export GROK_PROJECT_PATH="/Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue"
/grok --help | head -5
```

**Expected Result**:
- Help output displays
- No "project not found" error

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### A2: Level 2 - Settings File

**Test Command**:
```bash
# Temporarily unset env var
unset GROK_PROJECT_PATH

# Verify settings.json exists and has grok config
cat ~/.claude/settings.json | grep -A 2 '"grok"'

# Run command
/grok --help | head -5
```

**Expected Result**:
- Settings file contains grok.project_path
- Help output displays correctly

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### A3: Level 3 - Current Directory

**Test Command**:
```bash
unset GROK_PROJECT_PATH
cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
/grok --help | head -5
```

**Expected Result**:
- Auto-detects from pyproject.toml
- Help output displays

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### A4: Level 5 - Failure Case

**Test Command**:
```bash
# Temporarily rename project
mv ~/Documents/LUXOR/PROJECTS/ai-dialogue ~/Documents/LUXOR/PROJECTS/ai-dialogue-backup
unset GROK_PROJECT_PATH
cd ~

/grok --help

# Restore
mv ~/Documents/LUXOR/PROJECTS/ai-dialogue-backup ~/Documents/LUXOR/PROJECTS/ai-dialogue
```

**Expected Result**:
- Error message: "ai-dialogue project not found"
- Setup instructions displayed

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite B: /grok Command - Information Flags

**Purpose**: Test all information/help flags work correctly

### B1: --help Flag

**Test Command**:
```bash
/grok --help
```

**Expected Result**:
- Comprehensive help documentation
- Usage examples
- Flag descriptions
- Configuration instructions

**Actual Result**:
```
[TO BE FILLED DURING TEST]

[Paste first 50 lines of output]
```

**Status**: [ ] Pass [ ] Fail

---

### B2: --list-models Flag

**Test Command**:
```bash
/grok --list-models
```

**Expected Result**:
- Lists Grok 4 models (fast-reasoning, fast-non-reasoning, code-fast)
- Lists Grok 2 models (vision, image)
- Shows capabilities and use cases

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### B3: --list-modes Flag

**Test Command**:
```bash
/grok --list-modes
```

**Expected Result**:
- Lists all 6 modes: loop, debate, podcast, pipeline, dynamic, research-enhanced
- Shows default turn counts
- Provides use case examples

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### B4: --test Flag

**Test Command**:
```bash
/grok --test
```

**Expected Result**:
- Runs adapter test suite
- All tests pass (or clear failure messages)
- Shows test results summary

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite C: /grok Command - Quick Mode

**Purpose**: Test quick query mode (--quick flag)

### C1: Basic Quick Query

**Test Command**:
```bash
/grok "What is 2+2? Answer in one word." --quick
```

**Expected Result**:
- Fast response (<5 seconds)
- Direct answer
- Token count displayed

**Actual Result**:
```
Response Time: [_____] seconds

Response:
[TO BE FILLED DURING TEST]

Tokens:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### C2: Quick Query with Technical Question

**Test Command**:
```bash
/grok "What is JWT? Answer in one sentence." --quick
```

**Expected Result**:
- Concise technical answer
- Response time <5s

**Actual Result**:
```
Response:
[TO BE FILLED DURING TEST]

Tokens:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### C3: Quick Query with Code Question

**Test Command**:
```bash
/grok "Write a Python function to reverse a string. Just the code, no explanation." --quick
```

**Expected Result**:
- Returns Python code
- Minimal formatting

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite D: /grok Command - Orchestration Modes

**Purpose**: Test all 6 orchestration modes

### D1: Loop Mode (Default 8 turns)

**Test Command**:
```bash
/grok "What is category theory?" --mode loop --turns 2 --output test-outputs/loop-mode.md
```

**Expected Result**:
- Sequential dialogue for 2 turns
- Session saved to test-outputs/loop-mode.md
- Session ID displayed
- Auto-saved to sessions/

**Actual Result**:
```
Execution time: [_____] seconds

Session ID: [TO BE FILLED]

Session saved to: [TO BE FILLED]

Output preview (first 500 chars):
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### D2: Debate Mode (Default 6 turns)

**Test Command**:
```bash
/grok "Microservices vs Monolith" --mode debate --turns 2 --output test-outputs/debate-mode.md
```

**Expected Result**:
- Adversarial/balanced exploration
- Two perspectives presented
- Session saved

**Actual Result**:
```
Session ID: [TO BE FILLED]

Output preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### D3: Podcast Mode (Default 10 turns)

**Test Command**:
```bash
/grok "AI safety basics" --mode podcast --turns 2 --output test-outputs/podcast-mode.md
```

**Expected Result**:
- Conversational tone
- Accessible explanations
- Session saved

**Actual Result**:
```
Session ID: [TO BE FILLED]

Output preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### D4: Pipeline Mode (Default 7 turns)

**Test Command**:
```bash
/grok "Design a simple REST API" --mode pipeline --turns 2 --output test-outputs/pipeline-mode.md
```

**Expected Result**:
- Systematic workflow
- Step-by-step process
- Session saved

**Actual Result**:
```
Session ID: [TO BE FILLED]

Output preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### D5: Dynamic Mode (Variable turns)

**Test Command**:
```bash
/grok "Distributed consensus" --mode dynamic --turns 2 --output test-outputs/dynamic-mode.md
```

**Expected Result**:
- Adaptive approach
- Variable structure based on complexity
- Session saved

**Actual Result**:
```
Session ID: [TO BE FILLED]

Output preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### D6: Research-Enhanced Mode (Variable turns)

**Test Command**:
```bash
/grok "Machine learning optimization" --mode research-enhanced --turns 2 --output test-outputs/research-mode.md
```

**Expected Result**:
- Deep research approach
- Comprehensive analysis
- Session saved

**Actual Result**:
```
Session ID: [TO BE FILLED]

Output preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite E: /grok Command - Advanced Flags

**Purpose**: Test all advanced customization flags

### E1: Custom Model Flag

**Test Command**:
```bash
/grok "Write Python code for factorial" --quick --model grok-code-fast-1
```

**Expected Result**:
- Uses grok-code-fast-1 model
- Returns Python code

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### E2: Temperature Flag

**Test Command**:
```bash
# Low temperature (deterministic)
/grok "Count from 1 to 5" --quick --temperature 0.1

# High temperature (creative)
/grok "Count from 1 to 5" --quick --temperature 1.5
```

**Expected Result**:
- Low temp: Predictable output
- High temp: More varied output

**Actual Result**:
```
Low temperature output:
[TO BE FILLED DURING TEST]

High temperature output:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### E3: Max Tokens Flag

**Test Command**:
```bash
/grok "Explain quantum computing" --quick --max-tokens 50
```

**Expected Result**:
- Response limited to ~50 tokens
- Truncated but coherent

**Actual Result**:
```
[TO BE FILLED DURING TEST]

Token count: [_____]
```

**Status**: [ ] Pass [ ] Fail

---

### E4: Output File Flag

**Test Command**:
```bash
/grok "What is Rust?" --mode loop --turns 2 --output test-outputs/custom-output.md

# Verify file created
ls -lh test-outputs/custom-output.md
cat test-outputs/custom-output.md | head -20
```

**Expected Result**:
- File created at specified path
- Contains session transcript

**Actual Result**:
```
File info:
[TO BE FILLED DURING TEST]

File preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### E5: Verbose Flag

**Test Command**:
```bash
/grok "What is Go?" --quick --verbose
```

**Expected Result**:
- Detailed execution information
- Shows configuration
- Token breakdown

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### E6: Combined Flags

**Test Command**:
```bash
/grok "Design a caching system" \
  --mode loop \
  --turns 2 \
  --model grok-code-fast-1 \
  --temperature 0.7 \
  --max-tokens 2000 \
  --output test-outputs/combined-flags.md \
  --verbose
```

**Expected Result**:
- All flags respected
- Verbose output shown
- Session saved to specified file

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite F: /grok-list Command

**Purpose**: Test session listing functionality

### F1: List Sessions (After Running Tests)

**Test Command**:
```bash
/grok-list
```

**Expected Result**:
- Shows all sessions from Suite D tests
- Displays session IDs, modes, turns, timestamps
- Shows both JSON and MD files

**Actual Result**:
```
[TO BE FILLED DURING TEST]

Session count: [_____]
```

**Status**: [ ] Pass [ ] Fail

---

### F2: List Sessions (Empty Directory)

**Test Command**:
```bash
# Temporarily move sessions
mv ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions-backup

/grok-list

# Restore
mv ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions-backup ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions
```

**Expected Result**:
- Message: "No sessions found"
- Helpful tip to run /grok

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite G: /grok-export Command

**Purpose**: Test session export functionality

### G1: Export to Stdout (Preview)

**Test Command**:
```bash
# Get first session ID from /grok-list
SESSION_ID=$(ls ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions/*.json | head -1 | xargs basename -s .json)

/grok-export "$SESSION_ID" | head -50
```

**Expected Result**:
- Markdown output to stdout
- Readable session transcript

**Actual Result**:
```
Session ID used: [TO BE FILLED]

Output preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### G2: Export to Markdown File

**Test Command**:
```bash
SESSION_ID=$(ls ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions/*.json | head -1 | xargs basename -s .json)

/grok-export "$SESSION_ID" --output test-outputs/export-markdown.md

# Verify
ls -lh test-outputs/export-markdown.md
head -30 test-outputs/export-markdown.md
```

**Expected Result**:
- File created
- Contains formatted markdown

**Actual Result**:
```
File size: [_____]

Content preview:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### G3: Export to JSON Format

**Test Command**:
```bash
SESSION_ID=$(ls ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions/*.json | head -1 | xargs basename -s .json)

/grok-export "$SESSION_ID" --format json --output test-outputs/export-json.json

# Verify structure
cat test-outputs/export-json.json | jq '.session_id, .mode, .turns'
```

**Expected Result**:
- Valid JSON file
- Contains session metadata

**Actual Result**:
```
Session ID: [TO BE FILLED]
Mode: [TO BE FILLED]
Turns: [TO BE FILLED]

JSON structure:
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### G4: Export to Plain Text

**Test Command**:
```bash
SESSION_ID=$(ls ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions/*.json | head -1 | xargs basename -s .json)

/grok-export "$SESSION_ID" --format text --output test-outputs/export-text.txt

# Verify
head -40 test-outputs/export-text.txt
```

**Expected Result**:
- Plain text output
- No markdown formatting

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### G5: Export with Verbose Mode

**Test Command**:
```bash
SESSION_ID=$(ls ~/Documents/LUXOR/PROJECTS/ai-dialogue/sessions/*.json | head -1 | xargs basename -s .json)

/grok-export "$SESSION_ID" --output test-outputs/export-verbose.md --verbose
```

**Expected Result**:
- Shows file location
- Shows file size
- Preview of content

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite H: Error Handling

**Purpose**: Test error handling for invalid inputs

### H1: /grok - Missing Topic

**Test Command**:
```bash
/grok --mode loop
```

**Expected Result**:
- Error message: "Topic required"
- Usage instructions

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### H2: /grok - Invalid Mode

**Test Command**:
```bash
/grok "test topic" --mode invalid-mode
```

**Expected Result**:
- Error message about invalid mode
- List of available modes

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### H3: /grok - Missing API Key

**Test Command**:
```bash
unset XAI_API_KEY
/grok "test" --quick

# Restore
export XAI_API_KEY="your-key"
```

**Expected Result**:
- Error: "XAI_API_KEY not set"
- Setup instructions

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### H4: /grok-export - Session Not Found

**Test Command**:
```bash
/grok-export "nonexistent-session-id"
```

**Expected Result**:
- Error: "Session not found"
- Shows available sessions

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

### H5: /grok-export - Missing Session ID

**Test Command**:
```bash
/grok-export
```

**Expected Result**:
- Error: "Session ID required"
- Usage examples

**Actual Result**:
```
[TO BE FILLED DURING TEST]
```

**Status**: [ ] Pass [ ] Fail

---

## Test Results Summary

**Test Date**: [TO BE FILLED]
**Tester**: [TO BE FILLED]
**Total Tests**: 40

### Results by Suite

| Suite | Total | Passed | Failed | Notes |
|-------|-------|--------|--------|-------|
| A: Path Detection | 4 | [ ] | [ ] | |
| B: Information Flags | 4 | [ ] | [ ] | |
| C: Quick Mode | 3 | [ ] | [ ] | |
| D: Orchestration Modes | 6 | [ ] | [ ] | |
| E: Advanced Flags | 6 | [ ] | [ ] | |
| F: /grok-list | 2 | [ ] | [ ] | |
| G: /grok-export | 5 | [ ] | [ ] | |
| H: Error Handling | 5 | [ ] | [ ] | |
| **TOTAL** | **40** | [ ] | [ ] | |

### Overall Status

**Pass Rate**: ____%

**Critical Issues Found**: [ ] None [ ] Minor [ ] Major

**Production Readiness**: [ ] Ready [ ] Needs fixes [ ] Significant work required

---

## Issues Found

### Issue 1
- **Test**: [Test ID]
- **Severity**: [ ] Critical [ ] Major [ ] Minor
- **Description**: [Description]
- **Expected**: [Expected behavior]
- **Actual**: [Actual behavior]
- **Fix Required**: [Fix description]

### Issue 2
[Add as needed]

---

## Performance Metrics

**Average Response Times**:
- Quick mode: [_____] seconds
- Orchestration mode (2 turns): [_____] seconds
- List sessions: [_____] seconds
- Export session: [_____] seconds

**Token Usage**:
- Total tokens consumed: [_____]
- Estimated cost: $[_____]

---

## Recommendations

### Short-term
1. [Recommendation based on test results]
2. [Recommendation based on test results]

### Long-term
1. [Recommendation for improvements]
2. [Recommendation for enhancements]

---

## Test Execution Instructions

### How to Run This Test Plan

1. **Prepare environment**:
   ```bash
   export XAI_API_KEY="your-key"
   export GROK_PROJECT_PATH="/path/to/ai-dialogue"
   cd ~/Documents/LUXOR/PROJECTS/ai-dialogue
   source venv/bin/activate
   mkdir -p test-outputs
   ```

2. **Open this document in editor** for filling results

3. **Run each test** sequentially, copying commands exactly

4. **Record results** immediately after each test

5. **Mark status** (Pass/Fail) for each test

6. **Document issues** in Issues Found section

7. **Calculate summary** statistics

8. **Save final document** with timestamp:
   ```bash
   cp docs/GROK-COMMANDS-TEST-PLAN.md docs/GROK-COMMANDS-TEST-RESULTS-$(date +%Y%m%d).md
   ```

---

**Test Plan Version**: 1.0.0
**Created By**: AI Dialogue System Analysis (MARS × MERCURIO × cc2-observe)
**Review Required**: Yes - before production release
**Next Review**: After test execution

---

*Comprehensive validation ensures production readiness and user confidence.*
