/**
 * Next.js Error Handling examples
 */
'use client';

import { useEffect } from 'react';

// error.tsx - Error boundary
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}

// global-error.tsx - Root error boundary
export function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  );
}

// not-found.tsx
export function NotFound() {
  return (
    <div>
      <h2>404 - Page Not Found</h2>
      <p>Could not find requested resource</p>
      <a href="/">Return Home</a>
    </div>
  );
}

// Custom 404 with notFound()
import { notFound } from 'next/navigation';

export async function PageWithNotFound({ params }: { params: { id: string } }) {
  const data = await getData(params.id);

  if (!data) {
    notFound();
  }

  return <div>{data.title}</div>;
}

async function getData(id: string) {
  // Return null if not found
  return null;
}
