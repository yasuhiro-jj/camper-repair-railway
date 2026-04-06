'use client';

import { FactoryCase } from '@/types';
import CaseCard from './CaseCard';

interface CaseListProps {
  cases: FactoryCase[];
  isLoading: boolean;
  onStatusUpdate: (caseId: string, status: string) => void;
  onCommentAdd: (caseId: string, comment: string) => void;
}

export default function CaseList({ cases, isLoading, onStatusUpdate, onCommentAdd }: CaseListProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <div className="inline-flex items-center gap-3 rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm text-slate-600">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-blue-600" />
          <span>読み込み中...</span>
        </div>
      </div>
    );
  }

  if (cases.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/80 px-6 py-14 text-center">
        <p className="text-base font-medium text-slate-700">該当する案件はありません</p>
        <p className="mt-2 text-sm text-slate-500">フィルタを「すべて」にするか、しばらくしてから更新してください。</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {cases.map((caseItem) => (
        <CaseCard
          key={caseItem.id || caseItem.page_id}
          case={caseItem}
          onStatusUpdate={onStatusUpdate}
          onCommentAdd={onCommentAdd}
        />
      ))}
    </div>
  );
}

