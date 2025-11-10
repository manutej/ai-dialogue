"""
Enhanced Grok API Client with Files, Collections, and Server-Side Tools

Features:
- File upload and analysis (Files API)
- Collections management for knowledge bases
- Server-side tools (web_search, x_search, code_execution)
- Multi-modal chat (text + images + documents)
- Backward compatible with existing GrokClient
"""

import os
import logging
from typing import Dict, Tuple, Optional, List
from pathlib import Path
import base64
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class EnhancedGrokClient:
    """
    Enhanced async client for Grok API

    New features over basic GrokClient:
    - File upload and analysis
    - Collections management
    - Server-side tools (web_search, x_search, code_execution)
    - Multi-modal chat (text + images + documents)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "grok-4-fast"
    ):
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

        # Initialize collections manager (lazy loading)
        self._collections_manager = None

        logger.info(f"Enhanced Grok client initialized with model: {model}")

    @property
    def collections(self):
        """Lazy-load collections manager"""
        if self._collections_manager is None:
            from .collections_manager import CollectionsManager
            self._collections_manager = CollectionsManager(self.api_key)
        return self._collections_manager

    async def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        files: Optional[List[str]] = None,
        server_side_tools: Optional[List[str]] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Enhanced chat with file and tool support

        Args:
            prompt: User prompt
            model: Model to use (grok-4, grok-4-fast, grok-3)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            files: Optional list of file paths to include
            server_side_tools: Optional list of server-side tools
                             ['web_search', 'x_search', 'code_execution']

        Returns:
            (response_text, token_usage_dict)
        """
        use_model = model or self.default_model

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Handle file attachments
        if files:
            content_parts = [{"type": "text", "text": prompt}]

            for file_path in files:
                file_content = Path(file_path).read_bytes()
                encoded = base64.b64encode(file_content).decode('utf-8')

                # Determine MIME type
                suffix = Path(file_path).suffix.lower()
                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                    '.pdf': 'application/pdf',
                    '.txt': 'text/plain',
                    '.csv': 'text/csv',
                    '.md': 'text/markdown',
                }
                mime_type = mime_types.get(suffix, 'application/octet-stream')

                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded}"
                    }
                })

            messages.append({"role": "user", "content": content_parts})
        else:
            messages.append({"role": "user", "content": prompt})

        # Build tools list
        tools = None
        if server_side_tools:
            tools = [{"type": tool} for tool in server_side_tools]

        logger.debug(
            f"Grok request: model={use_model}, temp={temperature}, "
            f"files={len(files) if files else 0}, tools={server_side_tools}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=use_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
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

        Note: Streaming not yet supported with files or tools
        """
        use_model = model or self.default_model

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

    async def chat_with_collection(
        self,
        prompt: str,
        collection_ids: List[str],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        search_top_k: int = 3
    ) -> Tuple[str, Dict]:
        """
        Chat with context from collections

        Args:
            prompt: User query
            collection_ids: Collections to search
            model: Model to use
            temperature: Sampling temperature (lower for factual answers)
            max_tokens: Maximum tokens
            search_top_k: Number of search results to include

        Returns:
            (response_text, metadata_dict)
        """
        use_model = model or self.default_model

        # Get answer from collections
        answer, search_results = await self.collections.chat_with_collections(
            query=prompt,
            collection_ids=collection_ids,
            model=use_model,
            search_top_k=search_top_k
        )

        metadata = {
            "sources": len(search_results),
            "search_results": search_results,
            "collection_ids": collection_ids
        }

        return answer, metadata

    async def analyze_file(
        self,
        file_path: str,
        analysis_prompt: str,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Analyze a single file

        Args:
            file_path: Path to file
            analysis_prompt: Analysis instructions
            model: Model to use

        Returns:
            (analysis_result, token_usage)
        """
        return await self.chat(
            prompt=analysis_prompt,
            model=model,
            files=[file_path],
            temperature=0.3  # Lower temperature for analytical tasks
        )

    async def analyze_files(
        self,
        file_paths: List[str],
        analysis_prompt: str,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Analyze multiple files at once (up to 10 images)

        Args:
            file_paths: List of file paths
            analysis_prompt: Analysis instructions
            model: Model to use

        Returns:
            (analysis_result, token_usage)
        """
        if len(file_paths) > 10:
            raise ValueError(f"Cannot analyze more than 10 files at once (got {len(file_paths)})")

        return await self.chat(
            prompt=analysis_prompt,
            model=model,
            files=file_paths,
            temperature=0.3
        )

    async def research_query(
        self,
        query: str,
        use_web: bool = True,
        use_x: bool = False,
        use_code: bool = False,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Research query using server-side tools

        Args:
            query: Research query
            use_web: Enable web search
            use_x: Enable X (Twitter) search
            use_code: Enable code execution
            model: Model to use (default: grok-4-fast, optimized for tools)

        Returns:
            (research_result, token_usage)
        """
        tools = []
        if use_web:
            tools.append("web_search")
        if use_x:
            tools.append("x_search")
        if use_code:
            tools.append("code_execution")

        if not tools:
            raise ValueError("At least one tool must be enabled")

        return await self.chat(
            prompt=query,
            model=model or "grok-4-fast",  # Optimized for agentic tool use
            server_side_tools=tools,
            temperature=0.3  # Lower temperature for research
        )

    async def close(self):
        """Close async clients"""
        await self.client.close()
        if self._collections_manager:
            await self._collections_manager.close()
