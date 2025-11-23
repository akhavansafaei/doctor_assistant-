/**
 * Language Switcher Component
 * Allows users to toggle between English and Persian
 */

import { useLanguage } from '@/contexts/LanguageContext';
import { Language } from '@/utils/i18n';

interface LanguageSwitcherProps {
  variant?: 'default' | 'compact' | 'icon';
  className?: string;
}

export default function LanguageSwitcher({ variant = 'default', className = '' }: LanguageSwitcherProps) {
  const { language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'fa' : 'en');
  };

  if (variant === 'icon') {
    return (
      <button
        onClick={toggleLanguage}
        className={`px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition ${className}`}
        title={language === 'en' ? 'Switch to Persian' : 'تغییر به انگلیسی'}
      >
        {language === 'en' ? '🇮🇷' : '🇬🇧'}
      </button>
    );
  }

  if (variant === 'compact') {
    return (
      <button
        onClick={toggleLanguage}
        className={`px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg font-medium text-sm hover:bg-gray-200 dark:hover:bg-gray-700 transition ${className}`}
      >
        {language === 'en' ? 'فارسی' : 'English'}
      </button>
    );
  }

  // Default variant - toggle buttons
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <button
        onClick={() => setLanguage('en')}
        className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
          language === 'en'
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300'
        }`}
      >
        English
      </button>
      <button
        onClick={() => setLanguage('fa')}
        className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
          language === 'fa'
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300'
        }`}
      >
        فارسی
      </button>
    </div>
  );
}
