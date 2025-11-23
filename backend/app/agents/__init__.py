"""Multi-agent system for legal assistance"""
from .orchestrator import AgentOrchestrator
from .triage_agent import IntakeAgent
from .diagnostic_agent import LegalAnalysisAgent
from .treatment_agent import LegalAdviceAgent

__all__ = [
    "AgentOrchestrator",
    "IntakeAgent",
    "LegalAnalysisAgent",
    "LegalAdviceAgent"
]
