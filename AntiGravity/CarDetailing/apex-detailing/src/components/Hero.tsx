"use client";

import { useEffect, useRef, useState, TouchEvent } from "react";
import { gsap } from "gsap";
import { ChevronRight, ChevronLeft } from "lucide-react";

import { slides } from "@/data/hero";

export default function Hero() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const heroRef = useRef<HTMLDivElement>(null);
  const slideRefs = useRef<(HTMLDivElement | null)[]>([]);
  const textRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);
  const [mouseStart, setMouseStart] = useState<number | null>(null);
  const [mouseEnd, setMouseEnd] = useState<number | null>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    const distance = touchStart - touchEnd;
    if (distance > minSwipeDistance) nextSlide();
    if (distance < -minSwipeDistance) prevSlide();
  };

  const onMouseDown = (e: React.MouseEvent) => {
    setMouseEnd(null);
    setMouseStart(e.clientX);
  };

  const onMouseMove = (e: React.MouseEvent) => {
    if (mouseStart !== null) {
      setMouseEnd(e.clientX);
    }
  };

  const onMouseUp = () => {
    if (!mouseStart || !mouseEnd) {
      setMouseStart(null);
      setMouseEnd(null);
      return;
    }
    const distance = mouseStart - mouseEnd;
    if (distance > minSwipeDistance) nextSlide();
    if (distance < -minSwipeDistance) prevSlide();
    setMouseStart(null);
    setMouseEnd(null);
  };

  const onMouseLeave = () => {
    setMouseStart(null);
    setMouseEnd(null);
  };

  const nextSlide = () => {
    if (isAnimating) return;
    setCurrentSlide((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
  };

  const prevSlide = () => {
    if (isAnimating) return;
    setCurrentSlide((prev) => (prev === 0 ? slides.length - 1 : prev - 1));
  };

  useEffect(() => {
    const timer = setInterval(() => {
      if (!isAnimating) {
        setCurrentSlide((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
      }
    }, 4000); // Faster interval as requested
    return () => clearInterval(timer);
  }, [isAnimating]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      setIsAnimating(true);
      
      gsap.set(slideRefs.current, { zIndex: 0, opacity: 0 });
      gsap.set(slideRefs.current[currentSlide], { zIndex: 10, opacity: 1 });
      
      const currentBg = slideRefs.current[currentSlide]?.querySelector('.bg-image');
      if (currentBg) {
        gsap.fromTo(currentBg, 
          { scale: 1 }, 
          { scale: 1.1, duration: 10, ease: "none" }
        );
      }

      const currentText = textRefs.current[currentSlide];
      if (currentText) {
        const elements = currentText.querySelectorAll('.hero-animate');
        gsap.fromTo(
          elements,
          { y: 50, opacity: 0 },
          { y: 0, opacity: 1, duration: 1, stagger: 0.15, ease: "power4.out", delay: 0.1, onComplete: () => setIsAnimating(false) }
        );
      } else {
        setIsAnimating(false);
      }

    }, heroRef);

    return () => ctx.revert();
  }, [currentSlide]);

  return (
    <section 
      ref={heroRef} 
      className="relative w-full h-screen overflow-hidden bg-[#0a0a0a] cursor-grab active:cursor-grabbing"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseLeave}
    >
      {slides.map((slide, index) => (
        <div 
          key={slide.id}
          ref={(el) => { slideRefs.current[index] = el; }}
          className="absolute inset-0 w-full h-full opacity-0 pointer-events-none"
        >
          <div className="absolute inset-0 w-full h-full overflow-hidden bg-[#0a0a0a]">
            <div 
              className="bg-image absolute inset-0 w-full h-full bg-cover bg-center pointer-events-none"
              style={{ backgroundImage: `url(${slide.image})` }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0a] via-[#0a0a0a]/80 to-transparent z-10 pointer-events-none" />
            <div className="absolute inset-0 bg-black/40 z-10 pointer-events-none" />
          </div>

          <div className="relative z-20 h-full flex flex-col justify-center max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pointer-events-none">
            <div ref={(el) => { textRefs.current[index] = el; }} className="max-w-3xl mt-20">
              
              <div className="hero-animate overflow-hidden mb-4">
                <div className="inline-flex items-center gap-3 px-4 py-1.5 border border-[#dc2d13]/30 bg-[#dc2d13]/10 backdrop-blur-md">
                  <span className="w-2 h-2 bg-[#dc2d13] shadow-[0_0_8px_#dc2d13]" />
                  <span className="text-white text-xs font-semibold uppercase tracking-[0.3em]">Premium Detailing</span>
                </div>
              </div>

              <h1 className="font-heading text-6xl md:text-8xl font-bold text-white mb-6 leading-[0.9] tracking-tight uppercase">
                <div className="hero-animate overflow-hidden">
                  <span>{slide.title}</span>
                </div>
                <div className="hero-animate overflow-hidden">
                  <span className="text-[#dc2d13]">{slide.titleHighlight}</span>
                </div>
              </h1>
              
              <div className="hero-animate overflow-hidden mb-10">
                <p className="text-gray-300 text-lg md:text-xl max-w-xl leading-relaxed font-sans font-light">
                  {slide.subtitle}
                </p>
              </div>

              <div className="hero-animate flex flex-col sm:flex-row gap-6 pointer-events-auto">
                <button className="relative overflow-hidden bg-[#dc2d13] text-white transition-all duration-300 px-10 py-4 rounded-none font-bold uppercase tracking-[0.2em] text-sm group">
                  <span className="absolute inset-0 w-full h-full bg-white/20 -translate-x-full group-hover:translate-x-0 transition-transform duration-300 ease-out" />
                  <span className="relative z-10 flex items-center justify-center gap-3">
                    View Packages
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
              </div>

            </div>
          </div>
        </div>
      ))}

      <div className="absolute bottom-10 right-10 z-30 flex items-center gap-4 pointer-events-auto">
        <div className="text-white font-heading text-xl font-bold tracking-widest mr-4 select-none">
          0{currentSlide + 1} <span className="text-gray-600">/ 0{slides.length}</span>
        </div>
        <button 
          onClick={(e) => { e.stopPropagation(); prevSlide(); }}
          disabled={isAnimating}
          className="w-12 h-12 border border-white/20 flex items-center justify-center text-white hover:bg-[#dc2d13] hover:border-[#dc2d13] transition-colors disabled:opacity-50 cursor-pointer"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <button 
          onClick={(e) => { e.stopPropagation(); nextSlide(); }}
          disabled={isAnimating}
          className="w-12 h-12 border border-white/20 flex items-center justify-center text-white hover:bg-[#dc2d13] hover:border-[#dc2d13] transition-colors disabled:opacity-50 cursor-pointer"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center pb-8 hidden md:flex pointer-events-none">
        <span className="text-white/50 text-[10px] uppercase tracking-[0.3em] mb-4 rotate-90 origin-left translate-y-6">Scroll</span>
        <div className="w-[1px] h-16 bg-white/20 relative overflow-hidden">
          <div className="w-full h-full bg-[#dc2d13] absolute top-0 left-0 animate-[scrolldown_2s_ease-in-out_infinite]" />
        </div>
      </div>
    </section>
  );
}
