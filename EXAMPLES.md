# Usage Examples

This document provides practical examples of using the AI Doctor Chatbot.

---

## Basic Chat Examples

### Example 1: Simple Symptom Query

```python
import requests

# Simple symptom check
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "I have a headache and fever for 2 days",
        "enable_agents": True,
        "include_sources": True
    }
)

result = response.json()
print(f"Session ID: {result['session_id']}")
print(f"Severity: {result['severity_level']}")
print(f"\nResponse:\n{result['message']}")

if result.get('sources'):
    print("\n📚 Medical Sources:")
    for source in result['sources'][:3]:
        print(f"  - {source['title']}: {source['text'][:100]}...")
```

**Output:**
```
Session ID: 550e8400-e29b-41d4-a716-446655440000
Severity: MODERATE

Response:
Assessment Level: MODERATE

Based on your symptoms of headache and fever lasting 2 days, here's my assessment...

## Possible Conditions (Differential Diagnosis)

1. **Viral Upper Respiratory Infection** (High likelihood)
   - Supporting evidence: Headache and fever are common symptoms...

📚 Medical Sources:
  - CDC Guidelines on Fever Management: Fever is defined as a temperature...
```

### Example 2: Emergency Detection

```python
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "Severe chest pain radiating to left arm and shortness of breath",
        "enable_agents": True
    }
)

result = response.json()

if result.get('emergency_detected'):
    print("🚨 EMERGENCY DETECTED!")
    print(result['message'])
```

**Output:**
```
🚨 EMERGENCY DETECTED!

⚠️ EMERGENCY DETECTED ⚠️

CALL 911 IMMEDIATELY - Possible heart attack

Reasoning: Emergency keywords detected: chest pain, pain radiating to arm,
shortness of breath. This requires immediate medical attention.

**Emergency Contacts:**
• 911: Emergency Services (Fire, Police, Medical)
```

---

## Chat with Patient Profile

### Example 3: Personalized Assessment

```python
# User with medical history
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "I'm experiencing increased thirst and frequent urination",
        "enable_agents": True,
        "context": {
            "patient_profile": {
                "age": 55,
                "chronic_conditions": ["Type 2 Diabetes", "Hypertension"],
                "current_medications": [
                    {"name": "Metformin", "dose": "1000mg twice daily"},
                    {"name": "Lisinopril", "dose": "10mg daily"}
                ],
                "allergies": {
                    "drug": ["Sulfa drugs"],
                    "food": [],
                    "environmental": ["Pollen"]
                }
            }
        }
    }
)

print(response.json()['message'])
```

---

## Multi-turn Conversation

### Example 4: Following Up

```python
# First message
response1 = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={"message": "I have a rash on my arm", "enable_agents": True}
)

session_id = response1.json()['session_id']

# Follow-up question
response2 = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "The rash is red and itchy, appeared 2 days ago",
        "session_id": session_id,
        "enable_agents": True
    }
)

# Agent remembers context
print(response2.json()['message'])
```

---

## Health Profile Management

### Example 5: Creating Health Profile

```python
# First, register and login
register_response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "SecurePassword123!",
        "full_name": "John Doe",
        "date_of_birth": "1980-01-15"
    }
)

# Login to get token
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "johndoe",
        "password": "SecurePassword123!"
    }
)

token = login_response.json()['access_token']

# Create health profile
profile_response = requests.post(
    "http://localhost:8000/api/v1/profile/health-profile",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "height_cm": 180,
        "weight_kg": 75,
        "blood_type": "O+",
        "chronic_conditions": ["Asthma"],
        "allergies": {
            "drug": ["Penicillin"],
            "food": ["Peanuts"],
            "environmental": ["Dust mites"]
        },
        "current_medications": [
            {"name": "Albuterol inhaler", "dose": "As needed"}
        ],
        "smoking_status": "Never",
        "exercise_frequency": "3-4 times per week"
    }
)

print("✅ Health profile created")
```

### Example 6: Viewing Health Timeline

```python
# Get health timeline
timeline = requests.get(
    "http://localhost:8000/api/v1/profile/timeline",
    headers={"Authorization": f"Bearer {token}"}
)

timeline_data = timeline.json()
print(f"Total medical events: {timeline_data['total_records']}")

for event in timeline_data['timeline'][:5]:
    print(f"\n{event['date']}: {event['title']}")
    print(f"  Type: {event['type']}")
    print(f"  Description: {event['description']}")
```

---

## Advanced Features

### Example 7: Batch Symptom Checking

```python
symptoms = [
    "Persistent cough for 3 weeks",
    "Severe headache with visual disturbances",
    "Ankle swelling after long flight"
]

for symptom in symptoms:
    response = requests.post(
        "http://localhost:8000/api/v1/chat/message",
        json={"message": symptom, "enable_agents": True}
    )

    result = response.json()
    print(f"\nSymptom: {symptom}")
    print(f"Severity: {result['severity_level']}")
    print(f"Emergency: {result.get('emergency_detected', False)}")
```

### Example 8: Quick Emergency Check (No Agent Processing)

```python
# Fast emergency check without full agent processing
response = requests.get(
    "http://localhost:8000/api/v1/chat/emergency-check",
    params={"message": "chest pain and difficulty breathing"}
)

emergency_data = response.json()

if emergency_data['is_emergency']:
    print(f"🚨 EMERGENCY: {emergency_data['severity']}")
    print(f"Action: {emergency_data['immediate_action']}")
    print("Contacts:", emergency_data['emergency_contacts'])
else:
    print("Not an emergency")
```

---

## Python Client Example

### Example 9: Full Client Implementation

```python
class DoctorAIClient:
    """Python client for AI Doctor Chatbot"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        self.token = None

    def login(self, username, password):
        """Login and get access token"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()['access_token']
        return self.token

    def chat(self, message, enable_agents=True, include_sources=True):
        """Send a chat message"""
        response = requests.post(
            f"{self.base_url}/api/v1/chat/message",
            json={
                "message": message,
                "session_id": self.session_id,
                "enable_agents": enable_agents,
                "include_sources": include_sources
            }
        )
        response.raise_for_status()
        result = response.json()

        # Store session ID for conversation continuity
        self.session_id = result['session_id']
        return result

    def get_history(self):
        """Get conversation history"""
        if not self.session_id:
            return []

        response = requests.get(
            f"{self.base_url}/api/v1/chat/history/{self.session_id}"
        )
        response.raise_for_status()
        return response.json()

# Usage
client = DoctorAIClient()
client.login("johndoe", "password")

# Start conversation
result = client.chat("I have a persistent cough")
print(result['message'])

# Follow up
result = client.chat("It's been going on for 2 weeks")
print(result['message'])

# View history
history = client.get_history()
print(f"\nConversation has {len(history)} messages")
```

---

## cURL Examples

### Example 10: Using cURL

```bash
# Chat
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a sore throat and cough",
    "enable_agents": true
  }'

# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "SecurePass123!",
    "full_name": "User Name"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user&password=SecurePass123!"

# Create Health Profile (with token)
curl -X POST http://localhost:8000/api/v1/profile/health-profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "height_cm": 175,
    "weight_kg": 70,
    "chronic_conditions": ["diabetes"]
  }'
```

---

## Error Handling

### Example 11: Handling Errors

```python
import requests
from requests.exceptions import RequestException

def safe_chat(message):
    """Chat with error handling"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/message",
            json={"message": message, "enable_agents": True},
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("❌ Request timed out. Please try again.")
        return None

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("❌ Invalid request:", e.response.json())
        elif e.response.status_code == 500:
            print("❌ Server error. Please try again later.")
        else:
            print(f"❌ HTTP Error: {e}")
        return None

    except RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

# Usage
result = safe_chat("I have a headache")
if result:
    print(result['message'])
```

---

## Testing Examples

### Example 12: Unit Testing Chat Endpoint

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    """Test basic chat functionality"""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "I have a fever",
            "enable_agents": True
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "session_id" in data
    assert "message" in data
    assert "severity_level" in data
    assert data["severity_level"] in ["EMERGENCY", "URGENT", "MODERATE", "MINOR", "INFO"]

def test_emergency_detection():
    """Test emergency detection"""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "Severe chest pain",
            "enable_agents": True
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data.get("emergency_detected") == True
    assert "911" in data["message"] or "emergency" in data["message"].lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

**For more examples, see the [API Documentation](http://localhost:8000/api/docs) or [README.md](./README.md)**
