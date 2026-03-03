/**
 * ビルダー一覧API - バックエンドへのプロキシ
 * Notion API経由のため応答が遅くなる場合がある
 */

import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const maxDuration = 60; // Vercel Pro: 最大60秒まで延長可能

const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : process.env.NEXT_PUBLIC_API_URL || 'https://web-production-c8b78.up.railway.app';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const params = new URLSearchParams();
    if (searchParams.get('limit')) params.append('limit', searchParams.get('limit')!);
    if (searchParams.get('status')) params.append('status', searchParams.get('status')!);
    if (searchParams.get('prefecture')) params.append('prefecture', searchParams.get('prefecture')!);

    const url = `${BACKEND_URL}/api/v1/builders${params.toString() ? '?' + params.toString() : ''}`;

    const res = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(45000), // 45秒（Vercel→Railway→Notion往復で時間がかかる場合あり）
      cache: 'no-store',
    });

    const data = await res.json();

    if (!res.ok) {
      // 503（Builder Manager未利用時）は空リストで正常応答（UX改善）
      if (res.status === 503) {
        return NextResponse.json({ builders: [], count: 0 });
      }
      return NextResponse.json(
        { error: data?.error || 'ビルダー一覧の取得に失敗しました', builders: [] },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[Admin API] builders error:', error);
    return NextResponse.json(
      {
        error: error.message || 'ビルダー一覧の取得に失敗しました',
        builders: [],
        count: 0,
      },
      { status: 500 }
    );
  }
}
