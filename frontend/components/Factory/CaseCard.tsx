'use client';

import { useState } from 'react';
import { FactoryCase } from '@/types';

interface CaseCardProps {
  case: FactoryCase;
  onStatusUpdate: (caseId: string, status: string) => void;
  onCommentAdd: (caseId: string, comment: string) => void;
}

export default function CaseCard({ case: caseItem, onStatusUpdate, onCommentAdd }: CaseCardProps) {
  const [showCommentForm, setShowCommentForm] = useState(false);
  const [comment, setComment] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const handleStatusChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStatus = e.target.value;
    setIsUpdating(true);
    try {
      await onStatusUpdate(caseItem.id, newStatus);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim()) return;
    
    setIsUpdating(true);
    try {
      await onCommentAdd(caseItem.id, comment);
      setComment('');
      setShowCommentForm(false);
    } finally {
      setIsUpdating(false);
    }
  };

  const getStatusColor = (status: string) => {
    // 日本語ステータスと英語ステータスの両方に対応
    const statusLower = status.toLowerCase();
    if (status === '受付' || statusLower === 'pending') {
      return 'bg-yellow-100 text-yellow-800';
    }
    if (status === '診断中' || status === '修理中' || statusLower === 'in_progress') {
      return 'bg-blue-100 text-blue-800';
    }
    if (status === '完了' || statusLower === 'completed') {
      return 'bg-green-100 text-green-800';
    }
    if (status === 'キャンセル' || statusLower === 'cancelled') {
      return 'bg-red-100 text-red-800';
    }
    return 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status: string) => {
    // 既存のステータスをそのまま返す（日本語の可能性がある）
    return status;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {caseItem.title || `案件 #${caseItem.id}`}
          </h3>
          {caseItem.customerName && (
            <p className="text-sm text-gray-600 mb-1">
              顧客名: {caseItem.customerName}
            </p>
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
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(caseItem.status)}`}>
          {getStatusLabel(caseItem.status)}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 text-sm text-gray-600">
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
        <div className="bg-gray-50 p-3 rounded mb-4 text-sm text-gray-700 whitespace-pre-wrap">
          {caseItem.comment}
        </div>
      )}

      <div className="flex gap-2">
        <select
          value={caseItem.status}
          onChange={handleStatusChange}
          disabled={isUpdating}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 text-black bg-white"
          style={{ color: '#000000' }}
        >
          <option value="受付">受付</option>
          <option value="診断中">診断中</option>
          <option value="修理中">修理中</option>
          <option value="完了">完了</option>
          <option value="キャンセル">キャンセル</option>
        </select>
        
        <button
          onClick={() => setShowCommentForm(!showCommentForm)}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          💬 コメント
        </button>
      </div>

      {showCommentForm && (
        <form onSubmit={handleCommentSubmit} className="mt-4 pt-4 border-t border-gray-200">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="コメントを入力..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2 text-black bg-white"
            style={{ color: '#000000' }}
            rows={3}
          />
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isUpdating || !comment.trim()}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              送信
            </button>
            <button
              type="button"
              onClick={() => {
                setShowCommentForm(false);
                setComment('');
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              キャンセル
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

