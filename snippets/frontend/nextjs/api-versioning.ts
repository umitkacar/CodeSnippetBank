/**
 * Next.js API Versioning
 */
import { NextRequest, NextResponse } from 'next/server';

// Version 1 API
// app/api/v1/users/route.ts
export async function GET() {
  return NextResponse.json({ version: 1, users: [] });
}

// Version 2 API
// app/api/v2/users/route.ts
export async function GETv2() {
  return NextResponse.json({ version: 2, data: { users: [] } });
}

// Version negotiation middleware
export function apiVersionMiddleware(request: NextRequest) {
  const version = request.headers.get('API-Version') || '1';
  const response = NextResponse.next();
  response.headers.set('API-Version', version);
  return response;
}

// Backward compatibility helper
export function supportsFeature(version: string, feature: string): boolean {
  const features: Record<string, string[]> = {
    '1': ['users', 'posts'],
    '2': ['users', 'posts', 'comments', 'reactions'],
  };

  return features[version]?.includes(feature) || false;
}
