# Migration Guide: ai-dialogue v1.0 → v2.0 (Enhanced Features)

**Version**: 2.0.0
**Date**: 2025-11-10
**Branch**: `feature/grok-enhanced-v2`

---

## Overview

Version 2.0 introduces significant enhancements to the Grok integration:

- **Files API** - Upload and analyze documents, images, PDFs
- **Collections API** - Create knowledge bases with semantic search
- **Server-Side Tools** - Web search, X search, code execution
- **Enhanced Protocol Engine** - Support for files, collections, and tools in mode configurations

**Backward Compatibility**: ✅ Fully backward compatible with v1.0

---

## What's New

### 1. Files API

Upload and analyze files directly in chat conversations:

```python
# Analyze a single document
response, tokens = await grok.analyze_file(
    "research.pdf",
    "Summarize this document and extract key findings"
)

# Analyze multiple files
response, tokens = await grok.analyze_files(
    ["doc1.pdf", "doc2.pdf", "chart.png"],
    "Compare these documents and identify common themes"
)
```

**Supported Formats**: JPEG, PNG, GIF, WebP, PDF, TXT, CSV, MD, DOCX
**Size Limits**: 30 MB per file, up to 10 files per request

### 2. Collections API

Create searchable knowledge bases:

```python
# Create collection
collection = await grok.collections.create_collection(
    "Technical Docs",
    enable_embeddings=True
)

# Upload files
await grok.collections.upload_files_batch(
    collection['id'],
    ["docs/api.md", "docs/architecture.md"],
    max_concurrent=3
)

# Chat with knowledge base
answer, sources = await grok.chat_with_collection(
    "How do I deploy the application?",
    collection_ids=[collection['id']],
    search_top_k=3
)
```

### 3. Server-Side Tools

Autonomous tool usage for research:

```python
# Web research
response, tokens = await grok.research_query(
    "Latest developments in quantum computing",
    use_web=True,
    use_x=False,
    use_code=False
)

# Multi-tool research
response, tokens = await grok.research_query(
    "Analyze AI safety trends with data",
    use_web=True,
    use_x=True,
    use_code=True  # For calculations
)
```

**Available Tools**:
- `web_search` - Real-time web search
- `x_search` - X (Twitter) sentiment analysis
- `code_execution` - Python code execution

---

## Migration Steps

### Step 1: Update Code

**Option A: Drop-in Replacement (Recommended)**

```python
# Old
from src.clients.grok import GrokClient

# New
from src.clients.grok_enhanced import EnhancedGrokClient as GrokClient

# Usage remains identical
grok = GrokClient(model="grok-4-fast")
response, tokens = await grok.chat("Hello!")
```

**Option B: Explicit Import**

```python
from src.clients.grok_enhanced import EnhancedGrokClient

grok = EnhancedGrokClient(model="grok-4-fast")

# Use new features
response, tokens = await grok.analyze_file("doc.pdf", "Summarize")
```

### Step 2: Update Mode Configurations (Optional)

Add new features to existing modes:

```json
{
  "prompts": {
    "turn_1": {
      "role": "research",
      "participant": "grok",
      // New fields (all optional)
      "server_side_tools": ["web_search"],
      "files": ["research/background.pdf"],
      "collections": ["col_technical_docs"]
    }
  }
}
```

### Step 3: Test Backward Compatibility

```bash
# Run existing workflows (should work unchanged)
ai-dialogue run --mode loop --topic "quantum computing"
ai-dialogue run --mode debate --topic "microservices vs monolith"

# Test new features
ai-dialogue run --mode research-enhanced --topic "AI safety"
```

### Step 4: Gradual Feature Adoption

**Week 1**: Deploy enhanced client alongside old client
**Week 2**: Enable Files API in non-critical modes
**Week 3**: Enable server-side tools for research modes
**Week 4**: Integrate collections for knowledge-heavy workflows
**Week 5**: Full migration, deprecate old client

---

## API Changes

### EnhancedGrokClient

**New Methods**:

```python
# File analysis
async def analyze_file(file_path: str, analysis_prompt: str) -> Tuple[str, Dict]
async def analyze_files(file_paths: List[str], analysis_prompt: str) -> Tuple[str, Dict]

# Research with tools
async def research_query(
    query: str,
    use_web: bool = True,
    use_x: bool = False,
    use_code: bool = False
) -> Tuple[str, Dict]

# Collections
async def chat_with_collection(
    prompt: str,
    collection_ids: List[str],
    search_top_k: int = 3
) -> Tuple[str, Dict]

# Access collections manager
grok.collections  # CollectionsManager instance
```

**Enhanced Existing Methods**:

```python
# chat() now accepts files and server_side_tools
async def chat(
    prompt: str,
    # Existing parameters...
    files: Optional[List[str]] = None,  # NEW
    server_side_tools: Optional[List[str]] = None  # NEW
) -> Tuple[str, Dict]
```

### CollectionsManager

**New Class**:

```python
from src.clients.collections_manager import CollectionsManager

manager = CollectionsManager(api_key=XAI_API_KEY)

# Core operations
await manager.create_collection(name, description, enable_embeddings=True)
await manager.upload_file(collection_id, file_path)
await manager.upload_files_batch(collection_id, file_paths, max_concurrent=3)
await manager.search(query, collection_ids, top_k=5)
await manager.chat_with_collections(query, collection_ids, model, search_top_k=3)
await manager.delete_collection(collection_id)
```

---

## Breaking Changes

**None** - Full backward compatibility maintained.

All new features are opt-in through new parameters or methods.

---

## Performance Considerations

### Files API

- **Base64 encoding**: Small overhead for file encoding
- **Token usage**: Files increase prompt tokens
- **Recommendation**: Use for files < 10 MB

### Collections API

- **Embedding generation**: 2-5 seconds per file
- **Search latency**: ~100-300ms
- **Recommendation**: Pre-load collections during initialization

### Server-Side Tools

- **Tool invocations**: Unpredictable (agent decides)
- **Cost**: Free until Nov 21, 2025
- **Recommendation**: Use specific prompts to guide tool usage

---

## Example Migrations

### Example 1: Simple Research (Before → After)

**Before (v1.0)**:

```python
response, tokens = await grok.chat(
    "Research quantum computing applications",
    model="grok-4-fast"
)
```

**After (v2.0 with web search)**:

```python
response, tokens = await grok.research_query(
    "Research quantum computing applications",
    use_web=True  # Now includes real-time web search
)
```

### Example 2: Document Analysis (New in v2.0)

**Before (v1.0)**: Not possible

**After (v2.0)**:

```python
# Analyze PDF document
response, tokens = await grok.analyze_file(
    "research/quantum-paper.pdf",
    "Summarize this paper and extract methodology"
)

# Compare multiple documents
response, tokens = await grok.analyze_files(
    ["paper1.pdf", "paper2.pdf", "paper3.pdf"],
    "Compare methodologies across these papers"
)
```

### Example 3: Knowledge Base Q&A (New in v2.0)

**Before (v1.0)**: Manual context management

**After (v2.0)**:

```python
# Create knowledge base
collection = await grok.collections.create_collection(
    "Engineering Docs",
    enable_embeddings=True
)

# Upload documentation
await grok.collections.upload_files_batch(
    collection['id'],
    ["docs/api.md", "docs/deployment.md", "docs/architecture.md"]
)

# Query with automatic context retrieval
answer, sources = await grok.chat_with_collection(
    "How do I deploy to production?",
    collection_ids=[collection['id']],
    search_top_k=3
)

print(f"Answer: {answer}")
print(f"Based on {len(sources)} sources")
```

---

## Testing Checklist

### Backward Compatibility

- [ ] Existing modes run without modification
- [ ] Basic `chat()` calls work unchanged
- [ ] Streaming continues to function
- [ ] Token tracking remains accurate
- [ ] Error handling behaves consistently

### New Features

- [ ] Files API: Upload and analyze PDF
- [ ] Files API: Analyze multiple images
- [ ] Collections: Create and populate collection
- [ ] Collections: Semantic search returns results
- [ ] Collections: Chat with collection context
- [ ] Server-Side Tools: Web search works
- [ ] Server-Side Tools: X search works
- [ ] Server-Side Tools: Code execution works
- [ ] Enhanced modes: research-enhanced runs successfully

### Integration

- [ ] Protocol engine handles files in turn configs
- [ ] Protocol engine handles collections in turn configs
- [ ] Protocol engine handles server_side_tools in turn configs
- [ ] State manager persists enhanced turn data
- [ ] Markdown export includes file/collection metadata

---

## Troubleshooting

### Issue: "XAI_API_KEY not found"

**Solution**: Ensure environment variable is set

```bash
export XAI_API_KEY="your-api-key-here"
```

### Issue: "File too large" error

**Solution**: Files must be < 30 MB

```python
# Compress or split large files before upload
def check_file_size(file_path):
    size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    if size_mb > 30:
        raise ValueError(f"File too large: {size_mb:.1f} MB")
```

### Issue: "Cannot mix server-side and client-side tools"

**Solution**: Use sequential requests

```python
# Step 1: Server-side research
research, tokens1 = await grok.research_query(
    "Topic",
    use_web=True
)

# Step 2: Client-side processing (separate request)
processed, tokens2 = await grok.chat(
    f"Process: {research}",
    # Use client-side tools if needed
)
```

### Issue: Collections search returns no results

**Solution**: Check embeddings and wait for processing

```python
# Ensure embeddings are enabled
collection = await grok.collections.create_collection(
    "name",
    enable_embeddings=True  # MUST be True for search
)

# Wait for embedding generation
await asyncio.sleep(5)  # Allow time for processing
```

---

## Rollback Plan

If issues arise during migration:

### Option 1: Revert to Old Client

```python
# Temporarily use old client
from src.clients.grok import GrokClient  # Original v1.0 client
```

### Option 2: Merge Branch

```bash
# Checkout master
git checkout master

# Keep enhanced client available
git merge --no-commit --no-ff feature/grok-enhanced-v2
git reset HEAD src/clients/grok_enhanced.py
git commit -m "Keep enhanced client as optional"
```

### Option 3: Feature Flags

```python
# In your code
USE_ENHANCED_GROK = os.environ.get("USE_ENHANCED_GROK", "false").lower() == "true"

if USE_ENHANCED_GROK:
    from src.clients.grok_enhanced import EnhancedGrokClient as GrokClient
else:
    from src.clients.grok import GrokClient
```

---

## Support

- **Documentation**: See `docs/GROK-NEW-FEATURES.md` for comprehensive guide
- **Examples**: See `examples/enhanced_research.py`
- **Issues**: Open GitHub issue with `[v2.0]` prefix

---

## Changelog

### v2.0.0 (2025-11-10)

**Added**:
- EnhancedGrokClient with Files, Collections, and Server-Side Tools support
- CollectionsManager for knowledge base management
- research-enhanced mode demonstrating new features
- Comprehensive documentation in docs/GROK-NEW-FEATURES.md

**Changed**:
- None (fully backward compatible)

**Deprecated**:
- None

**Fixed**:
- None

---

**Status**: Ready for testing
**Next**: Run integration tests and validate workflow
