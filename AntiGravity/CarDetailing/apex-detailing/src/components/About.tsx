"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Shield, Sparkles, Award } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

export default function About() {
  const sectionRef = useRef<HTMLElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Fade in text content from the left
      gsap.fromTo(
        contentRef.current,
        { x: -50, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 1.2,
          ease: "power4.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 70%",
          },
        }
      );

      // Fade in image from the right with a slight scale down
      gsap.fromTo(
        imageRef.current,
        { x: 50, opacity: 0, scale: 1.05 },
        {
          x: 0,
          opacity: 1,
          scale: 1,
          duration: 1.5,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 70%",
          },
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="about" className="py-24 bg-[#050505] relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-transparent to-[#0a0a0a] pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
          {/* Text Content */}
          <div ref={contentRef} className="space-y-8">
            <div className="inline-flex items-center gap-3 px-4 py-1.5 border border-[#dc2d13]/30 bg-[#dc2d13]/10 backdrop-blur-md">
              <span className="w-2 h-2 bg-[#dc2d13] shadow-[0_0_8px_#dc2d13]" />
              <span className="text-white text-xs font-semibold uppercase tracking-[0.3em]">Our Ethos</span>
            </div>
            
            <h2 className="font-heading text-4xl md:text-5xl font-bold uppercase tracking-tight text-white leading-tight">
              Driven by <span className="text-[#dc2d13]">Passion.</span><br />
              Defined by <span className="text-[#dc2d13]">Precision.</span>
            </h2>
            
            <div className="space-y-6 text-gray-400 font-sans font-light text-lg leading-relaxed">
              <p>
                At King of Detailing, we believe that an automobile is more than just transportation—it is a mechanical work of art. Our journey began with a singular obsession: to push the boundaries of automotive aesthetics and deliver a level of perfection that surpasses showroom standards.
              </p>
              <p>
                Founded by <strong className="text-white font-medium">Mr. Acchu</strong>, a master detailer with years of relentless dedication to the craft, our studio was built on the principle that true detailing cannot be rushed. We don't believe in quick washes or temporary glazes. We believe in meticulous restoration, permanent correction, and advanced ceramic protection.
              </p>
              <p className="border-l-2 border-[#dc2d13] pl-6 italic text-gray-300">
                "Our motto is simple: Every vehicle that enters our studio is treated as if it were our own. No compromises, no shortcuts. Just pure, unadulterated perfection."
              </p>
            </div>

            <div className="grid grid-cols-2 gap-6 pt-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#dc2d13]/10 border border-[#dc2d13]/20 flex items-center justify-center">
                  <Award className="w-6 h-6 text-[#dc2d13]" />
                </div>
                <div>
                  <h4 className="text-white font-bold uppercase tracking-wider text-sm">Master</h4>
                  <p className="text-gray-500 text-xs uppercase tracking-widest">Technicians</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#dc2d13]/10 border border-[#dc2d13]/20 flex items-center justify-center">
                  <Shield className="w-6 h-6 text-[#dc2d13]" />
                </div>
                <div>
                  <h4 className="text-white font-bold uppercase tracking-wider text-sm">Premium</h4>
                  <p className="text-gray-500 text-xs uppercase tracking-widest">Materials</p>
                </div>
              </div>
            </div>
          </div>

          {/* Image Content */}
          <div ref={imageRef} className="relative h-[600px] w-full border border-white/10 group overflow-hidden">
            <div className="absolute inset-0 bg-[#dc2d13]/20 mix-blend-overlay z-10 group-hover:bg-transparent transition-colors duration-700" />
            <img 
              src="https://images.unsplash.com/photo-1600706432502-77a0e2e32766?q=80&w=2070&auto=format&fit=crop" 
              alt="Detailing Craftsman"
              className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-1000"
            />
            
            {/* Floating Badge */}
            <div className="absolute bottom-10 left-10 z-20 bg-black/80 backdrop-blur-md border border-white/10 p-6 flex items-center gap-6">
              <Sparkles className="w-8 h-8 text-[#dc2d13]" />
              <div>
                <div className="text-3xl font-heading font-bold text-white mb-1">5.0</div>
                <div className="text-xs text-gray-400 uppercase tracking-widest">Google Rating</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
