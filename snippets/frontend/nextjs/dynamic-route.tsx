/**
 * Next.js Dynamic Routes examples
 */

// app/posts/[id]/page.tsx
interface PageProps {
  params: { id: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export default async function PostPage({ params, searchParams }: PageProps) {
  const post = await getPost(params.id);

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
    </article>
  );
}

// Generate static params for SSG
export async function generateStaticParams() {
  const posts = await getPosts();

  return posts.map((post) => ({
    id: post.id,
  }));
}

// Generate metadata dynamically
import { Metadata } from 'next';

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const post = await getPost(params.id);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.image],
    },
  };
}

// Catch-all route: app/blog/[...slug]/page.tsx
interface CatchAllProps {
  params: { slug: string[] };
}

export default function CatchAllPage({ params }: CatchAllProps) {
  const path = params.slug.join('/');
  return <div>Path: {path}</div>;
}

// Optional catch-all: app/shop/[[...slug]]/page.tsx
export function OptionalCatchAllPage({ params }: CatchAllProps) {
  // This matches /shop, /shop/clothes, /shop/clothes/t-shirts, etc.
  const slug = params.slug || [];
  return <div>Segments: {slug.join(' > ')}</div>;
}

// Parallel routes with dynamic segments
// app/[category]/layout.tsx
export default function CategoryLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { category: string };
}) {
  return (
    <div>
      <nav>Category: {params.category}</nav>
      {children}
    </div>
  );
}

// Route groups with dynamic segments
// app/(shop)/products/[id]/page.tsx
export function ProductPage({ params }: { params: { id: string } }) {
  return <div>Product ID: {params.id}</div>;
}

// Helper functions
async function getPost(id: string) {
  // Fetch post from database
  return {
    id,
    title: 'Sample Post',
    content: 'Content here',
    excerpt: 'Excerpt here',
    image: '/image.jpg',
  };
}

async function getPosts() {
  // Fetch all posts
  return [
    { id: '1', title: 'Post 1' },
    { id: '2', title: 'Post 2' },
  ];
}
