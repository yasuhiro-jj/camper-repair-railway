import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development"
    ? "http://localhost:5002"
    : "https://web-development-8c2f.up.railway.app");

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


