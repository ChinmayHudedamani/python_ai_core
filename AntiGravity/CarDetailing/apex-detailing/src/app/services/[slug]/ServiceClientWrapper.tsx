"use client";

import { useState } from "react";
import BookingModal from "@/components/BookingModal";

export default function ServiceClientWrapper({ serviceTitle }: { serviceTitle: string }) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <section className="py-24 bg-[#050505] text-center border-t border-white/10 mt-12 relative z-10">
        <h3 className="font-heading text-3xl font-bold text-white uppercase tracking-wider mb-6">
          Ready to Book?
        </h3>
        <p className="text-gray-400 mb-8 max-w-xl mx-auto font-sans font-light">
          Book your <strong className="text-white font-bold">{serviceTitle}</strong> service today and experience the King of Detailing transformation.
        </p>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-[#dc2d13] text-white px-10 py-4 font-bold uppercase tracking-[0.2em] text-sm hover:bg-[#ff3b1f] transition-colors"
        >
          Book Now
        </button>
      </section>

      <BookingModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        initialService={serviceTitle} 
      />
    </>
  );
}
