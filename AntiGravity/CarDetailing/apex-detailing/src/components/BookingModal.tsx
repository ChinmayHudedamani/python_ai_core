"use client";

import { useState, useEffect } from "react";
import { X, CheckCircle2, ChevronRight } from "lucide-react";
import { gsap } from "gsap";

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialService: string;
}

export default function BookingModal({ isOpen, onClose, initialService }: BookingModalProps) {
  const [step, setStep] = useState(1);
  const [vehicle, setVehicle] = useState("");
  const [date, setDate] = useState("");

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      gsap.fromTo(".modal-overlay", { opacity: 0 }, { opacity: 1, duration: 0.3 });
      gsap.fromTo(".modal-content", { y: 50, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, delay: 0.1, ease: "power3.out" });
    } else {
      document.body.style.overflow = 'auto';
      setStep(1); // reset on close
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleNext = () => setStep(s => s + 1);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="modal-overlay absolute inset-0 bg-black/80 backdrop-blur-md"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="modal-content relative bg-[#0f0f0f] border border-white/10 w-full max-w-2xl rounded-sm shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="p-6 border-b border-white/5 flex items-center justify-between bg-black/50">
          <div>
            <span className="text-[#dc2d13] text-xs font-bold tracking-[0.2em] uppercase">Booking Request</span>
            <h3 className="text-white font-heading text-xl font-bold uppercase tracking-wider">{initialService}</h3>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-8 overflow-y-auto">
          {/* Step 1: Vehicle Type */}
          {step === 1 && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-500">
              <h4 className="text-white font-heading text-2xl mb-6">Select Vehicle Type</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {['Sedan / Coupe', 'SUV / Truck', 'Exotic / Classic'].map(type => (
                  <div 
                    key={type}
                    onClick={() => setVehicle(type)}
                    className={`p-6 border cursor-pointer transition-all duration-300 text-center flex flex-col items-center gap-3 ${vehicle === type ? 'border-[#dc2d13] bg-[#dc2d13]/5' : 'border-white/10 hover:border-white/30 bg-[#1a1a1a]'}`}
                  >
                    <div className={`w-3 h-3 rounded-full ${vehicle === type ? 'bg-[#dc2d13]' : 'bg-gray-600'}`} />
                    <span className="text-sm font-bold text-gray-200">{type}</span>
                  </div>
                ))}
              </div>
              <div className="mt-10 flex justify-end">
                <button 
                  disabled={!vehicle}
                  onClick={handleNext}
                  className="bg-white text-black px-8 py-3 text-sm font-bold tracking-widest uppercase hover:bg-gray-200 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  Continue <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Date & Time */}
          {step === 2 && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-500">
              <h4 className="text-white font-heading text-2xl mb-6">Preferred Schedule</h4>
              <div className="space-y-6">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Select Date</label>
                  <input 
                    type="date" 
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full bg-[#1a1a1a] border border-white/10 p-4 text-white focus:outline-none focus:border-[#dc2d13] transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Preferred Time Slot</label>
                  <select className="w-full bg-[#1a1a1a] border border-white/10 p-4 text-white focus:outline-none focus:border-[#dc2d13] transition-colors appearance-none">
                    <option>Morning (8AM - 12PM)</option>
                    <option>Afternoon (12PM - 4PM)</option>
                    <option>Evening (4PM - 8PM)</option>
                  </select>
                </div>
              </div>
              <div className="mt-10 flex justify-between">
                <button onClick={() => setStep(1)} className="text-gray-500 hover:text-white text-sm font-bold tracking-widest uppercase">Back</button>
                <button 
                  disabled={!date}
                  onClick={handleNext}
                  className="bg-white text-black px-8 py-3 text-sm font-bold tracking-widest uppercase hover:bg-gray-200 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  Continue <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Contact Details */}
          {step === 3 && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-500">
              <h4 className="text-white font-heading text-2xl mb-6">Your Details</h4>
              <div className="space-y-4">
                <input type="text" placeholder="Full Name" className="w-full bg-[#1a1a1a] border border-white/10 p-4 text-white focus:outline-none focus:border-[#dc2d13]" />
                <input type="email" placeholder="Email Address" className="w-full bg-[#1a1a1a] border border-white/10 p-4 text-white focus:outline-none focus:border-[#dc2d13]" />
                <input type="tel" placeholder="Phone Number" className="w-full bg-[#1a1a1a] border border-white/10 p-4 text-white focus:outline-none focus:border-[#dc2d13]" />
              </div>
              <div className="mt-10 flex justify-between">
                <button onClick={() => setStep(2)} className="text-gray-500 hover:text-white text-sm font-bold tracking-widest uppercase">Back</button>
                <button onClick={handleNext} className="bg-[#dc2d13] text-white px-8 py-3 text-sm font-bold tracking-widest uppercase hover:bg-[#ff3b1f] transition-colors">
                  Confirm Booking
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Success */}
          {step === 4 && (
            <div className="animate-in fade-in zoom-in duration-500 text-center py-12">
              <CheckCircle2 className="w-20 h-20 text-[#dc2d13] mx-auto mb-6" />
              <h4 className="text-white font-heading text-3xl mb-4 uppercase tracking-wider">Request Received</h4>
              <p className="text-gray-400 font-light max-w-md mx-auto mb-8">
                Thank you. We have received your booking request for <strong>{initialService}</strong> for your {vehicle}. Our concierge team will contact you shortly to confirm your appointment.
              </p>
              <button onClick={onClose} className="border border-white/20 text-white px-8 py-3 text-sm font-bold tracking-widest uppercase hover:bg-white hover:text-black transition-colors">
                Return to Site
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
