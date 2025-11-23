# ⚖️ AI Law Assistant - State-of-the-Art Legal Support System

> **قانون‌یار (GhanooonYar)** - Your Intelligent Legal Companion

A cutting-edge AI-powered legal assistant featuring RAG (Retrieval Augmented Generation), multi-agent workflows, advanced safety guardrails, and SOTA (State-of-the-Art) LLM capabilities.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-green.svg)](https://python.langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ Legal Disclaimer

**THIS IS NOT A SUBSTITUTE FOR PROFESSIONAL LEGAL ADVICE AND SHOULD NOT BE USED FOR URGENT LEGAL MATTERS WITHOUT ATTORNEY CONSULTATION**

This AI legal assistant is designed for educational and informational purposes only. It is NOT:
- A substitute for professional legal advice, consultation, or representation
- Intended to create an attorney-client relationship
- A replacement for consultation with a qualified attorney
- Able to provide legal opinions or represent you in court

**Always seek the advice of a qualified attorney or other legal professional with any questions you may have regarding a legal matter.**

**In case of urgent legal deadlines, court dates, or time-sensitive matters, consult with an attorney immediately.**

---

## 🌟 Features

### Core AI Capabilities
- ✅ **Multi-Agent System**: Specialized agents for intake, legal analysis, and advice
- ✅ **Advanced RAG**: Hybrid retrieval (dense + sparse) with reranking for legal documents
- ✅ **LangGraph Orchestration**: State-machine based agent coordination
- ✅ **Legal Knowledge Base**: Integration with statutes, case law, and legal regulations
- ✅ **Multimodal Support**: Text, voice (STT), and document analysis capabilities

### Safety & Compliance
- ✅ **Urgency Detection**: Automatic identification of time-sensitive legal matters
- ✅ **Safety Guardrails**: Hallucination prevention and output validation
- ✅ **Privacy Compliance**: Audit logging, data encryption, consent management
- ✅ **Legal Disclaimers**: Automatic disclaimer injection for all legal guidance

### Intelligent Features
- ✅ **Legal Issue Spotting**: Identification of multiple potential legal issues
- ✅ **Legal Analysis**: Analysis based on applicable statutes and case law
- ✅ **Deadline Tracking**: Detection of critical legal deadlines and statutes of limitations
- ✅ **Jurisdiction Awareness**: Consideration of applicable laws based on jurisdiction
- ✅ **Practice Area Routing**: Recommendation for appropriate legal specialty

### Bilingual Support
- ✅ **English/Persian (Farsi)**: Automatic language detection and response
- ✅ **Localized Legal Terms**: Proper legal terminology in both languages
- ✅ **Seamless Switching**: Natural language switching within conversations

### Advanced Architecture
- ✅ **Intelligent Memory System**:
  - **Short-term memory**: Within-conversation context retention
  - **Long-term memory**: Automatic summarization and retrieval of past case context
  - **Smart Context Injection**: Relevant historical information included automatically
- ✅ **Profile Management**: Comprehensive client legal profiles
- ✅ **WebSocket Support**: Real-time streaming responses
- ✅ **Conversation Management**: Session persistence and history tracking

---

## 🏗️ Architecture

### Multi-Agent Workflow

```
┌─────────────────┐
│  User Inquiry   │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Intake Agent       │  ← Detects urgency & routes
│  - Urgency Assessment
│  - Keyword Detection
│  - Initial Routing
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Legal Analysis      │  ← Identifies legal issues
│ Agent               │
│  - Issue Spotting
│  - Statute/Case Law
│  - Risk Assessment
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Legal Advice Agent  │  ← Provides guidance
│  - Options Analysis
│  - Recommendations
│  - Next Steps
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Response to User   │
│  + Legal Disclaimer │
└─────────────────────┘
```

### Technology Stack

#### Backend
- **Framework**: FastAPI (async/await)
- **AI/LLM**:
  - OpenAI GPT-4 Turbo / Anthropic Claude
  - LangChain for LLM orchestration
  - LangGraph for multi-agent workflows
- **Vector Database**: Qdrant (for RAG)
- **Database**: PostgreSQL (user data, conversations)
- **Cache**: Redis (session management)
- **Embeddings**: OpenAI text-embedding-3-large

#### Frontend
- **Framework**: React 18 + TypeScript
- **State Management**: Zustand
- **UI Library**: Material-UI (MUI)
- **Internationalization**: Custom i18n system (English/Persian)
- **Real-time**: WebSocket client

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Qdrant (vector database)

### Environment Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd law_assistant
```

2. **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your API keys and database credentials
nano .env
```

3. **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file (if needed)
cp .env.example .env
```

4. **Database Setup**
```bash
# Run PostgreSQL migrations
cd backend
alembic upgrade head
```

5. **Start Services**
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Redis (if not running as service)
redis-server

# Terminal 4: Qdrant (if not running as service)
docker run -p 6333:6333 qdrant/qdrant
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📖 Documentation

Detailed documentation is available in the `/docs` folder:
- [Architecture Guide](./ARCHITECTURE.md) - System design and component overview
- [Profile & Onboarding](./PROFILE_ONBOARDING_GUIDE.md) - Client profile management
- [Memory System](./MEMORY_SYSTEM_GUIDE.md) - Short-term and long-term memory
- [WebSocket Guide](./WEBSOCKET_GUIDE.md) - Real-time communication
- [Bilingual Support](./BILINGUAL_SUPPORT_GUIDE.md) - English/Persian implementation
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment

---

## 🧪 Example Use Cases

### General Legal Inquiry
```
User: "I received a lease termination notice. What are my rights?"

AI: [Intake Agent assesses urgency]
    [Legal Analysis Agent identifies: tenant rights, lease law, notice requirements]
    [Legal Advice Agent provides: options, timeline, recommended actions]

Response: Based on your situation, several legal issues may apply...
          1. Lease termination requirements (varies by jurisdiction)
          2. Tenant rights and protections
          3. Notice period compliance

          I recommend consulting with a tenant rights attorney to...
```

### Time-Sensitive Matter
```
User: "Court date tomorrow, haven't prepared"

AI: [CRITICAL_URGENT detected]
    → Immediate recommendation to contact attorney
    → Explains consequences of missing court date
    → Provides emergency legal resources
```

---

## 🔒 Security & Privacy

- **Data Encryption**: All data encrypted at rest and in transit (TLS 1.3)
- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control (Client, Lawyer, Admin)
- **Audit Logging**: Complete audit trail of all actions
- **GDPR Compliance**: Right to deletion, data export, consent management
- **Confidentiality**: Attorney-client privilege considerations in design

---

## 🛠️ Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd backend
pylint app/
black app/

# Frontend linting
cd frontend
npm run lint
```

---

## 📊 Roadmap

- [ ] Additional legal practice area modules (Tax, IP, Immigration)
- [ ] Court filing integration
- [ ] Document generation (contracts, letters, motions)
- [ ] Legal calendar with deadline reminders
- [ ] Multi-jurisdiction support
- [ ] Attorney collaboration features
- [ ] Mobile applications (iOS/Android)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## ⚠️ Important Notes

1. **Not Legal Advice**: This system provides general legal information, not legal advice
2. **Jurisdiction Specific**: Laws vary by location - always verify with local attorney
3. **No Attorney-Client Relationship**: Using this system does not create any legal relationship
4. **For Educational Purposes**: This is a demonstration of AI capabilities in legal domain
5. **Professional Consultation Required**: Always consult with a qualified attorney for legal matters

---

## 📧 Contact

For questions, issues, or feedback:
- GitHub Issues: [Project Issues](./issues)
- Documentation: See `/docs` folder
- Email: [contact information]

---

**Built with ❤️ using state-of-the-art AI technology**
