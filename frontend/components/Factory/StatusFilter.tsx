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
    <div className="flex gap-2 flex-wrap">
      {statusOptions.map((option) => (
        <button
          key={option.value}
          onClick={() => onStatusChange(option.value)}
          className={`px-4 py-2 rounded-lg border-2 transition-all ${
            activeStatus === option.value
              ? 'bg-purple-600 text-white border-purple-600'
              : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400 hover:text-purple-600'
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

