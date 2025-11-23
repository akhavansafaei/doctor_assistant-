/**
 * Internationalization (i18n) utility for bilingual UI support
 * Supports English and Persian (Farsi)
 */

export type Language = 'en' | 'fa';

export interface Translations {
  en: Record<string, string>;
  fa: Record<string, string>;
}

// UI Translations
export const translations: Translations = {
  en: {
    // App
    'app.title': 'AI Doctor Chatbot',
    'app.subtitle': 'Your personal health assistant',

    // Navigation
    'nav.chat': 'Chat',
    'nav.profile': 'Profile',
    'nav.settings': 'Settings',
    'nav.logout': 'Logout',

    // Auth
    'auth.login': 'Login',
    'auth.signup': 'Sign Up',
    'auth.logout': 'Logout',
    'auth.forgotPassword': 'Forgot Password?',
    'auth.username': 'Username',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.fullName': 'Full Name',
    'auth.rememberMe': 'Remember me',
    'auth.dontHaveAccount': "Don't have an account?",
    'auth.alreadyHaveAccount': 'Already have an account?',
    'auth.welcomeBack': 'Welcome back!',
    'auth.createAccount': 'Create your account',

    // Chat
    'chat.connected': 'Connected',
    'chat.disconnected': 'Disconnected',
    'chat.typing': 'AI is typing...',
    'chat.newChat': 'New Chat',
    'chat.conversations': 'Conversations',
    'chat.messagePlaceholder': 'Type your message...',
    'chat.send': 'Send',
    'chat.emergency': 'Emergency Detected',
    'chat.aiDoctor': 'AI Doctor Assistant',

    // Profile
    'profile.title': 'Health Profile',
    'profile.subtitle': 'Keep your health information up to date',
    'profile.basicInfo': 'Basic Information',
    'profile.medicalHistory': 'Medical History',
    'profile.allergies': 'Allergies',
    'profile.medications': 'Current Medications',
    'profile.surgeries': 'Past Surgeries',
    'profile.lifestyle': 'Lifestyle',
    'profile.emergencyContact': 'Emergency Contact',
    'profile.save': 'Save Health Profile',
    'profile.cancel': 'Cancel',
    'profile.age': 'Age',
    'profile.gender': 'Gender',
    'profile.height': 'Height (cm)',
    'profile.weight': 'Weight (kg)',
    'profile.bloodType': 'Blood Type',
    'profile.bmi': 'BMI',
    'profile.chronicConditions': 'Chronic Conditions',
    'profile.drugAllergies': 'Drug Allergies',
    'profile.foodAllergies': 'Food Allergies',
    'profile.environmentalAllergies': 'Environmental Allergies',
    'profile.medicationName': 'Medication name',
    'profile.dosage': 'Dosage',
    'profile.add': 'Add',
    'profile.smokingStatus': 'Smoking Status',
    'profile.alcoholConsumption': 'Alcohol Consumption',
    'profile.exerciseFrequency': 'Exercise Frequency',
    'profile.emergencyContactName': 'Name',
    'profile.emergencyContactRelationship': 'Relationship',
    'profile.emergencyContactPhone': 'Phone Number',

    // Profile Completion
    'profileCompletion.incomplete': 'Complete your health profile for personalized advice',
    'profileCompletion.complete': 'Health profile complete!',
    'profileCompletion.completeNow': 'Complete Now →',
    'profileCompletion.missing': 'Missing',

    // Settings
    'settings.title': 'Settings',
    'settings.general': 'General',
    'settings.appearance': 'Appearance',
    'settings.notifications': 'Notifications',
    'settings.account': 'Account',
    'settings.language': 'Language',
    'settings.theme': 'Theme',
    'settings.soundEnabled': 'Sound Effects',
    'settings.showSources': 'Show Sources',

    // Common
    'common.loading': 'Loading...',
    'common.saving': 'Saving...',
    'common.saved': 'Saved successfully',
    'common.error': 'An error occurred',
    'common.retry': 'Retry',
    'common.close': 'Close',
    'common.confirm': 'Confirm',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.search': 'Search',
    'common.filter': 'Filter',
    'common.male': 'Male',
    'common.female': 'Female',
    'common.other': 'Other',

    // Notifications
    'notification.profileUpdated': 'Health profile updated successfully!',
    'notification.profileOnboarding': 'Profile onboarding started',
    'notification.profileComplete': 'Health profile completed! Your advice will now be personalized.',
    'notification.connectionLost': 'Disconnected from server. Reconnecting...',
    'notification.messageFailed': 'Failed to send message',
  },
  fa: {
    // App
    'app.title': 'دستیار پزشکی هوش مصنوعی',
    'app.subtitle': 'دستیار سلامت شخصی شما',

    // Navigation
    'nav.chat': 'گفتگو',
    'nav.profile': 'پروفایل',
    'nav.settings': 'تنظیمات',
    'nav.logout': 'خروج',

    // Auth
    'auth.login': 'ورود',
    'auth.signup': 'ثبت‌نام',
    'auth.logout': 'خروج',
    'auth.forgotPassword': 'فراموشی رمز عبور؟',
    'auth.username': 'نام کاربری',
    'auth.email': 'ایمیل',
    'auth.password': 'رمز عبور',
    'auth.fullName': 'نام کامل',
    'auth.rememberMe': 'مرا به خاطر بسپار',
    'auth.dontHaveAccount': 'حساب کاربری ندارید؟',
    'auth.alreadyHaveAccount': 'قبلاً حساب کاربری دارید؟',
    'auth.welcomeBack': 'خوش آمدید!',
    'auth.createAccount': 'ایجاد حساب کاربری',

    // Chat
    'chat.connected': 'متصل',
    'chat.disconnected': 'قطع شده',
    'chat.typing': 'هوش مصنوعی در حال تایپ...',
    'chat.newChat': 'گفتگوی جدید',
    'chat.conversations': 'گفتگوها',
    'chat.messagePlaceholder': 'پیام خود را بنویسید...',
    'chat.send': 'ارسال',
    'chat.emergency': 'وضعیت اضطراری شناسایی شد',
    'chat.aiDoctor': 'دستیار پزشکی هوش مصنوعی',

    // Profile
    'profile.title': 'پروفایل سلامت',
    'profile.subtitle': 'اطلاعات سلامتی خود را به‌روز نگه دارید',
    'profile.basicInfo': 'اطلاعات پایه',
    'profile.medicalHistory': 'سابقه پزشکی',
    'profile.allergies': 'آلرژی‌ها',
    'profile.medications': 'داروهای فعلی',
    'profile.surgeries': 'جراحی‌های گذشته',
    'profile.lifestyle': 'سبک زندگی',
    'profile.emergencyContact': 'تماس اضطراری',
    'profile.save': 'ذخیره پروفایل سلامت',
    'profile.cancel': 'لغو',
    'profile.age': 'سن',
    'profile.gender': 'جنسیت',
    'profile.height': 'قد (سانتی‌متر)',
    'profile.weight': 'وزن (کیلوگرم)',
    'profile.bloodType': 'گروه خونی',
    'profile.bmi': 'شاخص توده بدنی',
    'profile.chronicConditions': 'بیماری‌های مزمن',
    'profile.drugAllergies': 'آلرژی دارویی',
    'profile.foodAllergies': 'آلرژی غذایی',
    'profile.environmentalAllergies': 'آلرژی محیطی',
    'profile.medicationName': 'نام دارو',
    'profile.dosage': 'دوز مصرف',
    'profile.add': 'افزودن',
    'profile.smokingStatus': 'وضعیت سیگار',
    'profile.alcoholConsumption': 'مصرف الکل',
    'profile.exerciseFrequency': 'فراوانی ورزش',
    'profile.emergencyContactName': 'نام',
    'profile.emergencyContactRelationship': 'نسبت',
    'profile.emergencyContactPhone': 'شماره تلفن',

    // Profile Completion
    'profileCompletion.incomplete': 'پروفایل سلامت خود را برای مشاوره شخصی‌سازی شده تکمیل کنید',
    'profileCompletion.complete': 'پروفایل سلامت کامل است!',
    'profileCompletion.completeNow': 'تکمیل کنید ←',
    'profileCompletion.missing': 'ناقص',

    // Settings
    'settings.title': 'تنظیمات',
    'settings.general': 'عمومی',
    'settings.appearance': 'ظاهر',
    'settings.notifications': 'اعلان‌ها',
    'settings.account': 'حساب کاربری',
    'settings.language': 'زبان',
    'settings.theme': 'تم',
    'settings.soundEnabled': 'جلوه‌های صوتی',
    'settings.showSources': 'نمایش منابع',

    // Common
    'common.loading': 'در حال بارگذاری...',
    'common.saving': 'در حال ذخیره...',
    'common.saved': 'با موفقیت ذخیره شد',
    'common.error': 'خطایی رخ داد',
    'common.retry': 'تلاش مجدد',
    'common.close': 'بستن',
    'common.confirm': 'تأیید',
    'common.delete': 'حذف',
    'common.edit': 'ویرایش',
    'common.search': 'جستجو',
    'common.filter': 'فیلتر',
    'common.male': 'مرد',
    'common.female': 'زن',
    'common.other': 'دیگر',

    // Notifications
    'notification.profileUpdated': 'پروفایل سلامت با موفقیت به‌روزرسانی شد!',
    'notification.profileOnboarding': 'ثبت پروفایل آغاز شد',
    'notification.profileComplete': '🎉 پروفایل سلامت تکمیل شد! مشاوره شما اکنون شخصی‌سازی می‌شود.',
    'notification.connectionLost': 'اتصال قطع شد. در حال اتصال مجدد...',
    'notification.messageFailed': 'ارسال پیام ناموفق بود',
  },
};

/**
 * Get translation for a key
 * @param key Translation key
 * @param lang Language code
 * @returns Translated string
 */
export function t(key: string, lang: Language = 'en'): string {
  return translations[lang][key] || translations.en[key] || key;
}

/**
 * Detect if language is RTL (right-to-left)
 * @param lang Language code
 * @returns true if RTL
 */
export function isRTL(lang: Language): boolean {
  return lang === 'fa';
}

/**
 * Get direction for CSS
 * @param lang Language code
 * @returns 'rtl' or 'ltr'
 */
export function getDirection(lang: Language): 'rtl' | 'ltr' {
  return isRTL(lang) ? 'rtl' : 'ltr';
}

/**
 * Get text alignment for language
 * @param lang Language code
 * @returns 'right' or 'left'
 */
export function getTextAlign(lang: Language): 'right' | 'left' {
  return isRTL(lang) ? 'right' : 'left';
}

/**
 * Get font family for language
 * @param lang Language code
 * @returns Font family string
 */
export function getFontFamily(lang: Language): string {
  if (lang === 'fa') {
    return "'Vazir', 'Tahoma', 'Arial', sans-serif";
  }
  return "'Inter', 'Roboto', 'Arial', sans-serif";
}

/**
 * Detect language from text (simple heuristic)
 * @param text Text to analyze
 * @returns Detected language code
 */
export function detectLanguage(text: string): Language {
  // Check for Persian characters
  const persianRegex = /[\u0600-\u06FF\uFB50-\uFDFF]/;

  const persianChars = (text.match(persianRegex) || []).length;
  const totalChars = text.replace(/\s/g, '').length;

  if (totalChars === 0) return 'en';

  // If more than 30% Persian characters, consider it Persian
  return (persianChars / totalChars) > 0.3 ? 'fa' : 'en';
}

/**
 * Format number for language (e.g., Persian numerals)
 * @param num Number to format
 * @param lang Language code
 * @returns Formatted number string
 */
export function formatNumber(num: number, lang: Language): string {
  if (lang === 'fa') {
    // Convert to Persian numerals
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return num.toString().replace(/\d/g, (digit) => persianDigits[parseInt(digit)]);
  }
  return num.toString();
}

export default {
  t,
  isRTL,
  getDirection,
  getTextAlign,
  getFontFamily,
  detectLanguage,
  formatNumber,
};
