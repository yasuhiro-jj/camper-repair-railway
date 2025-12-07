import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // バリデーション
    const { name, email, phone, region, issue, type, message } = body;
    
    if (!name || !email || !phone || !region || !issue) {
      return NextResponse.json(
        { error: '必須項目が不足しています' },
        { status: 400 }
      );
    }

    // TODO: ここでNotionやSendGridに送信する処理を実装
    // 現在はモック実装として、ログに出力
    console.log('問い合わせ受信:', {
      name,
      email,
      phone,
      region,
      issue,
      type,
      message,
      timestamp: new Date().toISOString(),
    });

    // 実際の実装例（Notion API使用の場合）
    // const notionResponse = await fetch('https://api.notion.com/v1/pages', {
    //   method: 'POST',
    //   headers: {
    //     'Authorization': `Bearer ${process.env.NOTION_API_KEY}`,
    //     'Content-Type': 'application/json',
    //     'Notion-Version': '2022-06-28',
    //   },
    //   body: JSON.stringify({
    //     parent: { database_id: process.env.NOTION_DATABASE_ID },
    //     properties: {
    //       Name: { title: [{ text: { content: name } }] },
    //       Email: { email: email },
    //       Phone: { phone_number: phone },
    //       Region: { rich_text: [{ text: { content: region } }] },
    //       Issue: { rich_text: [{ text: { content: issue } }] },
    //       Type: { select: { name: type } },
    //       Message: { rich_text: [{ text: { content: message || '' } }] },
    //     },
    //   }),
    // });

    // SendGrid使用の場合の例
    // const sgMail = require('@sendgrid/mail');
    // sgMail.setApiKey(process.env.SENDGRID_API_KEY);
    // const msg = {
    //   to: 'info@example.com',
    //   from: 'noreply@example.com',
    //   subject: `【${type === 'user' ? 'ユーザー' : '修理工場登録'}】問い合わせ`,
    //   text: `
    //     名前: ${name}
    //     メール: ${email}
    //     電話: ${phone}
    //     地域: ${region}
    //     内容: ${issue}
    //     メッセージ: ${message || 'なし'}
    //   `,
    // };
    // await sgMail.send(msg);

    return NextResponse.json(
      { 
        success: true,
        message: '問い合わせを受け付けました。担当者より3営業日以内にご連絡いたします。'
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('問い合わせ送信エラー:', error);
    return NextResponse.json(
      { error: '問い合わせの送信に失敗しました。もう一度お試しください。' },
      { status: 500 }
    );
  }
}

