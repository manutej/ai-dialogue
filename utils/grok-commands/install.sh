#!/bin/bash
# Grok Commands Installer
# Installs /grok slash commands for Claude Code
# Usage: ./install.sh [--global|--project]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Grok Commands Installer for Claude Code      ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo ""

# Determine installation target
INSTALL_MODE="${1:---project}"

if [[ "$INSTALL_MODE" == "--global" ]]; then
    TARGET_DIR="$HOME/.claude/commands"
    SCOPE="global (all projects)"
elif [[ "$INSTALL_MODE" == "--project" ]]; then
    TARGET_DIR=".claude/commands"
    SCOPE="project-level (ai-dialogue only)"
else
    echo -e "${RED}Error: Invalid option '$INSTALL_MODE'${NC}"
    echo "Usage: $0 [--global|--project]"
    exit 1
fi

echo -e "${BLUE}Installation target:${NC} $SCOPE"
echo -e "${BLUE}Target directory:${NC} $TARGET_DIR"
echo ""

# Verify we're in the right directory
if [[ ! -f "utils/grok-commands/commands/grok.md" ]]; then
    echo -e "${RED}Error: Must run from ai-dialogue project root${NC}"
    echo "Current directory: $(pwd)"
    echo "Expected: .../ai-dialogue/"
    exit 1
fi

# Create target directory if needed
if [[ ! -d "$TARGET_DIR" ]]; then
    echo -e "${YELLOW}Creating directory: $TARGET_DIR${NC}"
    mkdir -p "$TARGET_DIR"
fi

# Install commands
echo "Installing commands..."
echo ""

install_command() {
    local cmd_file="$1"
    local cmd_name=$(basename "$cmd_file")

    echo -n "  Installing $cmd_name... "

    if cp "utils/grok-commands/commands/$cmd_file" "$TARGET_DIR/"; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Install each command
install_command "grok.md"
install_command "grok-list.md"
install_command "grok-export.md"

echo ""
echo -e "${GREEN}✓ Commands installed successfully!${NC}"
echo ""

# Check for API key
echo "Checking prerequisites..."
echo ""

if [[ -z "${XAI_API_KEY:-}" ]]; then
    echo -e "${YELLOW}⚠ XAI_API_KEY not set${NC}"
    echo ""
    echo "To use /grok commands, set your xAI API key:"
    echo "  export XAI_API_KEY='your-key-here'"
    echo ""
    echo "Make it permanent by adding to ~/.zshrc or ~/.bashrc:"
    echo "  echo 'export XAI_API_KEY=\"your-key-here\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    echo ""
else
    echo -e "${GREEN}✓ XAI_API_KEY is set${NC}"
fi

# Check for project path
if [[ -z "${GROK_PROJECT_PATH:-}" ]]; then
    echo -e "${BLUE}ℹ GROK_PROJECT_PATH not set (optional)${NC}"
    echo ""
    echo "Commands will auto-detect the ai-dialogue project."
    echo "If auto-detection fails, you can set manually:"
    echo "  export GROK_PROJECT_PATH='$(pwd)'"
    echo ""
else
    echo -e "${GREEN}✓ GROK_PROJECT_PATH set to: $GROK_PROJECT_PATH${NC}"
fi

# Check Python environment
echo "Checking Python environment..."
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 available${NC}"

    # Check if venv exists and dependencies are installed
    if [[ -f "venv/bin/activate" ]]; then
        echo -e "${GREEN}✓ Virtual environment found${NC}"

        # Test dependencies
        if source venv/bin/activate && python -c "import click; from src.clients.grok import GrokClient" 2>/dev/null; then
            echo -e "${GREEN}✓ Dependencies installed${NC}"
            deactivate 2>/dev/null || true
        else
            echo -e "${YELLOW}⚠ Some dependencies missing${NC}"
            echo "  Run: pip install -e ."
            deactivate 2>/dev/null || true
        fi
    else
        echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
        echo "  Run: python -m venv venv && source venv/bin/activate && pip install -e ."
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "  Install Python 3 to use /grok commands"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. ${YELLOW}Restart Claude Code${NC} (important - commands are cached)"
echo "   - Close Claude Code completely and reopen"
echo "   - OR start a new conversation"
echo ""
echo "2. Test installation:"
echo "   /grok --help"
echo "   /grok --quick \"What is 2+2?\""
echo "   /grok-list"
echo ""
echo "3. Run comprehensive tests:"
echo "   ./tests/grok-commands/scripts/run-quick-tests.sh"
echo ""
echo "Documentation:"
echo "  - Quick Start: utils/grok-commands/README.md"
echo "  - User Guide: utils/grok-commands/docs/GROK-COMMANDS-QUICK-REFERENCE.md"
echo "  - Testing: tests/grok-commands/docs/TESTING-SUMMARY.md"
echo ""
echo -e "${GREEN}Happy orchestrating with Grok! 🚀${NC}"
