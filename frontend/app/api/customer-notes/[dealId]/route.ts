import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : 'https://web-development-8c2f.up.railway.app';

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ dealId: string }> },
) {
  try {
    const { dealId } = await params;
    const body = await req.json();

    const res = await fetch(
      `${BACKEND_URL}/v1/deals/${dealId}/customer-notes`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      },
    );

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error('[customer-notes proxy] error:', error);
    return NextResponse.json(
      { success: false, error: 'メッセージ送信APIへの接続に失敗しました。' },
      { status: 500 },
    );
  }
}

