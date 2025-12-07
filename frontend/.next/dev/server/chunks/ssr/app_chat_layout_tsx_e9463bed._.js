module.exports = [
"[project]/app/chat/layout.tsx [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ChatLayout,
    "metadata",
    ()=>metadata
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/rsc/react-jsx-dev-runtime.js [app-rsc] (ecmascript)");
;
const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';
const metadata = {
    title: 'チャット - AI修理サポート',
    description: 'キャンピングカーの症状を入力するだけで、AIが原因を特定し、専門的な修理アドバイスを提供します。24時間対応、無料診断。',
    openGraph: {
        title: 'チャット - AI修理サポート | キャンピングカー修理チャットボット',
        description: 'キャンピングカーの症状を入力するだけで、AIが原因を特定し、専門的な修理アドバイスを提供します。',
        url: `${baseUrl}/chat`
    }
};
function ChatLayout({ children }) {
    // FAQPage構造化データ
    const faqData = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: [
            {
                '@type': 'Question',
                name: 'キャンピングカーの修理はどこでできますか？',
                acceptedAnswer: {
                    '@type': 'Answer',
                    text: '岡山キャンピングカー修理サポートセンターで対応しています。電話番号：086-206-6622、営業時間：平日 9:00〜18:00 | 土日祝 10:00〜17:00'
                }
            },
            {
                '@type': 'Question',
                name: 'AIチャットボットで何ができますか？',
                acceptedAnswer: {
                    '@type': 'Answer',
                    text: '症状を入力するだけで、AIが原因を特定し、専門的な修理アドバイスを提供します。24時間対応、無料診断・見積り対応。'
                }
            }
        ]
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["Fragment"], {
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("script", {
                type: "application/ld+json",
                dangerouslySetInnerHTML: {
                    __html: JSON.stringify(faqData)
                }
            }, void 0, false, {
                fileName: "[project]/app/chat/layout.tsx",
                lineNumber: 46,
                columnNumber: 7
            }, this),
            children
        ]
    }, void 0, true);
}
}),
];

//# sourceMappingURL=app_chat_layout_tsx_e9463bed._.js.map