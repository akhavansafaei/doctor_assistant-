# Contributing to AI Doctor Chatbot

First off, thank you for considering contributing to the AI Doctor Chatbot! It's people like you that help make healthcare technology more accessible and reliable.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python Version: [e.g. 3.11.5]
 - Docker Version: [e.g. 24.0.6]

**Additional context**
Any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Follow the coding style** used throughout the project
3. **Write tests** for your changes
4. **Update documentation** as needed
5. **Ensure the test suite passes**
6. **Make sure your code lints**
7. **Issue the pull request**

## Development Setup

```bash
# 1. Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/doctor_assistant.git
cd doctor_assistant

# 2. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/doctor_assistant.git

# 3. Create a branch
git checkout -b feature/your-feature-name

# 4. Setup development environment
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 5. Setup pre-commit hooks
pre-commit install
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 100 characters (not 79)
- Use type hints for all function signatures
- Use docstrings for all public functions and classes

**Example:**
```python
from typing import List, Dict, Any

async def process_medical_query(
    query: str,
    patient_profile: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Process a medical query using RAG and multi-agent system.

    Args:
        query: The patient's medical question or symptom description
        patient_profile: Patient's health profile and medical history

    Returns:
        List of potential diagnoses with supporting evidence

    Raises:
        ValueError: If query is empty or invalid
    """
    # Implementation here
    pass
```

### Code Formatting

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run before committing:
```bash
black .
isort .
flake8 .
mypy app/
```

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use pytest for testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_agents.py::test_triage_agent -v
```

## Project Structure

```
doctor_assistant-/
├── backend/
│   ├── app/
│   │   ├── agents/          # Multi-agent system
│   │   ├── api/             # API routes
│   │   ├── core/            # Core configuration
│   │   ├── models/          # Database models
│   │   ├── rag/             # RAG system
│   │   ├── safety/          # Safety guardrails
│   │   ├── schemas/         # Pydantic schemas
│   │   └── utils/           # Utility functions
│   ├── tests/               # Test files
│   └── requirements.txt
├── frontend/                # Frontend application
├── docs/                    # Documentation
└── docker-compose.yml
```

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(agents): add drug interaction checker agent

fix(rag): resolve retrieval timeout issue

docs(readme): update installation instructions

test(safety): add tests for emergency detector
```

## Adding New Agents

When adding a new specialized agent:

1. **Create agent file** in `backend/app/agents/`
2. **Inherit from BaseAgent**
3. **Implement `process()` method**
4. **Add comprehensive docstrings**
5. **Write tests** in `tests/test_agents.py`
6. **Update orchestrator** if needed
7. **Document the agent** in ARCHITECTURE.md

**Example:**
```python
from typing import Dict, Any, Optional
from .base_agent import BaseAgent

class NewMedicalAgent(BaseAgent):
    """
    Description of what this agent does
    """

    def __init__(self):
        system_prompt = """Your specialized agent prompt..."""
        super().__init__(
            name="New Medical Agent",
            description="Brief description",
            system_prompt=system_prompt,
            use_rag=True
        )

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process input and return agent output

        Args:
            input_data: Input data for processing
            context: Additional context

        Returns:
            Agent output with results
        """
        # Implementation
        pass
```

## Adding API Endpoints

1. **Create/update router** in `backend/app/api/`
2. **Use Pydantic schemas** for validation
3. **Add proper error handling**
4. **Document with docstrings**
5. **Add tests** for the endpoint

```python
from fastapi import APIRouter, HTTPException
from app.schemas.your_schema import YourSchema

router = APIRouter()

@router.post("/endpoint", response_model=ResponseSchema)
async def your_endpoint(data: YourSchema):
    """
    Endpoint description

    Args:
        data: Input data

    Returns:
        Response with results

    Raises:
        HTTPException: If operation fails
    """
    try:
        # Implementation
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Medical Safety Guidelines

**CRITICAL:** When working on medical features:

1. **Never remove safety guardrails**
2. **Always validate medical outputs**
3. **Include appropriate disclaimers**
4. **Test emergency detection thoroughly**
5. **Get review from medical professionals when possible**
6. **Document medical reasoning clearly**

## Documentation

- Update README.md if you change functionality
- Update ARCHITECTURE.md for architectural changes
- Add inline comments for complex logic
- Update API documentation
- Create examples for new features

## Review Process

1. **Self-review** your code before submitting
2. **Ensure CI passes** (tests, linting, etc.)
3. **Request reviews** from maintainers
4. **Address feedback** promptly
5. **Update based on review** comments

## Getting Help

- **Questions?** Open a discussion on GitHub
- **Stuck?** Ask in the developer channel
- **Need clarification?** Comment on the issue

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making healthcare technology better! 🙏**
