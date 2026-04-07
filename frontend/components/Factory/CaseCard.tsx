'use client';

import { useState } from 'react';
import { FactoryCase } from '@/types';

interface CaseCardProps {
  case: FactoryCase;
  onStatusUpdate: (caseId: string, status: string) => void;
  onCommentAdd: (caseId: string, comment: string, notifyCustomerEmail?: boolean) => void;
}

export default function CaseCard({ case: caseItem, onStatusUpdate, onCommentAdd }: CaseCardProps) {
  const [showCommentForm, setShowCommentForm] = useState(false);
  const [comment, setComment] = useState('');
  const [notifyCustomerEmail, setNotifyCustomerEmail] = useState(false);
  const [isStatusUpdating, setIsStatusUpdating] = useState(false);
  const [isCommentSubmitting, setIsCommentSubmitting] = useState(false);

  const caseKey = caseItem.id || caseItem.page_id || '';

  const handleStatusChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStatus = e.target.value;
    setIsStatusUpdating(true);
    try {
      await onStatusUpdate(caseKey, newStatus);
    } finally {
      setIsStatusUpdating(false);
    }
  };

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim()) return;
    
    setIsCommentSubmitting(true);
    try {
      await onCommentAdd(caseKey, comment, notifyCustomerEmail);
      setComment('');
      setNotifyCustomerEmail(false);
      setShowCommentForm(false);
    } finally {
      setIsCommentSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    // 日本語ステータスと英語ステータスの両方に対応
    const statusLower = status.toLowerCase();
    if (status === '受付' || statusLower === 'pending') {
      return 'bg-amber-100 text-amber-900 ring-1 ring-amber-200/80';
    }
    if (status === '診断中' || status === '修理中' || statusLower === 'in_progress') {
      return 'bg-blue-100 text-blue-900 ring-1 ring-blue-200/80';
    }
    if (status === '完了' || statusLower === 'completed') {
      return 'bg-emerald-100 text-emerald-900 ring-1 ring-emerald-200/80';
    }
    if (status === 'キャンセル' || statusLower === 'cancelled') {
      return 'bg-red-100 text-red-900 ring-1 ring-red-200/80';
    }
    return 'bg-slate-100 text-slate-800 ring-1 ring-slate-200/80';
  };

  const getStatusAccent = (status: string) => {
    const statusLower = status.toLowerCase();
    if (status === '受付' || statusLower === 'pending') return 'border-l-amber-400';
    if (status === '診断中' || status === '修理中' || statusLower === 'in_progress')
      return 'border-l-blue-500';
    if (status === '完了' || statusLower === 'completed') return 'border-l-emerald-500';
    if (status === 'キャンセル' || statusLower === 'cancelled') return 'border-l-red-400';
    return 'border-l-slate-300';
  };

  const getStatusLabel = (status: string) => {
    // 既存のステータスをそのまま返す（日本語の可能性がある）
    return status;
  };

  const displayName = (caseItem.customerName || caseItem.customer_name || '').trim();
  const email = caseItem.email?.trim() || '';
  const phone = caseItem.phone?.trim() || '';
  const hasContact = Boolean(displayName || email || phone);
  const canSubmitComment = comment.trim().length > 0 && !isCommentSubmitting;

  return (
    <article
      className={`rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm transition hover:shadow-md ${getStatusAccent(caseItem.status)} border-l-4`}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="mb-2 text-base font-semibold leading-snug text-slate-900 sm:text-lg">
            {caseItem.title || `案件 #${caseItem.id || caseItem.page_id}`}
          </h3>
          {hasContact && (
            <div className="mb-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-gray-800">
              <p className="text-xs font-semibold text-slate-600 mb-1.5">連絡先（お客様）</p>
              {displayName && (
                <p className="mb-1">
                  <span className="text-gray-500">お名前: </span>
                  {displayName}
                </p>
              )}
              {email && (
                <p className="mb-1 break-all">
                  <span className="text-gray-500">メール: </span>
                  <a href={`mailto:${email}`} className="text-blue-700 underline hover:text-blue-900">
                    {email}
                  </a>
                </p>
              )}
              {phone && (
                <p>
                  <span className="text-gray-500">電話: </span>
                  <a href={`tel:${phone.replace(/\s/g, '')}`} className="text-blue-700 underline hover:text-blue-900">
                    {phone}
                  </a>
                </p>
              )}
            </div>
          )}
          {caseItem.description && (
            <p className="text-sm text-gray-600 mb-2 line-clamp-2">
              {caseItem.description}
            </p>
          )}
          {caseItem.user_message && (
            <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded mb-2">
              <p className="text-xs font-semibold text-blue-800 mb-1">ユーザー:</p>
              <p className="text-sm text-gray-700">
                {caseItem.user_message.length > 200
                  ? `${caseItem.user_message.substring(0, 200)}...`
                  : caseItem.user_message}
              </p>
            </div>
          )}
          {caseItem.bot_message && (
            <div className="bg-green-50 border-l-4 border-green-400 p-3 rounded mb-2">
              <p className="text-xs font-semibold text-green-800 mb-1">AI応答:</p>
              <p className="text-sm text-gray-700">
                {caseItem.bot_message.length > 200
                  ? `${caseItem.bot_message.substring(0, 200)}...`
                  : caseItem.bot_message}
              </p>
            </div>
          )}
          {caseItem.category && (
            <p className="text-xs text-gray-500 mb-1">
              🏷️ {caseItem.category}
            </p>
          )}
        </div>
        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusColor(caseItem.status)}`}
        >
          {getStatusLabel(caseItem.status)}
        </span>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 text-xs text-slate-600 sm:text-sm">
        <div>
          <span className="font-semibold">作成日:</span>{' '}
          {caseItem.timestamp || caseItem.created_time || caseItem.createdAt
            ? new Date(caseItem.timestamp || caseItem.created_time || caseItem.createdAt).toLocaleDateString('ja-JP')
            : 'N/A'}
        </div>
        <div>
          <span className="font-semibold">更新日:</span>{' '}
          {caseItem.updatedAt
            ? new Date(caseItem.updatedAt).toLocaleDateString('ja-JP')
            : 'N/A'}
        </div>
      </div>
      {caseItem.comment && (
        <div className="mb-4 whitespace-pre-wrap rounded-lg border border-slate-100 bg-slate-50 p-3 text-sm text-slate-800">
          {caseItem.comment}
        </div>
      )}

      <div className="flex flex-col gap-2 sm:flex-row sm:items-stretch">
        <select
          value={caseItem.status}
          onChange={handleStatusChange}
          disabled={isStatusUpdating}
          className="min-h-[44px] flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-black focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
          style={{ color: '#000000' }}
        >
          <option value="受付">受付</option>
          <option value="診断中">診断中</option>
          <option value="修理中">修理中</option>
          <option value="完了">完了</option>
          <option value="キャンセル">キャンセル</option>
        </select>
        
        <button
          type="button"
          onClick={() => setShowCommentForm(!showCommentForm)}
          className="min-h-[44px] rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-50"
        >
          コメント
        </button>
      </div>

      {showCommentForm && (
        <form onSubmit={handleCommentSubmit} className="mt-4 border-t border-slate-100 pt-4">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="コメントを入力..."
            disabled={isCommentSubmitting}
            className="mb-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ color: '#000000' }}
            rows={3}
          />
          {email && (
            <label className="mb-3 flex cursor-pointer items-start gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={notifyCustomerEmail}
                onChange={(e) => setNotifyCustomerEmail(e.target.checked)}
                disabled={isCommentSubmitting}
                className="mt-0.5 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span>
                お客様のメール（{email}）に、このコメントを送信する
              </span>
            </label>
          )}
          <div className="flex flex-wrap gap-2">
            <button
              type="submit"
              disabled={!canSubmitComment}
              className={`rounded-lg px-4 py-2 text-sm font-medium text-white transition ${
                canSubmitComment
                  ? 'bg-blue-600 hover:bg-blue-700'
                  : 'cursor-not-allowed bg-slate-300'
              }`}
            >
              {isCommentSubmitting ? '送信中...' : '送信'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowCommentForm(false);
                setComment('');
                setNotifyCustomerEmail(false);
              }}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              キャンセル
            </button>
          </div>
        </form>
      )}
    </article>
  );
}

