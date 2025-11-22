"""Emergency condition detector"""
from typing import Dict, Any, List
import re


class EmergencyDetector:
    """
    Detects emergency medical conditions that require immediate attention
    """

    # Life-threatening conditions
    EMERGENCY_CONDITIONS = {
        "cardiac": {
            "keywords": [
                "chest pain", "heart attack", "severe chest pressure",
                "crushing chest pain", "pain radiating to arm",
                "pain in jaw", "chest tightness with sweating"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 IMMEDIATELY - Possible heart attack"
        },
        "respiratory": {
            "keywords": [
                "can't breathe", "cannot breathe", "difficulty breathing",
                "shortness of breath severe", "gasping for air",
                "turning blue", "lips blue", "choking"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 IMMEDIATELY - Severe respiratory distress"
        },
        "neurological": {
            "keywords": [
                "stroke", "facial drooping", "slurred speech",
                "severe headache sudden", "worst headache of life",
                "unconscious", "unresponsive", "seizure",
                "paralysis", "can't move arm", "can't move leg"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 IMMEDIATELY - Possible stroke or neurological emergency"
        },
        "bleeding": {
            "keywords": [
                "severe bleeding", "heavy bleeding", "bleeding won't stop",
                "coughing blood", "vomiting blood", "blood in stool severe"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 IMMEDIATELY - Severe bleeding"
        },
        "trauma": {
            "keywords": [
                "severe head injury", "head trauma", "fell from height",
                "car accident", "severe injury", "broken neck",
                "spinal injury", "compound fracture"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 IMMEDIATELY - Severe trauma"
        },
        "allergic": {
            "keywords": [
                "anaphylaxis", "severe allergic reaction",
                "throat closing", "tongue swelling", "difficulty swallowing severe",
                "hives all over body", "allergic reaction severe"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 IMMEDIATELY - Severe allergic reaction. Use EpiPen if available."
        },
        "mental_health": {
            "keywords": [
                "suicidal", "want to kill myself", "suicide",
                "want to die", "end my life", "harm myself"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 988 (Suicide & Crisis Lifeline) or 911 IMMEDIATELY"
        },
        "obstetric": {
            "keywords": [
                "pregnant severe pain", "pregnant bleeding heavy",
                "baby not moving", "severe pregnancy pain",
                "pregnancy bleeding third trimester"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 or go to ER IMMEDIATELY"
        },
        "poisoning": {
            "keywords": [
                "overdose", "poisoning", "swallowed poison",
                "took too many pills", "ingested chemicals"
            ],
            "severity": "CRITICAL",
            "recommendation": "CALL 911 and Poison Control (1-800-222-1222) IMMEDIATELY"
        },
        "abdominal": {
            "keywords": [
                "severe abdominal pain", "severe stomach pain",
                "appendicitis", "rigid abdomen", "rebound tenderness"
            ],
            "severity": "URGENT",
            "recommendation": "Go to ER immediately - Possible surgical emergency"
        }
    }

    def __init__(self):
        # Compile regex patterns for faster matching
        self.patterns = {}
        for category, data in self.EMERGENCY_CONDITIONS.items():
            patterns = []
            for keyword in data["keywords"]:
                # Create regex pattern that matches the keyword with word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                patterns.append(pattern)
            self.patterns[category] = patterns

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect emergency conditions in text

        Returns:
            Dict with emergency status, detected conditions, and recommendations
        """
        text_lower = text.lower()

        detected_emergencies = []
        max_severity = None
        recommendations = []

        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    condition_data = self.EMERGENCY_CONDITIONS[category]

                    detected_emergencies.append({
                        "category": category,
                        "severity": condition_data["severity"],
                        "recommendation": condition_data["recommendation"],
                        "matched_keyword": pattern
                    })

                    if max_severity is None or condition_data["severity"] == "CRITICAL":
                        max_severity = condition_data["severity"]
                        if condition_data["recommendation"] not in recommendations:
                            recommendations.append(condition_data["recommendation"])

                    break  # Only match once per category

        is_emergency = len(detected_emergencies) > 0

        result = {
            "is_emergency": is_emergency,
            "severity": max_severity or "NONE",
            "detected_conditions": detected_emergencies,
            "immediate_action": recommendations[0] if recommendations else None,
            "all_recommendations": recommendations
        }

        # Add emergency numbers
        if is_emergency:
            result["emergency_contacts"] = self._get_emergency_contacts(detected_emergencies)

        return result

    def _get_emergency_contacts(self, detected_emergencies: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get relevant emergency contact numbers"""
        contacts = {
            "911": "Emergency Services (Fire, Police, Medical)",
        }

        # Add specific hotlines based on detected conditions
        for emergency in detected_emergencies:
            if emergency["category"] == "mental_health":
                contacts["988"] = "Suicide & Crisis Lifeline"
                contacts["crisis_text"] = "Text HOME to 741741 (Crisis Text Line)"

            if emergency["category"] == "poisoning":
                contacts["poison_control"] = "1-800-222-1222 (Poison Control)"

        return contacts

    def assess_urgency_level(self, text: str, symptoms_duration: Optional[str] = None) -> str:
        """
        Assess urgency level based on symptoms and duration

        Returns:
            EMERGENCY, URGENT, MODERATE, or ROUTINE
        """
        emergency_check = self.detect(text)

        if emergency_check["is_emergency"]:
            return "EMERGENCY"

        # Check for urgent keywords
        urgent_keywords = [
            "severe pain", "high fever", "rapid heartbeat",
            "confusion", "dizziness severe", "fainting",
            "deep cut", "broken bone", "severe burn",
            "persistent vomiting", "severe diarrhea"
        ]

        text_lower = text.lower()
        for keyword in urgent_keywords:
            if keyword in text_lower:
                return "URGENT"

        # Check duration
        if symptoms_duration:
            if any(word in symptoms_duration.lower() for word in ["weeks", "months"]):
                return "ROUTINE"
            elif any(word in symptoms_duration.lower() for word in ["days", "hours"]):
                return "MODERATE"

        return "MODERATE"
