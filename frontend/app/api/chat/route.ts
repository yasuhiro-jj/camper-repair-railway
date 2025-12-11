import { NextRequest, NextResponse } from "next/server";

// デフォルトはRailwayのURL（Vercel本番環境用）
// 開発環境では環境変数 NEXT_PUBLIC_API_URL=http://localhost:5002 を設定
const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://web-development-8c2f.up.railway.app";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const res = await fetch(`${API_URL}/api/unified/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error("Chat proxy error:", error);
    return NextResponse.json(
      { error: "チャットAPIへの接続に失敗しました。" },
      { status: 500 },
    );
  }
}


