"""
Grok Model Adapter using LangChain

Simple, focused adapter following CONSTITUTION principles.
"""

import os
from typing import Tuple, List
from langchain_openai import ChatOpenAI
from .base import BaseAdapter, TokenUsage


# Model ID mapping (from existing grok.py)
MODEL_IDS = {
    "grok-4": "grok-4-0709",
    "grok-4-0709": "grok-4-0709",
    "grok-3": "grok-3",
    "grok-vision": "grok-2-vision-1212",
    "grok-2-vision-1212": "grok-2-vision-1212",
    "grok-image": "grok-2-image",
    "grok-2-image": "grok-2-image",
}


class GrokAdapter(BaseAdapter):
    """
    Grok model adapter using LangChain.

    Minimal implementation following CONSTITUTION Principle 9: Progressive Complexity
    - Simple use cases are simple
    - Complex customization available but not required
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "grok-4",
        temperature: float = 0.7
    ):
        """
        Initialize Grok adapter.

        Args:
            api_key: XAI API key (or set XAI_API_KEY env var)
            model: Model name (will resolve to actual ID)
            temperature: Sampling temperature
        """
        self.api_key = api_key or os.environ.get("XAI_API_KEY")
        self.model_name = model
        self.resolved_model = MODEL_IDS.get(model, model)
        self.default_temperature = temperature

        # Create LangChain client
        self.client = ChatOpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
            model=self.resolved_model,
            temperature=self.default_temperature
        )

    async def chat(self, prompt: str, **kwargs) -> Tuple[str, TokenUsage]:
        """
        Send chat request via LangChain.

        Args:
            prompt: User message
            **kwargs: Optional overrides (temperature, max_tokens, etc.)

        Returns:
            (response_text, token_usage)
        """
        # Use LangChain's async invoke
        response = await self.client.ainvoke(prompt)

        # Extract token usage if available
        usage = TokenUsage(
            prompt=0,  # LangChain might not always provide this
            completion=0,
            total=0
        )

        # Try to get usage from response metadata
        if hasattr(response, 'response_metadata'):
            token_usage = response.response_metadata.get('token_usage', {})
            usage = TokenUsage(
                prompt=token_usage.get('prompt_tokens', 0),
                completion=token_usage.get('completion_tokens', 0),
                total=token_usage.get('total_tokens', 0)
            )

        return response.content, usage

    @property
    def capabilities(self) -> List[str]:
        """
        Return Grok's capabilities.

        Following CORE-ARCHITECTURE-SPEC.md SC1.2: Model Registry
        """
        return ["reasoning", "analysis", "code"]
