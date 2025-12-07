/**
 * 構造化データ（JSON-LD）コンポーネント
 * SEO向上のための構造化データを提供
 */

interface StructuredDataProps {
  type: 'Organization' | 'WebSite' | 'FAQPage' | 'Article' | 'BreadcrumbList';
  data: Record<string, any>;
}

export default function StructuredData({ type, data }: StructuredDataProps) {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';

  const getStructuredData = () => {
    switch (type) {
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
            availableLanguage: 'Japanese',
          },
          sameAs: data.sameAs || [
            'https://camper-repair.net/blog/',
          ],
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
              urlTemplate: `${baseUrl}/chat?q={search_term_string}`,
            },
            'query-input': 'required name=search_term_string',
          },
        };

      case 'FAQPage':
        return {
          '@context': 'https://schema.org',
          '@type': 'FAQPage',
          mainEntity: data.faqs || [],
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
            name: 'キャンピングカー修理サポートセンター',
          },
          publisher: {
            '@type': 'Organization',
            name: 'キャンピングカー修理サポートセンター',
            logo: {
              '@type': 'ImageObject',
              url: `${baseUrl}/logo.png`,
            },
          },
        };

      case 'BreadcrumbList':
        return {
          '@context': 'https://schema.org',
          '@type': 'BreadcrumbList',
          itemListElement: data.items || [],
        };

      default:
        return {};
    }
  };

  const structuredData = getStructuredData();

  if (!structuredData || Object.keys(structuredData).length === 0) {
    return null;
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}

