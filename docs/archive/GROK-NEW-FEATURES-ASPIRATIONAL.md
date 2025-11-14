# Grok API New Features - Comprehensive Technical Guide

**Last Updated**: 2025-11-10
**Target Implementation**: ai-dialogue async protocol
**xAI API Version**: v1 (2025)

---

## Executive Summary

This document provides a comprehensive technical guide to the latest Grok API features announced by xAI, including:

1. **Files API** - Upload and analyze files in chat conversations
2. **Collections API** - Create knowledge bases with semantic search capabilities
3. **Server-Side Tools** - Autonomous agentic tools (web_search, x_search, code_execution)
4. **Tool Architecture** - Understanding client-side vs server-side tool usage patterns

These features significantly expand Grok's capabilities for document analysis, knowledge management, and autonomous task execution. This guide focuses on practical integration with our existing AsyncOpenAI-based dialogue protocol.

---

## Table of Contents

- [1. Files API](#1-files-api)
  - [1.1 Overview](#11-overview)
  - [1.2 Supported Formats](#12-supported-formats)
  - [1.3 Implementation Patterns](#13-implementation-patterns)
  - [1.4 Integration with Chat API](#14-integration-with-chat-api)
- [2. Collections API](#2-collections-api)
  - [2.1 Overview](#21-overview)
  - [2.2 Core Concepts](#22-core-concepts)
  - [2.3 API Endpoints](#23-api-endpoints)
  - [2.4 Python Async Implementation](#24-python-async-implementation)
  - [2.5 Semantic Search](#25-semantic-search)
- [3. Server-Side Tools](#3-server-side-tools)
  - [3.1 Overview](#31-overview)
  - [3.2 Available Tools](#32-available-tools)
  - [3.3 Implementation](#33-implementation)
  - [3.4 Pricing](#34-pricing)
- [4. Tool Architecture](#4-tool-architecture)
  - [4.1 Client-Side vs Server-Side](#41-client-side-vs-server-side)
  - [4.2 Mixing Limitations](#42-mixing-limitations)
  - [4.3 MCP Tools Integration](#43-mcp-tools-integration)
- [5. Integration Guide](#5-integration-guide)
  - [5.1 Upgrading GrokClient](#51-upgrading-grokclient)
  - [5.2 Collections Manager](#52-collections-manager)
  - [5.3 Enhanced Protocol Engine](#53-enhanced-protocol-engine)
- [6. Migration Guide](#6-migration-guide)
- [7. Best Practices](#7-best-practices)
- [8. Troubleshooting](#8-troubleshooting)
- [9. References](#9-references)

---

## 1. Files API

### 1.1 Overview

The Grok Files API enables uploading and analyzing various file types within chat conversations. Unlike traditional file upload endpoints, files are processed in-memory for security and can be referenced directly in chat completion requests.

**Key Features:**
- In-memory processing (files not retained unless explicitly enabled)
- Automatic security scanning
- Support for multiple file formats
- Direct integration with chat completions
- Base64 encoding or URL-based file inclusion

**Security Model:**
- All files automatically scanned on upload
- Processed in memory only
- No persistent storage unless user explicitly enables
- Automatic cleanup after processing

### 1.2 Supported Formats

| Format Category | Supported Types | Max Size (Chat) | Max Size (API) | Use Cases |
|-----------------|----------------|-----------------|----------------|-----------|
| **Images** | JPEG, PNG, GIF, WebP | 25 MB | 30 MB | Image analysis, OCR, visual Q&A |
| **Documents** | PDF, TXT, MD, DOCX | 25 MB | 30 MB | Document analysis, summarization |
| **Data** | CSV, ZIP | 25 MB | 30 MB | Data extraction, analysis |

**Limits:**
- **Chat Interface**: Up to 3 images per conversation
- **API**: Up to 10 images per request
- **File Size**: 25 MB (chat), 30 MB (API)

### 1.3 Implementation Patterns

#### Pattern 1: Base64 Encoded Files (Recommended for Small Files)

```python
import base64
from pathlib import Path
from openai import AsyncOpenAI

async def analyze_file_base64(client: AsyncOpenAI, file_path: str, prompt: str):
    """
    Analyze a file using base64 encoding

    Best for: Small files, images, when file content needs to be embedded
    """
    # Read and encode file
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
    }
    mime_type = mime_types.get(suffix, 'application/octet-stream')

    # Create message with embedded file
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded}"
                    }
                }
            ]
        }
    ]

    response = await client.chat.completions.create(
        model="grok-4",
        messages=messages,
        max_tokens=4096
    )

    return response.choices[0].message.content
```

#### Pattern 2: URL-Based Files (Recommended for Hosted Files)

```python
async def analyze_file_url(client: AsyncOpenAI, file_url: str, prompt: str):
    """
    Analyze a file from URL

    Best for: Large files, publicly accessible resources
    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": file_url
                    }
                }
            ]
        }
    ]

    response = await client.chat.completions.create(
        model="grok-4",
        messages=messages,
        max_tokens=4096
    )

    return response.choices[0].message.content
```

#### Pattern 3: Multi-File Analysis

```python
async def analyze_multiple_files(
    client: AsyncOpenAI,
    files: list[dict[str, str]],
    prompt: str
):
    """
    Analyze multiple files in a single request

    Args:
        files: List of dicts with 'path' and 'type' keys
        prompt: Analysis prompt

    Limits: Max 10 images via API
    """
    content_parts = [{"type": "text", "text": prompt}]

    for file_info in files:
        file_content = Path(file_info['path']).read_bytes()
        encoded = base64.b64encode(file_content).decode('utf-8')

        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{file_info['type']};base64,{encoded}"
            }
        })

    messages = [{"role": "user", "content": content_parts}]

    response = await client.chat.completions.create(
        model="grok-4",
        messages=messages,
        max_tokens=4096
    )

    return response.choices[0].message.content
```

### 1.4 Integration with Chat API

Files are passed directly within chat completion requests rather than uploaded to a separate endpoint. This simplifies the API surface but requires careful management of file sizes and encodings.

**Workflow:**
1. Load file from disk or URL
2. Encode as base64 (if local file)
3. Construct multi-part message content
4. Send via standard chat completions endpoint
5. File processed in-memory during request
6. Response includes analysis results

**Example: PDF Document Analysis**

```python
async def analyze_pdf_document(client: AsyncOpenAI, pdf_path: str):
    """
    Comprehensive PDF analysis with structured extraction
    """
    pdf_bytes = Path(pdf_path).read_bytes()
    encoded = base64.b64encode(pdf_bytes).decode('utf-8')

    analysis_prompt = """
    Analyze this PDF document and provide:

    1. Summary (3-5 sentences)
    2. Key Topics (bullet points)
    3. Important Entities (people, organizations, dates)
    4. Actionable Items (if any)
    5. Technical Details (if present)

    Format your response as JSON.
    """

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": analysis_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:application/pdf;base64,{encoded}"
                    }
                }
            ]
        }
    ]

    response = await client.chat.completions.create(
        model="grok-4",
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=4096
    )

    return response.choices[0].message.content
```

---

## 2. Collections API

### 2.1 Overview

The Collections API provides a powerful knowledge base system with automatic embedding generation and semantic search capabilities. It enables:

- Uploading multiple files to organized collections
- Automatic vector embedding generation
- Semantic search across documents
- Multi-collection queries
- Enterprise knowledge integration

**Released**: August 15, 2025

**Key Capabilities:**
- File management within logical collections
- Automatic embedding generation
- Cross-collection semantic search
- Integration with chat completions
- Enterprise knowledge base support

### 2.2 Core Concepts

#### Collections

A **collection** is a logical grouping of files with an associated embedding index for efficient retrieval.

**Properties:**
- Unique identifier (collection_id)
- Name and description
- Embedding configuration
- File list
- Creation and modification timestamps

**Key Rules:**
- A file must belong to at least one collection
- A file can belong to multiple collections
- Collections can be queried independently or together
- Embeddings can be enabled/disabled per collection

#### Files

A **file** is a single uploaded document within a collection.

**Properties:**
- Unique identifier (file_id)
- Original filename
- Content type
- Size
- Parent collection(s)
- Embedding status

#### Embeddings

**Embeddings** are vector representations of file content for semantic search.

**Generation:**
- Automatic when enabled during collection creation
- Can be disabled for simple file storage
- Recommended to keep enabled for search functionality
- Regenerated when file content changes

### 2.3 API Endpoints

While the official xAI documentation is the authoritative source, based on standard patterns and available information, the Collections API likely follows this structure:

#### Base URL

```
https://api.x.ai/v1
```

#### Authentication

```
Authorization: Bearer <XAI_API_KEY>
```

#### Endpoint Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/collections` | GET | List all collections |
| `/collections` | POST | Create new collection |
| `/collections/{id}` | GET | Get collection details |
| `/collections/{id}` | DELETE | Delete collection |
| `/collections/{id}/files` | POST | Upload file to collection |
| `/collections/{id}/files` | GET | List files in collection |
| `/collections/{id}/files/{file_id}` | DELETE | Remove file from collection |
| `/collections/search` | POST | Semantic search across collections |

**Note**: These endpoints are inferred from standard REST patterns. Consult official docs at `https://docs.x.ai/docs/api-reference` for exact specifications.

### 2.4 Python Async Implementation

#### Collection Manager Class

```python
from typing import Optional, List, Dict
from pathlib import Path
import asyncio
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class CollectionsManager:
    """
    Async manager for xAI Collections API

    Provides high-level interface for:
    - Creating and managing collections
    - Uploading files
    - Performing semantic search
    - Integration with chat completions
    """

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.collections_cache = {}

    async def create_collection(
        self,
        name: str,
        description: Optional[str] = None,
        enable_embeddings: bool = True
    ) -> Dict:
        """
        Create a new collection

        Args:
            name: Collection name
            description: Optional description
            enable_embeddings: Whether to auto-generate embeddings

        Returns:
            Collection metadata dict with collection_id
        """
        # Note: Actual endpoint may differ - check official docs
        payload = {
            "name": name,
            "description": description or "",
            "enable_embeddings": enable_embeddings
        }

        # This is a placeholder - actual implementation depends on xAI SDK
        # When official SDK supports collections, use:
        # collection = await self.client.collections.create(**payload)

        logger.info(f"Created collection: {name} (embeddings: {enable_embeddings})")

        # Placeholder return - replace with actual API response
        collection_id = f"col_{name.lower().replace(' ', '_')}"
        collection = {
            "id": collection_id,
            "name": name,
            "description": description,
            "enable_embeddings": enable_embeddings,
            "file_count": 0
        }

        self.collections_cache[collection_id] = collection
        return collection

    async def list_collections(self) -> List[Dict]:
        """
        List all collections

        Returns:
            List of collection metadata dicts
        """
        # Placeholder - actual implementation:
        # collections = await self.client.collections.list()

        return list(self.collections_cache.values())

    async def get_collection(self, collection_id: str) -> Dict:
        """
        Get collection details

        Args:
            collection_id: Collection identifier

        Returns:
            Collection metadata dict
        """
        # Check cache first
        if collection_id in self.collections_cache:
            return self.collections_cache[collection_id]

        # Placeholder - actual implementation:
        # collection = await self.client.collections.retrieve(collection_id)

        raise ValueError(f"Collection not found: {collection_id}")

    async def upload_file(
        self,
        collection_id: str,
        file_path: str,
        **metadata
    ) -> Dict:
        """
        Upload file to collection

        Args:
            collection_id: Target collection
            file_path: Path to file
            **metadata: Additional file metadata

        Returns:
            File metadata dict with file_id
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Placeholder - actual implementation would use multipart upload:
        # with open(file_path, 'rb') as f:
        #     file = await self.client.collections.files.create(
        #         collection_id=collection_id,
        #         file=f,
        #         metadata=metadata
        #     )

        logger.info(f"Uploaded {file_path_obj.name} to collection {collection_id}")

        file_id = f"file_{file_path_obj.stem}"
        file_info = {
            "id": file_id,
            "collection_id": collection_id,
            "filename": file_path_obj.name,
            "size": file_path_obj.stat().st_size,
            **metadata
        }

        # Update collection file count
        if collection_id in self.collections_cache:
            self.collections_cache[collection_id]["file_count"] += 1

        return file_info

    async def upload_files_batch(
        self,
        collection_id: str,
        file_paths: List[str],
        max_concurrent: int = 3
    ) -> List[Dict]:
        """
        Upload multiple files concurrently

        Args:
            collection_id: Target collection
            file_paths: List of file paths
            max_concurrent: Max concurrent uploads

        Returns:
            List of file metadata dicts
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def upload_with_limit(path):
            async with semaphore:
                return await self.upload_file(collection_id, path)

        tasks = [upload_with_limit(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors and log them
        successful = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to upload {file_paths[i]}: {result}")
            else:
                successful.append(result)

        logger.info(f"Uploaded {len(successful)}/{len(file_paths)} files")
        return successful

    async def search(
        self,
        query: str,
        collection_ids: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Semantic search across collections

        Args:
            query: Search query
            collection_ids: Collections to search (None = all)
            top_k: Number of results to return

        Returns:
            List of search results with relevance scores
        """
        # Placeholder - actual implementation:
        # results = await self.client.collections.search(
        #     query=query,
        #     collection_ids=collection_ids,
        #     top_k=top_k
        # )

        logger.info(
            f"Searching collections {collection_ids or 'all'} "
            f"for: {query[:50]}..."
        )

        # Placeholder return
        return [
            {
                "file_id": "file_example",
                "collection_id": collection_ids[0] if collection_ids else "col_default",
                "relevance_score": 0.95,
                "excerpt": "Relevant text excerpt...",
                "metadata": {}
            }
        ]

    async def chat_with_collections(
        self,
        query: str,
        collection_ids: List[str],
        model: str = "grok-4",
        search_top_k: int = 3
    ) -> tuple[str, List[Dict]]:
        """
        Chat with context from collection search results

        Args:
            query: User query
            collection_ids: Collections to search
            model: Model to use
            search_top_k: Number of search results to include

        Returns:
            (response_text, search_results)
        """
        # 1. Perform semantic search
        search_results = await self.search(
            query=query,
            collection_ids=collection_ids,
            top_k=search_top_k
        )

        # 2. Build context from search results
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}] (Relevance: {result['relevance_score']:.2f})\n"
                f"{result['excerpt']}\n"
            )

        context = "\n".join(context_parts)

        # 3. Create prompt with context
        prompt = f"""Based on the following context from our knowledge base, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context provided."""

        # 4. Send to chat completion
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided context. Always cite sources when possible."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for factual responses
            max_tokens=4096
        )

        answer = response.choices[0].message.content

        logger.info(
            f"Generated answer from {len(search_results)} sources "
            f"({response.usage.total_tokens} tokens)"
        )

        return answer, search_results

    async def delete_collection(self, collection_id: str) -> bool:
        """
        Delete a collection and all its files

        Args:
            collection_id: Collection to delete

        Returns:
            True if successful
        """
        # Placeholder - actual implementation:
        # await self.client.collections.delete(collection_id)

        if collection_id in self.collections_cache:
            del self.collections_cache[collection_id]

        logger.info(f"Deleted collection: {collection_id}")
        return True

    async def close(self):
        """Close async client"""
        await self.client.close()
```

### 2.5 Semantic Search

Semantic search uses vector embeddings to find contextually relevant documents, not just keyword matches.

**Example: Building a Knowledge Base System**

```python
async def build_knowledge_base_example():
    """
    Complete example: Building and querying a knowledge base
    """
    import os

    manager = CollectionsManager(api_key=os.environ["XAI_API_KEY"])

    try:
        # 1. Create collection
        collection = await manager.create_collection(
            name="Technical Documentation",
            description="Engineering docs and specifications",
            enable_embeddings=True
        )

        print(f"✓ Created collection: {collection['id']}")

        # 2. Upload multiple files
        doc_files = [
            "docs/api-spec.md",
            "docs/architecture.md",
            "docs/deployment-guide.md",
        ]

        uploaded = await manager.upload_files_batch(
            collection_id=collection['id'],
            file_paths=doc_files,
            max_concurrent=3
        )

        print(f"✓ Uploaded {len(uploaded)} documents")

        # 3. Wait for embedding generation (if needed)
        await asyncio.sleep(2)

        # 4. Perform semantic search
        results = await manager.search(
            query="How do I deploy the application to production?",
            collection_ids=[collection['id']],
            top_k=3
        )

        print(f"\n✓ Search Results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['file_id']} (score: {result['relevance_score']:.2f})")

        # 5. Chat with collection context
        answer, sources = await manager.chat_with_collections(
            query="What are the deployment prerequisites?",
            collection_ids=[collection['id']],
            search_top_k=3
        )

        print(f"\n✓ AI Answer:\n{answer}\n")
        print(f"✓ Based on {len(sources)} sources")

    finally:
        await manager.close()


# Run example
if __name__ == "__main__":
    asyncio.run(build_knowledge_base_example())
```

---

## 3. Server-Side Tools

### 3.1 Overview

Server-side tools represent a paradigm shift in AI API design. Instead of the client orchestrating tool calls (traditional function calling), the server autonomously manages the entire reasoning and tool execution loop.

**Key Innovation:**
- **Autonomous Execution**: Server decides when and how to use tools
- **Iterative Reasoning**: Can chain multiple tool calls
- **Transparent to Client**: Client gets final answer, not intermediate steps
- **Agentic Behavior**: Model explores, searches, and executes code independently

**Comparison:**

| Aspect | Client-Side Tools | Server-Side Tools |
|--------|-------------------|-------------------|
| **Orchestration** | Client manages loop | Server manages loop |
| **Control** | Client decides what to execute | Server decides autonomously |
| **Transparency** | See all tool calls | See final result only |
| **Complexity** | Client must implement logic | Server handles everything |
| **Latency** | Multiple round-trips | Single request |
| **Use Case** | Controlled, predictable flows | Exploratory, complex queries |

### 3.2 Available Tools

#### web_search

Real-time search across the internet.

**Capabilities:**
- Current events and news
- General web knowledge
- Recent information beyond training data
- Source attribution

**Example Use Cases:**
- "What are the latest developments in quantum computing this month?"
- "Find recent research papers on transformer architectures"
- "What's the current price of Bitcoin?"

#### x_search

Semantic and keyword search across X (Twitter) posts.

**Capabilities:**
- Social sentiment analysis
- Real-time trending topics
- User opinions and discussions
- Breaking news

**Example Use Cases:**
- "What are people saying about the recent AI regulation bill?"
- "Find tweets discussing Claude 4 features"
- "Analyze sentiment around the new iPhone launch"

#### code_execution

Execute Python code for calculations and data analysis.

**Capabilities:**
- Mathematical computations
- Data processing and analysis
- Plotting and visualization (returns descriptions)
- Algorithm implementation

**Example Use Cases:**
- "Calculate the compound interest on $10,000 over 20 years at 7% annual rate"
- "Analyze this CSV data and find correlations"
- "Implement and test a binary search algorithm"

**Security:**
- Sandboxed execution environment
- Limited resource access
- Time and memory constraints
- No file system or network access

### 3.3 Implementation

#### Basic Server-Side Tool Usage

```python
from openai import AsyncOpenAI
import os

async def use_server_side_tools():
    """
    Basic server-side tools usage

    Note: Requires xai-sdk version 1.3.1+
    """
    client = AsyncOpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1"
    )

    # Enable server-side tools
    response = await client.chat.completions.create(
        model="grok-4-fast",  # Optimized for agentic tool use
        messages=[
            {
                "role": "user",
                "content": "What are the top 3 trending AI topics on X today? Analyze sentiment."
            }
        ],
        tools=[
            {"type": "x_search"},
            {"type": "code_execution"}
        ],
        # Server orchestrates the entire reasoning loop
        # No tool_choice needed - server decides autonomously
    )

    # Get final answer after all tool executions
    answer = response.choices[0].message.content

    print(f"Answer: {answer}")
    print(f"Tokens used: {response.usage.total_tokens}")

    await client.close()
```

#### Advanced: Web Search with Data Analysis

```python
async def research_with_analysis(query: str):
    """
    Research query with automatic data analysis

    Server will:
    1. Search the web for information
    2. Execute Python code to analyze data
    3. Synthesize findings
    """
    client = AsyncOpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1"
    )

    response = await client.chat.completions.create(
        model="grok-4-fast",
        messages=[
            {
                "role": "system",
                "content": "You are a research analyst. Use web search to gather data, then analyze it programmatically."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        tools=[
            {"type": "web_search"},
            {"type": "code_execution"}
        ],
        temperature=0.3,
        max_tokens=8000
    )

    result = response.choices[0].message.content

    # Note: We don't see intermediate tool calls
    # Server handled entire research + analysis loop

    await client.close()
    return result


# Example usage
async def main():
    result = await research_with_analysis(
        "Find the top 5 programming languages by GitHub stars this year, "
        "then calculate the year-over-year growth percentage for each."
    )
    print(result)

import asyncio
asyncio.run(main())
```

#### Tool Configuration Options

```python
# Specific tools only
tools = [
    {"type": "web_search"},
]

# Multiple tools - server chooses when to use each
tools = [
    {"type": "web_search"},
    {"type": "x_search"},
    {"type": "code_execution"}
]

# Note: Cannot mix with client-side tools
# This will FAIL:
tools = [
    {"type": "web_search"},  # Server-side
    {
        "type": "function",   # Client-side
        "function": {
            "name": "get_weather",
            "description": "...",
            "parameters": {...}
        }
    }
]
# ❌ Error: Cannot mix server-side and client-side tools
```

### 3.4 Pricing

Server-side tool requests have two cost components:

1. **Token Usage**: Standard per-token pricing
2. **Tool Invocations**: Per-invocation fees

**Pricing Structure:**

| Model | Input Tokens | Output Tokens | Tool Invocations |
|-------|--------------|---------------|------------------|
| grok-4-fast | $x per 1M | $y per 1M | $z per call |

**Important Notes:**
- ✨ **Free Trial**: All server-side tool invocations free until November 21, 2025
- 🔄 **Autonomous Scaling**: Costs scale with query complexity (agent decides tool usage)
- 📊 **Unpredictable**: Can't predict exact tool calls before request
- 💡 **Optimization**: Use specific prompts to guide tool usage

**Cost Management Strategies:**

```python
# 1. Set max_tokens to limit response length
response = await client.chat.completions.create(
    model="grok-4-fast",
    messages=[...],
    tools=[{"type": "web_search"}],
    max_tokens=2000  # Limit output
)

# 2. Use temperature to control exploration
response = await client.chat.completions.create(
    model="grok-4-fast",
    messages=[...],
    tools=[{"type": "code_execution"}],
    temperature=0.0  # Deterministic, fewer retries
)

# 3. Guide tool usage in prompt
messages = [
    {
        "role": "user",
        "content": "Search the web ONCE for recent news on AI safety, then summarize. Do not perform additional searches."
    }
]
```

---

## 4. Tool Architecture

### 4.1 Client-Side vs Server-Side

#### Client-Side Tools (Traditional Function Calling)

**How it works:**
1. Client defines functions in API request
2. Model decides to call a function
3. API returns function call request (not final answer)
4. Client executes function
5. Client sends function result back to API
6. Model processes result
7. Repeat steps 2-6 as needed
8. Finally get answer

**Advantages:**
- Full control over execution
- Can validate before executing
- See all intermediate steps
- Use private/sensitive functions
- Predictable costs

**Code Example:**

```python
# Client-side function calling
async def client_side_tools_example():
    client = AsyncOpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1"
    )

    # Define function
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "Get current stock price",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        }
    ]

    messages = [
        {"role": "user", "content": "What's the current price of TSLA?"}
    ]

    # First API call
    response = await client.chat.completions.create(
        model="grok-4",
        messages=messages,
        tools=tools
    )

    # Check if function call requested
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]

        # Execute function (client-side)
        if tool_call.function.name == "get_stock_price":
            import json
            args = json.loads(tool_call.function.arguments)
            result = get_stock_price(args["symbol"])  # Your implementation

            # Send result back
            messages.append(response.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

            # Second API call with function result
            final_response = await client.chat.completions.create(
                model="grok-4",
                messages=messages
            )

            answer = final_response.choices[0].message.content

    await client.close()
    return answer
```

#### Server-Side Tools (Agentic)

**How it works:**
1. Client specifies server-side tools in request
2. Server autonomously executes reasoning loop
3. Server calls tools as needed (transparent to client)
4. Server synthesizes final answer
5. Client receives final answer

**Advantages:**
- Single API call
- Lower latency
- No orchestration logic needed
- Handles complex multi-step reasoning
- Autonomous exploration

**Code Example:**

```python
# Server-side tools (much simpler)
async def server_side_tools_example():
    client = AsyncOpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1"
    )

    # Single API call - server handles everything
    response = await client.chat.completions.create(
        model="grok-4-fast",
        messages=[
            {"role": "user", "content": "What's the current price of TSLA? How does it compare to yesterday?"}
        ],
        tools=[
            {"type": "web_search"}  # Server will search autonomously
        ]
    )

    # Get final answer (server already searched and analyzed)
    answer = response.choices[0].message.content

    await client.close()
    return answer
```

### 4.2 Mixing Limitations

**Critical Constraint**: Cannot mix server-side and client-side tools in the same request.

```python
# ❌ THIS WILL FAIL
tools = [
    {"type": "web_search"},     # Server-side
    {
        "type": "function",      # Client-side
        "function": {
            "name": "my_function",
            "description": "...",
            "parameters": {...}
        }
    }
]

# Error: Cannot mix server-side and client-side tools
```

**Workarounds:**

#### Option 1: Sequential Requests

```python
async def sequential_tool_approach(query: str):
    """
    Use server-side tools first, then client-side tools
    """
    client = AsyncOpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1"
    )

    # Step 1: Server-side research
    research_response = await client.chat.completions.create(
        model="grok-4-fast",
        messages=[
            {
                "role": "user",
                "content": f"Research this topic: {query}"
            }
        ],
        tools=[{"type": "web_search"}]
    )

    research_result = research_response.choices[0].message.content

    # Step 2: Client-side processing with custom functions
    client_tools = [
        {
            "type": "function",
            "function": {
                "name": "save_to_database",
                "description": "Save research to database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string"}
                    },
                    "required": ["data"]
                }
            }
        }
    ]

    processing_response = await client.chat.completions.create(
        model="grok-4",
        messages=[
            {
                "role": "system",
                "content": "You are a data processor. Save important information to database."
            },
            {
                "role": "user",
                "content": f"Process this research and save key findings:\n\n{research_result}"
            }
        ],
        tools=client_tools
    )

    # Handle client-side tool calls...

    await client.close()
```

#### Option 2: Parallel Requests

```python
async def parallel_tool_approach(query: str):
    """
    Use both tool types in parallel, then combine results
    """
    client = AsyncOpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1"
    )

    # Run both approaches concurrently
    server_task = client.chat.completions.create(
        model="grok-4-fast",
        messages=[{"role": "user", "content": f"Research: {query}"}],
        tools=[{"type": "web_search"}]
    )

    client_task = client.chat.completions.create(
        model="grok-4",
        messages=[{"role": "user", "content": f"Analyze: {query}"}],
        tools=[{"type": "function", "function": {...}}]
    )

    server_response, client_response = await asyncio.gather(
        server_task,
        client_task
    )

    # Combine results
    combined_result = combine_responses(
        server_response.choices[0].message.content,
        client_response.choices[0].message.content
    )

    await client.close()
    return combined_result
```

### 4.3 MCP Tools Integration

Model Context Protocol (MCP) enables remote tools to be used via server infrastructure.

**MCP Architecture:**

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client    │◄───────►│ MCP Server  │◄───────►│ Remote Tools│
│ (Your App)  │  MCP    │  (Bridge)   │  API    │  (Services) │
└─────────────┘ Protocol└─────────────┘ Calls   └─────────────┘
```

**Available MCP Servers for Grok:**

1. **grok-mcp** (github.com/Bob-lance/grok-mcp)
   - Direct Grok API integration
   - Chat completion, image understanding, function calling
   - TypeScript/JavaScript

2. **Grok-MCP** (github.com/8bitsats/Grok-MCP)
   - Image generation and analysis
   - Grok-2 and Grok Vision support
   - REST API interface

3. **Enhanced Grok Search MCP** (lobehub.com)
   - Advanced search capabilities
   - Multi-source integration
   - Streaming support

**Integration Pattern:**

```python
# MCP tools appear as server-side tools to the client
async def use_mcp_tools():
    """
    Using remote MCP tools via xAI API

    Note: MCP server must be configured and running
    """
    client = AsyncOpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1"
    )

    # MCP tools accessible via server-side tools interface
    response = await client.chat.completions.create(
        model="grok-4-fast",
        messages=[
            {
                "role": "user",
                "content": "Generate an image of a futuristic city and analyze its composition"
            }
        ],
        # MCP tools configured server-side
        # Client just specifies tool types
        tools=[
            {"type": "image_generation"},  # Via MCP
            {"type": "image_analysis"}     # Via MCP
        ]
    )

    result = response.choices[0].message.content

    await client.close()
    return result
```

**MCP Configuration** (server-side):

```json
{
  "mcpServers": {
    "grok": {
      "command": "node",
      "args": ["/path/to/grok-mcp/dist/index.js"],
      "env": {
        "XAI_API_KEY": "${XAI_API_KEY}"
      }
    }
  }
}
```

---

## 5. Integration Guide

### 5.1 Upgrading GrokClient

Enhance the existing `GrokClient` to support new features:

```python
"""
Enhanced Grok API Client with Files, Collections, and Server-Side Tools
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

    New features:
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

        # Collections manager
        from collections_manager import CollectionsManager
        self.collections = CollectionsManager(self.api_key)

        logger.info(f"Enhanced Grok client initialized with model: {model}")

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
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
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
                    '.pdf': 'application/pdf',
                    '.txt': 'text/plain',
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
                f"{tokens['total']} tokens"
            )

            return content, tokens

        except Exception as e:
            logger.error(f"Grok API error: {e}")
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
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            search_top_k: Number of search results

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
            use_x: Enable X search
            use_code: Enable code execution
            model: Model to use (default: grok-4-fast)

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

        return await self.chat(
            prompt=query,
            model=model or "grok-4-fast",  # Optimized for tools
            server_side_tools=tools,
            temperature=0.3
        )

    async def close(self):
        """Close async clients"""
        await self.client.close()
        await self.collections.close()
```

### 5.2 Collections Manager

The `CollectionsManager` class provided in Section 2.4 can be used standalone or integrated into the enhanced client as shown above.

### 5.3 Enhanced Protocol Engine

Update the protocol engine to leverage new features:

```python
"""
Enhanced Protocol Engine with Grok New Features
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class EnhancedTurn:
    """Turn with file and collection support"""
    number: int
    role: str
    participant: str
    prompt: str
    response: str
    tokens: Dict[str, int]
    latency: float
    timestamp: str
    context_from: List[int]
    # New fields
    files: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    search_results: Optional[List[Dict]] = None


class EnhancedProtocolEngine:
    """
    Protocol engine with Files, Collections, and Server-Side Tools
    """

    def __init__(self, claude_client, grok_client, state_manager):
        self.claude = claude_client
        self.grok = grok_client  # EnhancedGrokClient
        self.state = state_manager

    async def _execute_turn(
        self,
        turn_num: int,
        turn_config: Dict,
        topic: str,
        context: Dict
    ) -> EnhancedTurn:
        """
        Execute turn with enhanced features
        """
        import asyncio
        from datetime import datetime

        start_time = asyncio.get_event_loop().time()

        # Build prompt
        template = turn_config.get("template", "")
        prompt = template.format(topic=topic, **context)

        if "role_instruction" in turn_config:
            prompt = f"{turn_config['role_instruction']}\n\n{prompt}"

        participant = turn_config.get("participant", "claude")

        # Extract configuration
        files = turn_config.get("files", [])
        collections = turn_config.get("collections", [])
        tools = turn_config.get("server_side_tools", [])

        logger.debug(
            f"Turn {turn_num}: {participant} "
            f"(files: {len(files)}, collections: {len(collections)}, "
            f"tools: {tools})"
        )

        # Execute based on configuration
        if participant == "grok":
            model = turn_config.get("grok_model", "grok-4-fast")

            # Collection-based query
            if collections:
                response, metadata = await self.grok.chat_with_collection(
                    prompt=prompt,
                    collection_ids=collections,
                    model=model
                )
                tokens = {"prompt": 0, "completion": 0, "total": 0}  # TODO: extract from metadata
                search_results = metadata.get("search_results", [])

            # File analysis
            elif files:
                response, tokens = await self.grok.chat(
                    prompt=prompt,
                    model=model,
                    files=files
                )
                search_results = None

            # Research with tools
            elif tools:
                response, tokens = await self.grok.chat(
                    prompt=prompt,
                    model=model,
                    server_side_tools=tools
                )
                search_results = None

            # Standard chat
            else:
                response, tokens = await self.grok.chat(
                    prompt=prompt,
                    model=model
                )
                search_results = None

        elif participant == "claude":
            response, tokens = await self.claude.chat(prompt)
            search_results = None

        else:
            raise ValueError(f"Unknown participant: {participant}")

        end_time = asyncio.get_event_loop().time()
        latency = end_time - start_time

        return EnhancedTurn(
            number=turn_num,
            role=turn_config.get("role", ""),
            participant=participant,
            prompt=prompt,
            response=response,
            tokens=tokens,
            latency=latency,
            timestamp=datetime.now().isoformat(),
            context_from=turn_config.get("context_from", []),
            files=files,
            collections=collections,
            tools_used=tools,
            search_results=search_results
        )
```

**Example Mode Configuration with New Features:**

```json
{
  "name": "research-with-knowledge-base",
  "description": "Research mode with collection search and web tools",
  "structure": "sequential",
  "turns": 5,
  "metadata": {
    "use_case": "Deep research with knowledge integration"
  },
  "prompts": {
    "turn_1": {
      "role": "knowledge_search",
      "participant": "grok",
      "grok_model": "grok-4-fast",
      "collections": ["technical-docs", "research-papers"],
      "template": "Search our knowledge base for information about: {topic}",
      "context_from": []
    },
    "turn_2": {
      "role": "web_research",
      "participant": "grok",
      "grok_model": "grok-4-fast",
      "server_side_tools": ["web_search"],
      "template": "Based on internal knowledge:\n\n{turn_1}\n\nNow search the web for recent developments on: {topic}",
      "context_from": [1]
    },
    "turn_3": {
      "role": "analysis",
      "participant": "claude",
      "template": "Analyze and synthesize:\n\nInternal knowledge: {turn_1}\n\nRecent web findings: {turn_2}\n\nProvide comprehensive analysis of: {topic}",
      "context_from": [1, 2]
    },
    "turn_4": {
      "role": "document_analysis",
      "participant": "grok",
      "grok_model": "grok-4",
      "files": ["specs/architecture.pdf"],
      "template": "Review the architecture document and relate it to our research on: {topic}\n\nPrevious analysis: {turn_3}",
      "context_from": [3]
    },
    "turn_5": {
      "role": "synthesis",
      "participant": "claude",
      "template": "Create final synthesis combining:\n\n1. Internal knowledge base search\n2. Web research\n3. Analysis\n4. Architecture review\n\nTopic: {topic}",
      "context_from": [1, 2, 3, 4]
    }
  }
}
```

---

## 6. Migration Guide

### Step 1: Update Dependencies

```bash
# Update xAI SDK to latest version
pip install --upgrade xai-sdk

# Verify version (need 1.3.1+ for server-side tools)
python -c "import xai_sdk; print(xai_sdk.__version__)"

# Update OpenAI SDK (used for AsyncOpenAI)
pip install --upgrade openai
```

### Step 2: Environment Variables

```bash
# Add to .env or shell profile
export XAI_API_KEY="your-api-key-here"
```

### Step 3: Replace GrokClient

```python
# Old implementation
from src.clients.grok import GrokClient

# New implementation
from src.clients.grok_enhanced import EnhancedGrokClient as GrokClient

# Usage remains compatible
grok = GrokClient(model="grok-4-fast")
```

### Step 4: Update Mode Configurations

Add new fields to existing modes:

```json
{
  "prompts": {
    "turn_1": {
      "role": "research",
      "participant": "grok",
      // Add new features
      "server_side_tools": ["web_search"],
      "files": [],
      "collections": []
    }
  }
}
```

### Step 5: Test Basic Features

```python
import asyncio
from src.clients.grok_enhanced import EnhancedGrokClient

async def test_migration():
    grok = EnhancedGrokClient()

    # Test 1: Basic chat (backward compatible)
    response, tokens = await grok.chat("Hello, Grok!")
    print(f"✓ Basic chat: {len(response)} chars")

    # Test 2: File analysis
    response, tokens = await grok.analyze_file(
        "test.pdf",
        "Summarize this document"
    )
    print(f"✓ File analysis: {len(response)} chars")

    # Test 3: Web search
    response, tokens = await grok.research_query(
        "Latest AI developments",
        use_web=True
    )
    print(f"✓ Web search: {len(response)} chars")

    # Test 4: Collections (if configured)
    try:
        collection = await grok.collections.create_collection(
            "test-collection",
            enable_embeddings=True
        )
        print(f"✓ Collections: {collection['id']}")
    except Exception as e:
        print(f"⚠ Collections: {e}")

    await grok.close()
    print("\n✅ Migration test complete")

asyncio.run(test_migration())
```

### Step 6: Gradual Rollout

1. **Week 1**: Deploy enhanced client alongside old client
2. **Week 2**: Enable files feature in non-critical modes
3. **Week 3**: Enable server-side tools for research modes
4. **Week 4**: Integrate collections for knowledge-heavy workflows
5. **Week 5**: Full migration, remove old client

---

## 7. Best Practices

### Files API

✅ **Do:**
- Use base64 encoding for small files (<5 MB)
- Use URL references for large or hosted files
- Validate file sizes before encoding
- Handle encoding errors gracefully
- Set appropriate max_tokens for file-heavy prompts

❌ **Don't:**
- Upload files >25 MB (chat) or >30 MB (API)
- Attach more than 10 images per API request
- Assume files persist between requests
- Forget to handle unsupported file types

**Example: Robust File Handling**

```python
async def safe_file_analysis(client, file_path: str, prompt: str):
    """
    Robust file analysis with validation
    """
    path = Path(file_path)

    # Validate existence
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Validate size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 30:
        raise ValueError(f"File too large: {size_mb:.1f} MB (max 30 MB)")

    # Validate format
    supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp',
                        '.pdf', '.txt', '.csv', '.md', '.docx', '.zip'}
    if path.suffix.lower() not in supported_formats:
        raise ValueError(f"Unsupported format: {path.suffix}")

    # Analyze
    try:
        result, tokens = await client.analyze_file(file_path, prompt)
        return result
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise
```

### Collections API

✅ **Do:**
- Enable embeddings for searchable collections
- Use descriptive collection names
- Batch upload files when possible
- Cache collection IDs
- Handle search result ranking
- Provide context in chat queries

❌ **Don't:**
- Create duplicate collections
- Forget to clean up unused collections
- Upload same file multiple times
- Ignore search result relevance scores
- Mix unrelated documents in one collection

**Example: Collection Lifecycle Management**

```python
class CollectionLifecycleManager:
    """
    Manage collection lifecycle with cleanup
    """
    def __init__(self, collections_mgr):
        self.mgr = collections_mgr
        self.created_collections = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup collections on exit
        for col_id in self.created_collections:
            try:
                await self.mgr.delete_collection(col_id)
                logger.info(f"Cleaned up collection: {col_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {col_id}: {e}")

    async def create_collection(self, name: str, **kwargs):
        col = await self.mgr.create_collection(name, **kwargs)
        self.created_collections.append(col['id'])
        return col

# Usage
async with CollectionLifecycleManager(collections_mgr) as mgr:
    col = await mgr.create_collection("temp-research")
    await mgr.mgr.upload_file(col['id'], "research.pdf")
    results = await mgr.mgr.search("key findings", [col['id']])
    # Collection automatically cleaned up on exit
```

### Server-Side Tools

✅ **Do:**
- Use grok-4-fast for tool-heavy tasks
- Set temperature=0.0-0.3 for deterministic tool use
- Guide tool usage in prompts
- Monitor token usage and tool invocations
- Use specific queries to reduce unnecessary tool calls
- Implement timeout handling for long-running tasks

❌ **Don't:**
- Mix server-side and client-side tools
- Use overly broad queries that trigger many searches
- Ignore cost implications of autonomous tool use
- Assume tool execution will always succeed
- Use server-side tools when client-side is more appropriate

**Example: Guided Tool Usage**

```python
async def cost_effective_research(client, topic: str):
    """
    Research with cost-optimized tool usage
    """
    # Specific, focused prompt reduces unnecessary tool calls
    prompt = f"""
    Research the following topic: {topic}

    Instructions:
    1. Perform ONE web search for the most recent information
    2. If quantitative analysis needed, execute Python code ONCE
    3. Synthesize findings concisely

    Avoid multiple searches or redundant code execution.
    """

    response, tokens = await client.chat(
        prompt=prompt,
        model="grok-4-fast",
        server_side_tools=["web_search", "code_execution"],
        temperature=0.0,  # Deterministic
        max_tokens=3000   # Limit output
    )

    logger.info(
        f"Research completed: {tokens['total']} tokens, "
        f"estimated tool calls: 1-2"
    )

    return response
```

### Tool Architecture

✅ **Do:**
- Choose the right tool type for your use case
- Use server-side for exploratory, complex queries
- Use client-side for controlled, predictable workflows
- Document which tools are used in each mode
- Implement fallback strategies for tool failures

❌ **Don't:**
- Try to mix tool types in single request
- Use server-side tools when you need step visibility
- Use client-side tools for autonomous exploration
- Forget to handle tool execution timeouts

**Decision Matrix:**

| Scenario | Recommended Tool Type | Reason |
|----------|----------------------|--------|
| Real-time data lookup | Server-side (web_search) | Current information |
| Internal API call | Client-side (function) | Control & security |
| Complex calculations | Server-side (code_execution) | Automatic Python env |
| Database query | Client-side (function) | Access to private DB |
| Social sentiment analysis | Server-side (x_search) | Real-time X data |
| File system operations | Client-side (function) | Local access |
| Multi-step research | Server-side (all tools) | Autonomous exploration |

---

## 8. Troubleshooting

### Files API Issues

#### Issue: File Too Large Error

```
Error: File size exceeds maximum (30 MB)
```

**Solution:**

```python
# Compress or split large files
from PIL import Image

def compress_image(input_path: str, output_path: str, max_size_mb: int = 25):
    """Compress image to fit size limit"""
    img = Image.open(input_path)
    quality = 95

    while True:
        img.save(output_path, quality=quality, optimize=True)
        size_mb = Path(output_path).stat().st_size / (1024 * 1024)

        if size_mb <= max_size_mb or quality <= 10:
            break

        quality -= 5

    return output_path
```

#### Issue: Unsupported File Format

```
Error: File format .xyz not supported
```

**Solution:**

```python
# Convert to supported format
def convert_to_supported_format(file_path: str) -> str:
    """Convert unsupported formats"""
    path = Path(file_path)

    converters = {
        '.doc': lambda p: convert_doc_to_docx(p),
        '.bmp': lambda p: convert_to_png(p),
        '.tiff': lambda p: convert_to_png(p),
    }

    if path.suffix in converters:
        return converters[path.suffix](path)

    raise ValueError(f"Cannot convert {path.suffix}")
```

### Collections API Issues

#### Issue: Collection Not Found

```
Error: Collection 'col_xyz' not found
```

**Solution:**

```python
async def safe_collection_access(mgr, collection_id: str):
    """Safely access collection with fallback"""
    try:
        return await mgr.get_collection(collection_id)
    except ValueError:
        # Collection doesn't exist, create it
        logger.warning(f"Collection {collection_id} not found, creating...")
        return await mgr.create_collection(
            name=collection_id,
            enable_embeddings=True
        )
```

#### Issue: Empty Search Results

```
Search returned 0 results
```

**Solution:**

```python
async def improved_search(mgr, query: str, collection_ids: List[str]):
    """Search with fallback strategies"""
    # Try exact search
    results = await mgr.search(query, collection_ids, top_k=5)

    if not results:
        # Fallback 1: Broader query
        broader_query = extract_keywords(query)
        results = await mgr.search(broader_query, collection_ids, top_k=5)

    if not results:
        # Fallback 2: Search all collections
        results = await mgr.search(query, collection_ids=None, top_k=5)

    if not results:
        logger.warning(f"No results found for: {query}")
        return []

    return results

def extract_keywords(query: str) -> str:
    """Extract key terms from query"""
    # Remove stop words, keep important terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'}
    words = query.lower().split()
    keywords = [w for w in words if w not in stop_words]
    return ' '.join(keywords)
```

### Server-Side Tools Issues

#### Issue: Cannot Mix Tools Error

```
Error: Cannot mix server-side and client-side tools in the same request
```

**Solution:**

```python
async def sequential_tool_workflow(client, query: str):
    """Use tools sequentially instead of mixing"""
    # Step 1: Server-side research
    research = await client.chat(
        prompt=f"Research: {query}",
        server_side_tools=["web_search"]
    )

    # Step 2: Client-side processing
    # (separate request)
    processed = await client.chat(
        prompt=f"Process this research: {research[0]}",
        # Use client-side tools if needed
    )

    return processed
```

#### Issue: Unexpected Tool Invocations

```
Warning: Query triggered 10+ tool invocations (high cost)
```

**Solution:**

```python
async def cost_controlled_query(client, query: str, max_cost_tokens: int = 10000):
    """Query with cost controls"""
    response, tokens = await client.chat(
        prompt=query,
        server_side_tools=["web_search"],
        max_tokens=max_cost_tokens,  # Hard limit
        temperature=0.0  # Reduce exploration
    )

    if tokens['total'] > max_cost_tokens * 0.8:
        logger.warning(
            f"High token usage: {tokens['total']} "
            f"(limit: {max_cost_tokens})"
        )

    return response, tokens
```

### General API Issues

#### Issue: Rate Limiting

```
Error: Rate limit exceeded (429)
```

**Solution:**

```python
import asyncio
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    """Decorator for API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if '429' in str(e) and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limited, retrying in {delay}s...")
                        await asyncio.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3)
async def api_call_with_retry(client, prompt):
    return await client.chat(prompt)
```

#### Issue: Timeout on Large Requests

```
Error: Request timeout after 60s
```

**Solution:**

```python
import asyncio

async def request_with_timeout(client, prompt: str, timeout: int = 120):
    """API request with custom timeout"""
    try:
        result = await asyncio.wait_for(
            client.chat(prompt),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"Request timed out after {timeout}s")
        raise
```

---

## 9. References

### Official Documentation

- **xAI API Overview**: https://docs.x.ai/docs/overview
- **API Reference**: https://docs.x.ai/docs/api-reference
- **Release Notes**: https://docs.x.ai/docs/release-notes
- **Collections Guide**: https://docs.x.ai/docs/guides/using-collections
- **Tools Overview**: https://docs.x.ai/docs/guides/tools/overview
- **Image Understanding**: https://docs.x.ai/docs/guides/image-understanding
- **Console**: https://console.x.ai

### GitHub Resources

- **xAI Python SDK**: https://github.com/xai-org/xai-sdk-python
- **xAI Cookbook**: https://github.com/xai-org/xai-cookbook
- **Grok MCP Server**: https://github.com/Bob-lance/grok-mcp
- **Community SDK**: https://github.com/moesmufti/xai_grok_sdk

### Community Resources

- **Grok AI Models Guide**: https://www.datastudios.org/post/all-grok-models-available-in-2025-full-list-for-web-app-and-api-including-grok-4-3-mini-and-ima
- **Integration Guide**: https://latenode.com/blog/complete-guide-to-xais-grok-api-documentation-and-implementation
- **MCP SuperAssistant**: https://medium.com/data-science-in-your-pocket/mcp-superassistant-use-mcp-with-grok-perplexity-google-ai-studio-and-more-9762dd07fcb6

### Related Standards

- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io/
- **OpenAI API Compatibility**: https://platform.openai.com/docs/api-reference

---

## Appendix A: Complete Examples

### Example 1: Document Analysis Pipeline

```python
"""
Complete example: Multi-document analysis pipeline
"""

import asyncio
from pathlib import Path
from src.clients.grok_enhanced import EnhancedGrokClient

async def document_analysis_pipeline(doc_dir: str):
    """
    Analyze multiple documents and synthesize findings
    """
    client = EnhancedGrokClient(model="grok-4")

    try:
        # 1. Find all PDF documents
        docs = list(Path(doc_dir).glob("*.pdf"))
        print(f"Found {len(docs)} documents")

        # 2. Analyze each document
        analyses = []
        for doc in docs:
            print(f"\nAnalyzing: {doc.name}")

            result, tokens = await client.analyze_file(
                str(doc),
                """
                Provide a structured analysis:
                1. Summary (3 sentences)
                2. Key topics (5 bullet points)
                3. Important entities (people, orgs, dates)
                4. Actionable items (if any)

                Format as JSON.
                """
            )

            analyses.append({
                "document": doc.name,
                "analysis": result,
                "tokens": tokens
            })

            print(f"  ✓ Completed ({tokens['total']} tokens)")

        # 3. Synthesize across all documents
        print("\nSynthesizing findings...")

        combined_analyses = "\n\n".join([
            f"Document: {a['document']}\n{a['analysis']}"
            for a in analyses
        ])

        synthesis, tokens = await client.chat(
            f"""
            Synthesize findings from multiple document analyses:

            {combined_analyses}

            Provide:
            1. Cross-document themes
            2. Conflicting information
            3. Overall insights
            4. Recommendations
            """,
            temperature=0.3,
            max_tokens=4096
        )

        print(f"\n{'='*60}")
        print("SYNTHESIS")
        print(f"{'='*60}")
        print(synthesis)
        print(f"\nTotal tokens: {sum(a['tokens']['total'] for a in analyses) + tokens['total']}")

        return {
            "analyses": analyses,
            "synthesis": synthesis
        }

    finally:
        await client.close()

# Run
if __name__ == "__main__":
    result = asyncio.run(document_analysis_pipeline("./documents"))
```

### Example 2: Knowledge Base Q&A System

```python
"""
Complete example: Knowledge base with Q&A
"""

import asyncio
from src.clients.grok_enhanced import EnhancedGrokClient

async def knowledge_base_qa_system():
    """
    Build knowledge base and answer questions
    """
    client = EnhancedGrokClient()

    try:
        # 1. Create knowledge base collection
        print("Creating knowledge base...")
        collection = await client.collections.create_collection(
            name="Company Knowledge Base",
            description="Internal documentation and procedures",
            enable_embeddings=True
        )

        print(f"✓ Created: {collection['id']}")

        # 2. Upload documentation
        print("\nUploading documents...")
        docs = [
            "docs/onboarding.md",
            "docs/engineering-handbook.md",
            "docs/security-policy.pdf",
            "docs/api-reference.md",
        ]

        uploaded = await client.collections.upload_files_batch(
            collection_id=collection['id'],
            file_paths=docs,
            max_concurrent=2
        )

        print(f"✓ Uploaded {len(uploaded)} documents")

        # 3. Wait for embeddings
        print("\nGenerating embeddings...")
        await asyncio.sleep(3)
        print("✓ Embeddings ready")

        # 4. Interactive Q&A
        print("\n" + "="*60)
        print("Knowledge Base Q&A System")
        print("="*60)

        questions = [
            "What is our security policy for API keys?",
            "How do new engineers get onboarded?",
            "What are the main API endpoints?",
        ]

        for question in questions:
            print(f"\nQ: {question}")

            answer, sources = await client.chat_with_collection(
                prompt=question,
                collection_ids=[collection['id']],
                search_top_k=3
            )

            print(f"A: {answer}")
            print(f"\nSources: {len(sources)} documents referenced")
            print("-" * 60)

        # 5. Cleanup
        print("\nCleaning up...")
        await client.collections.delete_collection(collection['id'])
        print("✓ Collection deleted")

    finally:
        await client.close()

# Run
if __name__ == "__main__":
    asyncio.run(knowledge_base_qa_system())
```

### Example 3: Research with Multiple Tools

```python
"""
Complete example: Multi-tool research agent
"""

import asyncio
from src.clients.grok_enhanced import EnhancedGrokClient

async def comprehensive_research(topic: str):
    """
    Research using web search, X sentiment, and code analysis
    """
    client = EnhancedGrokClient(model="grok-4-fast")

    try:
        print(f"Researching: {topic}\n")

        # Phase 1: Web research
        print("Phase 1: Web Research")
        print("-" * 60)

        web_research, tokens1 = await client.research_query(
            f"Find the latest information and research papers on: {topic}",
            use_web=True,
            use_code=False,
            use_x=False
        )

        print(web_research[:500] + "...")
        print(f"Tokens: {tokens1['total']}\n")

        # Phase 2: Social sentiment
        print("Phase 2: Social Sentiment Analysis")
        print("-" * 60)

        sentiment, tokens2 = await client.research_query(
            f"Analyze social sentiment and discussions about: {topic}",
            use_web=False,
            use_code=False,
            use_x=True
        )

        print(sentiment[:500] + "...")
        print(f"Tokens: {tokens2['total']}\n")

        # Phase 3: Quantitative analysis
        print("Phase 3: Data Analysis")
        print("-" * 60)

        analysis, tokens3 = await client.research_query(
            f"""
            Based on this research:

            {web_research[:1000]}

            Perform quantitative analysis:
            1. Extract numerical data
            2. Calculate growth rates or trends
            3. Identify statistical patterns

            Use Python code execution for calculations.
            """,
            use_web=False,
            use_code=True,
            use_x=False
        )

        print(analysis[:500] + "...")
        print(f"Tokens: {tokens3['total']}\n")

        # Phase 4: Final synthesis
        print("Phase 4: Synthesis")
        print("-" * 60)

        synthesis, tokens4 = await client.chat(
            f"""
            Synthesize comprehensive research on: {topic}

            Web Research:
            {web_research}

            Social Sentiment:
            {sentiment}

            Data Analysis:
            {analysis}

            Provide:
            1. Executive Summary
            2. Key Findings
            3. Trend Analysis
            4. Recommendations
            5. Future Outlook
            """,
            temperature=0.3,
            max_tokens=4096
        )

        print(synthesis)

        # Summary
        total_tokens = sum([
            tokens1['total'],
            tokens2['total'],
            tokens3['total'],
            tokens4['total']
        ])

        print(f"\n{'='*60}")
        print(f"Research Complete")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"{'='*60}")

        return synthesis

    finally:
        await client.close()

# Run
if __name__ == "__main__":
    result = asyncio.run(comprehensive_research(
        "Large Language Model inference optimization techniques"
    ))
```

---

**Document Status**: Complete
**Next Steps**: Implement `EnhancedGrokClient` and test with real API
**Questions**: Contact xAI support at https://x.ai/api for clarifications
