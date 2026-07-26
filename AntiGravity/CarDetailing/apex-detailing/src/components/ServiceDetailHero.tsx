"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ChevronDown } from "lucide-react";

interface ServiceDetailHeroProps {
  title: string;
  subtitle: string;
  videoSrc?: string;
  imageSrc?: string;
}

export default function ServiceDetailHero({ title, subtitle, videoSrc, imageSrc }: ServiceDetailHeroProps) {
  const heroRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Background slow zoom
      const bg = heroRef.current?.querySelector('.hero-bg');
      if (bg) {
        gsap.fromTo(bg, { scale: 1 }, { scale: 1.1, duration: 15, ease: "none" });
      }

      // Text reveal
      const elements = textRef.current?.querySelectorAll('.hero-animate');
      if (elements) {
        gsap.fromTo(
          elements,
          { y: 50, opacity: 0 },
          { y: 0, opacity: 1, duration: 1, stagger: 0.15, ease: "power4.out", delay: 0.2 }
        );
      }
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={heroRef} className="relative w-full h-[80vh] overflow-hidden bg-[#0a0a0a]">
      <div className="absolute inset-0 w-full h-full overflow-hidden hero-bg">
        {videoSrc ? (
          <video 
            autoPlay 
            muted 
            loop 
            playsInline 
            className="absolute inset-0 w-full h-full object-cover opacity-60"
          >
            <source src={videoSrc} type="video/mp4" />
          </video>
        ) : (
          <div 
            className="absolute inset-0 w-full h-full bg-cover bg-center opacity-60"
            style={{ backgroundImage: `url(${imageSrc})` }}
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/50 to-[#0a0a0a]/30" />
      </div>

      <div className="relative z-20 h-full flex flex-col justify-end max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        <div ref={textRef} className="max-w-4xl">
          <div className="hero-animate overflow-hidden mb-4">
            <span className="text-[#dc2d13] font-bold tracking-[0.3em] uppercase text-sm">Signature Process</span>
          </div>
          <h1 className="hero-animate font-heading text-5xl md:text-8xl font-extrabold text-white mb-6 uppercase tracking-tight">
            {title}
          </h1>
          <p className="hero-animate text-gray-300 text-lg md:text-xl max-w-2xl font-light leading-relaxed">
            {subtitle}
          </p>
        </div>
      </div>

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-30 animate-bounce">
        <ChevronDown className="w-8 h-8 text-white/50" />
      </div>
    </section>
  );
}
