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
      <div className="text-center py-12">
        <div className="inline-flex items-center gap-2 text-gray-600">
          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span>読み込み中...</span>
        </div>
      </div>
    );
  }

  if (cases.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">案件がありません</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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

