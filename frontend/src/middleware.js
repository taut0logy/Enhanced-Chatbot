import { NextResponse } from 'next/server';

const publicPaths = ['/login', '/signup', '/verify-email', '/forgot-password', '/reset-password'];

function isTokenExpired(token) {
  try {
    const [, payload] = token.split('.');
    const decodedPayload = JSON.parse(atob(payload));
    const expirationTime = decodedPayload.exp * 1000;
    return Date.now() >= expirationTime;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true;
  }
}

export function middleware(request) {
  const token = request.cookies.get('token');
  const { pathname } = request.nextUrl;

  if (publicPaths.some(path => pathname.startsWith(path))) {
    if (token?.value && !isTokenExpired(token.value)) {
      return NextResponse.redirect(new URL('/', request.url));
    }
    return NextResponse.next();
  }

  // For protected routes
  if (!token?.value || isTokenExpired(token.value)) {
    // Clear the invalid/expired token
    const response = NextResponse.redirect(new URL('/login', request.url));
    response.cookies.delete('token');
    return response;
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes
     * - static files (/_next, /images, /favicon.ico, etc.)
     * - other public assets
     */
    '/((?!api|_next/static|_next/image|images|favicon.ico|manifest.json|robots.txt|sitemap.xml).*)',
  ],
}; 