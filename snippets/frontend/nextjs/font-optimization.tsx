/**
 * Next.js Font Optimization examples
 */
import {
  Inter,
  Roboto,
  Open_Sans,
  Playfair_Display,
  Source_Code_Pro,
} from 'next/font/google';
import localFont from 'next/font/local';

// Google Fonts - Single font
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
});

export function InterFont() {
  return <div className={inter.className}>Text with Inter font</div>;
}

// Google Fonts - Multiple weights
const roboto = Roboto({
  weight: ['400', '700'],
  subsets: ['latin'],
  display: 'swap',
});

// Google Fonts - Variable font
const openSans = Open_Sans({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-open-sans',
});

// Google Fonts - Multiple fonts
const playfair = Playfair_Display({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-playfair',
});

const sourceCodePro = Source_Code_Pro({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
});

export function MultipleFonts() {
  return (
    <div className={`${playfair.variable} ${sourceCodePro.variable}`}>
      <h1 style={{ fontFamily: 'var(--font-playfair)' }}>Heading</h1>
      <code style={{ fontFamily: 'var(--font-mono)' }}>Code</code>
    </div>
  );
}

// Local fonts
const customFont = localFont({
  src: [
    {
      path: './fonts/custom-regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: './fonts/custom-bold.woff2',
      weight: '700',
      style: 'normal',
    },
  ],
  display: 'swap',
  variable: '--font-custom',
});

export function LocalFont() {
  return <div className={customFont.className}>Custom local font</div>;
}

// Multiple local fonts with variable
const myFont = localFont({
  src: './fonts/my-font.woff2',
  display: 'swap',
  variable: '--font-my',
});

// Preload fonts
const preloadedFont = Inter({
  subsets: ['latin'],
  preload: true,
  display: 'swap',
});

// Font with fallback
const fontWithFallback = Inter({
  subsets: ['latin'],
  display: 'swap',
  fallback: ['system-ui', 'arial'],
});

// Global font setup in layout
export function RootLayoutWithFonts({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${roboto.variable}`}>
      <body className={inter.className}>{children}</body>
    </html>
  );
}

// Tailwind CSS configuration for fonts
/**
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        serif: ['var(--font-playfair)', 'serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
    },
  },
};
*/

// CSS variables approach
export function CSSVariablesFont() {
  return (
    <div
      className={`${inter.variable} ${playfair.variable}`}
      style={{
        fontFamily: 'var(--font-inter)',
      }}
    >
      <h1 style={{ fontFamily: 'var(--font-playfair)' }}>Heading</h1>
      <p>Body text with Inter</p>
    </div>
  );
}

// Adjust line height
const customInter = Inter({
  subsets: ['latin'],
  display: 'swap',
  adjustFontFallback: true,
});

// Font with specific characters
const japaneseFont = Inter({
  subsets: ['latin', 'latin-ext'],
  display: 'swap',
});
