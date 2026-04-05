## FILDZA_AI_ACTIVE - BocorCheck AI Integration Setup Guide

### 📋 Overview

This guide explains the new **FILDZA_AI_ACTIVE** feature: dynamic, AI-powered mitigation recommendations using a local Ollama instance with the lightweight **phi3** model.

---

### ✨ New Features

**What's New:**
- ✅ Dynamic mitigation plans (not static/hardcoded)
- ✅ AI-generated recommendations based on:
  - Breach type (email, password, phone, bank)
  - Risk level (LOW, MEDIUM, HIGH)
  - Actual data exposed
- ✅ Integrated with Telegram bot (`/check` command)
- ✅ Graceful fallback if Ollama unavailable
- ✅ Comprehensive logging for debugging
- ✅ Optimized for low-RAM systems (phi3 model)

---

### 🚀 Quick Start

#### 1. Install Ollama

Download from: https://ollama.ai

#### 2. Pull phi3 Model

```bash
ollama pull phi3
```

#### 3. Start Ollama

```bash
ollama serve
```

This starts Ollama on `http://localhost:11434`

#### 4. Run BocorCheck Bot

```bash
python bot.py
```

#### 5. Test with Telegram

Send to bot:
```
/start          # Help
/check user@email.com  # Breach check with AI mitigation
```

---

### 📝 Configuration

**Environment Variables:**
```bash
OLLAMA_MODEL=phi3              # Model to use
OLLAMA_URL=http://localhost:11434  # Ollama endpoint
OLLAMA_TIMEOUT=40              # Seconds
TELEGRAM_BOT_TOKEN=...         # Your bot token
TELEGRAM_CHAT_ID=...           # Optional: restrict access
```

---

### 🤖 How AI Mitigation Works

#### 1. **User sends email check**
```
/check test@example.com
```

#### 2. **System retrieves breach data**
- Queries HIBP API (or mock data)
- Extracts breach names, dates, exposed data types

#### 3. **AI analysis (phi3 via Ollama)**
- Sends structured prompt with breach context
- Ollama processes and generates response
- Extracts JSON with:
  - `risk_level`: HIGH | MEDIUM | LOW
  - `explanation`: Cybersecurity assessment
  - `mitigation`: immediate, short_term, long_term actions

#### 4. **Display results**
- Shows breach summary
- Displays AI risk assessment
- Lists tailored mitigation actions
- Falls back to static if AI unavailable

---

### 📊 Example Output

**Prompt to AI:**
```
Breach Data:
Email: test@example.com
Breaches: 2
Exposed: Email, Password

1. LinkedIn: Email, Password (Date: 2021-06-28)
2. MyAdidas: Email (Date: 2020-03-20)

For each mitigation, make it SPECIFIC to exposed data:
- Password exposed? → Reset all passwords, enable 2FA
- Email exposed? → Check for unauthorized access, enable recovery options
```

**AI Response:**
```json
{
  "risk_level": "HIGH",
  "explanation": "Password exposure is critical. Immediate action required.",
  "mitigation": {
    "immediate": [
      "Reset password immediately for all accounts using this email",
      "Enable 2FA on all accounts, especially email",
      "Check for unauthorized logins in account activity"
    ],
    "short_term": [
      "Monitor email for password reset attempts or suspicious access",
      "Review account recovery options (phone, backup email)",
      "Check LinkedIn and Adidas accounts for suspicious activity"
    ],
    "long_term": [
      "Use unique passwords for each online account",
      "Enable breach notifications in email settings",
      "Implement password manager (e.g., Bitwarden, 1Password)"
    ]
  }
}
```

**Telegram Bot Output:**
```
🔍 BREACH ANALYSIS FOR: test@example.com
==================================================

Breach #1:
  Company: LinkedIn
  Date: 2021-06-28
  Data Exposed: Email, Password

Breach #2:
  Company: MyAdidas
  Date: 2020-03-20
  Data Exposed: Email

🔴 AI RISK ASSESSMENT: HIGH
📋 Analysis: Password exposure is critical. Immediate action required.

🛡️ AI-GENERATED MITIGATION PLAN
==================================================

⚠️ IMMEDIATE ACTIONS (Do NOW):
  1. Reset password immediately for all accounts using this email
  2. Enable 2FA on all accounts, especially email
  3. Check for unauthorized logins in account activity

📅 SHORT-TERM ACTIONS (Days 1-7):
  1. Monitor email for password reset attempts or suspicious access
  2. Review account recovery options (phone, backup email)
  3. Check LinkedIn and Adidas accounts for suspicious activity

🔄 LONG-TERM ACTIONS (Ongoing):
  1. Use unique passwords for each online account
  2. Enable breach notifications in email settings
  3. Implement password manager (e.g., Bitwarden, 1Password)

==================================================
Status: AI-Powered Recommendation (FILDZA_AI_ACTIVE)
```

---

### 🔍 Logging & Debugging

#### View AI Logs

Run with logging enabled:
```bash
python bot.py 2>&1 | grep FILDZA_AI_ACTIVE
```

#### Example Log Output
```
============================================================
FILDZA_AI_ACTIVE - /check command for: test@example.com
============================================================
Found 2 breach(es) for test@example.com
FILDZA_AI_ACTIVE - Starting AI mitigation generation

============================================================
FILDZA_AI_ACTIVE - Ollama Analysis Started
============================================================
Email: test@example.com
Breaches: 2 | Data types: Email, Password
Model: phi3 | Timeout: 40s
Connecting to Ollama (http://localhost:11434/api/generate)...
✓ Ollama responded (status 200)
Response length: 1256 chars
✓ JSON parsed successfully
✓ FILDZA_AI_ACTIVE - Analysis Complete
  Risk: HIGH
  Actions: 3 immediate, 3 short-term, 3 long-term
============================================================

FILDZA_AI_ACTIVE - Using AI-generated mitigation plan
FILDZA_AI_ACTIVE - Sending AI-powered response to Telegram
```

---

### ⚙️ Code Structure

#### Main Files

**bot.py**
- `analyzeWithAI(osint_data)` - Calls Ollama phi3 model
- `check(update, context)` - /check command handler with AI integration
- `main()` - Bot initialization with FILDZA_AI_ACTIVE logging

**ai_mitigation.py** (Optional, for reuse in Flask routes)
- `generate_ai_mitigation()` - Wrapper for AI analysis
- `format_mitigation_for_display()` - Format for HTML templates
- `DEFAULT_MITIGATION` - Static fallback

**requirements.txt**
- `requests` - HTTP library for Ollama API
- `python-telegram-bot` - Telegram bot library
- `ollama` (optional) - Direct Ollama SDK

---

### 🔄 Fallback Behavior

If Ollama is unavailable:

```python
❌ Cannot connect to Ollama at http://localhost:11434
Make sure Ollama is running: 'ollama run phi3'
Fallback: Using static mitigation
```

The bot will automatically use pre-defined static mitigation plan without crashing.

---

### 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'aiohttp'` | `pip install -r requirements.txt` or just `pip install requests` |
| `Cannot connect to Ollama` | Run `ollama serve` in separate terminal |
| `Ollama timeout (40s)` | Model loading slowly: ensure phi3 is pulled (`ollama pull phi3`) |
| `No JSON in response` | Ollama response format changed; check Ollama version |
| `Missing required keys` | AI response malformed; check prompt formatting |

---

### 📈 Performance Notes

**phi3 Model:**
- Size: ~2.3 GB
- RAM: 4-8 GB minimum
- GPU: Optional (CPU fallback works)
- Response time: 10-30 seconds (first run slower due to model loading)

**Optimization Tips:**
- Keep Ollama running (`ollama serve`)  in background
- First request loads model into memory (slower)
- Subsequent requests are faster
- Timeout set to 40s for slower systems

---

### ✅ Verification Checklist

- [ ] Ollama installed and running
- [ ] φ3 model pulled (`ollama pull phi3`)
- [ ] Bot token set in `TELEGRAM_BOT_TOKEN`
- [ ] Requirements installed (`pip install -r requirements.txt`)
- [ ] Flask app runs without errors (`python app.py`)
- [ ] Bot starts without errors (`python bot.py`)
- [ ] Cantest with `/start` command
- [ ] Test with `/check test@example.com`
- [ ] Check logs for "FILDZA_AI_ACTIVE" keyword

---

### 📚 Files Modified/Created

**Modified:**
- `bot.py` - Added AI integration, updated `/check` handler
- `requirements.txt` - Ensured `requests` is present

**Created:**
- `ai_mitigation.py` - Reusable AI mitigation module (optional)
- `FILDZA_AI_INTEGRATION_GUIDE.md` - This guide

---

### 🎯 Summary

**FILDZA_AI_ACTIVE** brings dynamic, AI-powered mitigation recommendations to BocorCheck:

✅ Real-time analysis based on actual breach data  
✅ Low-resource phi3 model (no GPU required)  
✅ Automatic fallback if Ollama unavailable  
✅ Production-ready logging and error handling  
✅ Seamless Telegram bot integration  

---

### 📞 Questions?

Check logs with:
```bash
grep -i "fildza_ai_active" app.log
```

Test AI directly:
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"phi3","prompt":"Hello","stream":false}'
```

---

**Version:** 1.0  
**Status:** Production-Ready  
**Last Updated:** 2026-04-02  
**Keyword:** FILDZA_AI_ACTIVE
