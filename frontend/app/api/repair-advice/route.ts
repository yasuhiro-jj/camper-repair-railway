import { NextRequest, NextResponse } from "next/server";

// 本番環境では常にRailway URLを使用（環境変数なしで動作）
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://web-production-c8b78.up.railway.app";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const res = await fetch(`${API_URL}/api/repair_advice/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error("Repair advice search proxy error:", error);
    return NextResponse.json(
      { error: "修理アドバイス検索APIへの接続に失敗しました。" },
      { status: 500 },
    );
  }
}
















