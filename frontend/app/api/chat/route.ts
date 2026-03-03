import { NextRequest, NextResponse } from "next/server";

// 本番環境では常にRailway URLを使用（環境変数なしで動作）
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://web-production-c8b78.up.railway.app";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    console.log("[Chat API] Request to:", `${API_URL}/api/unified/chat`);
    console.log("[Chat API] API_URL:", API_URL);

    const res = await fetch(`${API_URL}/api/unified/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(60000), // 60秒タイムアウト
    });

    if (!res.ok) {
      console.error("[Chat API] Backend error:", res.status, res.statusText);
      const errorText = await res.text();
      console.error("[Chat API] Error response:", errorText);
      return NextResponse.json(
        { error: `バックエンドエラー: ${res.status} ${res.statusText}` },
        { status: res.status },
      );
    }

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    console.error("[Chat API] Error:", error);
    console.error("[Chat API] Error details:", {
      message: error.message,
      name: error.name,
      stack: error.stack,
    });
    return NextResponse.json(
      { 
        error: "チャットAPIへの接続に失敗しました。",
        details: process.env.NODE_ENV === 'development' ? error.message : undefined
      },
      { status: 500 },
    );
  }
}


