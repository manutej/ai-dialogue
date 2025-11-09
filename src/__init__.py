"""
AI Dialogue - Universal Async AI Orchestration Protocol

Enables multi-turn conversations between Claude and Grok with configurable
interaction modes and dynamic workflow capabilities.
"""

__version__ = "1.0.0"

from .protocol import ProtocolEngine, Conversation, Turn
from .dynamic_protocol import DynamicProtocolEngine, CycleConfig
from .intelligent_orchestrator import IntelligentOrchestrator, Subtask, ExecutionStrategy
from .state import StateManager
from .clients.claude import ClaudeClient
from .clients.grok import GrokClient

__all__ = [
    "ProtocolEngine",
    "DynamicProtocolEngine",
    "IntelligentOrchestrator",
    "Conversation",
    "Turn",
    "Subtask",
    "ExecutionStrategy",
    "CycleConfig",
    "StateManager",
    "ClaudeClient",
    "GrokClient",
]
