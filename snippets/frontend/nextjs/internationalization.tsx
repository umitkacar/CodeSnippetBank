/**
 * Next.js Internationalization (i18n) patterns
 */

// next.config.js i18n setup
const nextConfig = {
  i18n: {
    locales: ['en', 'es', 'fr', 'de'],
    defaultLocale: 'en',
    localeDetection: true,
  },
};

// App Router i18n
// app/[lang]/layout.tsx
export async function generateStaticParams() {
  return [{ lang: 'en' }, { lang: 'es' }, { lang: 'fr' }];
}

export default function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { lang: string };
}) {
  return (
    <html lang={params.lang}>
      <body>{children}</body>
    </html>
  );
}

// Dictionary loader
const dictionaries = {
  en: () => import('./dictionaries/en.json').then((module) => module.default),
  es: () => import('./dictionaries/es.json').then((module) => module.default),
  fr: () => import('./dictionaries/fr.json').then((module) => module.default),
};

export const getDictionary = async (locale: keyof typeof dictionaries) => {
  return dictionaries[locale]();
};

// Using translations in page
export default async function Page({ params }: { params: { lang: string } }) {
  const dict = await getDictionary(params.lang as any);

  return (
    <div>
      <h1>{dict.title}</h1>
      <p>{dict.description}</p>
    </div>
  );
}

// Language switcher
'use client';

import { useRouter, usePathname } from 'next/navigation';

export function LanguageSwitcher({ currentLang }: { currentLang: string }) {
  const router = useRouter();
  const pathname = usePathname();

  const switchLanguage = (newLang: string) => {
    const newPath = pathname.replace(`/${currentLang}`, `/${newLang}`);
    router.push(newPath);
  };

  return (
    <select value={currentLang} onChange={(e) => switchLanguage(e.target.value)}>
      <option value="en">English</option>
      <option value="es">Español</option>
      <option value="fr">Français</option>
    </select>
  );
}

// Type-safe translations
type Dictionary = {
  title: string;
  description: string;
  buttons: {
    submit: string;
    cancel: string;
  };
};

export async function TypeSafePage({ params }: { params: { lang: string } }) {
  const dict: Dictionary = await getDictionary(params.lang as any);

  return (
    <div>
      <h1>{dict.title}</h1>
      <button>{dict.buttons.submit}</button>
    </div>
  );
}

// Next-intl integration
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';

export async function IntlLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages(params.locale);

  return (
    <NextIntlClientProvider locale={params.locale} messages={messages}>
      {children}
    </NextIntlClientProvider>
  );
}

// Using next-intl in component
'use client';

import { useTranslations } from 'next-intl';

export function TranslatedComponent() {
  const t = useTranslations('common');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}

// Pluralization
export function PluralExample({ count }: { count: number }) {
  const t = useTranslations();

  return <p>{t('items', { count })}</p>;
}

// Date and number formatting
import { useFormatter } from 'next-intl';

export function FormattedContent() {
  const format = useFormatter();

  const date = new Date();
  const number = 1234.56;

  return (
    <div>
      <p>{format.dateTime(date, { dateStyle: 'long' })}</p>
      <p>{format.number(number, { style: 'currency', currency: 'USD' })}</p>
    </div>
  );
}
