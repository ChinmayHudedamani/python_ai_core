"use client";

import Link from "next/link";
import { MapPin, Phone, Clock, Shield, Mail } from "lucide-react";
import { servicesData } from "@/data/services";

export default function Footer() {
  return (
    <footer className="bg-[#050505] border-t border-white/10 pt-24 pb-12 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-[#dc2d13]/5 via-transparent to-transparent pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 lg:gap-8 mb-16">
          
          {/* Brand & About */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-sm bg-[#dc2d13] flex items-center justify-center">
                <Shield className="text-white w-5 h-5" />
              </div>
              <span className="text-white font-heading font-extrabold text-2xl tracking-wider uppercase">
                King of Detailing
              </span>
            </div>
            <p className="text-gray-400 font-sans font-light leading-relaxed mb-8">
              Bengaluru's premier auto detailing, paint correction, and body shop. We restore pride and showroom brilliance to your daily drive.
            </p>
            <div className="flex gap-4">
              <a href="#" className="w-10 h-10 rounded-full border border-white/20 flex items-center justify-center text-white hover:bg-[#dc2d13] hover:border-[#dc2d13] transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
              </a>
              <a href="#" className="w-10 h-10 rounded-full border border-white/20 flex items-center justify-center text-white hover:bg-[#dc2d13] hover:border-[#dc2d13] transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
              </a>
              <a href="#" className="w-10 h-10 rounded-full border border-white/20 flex items-center justify-center text-white hover:bg-[#dc2d13] hover:border-[#dc2d13] transition-colors">
                <Mail className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Contact Info */}
          <div className="lg:col-span-1">
            <h4 className="font-heading text-white font-bold uppercase tracking-wider mb-6">Visit Us</h4>
            <ul className="space-y-6">
              <li className="flex items-start gap-4 text-gray-400">
                <MapPin className="w-5 h-5 text-[#dc2d13] shrink-0 mt-1" />
                <span className="font-light leading-relaxed text-sm">
                  Opposite to TVS Emerland Auralis Apt, next to Reva College Main Road, Yelankha, Srinivasa Nagar, Sathanur, Bengaluru, Karnataka 560064
                </span>
              </li>
              <li className="flex items-center gap-4 text-gray-400">
                <Phone className="w-5 h-5 text-[#dc2d13] shrink-0" />
                <span className="font-light">099020 57985</span>
              </li>
              <li className="flex items-center gap-4 text-gray-400">
                <Clock className="w-5 h-5 text-[#dc2d13] shrink-0" />
                <span className="font-light">Open Daily • Closes 9 PM</span>
              </li>
            </ul>
          </div>

          {/* Services (Split into two columns for styling) */}
          <div className="lg:col-span-2">
            <h4 className="font-heading text-white font-bold uppercase tracking-wider mb-6">Our Services</h4>
            <div className="grid grid-cols-2 gap-4">
              <ul className="space-y-3">
                {servicesData.slice(3, 9).map(service => (
                  <li key={service.slug}>
                    <Link href={`/services/${service.slug}`} className="text-gray-400 text-sm font-light hover:text-[#dc2d13] transition-colors cursor-pointer block">
                      {service.title}
                    </Link>
                  </li>
                ))}
              </ul>
              <ul className="space-y-3">
                {servicesData.slice(9, 15).map(service => (
                  <li key={service.slug}>
                    <Link href={`/services/${service.slug}`} className="text-gray-400 text-sm font-light hover:text-[#dc2d13] transition-colors cursor-pointer block">
                      {service.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

        </div>

        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-600 text-xs font-light tracking-wider uppercase">
            &copy; {new Date().getFullYear()} King of Detailing. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-gray-600 text-xs font-light tracking-wider uppercase hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="text-gray-600 text-xs font-light tracking-wider uppercase hover:text-white transition-colors">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
