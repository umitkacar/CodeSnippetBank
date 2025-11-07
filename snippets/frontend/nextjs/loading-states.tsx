/**
 * Next.js Loading States examples
 */

// loading.tsx - Automatic loading UI
export default function Loading() {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p>Loading...</p>
    </div>
  );
}

// Skeleton loader
export function SkeletonLoader() {
  return (
    <div className="space-y-4">
      <div className="h-8 bg-gray-200 rounded animate-pulse" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
    </div>
  );
}

// Loading with Suspense
import { Suspense } from 'react';

export function PageWithSuspense() {
  return (
    <div>
      <h1>My Page</h1>
      <Suspense fallback={<Loading />}>
        <DataComponent />
      </Suspense>
    </div>
  );
}

async function DataComponent() {
  const data = await fetchData();
  return <div>{JSON.stringify(data)}</div>;
}

// Multiple Suspense boundaries
export function MultipleSuspenseBoundaries() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <Header />
      </Suspense>

      <div className="grid grid-cols-2 gap-4">
        <Suspense fallback={<SidebarSkeleton />}>
          <Sidebar />
        </Suspense>

        <Suspense fallback={<ContentSkeleton />}>
          <MainContent />
        </Suspense>
      </div>
    </div>
  );
}

// Streaming with loading
export function StreamingExample() {
  return (
    <Suspense fallback={<p>Loading posts...</p>}>
      <Posts />
    </Suspense>
  );
}

async function Posts() {
  const posts = await getPosts();
  return (
    <ul>
      {posts.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}

// Error boundary with loading
import { ErrorBoundary } from 'react-error-boundary';

export function WithErrorBoundary() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <Suspense fallback={<Loading />}>
        <DataComponent />
      </Suspense>
    </ErrorBoundary>
  );
}

function ErrorFallback() {
  return <div>Something went wrong</div>;
}

// Skeleton components
function HeaderSkeleton() {
  return <div className="h-16 bg-gray-200 animate-pulse" />;
}

function SidebarSkeleton() {
  return <div className="h-screen bg-gray-200 animate-pulse" />;
}

function ContentSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-24 bg-gray-200 rounded animate-pulse" />
      ))}
    </div>
  );
}

// Helper functions
async function fetchData() {
  return { data: 'example' };
}

async function getPosts() {
  return [
    { id: 1, title: 'Post 1' },
    { id: 2, title: 'Post 2' },
  ];
}

async function Header() {
  return <header>Header</header>;
}

async function Sidebar() {
  return <aside>Sidebar</aside>;
}

async function MainContent() {
  return <main>Content</main>;
}
