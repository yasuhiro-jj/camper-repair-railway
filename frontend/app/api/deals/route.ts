import { NextRequest, NextResponse } from 'next/server';

// 本番環境ではRailway、開発ではenv/localhostを使用
const BACKEND_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : process.env.NEXT_PUBLIC_API_URL || 'https://web-production-c8b78.up.railway.app';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log('[deals proxy] リクエスト受信:', {
      backend_url: BACKEND_URL,
      partner_page_id: body.partner_page_id,
      customer_name: body.customer_name,
      notification_method: body.notification_method,
    });
    
    const res = await fetch(`${BACKEND_URL}/api/v1/deals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    console.log('[deals proxy] バックエンドレスポンス:', {
      status: res.status,
      statusText: res.statusText,
    });
    
    const data = await res.json();
    console.log('[deals proxy] レスポンスデータ:', {
      success: data.success,
      deal_id: data.deal?.deal_id,
      error: data.error,
    });
    
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    console.error('[deals proxy] error:', error);
    console.error('[deals proxy] error details:', {
      message: error.message,
      stack: error.stack,
    });
    return NextResponse.json(
      { success: false, error: '商談作成APIへの接続に失敗しました。' },
      { status: 500 },
    );
  }
}













