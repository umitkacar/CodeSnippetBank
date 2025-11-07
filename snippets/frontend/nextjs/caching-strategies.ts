/**
 * Next.js Caching Strategies
 */
import { unstable_cache, revalidateTag, revalidatePath } from 'next/cache';

// Request memoization (automatic in same render pass)
async function getUser(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}`);
  return res.json();
}

// Data cache with different strategies
export async function DataCachingExamples() {
  // 1. Force cache (default)
  const staticData = await fetch('https://api.example.com/static', {
    cache: 'force-cache',
  });

  // 2. No store (always fresh)
  const dynamicData = await fetch('https://api.example.com/dynamic', {
    cache: 'no-store',
  });

  // 3. Revalidate after time
  const revalidatedData = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 }, // Revalidate every hour
  });

  // 4. Tagged cache
  const taggedData = await fetch('https://api.example.com/products', {
    next: { tags: ['products', 'inventory'] },
  });

  return { staticData, dynamicData, revalidatedData, taggedData };
}

// Unstable cache wrapper
const getCachedUser = unstable_cache(
  async (id: string) => {
    return await fetch(`https://api.example.com/users/${id}`).then((r) =>
      r.json()
    );
  },
  ['user'],
  {
    revalidate: 3600,
    tags: ['users'],
  }
);

// On-demand revalidation
'use server';

export async function revalidateProducts() {
  revalidateTag('products');
}

export async function revalidateProductsPage() {
  revalidatePath('/products');
}

// Full route cache configuration
export const revalidate = 3600; // ISR - revalidate every hour
export const dynamic = 'force-static'; // Generate at build time
export const fetchCache = 'default-cache'; // Use cache by default

// Per-page caching strategy
export const metadata = {
  title: 'Cached Page',
};

export default async function CachedPage() {
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 60 },
  });

  return <div>{JSON.stringify(await data.json())}</div>;
}

// Segment config for caching
export const dynamicParams = true; // Allow dynamic params not in generateStaticParams
export const runtime = 'nodejs'; // 'nodejs' | 'edge'

// Cache tags pattern
async function getProductsWithTags() {
  const res = await fetch('https://api.example.com/products', {
    next: {
      tags: ['products', 'catalog'],
      revalidate: 3600,
    },
  });
  return res.json();
}

// Multiple cache tags
async function getProductById(id: string) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: {
      tags: ['products', `product-${id}`],
    },
  });
  return res.json();
}

// Opt out of caching
export const dynamic = 'force-dynamic';
export const revalidate = 0;

// Client-side caching with SWR
'use client';

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function ClientCachedComponent() {
  const { data, error, isLoading } = useSWR('/api/data', fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: true,
    refreshInterval: 60000, // 1 minute
  });

  if (error) return <div>Failed to load</div>;
  if (isLoading) return <div>Loading...</div>;

  return <div>{JSON.stringify(data)}</div>;
}

// React Query caching
'use client';

import { useQuery } from '@tanstack/react-query';

export function ReactQueryComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['todos'],
    queryFn: () => fetch('/api/todos').then((r) => r.json()),
    staleTime: 60000, // Data is fresh for 1 minute
    cacheTime: 300000, // Keep in cache for 5 minutes
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading data</div>;

  return <div>{JSON.stringify(data)}</div>;
}
