import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { servicesData } from "@/data/services";

export default function ServicesPage() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col relative">
      <Navbar />
      
      <section className="pt-40 pb-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#1a1a1a]/50 to-transparent pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-20 animate-in fade-in slide-in-from-bottom-10 duration-1000">
            <h1 className="font-heading text-4xl md:text-6xl font-bold uppercase tracking-tight mb-6 text-white">
              Our Complete <span className="text-[#dc2d13]">Services</span>
            </h1>
            <p className="text-gray-400 font-sans text-lg md:text-xl font-light leading-relaxed">
              Explore our full suite of premium detailing, restoration, and mechanical services. We bring perfection to every inch of your vehicle.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {servicesData.map((service, index) => (
              <Link 
                href={`/services/${service.slug}`}
                key={service.slug}
                className="bg-[#1a1a1a] border border-white/5 group relative overflow-hidden flex flex-col cursor-pointer animate-in fade-in slide-in-from-bottom-8 duration-700"
                style={{ animationDelay: `${index * 50}ms`, animationFillMode: 'both' }}
              >
                <div className="h-48 w-full relative overflow-hidden">
                  <div className="absolute inset-0 bg-black/20 z-10 group-hover:bg-transparent transition-colors duration-500" />
                  <img 
                    src={service.heroImage} 
                    alt={service.title}
                    className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-700"
                  />
                </div>
                
                <div className="p-8 flex flex-col flex-grow">
                  <h3 className="font-heading text-xl font-bold text-white uppercase tracking-wider mb-4 group-hover:text-[#dc2d13] transition-colors">
                    {service.title}
                  </h3>
                  <p className="text-gray-400 font-sans font-light leading-relaxed mb-8 flex-grow text-sm line-clamp-3">
                    {service.subtitle}
                  </p>
                  
                  <div className="flex items-center gap-2 text-[#dc2d13] font-bold text-xs tracking-widest uppercase mt-auto">
                    View Details 
                    <ArrowRight className="w-4 h-4 transform group-hover:translate-x-2 transition-transform duration-300" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
