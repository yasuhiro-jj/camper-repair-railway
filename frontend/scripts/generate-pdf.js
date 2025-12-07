const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function generatePDF() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    
    // ローカル開発サーバーのURL
    const url = process.env.URL || 'http://localhost:3000/lp-partner-recruit';
    
    console.log(`📄 PDF生成中: ${url}`);
    
    await page.goto(url, {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    // ページが完全に読み込まれるまで少し待つ
    await page.waitForTimeout(2000);

    // PDF出力ディレクトリを作成
    const outputDir = path.join(__dirname, '..', 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const outputPath = path.join(outputDir, 'partner-recruit-lp.pdf');
    
    await page.pdf({
      path: outputPath,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20mm',
        right: '15mm',
        bottom: '20mm',
        left: '15mm'
      }
    });

    console.log(`✅ PDF生成完了: ${outputPath}`);
  } catch (error) {
    console.error('❌ PDF生成エラー:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

generatePDF();



