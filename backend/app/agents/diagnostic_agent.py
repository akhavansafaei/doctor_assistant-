"""Legal analysis agent for identifying and analyzing legal issues"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import json


class LegalAnalysisAgent(BaseAgent):
    """
    Legal Analysis Agent
    - Identifies potential legal issues
    - Analyzes applicable laws and regulations
    - Provides legal reasoning and precedents
    - Maps to relevant statutes and case law
    """

    def __init__(self):
        system_prompt = """You are an expert legal analysis AI assistant trained in legal reasoning and issue spotting.

Your role is to:
1. Analyze client's situation and identify potential legal issues
2. Identify multiple legal issues or claims that may apply
3. Rank issues by relevance and potential impact
4. Identify key legal elements and requirements
5. Suggest additional information needed for complete analysis
6. Reference applicable statutes, regulations, or case law when relevant

CRITICAL GUIDELINES:
- Always identify multiple potential legal issues, not just one
- Rank by relevance based on facts provided, jurisdiction, and legal precedents
- Consider both obvious and less apparent legal issues
- Account for client's jurisdiction, business context, and specific circumstances
- Use established legal principles and precedents
- Be transparent about areas of uncertainty
- Flag when situation involves multiple areas of law or unusual circumstances
- NEVER provide definitive legal advice - always recommend professional attorney consultation

Legal Analysis Framework:
1. Issue Spotting: Identify all potential legal issues in the facts
2. Rule Statement: State the applicable legal rules and standards
3. Analysis: Apply the law to the facts systematically
4. Conclusion: Assess likely outcomes and legal positions
5. Risk Assessment: Identify potential legal risks and liabilities

Always structure your output clearly with:
- Legal issues identified (ranked)
- Supporting legal authority for each
- Distinguishing factors
- Recommended next steps
- Clarifying questions for the client
"""

        super().__init__(
            name="Legal Analysis Agent",
            description="Legal issue identification and analysis",
            system_prompt=system_prompt,
            use_rag=True
        )

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate legal analysis

        Args:
            input_data: Contains situation description, client profile, and any documents
            context: Conversation history and intake assessment

        Returns:
            Legal analysis with identified issues and recommendations
        """
        situation = input_data.get("situation", input_data.get("message", ""))
        client_profile = input_data.get("client_profile", {})
        documents = input_data.get("documents", {})

        # Build comprehensive legal query
        legal_query = self._build_legal_query(
            situation, client_profile, documents
        )

        # Retrieve relevant legal sources and precedents
        retrieved_docs = await self.retrieve_context(
            query=legal_query,
            filters={"document_type": ["statute", "case_law"]}
        )

        legal_context = self.format_context(retrieved_docs)

        # Build analysis prompt
        analysis_prompt = f"""Perform legal analysis for the following situation:

SITUATION DESCRIPTION:
{situation}

CLIENT INFORMATION:
{self._format_client_info(client_profile)}

{legal_context}

Provide legal analysis in the following structured format:

LEGAL_ISSUES_IDENTIFIED:
1. [Legal Issue Name] (Area of Law: [e.g., Contract Law, Employment Law, etc.])
   - Relevance: [High/Moderate/Low]
   - Supporting Legal Authority: [Applicable statutes, regulations, or case law]
   - Key Elements: [Legal elements that must be proven/established]
   - Analysis: [How the facts relate to this legal issue]

2. [Next issue...]
   ...

DISTINGUISHING_FACTORS:
[What facts or circumstances are critical in determining the legal analysis]

RECOMMENDED_INFORMATION:
[What additional information, documents, or evidence would strengthen the analysis]

CLARIFYING_QUESTIONS:
1. [Important question to ask client]
2. [Another question]
   ...

RISK_ASSESSMENT:
[Potential legal risks, liabilities, or adverse outcomes to be aware of]

LEGAL_REASONING:
[Your step-by-step legal analysis and reasoning process]
"""

        # Get conversation history
        conversation_history = context.get("conversation_history", []) if context else []

        # Create messages
        messages = self.create_messages(
            user_message=analysis_prompt,
            conversation_history=conversation_history[-6:]  # Last 3 exchanges
        )

        # Invoke LLM with slightly higher temperature for thorough analysis
        response = await self.invoke_llm(messages, temperature=0.2)

        # Parse structured output
        parsed = self._parse_analysis_output(response)

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

    def _build_legal_query(
        self,
        situation: str,
        client_profile: Dict[str, Any],
        documents: Dict[str, Any]
    ) -> str:
        """Build comprehensive query for legal knowledge retrieval"""
        query_parts = [situation]

        # Add relevant client factors
        if client_profile.get("jurisdiction"):
            query_parts.append(f"jurisdiction {client_profile['jurisdiction']}")

        if client_profile.get("legal_areas_of_interest"):
            query_parts.append(
                f"areas: {', '.join(client_profile['legal_areas_of_interest'])}"
            )

        # Add document context if available
        if documents:
            query_parts.append(f"with documents: {str(documents)}")

        return " ".join(query_parts)

    def _format_client_info(self, client_profile: Dict[str, Any]) -> str:
        """Format client information for prompt"""
        info_parts = []

        if client_profile.get("occupation"):
            info_parts.append(f"- Occupation: {client_profile['occupation']}")

        if client_profile.get("citizenship"):
            info_parts.append(f"- Citizenship: {client_profile['citizenship']}")

        if client_profile.get("active_legal_matters"):
            info_parts.append(
                f"- Active Legal Matters: {len(client_profile['active_legal_matters'])} ongoing"
            )

        if client_profile.get("previous_legal_issues"):
            issues = [issue.get('type', 'Unknown') for issue in client_profile.get('previous_legal_issues', [])]
            if issues:
                info_parts.append(f"- Previous Legal Issues: {', '.join(issues)}")

        if client_profile.get("legal_restrictions"):
            if client_profile['legal_restrictions']:
                info_parts.append(f"- Legal Restrictions: Present (see profile for details)")

        if client_profile.get("business_entities"):
            if client_profile['business_entities']:
                info_parts.append(f"- Business Entities: {len(client_profile['business_entities'])}")

        return "\n".join(info_parts) if info_parts else "No additional client information available"

    def _parse_analysis_output(self, response: str) -> Dict[str, Any]:
        """Parse the legal analysis output into structured format"""
        import re

        result = {
            "legal_issues_identified": [],
            "distinguishing_factors": "",
            "recommended_information": "",
            "clarifying_questions": [],
            "risk_assessment": "",
            "legal_reasoning": ""
        }

        # Extract legal issues
        issues_section = self._extract_section(response, "LEGAL_ISSUES_IDENTIFIED")
        if issues_section:
            result["legal_issues_identified"] = self._parse_legal_issues(issues_section)

        # Extract other sections
        result["distinguishing_factors"] = self._extract_section(
            response, "DISTINGUISHING_FACTORS"
        )
        result["recommended_information"] = self._extract_section(
            response, "RECOMMENDED_INFORMATION"
        )
        result["risk_assessment"] = self._extract_section(response, "RISK_ASSESSMENT")
        result["legal_reasoning"] = self._extract_section(
            response, "LEGAL_REASONING"
        )

        # Extract clarifying questions
        questions_section = self._extract_section(response, "CLARIFYING_QUESTIONS")
        if questions_section:
            questions = re.findall(r'^\d+\.\s*(.+)$', questions_section, re.MULTILINE)
            result["clarifying_questions"] = questions

        return result

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from the response"""
        pattern = f"{section_name}:\\s*(.+?)(?=\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_legal_issues(self, issues_text: str) -> List[Dict[str, Any]]:
        """Parse legal issues from text"""
        issues = []
        current_issue = None

        lines = issues_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a new issue (starts with number)
            if re.match(r'^\d+\.', line):
                if current_issue:
                    issues.append(current_issue)

                # Extract issue name and area of law
                issue_match = re.match(
                    r'^\d+\.\s*(.+?)(?:\s*\(Area of Law:\s*([^)]+)\))?',
                    line
                )
                if issue_match:
                    current_issue = {
                        "issue": issue_match.group(1).strip(),
                        "area_of_law": issue_match.group(2),
                        "relevance": "",
                        "supporting_authority": "",
                        "key_elements": "",
                        "analysis": ""
                    }
            elif current_issue:
                # Parse sub-fields
                if "Relevance:" in line:
                    current_issue["relevance"] = line.split(":", 1)[1].strip()
                elif "Supporting Legal Authority:" in line:
                    current_issue["supporting_authority"] = line.split(":", 1)[1].strip()
                elif "Key Elements:" in line:
                    current_issue["key_elements"] = line.split(":", 1)[1].strip()
                elif "Analysis:" in line:
                    current_issue["analysis"] = line.split(":", 1)[1].strip()

        # Add last issue
        if current_issue:
            issues.append(current_issue)

        return issues
