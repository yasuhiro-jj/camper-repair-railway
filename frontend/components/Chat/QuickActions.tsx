'use client';

interface QuickActionsProps {
  onQuickMessage: (message: string) => void;
}

const quickActions = [
  { label: 'バッテリー上がり', message: 'バッテリーが上がりません' },
  { label: 'トイレ詰まり', message: 'トイレが詰まりました' },
  { label: 'エアコン故障', message: 'エアコンが効きません' },
  { label: '雨漏り', message: '雨漏りがします' },
  { label: '費用相談', message: '修理費用を知りたい' },
];

export default function QuickActions({ onQuickMessage }: QuickActionsProps) {
  return (
    <div className="flex flex-wrap gap-3 mb-6 justify-center">
      {quickActions.map((action) => (
        <button
          key={action.label}
          onClick={() => onQuickMessage(action.message)}
          className="px-5 py-2.5 bg-white rounded-lg text-gray-700 font-medium hover:bg-purple-50 hover:text-purple-700 transition-all duration-200 shadow-sm hover:shadow-md border-2 border-gray-200 hover:border-purple-300"
        >
          {action.label}
        </button>
      ))}
    </div>
  );
}
























