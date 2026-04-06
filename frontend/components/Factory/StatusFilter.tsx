'use client';

interface StatusFilterProps {
  activeStatus: string;
  onStatusChange: (status: string) => void;
}

const statusOptions = [
  { value: '', label: 'すべて' },
  { value: '受付', label: '受付' },
  { value: '診断中', label: '診断中' },
  { value: '修理中', label: '修理中' },
  { value: '完了', label: '完了' },
  { value: 'キャンセル', label: 'キャンセル' },
];

export default function StatusFilter({ activeStatus, onStatusChange }: StatusFilterProps) {
  return (
    <div className="-mx-1 flex gap-2 overflow-x-auto pb-1 sm:flex-wrap sm:overflow-visible">
      {statusOptions.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onStatusChange(option.value)}
          className={`shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
            activeStatus === option.value
              ? 'bg-slate-900 text-white shadow-sm ring-1 ring-slate-900'
              : 'border border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

