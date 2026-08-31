/**
 * データベース再構築API - バックエンドへのプロキシ
 */

import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : process.env.NEXT_PUBLIC_API_URL || 'https://web-production-c8b78.up.railway.app';
const BACKEND_ADMIN_CODE = process.env.ADMIN_CODE || '';

export async function POST() {
  try {
    const res = await fetch(`${BACKEND_URL}/reload_data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(BACKEND_ADMIN_CODE ? { 'X-Admin-Code': BACKEND_ADMIN_CODE } : {}),
      },
      body: JSON.stringify({}),
      signal: AbortSignal.timeout(120000), // 2分（再構築は時間がかかる場合あり）
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { success: false, error: data?.error || 'データベースの再構築に失敗しました' },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: unknown) {
    console.error('[Admin API] reload-database error:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'エラーが発生しました',
      },
      { status: 500 }
    );
  }
}
