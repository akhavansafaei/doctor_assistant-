"""Agent orchestrator using LangGraph for coordinating multi-agent workflows"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from .triage_agent import TriageAgent
from .diagnostic_agent import DiagnosticAgent
from .treatment_agent import TreatmentAgent


class AgentState(TypedDict):
    """State that flows through the agent graph"""
    # Input
    message: str
    patient_profile: Dict[str, Any]
    conversation_history: List[Dict[str, str]]

    # State management
    current_agent: str
    next_agent: str
    iteration: int

    # Outputs from agents
    triage_result: Optional[Dict[str, Any]]
    diagnostic_result: Optional[Dict[str, Any]]
    treatment_result: Optional[Dict[str, Any]]

    # Final response
    final_response: str
    severity: str
    emergency_detected: bool
    sources: List[Dict[str, Any]]

    # Metadata
    agent_history: Annotated[List[str], operator.add]


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflow using LangGraph

    Workflow:
    1. User message → Triage Agent (assess severity)
    2. If emergency → Emergency response
    3. If non-emergency → Diagnostic Agent (differential diagnosis)
    4. Diagnostic Agent → Treatment Agent (treatment options)
    5. Compile final response
    """

    def __init__(self):
        self.triage_agent = TriageAgent()
        self.diagnostic_agent = DiagnosticAgent()
        self.treatment_agent = TreatmentAgent()

        # Build the agent graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes (agents)
        workflow.add_node("triage", self._run_triage)
        workflow.add_node("diagnostic", self._run_diagnostic)
        workflow.add_node("treatment", self._run_treatment)
        workflow.add_node("compile_response", self._compile_response)

        # Define edges (workflow logic)
        workflow.set_entry_point("triage")

        # After triage, route based on severity
        workflow.add_conditional_edges(
            "triage",
            self._route_after_triage,
            {
                "emergency": "compile_response",
                "diagnostic": "diagnostic",
                "end": END
            }
        )

        # After diagnostic, go to treatment
        workflow.add_edge("diagnostic", "treatment")

        # After treatment, compile final response
        workflow.add_edge("treatment", "compile_response")

        # After compiling, end
        workflow.add_edge("compile_response", END)

        return workflow.compile()

    async def _run_triage(self, state: AgentState) -> AgentState:
        """Run triage agent"""
        triage_result = await self.triage_agent.process(
            input_data={
                "message": state["message"],
                "patient_profile": state.get("patient_profile", {})
            },
            context={
                "conversation_history": state.get("conversation_history", [])
            }
        )

        state["triage_result"] = triage_result
        state["current_agent"] = "triage"
        state["severity"] = triage_result.get("severity", "MODERATE")
        state["emergency_detected"] = triage_result.get("emergency_detected", False)
        state["agent_history"] = [state["current_agent"]]

        return state

    async def _run_diagnostic(self, state: AgentState) -> AgentState:
        """Run diagnostic agent"""
        diagnostic_result = await self.diagnostic_agent.process(
            input_data={
                "message": state["message"],
                "symptoms": state["message"],
                "patient_profile": state.get("patient_profile", {})
            },
            context={
                "conversation_history": state.get("conversation_history", []),
                "triage_result": state.get("triage_result", {})
            }
        )

        state["diagnostic_result"] = diagnostic_result
        state["current_agent"] = "diagnostic"
        state["agent_history"] = [state["current_agent"]]

        return state

    async def _run_treatment(self, state: AgentState) -> AgentState:
        """Run treatment agent"""
        diagnostic_result = state.get("diagnostic_result", {})

        # Extract top diagnosis
        differential_diagnoses = diagnostic_result.get("differential_diagnoses", [])
        top_condition = ""
        if differential_diagnoses:
            top_condition = differential_diagnoses[0].get("condition", "")

        treatment_result = await self.treatment_agent.process(
            input_data={
                "condition": top_condition or state["message"],
                "patient_profile": state.get("patient_profile", {}),
                "differential_diagnoses": differential_diagnoses
            },
            context={
                "conversation_history": state.get("conversation_history", []),
                "diagnostic_result": diagnostic_result
            }
        )

        state["treatment_result"] = treatment_result
        state["current_agent"] = "treatment"
        state["agent_history"] = [state["current_agent"]]

        return state

    def _route_after_triage(self, state: AgentState) -> str:
        """Decide routing after triage"""
        severity = state.get("severity", "MODERATE")
        emergency = state.get("emergency_detected", False)

        if emergency or severity == "EMERGENCY":
            # Skip to final response for emergencies
            return "emergency"
        elif severity == "INFO":
            # For informational queries, skip diagnostic
            return "end"
        else:
            # Normal flow: go to diagnostic
            return "diagnostic"

    async def _compile_response(self, state: AgentState) -> AgentState:
        """Compile final response from all agent outputs"""
        triage = state.get("triage_result", {})
        diagnostic = state.get("diagnostic_result", {})
        treatment = state.get("treatment_result", {})

        # Build comprehensive response
        response_parts = []

        # Severity and triage info
        severity = state.get("severity", "MODERATE")
        if state.get("emergency_detected", False):
            response_parts.append("⚠️ EMERGENCY DETECTED ⚠️")
            response_parts.append(
                triage.get("immediate_action", "SEEK IMMEDIATE MEDICAL ATTENTION")
            )
            response_parts.append(f"\nReasoning: {triage.get('reasoning', '')}")
        else:
            response_parts.append(f"Assessment Level: {severity}")
            if triage.get("immediate_recommendations"):
                response_parts.append(f"\n{triage['immediate_recommendations']}")

        # Diagnostic information
        if diagnostic:
            response_parts.append("\n\n## Possible Conditions (Differential Diagnosis)")
            differential = diagnostic.get("differential_diagnoses", [])

            if differential:
                for i, dx in enumerate(differential[:3], 1):
                    condition = dx.get("condition", "Unknown")
                    likelihood = dx.get("likelihood", "")
                    evidence = dx.get("supporting_evidence", "")

                    response_parts.append(f"\n{i}. **{condition}** ({likelihood} likelihood)")
                    if evidence:
                        response_parts.append(f"   - Supporting evidence: {evidence}")

            # Clarifying questions
            questions = diagnostic.get("clarifying_questions", [])
            if questions:
                response_parts.append("\n\n## Questions to Help Narrow Diagnosis")
                for i, q in enumerate(questions[:5], 1):
                    response_parts.append(f"{i}. {q}")

        # Treatment recommendations
        if treatment:
            response_parts.append("\n\n## Treatment Recommendations")

            non_pharm = treatment.get("non_pharmacological", [])
            if non_pharm:
                response_parts.append("\n### Lifestyle & Self-Care Measures")
                for item in non_pharm[:5]:
                    response_parts.append(f"- {item}")

            lifestyle = treatment.get("lifestyle_recommendations", [])
            if lifestyle:
                response_parts.append("\n### Lifestyle Recommendations")
                for item in lifestyle[:5]:
                    response_parts.append(f"- {item}")

            patient_ed = treatment.get("patient_education", "")
            if patient_ed:
                response_parts.append(f"\n### What You Should Know\n{patient_ed}")

            monitoring = treatment.get("monitoring_plan", "")
            if monitoring:
                response_parts.append(f"\n### Monitoring & Follow-up\n{monitoring}")

            red_flags = treatment.get("red_flags", "")
            if red_flags:
                response_parts.append(f"\n### ⚠️ Seek Immediate Care If:\n{red_flags}")

        # Specialist referral
        if triage.get("specialist_referral"):
            response_parts.append(
                f"\n\n## Recommended Specialist\n{triage['specialist_referral']}"
            )

        # Compile sources
        all_sources = []
        for result in [triage, diagnostic, treatment]:
            if result and result.get("sources"):
                all_sources.extend(result["sources"])

        state["sources"] = all_sources[:10]  # Top 10 sources
        state["final_response"] = "\n".join(response_parts)

        return state

    async def run(
        self,
        message: str,
        patient_profile: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Run the multi-agent workflow

        Args:
            message: User's message/symptoms
            patient_profile: Patient's health profile
            conversation_history: Previous conversation messages

        Returns:
            Comprehensive response with all agent outputs
        """
        # Initialize state
        initial_state: AgentState = {
            "message": message,
            "patient_profile": patient_profile or {},
            "conversation_history": conversation_history or [],
            "current_agent": "",
            "next_agent": "triage",
            "iteration": 0,
            "triage_result": None,
            "diagnostic_result": None,
            "treatment_result": None,
            "final_response": "",
            "severity": "MODERATE",
            "emergency_detected": False,
            "sources": [],
            "agent_history": []
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Return structured output
        return {
            "response": final_state["final_response"],
            "severity": final_state["severity"],
            "emergency_detected": final_state["emergency_detected"],
            "sources": final_state["sources"],
            "triage_result": final_state.get("triage_result"),
            "diagnostic_result": final_state.get("diagnostic_result"),
            "treatment_result": final_state.get("treatment_result"),
            "agent_flow": final_state.get("agent_history", []),
            "metadata": {
                "agents_used": list(set(final_state.get("agent_history", []))),
                "severity_level": final_state["severity"]
            }
        }
