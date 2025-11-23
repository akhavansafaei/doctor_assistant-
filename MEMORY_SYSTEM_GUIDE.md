# Memory System for AI Doctor Chatbot

## Overview

The AI Doctor Chatbot now includes an intelligent **short-term and long-term memory system** that maintains conversational context across sessions, enabling true continuity of care.

## Key Features

✅ **Short-term memory**: Current session messages (within-chat context)
✅ **Long-term memory**: Past conversations retrieved from database
✅ **Automatic summarization**: Conversations summarized when too long
✅ **Two-level thresholds**: Individual chat + total memory compression
✅ **LLM-based summaries**: Medical-focused intelligent summarization
✅ **Context injection**: Memory automatically added to agent prompts
✅ **Efficient token usage**: Smart compression prevents context overflow

---

## How It Works

### 1. Memory Types

**Short-term Memory (Within Session)**
- All messages in the current chat session
- Stored in conversation history
- Always included in agent context
- No summarization needed (current conversation)

**Long-term Memory (Past Sessions)**
- Previous conversations from database
- Retrieved based on recency (last 30 days default)
- Automatically summarized if too long
- Injected into agent prompts for continuity

### 2. Threshold System

#### **Threshold 1: Single Conversation**

```python
SINGLE_CHAT_TOKEN_THRESHOLD = 2000  # If chat > 2000 tokens
SINGLE_CHAT_SUMMARY_TARGET = 500    # Summarize to ~500 tokens
SINGLE_CHAT_MESSAGE_THRESHOLD = 30   # Or if > 30 messages
```

**When triggered:**
- A single past conversation exceeds 2000 tokens OR 30 messages
- **Action**: LLM creates a structured medical summary (~500 tokens)

**Summary Format:**
```
Chief Complaint: [Main issue discussed]
Key Symptoms: [Symptoms mentioned]
Medical Advice Given: [Recommendations]
Medications/Treatments: [Any prescribed]
Follow-up: [Follow-up instructions]
Red Flags: [Warnings or concerns]
```

#### **Threshold 2: Total Memory**

```python
TOTAL_MEMORY_TOKEN_THRESHOLD = 8000  # If all memory > 8000 tokens
TOTAL_MEMORY_SUMMARY_TARGET = 2000   # Compress to ~2000 tokens
```

**When triggered:**
- Combined token count of ALL past conversations exceeds 8000
- **Action**:
  1. Keep 2 most recent conversations as-is
  2. Create comprehensive summary of older conversations
  3. Result: Recent context + historical overview

**Comprehensive Summary Format:**
```
Medical History Overview: [Patient's journey]
Chronic Conditions: [Ongoing conditions]
Recurring Symptoms: [Patterns across visits]
Medications History: [All medications over time]
Allergies/Contraindications: [Warnings]
Key Medical Advice: [Important recommendations]
Trends & Observations: [Patterns noticed]
```

---

## Implementation Details

### Architecture

```
┌─────────────────────────────────────────────┐
│          User sends message                 │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  MemoryManager                              │
│  - Loads past conversations from DB         │
│  - Checks thresholds                        │
│  - Triggers summarization if needed         │
│  - Formats memory for prompt                │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  ConversationSummarizer                     │
│  - Uses LLM (GPT-3.5/Claude Haiku)         │
│  - Medical-focused summarization            │
│  - Structured output                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Memory injected into agent prompts         │
│  - Triage Agent                             │
│  - Diagnostic Agent                         │
│  - Treatment Agent                          │
└─────────────────────────────────────────────┘
```

### File Structure

```
backend/app/memory/
├── __init__.py
├── memory_manager.py       # Core memory management
└── summarizer.py           # LLM-based summarization

backend/app/agents/
├── base_agent.py           # Updated with memory formatting
├── triage_agent.py         # Uses memory context
├── diagnostic_agent.py     # Uses memory context (ready)
└── treatment_agent.py      # Uses memory context (ready)

backend/app/api/
└── websocket_enhanced.py   # Memory integration (TODO section)
```

---

## Usage Example

### Backend Code

```python
from app.memory import MemoryManager
from sqlalchemy.orm import Session

# Initialize memory manager
memory_manager = MemoryManager(
    db=db_session,
    user_id=current_user_id
)

# Get formatted memory for prompts
long_term_memory = await memory_manager.format_memory_for_prompt(
    current_session_id=session_id,
    include_short_term=False  # Short-term already in conversation_history
)

# Get memory statistics (for monitoring)
memory_stats = await memory_manager.get_memory_summary(session_id)
print(f"Long-term conversations: {memory_stats['long_term_conversations']}")
print(f"Summarized: {memory_stats['summarized_conversations']}")
print(f"Total tokens: {memory_stats['total_long_term_tokens']}")

# Pass to agent orchestrator
state = {
    "message": user_message,
    "patient_profile": health_profile,
    "conversation_history": short_term_messages,
    "long_term_memory": long_term_memory,  # NEW!
    "memory_summary": memory_stats
}

result = await orchestrator.graph.ainvoke(state)
```

### Agent Usage (Automatic)

The memory is automatically injected into agent prompts:

```python
# In base_agent.py
memory_context = self.format_memory_context(
    context.get("long_term_memory", "")
)

# Added to prompt
assessment_prompt = f"""
{user_message}
{patient_profile_context}
{memory_context}  # ← Long-term memory injected here
{medical_knowledge_context}
"""
```

---

## Memory Lifecycle

### 1. **First Conversation**
```
User: "I have a headache"
└─> No long-term memory (new patient)
└─> System responds with general advice
└─> Conversation saved to DB
```

### 2. **Second Conversation (Week Later)**
```
User: "My headache is back"
└─> Memory Manager retrieves past conversation
    ├─> Chat 1: 15 messages, 800 tokens
    └─> Below threshold, no summarization
└─> System: "I see you had a headache last week. Has it been continuous?"
```

### 3. **Fifth Conversation (After Multiple Visits)**
```
User: "Headache again, worse this time"
└─> Memory Manager retrieves 4 past conversations
    ├─> Chat 1: 35 messages, 2500 tokens → Summarized to 500 tokens
    ├─> Chat 2: 28 messages, 1800 tokens → Kept as-is
    ├─> Chat 3: 40 messages, 3000 tokens → Summarized to 500 tokens
    └─> Chat 4: 20 messages, 1200 tokens → Kept as-is
    Total: 4200 tokens (below 8000, no comprehensive summary)
└─> System sees pattern: "This is your 5th headache episode.
    Last time we discussed trying preventive medication..."
```

### 4. **After Many Conversations (Total Memory > 8000 tokens)**
```
User: "Feeling dizzy today"
└─> Memory Manager retrieves 10 past conversations
    ├─> Total: 12,000 tokens (exceeds threshold!)
    └─> Compression strategy:
        ├─> Keep 2 most recent (full detail)
        └─> Create comprehensive summary of older 8 conversations
    Result: 2 recent + 1 comprehensive summary ≈ 3500 tokens
└─> System has: Recent detail + Historical overview
```

---

## Configuration

### Adjusting Thresholds

**In `backend/app/memory/memory_manager.py`:**

```python
class MemoryThresholds:
    # Increase for longer individual summaries
    SINGLE_CHAT_TOKEN_THRESHOLD = 2000
    SINGLE_CHAT_SUMMARY_TARGET = 500

    # Increase for more historical context
    TOTAL_MEMORY_TOKEN_THRESHOLD = 8000
    TOTAL_MEMORY_SUMMARY_TARGET = 2000

    # Time-based settings
    RECENT_CONVERSATIONS_DAYS = 30      # Consider last 30 days
    MAX_CONVERSATIONS_TO_RETRIEVE = 10  # Max past conversations
```

### Custom Thresholds Per Session

```python
from app.memory import MemoryThresholds

custom_thresholds = MemoryThresholds()
custom_thresholds.TOTAL_MEMORY_TOKEN_THRESHOLD = 10000  # More context
custom_thresholds.RECENT_CONVERSATIONS_DAYS = 60        # 2 months history

memory_manager = MemoryManager(
    db=db,
    user_id=user_id,
    thresholds=custom_thresholds
)
```

---

## Benefits for Medical Care

### 1. **Continuity of Care**
```
Week 1: "I have insomnia"
Week 2: "Still can't sleep"
Week 3: "Sleep is better, but feeling anxious"

AI remembers progression, asks targeted follow-ups:
"You mentioned last week that sleep improved.
 Is the anxiety new, or related to the sleep issues?"
```

### 2. **Medication Tracking**
```
Month 1: Prescribed Lisinopril 10mg
Month 2: Increased to 20mg due to BP
Month 3: User reports dizziness

AI recalls medication changes:
"You're on Lisinopril 20mg since last month.
 Dizziness could be related to the dose increase..."
```

### 3. **Pattern Recognition**
```
Jan: Migraine with aura
Mar: Migraine with aura
May: Migraine with aura

AI detects pattern:
"This is your 3rd migraine in 5 months.
 Have you noticed any triggers?
 Consider discussing preventive treatment with your doctor."
```

### 4. **Avoiding Repeated Questions**
```
Without memory:
AI: "Do you have any chronic conditions?"
User: "I told you last time, I have diabetes!"

With memory:
AI: "Given your diabetes history, let's check your blood sugar levels first..."
```

---

## Testing the Memory System

### Test Scenario 1: Single Chat Summarization

```bash
# 1. Create a long conversation (> 30 messages)
# 2. Check if it gets summarized

from app.memory import MemoryManager, ConversationSummarizer

messages = [
    {"role": "user", "content": "I have a headache"},
    {"role": "assistant", "content": "Can you describe the pain?"},
    # ... 30+ messages
]

summarizer = ConversationSummarizer()
summary = await summarizer.summarize_conversation(messages, target_length=500)
print(summary)

# Expected output: Structured medical summary
```

### Test Scenario 2: Total Memory Compression

```bash
# Simulate 10 past conversations totaling > 8000 tokens
# Check if older ones get compressed into comprehensive summary

memory_manager = MemoryManager(db=db, user_id=1)
long_term = await memory_manager.get_long_term_memory(current_session_id="test")

for memory in long_term:
    if memory.is_summarized:
        print(f"Summarized: {memory.summary[:100]}...")
```

### Test Scenario 3: End-to-End

```bash
# 1. User has 5 past conversations about headaches
# 2. User sends new message about headaches
# 3. Check if AI references past history

# Expected response should mention:
# - Previous headache episodes
# - Past advice given
# - Changes or patterns
```

---

## Monitoring Memory Usage

### Get Memory Statistics

```python
memory_stats = await memory_manager.get_memory_summary(session_id)

print(f"""
Memory Stats:
- Short-term messages: {memory_stats['short_term_messages']}
- Long-term conversations: {memory_stats['long_term_conversations']}
- Summarized conversations: {memory_stats['summarized_conversations']}
- Total long-term tokens: {memory_stats['total_long_term_tokens']}

Thresholds:
- Single chat threshold: {memory_stats['thresholds']['single_chat_token_threshold']}
- Total memory threshold: {memory_stats['thresholds']['total_memory_token_threshold']}
""")
```

### Clear Old Conversations

```python
# Delete conversations older than 90 days
deleted_count = await memory_manager.clear_old_memories(days=90)
print(f"Deleted {deleted_count} old conversations")
```

---

## TODO: Production Integration

Currently, the memory system is **fully implemented but not yet integrated** into the WebSocket endpoint. To complete the integration:

### 1. Add Database Session to WebSocket

```python
# In websocket_enhanced.py
from app.database import get_db

@router.websocket("/ws/chat/enhanced")
async def websocket_chat_with_onboarding(
    websocket: WebSocket,
    db: Session = Depends(get_db)  # Add DB dependency
):
    # ... existing code ...
```

### 2. Extract User ID from JWT Token

```python
from app.auth import get_current_user_from_websocket

user = await get_current_user_from_websocket(websocket)
user_id = user.id
```

### 3. Initialize Memory Manager

```python
# In handle_chat_with_profile()
memory_manager = MemoryManager(db=db, user_id=user_id)

long_term_memory = await memory_manager.format_memory_for_prompt(
    current_session_id=session_id,
    include_short_term=False
)

memory_summary = await memory_manager.get_memory_summary(session_id)
```

### 4. Test End-to-End

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Test with multiple conversations
# Verify memory is retrieved and summarized correctly
```

---

## Advanced Features

### 1. Entity Extraction

```python
# Extract specific medical entities from conversations
entities = await summarizer.extract_key_medical_entities(messages)

print(f"""
Symptoms: {entities['symptoms']}
Conditions: {entities['conditions']}
Medications: {entities['medications']}
Allergies: {entities['allergies']}
Warnings: {entities['warnings']}
""")
```

### 2. Continuity Context

```python
# Generate brief continuity context connecting past to present
continuity = await summarizer.generate_continuity_context(
    past_summaries=[summary1, summary2, summary3],
    current_query="I'm feeling dizzy"
)

# Output: "Patient previously reported hypertension and started Lisinopril
#         last month. Dizziness could be medication-related."
```

---

## Performance Considerations

### Token Estimation
- 1 token ≈ 4 characters (rough approximation)
- Actual tokens may vary by model

### LLM Costs
- Summarization uses cheaper models (GPT-3.5-Turbo or Claude Haiku)
- Typical cost per summary: $0.001 - $0.005
- Cost-effective for improved continuity

### Database Queries
- Retrieves max 10 conversations per session
- Uses indexes on `user_id`, `created_at`, `session_id`
- Efficient even with large conversation history

---

## Future Enhancements

1. **Semantic Memory Retrieval**: Use embeddings to find relevant past conversations based on topic similarity, not just recency
2. **Importance Scoring**: Keep important conversations (emergency visits, diagnoses) even if old
3. **Memory Decay**: Gradually reduce weight of very old information
4. **Shared Family Memory**: Link memories across family member accounts
5. **Memory Export**: Allow users to download conversation summaries
6. **Memory Visualization**: Dashboard showing conversation timeline and patterns

---

**The memory system transforms the chatbot from a stateless Q&A tool into a continuous care companion!** 🧠✨
