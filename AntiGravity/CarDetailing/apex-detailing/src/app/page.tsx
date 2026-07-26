import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import About from "@/components/About";
import Packages from "@/components/Packages";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <Hero />
      <About />
      <Packages />
      <Footer />
    </main>
  );
}
