# AI Mitigation Plan Debugging Guide
## FILDZA_AI_ACTIVE - How to Verify AI is Working & Generating Different Plans

---

## Problem: Mitigation Plans Are All The Same

### Quick Diagnosis

**Step 1: Run the debug test**
```powershell
python debug_ai_mitigation.py
```

This tests 4 different breach scenarios and shows:
- ✓ Whether AI is being called
- ✓ Whether risk levels differ  
- ✓ Whether mitigation actions are different/specific

---

## Solutions

### Solution 1: Verify Ollama is Running (CRITICAL)

```powershell
# Terminal 1: Start Ollama
ollama run phi3

# You should see:
# >>> hi
# (waiting for input)
```

**If Ollama isn't running:**
```powershell
# Installation (if not installed)
Download from: https://ollama.ai

# Then:
ollama pull phi3
ollama run phi3
```

---

### Solution 2: Check Logs for AI Calls

When you run `/check email@example.com` in Telegram, **check bot.py console logs**:

**Expected log output:**
```
============================================================
FILDZA_AI_ACTIVE - Ollama Analysis Started
============================================================
Email: email@example.com
Breaches: 2
Data types: Email, Password
Password exposed: True | Financial: False | Phone: False | Multiple: True
Model: phi3 | Timeout: 40s

Breach Details:
  1. LinkedIn: ['Email', 'Password']
  2. Dropbox: ['Email', 'Password']

Connecting to Ollama (http://localhost:11434/api/generate)...
✓ Ollama responded (status 200)
Response length: 1523 chars
✓ JSON parsed successfully

============================================================
AI RESULT FOR: email@example.com
============================================================
Risk Level: HIGH
Explanation: Password exposure in multiple breaches requires immediate action...
Immediate Actions (3):
  • Reset password on LinkedIn and Dropbox immediately
  • Enable 2FA on all accounts
  • Monitor for unauthorized logins
...
```

**If you see this, AI is working!** ✓

---

### Solution 3: If Logs Show "Fallback" or "None"

**Check for errors in console:**
```
❌ Cannot connect to Ollama at http://localhost:11434
Run: ollama run phi3
```

**Fix:**
1. Start Ollama in separate terminal
2. Verify it's accessible: `curl http://localhost:11434/api/tags`
3. Restart bot.py

---

### Solution 4: If AI Response is Generic

**Possible causes:**

1. **phi3 model is too lightweight**
   - Try a better model:
   ```powershell
   ollama pull mistral
   # Then update bot.py: change "model": "phi3" → "model": "mistral"
   ```

2. **Prompt needs tweaking**
   - Check the prompt in bot.py (line ~23)
   - Make sure it includes examples

3. **phi3 model is corrupted**
   - Delete and re-pull:
   ```powershell
   ollama rm phi3
   ollama pull phi3
   ```

---

## Testing: Verify AI Generates Different Plans

### Manual Test: 3 Different Emails

**Email 1: test1@example.com (Email only)**
```
Expected: LOW/MEDIUM risk
Expected: Focus on account security, email recovery
```

**Email 2: test2@example.com (Email + Password)**
```
Expected: HIGH risk  
Expected: Focus on password reset, 2FA, monitor logins
```

**Email 3: test3@example.com (Email + Password + Phone)**
```
Expected: CRITICAL risk
Expected: Focus on urgent password reset, SIM swap check, credit monitoring
```

### Check: Are Immediate Actions Different?

Run debug test:
```powershell
python debug_ai_mitigation.py
```

**Good output:**
```
Scenario 1 immediate actions:
  • Review email security settings
  • Monitor account for unauthorized access

Scenario 2 immediate actions:
  • Reset password immediately
  • Enable 2FA on all accounts
  • Check for unauthorized logins

Scenario 3 immediate actions:
  • Contact your bank immediately
  • Reset password on affected accounts
  • Enable 2FA and 2FA on banking apps
```

**Bad output (all same):**
```
All scenarios have same immediate actions:
  • Change all passwords immediately
  • Enable 2FA/MFA wherever possible
  • Monitor bank & credit accounts
```
→ **AI is not being specific - try different model**

---

## Checking Bot Logs

### Option 1: Live Console

```powershell
python bot.py

# Watch for FILDZA_AI_ACTIVE messages
```

### Option 2: Save Logs to File

```python
# Add to top of bot.py after logging.basicConfig:
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_debug.log')  # Save to file
    ]
)
```

Then check `bot_debug.log` after running `/check` command.

---

## Model Recommendations

| Model | Size | Speed | Quality | RAM |
|-------|------|-------|---------|-----|
| **phi3** | 2.3GB | Fast | Generic | ✓ Low |
| **mistral** | 4.1GB | Medium | Better | ≈ Medium |
| **llama3** | 7.9GB | Slow | Excellent | ✗ High |

**For FYP:** Start with **mistral** if you have 8GB+ RAM

---

## Quick Fix Checklist

- [ ] Ollama is running: `ollama run phi3`
- [ ] Debug test passes: `python debug_ai_mitigation.py`
- [ ] Logs show "FILDZA_AI_ACTIVE - Analysis Complete" 
- [ ] Risk levels differ across scenarios
- [ ] Immediate actions mention specific data types (password, phone, financial)
- [ ] `/check` in Telegram shows "Status: AI-Powered Recommendation"

---

## Still Not Working?

1. **Restart everything:**
   ```powershell
   # Terminal 1: Stop everything
   Ctrl+C (several times)
   
   # Terminal 2: Kill Ollama
   taskkill /F /IM ollama.exe
   
   # Terminal 1: Start fresh
   ollama run phi3
   
   # Terminal 2: Start bot
   python bot.py
   ```

2. **Clear cache:**
   ```powershell
   # Remove Ollama cache
   remove-item $env:USERPROFILE\.ollama -Recurse -Force
   ollama pull phi3
   ```

3. **Try a different model:**
   ```powershell
   ollama pull mistral
   # Update bot.py line: "model": "mistral"
   ```

---

**Remember:** AI Mitigation is an enhancement. Even if it fails, the bot **always falls back to static mitigation** safely.

For further debugging, check `debug_ai_mitigation.py` output and logs in console.

**Keyword: FILDZA_AI_ACTIVE** ✓
