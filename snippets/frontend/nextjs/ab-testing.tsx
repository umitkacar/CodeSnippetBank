/**
 * Next.js A/B Testing Implementation
 */
'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';

export function useABTest(testName: string) {
  const [variant, setVariant] = useState<'A' | 'B'>('A');

  useEffect(() => {
    const stored = localStorage.getItem(`ab_test_${testName}`);

    if (stored) {
      setVariant(stored as 'A' | 'B');
    } else {
      const newVariant = Math.random() > 0.5 ? 'A' : 'B';
      localStorage.setItem(`ab_test_${testName}`, newVariant);
      setVariant(newVariant);
    }
  }, [testName]);

  return variant;
}

// Usage
export function ABTestComponent() {
  const variant = useABTest('homepage_cta');

  return (
    <div>
      {variant === 'A' ? (
        <button className="bg-blue-500">Buy Now</button>
      ) : (
        <button className="bg-green-500">Get Started</button>
      )}
    </div>
  );
}

// Server-side A/B testing with middleware
import { NextRequest, NextResponse } from 'next/server';

export function abTestMiddleware(request: NextRequest) {
  let variant = request.cookies.get('ab_variant')?.value;

  if (!variant) {
    variant = Math.random() > 0.5 ? 'A' : 'B';
    const response = NextResponse.next();
    response.cookies.set('ab_variant', variant);
    return response;
  }

  return NextResponse.next();
}
