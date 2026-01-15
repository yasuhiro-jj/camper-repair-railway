/**
 * パートナーショップAPI - Next.js APIルート
 * バックエンドへのプロキシとしてCORS問題を回避
 */

import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : process.env.NEXT_PUBLIC_API_URL || 'https://web-production-c8b78.up.railway.app';

export async function GET(request: NextRequest) {
  try {
    // クエリパラメータを取得
    const searchParams = request.nextUrl.searchParams;
    const status = searchParams.get('status');
    const prefecture = searchParams.get('prefecture');
    const specialty = searchParams.get('specialty');

    // バックエンドURLを構築
    const backendUrl = new URL('/api/v1/partner-shops', BACKEND_URL);
    if (status) backendUrl.searchParams.append('status', status);
    if (prefecture) backendUrl.searchParams.append('prefecture', prefecture);
    if (specialty) backendUrl.searchParams.append('specialty', specialty);

    console.log('[Partner Shops API] Fetching from:', backendUrl.toString());

    // バックエンドにリクエストを送信
    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(60000),
      cache: 'no-store',
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      console.error('[Partner Shops API] Backend error:', response.status, response.statusText);
      return NextResponse.json(
        { error: 'Backend error', status: response.status },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('[Partner Shops API] Success, shops count:', data.shops?.length || 0);

    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error: any) {
    console.error('[Partner Shops API] Error:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch partner shops',
        message: error.message,
        shops: [],
        count: 0,
      },
      { status: 500 }
    );
  }
}















