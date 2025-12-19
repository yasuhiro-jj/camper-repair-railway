import { NextRequest, NextResponse } from 'next/server';

// 本番環境ではRailway、開発ではenv/localhostを使用
const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : 'https://web-development-8c2f.up.railway.app';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/deals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error('[deals proxy] error:', error);
    return NextResponse.json(
      { success: false, error: '商談作成APIへの接続に失敗しました。' },
      { status: 500 },
    );
  }
}


