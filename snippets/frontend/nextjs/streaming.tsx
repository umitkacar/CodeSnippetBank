/**
 * Next.js Streaming examples
 */
import { Suspense } from 'react';

// Basic streaming component
export default async function StreamingPage() {
  return (
    <div>
      <Header />
      <Suspense fallback={<Skeleton />}>
        <SlowComponent />
      </Suspense>
    </div>
  );
}

// Multiple streaming sections
export async function MultiStreamingPage() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <AsyncHeader />
      </Suspense>

      <div className="grid grid-cols-2">
        <Suspense fallback={<SidebarSkeleton />}>
          <AsyncSidebar />
        </Suspense>

        <Suspense fallback={<ContentSkeleton />}>
          <AsyncContent />
        </Suspense>
      </div>
    </div>
  );
}

// Streaming with React Server Components
async function AsyncHeader() {
  const data = await fetchHeaderData();
  return <header>{data.title}</header>;
}

async function AsyncSidebar() {
  const nav = await fetchNavigation();
  return (
    <aside>
      <ul>
        {nav.map((item: any) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </aside>
  );
}

async function AsyncContent() {
  const posts = await fetchPosts();
  return (
    <main>
      {posts.map((post: any) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </main>
  );
}

// Streaming API route
export async function StreamingAPIRoute() {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        const data = await fetchData(i);
        controller.enqueue(encoder.encode(JSON.stringify(data) + '\n'));
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain',
      'Transfer-Encoding': 'chunked',
    },
  });
}

// Helper components
function Header() {
  return <header>Fast Header</header>;
}

function Skeleton() {
  return <div className="animate-pulse bg-gray-200 h-32" />;
}

function HeaderSkeleton() {
  return <div className="animate-pulse bg-gray-200 h-16" />;
}

function SidebarSkeleton() {
  return <div className="animate-pulse bg-gray-200 h-screen" />;
}

function ContentSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="animate-pulse bg-gray-200 h-48" />
      ))}
    </div>
  );
}

async function SlowComponent() {
  await new Promise((resolve) => setTimeout(resolve, 3000));
  return <div>Slow component loaded!</div>;
}

// Helper functions
async function fetchHeaderData() {
  return { title: 'My Site' };
}

async function fetchNavigation() {
  return [
    { id: 1, name: 'Home' },
    { id: 2, name: 'About' },
  ];
}

async function fetchPosts() {
  return [
    { id: 1, title: 'Post 1', excerpt: 'Excerpt 1' },
    { id: 2, title: 'Post 2', excerpt: 'Excerpt 2' },
  ];
}

async function fetchData(index: number) {
  return { index, data: `Data ${index}` };
}
