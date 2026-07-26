import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Testimonials from "@/components/Testimonials";

export default function ReviewsPage() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col relative">
      <Navbar />
      
      {/* Add top padding so the navbar doesn't overlap the component */}
      <div className="pt-20">
        <Testimonials />
      </div>

      <Footer />
    </main>
  );
}
