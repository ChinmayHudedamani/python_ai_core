"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Star } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

import { reviews } from "@/data/testimonials";

export default function Testimonials() {
  const sectionRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
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

      gsap.fromTo(
        cardsRef.current,
        { y: 50, opacity: 0 },
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
    <section ref={sectionRef} id="reviews" className="py-32 bg-[#0a0a0a] relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#1a1a1a] via-[#0a0a0a] to-[#0a0a0a] pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        <div ref={headerRef} className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-flex items-center gap-2 mb-6">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star key={star} className="w-6 h-6 fill-[#dc2d13] text-[#dc2d13]" />
            ))}
          </div>
          <h2 className="font-heading text-4xl md:text-5xl font-bold uppercase tracking-tight mb-4 text-white">
            5.0 Stars on <span className="text-[#dc2d13]">Google</span>
          </h2>
          <p className="text-gray-400 font-sans text-lg">
            Don't just take our word for it. See what our clients have to say about the King of Detailing experience.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {reviews.map((review, index) => (
            <div 
              key={review.id}
              ref={(el) => { cardsRef.current[index] = el; }}
              className="bg-black border border-white/10 p-8 hover:border-[#dc2d13]/30 transition-colors duration-500 relative group flex flex-col justify-between"
            >
              <div>
                <div className="flex gap-1 mb-6">
                  {[...Array(review.rating)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-[#dc2d13] text-[#dc2d13]" />
                  ))}
                </div>
                <p className="text-gray-300 font-sans font-light leading-relaxed mb-8 italic">
                  "{review.text}"
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#1a1a1a] border border-white/10 flex items-center justify-center font-bold text-white uppercase">
                  {review.author.charAt(0)}
                </div>
                <div>
                  <h4 className="font-bold text-white text-sm uppercase tracking-wider">{review.author}</h4>
                  <span className="text-xs text-gray-500 uppercase tracking-widest">Local Guide / Customer</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
