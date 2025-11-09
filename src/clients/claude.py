"""
Claude CLI Client

Async wrapper around Claude Code CLI for protocol integration
"""

import asyncio
import json
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Async wrapper for Claude CLI

    Simple subprocess-based integration. Can be enhanced
    later with direct API access if needed.
    """

    def __init__(self, model: str = "sonnet"):
        self.model = model
        self.default_temperature = 0.7

    async def chat(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = 4096
    ) -> Tuple[str, Dict[str, int]]:
        """
        Send chat request to Claude via CLI

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            (response_text, token_usage_dict)
        """
        temp = temperature if temperature is not None else self.default_temperature

        logger.debug(f"Claude request: model={self.model}, temp={temp}")

        try:
            # Create subprocess
            proc = await asyncio.create_subprocess_exec(
                "claude",
                "--model", self.model,
                "--prompt", prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=300  # 5 minutes max
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                raise TimeoutError("Claude CLI request timed out after 5 minutes")

            # Check for errors
            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Claude CLI error: {error_msg}")

            response = stdout.decode().strip()

            # Extract tokens from response if possible
            # Claude CLI may include metadata - parse if available
            tokens = self._parse_token_usage(response)

            logger.info(f"Claude response: {len(response)} chars, ~{tokens['total']} tokens")

            return response, tokens

        except FileNotFoundError:
            raise RuntimeError(
                "Claude CLI not found. Please ensure 'claude' command is available in PATH."
            )
        except Exception as e:
            logger.error(f"Claude client error: {e}")
            raise

    def _parse_token_usage(self, response: str) -> Dict[str, int]:
        """
        Parse token usage from Claude response

        Claude CLI may include metadata. For now, estimate tokens.
        Can be enhanced later with actual usage data.
        """
        # Rough estimation: 1 token ≈ 4 characters
        response_tokens = len(response) // 4

        return {
            "prompt": 0,  # Not available from CLI
            "completion": response_tokens,
            "total": response_tokens
        }

    async def chat_stream(
        self,
        prompt: str,
        temperature: float = None
    ):
        """
        Stream chat response (for future enhancement)

        Currently not implemented in simple CLI wrapper.
        Would require streaming support in Claude CLI.
        """
        raise NotImplementedError(
            "Streaming not yet supported with Claude CLI wrapper"
        )
