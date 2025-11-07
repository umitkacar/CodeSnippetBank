/**
 * Next.js Performance Optimization Techniques
 */
import dynamic from 'next/dynamic';
import { Suspense, lazy } from 'react';
import Script from 'next/script';

// 1. Dynamic imports with loading
const DynamicComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>,
  ssr: false, // Disable SSR for this component
});

// 2. Dynamic import with named export
const DynamicWithNamed = dynamic(
  () => import('./Components').then((mod) => mod.SpecificComponent),
  {
    loading: () => <div>Loading component...</div>,
  }
);

// 3. Multiple dynamic imports
const DynamicHeader = dynamic(() => import('./Header'));
const DynamicFooter = dynamic(() => import('./Footer'));

export function OptimizedLayout() {
  return (
    <div>
      <DynamicHeader />
      <main>Content</main>
      <DynamicFooter />
    </div>
  );
}

// 4. Preload components
const PreloadedComponent = dynamic(() => import('./Component'), {
  // @ts-ignore
  suspense: true,
});

// 5. Script optimization
export function ScriptOptimization() {
  return (
    <>
      {/* Load after page is interactive */}
      <Script
        src="https://example.com/script.js"
        strategy="afterInteractive"
      />

      {/* Load before page is interactive */}
      <Script
        src="https://example.com/critical.js"
        strategy="beforeInteractive"
      />

      {/* Load during idle time */}
      <Script src="https://example.com/analytics.js" strategy="lazyOnload" />

      {/* Inline script */}
      <Script id="inline-script">
        {`console.log('Inline script');`}
      </Script>
    </>
  );
}

// 6. Font optimization
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
  variable: '--font-inter',
});

// 7. Image optimization strategies
import Image from 'next/image';

export function OptimizedImages() {
  return (
    <div>
      {/* Priority loading for above-the-fold images */}
      <Image
        src="/hero.jpg"
        alt="Hero"
        width={1200}
        height={600}
        priority
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,..."
      />

      {/* Lazy loading for below-the-fold */}
      <Image
        src="/gallery.jpg"
        alt="Gallery"
        width={800}
        height={600}
        loading="lazy"
        sizes="(max-width: 768px) 100vw, 50vw"
      />
    </div>
  );
}

// 8. Parallel data fetching
export async function ParallelFetch() {
  const [users, posts, comments] = await Promise.all([
    fetch('https://api.example.com/users').then((r) => r.json()),
    fetch('https://api.example.com/posts').then((r) => r.json()),
    fetch('https://api.example.com/comments').then((r) => r.json()),
  ]);

  return { users, posts, comments };
}

// 9. Streaming with Suspense
export function StreamingLayout() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <AsyncHeader />
      </Suspense>

      <Suspense fallback={<ContentSkeleton />}>
        <AsyncContent />
      </Suspense>
    </div>
  );
}

// 10. Route prefetching
'use client';

import Link from 'next/link';

export function PrefetchedLinks() {
  return (
    <nav>
      {/* Prefetch on hover (default) */}
      <Link href="/products" prefetch={true}>
        Products
      </Link>

      {/* No prefetch */}
      <Link href="/contact" prefetch={false}>
        Contact
      </Link>
    </nav>
  );
}

// 11. Bundle size optimization
// next.config.js
const config = {
  experimental: {
    optimizePackageImports: ['lodash', 'date-fns'],
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Reduce client bundle size
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
        },
      };
    }
    return config;
  },
};

// 12. Static generation for maximum performance
export async function generateStaticParams() {
  const products = await fetch('https://api.example.com/products').then((r) =>
    r.json()
  );

  return products.map((product: any) => ({
    id: product.id.toString(),
  }));
}

// 13. Edge runtime for faster response
export const runtime = 'edge';

export async function EdgePage() {
  return <div>Fast edge response</div>;
}

// Helper components
async function AsyncHeader() {
  const data = await fetch('https://api.example.com/header').then((r) =>
    r.json()
  );
  return <header>{data.title}</header>;
}

async function AsyncContent() {
  const data = await fetch('https://api.example.com/content').then((r) =>
    r.json()
  );
  return <main>{data.content}</main>;
}

function HeaderSkeleton() {
  return <div className="h-16 bg-gray-200 animate-pulse" />;
}

function ContentSkeleton() {
  return <div className="h-96 bg-gray-200 animate-pulse" />;
}
