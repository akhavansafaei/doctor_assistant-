"""Utility to inject client profile context into LLM prompts"""
from typing import Dict, Any, Optional


def format_profile_for_prompt(client_profile: Optional[Dict[str, Any]]) -> str:
    """
    Format client profile into a context string for LLM prompts

    Args:
        client_profile: Client's legal profile data

    Returns:
        Formatted context string
    """
    if not client_profile:
        return ""

    context_parts = ["CLIENT LEGAL PROFILE:"]

    # Basic information
    basic_info = []
    if client_profile.get("occupation"):
        basic_info.append(f"Occupation: {client_profile['occupation']}")

    if client_profile.get("employer"):
        basic_info.append(f"Employer: {client_profile['employer']}")

    if client_profile.get("citizenship"):
        basic_info.append(f"Citizenship: {client_profile['citizenship']}")

    if client_profile.get("marital_status"):
        basic_info.append(f"Marital Status: {client_profile['marital_status']}")

    if basic_info:
        context_parts.append("Basic Info: " + ", ".join(basic_info))

    # Legal areas of interest
    legal_areas = client_profile.get("legal_areas_of_interest", [])
    if legal_areas:
        context_parts.append(f"Legal Areas of Interest: {', '.join(legal_areas)}")
    else:
        context_parts.append("Legal Areas of Interest: Not specified")

    # Active legal matters
    active_matters = client_profile.get("active_legal_matters", [])
    if active_matters:
        matter_list = []
        for matter in active_matters:
            if isinstance(matter, dict):
                description = matter.get("description", "Unknown matter")
                status = matter.get("status", "")
                matter_str = f"{description}"
                if status:
                    matter_str += f" ({status})"
                matter_list.append(matter_str)
            else:
                matter_list.append(str(matter))

        context_parts.append(f"Active Legal Matters: {', '.join(matter_list)}")
    else:
        context_parts.append("Active Legal Matters: None reported")

    # Previous legal issues
    previous_issues = client_profile.get("previous_legal_issues", [])
    if previous_issues:
        issue_list = []
        for issue in previous_issues:
            if isinstance(issue, dict):
                issue_type = issue.get("type", "Unknown")
                year = issue.get("year", "")
                issue_str = f"{issue_type}"
                if year:
                    issue_str += f" ({year})"
                issue_list.append(issue_str)
            else:
                issue_list.append(str(issue))

        context_parts.append(f"Previous Legal Issues: {', '.join(issue_list)}")

    # Legal restrictions
    restrictions = client_profile.get("legal_restrictions", [])
    if restrictions:
        restriction_list = []
        for restriction in restrictions:
            if isinstance(restriction, dict):
                restriction_type = restriction.get("type", "Unknown")
                details = restriction.get("details", "")
                restriction_str = f"{restriction_type}"
                if details:
                    restriction_str += f" - {details}"
                restriction_list.append(restriction_str)
            else:
                restriction_list.append(str(restriction))

        context_parts.append(f"Legal Restrictions: {', '.join(restriction_list)}")
    else:
        context_parts.append("Legal Restrictions: None reported")

    # Business entities
    business_entities = client_profile.get("business_entities", [])
    if business_entities:
        entity_list = []
        for entity in business_entities:
            if isinstance(entity, dict):
                name = entity.get("name", "Unknown entity")
                entity_type = entity.get("type", "")
                entity_str = f"{name}"
                if entity_type:
                    entity_str += f" ({entity_type})"
                entity_list.append(entity_str)
            else:
                entity_list.append(str(entity))

        context_parts.append(f"Business Entities: {', '.join(entity_list)}")

    # Financial concerns
    financial_concerns = client_profile.get("financial_concerns", [])
    if financial_concerns:
        context_parts.append(f"Financial Concerns: {', '.join(financial_concerns)}")

    # Communication preferences
    pref_comm = client_profile.get("preferred_communication")
    if pref_comm:
        context_parts.append(f"Preferred Communication: {pref_comm}")

    # Add important note
    context_parts.append("")
    context_parts.append("IMPORTANT: Consider this client profile when providing legal guidance. Account for their active legal matters, legal restrictions, and jurisdictional context in your recommendations.")

    return "\n".join(context_parts)


def get_critical_warnings(client_profile: Optional[Dict[str, Any]]) -> list[str]:
    """
    Extract critical warnings from profile that should be highlighted

    Args:
        client_profile: Client's legal profile

    Returns:
        List of warning messages
    """
    warnings = []

    if not client_profile:
        return warnings

    # Legal restrictions are critical
    restrictions = client_profile.get("legal_restrictions", [])
    if restrictions:
        restriction_types = []
        for restriction in restrictions:
            if isinstance(restriction, dict):
                restriction_types.append(restriction.get("type", "Unknown"))
            else:
                restriction_types.append(str(restriction))

        warnings.append(
            f"⚠️ LEGAL RESTRICTIONS: Client has {', '.join(restriction_types)}. "
            "Ensure any legal strategy complies with these restrictions."
        )

    # High-risk legal situations
    high_risk_areas = ["criminal", "bankruptcy", "deportation", "custody"]
    active_matters = client_profile.get("active_legal_matters", [])
    critical_matters = []

    for matter in active_matters:
        if isinstance(matter, dict):
            description = matter.get("description", "").lower()
            matter_type = matter.get("type", "").lower()

            if any(risk in description or risk in matter_type for risk in high_risk_areas):
                critical_matters.append(matter.get("description", "Critical matter"))

    if critical_matters:
        warnings.append(
            f"⚠️ HIGH-STAKES MATTERS: Client has critical legal matters ({', '.join(critical_matters)}). "
            "Exercise extra caution and recommend immediate attorney consultation."
        )

    # Check for multiple active matters (potential conflicts)
    if len(active_matters) >= 3:
        warnings.append(
            f"⚠️ MULTIPLE ACTIVE MATTERS: Client has {len(active_matters)} ongoing legal matters. "
            "Carefully check for potential conflicts or interactions between cases."
        )

    # Financial distress warnings
    financial_concerns = client_profile.get("financial_concerns", [])
    critical_financial = ["bankruptcy", "foreclosure", "debt collection", "tax liens"]

    critical_finances = [c for c in financial_concerns if any(crit.lower() in c.lower() for crit in critical_financial)]

    if critical_finances:
        warnings.append(
            f"⚠️ FINANCIAL DISTRESS: Client has {', '.join(critical_finances)}. "
            "Consider financial implications of legal strategies."
        )

    return warnings
