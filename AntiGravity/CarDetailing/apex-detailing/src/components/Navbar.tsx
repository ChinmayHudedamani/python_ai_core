"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X, Shield } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { name: "Home", href: "/" },
    { name: "About", href: "/#about" },
    { name: "Services", href: "/services" },
    { name: "Reviews", href: "/reviews" },
    { name: "Packages", href: "/#packages" },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 w-full z-50 transition-all duration-500 border-b ${
        scrolled
          ? "bg-[#0a0a0a]/90 backdrop-blur-lg border-white/10 shadow-[0_4px_30px_rgba(0,0,0,0.5)]"
          : "bg-transparent border-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-24">
          <Link href="/" className="flex-shrink-0 flex items-center gap-3 cursor-pointer group">
            <div className="w-10 h-10 rounded-sm bg-[#dc2d13] flex items-center justify-center group-hover:scale-105 transition-transform">
              <Shield className="text-white w-5 h-5" />
            </div>
            <span className="text-white font-heading font-extrabold text-2xl tracking-wider uppercase">
              King of Detailing
            </span>
          </Link>

          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-10">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className="text-gray-300 hover:text-[#dc2d13] transition-colors px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] relative after:content-[''] after:absolute after:w-0 after:h-[2px] after:bg-[#dc2d13] after:left-1/2 after:-translate-x-1/2 after:-bottom-1 hover:after:w-full after:transition-all after:duration-300"
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>

          <div className="hidden md:block">
            <Link href="/services">
              <button className="relative overflow-hidden bg-transparent border border-[#dc2d13] text-white hover:text-white transition-colors duration-300 px-8 py-3 rounded-none text-xs font-bold uppercase tracking-[0.2em] cursor-pointer group">
                <span className="absolute inset-0 w-full h-full bg-[#dc2d13] -translate-x-full group-hover:translate-x-0 transition-transform duration-300 ease-out -z-10" />
                <span className="relative z-10">Book Now</span>
              </button>
            </Link>
          </div>

          <div className="-mr-2 flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5 focus:outline-none cursor-pointer"
            >
              <span className="sr-only">Open main menu</span>
              {isOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#1a1a1a] border-t border-white/10 overflow-hidden"
          >
            <div className="px-4 pt-2 pb-6 space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className="text-gray-300 hover:text-white block px-3 py-4 text-sm font-semibold uppercase tracking-[0.2em] border-b border-white/5"
                  onClick={() => setIsOpen(false)}
                >
                  {link.name}
                </Link>
              ))}
              <div className="pt-6 pb-2">
                <button className="w-full bg-[#dc2d13] text-white transition-all duration-300 px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] cursor-pointer">
                  Book Now
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
