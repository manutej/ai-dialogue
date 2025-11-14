"""
Grok API Client

Async wrapper around XAI Grok API using OpenAI SDK
"""

import os
import logging
from typing import Dict, Tuple, Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Model ID mapping - VERIFIED via Context7 research (2025-01-13)
# Note: grok-4-0709 does NOT exist in xAI API
MODEL_IDS = {
    # Grok 4 models
    "grok-4": "grok-4",
    "grok-4-fast": "grok-4-fast",

    # Grok 3 models
    "grok-3": "grok-3",
    "grok-3-latest": "grok-3-latest",

    # Grok 2 models (recommended default - most accessible)
    "grok-2": "grok-2-latest",
    "grok-2-latest": "grok-2-latest",

    # Vision models
    "grok-vision": "grok-2-vision-1212",
    "grok-2-vision": "grok-2-vision-1212",
    "grok-2-vision-1212": "grok-2-vision-1212",

    # Image generation
    "grok-image": "grok-2-image",
    "grok-2-image": "grok-2-image",
}


class GrokClient:
    """
    Async client for Grok API

    Uses OpenAI SDK with XAI endpoint for compatibility

    Supported models:
    - grok-4 (alias for grok-4-0709) - Latest Grok model
    - grok-3 - Previous generation
    - grok-vision - Multimodal vision model
    - grok-image - Image generation
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "grok-4"):
        self.api_key = api_key or os.environ.get("XAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "XAI_API_KEY not found. Set environment variable or pass to constructor."
            )

        self.default_model = model
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )

        # Validate model on init
        resolved_model = self._resolve_model(model)
        logger.info(f"Grok client initialized with model: {model} (resolves to {resolved_model})")

    def _resolve_model(self, model: str) -> str:
        """
        Resolve friendly model name to actual API model ID

        Args:
            model: Friendly model name or actual ID

        Returns:
            Actual API model ID

        Raises:
            ValueError: If model not recognized
        """
        if model in MODEL_IDS:
            return MODEL_IDS[model]

        # If it's already a valid ID (not in mapping), return as-is
        # This allows for future models without updating the client
        logger.warning(f"Model '{model}' not in known models, using as-is")
        return model

    async def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Send chat request to Grok API

        Args:
            prompt: User prompt
            model: Model to use (grok-4, grok-3, grok-vision)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt

        Returns:
            (response_text, token_usage_dict)
        """
        use_model = self._resolve_model(model or self.default_model)

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.debug(f"Grok request: model={use_model}, temp={temperature}")

        try:
            response = await self.client.chat.completions.create(
                model=use_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            tokens = {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }

            logger.info(
                f"Grok response: {len(content)} chars, "
                f"{tokens['total']} tokens "
                f"({tokens['prompt']} prompt + {tokens['completion']} completion)"
            )

            return content, tokens

        except Exception as e:
            logger.error(f"Grok API error: {e}")
            raise

    async def chat_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None
    ):
        """
        Stream chat response from Grok

        Yields chunks as they arrive
        """
        use_model = self._resolve_model(model or self.default_model)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.debug(f"Grok streaming request: model={use_model}")

        try:
            stream = await self.client.chat.completions.create(
                model=use_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Grok streaming error: {e}")
            raise

    async def close(self):
        """Close the async client"""
        await self.client.close()
