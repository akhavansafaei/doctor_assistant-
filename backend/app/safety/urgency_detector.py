"""Urgency detector for time-sensitive legal matters"""
from typing import Dict, Any, List, Optional
import re


class UrgencyDetector:
    """
    Detects time-sensitive legal matters that require immediate attention
    """

    # Time-sensitive legal matters
    URGENT_LEGAL_MATTERS = {
        "court_deadlines": {
            "keywords": [
                "court date tomorrow", "hearing tomorrow", "deadline today",
                "deadline tomorrow", "court in morning", "hearing today",
                "trial tomorrow", "due today", "filing deadline today"
            ],
            "urgency": "CRITICAL_URGENT",
            "recommendation": "CONTACT AN ATTORNEY IMMEDIATELY - Missing court deadlines can result in default judgment or loss of rights"
        },
        "statute_limitations": {
            "keywords": [
                "statute of limitations expiring", "deadline to file lawsuit",
                "time limit to sue", "last day to file", "statute running out",
                "deadline to file claim"
            ],
            "urgency": "CRITICAL_URGENT",
            "recommendation": "CONTACT AN ATTORNEY URGENTLY - Missing the statute of limitations deadline permanently bars your claim"
        },
        "eviction": {
            "keywords": [
                "eviction notice", "eviction tomorrow", "sheriff evicting",
                "lockout notice", "3 day notice", "30 day notice to vacate",
                "unlawful detainer", "eviction hearing"
            ],
            "urgency": "CRITICAL_URGENT",
            "recommendation": "SEEK LEGAL HELP IMMEDIATELY - You may have limited time to respond to eviction proceedings"
        },
        "criminal_matters": {
            "keywords": [
                "arrested", "going to jail", "criminal charges",
                "arraignment tomorrow", "bail hearing", "police questioning",
                "detained", "in custody", "criminal investigation"
            ],
            "urgency": "CRITICAL_URGENT",
            "recommendation": "CONTACT A CRIMINAL DEFENSE ATTORNEY IMMEDIATELY - Exercise your right to remain silent and request an attorney"
        },
        "restraining_orders": {
            "keywords": [
                "restraining order hearing", "protective order", "tro hearing",
                "domestic violence order", "restraining order tomorrow",
                "order of protection hearing"
            ],
            "urgency": "CRITICAL_URGENT",
            "recommendation": "CONTACT AN ATTORNEY IMMEDIATELY - Restraining order hearings have serious consequences"
        },
        "custody_emergency": {
            "keywords": [
                "child taken", "custody emergency", "child abduction",
                "emergency custody hearing", "child not returned",
                "parental kidnapping", "violation of custody order"
            ],
            "urgency": "CRITICAL_URGENT",
            "recommendation": "CONTACT FAMILY LAW ATTORNEY AND LAW ENFORCEMENT IMMEDIATELY"
        },
        "foreclosure": {
            "keywords": [
                "foreclosure sale tomorrow", "home being foreclosed",
                "foreclosure auction", "notice of default", "foreclosure notice",
                "trustee sale", "foreclosure hearing"
            ],
            "urgency": "URGENT",
            "recommendation": "CONTACT A FORECLOSURE ATTORNEY URGENTLY - You may have options to prevent foreclosure"
        },
        "deportation": {
            "keywords": [
                "ice detention", "deportation", "removal proceedings",
                "immigration court", "detained by ice", "immigration hearing",
                "removal hearing", "deportation order"
            ],
            "urgency": "CRITICAL_URGENT",
            "recommendation": "CONTACT AN IMMIGRATION ATTORNEY IMMEDIATELY - Deportation proceedings require urgent legal representation"
        },
        "bankruptcy_urgency": {
            "keywords": [
                "wage garnishment starting", "bank account frozen",
                "car being repossessed", "eviction and garnishment",
                "foreclosure sale date set", "repossession tomorrow"
            ],
            "urgency": "URGENT",
            "recommendation": "CONSULT WITH A BANKRUPTCY ATTORNEY URGENTLY - Bankruptcy filing may provide immediate relief"
        },
        "employment_termination": {
            "keywords": [
                "wrongful termination", "fired illegally", "discrimination at work",
                "retaliation by employer", "hostile work environment",
                "employment discrimination", "whistleblower retaliation"
            ],
            "urgency": "URGENT",
            "recommendation": "CONSULT WITH AN EMPLOYMENT ATTORNEY - Discrimination and retaliation claims have strict filing deadlines"
        },
        "contract_breach": {
            "keywords": [
                "breach of contract", "contract violation", "business dispute urgent",
                "partnership dispute", "contract dispute deadline",
                "breach of agreement time-sensitive"
            ],
            "urgency": "MODERATE",
            "recommendation": "Consult with a contract attorney to review your options and deadlines"
        },
        "personal_injury": {
            "keywords": [
                "accident claim", "injury claim", "car accident lawsuit",
                "slip and fall claim", "medical malpractice deadline",
                "personal injury statute"
            ],
            "urgency": "MODERATE",
            "recommendation": "Consult with a personal injury attorney - Injury claims have statutes of limitations"
        }
    }

    def __init__(self):
        # Compile regex patterns for faster matching
        self.patterns = {}
        for category, data in self.URGENT_LEGAL_MATTERS.items():
            patterns = []
            for keyword in data["keywords"]:
                # Create regex pattern that matches the keyword with word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                patterns.append(pattern)
            self.patterns[category] = patterns

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect urgent legal matters in text

        Returns:
            Dict with urgency status, detected matters, and recommendations
        """
        text_lower = text.lower()

        detected_urgent_matters = []
        max_urgency = None
        recommendations = []

        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matter_data = self.URGENT_LEGAL_MATTERS[category]

                    detected_urgent_matters.append({
                        "category": category,
                        "urgency": matter_data["urgency"],
                        "recommendation": matter_data["recommendation"],
                        "matched_keyword": pattern
                    })

                    if max_urgency is None or matter_data["urgency"] == "CRITICAL_URGENT":
                        max_urgency = matter_data["urgency"]
                        if matter_data["recommendation"] not in recommendations:
                            recommendations.append(matter_data["recommendation"])

                    break  # Only match once per category

        is_urgent = len(detected_urgent_matters) > 0

        result = {
            "is_urgent": is_urgent,
            "urgency": max_urgency or "ROUTINE",
            "detected_matters": detected_urgent_matters,
            "immediate_action": recommendations[0] if recommendations else None,
            "all_recommendations": recommendations
        }

        # Add legal resource contacts
        if is_urgent:
            result["urgent_contacts"] = self._get_urgent_legal_resources(detected_urgent_matters)

        return result

    def _get_urgent_legal_resources(self, detected_matters: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get relevant urgent legal resource contacts"""
        contacts = {
            "attorney_referral": "Contact your state bar association's attorney referral service",
        }

        # Add specific resources based on detected matters
        for matter in detected_matters:
            if matter["category"] == "criminal_matters":
                contacts["public_defender"] = "Request a public defender if you cannot afford an attorney"
                contacts["right_to_silence"] = "Exercise your right to remain silent until you have legal representation"

            if matter["category"] == "eviction":
                contacts["legal_aid"] = "Contact your local legal aid society for emergency eviction assistance"
                contacts["tenant_rights"] = "Check your local tenant rights hotline"

            if matter["category"] == "deportation":
                contacts["immigration_legal_aid"] = "Contact RAICES, ACLU, or local immigration legal services immediately"

            if matter["category"] == "custody_emergency":
                contacts["law_enforcement"] = "Contact local law enforcement if child safety is at risk"
                contacts["emergency_custody"] = "File for emergency custody order at your local family court"

            if matter["category"] == "domestic_violence":
                contacts["domestic_violence_hotline"] = "1-800-799-7233 (National Domestic Violence Hotline)"

        return contacts

    def assess_urgency_level(
        self,
        text: str,
        matter_timeline: Optional[str] = None,
        active_matters: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Assess urgency level based on legal matter and timeline

        Returns:
            CRITICAL_URGENT, URGENT, MODERATE, ROUTINE, or INFO
        """
        urgency_check = self.detect(text)

        if urgency_check["is_urgent"]:
            return urgency_check["urgency"]

        # Check for urgent timeline keywords
        urgent_timeline_keywords = [
            "urgent", "asap", "time-sensitive", "deadline approaching",
            "running out of time", "need help now", "immediately",
            "court soon", "hearing soon", "deadline coming up"
        ]

        text_lower = text.lower()
        for keyword in urgent_timeline_keywords:
            if keyword in text_lower:
                return "URGENT"

        # Check matter timeline
        if matter_timeline:
            timeline_lower = matter_timeline.lower()
            if any(word in timeline_lower for word in ["days", "week", "tomorrow", "soon"]):
                return "URGENT"
            elif any(word in timeline_lower for word in ["month", "months"]):
                return "MODERATE"
            elif any(word in timeline_lower for word in ["year", "years"]):
                return "ROUTINE"

        # Check if multiple active matters (higher complexity)
        if active_matters and len(active_matters) >= 3:
            return "MODERATE"

        # Check for informational queries
        info_keywords = [
            "what is", "how does", "can you explain", "tell me about",
            "general question", "just curious", "wondering about"
        ]

        for keyword in info_keywords:
            if keyword in text_lower:
                return "INFO"

        return "MODERATE"
