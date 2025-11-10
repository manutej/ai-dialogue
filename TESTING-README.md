# 🧪 Quick Testing Guide

**Status**: Ready to test Enhanced Grok Client v2.0

---

## ⚡ Quick Start (2 minutes)

### Step 1: Set API Key

```bash
export XAI_API_KEY="your-xai-api-key-here"
```

Get your key at: https://console.x.ai/

### Step 2: Run Tests

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue
python3 tests/manual_test.py
```

### Step 3: Review Results

Tests will run automatically and show:
- ✅ Which tests passed
- ❌ Which tests failed (if any)
- 📊 Summary with success rate

---

## 📋 What Gets Tested

10 comprehensive tests covering all enhanced features:

1. **Basic Chat** - Simple completions
2. **System Prompt** - Instructed responses
3. **Temperature** - Parameter control
4. **File Analysis** - Document processing
5. **Multiple Files** - Batch file handling
6. **Web Search** - Real-time search tool
7. **Code Execution** - Python execution tool
8. **Concurrent Requests** - Async handling
9. **Streaming** - Streamed responses
10. **Error Handling** - Validation & errors

---

## ✅ Expected Result

```
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

## ⚠️ Troubleshooting

### API Key Not Found
```bash
# Check if set
echo $XAI_API_KEY

# Set it if needed
export XAI_API_KEY="your-key-here"
```

### Package Not Found
```bash
# Install dependencies
pip install openai click
```

### Tests Fail
1. Check API key is valid
2. Verify internet connection
3. Review error messages
4. See full guide: `docs/TESTING-GUIDE.md`

---

## 📚 More Information

- **Full Testing Guide**: `docs/TESTING-GUIDE.md`
- **Features Documentation**: `docs/GROK-NEW-FEATURES.md`
- **Migration Guide**: `docs/MIGRATION-GUIDE.md`
- **Examples**: `examples/enhanced_research.py`

---

## 🎯 Next Steps

After tests pass:

1. ✅ Document results
2. ✅ Commit to git
3. ✅ Create stable release
4. ✅ Merge to master

---

**Ready?** Run the tests now:

```bash
python3 tests/manual_test.py
```

Good luck! 🚀
