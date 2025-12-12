'use client';

type TabMode = 'chat' | 'diagnostic' | 'repair_advice';

interface TabNavigationProps {
  activeTab: TabMode;
  onTabChange: (tab: TabMode) => void;
}

export default function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  const tabs = [
    { id: 'chat' as TabMode, label: '🤖 統合チャット', icon: '🤖' },
    // { id: 'diagnostic' as TabMode, label: '🔍 症状診断', icon: '🔍' }, // 非表示: 統合チャットと機能が重複
    { id: 'repair_advice' as TabMode, label: '🔧 修理アドバイスセンター', icon: '🔧' },
  ];

  return (
    <div className="flex justify-center gap-2 mb-6 flex-wrap">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-6 py-3 rounded-full font-semibold transition-all duration-300 ${
            activeTab === tab.id
              ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg transform scale-105'
              : 'bg-white/90 text-gray-700 hover:bg-white hover:shadow-md border-2 border-transparent hover:border-purple-300'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
















