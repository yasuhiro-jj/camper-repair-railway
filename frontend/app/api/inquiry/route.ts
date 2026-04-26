import { NextRequest, NextResponse } from 'next/server';

const RESEND_API_URL = 'https://api.resend.com/emails';
const INQUIRY_EMAIL = 'shop@rq-plus.com';
// 届かない場合のバックアップ用（Vercel環境変数 INQUIRY_BACKUP_EMAIL で指定、例: Gmail）

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

    const inquiryType = type === 'partner' ? '修理工場登録' : 'ユーザー';
    const timestamp = new Date().toISOString();
    
    console.log('問い合わせ受信:', {
      name,
      email,
      phone,
      region,
      issue,
      type,
      message,
      timestamp,
    });

    // 1. Resendでメール送信
    const resendApiKey = process.env.RESEND_API_KEY;
    const fromEmail = process.env.FROM_EMAIL || 'info@camper-repair.net';
    
    if (resendApiKey) {
      try {
        const contentLabel = type === 'user' ? '故障内容' : '事業内容';
        const emailSubject = `【${inquiryType}】LPからのお問い合わせ - ${name}様`;
        const emailBody = [
          'LPお問い合わせフォームから新しいお問い合わせがありました。',
          '',
          '【お客様情報】',
          `お名前: ${name}`,
          `メールアドレス: ${email}`,
          `電話番号: ${phone}`,
          `地域（都道府県）: ${region}`,
          '',
          `【${contentLabel}】`,
          issue,
          '',
          '【メッセージ（任意）】',
          message || 'なし',
          '',
          '---',
          `種別: ${inquiryType}`,
          `送信日時: ${new Date().toLocaleString('ja-JP')}`,
        ].join('\n');

        const resendRes = await fetch(RESEND_API_URL, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${resendApiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: `岡山キャンピングカー修理サポートセンター <${fromEmail}>`,
            to: [INQUIRY_EMAIL, process.env.INQUIRY_BACKUP_EMAIL].filter(Boolean),
            subject: emailSubject,
            text: emailBody,
            reply_to: email,
          }),
        });

        if (!resendRes.ok) {
          const errText = await resendRes.text();
          console.error('Resend送信エラー:', resendRes.status, errText);
        } else {
          console.log('✅ Resendメール送信成功:', INQUIRY_EMAIL);
        }
      } catch (err) {
        console.error('Resend送信エラー:', err);
      }
    } else {
      console.warn('⚠️ RESEND_API_KEYが未設定です。メール送信をスキップします。');
    }

    // 2. Notionに保存（商談DB: 0976749dbf3f47a58990cdd1b50c5437）
    const notionApiKey = process.env.NOTION_API_KEY;
    const notionDbId = process.env.NOTION_DEAL_DB_ID || '0976749dbf3f47a58990cdd1b50c5437';
    
    if (notionApiKey && notionDbId) {
      try {
        const dealId = `LP-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.random().toString(36).slice(2, 5)}`;
        
        const notionRes = await fetch('https://api.notion.com/v1/pages', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${notionApiKey}`,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28',
          },
          body: JSON.stringify({
            parent: { database_id: notionDbId.replace(/-/g, '') },
            properties: {
              '商談ID': {
                title: [{ text: { content: dealId } }],
              },
              '顧客名': {
                rich_text: [{ text: { content: name } }],
              },
              'メールアドレス': {
                email: email,
              },
              '電話番号': {
                phone_number: phone,
              },
              '所在地（都道府県）': {
                select: { name: region },
              },
              '症状カテゴリ': {
                select: { name: 'LPお問い合わせ' },
              },
              '症状詳細': {
                rich_text: [{ text: { content: `${issue}${message ? `\n\n【メッセージ】\n${message}` : ''}` } }],
              },
              '紹介修理店': {
                relation: [],
              },
            },
          }),
        });

        if (!notionRes.ok) {
          const errText = await notionRes.text();
          console.error('Notion保存エラー:', notionRes.status, errText);
        } else {
          console.log('✅ Notion保存成功:', dealId);
        }
      } catch (err) {
        console.error('Notion保存エラー:', err);
      }
    } else {
      console.warn('⚠️ NOTION_API_KEY または NOTION_DEAL_DB_ID が未設定です。Notion保存をスキップします。');
    }

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
