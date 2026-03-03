'use client';

import { useState, useEffect } from 'react';
import { dealApi, InquiryFormData, costEstimationApi, CostEstimation, PartnerShop, customerNoteApi, diagnosticApi, DiagnosticResponse, partnerShopApi } from '@/lib/api';

interface InquiryFormProps {
  defaultCategory?: string;
  defaultDetail?: string;
  defaultPrefecture?: string;
  partnerPageId?: string;
  partnerShop?: PartnerShop;
  onSuccess?: (dealId: string) => void;
  onCancel?: () => void;
}

export default function InquiryForm({
  defaultCategory = '',
  defaultDetail = '',
  defaultPrefecture = '',
  partnerPageId = '',
  partnerShop,
  onSuccess,
  onCancel,
}: InquiryFormProps) {
  const inputBaseClass =
    'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder:text-gray-500 bg-white';

  const [formData, setFormData] = useState<InquiryFormData>({
    customer_name: '',
    phone: '',
    email: '',
    prefecture: defaultPrefecture,
    symptom_category: defaultCategory,
    symptom_detail: defaultDetail,
    partner_page_id: partnerPageId,
    notification_method: 'email', // デフォルトはメール
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isEstimating, setIsEstimating] = useState(false);
  const [estimation, setEstimation] = useState<CostEstimation | null>(null);
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [diagnosticResult, setDiagnosticResult] = useState<DiagnosticResponse | null>(null);
  const [submittedDealId, setSubmittedDealId] = useState<string | null>(null);
  const [showNoteForm, setShowNoteForm] = useState(false);
  const [customerNote, setCustomerNote] = useState('');
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);
  const [shops, setShops] = useState<PartnerShop[]>([]);
  const [isLoadingShops, setIsLoadingShops] = useState(false);

  // 修理店一覧を取得
  useEffect(() => {
    const loadShops = async () => {
      setIsLoadingShops(true);
      try {
        const shopList = await partnerShopApi.getShops('アクティブ');
        setShops(shopList);
        
        // partnerPageId が props で渡されている場合、それを初期値として設定
        if (partnerPageId && partnerPageId !== 'demo-page-id') {
          setFormData(prev => ({ ...prev, partner_page_id: partnerPageId }));
        }
      } catch (err) {
        console.error('修理店一覧の取得に失敗しました:', err);
      } finally {
        setIsLoadingShops(false);
      }
    };
    loadShops();
  }, [partnerPageId]);

  const formatDiagnosisFallback = (diag: any): string => {
    if (!diag || typeof diag !== 'object') return '';
    const lines: string[] = [];
    const causes = Array.isArray(diag.possible_causes) ? diag.possible_causes : [];
    const checks = Array.isArray(diag.quick_checks) ? diag.quick_checks : [];
    const actions = Array.isArray(diag.recommended_actions) ? diag.recommended_actions : [];
    const questions = Array.isArray(diag.questions_to_ask) ? diag.questions_to_ask : [];
    const tellShop = Array.isArray(diag.what_to_tell_shop) ? diag.what_to_tell_shop : [];
    if (causes.length) {
      lines.push('【想定される原因】', ...causes.map((c: string) => `- ${c}`), '');
    }
    if (checks.length) {
      lines.push('【まず確認すること（自分でできる）】', ...checks.map((c: string) => `- ${c}`), '');
    }
    if (actions.length) {
      lines.push('【推奨される対処】', ...actions.map((a: string) => `- ${a}`), '');
    }
    if (questions.length) {
      lines.push('【追加で確認したいこと】', ...questions.map((q: string) => `- ${q}`), '');
    }
    if (tellShop.length) {
      lines.push('【修理店に伝えると良い情報】', ...tellShop.map((t: string) => `- ${t}`), '');
    }
    const meta: string[] = [];
    if (diag.urgency) meta.push(`緊急度: ${diag.urgency}`);
    if (typeof diag.confidence === 'number') meta.push(`確信度: ${diag.confidence}`);
    if (meta.length) {
      lines.push('【補足】', `- ${meta.join(' / ')}`);
    }
    return lines.join('\n').trim();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // 必須項目チェック
      if (!formData.customer_name || !formData.phone || !formData.prefecture) {
        setError('名前、電話番号、都道府県は必須です');
        setIsLoading(false);
        return;
      }

      if (!formData.symptom_category || !formData.symptom_detail) {
        setError('症状カテゴリと症状詳細は必須です');
        setIsLoading(false);
        return;
      }

      if (!formData.partner_page_id || formData.partner_page_id === 'demo-page-id') {
        setError('紹介修理店が選択されていません。修理店一覧から実際の修理店を選択してください。');
        setIsLoading(false);
        return;
      }

      const deal = await dealApi.submitInquiry(formData);
      setSuccess(true);
      setSubmittedDealId(deal.deal_id);

      if (onSuccess) {
        onSuccess(deal.deal_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || '問い合わせの送信に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!submittedDealId || !customerNote.trim()) {
      setError('メッセージを入力してください');
      return;
    }

    setIsSubmittingNote(true);
    setError(null);

    try {
      const result = await customerNoteApi.addNote(submittedDealId, customerNote);
      if (result.success) {
        setCustomerNote('');
        setShowNoteForm(false);
        alert('✅ メッセージを送信しました。修理店より連絡がありますので、しばらくお待ちください。');
      } else {
        setError(result.error || 'メッセージの送信に失敗しました');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'メッセージの送信に失敗しました');
    } finally {
      setIsSubmittingNote(false);
    }
  };

  const resetForm = () => {
    setFormData({
      customer_name: '',
      phone: '',
      email: '',
      prefecture: defaultPrefecture,
      symptom_category: defaultCategory,
      symptom_detail: defaultDetail,
      partner_page_id: partnerPageId,
      notification_method: 'email',
    });
    setSuccess(false);
    setSubmittedDealId(null);
    setShowNoteForm(false);
    setCustomerNote('');
    setError(null);
  };

  if (success) {
    return (
      <div className="space-y-4">
        <div className="bg-green-100 text-green-800 p-6 rounded-lg border border-green-300">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">✅</span>
            <h3 className="text-lg font-bold">問い合わせを受け付けました</h3>
          </div>
          <p className="text-sm mb-4">修理店から連絡がありますので、しばらくお待ちください。</p>
          {submittedDealId && (
            <div className="mt-4 p-3 bg-white rounded-lg">
              <p className="text-xs text-gray-600 mb-2">商談ID: <span className="font-mono font-semibold">{submittedDealId}</span></p>
              <p className="text-xs text-gray-600 mb-2">スケジュール調整や追加のご質問がある場合は、下記のボタンからメッセージを送信できます。</p>
              <p className="text-xs text-gray-500">
                ※ 後からメッセージを送信する場合は、<a href="/customer-note" className="text-blue-600 hover:underline">専用ページ</a>から商談IDを入力して送信できます。
              </p>
            </div>
          )}
        </div>

        {submittedDealId && (
          <div className="bg-white border border-gray-300 rounded-lg p-4">
            {!showNoteForm ? (
              <button
                onClick={() => setShowNoteForm(true)}
                className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-semibold"
              >
                💬 修理店にメッセージを送る
              </button>
            ) : (
              <form onSubmit={handleAddNote} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    メッセージ <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={customerNote}
                    onChange={(e) => setCustomerNote(e.target.value)}
                    required
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder:text-gray-500 bg-white"
                    placeholder="例: 来週の月曜日から車を持って行けます。"
                  />
                </div>
                {error && (
                  <div className="bg-red-100 text-red-800 p-3 rounded-lg border border-red-300 text-sm">
                    ❌ {error}
                  </div>
                )}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={isSubmittingNote || !customerNote.trim()}
                    className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                  >
                    {isSubmittingNote ? '送信中...' : '📤 送信'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowNoteForm(false);
                      setCustomerNote('');
                      setError(null);
                    }}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    キャンセル
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        <button
          onClick={resetForm}
          className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors font-semibold"
        >
          🔄 新しいお問い合わせを送る
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* 修理店選択 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          紹介修理店 <span className="text-red-500">*</span>
        </label>
        {isLoadingShops ? (
          <div className="px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500">
            読み込み中...
          </div>
        ) : (
          <select
            value={formData.partner_page_id}
            onChange={(e) => setFormData({ ...formData, partner_page_id: e.target.value })}
            required
            className={inputBaseClass}
            disabled={!!partnerShop && partnerShop.shop_id !== 'demo'}
          >
            <option value="">-- 修理店を選択してください --</option>
            {shops.map((shop) => (
              <option key={shop.page_id} value={shop.page_id || ''}>
                {shop.name || '名称不明'} {shop.prefecture ? `(${shop.prefecture})` : ''}
              </option>
            ))}
          </select>
        )}
        {partnerShop && partnerShop.shop_id !== 'demo' && (
          <p className="text-xs text-gray-500 mt-1">
            選択済み: {partnerShop.name}
          </p>
        )}
        {formData.partner_page_id === 'demo-page-id' && (
          <p className="text-xs text-amber-600 mt-1">
            ⚠️ デモモードです。上記から実際の修理店を選択してください。
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          お名前 <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.customer_name}
          onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
          required
          className={inputBaseClass}
          placeholder="例: 山田太郎"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          電話番号 <span className="text-red-500">*</span>
        </label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          required
          className={inputBaseClass}
          placeholder="例: 090-1234-5678"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          メール相談の方はメールアドレス必須
        </label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className={inputBaseClass}
          placeholder="例: example@email.com"
        />
      </div>

      {/* 通知方法の選択 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          連絡方法の希望 <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
            <input
              type="radio"
              name="notification_method"
              value="email"
              checked={formData.notification_method === 'email'}
              onChange={(e) => setFormData({ ...formData, notification_method: e.target.value as 'email' | 'line' })}
              className="mr-3"
              required
            />
            <div className="flex-1">
              <div className="font-medium text-gray-900">📧 メールで連絡を希望</div>
              <div className="text-xs text-gray-500">メールアドレスに連絡先を記載してください</div>
            </div>
          </label>
          <label className="flex items-start p-3 border-2 border-[#00C300] bg-[#00C300]/10 rounded-lg cursor-pointer hover:bg-[#00C300]/20 transition-colors">
            <input
              type="radio"
              name="notification_method"
              value="line"
              checked={formData.notification_method === 'line'}
              onChange={(e) => setFormData({ ...formData, notification_method: e.target.value as 'email' | 'line' })}
              className="mr-3 mt-1"
              required
            />
            <div className="flex-1">
              <div className="font-medium text-gray-900 mb-1">💬 LINEで連絡を希望</div>
              <div className="text-xs text-gray-600 mb-2">LINE通知を受け取るには、修理店のLINE公式アカウントを友達追加してください</div>
              {partnerShop?.line_bot_id ? (
                <a
                  href={`https://line.me/R/ti/p/${partnerShop.line_bot_id.startsWith('@') ? partnerShop.line_bot_id.substring(1) : partnerShop.line_bot_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center justify-center gap-2 px-3 py-1.5 bg-[#00C300] text-white rounded-lg hover:bg-[#00B300] transition-colors font-semibold text-xs"
                >
                  <span>💬</span>
                  <span>LINE公式アカウントを友達追加</span>
                </a>
              ) : partnerShop?.line_webhook_url ? (
                <a
                  href={partnerShop.line_webhook_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center justify-center gap-2 px-3 py-1.5 bg-[#00C300] text-white rounded-lg hover:bg-[#00B300] transition-colors font-semibold text-xs"
                >
                  <span>💬</span>
                  <span>LINEで問い合わせ</span>
                </a>
              ) : null}
            </div>
          </label>
        </div>
        {formData.notification_method === 'email' && !formData.email && (
          <p className="text-xs text-amber-600 mt-1">⚠️ メール通知を希望する場合は、メールアドレスの入力をお願いします</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          所在地（都道府県） <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.prefecture}
          onChange={(e) => setFormData({ ...formData, prefecture: e.target.value })}
          required
          className={inputBaseClass}
          placeholder="例: 東京都"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          症状カテゴリ <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.symptom_category}
          onChange={(e) => setFormData({ ...formData, symptom_category: e.target.value })}
          required
          className={inputBaseClass}
          placeholder="例: エアコン、バッテリー"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          症状詳細 <span className="text-red-500">*</span>
        </label>
        <textarea
          value={formData.symptom_detail}
          onChange={(e) => {
            setFormData({ ...formData, symptom_detail: e.target.value });
            setEstimation(null); // 症状が変更されたら推定結果をクリア
            setDiagnosticResult(null); // 症状が変更されたら診断結果をクリア
          }}
          required
          rows={4}
          className={`${inputBaseClass}`}
          placeholder="例: エアコンが効かない、冷房が効かない"
        />
        {formData.symptom_detail && (
          <div className="flex gap-2 mt-2">
            <button
              type="button"
              onClick={async () => {
                setIsDiagnosing(true);
                setError(null);
                try {
                  const result = await diagnosticApi.diagnose({
                    message: `${formData.symptom_category}: ${formData.symptom_detail}`,
                    category: formData.symptom_category,
                  });
                  setDiagnosticResult(result);
                } catch (err: any) {
                  setError(err.message || '診断に失敗しました');
                } finally {
                  setIsDiagnosing(false);
                }
              }}
              disabled={isDiagnosing || !formData.symptom_detail}
              className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold"
            >
              {isDiagnosing ? '診断中...' : '🔍 AI診断'}
            </button>
            <button
              type="button"
              onClick={async () => {
                setIsEstimating(true);
                setError(null);
                try {
                  const result = await costEstimationApi.estimateCost({
                    symptoms: formData.symptom_detail,
                    category: formData.symptom_category,
                  });
                  setEstimation(result);
                } catch (err: any) {
                  setError(err.message || '工賃推定に失敗しました');
                } finally {
                  setIsEstimating(false);
                }
              }}
              disabled={isEstimating || !formData.symptom_detail}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold"
            >
              {isEstimating ? '推定中...' : '💰 工賃を推定'}
            </button>
          </div>
        )}
      </div>

      {/* 診断結果 */}
      {diagnosticResult && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-lg font-bold text-purple-900 mb-3">🔍 AI診断結果</h3>
          <div className="bg-white p-4 rounded-lg mb-3">
            {(() => {
              const text =
                diagnosticResult.response ||
                (diagnosticResult as any).message ||
                formatDiagnosisFallback((diagnosticResult as any).diagnosis);
              const html = (text || '診断結果が取得できませんでした').replace(/\n/g, '<br>');
              return (
            <div 
              className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: html }}
            />
              );
            })()}
          </div>
          {diagnosticResult.notion_results?.diagnostic_nodes && diagnosticResult.notion_results.diagnostic_nodes.length > 0 && (
            <div className="text-xs text-gray-500 mt-2">
              ※ 診断データベースから {diagnosticResult.notion_results.diagnostic_nodes.length} 件の関連情報を参照しました
            </div>
          )}
        </div>
      )}

      {/* 工賃推定結果 */}
      {estimation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-bold text-blue-900 mb-3">💰 工賃推定結果</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
            <div className="bg-white p-3 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">作業時間</div>
              <div className="text-xl font-bold text-blue-600">
                {estimation.estimated_work_hours}時間
              </div>
              <div className="text-xs text-gray-500 mt-1">難易度: {estimation.difficulty}</div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">診断料</div>
              <div className="text-xl font-bold text-blue-600">
                {estimation.diagnosis_fee.toLocaleString()}円
              </div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">工賃</div>
              <div className="text-xl font-bold text-blue-600">
                {estimation.labor_cost_min.toLocaleString()}円 〜 {estimation.labor_cost_max.toLocaleString()}円
              </div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">部品代</div>
              <div className="text-xl font-bold text-blue-600">
                {estimation.parts_cost_min.toLocaleString()}円 〜 {estimation.parts_cost_max.toLocaleString()}円
              </div>
            </div>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
            <div className="text-sm font-semibold text-yellow-900 mb-1">総額（目安）</div>
            <div className="text-2xl font-bold text-yellow-700">
              {estimation.total_cost_min.toLocaleString()}円 〜 {estimation.total_cost_max.toLocaleString()}円
            </div>
          </div>
          {estimation.reasoning && (
            <div className="text-sm text-gray-700 bg-white p-3 rounded-lg">
              <div className="font-semibold mb-1">推定理由:</div>
              <div>{estimation.reasoning}</div>
            </div>
          )}
          {estimation.similar_cases_count && estimation.similar_cases_count > 0 && (
            <div className="text-xs text-gray-500 mt-2">
              ※ 類似ケース {estimation.similar_cases_count}件を参考に推定しました
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="bg-red-100 text-red-800 p-4 rounded-lg border border-red-300">
          ❌ {error}
        </div>
      )}

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
        >
          {isLoading ? '送信中...' : '📧 問い合わせを送信'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
          >
            キャンセル
          </button>
        )}
      </div>
    </form>
  );
}

