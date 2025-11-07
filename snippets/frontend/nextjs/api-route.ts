/**
 * Next.js API Routes (App Router)
 */
import { NextRequest, NextResponse } from 'next/server';

// Basic GET route
export async function GET(request: NextRequest) {
  return NextResponse.json({ message: 'Hello from API' });
}

// POST route with body
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate body
    if (!body.name || !body.email) {
      return NextResponse.json(
        { error: 'Name and email are required' },
        { status: 400 }
      );
    }

    // Process data
    // await db.user.create({ data: body });

    return NextResponse.json({ success: true }, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request body' },
      { status: 400 }
    );
  }
}

// PUT route
export async function PUT(request: NextRequest) {
  const body = await request.json();

  // Update resource
  // await db.user.update({ where: { id: body.id }, data: body });

  return NextResponse.json({ success: true });
}

// DELETE route
export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return NextResponse.json({ error: 'ID required' }, { status: 400 });
  }

  // Delete resource
  // await db.user.delete({ where: { id } });

  return NextResponse.json({ success: true });
}

// Route with headers and cookies
export async function GETWithHeadersAndCookies(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const userAgent = request.headers.get('user-agent');

  const response = NextResponse.json({ data: 'protected' });

  // Set cookie
  response.cookies.set('visited', 'true', {
    maxAge: 60 * 60 * 24,
    httpOnly: true,
  });

  // Set header
  response.headers.set('x-custom-header', 'value');

  return response;
}

// Route with query parameters
export async function GETWithParams(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get('page') || '1');
  const limit = parseInt(searchParams.get('limit') || '10');

  // Fetch paginated data
  // const data = await db.posts.findMany({
  //   skip: (page - 1) * limit,
  //   take: limit,
  // });

  return NextResponse.json({
    data: [],
    page,
    limit,
  });
}

// Error handling
export async function GETWithErrorHandling(request: NextRequest) {
  try {
    // Simulate async operation
    // const data = await fetchData();

    return NextResponse.json({ data: [] });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// CORS configuration
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

// Streaming response
export async function GETStream(request: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(encoder.encode(`data: ${i}\n\n`));
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      controller.close();
    },
  });

  return new NextResponse(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}
