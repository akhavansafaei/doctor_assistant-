/**
 * Language Context for managing app language state
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Language, t, getDirection, isRTL } from '@/utils/i18n';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  direction: 'rtl' | 'ltr';
  isRTL: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  // Get initial language from localStorage or browser
  const getInitialLanguage = (): Language => {
    const saved = localStorage.getItem('language');
    if (saved === 'fa' || saved === 'en') {
      return saved;
    }
    // Detect from browser
    const browserLang = navigator.language.toLowerCase();
    return browserLang.startsWith('fa') || browserLang.startsWith('per') ? 'fa' : 'en';
  };

  const [language, setLanguageState] = useState<Language>(getInitialLanguage());

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
    // Update document direction
    document.documentElement.dir = getDirection(lang);
    document.documentElement.lang = lang;
  };

  // Set initial direction
  useEffect(() => {
    document.documentElement.dir = getDirection(language);
    document.documentElement.lang = language;
  }, [language]);

  const translate = (key: string) => t(key, language);

  const value: LanguageContextType = {
    language,
    setLanguage,
    t: translate,
    direction: getDirection(language),
    isRTL: isRTL(language),
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
