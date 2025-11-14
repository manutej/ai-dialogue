#!/bin/bash
# Quick Test Runner for /grok Commands
# Executes minimal viable tests to verify basic functionality
# Usage: ./run-quick-tests.sh

set -e

echo "🧪 /grok Commands - Quick Test Runner"
echo "======================================="
echo ""
echo "This will run 5 critical tests to verify basic functionality."
echo "Estimated time: 1-2 minutes"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

# Test function
test_command() {
    local name="$1"
    local command="$2"

    echo -n "Testing: $name... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

# Pre-checks
echo "Pre-flight checks:"
echo "-----------------"

if [[ -z "${XAI_API_KEY:-}" ]]; then
    echo -e "${RED}✗ XAI_API_KEY not set${NC}"
    echo "Please run: export XAI_API_KEY='your-key-here'"
    exit 1
else
    echo -e "${GREEN}✓ XAI_API_KEY is set${NC}"
fi

if [[ ! -f ~/.claude/commands/grok.md ]]; then
    echo -e "${RED}✗ Commands not installed${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Commands installed${NC}"
fi

echo ""
echo "Running tests:"
echo "--------------"

# Test 1: Help command
test_command "Help Command" "/grok --help | grep -q 'orchestration'"

# Test 2: List models
test_command "List Models" "/grok --list-models | grep -q 'grok-beta'"

# Test 3: List modes
test_command "List Modes" "/grok --list-modes | grep -q 'loop'"

# Test 4: Quick mode (actual API call)
echo -n "Testing: Quick Mode (API call)... "
if /grok --quick "What is 2+2?" 2>&1 | grep -qE "(4|four)"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 5: Session listing
test_command "List Sessions" "/grok-list | grep -qE '(Session|sessions|No sessions)'"

echo ""
echo "Summary:"
echo "--------"
echo "Passed: $PASSED/5"
echo "Failed: $FAILED/5"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All tests passed! Your /grok commands are working correctly.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. See GROK-TESTING-GUIDE.md for troubleshooting.${NC}"
    exit 1
fi
