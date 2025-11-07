/**
 * React Server Components examples (Next.js 13+ App Router)
 */

// 1. Basic Server Component (async component)
export default async function ServerComponent() {
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 }, // Revalidate every hour
  });
  const result = await data.json();

  return (
    <div>
      <h1>Server Component</h1>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
}

// 2. Server Component with multiple data fetches
async function getUser(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}`, {
    cache: 'force-cache', // Cache permanently
  });
  return res.json();
}

async function getUserPosts(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}/posts`, {
    cache: 'no-store', // Never cache
  });
  return res.json();
}

export async function UserProfile({ userId }: { userId: string }) {
  const [user, posts] = await Promise.all([
    getUser(userId),
    getUserPosts(userId),
  ]);

  return (
    <div>
      <h1>{user.name}</h1>
      <div>
        {posts.map((post: any) => (
          <article key={post.id}>{post.title}</article>
        ))}
      </div>
    </div>
  );
}

// 3. Server Component with streaming
export async function StreamingComponent() {
  // This will stream as data becomes available
  const data = await fetch('https://api.example.com/stream');

  return (
    <div>
      <h2>Streaming Data</h2>
      {/* Content will stream to client */}
    </div>
  );
}

// 4. Server Component with database query
// import { prisma } from '@/lib/prisma';

// export async function DatabaseComponent() {
//   const users = await prisma.user.findMany({
//     take: 10,
//     orderBy: { createdAt: 'desc' },
//   });

//   return (
//     <ul>
//       {users.map((user) => (
//         <li key={user.id}>{user.name}</li>
//       ))}
//     </ul>
//   );
// }

// 5. Mixing Server and Client Components
// app/page.tsx (Server Component)
import { Suspense } from 'react';

export function MixedComponentPage() {
  return (
    <div>
      <h1>Server Rendered</h1>
      <Suspense fallback={<p>Loading user data...</p>}>
        <UserData />
      </Suspense>
      {/* Client component for interactivity */}
      {/* <ClientCounter /> */}
    </div>
  );
}

async function UserData() {
  const data = await fetch('https://api.example.com/user');
  const user = await data.json();
  return <div>{user.name}</div>;
}

// 6. Server Component with search params
interface PageProps {
  searchParams: { [key: string]: string | string[] | undefined };
}

export async function SearchPage({ searchParams }: PageProps) {
  const query = searchParams.q as string;

  if (!query) {
    return <div>No search query provided</div>;
  }

  const results = await fetch(
    `https://api.example.com/search?q=${encodeURIComponent(query)}`
  );
  const data = await results.json();

  return (
    <div>
      <h1>Search Results for "{query}"</h1>
      <ul>
        {data.map((item: any) => (
          <li key={item.id}>{item.title}</li>
        ))}
      </ul>
    </div>
  );
}

// 7. Server Component with headers and cookies
import { headers, cookies } from 'next/headers';

export async function ServerWithHeaders() {
  const headersList = headers();
  const userAgent = headersList.get('user-agent');
  const cookieStore = cookies();
  const theme = cookieStore.get('theme');

  return (
    <div>
      <p>User Agent: {userAgent}</p>
      <p>Theme: {theme?.value}</p>
    </div>
  );
}
