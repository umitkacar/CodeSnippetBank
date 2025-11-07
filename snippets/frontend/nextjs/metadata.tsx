/**
 * Next.js Metadata API examples
 */
import { Metadata } from 'next';

// Basic metadata
export const metadata: Metadata = {
  title: 'My Page',
  description: 'Page description',
};

// Metadata with template
export const metadataWithTemplate: Metadata = {
  title: {
    default: 'My Site',
    template: '%s | My Site',
  },
  description: 'Default description',
};

// Complete SEO metadata
export const completeSEO: Metadata = {
  title: 'Complete SEO Example',
  description: 'A complete example of SEO metadata in Next.js',
  keywords: ['nextjs', 'seo', 'metadata', 'react'],
  authors: [{ name: 'John Doe', url: 'https://johndoe.com' }],
  creator: 'John Doe',
  publisher: 'My Company',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://example.com'),
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
      'es-ES': '/es-ES',
    },
  },
  openGraph: {
    title: 'Complete SEO Example',
    description: 'Open Graph description',
    url: 'https://example.com',
    siteName: 'My Site',
    images: [
      {
        url: 'https://example.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'OG Image Alt',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Twitter Title',
    description: 'Twitter description',
    creator: '@username',
    images: ['https://example.com/twitter-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/shortcut-icon.png',
    apple: '/apple-icon.png',
    other: {
      rel: 'apple-touch-icon-precomposed',
      url: '/apple-touch-icon-precomposed.png',
    },
  },
  manifest: '/manifest.json',
  verification: {
    google: 'google-site-verification-code',
    yandex: 'yandex-verification-code',
    yahoo: 'yahoo-verification-code',
  },
  appleWebApp: {
    title: 'App Title',
    statusBarStyle: 'black-translucent',
    startupImage: ['/apple-splash-screen.png'],
  },
};

// Dynamic metadata
export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const product = await fetch(`https://api.example.com/products/${params.id}`)
    .then((res) => res.json());

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [product.image],
    },
  };
}

// Metadata for blog post
export const blogPostMetadata: Metadata = {
  title: 'Blog Post Title',
  description: 'Blog post description',
  authors: [{ name: 'Author Name' }],
  openGraph: {
    type: 'article',
    publishedTime: '2024-01-01T00:00:00.000Z',
    modifiedTime: '2024-01-02T00:00:00.000Z',
    authors: ['Author Name'],
    tags: ['nextjs', 'react', 'web development'],
  },
};

// E-commerce product metadata
export const productMetadata: Metadata = {
  title: 'Product Name',
  description: 'Product description',
  openGraph: {
    type: 'website',
    images: [
      {
        url: 'https://example.com/product.jpg',
        width: 800,
        height: 600,
        alt: 'Product image',
      },
    ],
  },
  other: {
    'product:price:amount': '99.99',
    'product:price:currency': 'USD',
  },
};

// Video metadata
export const videoMetadata: Metadata = {
  title: 'Video Title',
  description: 'Video description',
  openGraph: {
    type: 'video.movie',
    videos: [
      {
        url: 'https://example.com/video.mp4',
        width: 1920,
        height: 1080,
      },
    ],
  },
};

// JSON-LD structured data
export function StructuredData() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: 'Article Headline',
    description: 'Article description',
    image: 'https://example.com/image.jpg',
    datePublished: '2024-01-01T00:00:00.000Z',
    dateModified: '2024-01-02T00:00:00.000Z',
    author: {
      '@type': 'Person',
      name: 'Author Name',
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}
