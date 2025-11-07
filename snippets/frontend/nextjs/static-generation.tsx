/**
 * Next.js Static Site Generation (SSG) examples
 */

// Basic static page
export default async function StaticPage() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'force-cache', // Default - cache indefinitely
  }).then((res) => res.json());

  return <div>{JSON.stringify(data)}</div>;
}

// Static page with revalidation (ISR)
export const revalidate = 3600; // Revalidate every hour

export default async function ISRPage() {
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 },
  }).then((res) => res.json());

  return <div>{JSON.stringify(data)}</div>;
}

// Static page with tags
export default async function TaggedPage() {
  const data = await fetch('https://api.example.com/data', {
    next: { tags: ['posts'] },
  }).then((res) => res.json());

  return <div>{JSON.stringify(data)}</div>;
}

// No caching (SSR equivalent)
export default async function DynamicPage() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'no-store',
  }).then((res) => res.json());

  return <div>{JSON.stringify(data)}</div>;
}

// Generate static params for dynamic routes
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then((res) =>
    res.json()
  );

  return posts.map((post: any) => ({
    id: post.id.toString(),
  }));
}

// Dynamic params with fallback
export const dynamicParams = true; // true | false | 'force-static'

// Segment config options
export const dynamic = 'auto'; // 'auto' | 'force-dynamic' | 'error' | 'force-static'
export const fetchCache = 'auto'; // 'auto' | 'default-cache' | 'only-cache' | 'force-cache' | 'force-no-store' | 'default-no-store' | 'only-no-store'
export const runtime = 'nodejs'; // 'nodejs' | 'edge'
export const preferredRegion = 'auto'; // 'auto' | 'global' | 'home' | string | string[]

// Incremental Static Regeneration with on-demand revalidation
// Trigger revalidation via API route:
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { path, tag } = await request.json();

  if (path) {
    revalidatePath(path);
  }

  if (tag) {
    revalidateTag(tag);
  }

  return NextResponse.json({ revalidated: true });
}

// Using generateMetadata for SEO
import { Metadata } from 'next';

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const post = await fetch(`https://api.example.com/posts/${params.id}`).then(
    (res) => res.json()
  );

  return {
    title: post.title,
    description: post.description,
    openGraph: {
      title: post.title,
      description: post.description,
      images: [post.image],
    },
  };
}
