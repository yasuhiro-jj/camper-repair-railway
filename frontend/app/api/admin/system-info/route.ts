/**
 * システム情報API - バックエンドへのプロキシ
 */

import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : process.env.NEXT_PUBLIC_API_URL || 'https://web-production-c8b78.up.railway.app';

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/admin/system-info`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(10000),
      cache: 'no-store',
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      return NextResponse.json(
        { error: data?.error || 'システム情報の取得に失敗しました' },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[Admin API] system-info error:', error);
    return NextResponse.json(
      { error: error.message || 'システム情報の取得に失敗しました' },
      { status: 500 }
    );
  }
}
