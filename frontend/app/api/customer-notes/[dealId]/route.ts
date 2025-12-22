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
    
    const backendUrl = `${BACKEND_URL}/api/v1/deals/${dealId}/customer-notes`;
    console.log('[customer-notes proxy] Sending to:', backendUrl);
    console.log('[customer-notes proxy] Body:', body);

    const res = await fetch(backendUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    console.log('[customer-notes proxy] Response status:', res.status);
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('[customer-notes proxy] Backend error:', errorText);
      return NextResponse.json(
        { success: false, error: `バックエンドエラー: ${res.status}` },
        { status: res.status },
      );
    }

    const data = await res.json();
    console.log('[customer-notes proxy] Success:', data);
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error('[customer-notes proxy] Exception:', error);
    return NextResponse.json(
      { success: false, error: `接続エラー: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 },
    );
  }
}

