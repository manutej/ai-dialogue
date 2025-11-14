# Grok API New Features - Quick Reference

**Quick Start Guide** | See [GROK-NEW-FEATURES.md](./GROK-NEW-FEATURES.md) for full documentation

---

## 🚀 What's New

| Feature | Status | Impact |
|---------|--------|--------|
| **Files API** | ✅ Available | Upload & analyze PDFs, images, docs in chat |
| **Collections API** | ✅ Available | Build knowledge bases with semantic search |
| **Server-Side Tools** | ✅ Available | Autonomous web_search, x_search, code_execution |
| **Tool Mixing** | ⚠️ Limited | Cannot mix client-side + server-side in same request |

---

## 📁 Files API - 30 Second Guide

### Quick Example

```python
from openai import AsyncOpenAI
import base64

client = AsyncOpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1"
)

# Analyze a PDF
file_bytes = open("document.pdf", "rb").read()
encoded = base64.b64encode(file_bytes).decode('utf-8')

response = await client.chat.completions.create(
    model="grok-4",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize this document"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:application/pdf;base64,{encoded}"
                }
            }
        ]
    }]
)
```

### Key Limits

- **Max file size**: 25 MB (chat) / 30 MB (API)
- **Max images**: 3 (chat) / 10 (API)
- **Supported formats**: PDF, DOCX, TXT, MD, CSV, ZIP, JPG, PNG, GIF, WebP

---

## 📚 Collections API - 30 Second Guide

### Quick Example

```python
from collections_manager import CollectionsManager

mgr = CollectionsManager(api_key=os.environ["XAI_API_KEY"])

# Create collection
collection = await mgr.create_collection(
    "Technical Docs",
    enable_embeddings=True
)

# Upload files
await mgr.upload_files_batch(
    collection['id'],
    ["doc1.pdf", "doc2.md", "doc3.txt"]
)

# Search + chat
answer, sources = await mgr.chat_with_collections(
    query="How do I deploy to production?",
    collection_ids=[collection['id']]
)
```

### Key Features

- **Automatic embeddings** for semantic search
- **Multi-collection search** across knowledge bases
- **Chat integration** with context from search results
- **File management** within logical groupings

---

## 🛠️ Server-Side Tools - 30 Second Guide

### Quick Example

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1"
)

# Server autonomously uses tools
response = await client.chat.completions.create(
    model="grok-4-fast",  # Optimized for tools
    messages=[{
        "role": "user",
        "content": "What are the top 3 AI trends this week? Analyze sentiment on X."
    }],
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
        {"type": "code_execution"}
    ]
)

# Get final answer (server handled all tool calls)
answer = response.choices[0].message.content
```

### Available Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| `web_search` | Real-time web search | Current events, recent research |
| `x_search` | X/Twitter search | Social sentiment, trending topics |
| `code_execution` | Python code execution | Calculations, data analysis |

### Key Points

- ✅ **Autonomous**: Server decides when/how to use tools
- ✅ **Single request**: No client orchestration needed
- ✅ **Free until Nov 21, 2025**: Tool invocations free during trial
- ⚠️ **Cannot mix**: No client-side tools in same request

---

## ⚠️ Tool Mixing Limitation

### ❌ This WILL FAIL

```python
tools = [
    {"type": "web_search"},     # Server-side
    {
        "type": "function",      # Client-side
        "function": {"name": "my_func", ...}
    }
]
# Error: Cannot mix server-side and client-side tools
```

### ✅ Workaround: Sequential Requests

```python
# Request 1: Server-side tools
research = await client.chat.completions.create(
    model="grok-4-fast",
    messages=[{"role": "user", "content": "Research topic X"}],
    tools=[{"type": "web_search"}]
)

# Request 2: Client-side tools (separate request)
processed = await client.chat.completions.create(
    model="grok-4",
    messages=[{"role": "user", "content": f"Process: {research}"}],
    tools=[{"type": "function", "function": {...}}]
)
```

---

## 🔄 Integration with ai-dialogue

### Enhanced GrokClient

```python
from src.clients.grok_enhanced import EnhancedGrokClient

# Drop-in replacement for existing GrokClient
grok = EnhancedGrokClient(model="grok-4-fast")

# New: File analysis
response, tokens = await grok.analyze_file(
    "architecture.pdf",
    "Summarize the system design"
)

# New: Research with tools
response, tokens = await grok.research_query(
    "Latest developments in quantum computing",
    use_web=True,
    use_x=True
)

# New: Chat with collections
response, metadata = await grok.chat_with_collection(
    "How does authentication work?",
    collection_ids=["technical-docs"]
)
```

### Enhanced Mode Configuration

```json
{
  "prompts": {
    "turn_1": {
      "participant": "grok",
      "server_side_tools": ["web_search"],
      "files": ["specs/design.pdf"],
      "collections": ["knowledge-base"]
    }
  }
}
```

---

## 💰 Pricing

### Current Pricing

| Component | Rate | Notes |
|-----------|------|-------|
| Input tokens | $x per 1M | Standard rate |
| Output tokens | $y per 1M | Standard rate |
| Tool invocations | **FREE** | Until Nov 21, 2025 |

### Cost Optimization

```python
# 1. Limit tokens
max_tokens=2000

# 2. Lower temperature (fewer retries)
temperature=0.0

# 3. Guide tool usage in prompt
"Search the web ONCE for recent news, then summarize."
```

---

## 📊 Feature Comparison

| Feature | Files API | Collections API | Server-Side Tools |
|---------|-----------|-----------------|-------------------|
| **Setup** | None | Create collection | None |
| **Processing** | Per-request | One-time upload | Per-request |
| **Context** | Single file | Multi-file search | Real-time data |
| **Cost** | Token-based | Token + storage | Token + invocations |
| **Best For** | Document analysis | Knowledge base Q&A | Research & exploration |

---

## 🎯 Use Case Selector

### When to Use Files API

- ✅ Analyzing specific documents (PDFs, images)
- ✅ One-time file processing
- ✅ Multi-modal chat (text + images)
- ❌ Repeated queries on same documents → Use Collections

### When to Use Collections API

- ✅ Building knowledge bases
- ✅ Semantic search across documents
- ✅ Repeated queries on same corpus
- ✅ Enterprise documentation systems
- ❌ Single-use files → Use Files API

### When to Use Server-Side Tools

- ✅ Research queries needing current data
- ✅ Social sentiment analysis
- ✅ Complex calculations/data analysis
- ✅ Exploratory multi-step reasoning
- ❌ Controlled workflows → Use client-side tools

---

## 🚨 Common Pitfalls

### 1. File Too Large

```python
# ❌ Bad: No size check
file_bytes = open("huge.pdf", "rb").read()

# ✅ Good: Validate size
path = Path("huge.pdf")
size_mb = path.stat().st_size / (1024 * 1024)
if size_mb > 30:
    raise ValueError(f"File too large: {size_mb:.1f} MB")
```

### 2. Mixing Tools

```python
# ❌ Bad: Mixing tool types
tools = [
    {"type": "web_search"},
    {"type": "function", "function": {...}}
]

# ✅ Good: Separate requests
# Request 1: server-side tools
# Request 2: client-side tools
```

### 3. No Collection Cleanup

```python
# ❌ Bad: Create and forget
col = await mgr.create_collection("temp")
# ... collection never deleted

# ✅ Good: Use context manager
async with CollectionLifecycleManager(mgr) as cm:
    col = await cm.create_collection("temp")
    # ... automatically cleaned up
```

---

## 📖 More Information

- **Full Documentation**: [GROK-NEW-FEATURES.md](./GROK-NEW-FEATURES.md)
- **Official Docs**: https://docs.x.ai/docs/overview
- **API Console**: https://console.x.ai
- **Python SDK**: https://github.com/xai-org/xai-sdk-python

---

## 🔧 Quick Migration Checklist

- [ ] Update xai-sdk to 1.3.1+
- [ ] Update environment variables (XAI_API_KEY)
- [ ] Replace `GrokClient` with `EnhancedGrokClient`
- [ ] Add new mode configuration fields (files, collections, tools)
- [ ] Test basic features (chat, files, tools)
- [ ] Update protocol engine to use enhanced features
- [ ] Document which modes use which features
- [ ] Set up monitoring for token usage and costs

---

**Last Updated**: 2025-11-10
**Status**: Production Ready
**Full Docs**: 2,732 lines in [GROK-NEW-FEATURES.md](./GROK-NEW-FEATURES.md)
