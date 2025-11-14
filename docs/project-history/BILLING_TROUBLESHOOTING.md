# xAI API Billing Troubleshooting

## Current Status (Updated 2025-11-14)

**Problem**: API keys still return `403 Forbidden` even after billing was added.

**Latest Test Results**:
- Key: `xai-iQNMFpwsYHj...7Nom3O7I14` ❌ 403 Forbidden
- Tested with official models:
  - `grok-4-fast-reasoning-latest` ❌
  - `grok-code-fast-1` ❌
  - `grok-4-fast-non-reasoning-latest` ❌
- Tested with both LangChain AND direct curl ❌

**Diagnosis**: 403 errors persist across all models and both Python and direct HTTP requests, confirming this is an API key/billing issue, not a code issue.

---

## Troubleshooting Checklist

### 1. Verify Billing Setup is Complete

Go to https://console.x.ai and check:

- [ ] **Payment method added**: Billing → Payment Methods → Should show card
- [ ] **Credits purchased**: Billing → API Credits → Should show balance > $0.00
- [ ] **No pending verification**: Check for any warning banners or verification emails
- [ ] **Billing status "Active"**: Look for status indicator

### 2. Check API Key Creation Timing

**CRITICAL**: API keys created BEFORE billing was set up will NOT work.

**Action Required**:
1. Go to https://console.x.ai → API Keys
2. **Delete old API keys** (created before billing)
3. **Create NEW API key** (after billing is active)
4. Copy the new key immediately (shown only once)

### 3. Wait for Activation (If Just Set Up)

- **Typical delay**: 5-10 minutes after billing setup
- **What to check**: Run test again in 5-10 min
- **How to verify**: Credits should show as "Available" not "Pending"

### 4. Verify Account Status

Check for:
- [ ] Email verification complete
- [ ] Terms of service accepted
- [ ] No account suspension warnings
- [ ] Region/country restrictions (if applicable)

### 5. Check Credit Balance

- Go to: Billing → API Credits
- Minimum recommended: $5-10
- If balance is $0.00, purchase credits
- Verify payment cleared (check bank/card)

---

## What to Provide for Further Debugging

If issue persists after above steps, please provide:

1. **Screenshot of billing page** showing:
   - Credit balance
   - Payment method status
   - Any warning messages

2. **API key creation date**:
   - Was it created BEFORE or AFTER billing setup?

3. **Account age**:
   - Newly created accounts might need manual verification

4. **Error from console.x.ai**:
   - Try making a test API call from their web interface
   - See if it works there but not via our code

---

## Next Steps

**Once you have a working API key**, test it with:

```bash
python3 test_api_detailed.py
```

Or set as environment variable and test:

```bash
export XAI_API_KEY="your-new-key-here"
python3 -m pytest tests/test_adapters.py -v
```

---

## Additional Resources

- Official docs: https://docs.x.ai/docs/models
- Console: https://console.x.ai
- Support: Check console.x.ai for support contact
