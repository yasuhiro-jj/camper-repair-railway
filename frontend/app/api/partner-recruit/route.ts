import { NextRequest, NextResponse } from 'next/server';

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

    // メール送信先（環境変数から取得、デフォルト値あり）
    const recipientEmail = process.env.PARTNER_RECRUIT_EMAIL || 'info@example.com';
    const fromEmail = process.env.FROM_EMAIL || 'noreply@example.com';

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
`;

    // メール送信処理
    // 方法1: SendGridを使用する場合
    if (process.env.SENDGRID_API_KEY) {
      try {
        const sgResponse = await fetch('https://api.sendgrid.com/v3/mail/send', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.SENDGRID_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            personalizations: [{
              to: [{ email: recipientEmail }],
              subject: emailSubject,
            }],
            from: { email: fromEmail },
            content: [{
              type: 'text/plain',
              value: emailBody,
            }],
          }),
        });

        if (!sgResponse.ok) {
          throw new Error('SendGrid API error');
        }
      } catch (error) {
        console.error('SendGrid送信エラー:', error);
        // SendGridが失敗してもログに記録して続行
      }
    }

    // 方法2: SMTPを使用する場合（Node.jsのnodemailerが必要）
    // nodemailerをインストール: npm install nodemailer
    if (process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASSWORD) {
      try {
        // 動的インポート（nodemailerがインストールされている場合のみ）
        const nodemailer = await import('nodemailer');
        const transporter = nodemailer.default.createTransport({
          host: process.env.SMTP_HOST,
          port: parseInt(process.env.SMTP_PORT || '587'),
          secure: false,
          auth: {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASSWORD,
          },
        });

        await transporter.sendMail({
          from: fromEmail,
          to: recipientEmail,
          subject: emailSubject,
          text: emailBody,
        });
      } catch (error) {
        console.error('SMTP送信エラー（nodemailerがインストールされていない可能性があります）:', error);
        // nodemailerがインストールされていない場合はスキップ
      }
    }

    // ログに記録（メール送信が失敗しても記録）
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

    // Notionに保存する場合（オプション）
    if (process.env.NOTION_API_KEY && process.env.NOTION_PARTNER_DB_ID) {
      try {
        await fetch('https://api.notion.com/v1/pages', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.NOTION_API_KEY}`,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28',
          },
          body: JSON.stringify({
            parent: { database_id: process.env.NOTION_PARTNER_DB_ID },
            properties: {
              Name: { title: [{ text: { content: name } }] },
              Company: { rich_text: [{ text: { content: company_name } }] },
              Email: { email: email },
              Phone: { phone_number: phone },
              Area: { rich_text: [{ text: { content: area } }] },
              Skills: { rich_text: [{ text: { content: skills } }] },
              Equipment: { rich_text: [{ text: { content: equipment || '' } }] },
              Experience: { rich_text: [{ text: { content: experience || '' } }] },
            },
          }),
        });
      } catch (error) {
        console.error('Notion保存エラー:', error);
        // Notionが失敗しても続行
      }
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

