"""Agent orchestrator using LangGraph for coordinating multi-agent workflows"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from .triage_agent import IntakeAgent
from .diagnostic_agent import LegalAnalysisAgent
from .treatment_agent import LegalAdviceAgent


class AgentState(TypedDict):
    """State that flows through the agent graph"""
    # Input
    message: str
    client_profile: Dict[str, Any]
    conversation_history: List[Dict[str, str]]

    # Memory context
    long_term_memory: Optional[str]  # Formatted memory from past conversations
    memory_summary: Optional[Dict[str, Any]]  # Memory statistics

    # Language context
    language: Optional[str]  # Detected language code ("en" or "fa")

    # State management
    current_agent: str
    next_agent: str
    iteration: int

    # Outputs from agents
    intake_result: Optional[Dict[str, Any]]
    legal_analysis_result: Optional[Dict[str, Any]]
    legal_advice_result: Optional[Dict[str, Any]]

    # Final response
    final_response: str
    urgency: str
    urgent_matter_detected: bool
    sources: List[Dict[str, Any]]

    # Metadata
    agent_history: Annotated[List[str], operator.add]


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflow using LangGraph

    Workflow:
    1. User inquiry → Intake Agent (assess urgency)
    2. If critical urgent → Urgent response
    3. If non-urgent → Legal Analysis Agent (identify legal issues)
    4. Legal Analysis Agent → Legal Advice Agent (provide guidance)
    5. Compile final response
    """

    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.legal_analysis_agent = LegalAnalysisAgent()
        self.legal_advice_agent = LegalAdviceAgent()

        # Build the agent graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes (agents)
        workflow.add_node("intake", self._run_intake)
        workflow.add_node("legal_analysis", self._run_legal_analysis)
        workflow.add_node("legal_advice", self._run_legal_advice)
        workflow.add_node("compile_response", self._compile_response)

        # Define edges (workflow logic)
        workflow.set_entry_point("intake")

        # After intake, route based on urgency
        workflow.add_conditional_edges(
            "intake",
            self._route_after_intake,
            {
                "critical_urgent": "compile_response",
                "legal_analysis": "legal_analysis",
                "end": END
            }
        )

        # After legal analysis, go to legal advice
        workflow.add_edge("legal_analysis", "legal_advice")

        # After legal advice, compile final response
        workflow.add_edge("legal_advice", "compile_response")

        # After compiling, end
        workflow.add_edge("compile_response", END)

        return workflow.compile()

    async def _run_intake(self, state: AgentState) -> AgentState:
        """Run intake agent"""
        intake_result = await self.intake_agent.process(
            input_data={
                "message": state["message"],
                "client_profile": state.get("client_profile", {})
            },
            context={
                "conversation_history": state.get("conversation_history", []),
                "long_term_memory": state.get("long_term_memory", "")
            }
        )

        state["intake_result"] = intake_result
        state["current_agent"] = "intake"
        state["urgency"] = intake_result.get("urgency", "MODERATE")
        state["urgent_matter_detected"] = intake_result.get("urgent_matter_detected", False)
        state["agent_history"] = [state["current_agent"]]

        return state

    async def _run_legal_analysis(self, state: AgentState) -> AgentState:
        """Run legal analysis agent"""
        legal_analysis_result = await self.legal_analysis_agent.process(
            input_data={
                "message": state["message"],
                "situation": state["message"],
                "client_profile": state.get("client_profile", {})
            },
            context={
                "conversation_history": state.get("conversation_history", []),
                "intake_result": state.get("intake_result", {}),
                "long_term_memory": state.get("long_term_memory", "")
            }
        )

        state["legal_analysis_result"] = legal_analysis_result
        state["current_agent"] = "legal_analysis"
        state["agent_history"] = [state["current_agent"]]

        return state

    async def _run_legal_advice(self, state: AgentState) -> AgentState:
        """Run legal advice agent"""
        legal_analysis_result = state.get("legal_analysis_result", {})

        # Extract top legal issue
        legal_issues = legal_analysis_result.get("legal_issues_identified", [])
        top_issue = ""
        if legal_issues:
            top_issue = legal_issues[0].get("issue", "")

        legal_advice_result = await self.legal_advice_agent.process(
            input_data={
                "legal_issue": top_issue or state["message"],
                "client_profile": state.get("client_profile", {}),
                "legal_issues_identified": legal_issues
            },
            context={
                "conversation_history": state.get("conversation_history", []),
                "legal_analysis_result": legal_analysis_result,
                "long_term_memory": state.get("long_term_memory", "")
            }
        )

        state["legal_advice_result"] = legal_advice_result
        state["current_agent"] = "legal_advice"
        state["agent_history"] = [state["current_agent"]]

        return state

    def _route_after_intake(self, state: AgentState) -> str:
        """Decide routing after intake"""
        urgency = state.get("urgency", "MODERATE")
        urgent_matter = state.get("urgent_matter_detected", False)

        if urgent_matter or urgency == "CRITICAL_URGENT":
            # Skip to final response for critical urgent matters
            return "critical_urgent"
        elif urgency == "INFO":
            # For informational queries, skip legal analysis
            return "end"
        else:
            # Normal flow: go to legal analysis
            return "legal_analysis"

    async def _compile_response(self, state: AgentState) -> AgentState:
        """Compile final response from all agent outputs"""
        intake = state.get("intake_result", {})
        legal_analysis = state.get("legal_analysis_result", {})
        legal_advice = state.get("legal_advice_result", {})

        # Build comprehensive response
        response_parts = []

        # Urgency and intake info
        urgency = state.get("urgency", "MODERATE")
        if state.get("urgent_matter_detected", False):
            response_parts.append("⚠️ TIME-SENSITIVE LEGAL MATTER DETECTED ⚠️")
            response_parts.append(
                intake.get("immediate_action", "CONSULT WITH AN ATTORNEY IMMEDIATELY")
            )
            response_parts.append(f"\nReasoning: {intake.get('reasoning', '')}")
        else:
            response_parts.append(f"Urgency Level: {urgency}")
            if intake.get("immediate_recommendations"):
                response_parts.append(f"\n{intake['immediate_recommendations']}")

        # Legal analysis information
        if legal_analysis:
            response_parts.append("\n\n## Legal Issues Identified")
            legal_issues = legal_analysis.get("legal_issues_identified", [])

            if legal_issues:
                for i, issue in enumerate(legal_issues[:3], 1):
                    issue_name = issue.get("issue", "Unknown")
                    relevance = issue.get("relevance", "")
                    authority = issue.get("supporting_authority", "")

                    response_parts.append(f"\n{i}. **{issue_name}** ({relevance} relevance)")
                    if authority:
                        response_parts.append(f"   - Legal authority: {authority}")

            # Clarifying questions
            questions = legal_analysis.get("clarifying_questions", [])
            if questions:
                response_parts.append("\n\n## Information Needed")
                for i, q in enumerate(questions[:5], 1):
                    response_parts.append(f"{i}. {q}")

        # Legal advice recommendations
        if legal_advice:
            response_parts.append("\n\n## Legal Guidance")

            options = legal_advice.get("legal_options", [])
            if options:
                response_parts.append("\n### Available Legal Options")
                for item in options[:5]:
                    response_parts.append(f"- {item}")

            next_steps = legal_advice.get("recommended_next_steps", [])
            if next_steps:
                response_parts.append("\n### Recommended Next Steps")
                for item in next_steps[:5]:
                    response_parts.append(f"- {item}")

            considerations = legal_advice.get("important_considerations", "")
            if considerations:
                response_parts.append(f"\n### Important Considerations\n{considerations}")

            timeline = legal_advice.get("timeline_considerations", "")
            if timeline:
                response_parts.append(f"\n### Timeline & Deadlines\n{timeline}")

            warnings = legal_advice.get("warnings", "")
            if warnings:
                response_parts.append(f"\n### ⚠️ Important Warnings:\n{warnings}")

        # Legal area referral
        if intake.get("legal_area_referral"):
            response_parts.append(
                f"\n\n## Recommended Legal Practice Area\n{intake['legal_area_referral']}"
            )

        # Compile sources
        all_sources = []
        for result in [intake, legal_analysis, legal_advice]:
            if result and result.get("sources"):
                all_sources.extend(result["sources"])

        state["sources"] = all_sources[:10]  # Top 10 sources
        state["final_response"] = "\n".join(response_parts)

        return state

    async def run(
        self,
        message: str,
        client_profile: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Run the multi-agent workflow

        Args:
            message: User's inquiry/legal matter
            client_profile: Client's legal profile
            conversation_history: Previous conversation messages

        Returns:
            Comprehensive response with all agent outputs
        """
        # Initialize state
        initial_state: AgentState = {
            "message": message,
            "client_profile": client_profile or {},
            "conversation_history": conversation_history or [],
            "current_agent": "",
            "next_agent": "intake",
            "iteration": 0,
            "intake_result": None,
            "legal_analysis_result": None,
            "legal_advice_result": None,
            "final_response": "",
            "urgency": "MODERATE",
            "urgent_matter_detected": False,
            "sources": [],
            "agent_history": [],
            "long_term_memory": None,
            "memory_summary": None,
            "language": None
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Return structured output
        return {
            "response": final_state["final_response"],
            "urgency": final_state["urgency"],
            "urgent_matter_detected": final_state["urgent_matter_detected"],
            "sources": final_state["sources"],
            "intake_result": final_state.get("intake_result"),
            "legal_analysis_result": final_state.get("legal_analysis_result"),
            "legal_advice_result": final_state.get("legal_advice_result"),
            "agent_flow": final_state.get("agent_history", []),
            "metadata": {
                "agents_used": list(set(final_state.get("agent_history", []))),
                "urgency_level": final_state["urgency"]
            }
        }
