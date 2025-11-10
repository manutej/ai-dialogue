# Testing Guide: Enhanced Grok Client

**Version**: 2.0.0
**Status**: Ready for testing
**Last Updated**: 2025-11-10

---

## Prerequisites

### 1. API Key

You need an XAI API key to run tests:

```bash
export XAI_API_KEY="your-xai-api-key-here"
```

**Get your API key**: https://console.x.ai/

### 2. Python Environment

Ensure you have Python 3.10+ and required packages:

```bash
# Check Python version
python3 --version  # Should be 3.10 or higher

# Install dependencies
cd /Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue
pip install -e .

# Or install just what you need
pip install openai click
```

---

## Quick Test (Manual)

Run the manual test suite to verify all functionality:

```bash
# Set API key (if not already set)
export XAI_API_KEY="your-key-here"

# Run manual tests
cd /Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue
python3 tests/manual_test.py
```

### What Gets Tested:

1. ✅ **Basic Chat** - Simple chat completions
2. ✅ **System Prompt** - Chat with system instructions
3. ✅ **Temperature Control** - Parameter testing
4. ✅ **File Analysis** - Single file upload and analysis
5. ✅ **Multiple Files** - Multi-file analysis
6. ✅ **Web Search** - Server-side web_search tool
7. ✅ **Code Execution** - Server-side code_execution tool
8. ✅ **Concurrent Requests** - Async context preservation
9. ✅ **Streaming Chat** - Streaming responses
10. ✅ **Error Handling** - Validation and error cases

### Expected Output:

```
============================================================
ENHANCED GROK CLIENT - MANUAL TEST SUITE
============================================================

✓ XAI_API_KEY found
✓ Initializing EnhancedGrokClient...
✓ Client initialized with model: grok-4-fast
✓ Test files created

============================================================
Test 1: Basic Chat
============================================================
Response: Hello from Grok!
Tokens: {'prompt': 10, 'completion': 5, 'total': 15}

✅ PASSED: Basic Chat

[... more tests ...]

============================================================
TEST SUMMARY
============================================================
✅ PASSED Basic Chat
✅ PASSED System Prompt
✅ PASSED Temperature Control
✅ PASSED File Analysis
✅ PASSED Multiple Files
✅ PASSED Web Search
✅ PASSED Code Execution
✅ PASSED Concurrent Requests
✅ PASSED Streaming Chat
✅ PASSED Error Handling

============================================================
Total: 10
Passed: 10 ✅
Failed: 0 ❌
Success Rate: 100.0%
============================================================

🎉 All tests passed! Implementation is stable.
```

---

## Advanced Testing (pytest)

For more comprehensive testing with pytest:

### Install pytest:

```bash
pip install pytest pytest-asyncio
```

### Run pytest suite:

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue

# Run all tests
pytest tests/test_grok_enhanced.py -v

# Run specific test class
pytest tests/test_grok_enhanced.py::TestBasicChat -v

# Run with detailed output
pytest tests/test_grok_enhanced.py -v -s

# Run and stop on first failure
pytest tests/test_grok_enhanced.py -x
```

### Pytest Test Coverage:

#### TestEnhancedGrokClientInit (Unit Tests)
- Client initialization with API key
- Missing API key error handling
- Collections lazy loading

#### TestBasicChat (Integration)
- Simple chat completions
- System prompt handling
- Temperature parameter

#### TestFilesAPI (Integration)
- Single file analysis
- Markdown file analysis
- Multiple file analysis
- File limit validation

#### TestServerSideTools (Integration)
- Web search functionality
- Tool validation (no tools error)
- Multiple tools together

#### TestAsyncContext (Integration)
- Concurrent requests
- Sequential requests with context

#### TestErrorHandling (Integration)
- Invalid model handling
- Non-existent file handling

#### TestStreamingChat (Integration)
- Streaming chat responses

---

## Testing Specific Features

### Test Files API

```python
import asyncio
from src.clients.grok_enhanced import EnhancedGrokClient

async def test_files():
    client = EnhancedGrokClient()

    # Test single file
    response, tokens = await client.analyze_file(
        "path/to/document.pdf",
        "Summarize this document"
    )
    print(f"Analysis: {response}")

    await client.close()

asyncio.run(test_files())
```

### Test Server-Side Tools

```python
import asyncio
from src.clients.grok_enhanced import EnhancedGrokClient

async def test_tools():
    client = EnhancedGrokClient()

    # Web search
    response, tokens = await client.research_query(
        "Latest developments in AI",
        use_web=True
    )
    print(f"Research: {response}")

    # Code execution
    response, tokens = await client.research_query(
        "Calculate factorial of 10",
        use_code=True
    )
    print(f"Calculation: {response}")

    await client.close()

asyncio.run(test_tools())
```

### Test Collections API

```python
import asyncio
from src.clients.grok_enhanced import EnhancedGrokClient

async def test_collections():
    client = EnhancedGrokClient()

    # Create collection
    collection = await client.collections.create_collection(
        "Test Collection",
        enable_embeddings=True
    )

    # Upload files
    files = ["doc1.md", "doc2.md"]
    uploaded = await client.collections.upload_files_batch(
        collection['id'],
        files
    )

    # Search
    results = await client.collections.search(
        "test query",
        collection_ids=[collection['id']]
    )

    # Chat with collection
    answer, sources = await client.chat_with_collection(
        "Question about docs?",
        collection_ids=[collection['id']]
    )

    await client.close()

asyncio.run(test_collections())
```

---

## Troubleshooting

### Issue: "XAI_API_KEY not found"

**Solution**:
```bash
# Set environment variable
export XAI_API_KEY="your-key-here"

# Verify it's set
echo $XAI_API_KEY

# Or pass directly to client
client = EnhancedGrokClient(api_key="your-key-here")
```

### Issue: "Module 'openai' not found"

**Solution**:
```bash
pip install openai
```

### Issue: Tests timeout or hang

**Possible causes**:
1. Network issues
2. API rate limiting
3. Large files taking time to process

**Solutions**:
- Check internet connection
- Wait a few seconds and retry
- Reduce file sizes for testing
- Increase timeout in client

### Issue: "401 Unauthorized"

**Cause**: Invalid or expired API key

**Solution**:
1. Verify API key is correct
2. Check API key hasn't expired
3. Generate new API key at console.x.ai

### Issue: Server-side tools not working

**Possible causes**:
1. Tool parameter format incorrect
2. API doesn't support tool yet
3. Model doesn't support tools

**Solutions**:
- Use `grok-4-fast` model (optimized for tools)
- Check tool name spelling: `web_search`, `x_search`, `code_execution`
- Verify API documentation for tool support

---

## Performance Testing

### Latency Benchmarks

```python
import asyncio
import time
from src.clients.grok_enhanced import EnhancedGrokClient

async def benchmark():
    client = EnhancedGrokClient()

    # Measure basic chat latency
    start = time.time()
    response, tokens = await client.chat("Hello", max_tokens=50)
    latency = time.time() - start

    print(f"Latency: {latency:.2f}s")
    print(f"Tokens: {tokens['total']}")
    print(f"Tokens/second: {tokens['total']/latency:.1f}")

    await client.close()

asyncio.run(benchmark())
```

### Concurrent Load Testing

```python
import asyncio
from src.clients.grok_enhanced import EnhancedGrokClient

async def load_test(num_requests=10):
    client = EnhancedGrokClient()

    tasks = [
        client.chat(f"Request {i}", max_tokens=20)
        for i in range(num_requests)
    ]

    start = time.time()
    results = await asyncio.gather(*tasks)
    duration = time.time() - start

    print(f"Completed {num_requests} requests in {duration:.2f}s")
    print(f"Requests/second: {num_requests/duration:.1f}")

    await client.close()

asyncio.run(load_test(10))
```

---

## Integration Testing

### Test with Existing Workflow

```bash
# Test enhanced mode
cd /Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue

# Run research-enhanced mode
python3 cli.py run \
  --mode research-enhanced \
  --topic "AI agent architectures" \
  --output test-output.md
```

### Test Backward Compatibility

```bash
# Run existing modes (should work unchanged)
python3 cli.py run --mode loop --topic "quantum computing"
python3 cli.py run --mode debate --topic "microservices vs monolith"
```

---

## Test Checklist

Before merging to master, ensure all tests pass:

### Unit Tests
- [ ] Client initialization
- [ ] Parameter validation
- [ ] Error handling
- [ ] Collections lazy loading

### Integration Tests
- [ ] Basic chat completions
- [ ] System prompts
- [ ] Temperature control
- [ ] File analysis (single)
- [ ] File analysis (multiple)
- [ ] Web search tool
- [ ] Code execution tool
- [ ] X search tool
- [ ] Streaming chat
- [ ] Concurrent requests
- [ ] Error cases

### Real-World Tests
- [ ] Analyze actual PDF document
- [ ] Analyze actual images
- [ ] Run research-enhanced mode
- [ ] Test with large files (near 30 MB limit)
- [ ] Test with 10 files simultaneously
- [ ] Verify backward compatibility

### Performance Tests
- [ ] Measure average latency
- [ ] Test concurrent load
- [ ] Monitor token usage
- [ ] Check memory usage

---

## Continuous Testing

### Automated Testing Setup

Create `.github/workflows/test.yml`:

```yaml
name: Test Enhanced Grok Client

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-asyncio

      - name: Run tests
        env:
          XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
        run: pytest tests/ -v
```

---

## Test Results Documentation

After running tests, document results:

### Template:

```markdown
# Test Results

**Date**: 2025-11-10
**Tester**: Your Name
**Branch**: feature/grok-enhanced-v2
**API Key**: ✓ Valid

## Summary

- Total Tests: 10
- Passed: 10
- Failed: 0
- Success Rate: 100%

## Details

### Basic Chat ✅
- Latency: 1.2s
- Tokens: 25

### File Analysis ✅
- File: test.pdf (1.2 MB)
- Latency: 3.5s
- Tokens: 450

[... more details ...]

## Issues Found

None

## Recommendations

- All tests passing
- Ready for merge
```

---

## Next Steps

1. **Run Manual Tests**: `python3 tests/manual_test.py`
2. **Document Results**: Save output to `docs/TEST-RESULTS.md`
3. **Fix Any Issues**: Update code as needed
4. **Retest**: Verify fixes work
5. **Merge**: Create PR when all tests pass

---

**Questions?** See:
- Examples: `examples/enhanced_research.py`
- Documentation: `docs/GROK-NEW-FEATURES.md`
- Migration: `docs/MIGRATION-GUIDE.md`

---

**Status**: Ready for testing
**Last Updated**: 2025-11-10
