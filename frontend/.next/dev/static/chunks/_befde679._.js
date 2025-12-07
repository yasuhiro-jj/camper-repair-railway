(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/lib/api.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * APIクライアント
 * 既存のFlaskバックエンドAPIと通信するための関数群
 */ __turbopack_context__.s([
    "adminApi",
    ()=>adminApi,
    "chatApi",
    ()=>chatApi,
    "costEstimationApi",
    ()=>costEstimationApi,
    "dealApi",
    ()=>dealApi,
    "default",
    ()=>__TURBOPACK__default__export__,
    "factoryApi",
    ()=>factoryApi,
    "factoryMatchingApi",
    ()=>factoryMatchingApi,
    "partnerShopApi",
    ()=>partnerShopApi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/axios/lib/axios.js [app-client] (ecmascript)");
;
const API_URL = ("TURBOPACK compile-time value", "http://localhost:5002") || 'http://localhost:5002';
const apiClient = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].create({
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
const factoryMatchingApi = {
    /**
   * 案件に最適な工場をマッチング
   */ matchFactories: async (caseInfo, maxResults = 5)=>{
        try {
            const response = await apiClient.post('/api/v1/factories/match', {
                case: caseInfo,
                max_results: maxResults
            });
            if (response.data.success && response.data.matched_factories) {
                return response.data.matched_factories;
            }
            return [];
        } catch (error) {
            console.error('工場マッチングAPIエラー:', error);
            throw error;
        }
    },
    /**
   * 案件を自動的に最適な工場に割り当て
   */ autoAssignCase: async (caseId, caseInfo)=>{
        try {
            const response = await apiClient.post(`/api/v1/cases/${caseId}/auto-assign`, {
                case: caseInfo
            });
            if (response.data.success && response.data.assigned_factory) {
                return response.data.assigned_factory;
            }
            return null;
        } catch (error) {
            console.error('案件自動割り当てAPIエラー:', error);
            throw error;
        }
    }
};
const partnerShopApi = {
    /**
   * パートナー修理店一覧を取得
   */ getShops: async (status, prefecture, specialty)=>{
        try {
            const params = {};
            if (status) params.status = status;
            if (prefecture) params.prefecture = prefecture;
            if (specialty) params.specialty = specialty;
            const response = await apiClient.get('/api/v1/partner-shops', {
                params
            });
            return response.data.shops || [];
        } catch (error) {
            console.error('パートナー修理店一覧取得エラー:', error);
            // 接続エラーの場合はより詳細な情報を提供
            if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
                const connectionError = new Error('バックエンドサーバーに接続できません。サーバーが起動しているか確認してください。');
                connectionError.code = error.code;
                throw connectionError;
            }
            throw error;
        }
    },
    /**
   * パートナー修理店詳細を取得
   */ getShop: async (shopId)=>{
        try {
            const response = await apiClient.get(`/api/v1/partner-shops/${shopId}`);
            return response.data;
        } catch (error) {
            console.error('パートナー修理店取得エラー:', error);
            return null;
        }
    }
};
const dealApi = {
    /**
   * 問い合わせフォームを送信（商談作成）
   */ submitInquiry: async (formData)=>{
        try {
            const response = await apiClient.post('/api/v1/deals', formData);
            if (response.data.success && response.data.deal) {
                return response.data.deal;
            }
            throw new Error(response.data.message || '問い合わせの送信に失敗しました');
        } catch (error) {
            console.error('問い合わせ送信エラー:', error);
            throw error;
        }
    },
    /**
   * 商談一覧を取得
   */ getDeals: async (status, partnerPageId)=>{
        try {
            const params = {};
            if (status) params.status = status;
            if (partnerPageId) params.partner_page_id = partnerPageId;
            const response = await apiClient.get('/api/v1/deals', {
                params
            });
            return response.data.deals || [];
        } catch (error) {
            console.error('商談一覧取得エラー:', error);
            throw error;
        }
    },
    /**
   * 商談ステータスを更新
   */ updateStatus: async (dealId, status)=>{
        try {
            const response = await apiClient.patch(`/api/v1/deals/${dealId}/status`, {
                status
            });
            if (response.data.success && response.data.deal) {
                return response.data.deal;
            }
            throw new Error('ステータス更新に失敗しました');
        } catch (error) {
            console.error('ステータス更新エラー:', error);
            throw error;
        }
    },
    /**
   * 成約金額を更新
   */ updateAmount: async (dealId, dealAmount, commissionRate)=>{
        try {
            const response = await apiClient.patch(`/api/v1/deals/${dealId}/amount`, {
                deal_amount: dealAmount,
                commission_rate: commissionRate
            });
            if (response.data.success && response.data.deal) {
                return response.data.deal;
            }
            throw new Error('成約金額更新に失敗しました');
        } catch (error) {
            console.error('成約金額更新エラー:', error);
            throw error;
        }
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
const costEstimationApi = {
    /**
   * 工賃を推定
   */ estimateCost: async (request)=>{
        try {
            const response = await apiClient.post('/api/v1/cost-estimation', request);
            if (response.data.success && response.data.estimation) {
                return response.data.estimation;
            }
            throw new Error(response.data.error || '工賃推定に失敗しました');
        } catch (error) {
            console.error('工賃推定APIエラー:', error);
            throw error;
        }
    }
};
const __TURBOPACK__default__export__ = apiClient;
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/Chat/MessageList.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>MessageList
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
'use client';
;
function MessageList({ messages }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col gap-4 p-4 bg-gray-50 rounded-lg border-2 border-gray-200 max-h-[400px] overflow-y-auto",
        children: messages.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "text-center text-gray-500 py-8",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "text-lg",
                children: "🆕 新しい会話を開始しました。何でもお聞きください！"
            }, void 0, false, {
                fileName: "[project]/components/Chat/MessageList.tsx",
                lineNumber: 14,
                columnNumber: 11
            }, this)
        }, void 0, false, {
            fileName: "[project]/components/Chat/MessageList.tsx",
            lineNumber: 13,
            columnNumber: 9
        }, this) : messages.map((message)=>{
            // システムメッセージの場合は中央に表示
            if (message.sender === 'system') {
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex justify-center my-4",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "max-w-[90%] bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg px-4 py-3 text-center italic",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "whitespace-pre-wrap break-words",
                            children: message.text
                        }, void 0, false, {
                            fileName: "[project]/components/Chat/MessageList.tsx",
                            lineNumber: 23,
                            columnNumber: 19
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/Chat/MessageList.tsx",
                        lineNumber: 22,
                        columnNumber: 17
                    }, this)
                }, message.id, false, {
                    fileName: "[project]/components/Chat/MessageList.tsx",
                    lineNumber: 21,
                    columnNumber: 15
                }, this);
            }
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: `flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`,
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: `max-w-[80%] rounded-lg px-4 py-2 ${message.sender === 'user' ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white' : 'bg-white text-gray-800 border border-gray-200 shadow-sm'}`,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "whitespace-pre-wrap break-words",
                            children: message.text
                        }, void 0, false, {
                            fileName: "[project]/components/Chat/MessageList.tsx",
                            lineNumber: 43,
                            columnNumber: 17
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: `text-xs mt-1 ${message.sender === 'user' ? 'text-purple-100' : 'text-gray-500'}`,
                            children: message.timestamp.toLocaleTimeString('ja-JP', {
                                hour: '2-digit',
                                minute: '2-digit'
                            })
                        }, void 0, false, {
                            fileName: "[project]/components/Chat/MessageList.tsx",
                            lineNumber: 46,
                            columnNumber: 17
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/Chat/MessageList.tsx",
                    lineNumber: 36,
                    columnNumber: 15
                }, this)
            }, message.id, false, {
                fileName: "[project]/components/Chat/MessageList.tsx",
                lineNumber: 30,
                columnNumber: 13
            }, this);
        })
    }, void 0, false, {
        fileName: "[project]/components/Chat/MessageList.tsx",
        lineNumber: 11,
        columnNumber: 5
    }, this);
}
_c = MessageList;
var _c;
__turbopack_context__.k.register(_c, "MessageList");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/Chat/MessageInput.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>MessageInput
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
'use client';
;
function MessageInput({ onSend, disabled = false }) {
    _s();
    const [message, setMessage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('');
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
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex gap-2 items-end",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
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
                fileName: "[project]/components/Chat/MessageInput.tsx",
                lineNumber: 29,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: handleSend,
                disabled: disabled || !message.trim(),
                className: "px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors",
                children: "送信"
            }, void 0, false, {
                fileName: "[project]/components/Chat/MessageInput.tsx",
                lineNumber: 39,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/Chat/MessageInput.tsx",
        lineNumber: 28,
        columnNumber: 5
    }, this);
}
_s(MessageInput, "l8KXAebGu4sZHsyCIQX7P8si41w=");
_c = MessageInput;
var _c;
__turbopack_context__.k.register(_c, "MessageInput");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/Chat/TabNavigation.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>TabNavigation
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
'use client';
;
function TabNavigation({ activeTab, onTabChange }) {
    const tabs = [
        {
            id: 'chat',
            label: '🤖 統合チャット',
            icon: '🤖'
        },
        {
            id: 'diagnostic',
            label: '🔍 症状診断',
            icon: '🔍'
        },
        {
            id: 'repair_advice',
            label: '🔧 修理アドバイスセンター',
            icon: '🔧'
        }
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex justify-center gap-2 mb-6 flex-wrap",
        children: tabs.map((tab)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: ()=>onTabChange(tab.id),
                className: `px-6 py-3 rounded-full font-semibold transition-all duration-300 ${activeTab === tab.id ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg transform scale-105' : 'bg-white/90 text-gray-700 hover:bg-white hover:shadow-md border-2 border-transparent hover:border-purple-300'}`,
                children: tab.label
            }, tab.id, false, {
                fileName: "[project]/components/Chat/TabNavigation.tsx",
                lineNumber: 20,
                columnNumber: 9
            }, this))
    }, void 0, false, {
        fileName: "[project]/components/Chat/TabNavigation.tsx",
        lineNumber: 18,
        columnNumber: 5
    }, this);
}
_c = TabNavigation;
var _c;
__turbopack_context__.k.register(_c, "TabNavigation");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/Chat/QuickActions.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>QuickActions
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
'use client';
;
const quickActions = [
    {
        label: 'バッテリー上がり',
        message: 'バッテリーが上がりません'
    },
    {
        label: 'トイレ詰まり',
        message: 'トイレが詰まりました'
    },
    {
        label: 'エアコン故障',
        message: 'エアコンが効きません'
    },
    {
        label: '雨漏り',
        message: '雨漏りがします'
    },
    {
        label: '費用相談',
        message: '修理費用を知りたい'
    }
];
function QuickActions({ onQuickMessage }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-wrap gap-3 mb-6 justify-center",
        children: quickActions.map((action)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: ()=>onQuickMessage(action.message),
                className: "px-5 py-2.5 bg-white rounded-lg text-gray-700 font-medium hover:bg-purple-50 hover:text-purple-700 transition-all duration-200 shadow-sm hover:shadow-md border-2 border-gray-200 hover:border-purple-300",
                children: action.label
            }, action.label, false, {
                fileName: "[project]/components/Chat/QuickActions.tsx",
                lineNumber: 19,
                columnNumber: 9
            }, this))
    }, void 0, false, {
        fileName: "[project]/components/Chat/QuickActions.tsx",
        lineNumber: 17,
        columnNumber: 5
    }, this);
}
_c = QuickActions;
var _c;
__turbopack_context__.k.register(_c, "QuickActions");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/Chat/RelatedBlogs.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>RelatedBlogs
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
'use client';
;
const blogLinks = [
    {
        title: '🔋 バッテリー・バッテリーの故障と修理方法',
        url: 'https://camper-repair.net/blog/repair1/'
    },
    {
        title: '🛠️ 基本修理・キャンピングカー修理の基本',
        url: 'https://camper-repair.net/blog/risk1/'
    },
    {
        title: '🔍 定期点検・定期点検とメンテナンス',
        url: 'https://camper-repair.net/battery-selection/'
    }
];
function RelatedBlogs() {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "bg-gray-50 border-l-4 border-purple-600 rounded-lg p-5 mb-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                className: "text-purple-600 font-bold text-lg mb-4",
                children: "📚 関連ブログ"
            }, void 0, false, {
                fileName: "[project]/components/Chat/RelatedBlogs.tsx",
                lineNumber: 21,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "text-gray-600 mb-4 text-sm",
                children: "より詳しい情報は修理ブログ一覧をご覧ください。"
            }, void 0, false, {
                fileName: "[project]/components/Chat/RelatedBlogs.tsx",
                lineNumber: 22,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex flex-col gap-3",
                children: blogLinks.map((blog, index)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("a", {
                        href: blog.url,
                        target: "_blank",
                        rel: "noopener noreferrer",
                        className: "text-purple-600 hover:text-purple-800 hover:underline transition-colors text-sm font-medium",
                        children: blog.title
                    }, index, false, {
                        fileName: "[project]/components/Chat/RelatedBlogs.tsx",
                        lineNumber: 27,
                        columnNumber: 11
                    }, this))
            }, void 0, false, {
                fileName: "[project]/components/Chat/RelatedBlogs.tsx",
                lineNumber: 25,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/Chat/RelatedBlogs.tsx",
        lineNumber: 20,
        columnNumber: 5
    }, this);
}
_c = RelatedBlogs;
var _c;
__turbopack_context__.k.register(_c, "RelatedBlogs");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/Chat/ChatWindow.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ChatWindow
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$MessageList$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/Chat/MessageList.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$MessageInput$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/Chat/MessageInput.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$TabNavigation$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/Chat/TabNavigation.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$QuickActions$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/Chat/QuickActions.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$RelatedBlogs$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/Chat/RelatedBlogs.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
'use client';
;
;
;
;
;
;
;
function ChatWindow() {
    _s();
    const [messages, setMessages] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [activeTab, setActiveTab] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('chat');
    const [sessionId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        "ChatWindow.useState": ()=>{
            // セッションIDを生成（ブラウザのローカルストレージから取得または新規作成）
            if ("TURBOPACK compile-time truthy", 1) {
                const stored = localStorage.getItem('chat_session_id');
                if (stored) return stored;
                const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                localStorage.setItem('chat_session_id', newId);
                return newId;
            }
            //TURBOPACK unreachable
            ;
        }
    }["ChatWindow.useState"]);
    const messagesEndRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    // メッセージリストの最後にスクロール
    const scrollToBottom = ()=>{
        messagesEndRef.current?.scrollIntoView({
            behavior: 'smooth'
        });
    };
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ChatWindow.useEffect": ()=>{
            scrollToBottom();
        }
    }["ChatWindow.useEffect"], [
        messages
    ]);
    // 会話開始
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ChatWindow.useEffect": ()=>{
            const startConversation = {
                "ChatWindow.useEffect.startConversation": async ()=>{
                    try {
                        await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["chatApi"].startConversation(sessionId);
                        // 初期メッセージを追加
                        const welcomeMessage = {
                            id: `msg_${Date.now()}_welcome`,
                            text: '🔧 キャンピングカー修理チャットボットにようこそ！\n修理について何でもお聞きください。AI診断、詳細検索、費用相談など、あらゆる機能を統合しています。',
                            sender: 'system',
                            timestamp: new Date()
                        };
                        setMessages([
                            welcomeMessage
                        ]);
                    } catch (error) {
                        console.error('会話開始エラー:', error);
                    }
                }
            }["ChatWindow.useEffect.startConversation"];
            startConversation();
        }
    }["ChatWindow.useEffect"], [
        sessionId
    ]);
    // タブ変更時の処理
    const handleTabChange = (tab)=>{
        setActiveTab(tab);
        if (tab === 'repair_advice') {
            // 修理アドバイスセンターの場合は別ページに遷移
            if ("TURBOPACK compile-time truthy", 1) {
                window.location.href = '/repair-advice';
            }
        }
    };
    // クイックメッセージ送信
    const handleQuickMessage = (message)=>{
        handleSend(message);
    };
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
            const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["chatApi"].sendMessage(text, sessionId);
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
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col h-full",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$TabNavigation$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                activeTab: activeTab,
                onTabChange: handleTabChange
            }, void 0, false, {
                fileName: "[project]/components/Chat/ChatWindow.tsx",
                lineNumber: 148,
                columnNumber: 7
            }, this),
            (activeTab === 'chat' || activeTab === 'diagnostic') && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$QuickActions$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                onQuickMessage: handleQuickMessage
            }, void 0, false, {
                fileName: "[project]/components/Chat/ChatWindow.tsx",
                lineNumber: 152,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex-1 overflow-hidden",
                children: [
                    activeTab === 'chat' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$MessageList$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                messages: messages
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 159,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                ref: messagesEndRef
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 160,
                                columnNumber: 13
                            }, this),
                            messages.length <= 1 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$RelatedBlogs$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 162,
                                columnNumber: 38
                            }, this)
                        ]
                    }, void 0, true),
                    activeTab === 'diagnostic' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "text-center py-8 text-gray-600",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "text-lg mb-4",
                                children: "🔍 症状診断機能"
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 167,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                children: "症状を詳しく教えてください。AIが原因を特定します。"
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 168,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$MessageList$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                messages: messages
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 169,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                ref: messagesEndRef
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 170,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/Chat/ChatWindow.tsx",
                        lineNumber: 166,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/Chat/ChatWindow.tsx",
                lineNumber: 156,
                columnNumber: 7
            }, this),
            (activeTab === 'chat' || activeTab === 'diagnostic') && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-4",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$MessageInput$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                    onSend: handleSend,
                    disabled: isLoading
                }, void 0, false, {
                    fileName: "[project]/components/Chat/ChatWindow.tsx",
                    lineNumber: 178,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/Chat/ChatWindow.tsx",
                lineNumber: 177,
                columnNumber: 9
            }, this),
            isLoading && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center justify-center gap-2 mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex gap-1",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-2 h-2 bg-blue-500 rounded-full animate-bounce",
                                style: {
                                    animationDelay: '0ms'
                                }
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 186,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-2 h-2 bg-blue-500 rounded-full animate-bounce",
                                style: {
                                    animationDelay: '150ms'
                                }
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 187,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "w-2 h-2 bg-blue-500 rounded-full animate-bounce",
                                style: {
                                    animationDelay: '300ms'
                                }
                            }, void 0, false, {
                                fileName: "[project]/components/Chat/ChatWindow.tsx",
                                lineNumber: 188,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/Chat/ChatWindow.tsx",
                        lineNumber: 185,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-blue-600 font-medium",
                        children: "AIが考えています..."
                    }, void 0, false, {
                        fileName: "[project]/components/Chat/ChatWindow.tsx",
                        lineNumber: 190,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-blue-400 text-sm",
                        children: "（通常10-30秒かかります）"
                    }, void 0, false, {
                        fileName: "[project]/components/Chat/ChatWindow.tsx",
                        lineNumber: 191,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/Chat/ChatWindow.tsx",
                lineNumber: 184,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/Chat/ChatWindow.tsx",
        lineNumber: 146,
        columnNumber: 5
    }, this);
}
_s(ChatWindow, "nM7Uqj/cma4vR7ewxjwPJpW1HSo=");
_c = ChatWindow;
var _c;
__turbopack_context__.k.register(_c, "ChatWindow");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/Navigation.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>Navigation
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
'use client';
;
;
function Navigation() {
    _s();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const navLinks = [
        {
            href: '/',
            label: '🏠 ホーム',
            icon: '🏠'
        },
        {
            href: '/chat',
            label: '💬 チャット',
            icon: '💬'
        },
        {
            href: '/partner',
            label: '🔧 修理店紹介',
            icon: '🔧'
        },
        {
            href: '/factory',
            label: '🏭 工場ダッシュボード',
            icon: '🏭'
        },
        {
            href: '/admin',
            label: '⚙️ 管理者画面',
            icon: '⚙️'
        }
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
        className: "bg-white/95 backdrop-blur-sm rounded-lg shadow-md p-4 mb-6",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex flex-wrap gap-2 justify-center items-center",
            children: navLinks.map((link)=>{
                const isActive = pathname === link.href;
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                    href: link.href,
                    className: `px-4 py-2 rounded-lg font-semibold transition-all ${isActive ? 'bg-purple-600 text-white shadow-lg' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`,
                    children: link.label
                }, link.href, false, {
                    fileName: "[project]/components/Navigation.tsx",
                    lineNumber: 23,
                    columnNumber: 13
                }, this);
            })
        }, void 0, false, {
            fileName: "[project]/components/Navigation.tsx",
            lineNumber: 19,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/Navigation.tsx",
        lineNumber: 18,
        columnNumber: 5
    }, this);
}
_s(Navigation, "xbyQPtUVMO7MNj7WjJlpdWqRcTo=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"]
    ];
});
_c = Navigation;
var _c;
__turbopack_context__.k.register(_c, "Navigation");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/chat/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ChatPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$ChatWindow$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/Chat/ChatWindow.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Navigation$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/Navigation.tsx [app-client] (ecmascript)");
'use client';
;
;
;
;
function ChatPage() {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "min-h-screen bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 p-4",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "max-w-6xl mx-auto",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Navigation$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                    fileName: "[project]/app/chat/page.tsx",
                    lineNumber: 12,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "bg-white/95 backdrop-blur-sm rounded-2xl p-8 mb-6 shadow-xl text-center",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                            className: "text-3xl font-bold text-purple-600 mb-2",
                            children: "🔧 キャンピングカー修理チャットボット"
                        }, void 0, false, {
                            fileName: "[project]/app/chat/page.tsx",
                            lineNumber: 16,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-gray-600 text-lg mb-4",
                            children: "AI診断 + リアルタイム情報 + 専門知識 = 修理支援"
                        }, void 0, false, {
                            fileName: "[project]/app/chat/page.tsx",
                            lineNumber: 19,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex justify-center gap-4 flex-wrap",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                    href: "/partner",
                                    className: "inline-block px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-semibold",
                                    children: "🔧 修理店を探す"
                                }, void 0, false, {
                                    fileName: "[project]/app/chat/page.tsx",
                                    lineNumber: 23,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                    href: "/lp-partner-recruit",
                                    className: "inline-block px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-semibold",
                                    children: "🏭 パートナー募集"
                                }, void 0, false, {
                                    fileName: "[project]/app/chat/page.tsx",
                                    lineNumber: 29,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/app/chat/page.tsx",
                            lineNumber: 22,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/app/chat/page.tsx",
                    lineNumber: 15,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "bg-white/95 backdrop-blur-sm rounded-2xl p-6 shadow-xl min-h-[600px]",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$Chat$2f$ChatWindow$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                        fileName: "[project]/app/chat/page.tsx",
                        lineNumber: 40,
                        columnNumber: 11
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/app/chat/page.tsx",
                    lineNumber: 39,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/app/chat/page.tsx",
            lineNumber: 10,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/chat/page.tsx",
        lineNumber: 9,
        columnNumber: 5
    }, this);
}
_c = ChatPage;
var _c;
__turbopack_context__.k.register(_c, "ChatPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_befde679._.js.map