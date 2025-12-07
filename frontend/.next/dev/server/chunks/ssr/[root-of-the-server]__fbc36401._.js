module.exports = [
"[next]/internal/font/google/geist_a71539c9.module.css [app-rsc] (css module)", ((__turbopack_context__) => {

__turbopack_context__.v({
  "className": "geist_a71539c9-module__T19VSG__className",
  "variable": "geist_a71539c9-module__T19VSG__variable",
});
}),
"[next]/internal/font/google/geist_a71539c9.js [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>__TURBOPACK__default__export__
]);
var __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_a71539c9$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__ = __turbopack_context__.i("[next]/internal/font/google/geist_a71539c9.module.css [app-rsc] (css module)");
;
const fontData = {
    className: __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_a71539c9$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__["default"].className,
    style: {
        fontFamily: "'Geist', 'Geist Fallback'",
        fontStyle: "normal"
    }
};
if (__TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_a71539c9$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__["default"].variable != null) {
    fontData.variable = __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_a71539c9$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__["default"].variable;
}
const __TURBOPACK__default__export__ = fontData;
}),
"[next]/internal/font/google/geist_mono_8d43a2aa.module.css [app-rsc] (css module)", ((__turbopack_context__) => {

__turbopack_context__.v({
  "className": "geist_mono_8d43a2aa-module__8Li5zG__className",
  "variable": "geist_mono_8d43a2aa-module__8Li5zG__variable",
});
}),
"[next]/internal/font/google/geist_mono_8d43a2aa.js [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>__TURBOPACK__default__export__
]);
var __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_mono_8d43a2aa$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__ = __turbopack_context__.i("[next]/internal/font/google/geist_mono_8d43a2aa.module.css [app-rsc] (css module)");
;
const fontData = {
    className: __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_mono_8d43a2aa$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__["default"].className,
    style: {
        fontFamily: "'Geist Mono', 'Geist Mono Fallback'",
        fontStyle: "normal"
    }
};
if (__TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_mono_8d43a2aa$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__["default"].variable != null) {
    fontData.variable = __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_mono_8d43a2aa$2e$module$2e$css__$5b$app$2d$rsc$5d$__$28$css__module$29$__["default"].variable;
}
const __TURBOPACK__default__export__ = fontData;
}),
"[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/SEO/StructuredData.tsx [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 構造化データ（JSON-LD）コンポーネント
 * SEO向上のための構造化データを提供
 */ __turbopack_context__.s([
    "default",
    ()=>StructuredData
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/rsc/react-jsx-dev-runtime.js [app-rsc] (ecmascript)");
;
function StructuredData({ type, data }) {
    const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';
    const getStructuredData = ()=>{
        switch(type){
            case 'Organization':
                return {
                    '@context': 'https://schema.org',
                    '@type': 'Organization',
                    name: data.name || 'キャンピングカー修理サポートセンター',
                    url: data.url || baseUrl,
                    logo: data.logo || `${baseUrl}/logo.png`,
                    contactPoint: {
                        '@type': 'ContactPoint',
                        telephone: data.telephone || '+81-86-206-6622',
                        contactType: 'customer service',
                        areaServed: 'JP',
                        availableLanguage: 'Japanese'
                    },
                    sameAs: data.sameAs || [
                        'https://camper-repair.net/blog/'
                    ]
                };
            case 'WebSite':
                return {
                    '@context': 'https://schema.org',
                    '@type': 'WebSite',
                    name: data.name || 'キャンピングカー修理チャットボット',
                    url: data.url || baseUrl,
                    description: data.description || 'AI搭載のキャンピングカー修理サポートシステム',
                    potentialAction: {
                        '@type': 'SearchAction',
                        target: {
                            '@type': 'EntryPoint',
                            urlTemplate: `${baseUrl}/chat?q={search_term_string}`
                        },
                        'query-input': 'required name=search_term_string'
                    }
                };
            case 'FAQPage':
                return {
                    '@context': 'https://schema.org',
                    '@type': 'FAQPage',
                    mainEntity: data.faqs || []
                };
            case 'Article':
                return {
                    '@context': 'https://schema.org',
                    '@type': 'Article',
                    headline: data.headline,
                    description: data.description,
                    image: data.image,
                    datePublished: data.datePublished,
                    dateModified: data.dateModified || data.datePublished,
                    author: {
                        '@type': 'Organization',
                        name: 'キャンピングカー修理サポートセンター'
                    },
                    publisher: {
                        '@type': 'Organization',
                        name: 'キャンピングカー修理サポートセンター',
                        logo: {
                            '@type': 'ImageObject',
                            url: `${baseUrl}/logo.png`
                        }
                    }
                };
            case 'BreadcrumbList':
                return {
                    '@context': 'https://schema.org',
                    '@type': 'BreadcrumbList',
                    itemListElement: data.items || []
                };
            default:
                return {};
        }
    };
    const structuredData = getStructuredData();
    if (!structuredData || Object.keys(structuredData).length === 0) {
        return null;
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("script", {
        type: "application/ld+json",
        dangerouslySetInnerHTML: {
            __html: JSON.stringify(structuredData)
        }
    }, void 0, false, {
        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/SEO/StructuredData.tsx",
        lineNumber: 101,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/app/layout.tsx [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>RootLayout,
    "metadata",
    ()=>metadata
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/rsc/react-jsx-dev-runtime.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_a71539c9$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[next]/internal/font/google/geist_a71539c9.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_mono_8d43a2aa$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[next]/internal/font/google/geist_mono_8d43a2aa.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$components$2f$SEO$2f$StructuredData$2e$tsx__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/components/SEO/StructuredData.tsx [app-rsc] (ecmascript)");
;
;
;
;
;
const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';
const metadata = {
    metadataBase: new URL(baseUrl),
    title: {
        default: "キャンピングカー修理チャットボット | AI搭載の修理サポート",
        template: "%s | キャンピングカー修理チャットボット"
    },
    description: "AI搭載のキャンピングカー修理サポートシステム。症状を入力するだけで、専門的な修理アドバイスを提供します。24時間対応、無料診断・見積り対応。",
    keywords: [
        "キャンピングカー",
        "修理",
        "メンテナンス",
        "チャットボット",
        "AI",
        "診断",
        "トラブルシューティング",
        "RV",
        "キャンピングカー修理",
        "岡山"
    ],
    authors: [
        {
            name: "キャンピングカー修理サポートセンター"
        }
    ],
    creator: "キャンピングカー修理サポートセンター",
    publisher: "キャンピングカー修理サポートセンター",
    formatDetection: {
        email: false,
        address: false,
        telephone: false
    },
    openGraph: {
        type: "website",
        locale: "ja_JP",
        url: baseUrl,
        siteName: "キャンピングカー修理チャットボット",
        title: "キャンピングカー修理チャットボット | AI搭載の修理サポート",
        description: "AI搭載のキャンピングカー修理サポートシステム。症状を入力するだけで、専門的な修理アドバイスを提供します。",
        images: [
            {
                url: `${baseUrl}/og-image.png`,
                width: 1200,
                height: 630,
                alt: "キャンピングカー修理チャットボット"
            }
        ]
    },
    twitter: {
        card: "summary_large_image",
        title: "キャンピングカー修理チャットボット | AI搭載の修理サポート",
        description: "AI搭載のキャンピングカー修理サポートシステム。症状を入力するだけで、専門的な修理アドバイスを提供します。",
        images: [
            `${baseUrl}/og-image.png`
        ]
    },
    robots: {
        index: true,
        follow: true,
        googleBot: {
            index: true,
            follow: true,
            "max-video-preview": -1,
            "max-image-preview": "large",
            "max-snippet": -1
        }
    },
    verification: {
    }
};
function RootLayout({ children }) {
    const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("html", {
        lang: "ja",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("head", {
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$components$2f$SEO$2f$StructuredData$2e$tsx__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["default"], {
                        type: "Organization",
                        data: {
                            name: "キャンピングカー修理サポートセンター",
                            url: baseUrl,
                            telephone: "+81-86-206-6622",
                            sameAs: [
                                "https://camper-repair.net/blog/"
                            ]
                        }
                    }, void 0, false, {
                        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/app/layout.tsx",
                        lineNumber: 95,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$components$2f$SEO$2f$StructuredData$2e$tsx__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["default"], {
                        type: "WebSite",
                        data: {
                            name: "キャンピングカー修理チャットボット",
                            url: baseUrl,
                            description: "AI搭載のキャンピングカー修理サポートシステム"
                        }
                    }, void 0, false, {
                        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/app/layout.tsx",
                        lineNumber: 105,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/app/layout.tsx",
                lineNumber: 93,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$udemy$2d$langchain$2f$camper$2d$repair$2d$clean$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])("body", {
                className: `${__TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_a71539c9$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["default"].variable} ${__TURBOPACK__imported__module__$5b$next$5d2f$internal$2f$font$2f$google$2f$geist_mono_8d43a2aa$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["default"].variable} antialiased`,
                children: children
            }, void 0, false, {
                fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/app/layout.tsx",
                lineNumber: 114,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/app/layout.tsx",
        lineNumber: 92,
        columnNumber: 5
    }, this);
}
}),
"[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/rsc/react-jsx-dev-runtime.js [app-rsc] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/Desktop/udemy-langchain/camper-repair-clean/frontend/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-rsc] (ecmascript)").vendored['react-rsc'].ReactJsxDevRuntime; //# sourceMappingURL=react-jsx-dev-runtime.js.map
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__fbc36401._.js.map