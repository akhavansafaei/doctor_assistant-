"""Compliance and regulatory features"""
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import json


class ComplianceManager:
    """
    Manages HIPAA/GDPR compliance features
    - Audit logging
    - Data anonymization
    - Consent management
    - Right to deletion
    """

    def __init__(self):
        self.audit_logs = []

    async def log_interaction(
        self,
        user_id: int,
        interaction_type: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Log all interactions for compliance audit trail

        Returns:
            Log ID
        """
        log_entry = {
            "log_id": self._generate_log_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "interaction_type": interaction_type,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent
        }

        self.audit_logs.append(log_entry)

        # In production, write to secure audit log database
        # await self._write_to_audit_db(log_entry)

        return log_entry["log_id"]

    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize sensitive data for analytics

        Removes PII while preserving medical insights
        """
        anonymized = data.copy()

        # Fields to anonymize
        pii_fields = [
            "email", "phone", "full_name", "address",
            "emergency_contact_name", "emergency_contact_phone",
            "ssn", "medical_record_number"
        ]

        for field in pii_fields:
            if field in anonymized:
                anonymized[field] = self._hash_field(str(anonymized[field]))

        # Keep medical data but remove identifiers
        if "date_of_birth" in anonymized:
            # Convert to age bracket
            dob = anonymized["date_of_birth"]
            if isinstance(dob, str):
                from datetime import datetime
                dob = datetime.fromisoformat(dob.replace('Z', '+00:00'))

            age = (datetime.now() - dob).days // 365
            anonymized["age_bracket"] = self._get_age_bracket(age)
            del anonymized["date_of_birth"]

        return anonymized

    def _hash_field(self, value: str) -> str:
        """Hash sensitive field for anonymization"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]

    def _get_age_bracket(self, age: int) -> str:
        """Convert age to bracket for anonymization"""
        if age < 18:
            return "0-17"
        elif age < 30:
            return "18-29"
        elif age < 50:
            return "30-49"
        elif age < 65:
            return "50-64"
        else:
            return "65+"

    def _generate_log_id(self) -> str:
        """Generate unique log ID"""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:12]

    def validate_consent(self, user_id: int, consent_type: str) -> bool:
        """
        Validate user consent for data processing

        Args:
            user_id: User ID
            consent_type: Type of consent (e.g., 'data_processing', 'ai_analysis')

        Returns:
            True if user has given consent
        """
        # In production, check database for user consent records
        # For now, assume consent is required and return True
        # This should be implemented with actual consent management
        return True

    def get_data_for_export(self, user_id: int) -> Dict[str, Any]:
        """
        Export all user data (GDPR right to data portability)

        Args:
            user_id: User ID

        Returns:
            Complete user data in structured format
        """
        # In production, gather all user data from all tables
        data_export = {
            "export_date": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "personal_information": {},
            "health_profile": {},
            "medical_history": [],
            "conversations": [],
            "audit_logs": []
        }

        return data_export

    async def delete_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Delete all user data (GDPR right to erasure)

        Args:
            user_id: User ID

        Returns:
            Deletion report
        """
        deletion_report = {
            "user_id": user_id,
            "deletion_timestamp": datetime.utcnow().isoformat(),
            "deleted_records": {
                "user_profile": 0,
                "health_profile": 0,
                "medical_history": 0,
                "conversations": 0,
                "messages": 0,
                "audit_logs_anonymized": 0
            }
        }

        # In production:
        # 1. Delete user profile
        # 2. Delete health profile
        # 3. Delete medical history
        # 4. Delete conversations and messages
        # 5. Anonymize (not delete) audit logs for compliance
        # 6. Remove from vector database
        # 7. Clear cache

        return deletion_report

    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate compliance report for regulatory review

        Args:
            start_date: Report start date
            end_date: Report end date

        Returns:
            Compliance metrics and statistics
        """
        report = {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_interactions": 0,
            "emergency_detections": 0,
            "safety_violations": 0,
            "data_requests": 0,
            "deletion_requests": 0,
            "consent_updates": 0,
            "audit_log_entries": len(self.audit_logs)
        }

        return report

    def check_data_retention_policy(self, record_date: datetime) -> bool:
        """
        Check if data should be retained or purged based on retention policy

        Args:
            record_date: Date of the record

        Returns:
            True if should be retained, False if should be purged
        """
        # Example: Retain data for 7 years (medical record standard in many jurisdictions)
        retention_period_days = 7 * 365

        age_days = (datetime.utcnow() - record_date).days

        return age_days < retention_period_days

    def generate_medical_disclaimer(self, context: Optional[str] = None) -> str:
        """Generate appropriate medical disclaimer"""
        base_disclaimer = """
**IMPORTANT MEDICAL DISCLAIMER**

This AI chatbot is designed to provide general health information and should NOT be used:
- As a substitute for professional medical advice, diagnosis, or treatment
- To diagnose or treat any medical condition
- To prescribe medications or treatments
- As a replacement for in-person medical evaluation

ALWAYS seek the advice of your physician or other qualified health provider with any questions
you may have regarding a medical condition. Never disregard professional medical advice or delay
in seeking it because of something you have read from this AI system.

**In Case of Emergency:** If you are experiencing a medical emergency, call 911 (US) or your
local emergency services immediately. Do not rely on this chatbot for emergency medical guidance.

**No Doctor-Patient Relationship:** Use of this AI chatbot does not create a doctor-patient
relationship. The information provided is for educational purposes only.

**Data Privacy:** Your conversations are encrypted and stored securely in compliance with HIPAA
and GDPR regulations. We do not share your personal health information without your consent.

By using this service, you acknowledge that you have read, understood, and agree to these terms.
"""

        if context and "emergency" in context.lower():
            emergency_addendum = """
\n**EMERGENCY DETECTED:** Based on your symptoms, this may be a medical emergency.
CALL 911 or go to the nearest emergency room immediately. Do not wait for this chatbot's response.
"""
            return base_disclaimer + emergency_addendum

        return base_disclaimer
