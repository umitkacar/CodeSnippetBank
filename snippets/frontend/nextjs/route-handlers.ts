/**
 * Next.js Route Handlers (Advanced)
 */
import { NextRequest, NextResponse } from 'next/server';
import { headers, cookies } from 'next/headers';

// Dynamic route handler: app/api/posts/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const id = params.id;

  return NextResponse.json({ id, title: 'Post title' });
}

// Route handler with request body
export async function POST(request: NextRequest) {
  const body = await request.json();
  return NextResponse.json({ success: true, data: body });
}

// Route handler with form data
export async function POSTFormData(request: NextRequest) {
  const formData = await request.formData();
  const name = formData.get('name');
  const file = formData.get('file') as File;

  return NextResponse.json({ name, fileSize: file.size });
}

// Route handler with cookies
export async function GETWithCookies(request: NextRequest) {
  const cookieStore = cookies();
  const theme = cookieStore.get('theme');

  const response = NextResponse.json({ theme: theme?.value });
  response.cookies.set('visited', 'true', {
    maxAge: 60 * 60 * 24,
  });

  return response;
}

// Route handler with headers
export async function GETWithHeaders(request: NextRequest) {
  const headersList = headers();
  const authorization = headersList.get('authorization');

  if (!authorization) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  return NextResponse.json({ data: 'protected' });
}

// Redirect route handler
export async function GETRedirect(request: NextRequest) {
  return NextResponse.redirect(new URL('/new-path', request.url));
}

// Rewrite route handler
export async function GETRewrite(request: NextRequest) {
  return NextResponse.rewrite(new URL('/api/new-endpoint', request.url));
}

// Route handler with edge runtime
export const runtime = 'edge';

export async function EdgeHandler(request: NextRequest) {
  return NextResponse.json({ message: 'Running on edge' });
}

// Rate-limited route handler
const rateLimitMap = new Map<string, { count: number; reset: number }>();

export async function RateLimitedHandler(request: NextRequest) {
  const ip = request.ip || 'unknown';
  const now = Date.now();
  const limit = 10;
  const window = 60000; // 1 minute

  const record = rateLimitMap.get(ip);

  if (!record || now > record.reset) {
    rateLimitMap.set(ip, { count: 1, reset: now + window });
    return NextResponse.json({ success: true });
  }

  if (record.count >= limit) {
    return NextResponse.json(
      { error: 'Too many requests' },
      { status: 429 }
    );
  }

  record.count++;
  return NextResponse.json({ success: true });
}

// WebSocket upgrade handler
export async function WebSocketHandler(request: NextRequest) {
  const upgradeHeader = request.headers.get('upgrade');

  if (upgradeHeader !== 'websocket') {
    return new NextResponse('Expected websocket', { status: 426 });
  }

  // Handle WebSocket connection
  return new NextResponse(null, { status: 101 });
}

// File download handler
export async function DownloadHandler(request: NextRequest) {
  const file = await fetch('https://example.com/file.pdf');
  const blob = await file.blob();

  return new NextResponse(blob, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="file.pdf"',
    },
  });
}

// Image generation handler
export async function ImageHandler(request: NextRequest) {
  // Generate or fetch image
  const imageBuffer = Buffer.from('image data');

  return new NextResponse(imageBuffer, {
    headers: {
      'Content-Type': 'image/png',
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  });
}

// Webhook handler with signature verification
export async function WebhookHandler(request: NextRequest) {
  const signature = request.headers.get('x-signature');
  const body = await request.text();

  // Verify signature
  // const isValid = verifySignature(body, signature);

  // if (!isValid) {
  //   return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
  // }

  return NextResponse.json({ received: true });
}
