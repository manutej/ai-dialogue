# Verify xAI Billing Setup

Your API keys are still returning 403 errors. Let's verify your billing setup step-by-step.

## Step 1: Check Billing Dashboard

1. Go to https://console.x.ai/billing
2. Screenshot or verify the following:

### Credit Balance
```
Current Balance: $_____
Status: [ ] Active / [ ] Pending / [ ] Inactive
```

**REQUIRED**: Balance must be > $0.00 AND status must be "Active"

### Payment Method
```
[ ] Credit/Debit card added
[ ] Card verified (no pending verification)
[ ] Billing address complete
```

**REQUIRED**: All boxes checked

### Transaction History
```
Most recent transaction:
- Date: _____
- Amount: $_____
- Status: [ ] Completed / [ ] Pending / [ ] Failed
```

**REQUIRED**: Status must be "Completed", not "Pending"

---

## Step 2: Check API Key Creation Date

1. Go to https://console.x.ai/api-keys
2. Find your current API key: `xai-iQNMFpwsYHj...`
3. Check "Created" date/time

### CRITICAL CHECK

**When was billing added?**: _____ (date/time)
**When was API key created?**: _____ (date/time)

**⚠️ API KEY MUST BE CREATED *AFTER* BILLING IS ACTIVE**

If API key was created BEFORE billing:
1. Delete the old key
2. Wait 2 minutes
3. Create a NEW key
4. Test with new key

---

## Step 3: Check for Account Restrictions

Look for any warning banners or messages at the top of console.x.ai:

```
[ ] "Email verification required"
[ ] "Identity verification pending"
[ ] "Payment method needs verification"
[ ] "Account under review"
[ ] Any other warnings
```

**REQUIRED**: No warnings present

---

## Step 4: Verify API Access is Enabled

1. Go to https://console.x.ai/settings or Account Settings
2. Look for "API Access" section

```
API Access: [ ] Enabled / [ ] Disabled / [ ] Pending
Rate Limits: _____
Usage Tier: _____
```

**REQUIRED**: API Access must be "Enabled"

---

## Step 5: Test from Web Console

1. Go to https://console.x.ai/playground (if available)
2. Try to run a test query using their web interface
3. Does it work?

```
[ ] Web console works → Problem is with API keys
[ ] Web console also fails → Account-level issue
```

---

## Step 6: Check Email

1. Check your email (including spam) for messages from xAI
2. Look for:
   - Payment confirmation
   - Account verification requests
   - API access approval

---

## Common Issues and Solutions

### Issue 1: Key Created Before Billing
**Symptom**: 403 on all requests, even though billing is set up
**Solution**: Delete old key, create new one AFTER billing is confirmed active

### Issue 2: Payment Pending
**Symptom**: Billing shows "Pending" status
**Solution**: Wait for payment to clear (can take 24-48 hours depending on bank)

### Issue 3: Insufficient Credits
**Symptom**: Balance shows $0.00 or very low amount
**Solution**: Add more credits (minimum $5-10 recommended)

### Issue 4: Account Verification Pending
**Symptom**: Warning banner about verification
**Solution**: Complete verification process (email, identity, etc.)

### Issue 5: Regional Restrictions
**Symptom**: All checks pass but still 403
**Solution**: Check if xAI API is available in your region/country

### Issue 6: API Access Not Enabled
**Symptom**: Billing works but API calls fail
**Solution**: Enable API access in account settings (may require application/approval)

---

## What to Report Back

After going through these checks, please provide:

1. **Credit balance**: $_____
2. **Billing status**: Active / Pending / Other
3. **API key created**: Before or After billing?
4. **Any warning messages**: Yes/No (what messages?)
5. **Web console test**: Works / Doesn't work / No playground available

With this information, I can provide more specific guidance.

---

## Alternative: Contact xAI Support

If all checks pass but API still fails:

1. Go to console.x.ai
2. Look for "Support" or "Help" link
3. Submit ticket with:
   - Account email
   - API key ID (first/last 4 chars)
   - Error message: "403 Access denied on all API calls"
   - What you've tried: "Billing set up, credits added, new key created, still getting 403"

They can verify your account status and API access permissions directly.
