"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Check, Minus } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

import { packages, features } from "@/data/packages";

export default function Packages() {
  const sectionRef = useRef<HTMLElement>(null);
  const tableRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        tableRef.current,
        { y: 50, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 1,
          ease: "power4.out",
          scrollTrigger: {
            trigger: tableRef.current,
            start: "top 85%",
          },
        }
      );
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="packages" className="py-32 bg-[#0a0a0a] relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center max-w-3xl mx-auto mb-24">
          <h2 className="font-heading text-4xl md:text-5xl font-bold uppercase tracking-tight mb-4 text-white">
            Compare <span className="text-[#dc2d13]">Packages</span>
          </h2>
          <p className="text-gray-400 font-sans text-lg">
            Transparent pricing. Elite results. Find the perfect transformation for your vehicle.
          </p>
        </div>

        <div ref={tableRef} className="overflow-x-auto pb-8">
          <div className="min-w-[800px]">
            {/* Headers (Sticky) */}
            <div className="grid grid-cols-4 gap-4 sticky top-24 bg-[#0a0a0a] z-30 pb-6 border-b border-white/10">
              <div className="col-span-1" /> {/* Empty corner */}
              
              {packages.map((pkg) => (
                <div key={pkg.id} className="col-span-1 text-center flex flex-col items-center">
                  {pkg.isPopular && (
                    <span className="text-[#dc2d13] text-xs font-bold uppercase tracking-widest mb-2">
                      Most Popular
                    </span>
                  )}
                  <h3 className="font-heading text-2xl font-bold text-white uppercase tracking-wider mb-2">
                    {pkg.name}
                  </h3>
                  <div className="text-3xl font-bold text-white mb-2">
                    {pkg.price}
                  </div>
                  <p className="text-gray-500 text-sm h-10 mb-4">{pkg.positioning}</p>
                  <button className={`w-full max-w-[160px] py-3 text-xs font-bold uppercase tracking-[0.2em] transition-all duration-300 ${
                    pkg.isPopular 
                      ? 'bg-[#dc2d13] text-white hover:bg-[#ff3b1f]' 
                      : 'bg-transparent border border-white/20 text-white hover:border-[#dc2d13] hover:text-[#dc2d13]'
                  }`}>
                    Book Now
                  </button>
                </div>
              ))}
            </div>

            {/* Feature Rows */}
            <div className="mt-8">
              {features.map((category) => (
                <div key={category.category} className="mb-12">
                  <div className="grid grid-cols-4 gap-4 border-b border-white/10 pb-4 mb-4">
                    <h4 className="col-span-4 font-heading text-xl font-bold text-white uppercase tracking-wider">
                      {category.category}
                    </h4>
                  </div>
                  
                  {category.items.map((item, index) => (
                    <div 
                      key={item.name} 
                      className={`grid grid-cols-4 gap-4 py-4 transition-colors hover:bg-white/5 ${index !== category.items.length - 1 ? 'border-b border-white/5' : ''}`}
                    >
                      <div className="col-span-1 flex items-center text-gray-300 text-sm font-medium pl-4">
                        {item.name}
                      </div>
                      {item.values.map((hasFeature, i) => (
                        <div key={i} className="col-span-1 flex items-center justify-center">
                          {hasFeature ? (
                            <Check className="w-5 h-5 text-[#dc2d13]" />
                          ) : (
                            <Minus className="w-5 h-5 text-gray-700" />
                          )}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ))}
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}
