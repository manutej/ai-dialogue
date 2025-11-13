"""
Base Model Adapter Interface

Defines the contract all model adapters must follow.
Keeps implementation simple and focused.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class TokenUsage:
    """Token usage information"""
    prompt: int
    completion: int
    total: int


class BaseAdapter(ABC):
    """
    Abstract base class for all model adapters.

    Following CONSTITUTION.md Principle 1: Model Agnostic by Design
    - Models are configuration, not code
    - Add new model with ≤50 lines of adapter code
    """

    @abstractmethod
    async def chat(self, prompt: str, **kwargs) -> Tuple[str, TokenUsage]:
        """
        Send chat request to model.

        Args:
            prompt: User message
            **kwargs: Model-specific parameters (temperature, max_tokens, etc.)

        Returns:
            (response_text, token_usage)
        """
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        Return list of model capabilities.

        Examples: ["reasoning", "analysis", "code", "vision"]
        """
        pass
