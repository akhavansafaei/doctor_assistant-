# 🏥 AI Doctor Chatbot - State-of-the-Art Medical Assistant

> **سلامت‌نگار (SalamatNegar)** - Your Intelligent Health Companion

A cutting-edge AI-powered medical chatbot featuring RAG (Retrieval Augmented Generation), multi-agent workflows, advanced safety guardrails, and SOTA (State-of-the-Art) LLM capabilities.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-green.svg)](https://python.langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ Medical Disclaimer

**THIS IS NOT A MEDICAL DEVICE AND SHOULD NOT BE USED FOR EMERGENCY SITUATIONS**

This AI chatbot is designed for educational and informational purposes only. It is NOT:
- A substitute for professional medical advice, diagnosis, or treatment
- Intended to diagnose or treat any medical condition
- A replacement for in-person medical evaluation
- Able to prescribe medications

**Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.**

**In case of emergency, call 911 (US) or your local emergency services immediately.**

---

## 🌟 Features

### Core AI Capabilities
- ✅ **Multi-Agent System**: Specialized agents for triage, diagnosis, and treatment planning
- ✅ **Advanced RAG**: Hybrid retrieval (dense + sparse) with reranking
- ✅ **LangGraph Orchestration**: State-machine based agent coordination
- ✅ **Medical Knowledge Base**: Integration with clinical guidelines and medical literature
- ✅ **Multimodal Support**: Text, voice (STT), and image analysis capabilities

### Safety & Compliance
- ✅ **Emergency Detection**: Automatic identification of life-threatening conditions
- ✅ **Safety Guardrails**: Hallucination prevention and output validation
- ✅ **HIPAA/GDPR Compliance**: Audit logging, data encryption, consent management
- ✅ **Medical Disclaimers**: Automatic disclaimer injection for all medical advice

### Intelligent Features
- ✅ **Differential Diagnosis**: Multiple possible conditions with confidence scores
- ✅ **Evidence-Based Treatment**: Recommendations based on clinical guidelines
- ✅ **Drug Interaction Checking**: Validation against current medications
- ✅ **Symptom Timeline Tracking**: Temporal reasoning for symptom progression
- ✅ **Specialist Routing**: Recommendation for appropriate medical specialty

### Technical Excellence
- ✅ **Vector Database**: Qdrant for semantic search
- ✅ **Real-time Processing**: Async/await throughout
- ✅ **Scalable Architecture**: Microservices-ready design
- ✅ **Comprehensive API**: RESTful endpoints with OpenAPI docs
- ✅ **Docker Support**: One-command deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│              (Web/Mobile/Voice/API)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Agent Orchestrator (LangGraph)              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │    │
│  │  │ Triage   │→ │Diagnostic│→ │Treatment │          │    │
│  │  │ Agent    │  │ Agent    │  │ Agent    │          │    │
│  │  └──────────┘  └──────────┘  └──────────┘          │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Safety & Compliance Layer                 │    │
│  │  • Emergency Detector  • Guardrails  • Audit Log   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   RAG & Data Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Qdrant   │  │PostgreSQL│  │  Redis   │  │   LLM    │   │
│  │ (Vector) │  │   (SQL)  │  │ (Cache)  │  │ (GPT-4)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.**

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (Recommended) OR
- Python 3.11+, PostgreSQL, Redis, Qdrant

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd doctor_assistant-

# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your API keys
# Required: OPENAI_API_KEY, SECRET_KEY
nano .env

# 4. Start all services
docker-compose up -d

# 5. Check health
curl http://localhost:8000/health

# 6. Access API documentation
open http://localhost:8000/api/docs
```

### Option 2: Manual Setup

```bash
# 1. Clone and navigate
git clone <repository-url>
cd doctor_assistant-/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp ../.env.example ../.env
# Edit .env with your configuration

# 5. Start dependencies
# Start PostgreSQL, Redis, and Qdrant separately

# 6. Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 API Documentation

### Interactive Docs

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **WebSocket**: `ws://localhost:8000/api/v1/ws/chat` (see [WEBSOCKET_GUIDE.md](./WEBSOCKET_GUIDE.md))

### WebSocket (Real-time Streaming) 🆕

```javascript
// Connect to WebSocket for token-by-token streaming
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'token') {
        console.log(data.content); // Stream tokens in real-time!
    }
};

ws.send(JSON.stringify({
    message: "I have a headache",
    enable_agents: true
}));
```

**See [WEBSOCKET_GUIDE.md](./WEBSOCKET_GUIDE.md) for complete documentation and examples.**

### Key Endpoints

#### Chat
```bash
# Send a message
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a severe headache and nausea for 2 days",
    "enable_agents": true,
    "include_sources": true
  }'

# Quick emergency check
curl "http://localhost:8000/api/v1/chat/emergency-check?message=chest%20pain"

# Get conversation history
curl http://localhost:8000/api/v1/chat/history/{session_id}
```

#### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=johndoe&password=SecurePass123!"
```

#### Health Profile
```bash
# Create health profile
curl -X POST http://localhost:8000/api/v1/profile/health-profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "height_cm": 175,
    "weight_kg": 70,
    "chronic_conditions": ["hypertension"],
    "allergies": {"drug": ["penicillin"]},
    "current_medications": [{"name": "Lisinopril", "dose": "10mg"}]
  }'
```

---

## 🔧 Configuration

### Environment Variables

Key configurations in `.env`:

```bash
# LLM APIs
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key
COHERE_API_KEY=your-cohere-key

# LLM Settings
PRIMARY_LLM=openai  # or anthropic
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.1

# RAG Settings
TOP_K_RETRIEVAL=10
RERANK_TOP_K=5
HYBRID_ALPHA=0.5  # Balance dense vs sparse

# Safety
ENABLE_GUARDRAILS=True
EMERGENCY_ALERT_EMAIL=emergency@hospital.com

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_HOST=localhost
QDRANT_HOST=localhost
```

---

## 🧪 Testing

```bash
# Run tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Test specific module
pytest tests/test_agents.py -v
```

---

## 📖 Usage Examples

### Example 1: Basic Symptom Assessment

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "I've had a persistent cough for a week with fever",
        "enable_agents": True,
        "include_sources": True
    }
)

result = response.json()
print(f"Severity: {result['severity_level']}")
print(f"Response: {result['message']}")
```

### Example 2: With Patient Profile

```python
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "Sharp pain in lower abdomen",
        "enable_agents": True,
        "context": {
            "patient_profile": {
                "age": 45,
                "chronic_conditions": ["diabetes"],
                "current_medications": [
                    {"name": "Metformin", "dose": "500mg twice daily"}
                ],
                "allergies": {"drug": ["sulfa drugs"]}
            }
        }
    }
)
```

### Example 3: Emergency Detection

```python
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "Severe chest pain radiating to left arm, shortness of breath",
        "enable_agents": True
    }
)

# Response will include emergency_detected: true
# And immediate action instructions
```

---

## 🛡️ Safety Features

### Emergency Detection
- Automatically detects life-threatening conditions
- Provides immediate action instructions
- Routes to emergency services when necessary

### Hallucination Prevention
- Cross-references LLM outputs with knowledge base
- Validates medical claims
- Flags inappropriate certainty

### Compliance
- HIPAA-compliant audit logging
- GDPR right to erasure
- Data anonymization for analytics
- Consent management

---

## 🗺️ Roadmap

### Phase 1: Current ✅
- Multi-agent RAG system
- Safety guardrails
- Basic chat interface
- Emergency detection

### Phase 2: In Progress 🚧
- Multimodal support (images, voice)
- Real-time vital sign integration
- Telemedicine preparation
- Advanced analytics dashboard

### Phase 3: Future 🔮
- Wearable device integration
- Predictive health analytics
- Digital twin modeling
- FHIR standard integration
- Blockchain medical records

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 and embeddings
- **Anthropic** for Claude
- **LangChain** for agent framework
- **Qdrant** for vector database
- **FastAPI** for web framework

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/your-username/doctor_assistant/issues)
- **Email**: support@salamatnegar.com
- **Documentation**: [Full Docs](https://docs.salamatnegar.com)

---

## ⚖️ Legal Notice

This software is provided "as is" without warranty of any kind. The developers are not liable for any damages arising from its use. This is an educational project and should not be used for actual medical decision-making without proper medical supervision.

By using this software, you acknowledge that:
- This is NOT a medical device
- It does NOT replace professional medical advice
- You will seek professional medical care for health concerns
- The developers are not responsible for medical decisions made based on this software

---

**Made with ❤️ for better healthcare accessibility**
