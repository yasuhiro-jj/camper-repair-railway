'use client';

const blogLinks = [
  {
    title: '🔋 キャンピングカーのサブバッテリー走行充電を完全解説',
    url: 'https://camper-repair.net/blog/',
  },
  {
    title: '🔥 キャンピングカー搭載FFヒーターのメンテナンス基礎知識',
    url: 'https://camper-repair.net/blog/',
  },
  {
    title: '🚗 買ってはいけないキャンピングカーとは？状態確認が後悔を防ぐカギ',
    url: 'https://camper-repair.net/blog/',
  },
];

export default function RelatedBlogs() {
  return (
    <div className="bg-gray-50 border-l-4 border-purple-600 rounded-lg p-5 mb-6">
      <h3 className="text-purple-600 font-bold text-lg mb-4">📚 関連ブログ</h3>
      <p className="text-gray-600 mb-4 text-sm">
        より詳しい情報は<a href="https://camper-repair.net/blog/" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline font-semibold">修理ブログ一覧</a>をご覧ください。
      </p>
      <div className="flex flex-col gap-3">
        {blogLinks.map((blog, index) => (
          <a
            key={index}
            href={blog.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-purple-600 hover:text-purple-800 hover:underline transition-colors text-sm font-medium"
          >
            {blog.title}
          </a>
        ))}
      </div>
    </div>
  );
}

