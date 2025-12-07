'use client';

import { Message } from '@/types';
import MessageInput from './MessageInput';

interface MessageListProps {
  messages: Message[];
  onSend?: (message: string) => void;
  disabled?: boolean;
}

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

export default function MessageList({ messages, onSend, disabled = false }: MessageListProps) {
  return (
    <div className={`flex flex-col gap-3 bg-gray-50 rounded-lg border-2 border-gray-200 flex-1 overflow-y-auto mb-0 ${messages.length === 0 ? 'p-3' : 'p-3'}`}>
      {messages.length === 0 ? (
        <>
          <div className="text-center text-gray-500 py-2">
            <p className="text-base mb-2">🆕 新しい会話を開始しました。何でもお聞きください！</p>
            {onSend && (
              <div className="mt-2">
                <MessageInput onSend={onSend} disabled={disabled} />
              </div>
            )}
          </div>
          
          {/* ブログセクション */}
          <div className="bg-white border-l-4 border-purple-600 rounded-lg p-4 mt-4">
            <h3 className="text-purple-600 font-bold text-base mb-3">📚 岡山キャンピングカー修理サポートブログ</h3>
            <p className="text-gray-600 mb-3 text-sm">
              より詳しい情報は<a href="https://camper-repair.net/blog/" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline font-semibold">修理ブログ一覧</a>をご覧ください。
            </p>
            <div className="flex flex-col gap-2">
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
        </>
      ) : (
        messages.map((message) => {
          // システムメッセージの場合は中央に表示
          if (message.sender === 'system') {
            return (
              <div key={message.id} className="flex justify-center my-3">
                <div className="max-w-[90%] bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg px-4 py-2.5 text-center italic">
                  <div className="whitespace-pre-wrap break-words">{message.text}</div>
                </div>
              </div>
            );
          }
          
          return (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.sender === 'user'
                    ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white'
                    : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
                }`}
              >
                <div className="whitespace-pre-wrap break-words">
                  {message.text}
                </div>
                <div
                  className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-purple-100' : 'text-gray-500'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString('ja-JP', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

