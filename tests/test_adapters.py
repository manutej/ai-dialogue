"""
Test suite for model adapters

Following TDD - tests written BEFORE implementation
"""

import pytest
from abc import ABC


def test_base_adapter_interface_exists():
    """RED: Test that BaseAdapter interface exists with required methods"""
    from src.adapters.base import BaseAdapter

    # Should be abstract
    assert issubclass(BaseAdapter, ABC)

    # Should have required abstract methods
    required_methods = ['chat', 'capabilities']
    for method in required_methods:
        assert hasattr(BaseAdapter, method), f"BaseAdapter missing {method} method"


def test_base_adapter_cannot_be_instantiated():
    """RED: Test that BaseAdapter is abstract and cannot be instantiated"""
    from src.adapters.base import BaseAdapter

    with pytest.raises(TypeError):
        BaseAdapter()  # Should fail - it's abstract


@pytest.mark.asyncio
async def test_grok_adapter_initialization():
    """RED: Test GrokAdapter can be created with LangChain"""
    from src.adapters.grok_adapter import GrokAdapter

    # Should initialize without error
    adapter = GrokAdapter(api_key="test-key")

    # Should have capabilities
    assert isinstance(adapter.capabilities, list)
    assert len(adapter.capabilities) > 0
    assert "reasoning" in adapter.capabilities


@pytest.mark.asyncio
async def test_grok_adapter_chat_interface():
    """RED: Test GrokAdapter follows BaseAdapter interface"""
    from src.adapters.grok_adapter import GrokAdapter
    from src.adapters.base import BaseAdapter

    adapter = GrokAdapter(api_key="test-key")

    # Should be instance of BaseAdapter
    assert isinstance(adapter, BaseAdapter)

    # Should have chat method
    assert hasattr(adapter, 'chat')
    assert callable(adapter.chat)
