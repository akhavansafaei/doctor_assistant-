# Bilingual Support (English/Persian) - Implementation Guide

## Overview

The AI Doctor Chatbot now supports **bilingual conversations** in English and Persian (Farsi). The bot automatically detects the language of the user's message and responds in the same language.

## Key Features

✅ **Automatic language detection**: Detects English vs Persian/Farsi
✅ **Same-language responses**: Always responds in the user's language
✅ **Bilingual emergency keywords**: Detects emergencies in both languages
✅ **Cultural awareness**: Culturally appropriate medical communication
✅ **Professional terminology**: Medical terms in both languages
✅ **RTL support**: Right-to-left text handling for Persian

---

## How It Works

### 1. Language Detection

**Algorithm:**
```python
# Counts Persian vs English characters
# Persian Unicode ranges: 0x0600-0x06FF, 0xFB50-0xFDFF
# If >30% Persian characters → Persian
# Otherwise → English
# Fallback: Common word matching
```

**Examples:**
```python
detect_language("I have a headache") → "en"
detect_language("سردرد دارم") → "fa"
detect_language("I have درد") → "fa" (mixed, but >30% Persian)
```

### 2. Response Generation

**Flow:**
```
User Message → Language Detection → Inject Language Instruction → LLM Response
```

**Language Instruction:**
```python
# For Persian messages:
"You MUST respond in Persian/Farsi (فارسی).
 Use proper Persian grammar and medical terminology."

# For English messages:
"You MUST respond in English.
 Use clear, professional medical English."
```

---

## Implementation Details

### Components

**1. Language Detector** (`backend/app/utils/language_detector.py`)
```python
from app.utils.language_detector import detect_language

language = detect_language("سلام، سردرد دارم")  # → "fa"
language = detect_language("Hello, I have a headache")  # → "en"
```

**Features:**
- Character-based detection (Persian Unicode ranges)
- Common word matching fallback
- Bilingual medical disclaimers
- Emergency messages in both languages
- RTL detection

**2. Base Agent Updates** (`backend/app/agents/base_agent.py`)
```python
# New method in BaseAgent
def detect_and_format_language(self, user_message: str, context: Optional[Dict] = None):
    language_code = detect_language(user_message)
    language_instruction = get_language_instruction(language_code)
    return language_code, language_instruction
```

**3. Triage Agent** (`backend/app/agents/triage_agent.py`)

**System Prompt Updated:**
```
You are a bilingual medical triage specialist (English/Persian).

BILINGUAL SUPPORT:
- You MUST respond in the SAME LANGUAGE as the user's message
- If user writes in English, respond in English
- If user writes in Persian/Farsi (فارسی), respond in Persian/Farsi
```

**Emergency Keywords (Bilingual):**
```python
EMERGENCY_KEYWORDS = [
    # English
    "chest pain", "difficulty breathing", "severe bleeding",
    # Persian
    "درد قفسه سینه", "تنگی نفس", "خونریزی شدید"
]
```

**4. Agent State** (`backend/app/agents/orchestrator.py`)
```python
class AgentState(TypedDict):
    message: str
    language: Optional[str]  # NEW: "en" or "fa"
    # ... other fields
```

---

## Usage Examples

### English Conversation

**User:**
```
I have a severe headache and dizziness
```

**AI Response:**
```
Based on your symptoms, I'm assessing this as MODERATE severity.

Reasoning: Headaches combined with dizziness can indicate several conditions
ranging from dehydration to more serious issues. The combination warrants
medical evaluation.

Immediate Recommendations:
1. Sit or lie down in a quiet, dark room
2. Drink water to ensure hydration
3. Avoid sudden movements
4. Monitor for worsening symptoms

You should see a doctor within 1-2 days. If symptoms worsen (severe headache,
vision changes, confusion), seek immediate medical care.
```

### Persian Conversation

**User:**
```
سردرد شدید و سرگیجه دارم
```

**AI Response:**
```
بر اساس علائم شما، من این وضعیت را به عنوان شدت متوسط ارزیابی می‌کنم.

استدلال: سردرد همراه با سرگیجه می‌تواند نشان‌دهنده چندین وضعیت از کم‌آبی
بدن تا مسائل جدی‌تر باشد. این ترکیب نیاز به ارزیابی پزشکی دارد.

توصیه‌های فوری:
۱. در یک اتاق ساکت و تاریک بنشینید یا دراز بکشید
۲. آب بنوشید تا از آبرسانی بدن اطمینان حاصل کنید
۳. از حرکات ناگهانی خودداری کنید
۴. علائم را برای بدتر شدن زیر نظر داشته باشید

شما باید ظرف ۱-۲ روز به پزشک مراجعه کنید. اگر علائم بدتر شد (سردرد شدید،
تغییرات بینایی، گیجی)، فوراً به مراقبت پزشکی مراجعه کنید.
```

### Mixed Language (Defaults to Detected Primary)

**User:**
```
I have سردرد شدید
```

**AI Response:** (In Persian, as >30% Persian detected)
```
متوجه شدم که سردرد شدید دارید. لطفاً اطلاعات بیشتری بدهید:
- سردرد از چه زمانی شروع شده است؟
- درد در کدام قسمت سر است؟
- آیا علائم دیگری هم دارید؟
```

---

## Emergency Handling (Bilingual)

### English Emergency

**User:**
```
Severe chest pain, can't breathe
```

**AI Response:**
```
🚨 EMERGENCY DETECTED 🚨

CALL EMERGENCY SERVICES OR GO TO THE NEAREST EMERGENCY ROOM IMMEDIATELY!

This is a potentially life-threatening situation that requires immediate
medical attention.

⚠️ CALL YOUR LOCAL EMERGENCY NUMBER (911 in USA, 115 in Iran) ⚠️
```

### Persian Emergency

**User:**
```
درد شدید قفسه سینه، نفس نمی‌کشم
```

**AI Response:**
```
🚨 وضعیت اضطراری شناسایی شد 🚨

فوراً با اورژانس تماس بگیرید یا به نزدیک‌ترین بیمارستان مراجعه کنید!

این یک وضعیت بالقوه تهدید کننده زندگی است و نیاز به توجه پزشکی فوری دارد.

⚠️ با شماره اورژانس محلی (در ایران: ۱۱۵) تماس بگیرید ⚠️
```

---

## Medical Disclaimers (Bilingual)

### English
```
⚠️ MEDICAL DISCLAIMER:
This AI assistant provides general health information only and is NOT a
substitute for professional medical advice, diagnosis, or treatment. Always
seek the advice of your physician or other qualified health provider.

In case of emergency, call your local emergency number immediately.
```

### Persian
```
⚠️ هشدار پزشکی:
این دستیار هوش مصنوعی تنها اطلاعات سلامتی عمومی ارائه می‌دهد و جایگزین
مشاوره، تشخیص یا درمان پزشکی حرفه‌ای نیست. همیشه برای هرگونه سؤال در مورد
وضعیت سلامتی خود به پزشک مراجعه کنید.

در موارد اضطراری، فوراً با شماره اورژانس محلی تماس بگیرید.
```

---

## Severity Levels (Bilingual Reference)

| English | Persian | Description |
|---------|---------|-------------|
| EMERGENCY | فوریت | Life-threatening |
| URGENT | فوری | Needs care within hours |
| MODERATE | متوسط | See doctor in 1-2 days |
| MINOR | جزئی | Self-care or routine appointment |
| INFO | اطلاعاتی | General health information |

---

## Testing

### Test Cases

```python
# Test language detection
test_cases = [
    ("I have a fever", "en"),
    ("تب دارم", "fa"),
    ("What are flu symptoms?", "en"),
    ("علائم آنفلوانزا چیست؟", "fa"),
    ("سلام دکتر", "fa"),
    ("Hello doctor", "en"),
]

for message, expected_lang in test_cases:
    detected = detect_language(message)
    assert detected == expected_lang
```

### End-to-End Test

**1. English Flow:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'

# Expected: English response with medical advice
```

**2. Persian Flow:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "سردرد دارم"}'

# Expected: Persian response with medical advice
```

---

## Common Persian Medical Terms

### Symptoms (علائم)
- سردرد (headache)
- تب (fever)
- سرفه (cough)
- تنگی نفس (shortness of breath)
- درد شکم (abdominal pain)
- سرگیجه (dizziness)
- تهوع (nausea)
- استفراغ (vomiting)

### Conditions (بیماری‌ها)
- دیابت (diabetes)
- فشار خون بالا (hypertension)
- آسم (asthma)
- آلرژی (allergy)
- عفونت (infection)

### Actions (اقدامات)
- مراجعه به پزشک (see a doctor)
- اورژانس (emergency)
- بستری شدن (hospitalization)
- آزمایش (test/examination)
- دارو (medication)

---

## Frontend Integration

### Language Indicator in UI

```typescript
// Show detected language
<div className="language-indicator">
  {language === 'fa' ? '🇮🇷 فارسی' : '🇬🇧 English'}
</div>
```

### RTL Support for Persian

```css
/* Auto-detect RTL for Persian messages */
.message-persian {
  direction: rtl;
  text-align: right;
  font-family: 'Vazir', 'Tahoma', sans-serif;
}

.message-english {
  direction: ltr;
  text-align: left;
}
```

### Language Toggle (Optional)

```typescript
<button onClick={() => setLanguage(lang === 'en' ? 'fa' : 'en')}>
  {lang === 'en' ? 'فارسی' : 'English'}
</button>
```

---

## Configuration

### Adding New Languages

To add support for a new language (e.g., Arabic):

**1. Update Language Detector:**
```python
# language_detector.py
ARABIC_RANGE = (0x0600, 0x06FF)

@staticmethod
def detect(text: str) -> LanguageCode:
    # Add Arabic character detection
    # Add Arabic common words
```

**2. Update Agent Prompts:**
```python
# triage_agent.py
system_prompt = """You are a multilingual medical assistant (English/Persian/Arabic).
- Respond in the same language as the user
- Support English, Persian (فارسی), and Arabic (العربية)
"""
```

**3. Add Emergency Keywords:**
```python
EMERGENCY_KEYWORDS = [
    # English
    "chest pain",
    # Persian
    "درد قفسه سینه",
    # Arabic
    "ألم في الصدر"
]
```

---

## Performance Considerations

### Language Detection Speed
- Character-based detection: < 1ms
- Negligible overhead on response time

### Token Usage
- Bilingual system prompts: ~100 extra tokens
- Language instruction: ~50 tokens
- Total overhead: ~150 tokens per request

### LLM Support
- **OpenAI (GPT-4/GPT-3.5)**: Excellent English & Persian support
- **Anthropic (Claude)**: Excellent English & Persian support
- **Local models**: May vary, test Persian quality

---

## Troubleshooting

### Problem: Bot responds in wrong language

**Solution:**
```python
# Force language in context
context = {
    "language": "fa"  # Override detection
}
```

### Problem: Poor Persian translation quality

**Solutions:**
1. Use GPT-4 instead of GPT-3.5 (better multilingual)
2. Add more Persian examples to system prompt
3. Use Claude Opus (excellent Persian support)

### Problem: Mixed language in response

**Solution:** Strengthen language instruction:
```python
language_instruction = """
CRITICAL: You MUST respond ENTIRELY in Persian. Do not mix English.
بحرانی: شما باید کاملاً به فارسی پاسخ دهید. انگلیسی را مخلوط نکنید.
"""
```

---

## Future Enhancements

1. **Voice Input/Output**: Text-to-speech in both languages
2. **More Languages**: Arabic, Urdu, Turkish, etc.
3. **Dialect Support**: Different Persian dialects
4. **Translation Mode**: Allow users to see both languages side-by-side
5. **Language Learning**: Help users learn medical terms in both languages

---

## Files Modified/Created

**Created:**
- `backend/app/utils/language_detector.py` (350 lines)

**Modified:**
- `backend/app/agents/base_agent.py` (added detect_and_format_language)
- `backend/app/agents/triage_agent.py` (bilingual prompt & keywords)
- `backend/app/agents/orchestrator.py` (language in state)

---

## Example Conversations

### Scenario 1: Migraine (English)

**User:** "I have a severe migraine with nausea"

**AI:** "Based on your symptoms, I'm assessing this as URGENT severity.

Reasoning: Severe migraine with nausea can be debilitating and may indicate
a more serious migraine variant or other neurological concern.

Immediate Recommendations:
1. Go to a dark, quiet room
2. Apply cold compress to forehead
3. Stay hydrated
4. Avoid bright lights and screens

You should seek medical care within a few hours if:
- Pain is the worst headache of your life
- Accompanied by fever, stiff neck, or confusion
- Vision changes or weakness

A doctor can prescribe appropriate migraine medication."

### Scenario 2: Migraine (Persian)

**User:** "میگرن شدید با حالت تهوع دارم"

**AI:** "بر اساس علائم شما، من این را به عنوان شدت فوری ارزیابی می‌کنم.

استدلال: میگرن شدید همراه با تهوع می‌تواند ناتوان‌کننده باشد و ممکن است نشان‌
دهنده یک نوع جدی‌تر میگرن یا مشکل عصبی دیگر باشد.

توصیه‌های فوری:
۱. به یک اتاق تاریک و ساکت بروید
۲. کمپرس سرد روی پیشانی بگذارید
۳. هیدراته بمانید و آب بنوشید
۴. از نورهای روشن و صفحه‌نمایش دوری کنید

اگر موارد زیر رخ داد، باید ظرف چند ساعت به مراقبت پزشکی مراجعه کنید:
- درد بدترین سردرد زندگی شماست
- همراه با تب، سفتی گردن، یا گیجی است
- تغییرات بینایی یا ضعف وجود دارد

پزشک می‌تواند داروی مناسب میگرن تجویز کند."

---

**The chatbot now serves both English and Persian speakers with culturally appropriate, professional medical guidance!** 🌍🏥
