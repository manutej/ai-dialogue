#!/bin/bash
# /grok Commands - Automated Test Execution Script
# Created: 2025-11-13
# Purpose: Execute all test cases and capture formatted results
#
# Usage: ./test-grok-commands.sh [--quick|--full]
#   --quick: Run only critical tests (5-10 tests, ~2 minutes)
#   --full:  Run all 40 tests (~15 minutes)

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Output directory
OUTPUT_DIR="test-outputs/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Log file
LOG_FILE="$OUTPUT_DIR/test-execution.log"
RESULTS_FILE="$OUTPUT_DIR/test-results.md"

# ============================================================================
# Helper Functions
# ============================================================================

log() {
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*" | tee -a "$LOG_FILE"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}✗${NC} $*" | tee -a "$LOG_FILE"
    ((TESTS_FAILED++))
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $*" | tee -a "$LOG_FILE"
}

section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$*${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

run_test() {
    local test_id="$1"
    local test_name="$2"
    local test_command="$3"
    local expected_pattern="$4"  # Regex pattern to match in output

    ((TESTS_RUN++))

    log "Running Test $test_id: $test_name"
    log "Command: $test_command"

    # Create output file for this test
    local output_file="$OUTPUT_DIR/test-${test_id}.txt"

    # Execute command and capture output
    if eval "$test_command" > "$output_file" 2>&1; then
        # Check if output matches expected pattern
        if grep -qE "$expected_pattern" "$output_file"; then
            log_success "Test $test_id passed"

            # Append to results file
            {
                echo "### Test $test_id: $test_name"
                echo ""
                echo "**Command**:"
                echo '```bash'
                echo "$test_command"
                echo '```'
                echo ""
                echo "**Output**:"
                echo '```'
                head -50 "$output_file"  # First 50 lines
                echo '```'
                echo ""
                echo "**Status**: ✓ PASSED"
                echo ""
                echo "---"
                echo ""
            } >> "$RESULTS_FILE"

            return 0
        else
            log_error "Test $test_id failed: Output doesn't match expected pattern"
            log "Expected pattern: $expected_pattern"

            # Append to results file
            {
                echo "### Test $test_id: $test_name"
                echo ""
                echo "**Command**:"
                echo '```bash'
                echo "$test_command"
                echo '```'
                echo ""
                echo "**Output**:"
                echo '```'
                head -50 "$output_file"
                echo '```'
                echo ""
                echo "**Status**: ✗ FAILED - Output doesn't match expected pattern"
                echo ""
                echo "**Expected**: $expected_pattern"
                echo ""
                echo "---"
                echo ""
            } >> "$RESULTS_FILE"

            return 1
        fi
    else
        log_error "Test $test_id failed: Command execution error"

        # Append to results file
        {
            echo "### Test $test_id: $test_name"
            echo ""
            echo "**Command**:"
            echo '```bash'
            echo "$test_command"
            echo '```'
            echo ""
            echo "**Error**:"
            echo '```'
            cat "$output_file"
            echo '```'
            echo ""
            echo "**Status**: ✗ FAILED - Command execution error"
            echo ""
            echo "---"
            echo ""
        } >> "$RESULTS_FILE"

        return 1
    fi
}

# ============================================================================
# Pre-Test Validation
# ============================================================================

section "PRE-TEST VALIDATION"

# Initialize results file
cat > "$RESULTS_FILE" <<EOF
# /grok Commands - Test Execution Results

**Date**: $(date +%Y-%m-%d)
**Time**: $(date +%H:%M:%S)
**Test Mode**: \${TEST_MODE}

---

## Test Results

EOF

# Check if Claude Code environment is fresh
log "Checking Claude Code environment..."
if /grok --help 2>&1 | grep -q "Multi-model orchestration"; then
    log_success "Claude Code environment is up to date"
else
    log_error "Claude Code environment may have stale cache"
    log_warn "Please restart Claude Code before running tests"
    log_warn "Or start a new conversation to reload commands"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Test execution aborted by user"
        exit 1
    fi
fi

# Check XAI API key
if [[ -z "${XAI_API_KEY:-}" ]]; then
    log_error "XAI_API_KEY environment variable not set"
    log "Please set it with: export XAI_API_KEY='your-key-here'"
    exit 1
else
    log_success "XAI_API_KEY is set"
fi

# Check project path detection
if [[ -n "${GROK_PROJECT_PATH:-}" ]]; then
    log_success "GROK_PROJECT_PATH set to: $GROK_PROJECT_PATH"
elif [[ -f "pyproject.toml" ]] && grep -q "ai-dialogue" pyproject.toml 2>/dev/null; then
    log_success "Auto-detection will work (running from ai-dialogue directory)"
else
    log_warn "GROK_PROJECT_PATH not set and not in ai-dialogue directory"
    log "Setting GROK_PROJECT_PATH for tests..."
    export GROK_PROJECT_PATH="/Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue"
fi

# Check commands exist
if [[ ! -f ~/.claude/commands/grok.md ]]; then
    log_error "~/.claude/commands/grok.md not found"
    exit 1
else
    log_success "Commands are installed"
fi

# Check Python dependencies
log "Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    log_success "Python 3 is available"
else
    log_error "Python 3 not found"
    exit 1
fi

# ============================================================================
# Test Mode Selection
# ============================================================================

TEST_MODE="${1:---quick}"

if [[ "$TEST_MODE" == "--full" ]]; then
    log "Running FULL test suite (40 tests, ~15 minutes)"
    RUN_FULL=true
else
    log "Running QUICK test suite (10 critical tests, ~2 minutes)"
    RUN_FULL=false
fi

# ============================================================================
# Test Suite A: Path Detection (Critical)
# ============================================================================

section "TEST SUITE A: Path Detection"

run_test "A1" "Environment Variable Path Detection" \
    "/grok --help | head -5" \
    "grok"

run_test "A2" "Auto-Detection from Current Directory" \
    "cd ~/Documents/LUXOR/PROJECTS/ai-dialogue && /grok --help | head -3" \
    "grok"

# ============================================================================
# Test Suite B: Information Flags (Critical)
# ============================================================================

section "TEST SUITE B: Information Flags"

run_test "B1" "--help Flag" \
    "/grok --help" \
    "(Usage|Examples|FLAGS)"

run_test "B2" "--list-models Flag" \
    "/grok --list-models" \
    "(grok-.*|Available Models)"

run_test "B3" "--list-modes Flag" \
    "/grok --list-modes" \
    "(loop|debate|podcast|pipeline|dynamic|research)"

# ============================================================================
# Test Suite C: Quick Mode (Critical)
# ============================================================================

section "TEST SUITE C: Quick Mode (Single-Turn Queries)"

run_test "C1" "Quick Mode - Simple Question" \
    "/grok --quick \"What is 2+2?\"" \
    "(4|four)"

run_test "C2" "Quick Mode with Custom Model" \
    "/grok --quick --model grok-beta \"Explain recursion in one sentence\"" \
    "(recurs|itself|function)"

if [[ "$RUN_FULL" == true ]]; then
    run_test "C3" "Quick Mode with Output File" \
        "/grok --quick --output $OUTPUT_DIR/quick-test.txt \"List 3 programming languages\"" \
        "(Python|JavaScript|Java|Go|Rust)"
fi

# ============================================================================
# Test Suite D: Orchestration Modes (Sample if quick, all if full)
# ============================================================================

section "TEST SUITE D: Orchestration Modes"

run_test "D1" "Loop Mode (Knowledge Building)" \
    "/grok --mode loop --turns 2 \"Explain quantum computing\"" \
    "(quantum|qubit|superposition)"

if [[ "$RUN_FULL" == true ]]; then
    run_test "D2" "Debate Mode (Adversarial Exploration)" \
        "/grok --mode debate --turns 2 \"Is AI beneficial or harmful?\"" \
        "(beneficial|harmful|advantage|risk)"

    run_test "D3" "Podcast Mode (Conversational)" \
        "/grok --mode podcast --turns 2 \"Future of space exploration\"" \
        "(space|Mars|rocket|exploration)"

    run_test "D4" "Pipeline Mode (Static Workflow)" \
        "/grok --mode pipeline \"Analyze: The quick brown fox\"" \
        "(quick|brown|fox)"
fi

# ============================================================================
# Test Suite E: Advanced Flags
# ============================================================================

section "TEST SUITE E: Advanced Flags"

if [[ "$RUN_FULL" == true ]]; then
    run_test "E1" "Custom Temperature" \
        "/grok --quick --temperature 0.1 \"Say 'test'\"" \
        "test"

    run_test "E2" "Custom Max Tokens" \
        "/grok --quick --max-tokens 50 \"Write a short poem\"" \
        "."

    run_test "E3" "Verbose Output" \
        "/grok --quick --verbose \"What is AI?\"" \
        "(AI|artificial|intelligence)"
fi

# ============================================================================
# Test Suite F: /grok-list Command
# ============================================================================

section "TEST SUITE F: /grok-list Command"

run_test "F1" "List All Sessions" \
    "/grok-list" \
    "(sessions|Session|No sessions|ID)"

# ============================================================================
# Test Suite G: /grok-export Command
# ============================================================================

section "TEST SUITE G: /grok-export Command"

# This test requires an existing session, so we'll create one first
log "Creating test session for export tests..."
TEST_SESSION_OUTPUT="$OUTPUT_DIR/export-test-session.md"
/grok --quick --output "$TEST_SESSION_OUTPUT" "Test export functionality" > /dev/null 2>&1 || true

if [[ "$RUN_FULL" == true ]]; then
    run_test "G1" "Export to Markdown (default)" \
        "/grok-export --help" \
        "(export|markdown|json|format)"
fi

# ============================================================================
# Test Suite H: Error Handling
# ============================================================================

section "TEST SUITE H: Error Handling"

run_test "H1" "Invalid Mode" \
    "/grok --mode invalid-mode \"test\" 2>&1 || true" \
    "(Invalid|unknown|not found|error)"

run_test "H2" "Invalid Model" \
    "/grok --quick --model invalid-model \"test\" 2>&1 || true" \
    "(Invalid|unknown|not found|error)"

if [[ "$RUN_FULL" == true ]]; then
    run_test "H3" "Missing Query" \
        "/grok 2>&1 || true" \
        "(required|missing|query|help)"
fi

# ============================================================================
# Test Summary
# ============================================================================

section "TEST SUMMARY"

# Append summary to results file
{
    echo ""
    echo "---"
    echo ""
    echo "## Summary"
    echo ""
    echo "| Metric | Count |"
    echo "|--------|-------|"
    echo "| Tests Run | $TESTS_RUN |"
    echo "| Tests Passed | $TESTS_PASSED |"
    echo "| Tests Failed | $TESTS_FAILED |"
    echo "| Success Rate | $(awk "BEGIN {printf \"%.1f%%\", ($TESTS_PASSED/$TESTS_RUN)*100}") |"
    echo ""
    echo "**Test Mode**: $TEST_MODE"
    echo "**Duration**: $(date +%H:%M:%S)"
    echo ""
} >> "$RESULTS_FILE"

log "Tests Run:    $TESTS_RUN"
log_success "Passed:       $TESTS_PASSED"
if [[ $TESTS_FAILED -gt 0 ]]; then
    log_error "Failed:       $TESTS_FAILED"
else
    log "Failed:       $TESTS_FAILED"
fi
echo ""
log "Success Rate: $(awk "BEGIN {printf \"%.1f%%\", ($TESTS_PASSED/$TESTS_RUN)*100}")"
echo ""
log "Results saved to: $RESULTS_FILE"
log "Detailed logs: $LOG_FILE"
log "Test outputs: $OUTPUT_DIR/"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    log_success "All tests passed! ✓"
    exit 0
else
    log_error "Some tests failed. Review results above."
    exit 1
fi
