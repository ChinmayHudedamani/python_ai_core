"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface ServiceFeatureSlideProps {
  step: string;
  title: string;
  description: string;
  imageSrc: string;
  reverse?: boolean;
}

export default function ServiceFeatureSlide({ step, title, description, imageSrc, reverse = false }: ServiceFeatureSlideProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Text reveal on scroll
      gsap.fromTo(
        textRef.current,
        { y: 100, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 1,
          ease: "power4.out",
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top 75%",
          },
        }
      );

      // Image parallax / zoom reveal
      gsap.fromTo(
        imageRef.current,
        { scale: 1.2, opacity: 0 },
        {
          scale: 1,
          opacity: 1,
          duration: 1.5,
          ease: "power3.out",
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top 75%",
          },
        }
      );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="w-full min-h-[80vh] flex items-center py-24 relative overflow-hidden bg-[#0a0a0a]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className={`flex flex-col gap-12 lg:gap-24 items-center ${reverse ? 'lg:flex-row-reverse' : 'lg:flex-row'}`}>
          
          {/* Text Content */}
          <div ref={textRef} className="w-full lg:w-1/2 flex flex-col justify-center">
            <span className="text-[#dc2d13] font-bold tracking-[0.2em] uppercase text-sm mb-4 block">
              Step {step}
            </span>
            <h2 className="font-heading text-4xl md:text-5xl font-bold uppercase tracking-tight text-white mb-6">
              {title}
            </h2>
            <p className="text-gray-400 font-sans text-lg font-light leading-relaxed">
              {description}
            </p>
          </div>

          {/* Image Content */}
          <div className="w-full lg:w-1/2 h-[50vh] lg:h-[60vh] relative overflow-hidden group">
            <div 
              ref={imageRef}
              className="absolute inset-0 w-full h-full bg-cover bg-center"
              style={{ backgroundImage: `url(${imageSrc})` }}
            />
            {/* Subtle overlay gradient */}
            <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-transparent opacity-80" />
            <div className="absolute inset-0 border border-white/10 group-hover:border-[#dc2d13]/50 transition-colors duration-700 pointer-events-none" />
          </div>

        </div>
      </div>
    </div>
  );
}
