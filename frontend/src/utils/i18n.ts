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
    'app.title': 'AI Law Assistant',
    'app.subtitle': 'Your intelligent legal companion',

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
    'chat.urgentMatter': 'Urgent Legal Matter Detected',
    'chat.aiLawyer': 'AI Law Assistant',

    // Profile
    'profile.title': 'Client Profile',
    'profile.subtitle': 'Keep your legal information up to date',
    'profile.basicInfo': 'Basic Information',
    'profile.legalHistory': 'Legal History',
    'profile.activeMatt': 'Active Legal Matters',
    'profile.legalAreas': 'Legal Areas of Interest',
    'profile.restrictions': 'Legal Restrictions',
    'profile.businessEntities': 'Business Entities',
    'profile.financialConcerns': 'Financial Concerns',
    'profile.emergencyContact': 'Emergency Contact',
    'profile.save': 'Save Client Profile',
    'profile.cancel': 'Cancel',
    'profile.occupation': 'Occupation',
    'profile.employer': 'Employer',
    'profile.citizenship': 'Citizenship',
    'profile.maritalStatus': 'Marital Status',
    'profile.legalAreasOfInterest': 'Legal Areas',
    'profile.activeLegalMatters': 'Active Matters',
    'profile.previousLegalIssues': 'Previous Issues',
    'profile.legalRestrictions': 'Restrictions',
    'profile.businessEntityName': 'Business name',
    'profile.entityType': 'Type',
    'profile.add': 'Add',
    'profile.preferredCommunication': 'Preferred Communication',
    'profile.emergencyContactName': 'Name',
    'profile.emergencyContactRelationship': 'Relationship',
    'profile.emergencyContactPhone': 'Phone Number',

    // Profile Completion
    'profileCompletion.incomplete': 'Complete your client profile for personalized legal guidance',
    'profileCompletion.complete': 'Client profile complete!',
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
    'settings.showSources': 'Show Legal Sources',

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
    'notification.profileUpdated': 'Client profile updated successfully!',
    'notification.profileOnboarding': 'Profile onboarding started',
    'notification.profileComplete': 'Client profile completed! Your guidance will now be personalized.',
    'notification.connectionLost': 'Disconnected from server. Reconnecting...',
    'notification.messageFailed': 'Failed to send message',
  },
  fa: {
    // App
    'app.title': 'دستیار حقوقی هوش مصنوعی',
    'app.subtitle': 'همراه هوشمند حقوقی شما',

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
    'chat.urgentMatter': 'موضوع حقوقی فوری شناسایی شد',
    'chat.aiLawyer': 'دستیار حقوقی هوش مصنوعی',

    // Profile
    'profile.title': 'پروفایل موکل',
    'profile.subtitle': 'اطلاعات حقوقی خود را به‌روز نگه دارید',
    'profile.basicInfo': 'اطلاعات پایه',
    'profile.legalHistory': 'سابقه حقوقی',
    'profile.activeMatters': 'موارد حقوقی فعال',
    'profile.legalAreas': 'زمینه‌های حقوقی مورد علاقه',
    'profile.restrictions': 'محدودیت‌های حقوقی',
    'profile.businessEntities': 'واحدهای تجاری',
    'profile.financialConcerns': 'نگرانی‌های مالی',
    'profile.emergencyContact': 'تماس اضطراری',
    'profile.save': 'ذخیره پروفایل موکل',
    'profile.cancel': 'لغو',
    'profile.occupation': 'شغل',
    'profile.employer': 'کارفرما',
    'profile.citizenship': 'تابعیت',
    'profile.maritalStatus': 'وضعیت تأهل',
    'profile.legalAreasOfInterest': 'زمینه‌های حقوقی',
    'profile.activeLegalMatters': 'موارد فعال',
    'profile.previousLegalIssues': 'مسائل قبلی',
    'profile.legalRestrictions': 'محدودیت‌ها',
    'profile.businessEntityName': 'نام کسب‌وکار',
    'profile.entityType': 'نوع',
    'profile.add': 'افزودن',
    'profile.preferredCommunication': 'روش ارتباط ترجیحی',
    'profile.emergencyContactName': 'نام',
    'profile.emergencyContactRelationship': 'نسبت',
    'profile.emergencyContactPhone': 'شماره تلفن',

    // Profile Completion
    'profileCompletion.incomplete': 'پروفایل موکل خود را برای راهنمایی حقوقی شخصی‌سازی شده تکمیل کنید',
    'profileCompletion.complete': 'پروفایل موکل کامل است!',
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
    'settings.showSources': 'نمایش منابع حقوقی',

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
    'notification.profileUpdated': 'پروفایل موکل با موفقیت به‌روزرسانی شد!',
    'notification.profileOnboarding': 'ثبت پروفایل آغاز شد',
    'notification.profileComplete': 'پروفایل موکل تکمیل شد! راهنمایی شما اکنون شخصی‌سازی می‌شود.',
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
