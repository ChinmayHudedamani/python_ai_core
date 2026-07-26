"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Link from "next/link";
import { Sparkles, Shield, Droplets, ArrowRight } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

import { servicesData } from "@/data/services";

const serviceIcons = [
  <Sparkles key="sparkles" className="w-8 h-8 text-[#dc2d13]" />,
  <Shield key="shield" className="w-8 h-8 text-[#dc2d13]" />,
  <Droplets key="droplets" className="w-8 h-8 text-[#dc2d13]" />
];

export default function Services() {
  const sectionRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLAnchorElement | null)[]>([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Header Animation
      gsap.fromTo(
        headerRef.current,
        { y: 50, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 1,
          ease: "power4.out",
          scrollTrigger: {
            trigger: headerRef.current,
            start: "top 80%",
          },
        }
      );

      // Cards Stagger Animation
      gsap.fromTo(
        cardsRef.current,
        { y: 100, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 1,
          stagger: 0.2,
          ease: "power4.out",
          scrollTrigger: {
            trigger: headerRef.current, 
            start: "top 60%",
          },
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="services" className="py-32 bg-[#0a0a0a] relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#1a1a1a]/50 to-transparent pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        <div ref={headerRef} className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="font-heading text-4xl md:text-6xl font-bold uppercase tracking-tight mb-6 text-white">
            Beyond A Simple <span className="text-[#dc2d13]">Wash.</span>
          </h2>
          <p className="text-gray-400 font-sans text-lg md:text-xl font-light leading-relaxed">
            We don't just clean cars; we restore, protect, and elevate them. Our detailing processes are engineered to provide long-lasting, immaculate results.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {servicesData.slice(0, 3).map((service, index) => (
            <Link 
              href={`/services/${service.slug}`}
              key={service.title}
              ref={(el) => { cardsRef.current[index] = el; }}
              className="bg-[#1a1a1a] border border-white/5 p-10 hover:border-[#dc2d13]/50 transition-colors duration-500 group relative overflow-hidden flex flex-col cursor-pointer"
            >
              <div className="w-16 h-16 bg-black flex items-center justify-center mb-8 border border-white/10 group-hover:bg-[#dc2d13]/10 transition-colors duration-500">
                {serviceIcons[index]}
              </div>
              <h3 className="font-heading text-2xl font-bold text-white uppercase tracking-wider mb-4">
                {service.title}
              </h3>
              <p className="text-gray-400 font-sans font-light leading-relaxed mb-8 flex-grow">
                {service.subtitle}
              </p>
              
              <div className="flex items-center gap-2 text-[#dc2d13] font-bold text-sm tracking-widest uppercase">
                Explore Service 
                <ArrowRight className="w-4 h-4 transform group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
