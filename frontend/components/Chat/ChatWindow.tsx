'use client';

import { useState, useEffect, useRef } from 'react';
import { Message } from '@/types';
import { chatApi, ChatResponse } from '@/lib/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import TabNavigation from './TabNavigation';
import QuickActions from './QuickActions';
import RelatedBlogs from './RelatedBlogs';

type TabMode = 'chat' | 'diagnostic' | 'repair_advice';

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<TabMode>('chat');
  const [sessionId] = useState<string>(() => {
    // セッションIDを生成（ブラウザのローカルストレージから取得または新規作成）
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('chat_session_id');
      if (stored) return stored;
      const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('chat_session_id', newId);
      return newId;
    }
    return `session_${Date.now()}`;
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // メッセージリストの最後にスクロール
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 会話開始
  useEffect(() => {
    const startConversation = async () => {
      try {
        await chatApi.startConversation(sessionId);
        // 初期メッセージを追加
        const welcomeMessage: Message = {
          id: `msg_${Date.now()}_welcome`,
          text: '🔧 キャンピングカー修理チャットボットにようこそ！\n修理について何でもお聞きください。AI診断、詳細検索、費用相談など、あらゆる機能を統合しています。',
          sender: 'system',
          timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
      } catch (error) {
        console.error('会話開始エラー:', error);
      }
    };
    startConversation();
  }, [sessionId]);

  // タブ変更時の処理
  const handleTabChange = (tab: TabMode) => {
    setActiveTab(tab);
    if (tab === 'repair_advice') {
      // 修理アドバイスセンターの場合は別ページに遷移
      if (typeof window !== 'undefined') {
        window.location.href = '/repair-advice';
      }
    }
  };

  // クイックメッセージ送信
  const handleQuickMessage = (message: string) => {
    handleSend(message);
  };

  const handleSend = async (text: string) => {
    // ユーザーメッセージを追加
    const userMessage: Message = {
      id: `msg_${Date.now()}_user`,
      text,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // タイムアウト設定（60秒）
    const timeoutId = setTimeout(() => {
      setIsLoading(false);
      const timeoutMessage: Message = {
        id: `msg_${Date.now()}_timeout`,
        text: '⏱️ 応答に時間がかかっています。しばらくお待ちください。',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, timeoutMessage]);
    }, 60000);

    try {
      // APIにメッセージを送信
      const startTime = Date.now();
      const response: ChatResponse = await chatApi.sendMessage(text, sessionId);
      const elapsedTime = Date.now() - startTime;

      clearTimeout(timeoutId);

      // AIレスポンスを追加
      const aiMessage: Message = {
        id: `msg_${Date.now()}_ai`,
        text: response.answer || response.response || '申し訳ございません。応答を生成できませんでした。',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);

      // デバッグ情報（開発環境のみ）
      if (process.env.NODE_ENV === 'development') {
        console.log(`応答時間: ${(elapsedTime / 1000).toFixed(2)}秒`);
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('メッセージ送信エラー:', error);
      
      let errorText = '❌ エラーが発生しました。';
      if (error instanceof Error) {
        if (error.message.includes('timeout') || error.message.includes('Network Error')) {
          errorText = '⏱️ タイムアウトしました。もう一度お試しください。';
        } else {
          errorText = `❌ エラー: ${error.message}`;
        }
      }
      
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        text: errorText,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* タブナビゲーション */}
      <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />

      {/* クイックアクション（統合チャットと症状診断の時のみ表示） */}
      {(activeTab === 'chat' || activeTab === 'diagnostic') && (
        <QuickActions onQuickMessage={handleQuickMessage} />
      )}

      {/* チャットメッセージエリア */}
      <div className="flex-1 flex flex-col overflow-hidden min-h-0">
        {activeTab === 'chat' && (
          <>
            <MessageList 
              messages={messages} 
              onSend={messages.length === 0 ? handleSend : undefined}
              disabled={isLoading}
            />
            <div ref={messagesEndRef} className="h-0" />
            {/* 関連ブログセクション（一時的に非表示） */}
            {/* {messages.length <= 1 && <RelatedBlogs />} */}
            {/* メッセージがある時は下部にメッセージ入力欄を表示 */}
            {messages.length > 0 && (
              <div className="mt-2 flex-shrink-0">
                <MessageInput onSend={handleSend} disabled={isLoading} />
              </div>
            )}
          </>
        )}
        {activeTab === 'diagnostic' && (
          <div className="flex-1 flex flex-col min-h-0">
            <div className="text-center py-4 text-gray-600">
              <p className="text-lg mb-2">🔍 症状診断機能</p>
              <p className="text-sm text-gray-500">
                症状を詳しく教えてください。AIが原因を特定します。
              </p>
            </div>
            <div className="flex-1 flex flex-col overflow-hidden">
              <MessageList
                messages={messages}
                onSend={messages.length === 0 ? handleSend : undefined}
                disabled={isLoading}
              />
              <div ref={messagesEndRef} className="h-0" />
            </div>
            {messages.length > 0 && (
              <div className="mt-2 flex-shrink-0">
                <MessageInput onSend={handleSend} disabled={isLoading} />
              </div>
            )}
          </div>
        )}
      </div>

      {/* ローディング表示 */}
      {isLoading && (
        <div className="flex items-center justify-center gap-2 mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="text-blue-600 font-medium">AIが考えています...</span>
          <span className="text-blue-400 text-sm">（通常10-30秒かかります）</span>
        </div>
      )}
    </div>
  );
}

