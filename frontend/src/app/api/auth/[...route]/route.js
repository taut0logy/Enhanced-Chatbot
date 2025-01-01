import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request, { params }) {
  const route = params.route.join('/');
  const { searchParams } = new URL(request.url);
  const queryString = searchParams.toString();
  const url = `${BACKEND_URL}/api/auth/${route}${queryString ? `?${queryString}` : ''}`;

  try {
    const response = await fetch(url, {
      headers: {
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch from backend' },
      { status: 500 }
    );
  }
}

export async function POST(request, { params }) {
  const route = params.route.join('/');
  const url = `${BACKEND_URL}/api/auth/${route}`;
  
  try {
    const contentType = request.headers.get('content-type');
    let body;
    let headers = {
      ...Object.fromEntries(request.headers),
      'host': new URL(BACKEND_URL).host,
    };

    if (contentType?.includes('application/json')) {
      body = await request.json();
      headers['content-type'] = 'application/json';
    } else if (contentType?.includes('application/x-www-form-urlencoded')) {
      const formData = await request.formData();
      body = new URLSearchParams(formData);
      headers['content-type'] = 'application/x-www-form-urlencoded';
    } else {
      body = await request.text();
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: typeof body === 'string' ? body : JSON.stringify(body),
    });

    const data = await response.json();
    
    // Create the response with the data
    const nextResponse = NextResponse.json(data, { status: response.status });
    
    // If login was successful, set the cookie
    if (route === 'login' && response.ok && data.access_token) {
      nextResponse.cookies.set('token', data.access_token, {
        path: '/',
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax'
      });
    }
    
    return nextResponse;
  } catch (error) {
    return NextResponse.json(
      { error: 'Backend fetch error: ' + error.message },
      { status: 500 }
    );
  }
}

export async function PUT(request, { params }) {
  const route = params.route.join('/');
  const url = `${BACKEND_URL}/api/auth/${route}`;

  try {
    const body = await request.json();
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch from backend' },
      { status: 500 }
    );
  }
}

export async function DELETE(request, { params }) {
  const route = params.route.join('/');
  const url = `${BACKEND_URL}/api/auth/${route}`;

  try {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch from backend' },
      { status: 500 }
    );
  }
} 