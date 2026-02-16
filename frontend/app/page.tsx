import CategoryGrid from "./components/CategoryGrid";
import Container from "./components/Container";
import DiagnosisCTA from "./components/DiagnosisCTA";
import FeaturedPosts from "./components/FeaturedPosts";
import FooterCTA from "./components/FooterCTA";
import Hero from "./components/Hero";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <Container className="space-y-16">
        <Hero />
        <CategoryGrid />
        <DiagnosisCTA />
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-slate-900">よく読まれている記事</h2>
        </section>
        <FeaturedPosts />
        <FooterCTA />
      </Container>
    </main>
  );
}
