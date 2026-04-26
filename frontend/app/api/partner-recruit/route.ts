import { NextRequest, NextResponse } from 'next/server';

const RESEND_API_URL = 'https://api.resend.com/emails';
const PARTNER_RECRUIT_EMAIL = 'shop@rq-plus.com';
// 届かない場合のバックアップ用（Vercel環境変数 PARTNER_BACKUP_EMAIL で指定、例: Gmail）

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // バリデーション
    const { name, company_name, phone, email, area, skills, equipment, experience } = body;
    
    if (!name || !company_name || !phone || !email || !area || !skills) {
      return NextResponse.json(
        { error: '必須項目が不足しています' },
        { status: 400 }
      );
    }

    const fromEmail = process.env.FROM_EMAIL || 'info@camper-repair.net';

    // メール本文を作成
    const emailSubject = `【パートナー登録】${company_name}様からのお申し込み`;
    const emailBody = `
パートナー登録フォームから新しいお申し込みがありました。

【申込者情報】
お名前: ${name}
会社名: ${company_name}
電話番号: ${phone}
メールアドレス: ${email}
対応エリア: ${area}

【できる作業】
${skills}

【設備・経験の有無】
${equipment || '記載なし'}

【その他の経験】
${experience || '記載なし'}

---
送信日時: ${new Date().toLocaleString('ja-JP')}
`.trim();

    // 1. Resendでメール送信
    const resendApiKey = process.env.RESEND_API_KEY;
    if (resendApiKey) {
      try {
        const resendRes = await fetch(RESEND_API_URL, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${resendApiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: `岡山キャンピングカー修理サポートセンター <${fromEmail}>`,
            to: [PARTNER_RECRUIT_EMAIL, process.env.PARTNER_BACKUP_EMAIL].filter(Boolean),
            subject: emailSubject,
            text: emailBody,
            reply_to: email,
          }),
        });

        if (!resendRes.ok) {
          const errText = await resendRes.text();
          console.error('Resend送信エラー:', resendRes.status, errText);
        } else {
          console.log('✅ Resendメール送信成功（パートナー登録）:', PARTNER_RECRUIT_EMAIL);
        }
      } catch (error) {
        console.error('Resend送信エラー:', error);
      }
    } else {
      console.warn('⚠️ RESEND_API_KEYが未設定です。メール送信をスキップします。');
    }

    // ログに記録
    console.log('パートナー登録受信:', {
      name,
      company_name,
      phone,
      email,
      area,
      skills,
      equipment,
      experience,
      timestamp: new Date().toISOString(),
    });

    // 2. NotionパートナーDBに保存（51ac4a26485544e89a4f6d5e28919bc7）
    const notionApiKey = process.env.NOTION_API_KEY;
    const notionDbId = (process.env.NOTION_PARTNER_DB_ID || '51ac4a26485544e89a4f6d5e28919bc7').replace(/-/g, '');
    
    if (notionApiKey && notionDbId) {
      try {
        const shopId = `LP申込-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.random().toString(36).slice(2, 5)}`;
        const detailText = `【担当者】${name}\n【できる作業】${skills}\n【設備・経験】${equipment || '記載なし'}\n【その他】${experience || '記載なし'}`;

        const notionRes = await fetch('https://api.notion.com/v1/pages', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${notionApiKey}`,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28',
          },
          body: JSON.stringify({
            parent: { database_id: notionDbId },
            properties: {
              '店舗ID': {
                title: [{ text: { content: shopId } }],
              },
              '店舗名': {
                rich_text: [{ text: { content: company_name } }],
              },
              '電話番号': {
                phone_number: phone,
              },
              'メールアドレス': {
                email: email,
              },
              '所在地（都道府県）': {
                select: { name: area },
              },
              '備考': {
                rich_text: [{ text: { content: detailText } }],
              },
            },
          }),
        });

        if (!notionRes.ok) {
          const errText = await notionRes.text();
          console.error('Notion保存エラー:', notionRes.status, errText);
        } else {
          console.log('✅ NotionパートナーDB保存成功:', shopId);
        }
      } catch (error) {
        console.error('Notion保存エラー:', error);
      }
    } else {
      console.warn('⚠️ NOTION_API_KEY または NOTION_PARTNER_DB_ID が未設定です。Notion保存をスキップします。');
    }

    return NextResponse.json(
      { 
        success: true,
        message: 'お申し込みを受け付けました。担当者より3営業日以内にご連絡いたします。'
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('パートナー登録送信エラー:', error);
    return NextResponse.json(
      { error: 'お申し込みの送信に失敗しました。もう一度お試しください。' },
      { status: 500 }
    );
  }
}
