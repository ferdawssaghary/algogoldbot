import React, { createContext, useContext, useState, useEffect } from 'react';

interface LanguageContextType {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Simple translations object
const translations = {
  en: {
    'app.title': 'Gold Trading Bot',
    'nav.dashboard': 'Dashboard',
    'nav.trading': 'Trading',
    'nav.settings': 'Settings',
    'nav.logout': 'Logout',
    'login.title': 'Login',
    'login.username': 'Username',
    'login.password': 'Password',
    'login.submit': 'Login',
    'dashboard.title': 'Dashboard',
    'trading.title': 'Trading',
    'settings.title': 'Settings',
  },
  fa: {
    'app.title': 'ربات معاملاتی طلا',
    'nav.dashboard': 'داشبورد',
    'nav.trading': 'معاملات',
    'nav.settings': 'تنظیمات',
    'nav.logout': 'خروج',
    'login.title': 'ورود',
    'login.username': 'نام کاربری',
    'login.password': 'رمز عبور',
    'login.submit': 'ورود',
    'dashboard.title': 'داشبورد',
    'trading.title': 'معاملات',
    'settings.title': 'تنظیمات',
  }
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState('en');

  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') || 'en';
    setLanguageState(savedLanguage);
  }, []);

  const setLanguage = (lang: string) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
    document.documentElement.dir = lang === 'fa' ? 'rtl' : 'ltr';
  };

  const t = (key: string): string => {
    return translations[language as keyof typeof translations]?.[key as keyof typeof translations.en] || key;
  };

  const value = {
    language,
    setLanguage,
    t
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};