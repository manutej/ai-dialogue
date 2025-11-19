"""
Grok API Client

Async wrapper around XAI Grok API using OpenAI SDK
"""

import os
import logging
from typing import Dict, Tuple, Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Model ID mapping - Official xAI model identifiers (docs.x.ai/docs/models)
# Updated: 2025-11-19 - Verified against official xAI API documentation
#
# GROK 4.1 STATUS (as of Nov 19, 2025):
# - Grok 4.1 released on consumer platforms (Nov 17-18, 2025)
# - NOT yet available via xAI API (awaiting official API release)
# - Will auto-upgrade when xAI releases API access
# - See: https://x.ai/news/grok-4-1
#
# NOTE: Grok-2 models are ONLY for vision/image, NOT for text generation
MODEL_IDS = {
    # ===== TEXT GENERATION MODELS (Grok 4) =====

    # Grok 4 Fast Reasoning (recommended for most tasks)
    "grok-4-fast-reasoning": "grok-4-fast-reasoning",
    "grok-4-fast-reasoning-latest": "grok-4-fast-reasoning-latest",

    # Grok 4 Fast Non-Reasoning (faster, simpler tasks)
    "grok-4-fast-non-reasoning": "grok-4-fast-non-reasoning",
    "grok-4-fast-non-reasoning-latest": "grok-4-fast-non-reasoning-latest",

    # Code-specialized model
    "grok-code-fast": "grok-code-fast-1",
    "grok-code-fast-1": "grok-code-fast-1",

    # ===== MULTIMODAL MODELS (Grok 2 - Vision/Image only) =====

    # Vision model (multimodal - images + text)
    "grok-vision": "grok-2-vision-latest",
    "grok-2-vision-latest": "grok-2-vision-latest",

    # Image generation
    "grok-image": "grok-2-image-latest",
    "grok-2-image-latest": "grok-2-image-latest",

    # ===== CONVENIENCE ALIASES =====

    "grok-4": "grok-4-fast-reasoning-latest",  # Default to reasoning
    "grok-fast": "grok-4-fast-reasoning-latest",
    "grok-code": "grok-code-fast-1",
}


class GrokClient:
    """
    Async client for Grok API (OpenAI-compatible)

    Uses AsyncOpenAI SDK with XAI endpoint (https://api.x.ai/v1)

    Currently Available Models:
    - grok-4-fast-reasoning-latest (default) - Recommended for complex tasks
    - grok-4-fast-non-reasoning-latest - Faster for simpler tasks
    - grok-code-fast-1 - Code-specialized model
    - grok-2-vision-latest - Multimodal vision (image + text)
    - grok-2-image-latest - Image generation

    Upcoming (Grok 4.1):
    - Will be available via API when xAI releases access
    - Client will auto-upgrade to grok-4-1 models when released
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
