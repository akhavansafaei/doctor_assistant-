# Intelligent Profile Onboarding System

## Overview

This system implements an intelligent, conversational health profile collection that:
1. ✅ Checks if user has a complete health profile
2. ✅ If not, triggers LLM-guided conversational onboarding
3. ✅ Extracts structured data from natural language responses
4. ✅ Auto-fills health profile automatically
5. ✅ Injects profile context into all future chats for personalized advice
6. ✅ Allows manual profile editing in settings

---

## How It Works

### 1. First Chat Experience

**User without profile:**
```
User: "I have a headache"

AI: Hi! 👋 To provide you with the most accurate health advice, I'd like to
    learn a bit about you. This will only take a minute and helps me give you
    personalized care. Shall we begin?

User: "Yes, sure"

AI: Great! Let's start simple - how old are you?

User: "I'm 35"

AI: Thanks! And what's your biological gender? This helps with gender-specific
    health considerations.

User: "Male"

AI: Perfect! Do you know your height and current weight? This helps assess
    various health metrics.

User: "I'm 180cm and weigh 75kg"

AI: Do you have any ongoing health conditions or chronic illnesses? For example,
    diabetes, high blood pressure, asthma, etc. If none, just say 'none'.

User: "I have type 2 diabetes"

AI: Great! Now, do you have any allergies? This could be to medications, foods,
    or environmental things like pollen.

User: "I'm allergic to penicillin and peanuts"

... (continues through all questions)

AI: Perfect! Thank you for sharing that information. I now have a good
    understanding of your health profile, which will help me provide more
    personalized and accurate advice.

📋 **Profile Summary**: Age: 35 | Chronic conditions: diabetes |
    Medications: Metformin | Allergies: penicillin, peanuts

    Now, about your headache - considering your diabetes and current medications...
```

### 2. Subsequent Chats

**User with complete profile:**
```
User: "I'm feeling dizzy"

AI: [Internally uses profile context]
    Given that you have diabetes and are on Metformin, dizziness could be related
    to blood sugar levels...
```

---

## Backend Implementation

### 1. Onboarding Agent

**File: `backend/app/agents/onboarding_agent.py`**

```python
class OnboardingAgent(BaseAgent):
    """Conversationally collects health information"""

    # Questions asked one at a time:
    1. Age
    2. Gender
    3. Height & Weight
    4. Chronic conditions
    5. Allergies (drug/food/environmental)
    6. Current medications
    7. Past surgeries
    8. Lifestyle (smoking, alcohol, exercise)
    9. Emergency contact (optional)
```

**Key Features:**
- Asks ONE question at a time
- Accepts "none"/"no" gracefully
- Explains WHY information is needed
- Friendly, conversational tone
- LLM extracts structured data from natural language

### 2. Profile Completion Checker

```python
class ProfileCompletionChecker:
    """Checks if profile is complete enough"""

    # Required fields:
    - age
    - chronic_conditions (can be empty)
    - allergies (can be empty)

    # Optional but recommended:
    - height, weight
    - current_medications
    - smoking_status
```

### 3. Profile Context Injection

**File: `backend/app/utils/profile_context.py`**

```python
def format_profile_for_prompt(health_profile):
    """
    Formats profile into context string for LLM:

    PATIENT HEALTH PROFILE:
    Basic Info: Age: 35, Gender: male, Height: 180cm, Weight: 75kg (BMI: 23.1)
    Chronic Conditions: Type 2 Diabetes
    Allergies: Drug: penicillin; Food: peanuts
    Current Medications: Metformin (500mg twice daily)

    IMPORTANT: Consider this patient profile when providing medical advice.
    Account for their chronic conditions, medications, and allergies.
    """
```

**Critical Warnings:**
```python
def get_critical_warnings(health_profile):
    """
    Extracts warnings that should be highlighted:

    ⚠️ DRUG ALLERGIES: Patient is allergic to penicillin. Avoid recommending
       these medications or related compounds.

    ⚠️ HIGH-RISK CONDITIONS: Patient has diabetes. Exercise extra caution
       with medication recommendations.
    """
```

### 4. Enhanced WebSocket Endpoint

**File: `backend/app/api/websocket_enhanced.py`**

**Flow:**
1. User connects
2. Check if profile exists and is complete
3. If NO → Start onboarding flow
4. If YES → Proceed to normal chat with profile context

```python
@router.websocket("/ws/chat/enhanced")
async def websocket_chat_with_onboarding(websocket: WebSocket):
    # Load profile
    profile = await load_user_health_profile(user_id)
    profile_complete = ProfileCompletionChecker.is_profile_complete(profile)

    if not profile_complete:
        # Start onboarding
        await handle_onboarding(...)
    else:
        # Normal chat with profile context
        await handle_chat_with_profile(...)
```

---

## Frontend Implementation

### 1. Profile Completion Indicator

Show in sidebar/header:

```typescript
// components/ProfileCompletionBanner.tsx
<div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
  <div className="flex items-center">
    <div className="flex-1">
      <p className="text-sm font-medium text-yellow-800">
        Complete your health profile for personalized advice
      </p>
      <div className="mt-2 bg-yellow-200 rounded-full h-2">
        <div
          className="bg-yellow-600 h-2 rounded-full transition-all"
          style={{ width: `${completionPercentage}%` }}
        />
      </div>
      <p className="text-xs text-yellow-700 mt-1">
        {completionPercentage}% complete
      </p>
    </div>
    <button className="ml-4 text-sm font-medium text-yellow-800 hover:text-yellow-900">
      Complete Now →
    </button>
  </div>
</div>
```

### 2. Manual Profile Form

**Page: `ProfilePage.tsx`**

Comprehensive form with sections:

```typescript
<ProfileForm>
  <Section title="Basic Information">
    <Input name="age" type="number" label="Age" />
    <Select name="gender" label="Gender" options={['male', 'female', 'other']} />
    <Input name="height_cm" type="number" label="Height (cm)" />
    <Input name="weight_kg" type="number" label="Weight (kg)" />
    <Input name="blood_type" label="Blood Type" placeholder="e.g., O+" />
  </Section>

  <Section title="Medical History">
    <TagInput
      name="chronic_conditions"
      label="Chronic Conditions"
      placeholder="e.g., diabetes, hypertension"
    />
  </Section>

  <Section title="Allergies">
    <TagInput name="allergies.drug" label="Drug Allergies" />
    <TagInput name="allergies.food" label="Food Allergies" />
    <TagInput name="allergies.environmental" label="Environmental Allergies" />
  </Section>

  <Section title="Current Medications">
    <MedicationList name="current_medications" />
    {/* Add/remove medications dynamically */}
  </Section>

  <Section title="Lifestyle">
    <Select name="smoking_status" label="Smoking Status" />
    <Select name="alcohol_consumption" label="Alcohol Consumption" />
    <Select name="exercise_frequency" label="Exercise Frequency" />
  </Section>
</ProfileForm>
```

### 3. Chat Integration

**Modified `useWebSocket.ts`:**

```typescript
// Handle onboarding messages
if (data.type === 'onboarding_question') {
  // Show special UI for onboarding
  showOnboardingUI(data.question);
} else if (data.type === 'onboarding_complete') {
  // Show success, hide onboarding UI
  toast.success('Profile completed! 🎉');
  updateProfileCompletion(100);
}
```

### 4. Settings Integration

**Toggle for manual profile entry:**

```typescript
// SettingsPage.tsx
<Setting>
  <label>Health Profile</label>
  <p className="text-sm text-gray-600">
    You can either fill your profile manually or let our AI collect it
    conversationally during your first chat.
  </p>
  <div className="mt-2 space-x-2">
    <Button onClick={() => navigate('/profile')}>
      Edit Profile Manually
    </Button>
    <Button variant="outline" onClick={restartOnboarding}>
      Restart Conversational Onboarding
    </Button>
  </div>
</Setting>
```

---

## Data Extraction Example

### Natural Language → Structured Data

**User says:**
```
"I'm 45 years old, female, about 5'6" and 150 pounds. I have high blood pressure
and take Lisinopril 10mg daily. I'm allergic to penicillin."
```

**LLM extracts:**
```json
{
  "age": 45,
  "gender": "female",
  "height_cm": 168,
  "weight_kg": 68,
  "chronic_conditions": ["hypertension"],
  "current_medications": [
    {
      "name": "Lisinopril",
      "dose": "10mg daily"
    }
  ],
  "allergies": {
    "drug": ["penicillin"],
    "food": [],
    "environmental": []
  }
}
```

---

## Profile Context in Action

### Without Profile:
```
User: "I have a headache"
AI: "Headaches can have many causes. Can you describe the pain? When did it start?"
```

### With Profile:
```
User: "I have a headache"
AI (sees profile):
   "Given that you have diabetes and are on Metformin, let's consider a few
   possibilities. Has your blood sugar been stable recently? Headaches can
   sometimes be related to blood sugar fluctuations..."
```

---

## API Endpoints

### Get Profile Completion Status

```http
GET /api/v1/profile/completion-status

Response:
{
  "complete": false,
  "completion_percentage": 60,
  "missing_fields": ["height_cm", "weight_kg", "exercise_frequency"]
}
```

### Save Extracted Profile

```http
POST /api/v1/profile/save-from-onboarding

Body:
{
  "extracted_data": {
    "age": 35,
    "chronic_conditions": ["diabetes"],
    ...
  }
}
```

### Restart Onboarding

```http
POST /api/v1/profile/restart-onboarding

Response:
{
  "onboarding_session_id": "uuid",
  "first_question": "Hi! To provide you with..."
}
```

---

## Benefits

### 1. Better User Experience
- ✅ No boring forms to fill
- ✅ Natural conversation
- ✅ Can skip/come back later
- ✅ Both options available (auto + manual)

### 2. Higher Completion Rates
- ✅ Conversational approach more engaging
- ✅ One question at a time less overwhelming
- ✅ Explains why information is needed

### 3. Better Medical Advice
- ✅ Personalized recommendations
- ✅ Considers drug allergies automatically
- ✅ Accounts for chronic conditions
- ✅ Checks medication interactions

### 4. Safety
- ✅ Critical allergies highlighted
- ✅ High-risk conditions flagged
- ✅ Polypharmacy warnings

---

## Testing

### Test Onboarding Flow:

```bash
# 1. Create new user (no profile)
# 2. Send first message
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "I have a fever"}'

# Expected: Onboarding starts
# Response: "Hi! To provide you with the most accurate health advice..."

# 3. Answer questions
# 4. Profile gets auto-filled
# 5. Future chats include profile context
```

### Test Profile Context:

```bash
# User with diabetes
# Message: "I'm feeling tired"
# Expected response considers diabetes:
# "Fatigue in diabetes can be related to blood sugar levels..."
```

---

## Future Enhancements

1. **Voice Onboarding**: Speak answers instead of typing
2. **Smart Skip**: Skip questions based on previous answers
3. **Profile Updates**: Ask to update profile periodically
4. **Family Profiles**: Manage profiles for family members
5. **Integration with Wearables**: Auto-fill from fitness trackers

---

## Files Created

1. `backend/app/agents/onboarding_agent.py` - Conversational profile collection
2. `backend/app/utils/profile_context.py` - Profile formatting for LLM prompts
3. `backend/app/api/websocket_enhanced.py` - Enhanced WebSocket with onboarding
4. Frontend components (to be created):
   - `ProfileCompletionBanner.tsx`
   - `ProfileForm.tsx`
   - `OnboardingChat.tsx`

---

**This creates a seamless, intelligent health profile collection system that makes the chatbot truly personalized!** 🏥✨
