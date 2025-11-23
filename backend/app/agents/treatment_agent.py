"""Legal advice agent"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class LegalAdviceAgent(BaseAgent):
    """
    Legal Advice Agent
    - Suggests legal options and strategies
    - Considers jurisdictional requirements
    - Provides procedural guidance
    - Offers client education on legal process
    """

    def __init__(self):
        system_prompt = """You are an expert legal guidance AI assistant.

Your role is to:
1. Suggest legal options and strategies based on applicable laws and precedents
2. Provide both legal remedies and alternative dispute resolution options
3. Consider client-specific factors (jurisdiction, business context, legal restrictions)
4. Identify potential conflicts or complications
5. Offer procedural guidance and next steps
6. Provide client education tailored to legal complexity

CRITICAL GUIDELINES:
- Base all guidance on applicable statutes, regulations, and legal precedents
- ALWAYS consider jurisdictional requirements and limitations
- Account for statutes of limitations and procedural deadlines
- Provide multiple legal options when available
- Explain risks, benefits, and costs of each option
- Include alternative dispute resolution methods (mediation, arbitration)
- Emphasize that guidance is for attorney consultation and review
- NEVER provide definitive legal advice - only suggest options for attorney review

Legal Guidance Framework:
1. Primary legal options (strongest legal position, best precedent)
2. Alternative approaches
3. Settlement and ADR options
4. Procedural requirements and deadlines
5. Next steps and timeline recommendations

Always structure output with:
- Legal options (ranked by strength/likelihood)
- Jurisdictional considerations
- Procedural requirements
- Timeline and deadlines
- Client education points
- Next steps and action items
"""

        super().__init__(
            name="Legal Advice Agent",
            description="Legal options and guidance",
            system_prompt=system_prompt,
            use_rag=True
        )

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate legal advice and recommendations

        Args:
            input_data: Contains legal issue, client profile, legal analysis
            context: Conversation history and previous agent outputs

        Returns:
            Legal guidance with options and recommendations
        """
        legal_issue = input_data.get("legal_issue", "")
        client_profile = input_data.get("client_profile", {})
        legal_issues_identified = input_data.get("legal_issues_identified", [])

        # Build query for legal guidance
        query = self._build_guidance_query(legal_issue, legal_issues_identified, client_profile)

        # Retrieve legal guidance and precedents
        retrieved_docs = await self.retrieve_context(
            query=query,
            filters={"document_type": ["statute", "case_law", "regulation"]}
        )

        legal_context = self.format_context(retrieved_docs)

        # Check for legal conflicts or complications
        conflict_warnings = self._check_legal_complications(client_profile)

        # Build legal guidance prompt
        guidance_prompt = f"""Develop legal guidance for the following scenario:

PRIMARY LEGAL ISSUE:
{legal_issue}

LEGAL ISSUES IDENTIFIED (if applicable):
{self._format_legal_issues(legal_issues_identified)}

CLIENT INFORMATION:
{self._format_client_info(client_profile)}

ACTIVE LEGAL MATTERS:
{self._format_active_matters(client_profile)}

LEGAL RESTRICTIONS:
{self._format_restrictions(client_profile)}

{legal_context}

{conflict_warnings}

Provide legal guidance in the following format:

PRIMARY_LEGAL_OPTIONS:
1. [Legal option or strategy]
   - Strength of Legal Position: [Strong/Moderate/Weak]
   - Legal Basis: [Applicable statutes, regulations, or case law]
   - Procedural Steps: [What needs to be done]
   - Potential Outcome: [What client can expect]
   - Risks and Considerations: [Important factors to consider]
   - Estimated Timeline: [How long this might take]
   - Cost Considerations: [Relative cost if applicable]

ALTERNATIVE_DISPUTE_RESOLUTION:
- [Mediation, arbitration, or settlement options]
- [Benefits and drawbacks of each]

JURISDICTIONAL_REQUIREMENTS:
[Specific requirements for the relevant jurisdiction]

PROCEDURAL_DEADLINES:
[Critical deadlines, statutes of limitations, filing requirements]

ALTERNATIVE_STRATEGIES:
[Other legal approaches if primary option fails or is unavailable]

RECOMMENDED_NEXT_STEPS:
- [Immediate actions to take]
- [Documents to gather]
- [People to contact]

CLIENT_EDUCATION:
[Key points client should understand about their legal situation and options]

TIMELINE_CONSIDERATIONS:
[Expected timeline, key milestones, deadline tracking]

IMPORTANT_WARNINGS:
[Critical factors, potential pitfalls, things to avoid]
"""

        # Get conversation history
        conversation_history = context.get("conversation_history", []) if context else []

        # Create messages
        messages = self.create_messages(
            user_message=guidance_prompt,
            conversation_history=conversation_history[-4:]
        )

        # Invoke LLM
        response = await self.invoke_llm(messages, temperature=0.1)

        # Parse response
        parsed = self._parse_guidance_output(response)

        # Add sources
        parsed["sources"] = [
            {
                "title": doc.get("metadata", {}).get("title", "Legal Source"),
                "text": doc["text"][:300],
                "source": doc.get("metadata", {}).get("source", "Unknown"),
                "relevance_score": doc.get("rerank_score", doc.get("rrf_score", 0))
            }
            for doc in retrieved_docs[:5]
        ]

        parsed["agent"] = self.name
        parsed["raw_response"] = response

        return parsed

    def _build_guidance_query(
        self,
        legal_issue: str,
        legal_issues_identified: List[Dict[str, Any]],
        client_profile: Dict[str, Any]
    ) -> str:
        """Build query for legal guidance retrieval"""
        query_parts = [f"legal options for {legal_issue}"]

        if legal_issues_identified:
            top_issue = legal_issues_identified[0].get("issue", "")
            if top_issue:
                query_parts.append(f"strategies for {top_issue}")

        # Add client-specific factors
        if client_profile.get("legal_areas_of_interest"):
            query_parts.append(f"in context of {client_profile['legal_areas_of_interest'][0]}")

        return " ".join(query_parts)

    def _format_legal_issues(self, issues: List[Dict[str, Any]]) -> str:
        """Format legal issues identified"""
        if not issues:
            return "None provided"

        formatted = []
        for i, issue in enumerate(issues[:3], 1):
            issue_name = issue.get("issue", "Unknown")
            relevance = issue.get("relevance", "")
            formatted.append(f"{i}. {issue_name} ({relevance})")

        return "\n".join(formatted)

    def _format_client_info(self, client_profile: Dict[str, Any]) -> str:
        """Format client information"""
        info_parts = []

        if client_profile.get("occupation"):
            info_parts.append(f"- Occupation: {client_profile['occupation']}")

        if client_profile.get("business_entities"):
            info_parts.append(
                f"- Business Entities: {len(client_profile['business_entities'])} entities"
            )

        if client_profile.get("citizenship"):
            info_parts.append(f"- Citizenship: {client_profile['citizenship']}")

        return "\n".join(info_parts) if info_parts else "Limited client information"

    def _format_active_matters(self, client_profile: Dict[str, Any]) -> str:
        """Format active legal matters"""
        matters = client_profile.get("active_legal_matters", [])
        if not matters:
            return "None reported"

        formatted = []
        for matter in matters[:5]:
            description = matter.get("description", "Unknown")
            status = matter.get("status", "")
            formatted.append(f"- {description} ({status})".strip())

        return "\n".join(formatted)

    def _format_restrictions(self, client_profile: Dict[str, Any]) -> str:
        """Format legal restrictions"""
        restrictions = client_profile.get("legal_restrictions", [])
        if not restrictions:
            return "None reported"

        formatted = []
        for restriction in restrictions:
            if isinstance(restriction, dict):
                restriction_type = restriction.get("type", "Unknown")
                details = restriction.get("details", "")
                formatted.append(f"- {restriction_type}: {details}".strip())
            else:
                formatted.append(f"- {restriction}")

        return "\n".join(formatted) if formatted else "None reported"

    def _check_legal_complications(self, client_profile: Dict[str, Any]) -> str:
        """Check for potential legal complications"""
        restrictions = client_profile.get("legal_restrictions", [])
        active_matters = client_profile.get("active_legal_matters", [])

        warnings = []

        if restrictions:
            warnings.append(
                f"⚠️ LEGAL RESTRICTIONS: Client has {len(restrictions)} legal restriction(s). "
                "Ensure any legal strategy complies with existing court orders or restrictions."
            )

        if active_matters and len(active_matters) > 2:
            warnings.append(
                f"⚠️ MULTIPLE ACTIVE MATTERS: Client has {len(active_matters)} ongoing legal matters. "
                "Consider potential conflicts or interactions between cases."
            )

        return "\n".join(warnings) if warnings else ""

    def _parse_guidance_output(self, response: str) -> Dict[str, Any]:
        """Parse legal guidance from response"""
        import re

        result = {
            "legal_options": [],
            "adr_options": [],
            "jurisdictional_requirements": "",
            "procedural_deadlines": "",
            "alternative_strategies": [],
            "recommended_next_steps": [],
            "important_considerations": "",
            "timeline_considerations": "",
            "warnings": ""
        }

        # Extract sections
        result["important_considerations"] = self._extract_section(response, "CLIENT_EDUCATION")
        result["timeline_considerations"] = self._extract_section(response, "TIMELINE_CONSIDERATIONS")
        result["warnings"] = self._extract_section(response, "IMPORTANT_WARNINGS")
        result["jurisdictional_requirements"] = self._extract_section(response, "JURISDICTIONAL_REQUIREMENTS")
        result["procedural_deadlines"] = self._extract_section(response, "PROCEDURAL_DEADLINES")

        # Extract lists
        adr = self._extract_section(response, "ALTERNATIVE_DISPUTE_RESOLUTION")
        if adr:
            result["adr_options"] = [
                line.strip('- ').strip()
                for line in adr.split('\n')
                if line.strip().startswith('-')
            ]

        next_steps = self._extract_section(response, "RECOMMENDED_NEXT_STEPS")
        if next_steps:
            result["recommended_next_steps"] = [
                line.strip('- ').strip()
                for line in next_steps.split('\n')
                if line.strip().startswith('-')
            ]

        alternative = self._extract_section(response, "ALTERNATIVE_STRATEGIES")
        if alternative:
            result["alternative_strategies"] = [
                line.strip('- ').strip()
                for line in alternative.split('\n')
                if line.strip().startswith('-')
            ]

        # Extract primary options
        primary = self._extract_section(response, "PRIMARY_LEGAL_OPTIONS")
        if primary:
            result["legal_options"] = self._parse_legal_options(primary)

        return result

    def _parse_legal_options(self, options_text: str) -> List[str]:
        """Parse legal options from text"""
        import re
        options = []

        # Split by numbered items
        items = re.split(r'\n\d+\.', options_text)
        for item in items:
            if item.strip():
                # Extract just the main option description (first line)
                lines = item.strip().split('\n')
                if lines:
                    option_desc = lines[0].strip()
                    if option_desc:
                        options.append(option_desc)

        return options

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract section from response"""
        import re
        pattern = f"{section_name}:\\s*(.+?)(?=\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
