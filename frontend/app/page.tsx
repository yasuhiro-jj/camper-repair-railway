import CategoryGrid from "./components/CategoryGrid";
import Container from "./components/Container";
import DiagnosisCTA from "./components/DiagnosisCTA";
import FeaturedPosts from "./components/FeaturedPosts";
import FooterCTA from "./components/FooterCTA";
import Hero from "./components/Hero";
import LatestPosts from "./components/LatestPosts";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <Container className="space-y-16">
        <Hero />
        <CategoryGrid />
        <DiagnosisCTA />
        <FeaturedPosts />
        <LatestPosts />
        <FooterCTA />
      </Container>
    </main>
  );
}
