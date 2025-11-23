"""
Language Detection Utility

Detects whether a message is in English or Farsi (Persian) to ensure
the chatbot responds in the same language as the user.
"""

import re
from typing import Literal


LanguageCode = Literal["en", "fa"]


class LanguageDetector:
    """Detects language of user input (English or Farsi)"""

    # Persian/Farsi Unicode ranges
    PERSIAN_RANGE = (0x0600, 0x06FF)  # Arabic/Persian
    PERSIAN_EXTENDED_RANGE = (0xFB50, 0xFDFF)  # Arabic Presentation Forms

    # Common Persian words for additional confirmation
    PERSIAN_WORDS = [
        "سلام", "درد", "دارم", "است", "می", "که", "من", "این", "از", "را",
        "به", "با", "در", "برای", "یا", "چه", "هستم", "دکتر", "پزشک", "علامت"
    ]

    # Common English words
    ENGLISH_WORDS = [
        "the", "is", "am", "are", "have", "has", "had", "do", "does", "did",
        "pain", "i", "you", "he", "she", "it", "we", "they", "doctor", "symptom"
    ]

    @staticmethod
    def detect(text: str) -> LanguageCode:
        """
        Detect language of text

        Args:
            text: Input text to analyze

        Returns:
            "fa" for Farsi/Persian, "en" for English
        """
        if not text or not text.strip():
            return "en"  # Default to English for empty input

        # Count Persian and English characters
        persian_chars = 0
        english_chars = 0
        total_alpha_chars = 0

        for char in text:
            code_point = ord(char)

            # Check if Persian character
            if (LanguageDetector.PERSIAN_RANGE[0] <= code_point <= LanguageDetector.PERSIAN_RANGE[1] or
                LanguageDetector.PERSIAN_EXTENDED_RANGE[0] <= code_point <= LanguageDetector.PERSIAN_EXTENDED_RANGE[1]):
                persian_chars += 1
                total_alpha_chars += 1

            # Check if English character
            elif char.isalpha() and ord('a') <= ord(char.lower()) <= ord('z'):
                english_chars += 1
                total_alpha_chars += 1

        # If we have alphabetic characters, decide based on count
        if total_alpha_chars > 0:
            persian_ratio = persian_chars / total_alpha_chars

            # If more than 30% Persian characters, consider it Persian
            if persian_ratio > 0.3:
                return "fa"
            else:
                return "en"

        # Fallback: Check for common words
        text_lower = text.lower()

        # Check Persian words
        persian_word_count = sum(1 for word in LanguageDetector.PERSIAN_WORDS if word in text)

        # Check English words
        english_word_count = sum(1 for word in LanguageDetector.ENGLISH_WORDS if word in text_lower)

        if persian_word_count > english_word_count:
            return "fa"
        else:
            return "en"

    @staticmethod
    def get_language_name(language_code: LanguageCode) -> str:
        """Get full language name from code"""
        return "Persian (Farsi)" if language_code == "fa" else "English"

    @staticmethod
    def is_rtl(language_code: LanguageCode) -> bool:
        """Check if language is right-to-left"""
        return language_code == "fa"


def detect_language(text: str) -> LanguageCode:
    """
    Convenience function to detect language

    Args:
        text: Input text

    Returns:
        Language code ("en" or "fa")
    """
    return LanguageDetector.detect(text)


def get_language_instruction(language_code: LanguageCode) -> str:
    """
    Get instruction for LLM to respond in detected language

    Args:
        language_code: Detected language code

    Returns:
        Instruction string for LLM prompt
    """
    if language_code == "fa":
        return """
IMPORTANT - LANGUAGE INSTRUCTION:
The user is writing in Persian/Farsi. You MUST respond in Persian/Farsi (فارسی).
Use proper Persian grammar, vocabulary, and cultural context.
Maintain professional medical terminology in Persian.

زبان پاسخ: شما باید به زبان فارسی پاسخ دهید.
"""
    else:
        return """
IMPORTANT - LANGUAGE INSTRUCTION:
The user is writing in English. You MUST respond in English.
Use clear, professional medical English.
"""


def format_bilingual_disclaimer() -> dict:
    """
    Get medical disclaimer in both languages

    Returns:
        Dictionary with "en" and "fa" keys
    """
    return {
        "en": """
⚠️ MEDICAL DISCLAIMER:
This AI assistant provides general health information only and is NOT a substitute
for professional medical advice, diagnosis, or treatment. Always seek the advice
of your physician or other qualified health provider with any questions you may
have regarding a medical condition. Never disregard professional medical advice
or delay in seeking it because of something you have read here.

In case of emergency, call your local emergency number immediately.
""",
        "fa": """
⚠️ هشدار پزشکی:
این دستیار هوش مصنوعی تنها اطلاعات سلامتی عمومی ارائه می‌دهد و جایگزین مشاوره،
تشخیص یا درمان پزشکی حرفه‌ای نیست. همیشه برای هرگونه سؤال در مورد وضعیت سلامتی
خود به پزشک یا ارائه‌دهنده مراقبت‌های بهداشتی واجد شرایط مراجعه کنید. هرگز به
دلیل چیزی که در اینجا خوانده‌اید، مشاوره پزشکی حرفه‌ای را نادیده نگیرید یا در
دریافت آن تأخیر نکنید.

در موارد اضطراری، فوراً با شماره اورژانس محلی تماس بگیرید.
"""
    }


def get_emergency_message(language_code: LanguageCode) -> str:
    """
    Get emergency message in detected language

    Args:
        language_code: Language code

    Returns:
        Emergency message
    """
    if language_code == "fa":
        return """
🚨 وضعیت اضطراری شناسایی شد 🚨

فوراً با اورژانس تماس بگیرید یا به نزدیک‌ترین بیمارستان مراجعه کنید!

این یک وضعیت بالقوه تهدید کننده زندگی است و نیاز به توجه پزشکی فوری دارد.

⚠️ با شماره اورژانس محلی (در ایران: ۱۱۵) تماس بگیرید ⚠️
"""
    else:
        return """
🚨 EMERGENCY DETECTED 🚨

CALL EMERGENCY SERVICES OR GO TO THE NEAREST EMERGENCY ROOM IMMEDIATELY!

This is a potentially life-threatening situation that requires immediate medical attention.

⚠️ CALL YOUR LOCAL EMERGENCY NUMBER (911 in USA, 999 in UK, 112 in EU) ⚠️
"""


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_messages = [
        ("I have a headache", "en"),
        ("سلام، سردرد دارم", "fa"),
        ("من احساس درد در قفسه سینه می‌کنم", "fa"),
        ("What are the symptoms of flu?", "en"),
        ("علائم آنفلوانزا چیست؟", "fa"),
        ("I'm feeling dizzy and nauseous", "en"),
        ("سرگیجه و حالت تهوع دارم", "fa"),
    ]

    print("Language Detection Tests:")
    print("=" * 50)

    for message, expected in test_messages:
        detected = detect_language(message)
        status = "✓" if detected == expected else "✗"
        print(f"{status} '{message[:50]}...' → {detected} (expected: {expected})")

    print("\n" + "=" * 50)
    print("\nLanguage Instructions:")
    print("\nEnglish:")
    print(get_language_instruction("en"))
    print("\nPersian:")
    print(get_language_instruction("fa"))
