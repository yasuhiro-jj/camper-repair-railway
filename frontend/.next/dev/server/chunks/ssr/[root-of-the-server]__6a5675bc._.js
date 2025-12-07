module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/util [external] (util, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("util", () => require("util"));

module.exports = mod;
}),
"[externals]/stream [external] (stream, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("stream", () => require("stream"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[externals]/http [external] (http, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http", () => require("http"));

module.exports = mod;
}),
"[externals]/https [external] (https, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("https", () => require("https"));

module.exports = mod;
}),
"[externals]/url [external] (url, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("url", () => require("url"));

module.exports = mod;
}),
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/crypto [external] (crypto, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("crypto", () => require("crypto"));

module.exports = mod;
}),
"[externals]/http2 [external] (http2, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http2", () => require("http2"));

module.exports = mod;
}),
"[externals]/assert [external] (assert, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("assert", () => require("assert"));

module.exports = mod;
}),
"[externals]/tty [external] (tty, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("tty", () => require("tty"));

module.exports = mod;
}),
"[externals]/os [external] (os, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("os", () => require("os"));

module.exports = mod;
}),
"[externals]/zlib [external] (zlib, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("zlib", () => require("zlib"));

module.exports = mod;
}),
"[externals]/events [external] (events, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("events", () => require("events"));

module.exports = mod;
}),
"[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/lib/api.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * APIクライアント
 * 既存のFlaskバックエンドAPIと通信するための関数群
 */ __turbopack_context__.s([
    "adminApi",
    ()=>adminApi,
    "chatApi",
    ()=>chatApi,
    "default",
    ()=>__TURBOPACK__default__export__,
    "factoryApi",
    ()=>factoryApi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/axios/lib/axios.js [app-ssr] (ecmascript)");
;
const API_URL = ("TURBOPACK compile-time value", "http://localhost:5002") || 'http://localhost:5002';
const apiClient = __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 60000
});
const chatApi = {
    /**
   * チャットメッセージを送信
   */ sendMessage: async (message, sessionId)=>{
        const response = await apiClient.post('/api/unified/chat', {
            message,
            session_id: sessionId
        });
        return response.data;
    },
    /**
   * 会話を開始
   */ startConversation: async (sessionId)=>{
        const response = await apiClient.post('/start_conversation', {
            session_id: sessionId
        });
        return response.data;
    }
};
const factoryApi = {
    /**
   * 案件一覧を取得
   */ getCases: async (status)=>{
        try {
            const params = status ? {
                status
            } : {};
            const response = await apiClient.get('/admin/api/cases', {
                params
            });
            if (response.data.success && response.data.cases) {
                return response.data.cases;
            }
            // 互換性のため、casesが直接配列の場合も対応
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error('案件取得APIエラー:', error);
            if (error.response) {
                console.error('レスポンス:', error.response.data);
                console.error('ステータス:', error.response.status);
            }
            throw error;
        }
    },
    /**
   * 案件のステータスを更新
   */ updateCaseStatus: async (pageId, status)=>{
        await apiClient.post('/admin/api/update-status', {
            page_id: pageId,
            status
        });
    },
    /**
   * コメントを追加
   */ addComment: async (pageId, comment)=>{
        await apiClient.post('/admin/api/add-comment', {
            page_id: pageId,
            comment
        });
    }
};
const adminApi = {
    /**
   * データベースを再構築
   */ reloadDatabase: async ()=>{
        const response = await apiClient.post('/reload_data');
        return response.data;
    },
    /**
   * ファイル一覧を取得
   */ getFileList: async ()=>{
        try {
            const response = await apiClient.get('/api/admin/files');
            return response.data.files || [];
        } catch (error) {
            console.error('ファイル一覧取得エラー:', error);
            return [];
        }
    },
    /**
   * システム情報を取得
   */ getSystemInfo: async ()=>{
        try {
            const response = await apiClient.get('/api/admin/system-info');
            return response.data;
        } catch (error) {
            console.error('システム情報取得エラー:', error);
            return {
                dbStatus: 'エラー',
                docCount: 0
            };
        }
    },
    /**
   * ビルダー一覧を取得
   */ getBuilders: async ()=>{
        try {
            const response = await apiClient.get('/api/v1/builders');
            return response.data.builders || [];
        } catch (error) {
            console.error('ビルダー一覧取得エラー:', error);
            throw error;
        }
    },
    /**
   * 工場ネットワーク情報を取得
   */ getFactoryNetwork: async ()=>{
        try {
            const response = await apiClient.get('/api/admin/factory-network');
            return response.data;
        } catch (error) {
            console.error('工場ネットワーク情報取得エラー:', error);
            return {
                factories: []
            };
        }
    },
    /**
   * トラブル傾向分析を取得
   */ getAnalytics: async ()=>{
        try {
            const response = await apiClient.get('/api/admin/analytics');
            return response.data;
        } catch (error) {
            console.error('トラブル傾向分析取得エラー:', error);
            return {
                trends: []
            };
        }
    }
};
const __TURBOPACK__default__export__ = apiClient;
}),
"[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>MessageList
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
'use client';
;
function MessageList({ messages }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col gap-4 p-4 bg-gray-50 rounded-lg border-2 border-gray-200 max-h-[400px] overflow-y-auto",
        children: messages.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "text-center text-gray-500 py-8",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "text-lg",
                children: "🆕 新しい会話を開始しました。何でもお聞きください！"
            }, void 0, false, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx",
                lineNumber: 14,
                columnNumber: 11
            }, this)
        }, void 0, false, {
            fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx",
            lineNumber: 13,
            columnNumber: 9
        }, this) : messages.map((message)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: `flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`,
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: `max-w-[80%] rounded-lg px-4 py-2 ${message.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-white text-gray-800 border border-gray-200'}`,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "whitespace-pre-wrap break-words",
                            children: message.text
                        }, void 0, false, {
                            fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx",
                            lineNumber: 31,
                            columnNumber: 15
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: `text-xs mt-1 ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'}`,
                            children: message.timestamp.toLocaleTimeString('ja-JP', {
                                hour: '2-digit',
                                minute: '2-digit'
                            })
                        }, void 0, false, {
                            fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx",
                            lineNumber: 34,
                            columnNumber: 15
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx",
                    lineNumber: 24,
                    columnNumber: 13
                }, this)
            }, message.id, false, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx",
                lineNumber: 18,
                columnNumber: 11
            }, this))
    }, void 0, false, {
        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx",
        lineNumber: 11,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageInput.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>MessageInput
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
'use client';
;
;
function MessageInput({ onSend, disabled = false }) {
    const [message, setMessage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const handleSend = ()=>{
        if (message.trim() && !disabled) {
            onSend(message.trim());
            setMessage('');
        }
    };
    const handleKeyPress = (e)=>{
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex gap-2 items-end",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                value: message,
                onChange: (e)=>setMessage(e.target.value),
                onKeyPress: handleKeyPress,
                placeholder: "メッセージを入力...",
                disabled: disabled,
                className: "flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:bg-gray-100 disabled:cursor-not-allowed",
                rows: 1,
                style: {
                    minHeight: '48px',
                    maxHeight: '120px'
                }
            }, void 0, false, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageInput.tsx",
                lineNumber: 29,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: handleSend,
                disabled: disabled || !message.trim(),
                className: "px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors",
                children: "送信"
            }, void 0, false, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageInput.tsx",
                lineNumber: 39,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageInput.tsx",
        lineNumber: 28,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ChatWindow
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/lib/api.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$components$2f$Chat$2f$MessageList$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageList.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$components$2f$Chat$2f$MessageInput$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/MessageInput.tsx [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
function ChatWindow() {
    const [messages, setMessages] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [sessionId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(()=>{
        // セッションIDを生成（ブラウザのローカルストレージから取得または新規作成）
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        return `session_${Date.now()}`;
    });
    const messagesEndRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    // メッセージリストの最後にスクロール
    const scrollToBottom = ()=>{
        messagesEndRef.current?.scrollIntoView({
            behavior: 'smooth'
        });
    };
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        scrollToBottom();
    }, [
        messages
    ]);
    // 会話開始
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const startConversation = async ()=>{
            try {
                await __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["chatApi"].startConversation(sessionId);
            } catch (error) {
                console.error('会話開始エラー:', error);
            }
        };
        startConversation();
    }, [
        sessionId
    ]);
    const handleSend = async (text)=>{
        // ユーザーメッセージを追加
        const userMessage = {
            id: `msg_${Date.now()}_user`,
            text,
            sender: 'user',
            timestamp: new Date()
        };
        setMessages((prev)=>[
                ...prev,
                userMessage
            ]);
        setIsLoading(true);
        // タイムアウト設定（60秒）
        const timeoutId = setTimeout(()=>{
            setIsLoading(false);
            const timeoutMessage = {
                id: `msg_${Date.now()}_timeout`,
                text: '⏱️ 応答に時間がかかっています。しばらくお待ちください。',
                sender: 'ai',
                timestamp: new Date()
            };
            setMessages((prev)=>[
                    ...prev,
                    timeoutMessage
                ]);
        }, 60000);
        try {
            // APIにメッセージを送信
            const startTime = Date.now();
            const response = await __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["chatApi"].sendMessage(text, sessionId);
            const elapsedTime = Date.now() - startTime;
            clearTimeout(timeoutId);
            // AIレスポンスを追加
            const aiMessage = {
                id: `msg_${Date.now()}_ai`,
                text: response.answer || response.response || '申し訳ございません。応答を生成できませんでした。',
                sender: 'ai',
                timestamp: new Date()
            };
            setMessages((prev)=>[
                    ...prev,
                    aiMessage
                ]);
            // デバッグ情報（開発環境のみ）
            if ("TURBOPACK compile-time truthy", 1) {
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
            const errorMessage = {
                id: `msg_${Date.now()}_error`,
                text: errorText,
                sender: 'ai',
                timestamp: new Date()
            };
            setMessages((prev)=>[
                    ...prev,
                    errorMessage
                ]);
        } finally{
            setIsLoading(false);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col h-full",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex-1 overflow-hidden",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$components$2f$Chat$2f$MessageList$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                        messages: messages
                    }, void 0, false, {
                        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                        lineNumber: 118,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        ref: messagesEndRef
                    }, void 0, false, {
                        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                        lineNumber: 119,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                lineNumber: 117,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-4",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$components$2f$Chat$2f$MessageInput$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                    onSend: handleSend,
                    disabled: isLoading
                }, void 0, false, {
                    fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                    lineNumber: 122,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                lineNumber: 121,
                columnNumber: 7
            }, this),
            isLoading && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center justify-center gap-2 mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex gap-1",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-2 h-2 bg-blue-500 rounded-full animate-bounce",
                                style: {
                                    animationDelay: '0ms'
                                }
                            }, void 0, false, {
                                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                                lineNumber: 127,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-2 h-2 bg-blue-500 rounded-full animate-bounce",
                                style: {
                                    animationDelay: '150ms'
                                }
                            }, void 0, false, {
                                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                                lineNumber: 128,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-2 h-2 bg-blue-500 rounded-full animate-bounce",
                                style: {
                                    animationDelay: '300ms'
                                }
                            }, void 0, false, {
                                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                                lineNumber: 129,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                        lineNumber: 126,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-blue-600 font-medium",
                        children: "AIが考えています..."
                    }, void 0, false, {
                        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                        lineNumber: 131,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-blue-400 text-sm",
                        children: "（通常10-30秒かかります）"
                    }, void 0, false, {
                        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                        lineNumber: 132,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
                lineNumber: 125,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/Chat/ChatWindow.tsx",
        lineNumber: 116,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__6a5675bc._.js.map