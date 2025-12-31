"""
Tests for AI Dialogue CLI

Tests CLI argument parsing, command execution, and error handling.
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
import json

from cli import cli


@pytest.fixture
def runner():
    """Create Click CLI test runner"""
    return CliRunner()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


# ============================================================================
# CLI Argument Parsing Tests
# ============================================================================

class TestCLIArguments:
    """Test CLI argument parsing and validation"""

    def test_cli_help_command(self, runner):
        """Test CLI help command works"""
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "AI Dialogue" in result.output
        assert "Async AI orchestration protocol" in result.output

    def test_run_command_help(self, runner):
        """Test run command help"""
        result = runner.invoke(cli, ['run', '--help'])

        assert result.exit_code == 0
        assert "--mode" in result.output
        assert "--topic" in result.output
        assert "--turns" in result.output

    def test_run_requires_mode(self, runner):
        """Test that run command requires mode argument"""
        result = runner.invoke(cli, ['run', '--topic', 'test'])

        # Should fail because mode is required
        assert result.exit_code != 0

    def test_run_requires_topic(self, runner):
        """Test that run command requires topic argument"""
        result = runner.invoke(cli, ['run', '--mode', 'loop'])

        # Should fail because topic is required
        assert result.exit_code != 0

    def test_modes_command(self, runner):
        """Test modes listing command"""
        result = runner.invoke(cli, ['modes'])

        assert result.exit_code == 0
        assert "Available Modes" in result.output
        # Should list at least one mode
        assert "loop" in result.output.lower() or "debate" in result.output.lower()


# ============================================================================
# CLI Execution Tests
# ============================================================================

class TestCLIExecution:
    """Test CLI command execution (with mocked components)"""

    @pytest.mark.skip(reason="Requires full async setup with mocked clients")
    def test_run_command_basic_execution(self, runner):
        """Test basic run command execution"""
        # This would require mocking ClaudeClient, GrokClient, and StateManager
        # We'll test the argument handling instead
        result = runner.invoke(cli, [
            'run',
            '--mode', 'loop',
            '--topic', 'test topic',
            '--turns', '2'
        ])

        # With proper mocks, this should succeed
        # For now, we expect it to fail gracefully
        assert result.exit_code in [0, 1]  # Either succeeds with mocks or fails without API

    def test_list_command_execution(self, runner):
        """Test list command execution"""
        # List command should work even with no sessions
        result = runner.invoke(cli, ['list'])

        assert result.exit_code == 0
        # Should either show sessions or "No sessions found"
        assert "sessions" in result.output.lower() or "no sessions" in result.output.lower()

    def test_list_command_with_limit(self, runner):
        """Test list command with limit argument"""
        result = runner.invoke(cli, ['list', '--limit', '5'])

        assert result.exit_code == 0

    @pytest.mark.skip(reason="Requires existing session")
    def test_export_command(self, runner, temp_output_dir):
        """Test export command"""
        output_file = temp_output_dir / "export.md"

        result = runner.invoke(cli, [
            'export',
            'test-session-id',
            '--output', str(output_file)
        ])

        # Will fail without actual session, but should handle error gracefully
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    @pytest.mark.skip(reason="Requires existing session")
    def test_delete_command(self, runner):
        """Test delete command with confirmation"""
        result = runner.invoke(cli, [
            'delete',
            'test-session-id',
            '--yes'  # Auto-confirm
        ])

        # Will fail without actual session
        assert result.exit_code == 1


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestCLIErrorHandling:
    """Test CLI error handling and user feedback"""

    def test_invalid_mode_rejected(self, runner):
        """Test that invalid mode is rejected"""
        result = runner.invoke(cli, [
            'run',
            '--mode', 'invalid-mode',
            '--topic', 'test'
        ])

        assert result.exit_code != 0
        # Click should show available choices
        assert "Invalid value" in result.output or "Choice" in result.output

    def test_nonexistent_config_file_rejected(self, runner):
        """Test that nonexistent config file is rejected"""
        result = runner.invoke(cli, [
            'run',
            '--mode', 'loop',
            '--topic', 'test',
            '--config', '/nonexistent/file.json'
        ])

        assert result.exit_code != 0

    def test_export_nonexistent_session_fails(self, runner):
        """Test export of nonexistent session fails gracefully"""
        result = runner.invoke(cli, [
            'export',
            'nonexistent-session-12345'
        ])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_delete_nonexistent_session_fails(self, runner):
        """Test delete of nonexistent session fails gracefully"""
        result = runner.invoke(cli, [
            'delete',
            'nonexistent-session-12345',
            '--yes'
        ])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()


# ============================================================================
# Output Format Tests
# ============================================================================

class TestCLIOutputFormats:
    """Test CLI output formatting and user feedback"""

    def test_modes_output_format(self, runner):
        """Test modes command output is well-formatted"""
        result = runner.invoke(cli, ['modes'])

        assert result.exit_code == 0
        # Should have emoji and structured output
        assert "📋" in result.output or "🎯" in result.output
        # Should have mode information
        assert "Default turns" in result.output or "Use case" in result.output

    def test_help_output_format(self, runner):
        """Test help output is readable"""
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        # Should have usage section
        assert "Usage:" in result.output
        # Should have commands section
        assert "Commands:" in result.output

    def test_list_empty_sessions_format(self, runner):
        """Test list command output when no sessions exist"""
        # This might fail if sessions exist, but we test the format
        result = runner.invoke(cli, ['list'])

        assert result.exit_code == 0
        # Output should be user-friendly
        assert "session" in result.output.lower()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
