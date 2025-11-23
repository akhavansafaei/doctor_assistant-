"""Utility to inject patient profile context into LLM prompts"""
from typing import Dict, Any, Optional


def format_profile_for_prompt(health_profile: Optional[Dict[str, Any]]) -> str:
    """
    Format health profile into a context string for LLM prompts

    Args:
        health_profile: Patient's health profile data

    Returns:
        Formatted context string
    """
    if not health_profile:
        return ""

    context_parts = ["PATIENT HEALTH PROFILE:"]

    # Basic information
    basic_info = []
    if health_profile.get("age"):
        basic_info.append(f"Age: {health_profile['age']} years")

    if health_profile.get("gender"):
        basic_info.append(f"Gender: {health_profile['gender']}")

    if health_profile.get("height_cm") and health_profile.get("weight_kg"):
        height = health_profile["height_cm"]
        weight = health_profile["weight_kg"]
        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)
        basic_info.append(f"Height: {height}cm, Weight: {weight}kg (BMI: {bmi:.1f})")

    if health_profile.get("blood_type"):
        basic_info.append(f"Blood Type: {health_profile['blood_type']}")

    if basic_info:
        context_parts.append("Basic Info: " + ", ".join(basic_info))

    # Chronic conditions
    chronic_conditions = health_profile.get("chronic_conditions", [])
    if chronic_conditions:
        context_parts.append(f"Chronic Conditions: {', '.join(chronic_conditions)}")
    else:
        context_parts.append("Chronic Conditions: None reported")

    # Allergies
    allergies = health_profile.get("allergies", {})
    if allergies:
        allergy_list = []
        for category, items in allergies.items():
            if items:
                allergy_list.append(f"{category.title()}: {', '.join(items)}")

        if allergy_list:
            context_parts.append("Allergies: " + "; ".join(allergy_list))
        else:
            context_parts.append("Allergies: None reported")
    else:
        context_parts.append("Allergies: None reported")

    # Current medications
    medications = health_profile.get("current_medications", [])
    if medications:
        med_list = []
        for med in medications:
            if isinstance(med, dict):
                name = med.get("name", "Unknown")
                dose = med.get("dose", "")
                med_str = f"{name}"
                if dose:
                    med_str += f" ({dose})"
                med_list.append(med_str)
            else:
                med_list.append(str(med))

        context_parts.append(f"Current Medications: {', '.join(med_list)}")
    else:
        context_parts.append("Current Medications: None")

    # Past surgeries
    surgeries = health_profile.get("past_surgeries", [])
    if surgeries:
        surgery_list = []
        for surgery in surgeries:
            if isinstance(surgery, dict):
                name = surgery.get("name", "Unknown")
                date = surgery.get("date", "")
                surgery_str = f"{name}"
                if date:
                    surgery_str += f" ({date})"
                surgery_list.append(surgery_str)
            else:
                surgery_list.append(str(surgery))

        context_parts.append(f"Past Surgeries: {', '.join(surgery_list)}")

    # Lifestyle factors
    lifestyle = []
    if health_profile.get("smoking_status"):
        lifestyle.append(f"Smoking: {health_profile['smoking_status']}")

    if health_profile.get("alcohol_consumption"):
        lifestyle.append(f"Alcohol: {health_profile['alcohol_consumption']}")

    if health_profile.get("exercise_frequency"):
        lifestyle.append(f"Exercise: {health_profile['exercise_frequency']}")

    if lifestyle:
        context_parts.append("Lifestyle: " + ", ".join(lifestyle))

    # Add important note
    context_parts.append("")
    context_parts.append("IMPORTANT: Consider this patient profile when providing medical advice. Account for their chronic conditions, medications, and allergies in your recommendations.")

    return "\n".join(context_parts)


def get_critical_warnings(health_profile: Optional[Dict[str, Any]]) -> list[str]:
    """
    Extract critical warnings from profile that should be highlighted

    Args:
        health_profile: Patient's health profile

    Returns:
        List of warning messages
    """
    warnings = []

    if not health_profile:
        return warnings

    # Drug allergies are critical
    allergies = health_profile.get("allergies", {})
    drug_allergies = allergies.get("drug", [])
    if drug_allergies:
        warnings.append(
            f"⚠️ DRUG ALLERGIES: Patient is allergic to {', '.join(drug_allergies)}. "
            "Avoid recommending these medications or related compounds."
        )

    # High-risk chronic conditions
    high_risk_conditions = ["diabetes", "heart disease", "kidney disease", "liver disease"]
    chronic_conditions = health_profile.get("chronic_conditions", [])
    critical_conditions = [c for c in chronic_conditions if any(risk in c.lower() for risk in high_risk_conditions)]

    if critical_conditions:
        warnings.append(
            f"⚠️ HIGH-RISK CONDITIONS: Patient has {', '.join(critical_conditions)}. "
            "Exercise extra caution with medication recommendations."
        )

    # Check for medication interactions
    medications = health_profile.get("current_medications", [])
    if len(medications) >= 5:
        warnings.append(
            "⚠️ POLYPHARMACY: Patient is on multiple medications. "
            "Carefully check for drug interactions."
        )

    return warnings
