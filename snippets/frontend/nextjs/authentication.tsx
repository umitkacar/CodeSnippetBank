/**
 * Next.js Authentication patterns
 */
'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { SignJWT, jwtVerify } from 'jose';

const secretKey = process.env.SESSION_SECRET || 'secret';
const key = new TextEncoder().encode(secretKey);

// Session management
export async function createSession(userId: string) {
  const session = await new SignJWT({ userId })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(key);

  cookies().set('session', session, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  });
}

export async function getSession() {
  const session = cookies().get('session')?.value;
  if (!session) return null;

  try {
    const { payload } = await jwtVerify(session, key);
    return payload;
  } catch (error) {
    return null;
  }
}

export async function destroySession() {
  cookies().delete('session');
}

// Login action
export async function login(formData: FormData) {
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  // Validate credentials
  // const user = await db.user.findUnique({ where: { email } });
  // if (!user || !await bcrypt.compare(password, user.password)) {
  //   return { error: 'Invalid credentials' };
  // }

  // Create session
  await createSession('user-id');
  redirect('/dashboard');
}

// Logout action
export async function logout() {
  await destroySession();
  redirect('/login');
}

// Protected page component
export async function ProtectedPage() {
  const session = await getSession();

  if (!session) {
    redirect('/login');
  }

  return <div>Protected content</div>;
}

// Middleware auth check
import { NextRequest, NextResponse } from 'next/server';

export function authMiddleware(request: NextRequest) {
  const session = request.cookies.get('session');

  if (!session && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

// Auth context provider
'use client';

import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  user: any;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check auth status
    fetch('/api/auth/me')
      .then((res) => res.json())
      .then((data) => setUser(data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// OAuth integration example
export async function signInWithGoogle() {
  const redirectUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${process.env.GOOGLE_CLIENT_ID}&redirect_uri=${process.env.GOOGLE_REDIRECT_URI}&response_type=code&scope=email profile`;
  redirect(redirectUrl);
}

// API route for OAuth callback
export async function OAuthCallback(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code');

  if (!code) {
    return NextResponse.json({ error: 'No code provided' }, { status: 400 });
  }

  // Exchange code for token
  // const token = await exchangeCodeForToken(code);
  // const user = await getUserFromToken(token);

  // Create session
  // await createSession(user.id);

  return NextResponse.redirect(new URL('/dashboard', request.url));
}
