/**
 * Next.js Middleware examples
 */
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Basic middleware
export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Add custom header
  response.headers.set('x-custom-header', 'my-value');

  return response;
}

// Middleware with authentication
export function authMiddleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

// Middleware with geolocation
export function geoMiddleware(request: NextRequest) {
  const country = request.geo?.country || 'US';
  const response = NextResponse.next();

  response.cookies.set('user-country', country);

  return response;
}

// A/B testing middleware
export function abTestMiddleware(request: NextRequest) {
  const bucket = request.cookies.get('bucket')?.value;

  if (!bucket) {
    const newBucket = Math.random() > 0.5 ? 'A' : 'B';
    const response = NextResponse.next();
    response.cookies.set('bucket', newBucket);
    return response;
  }

  return NextResponse.next();
}

// Rate limiting middleware
const rateLimit = new Map<string, { count: number; resetTime: number }>();

export function rateLimitMiddleware(request: NextRequest) {
  const ip = request.ip || 'anonymous';
  const now = Date.now();
  const limit = 100; // requests
  const window = 60 * 1000; // 1 minute

  const record = rateLimit.get(ip);

  if (!record || now > record.resetTime) {
    rateLimit.set(ip, { count: 1, resetTime: now + window });
    return NextResponse.next();
  }

  if (record.count >= limit) {
    return new NextResponse('Too Many Requests', { status: 429 });
  }

  record.count++;
  return NextResponse.next();
}

// Rewrite middleware
export function rewriteMiddleware(request: NextRequest) {
  // Rewrite old URLs to new ones
  if (request.nextUrl.pathname.startsWith('/old-path')) {
    return NextResponse.rewrite(new URL('/new-path', request.url));
  }

  return NextResponse.next();
}

// Locale detection middleware
export function localeMiddleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const pathnameIsMissingLocale = ['en', 'es', 'fr'].every(
    (locale) => !pathname.startsWith(`/${locale}/`) && pathname !== `/${locale}`
  );

  if (pathnameIsMissingLocale) {
    const locale = request.cookies.get('NEXT_LOCALE')?.value || 'en';
    return NextResponse.redirect(new URL(`/${locale}${pathname}`, request.url));
  }

  return NextResponse.next();
}

// Bot detection middleware
export function botMiddleware(request: NextRequest) {
  const userAgent = request.headers.get('user-agent') || '';
  const isBot = /bot|crawler|spider/i.test(userAgent);

  if (isBot) {
    const response = NextResponse.next();
    response.headers.set('x-is-bot', 'true');
    return response;
  }

  return NextResponse.next();
}

// Matcher configuration
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
};
