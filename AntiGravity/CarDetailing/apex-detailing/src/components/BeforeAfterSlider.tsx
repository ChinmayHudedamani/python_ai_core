"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronsLeftRight } from "lucide-react";

interface BeforeAfterSliderProps {
  beforeImage: string;
  afterImage: string;
}

export default function BeforeAfterSlider({ beforeImage, afterImage }: BeforeAfterSliderProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    handleMove(e.touches[0].clientX);
  };

  const handlePointerDown = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDragging(true);
    if ('clientX' in e) {
      handleMove(e.clientX);
    } else {
      handleMove(e.touches[0].clientX);
    }
  };

  useEffect(() => {
    const handleMouseUp = () => setIsDragging(false);
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("touchend", handleMouseUp);
    return () => {
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchend", handleMouseUp);
    };
  }, []);

  return (
    <div className="relative w-full max-w-5xl mx-auto rounded-2xl overflow-hidden shadow-2xl border border-white/10 group">
      <div
        ref={containerRef}
        className="relative w-full aspect-[16/9] sm:aspect-[21/9] cursor-ew-resize select-none"
        onMouseMove={handleMouseMove}
        onTouchMove={handleTouchMove}
        onMouseDown={handlePointerDown}
        onTouchStart={handlePointerDown}
      >
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${beforeImage})` }}
        >
          <div className="absolute inset-0 bg-black/20" />
          <span className="absolute bottom-4 left-4 bg-black/70 backdrop-blur-sm text-white px-3 py-1 text-sm font-bold tracking-widest uppercase rounded">
            Before
          </span>
        </div>

        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${afterImage})`,
            clipPath: `inset(0 ${100 - sliderPosition}% 0 0)`,
          }}
        >
          <span className="absolute bottom-4 right-4 bg-neon/90 text-black px-3 py-1 text-sm font-bold tracking-widest uppercase rounded">
            After
          </span>
        </div>

        <div
          className="absolute top-0 bottom-0 w-1 bg-neon shadow-[0_0_10px_#00E5FF] flex items-center justify-center z-10 transition-shadow"
          style={{ left: `${sliderPosition}%`, transform: "translateX(-50%)" }}
        >
          <motion.div
            animate={
              isDragging
                ? { scale: 1.2, backgroundColor: "#fff" }
                : { scale: 1, backgroundColor: "#00E5FF" }
            }
            className="w-10 h-10 rounded-full flex items-center justify-center shadow-lg border-2 border-black"
          >
            <ChevronsLeftRight className="text-black w-6 h-6" />
          </motion.div>
        </div>
      </div>
    </div>
  );
}
