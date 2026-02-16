import {
  Navbar,
  HeroSection,
  FeaturesSection,
  HowItWorksSection,
  AIHighlightSection,
  CTASection,
  Footer
} from '@/components/landing';

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900">
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <AIHighlightSection />
      <CTASection />
      <Footer />
    </main>
  );
}
