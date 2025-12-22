import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : 'https://web-development-8c2f.up.railway.app';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/cost-estimation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error('[cost-estimation proxy] error:', error);
    return NextResponse.json(
      { success: false, error: '工賃推定APIへの接続に失敗しました。' },
      { status: 500 },
    );
  }
}





