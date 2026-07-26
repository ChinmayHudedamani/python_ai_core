export interface ServiceFeature {
  step: string;
  title: string;
  description: string;
  imageSrc: string;
}

export interface ServiceData {
  slug: string;
  title: string;
  subtitle: string;
  heroImage: string;
  features: ServiceFeature[];
}

export const servicesData: ServiceData[] = [
  {
    slug: "paint-correction",
    title: "Paint Correction",
    subtitle: "We eliminate swirl marks, scratches, and oxidation to restore a flawless, mirror-like finish to your vehicle's clear coat.",
    heroImage: "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Decontamination",
        description: "Before any machine touches the paint, we perform a rigorous chemical and mechanical decontamination. Iron removers and clay bars extract embedded industrial fallout, brake dust, and tar, leaving the surface glass-smooth and ready for correction.",
        imageSrc: "https://images.unsplash.com/photo-1600706432502-77a0e2e32766?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Heavy Compounding",
        description: "Using dual-action polishers and specialized cutting compounds, we safely level the clear coat. This stage permanently removes deep scratches, wash-induced swirl marks, and severe oxidation that dull your vehicle's true color.",
        imageSrc: "https://images.unsplash.com/photo-1610647752706-3bb12232b3ab?q=80&w=2025&auto=format&fit=crop"
      },
      {
        step: "03",
        title: "Jeweling & Refinement",
        description: "The final stage involves ultra-fine polishes and soft finishing pads. This 'jewels' the paint, maximizing optical clarity and producing a wet, mirror-like gloss that prepares the surface perfectly for a Ceramic Shield application.",
        imageSrc: "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?q=80&w=2069&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "ceramic-shield",
    title: "Ceramic Shield",
    subtitle: "Advanced 9H nanotechnology that bonds to your paint, providing years of extreme gloss and unmatched protection against the elements.",
    heroImage: "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Surface Preparation",
        description: "The secret to a flawless ceramic coating lies in the prep work. We meticulously decontaminate and polish the clear coat to perfection, ensuring the nano-ceramic particles can bond directly to the bare paint structure without interference.",
        imageSrc: "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "9H Nano Bonding",
        description: "We hand-apply the liquid polymer in a climate-controlled environment. The coating chemically bonds with the factory clear coat, curing into a rigid super-structure that acts as a sacrificial layer of protection against UV rays, bird droppings, and chemical etching.",
        imageSrc: "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "03",
        title: "Extreme Hydrophobics",
        description: "Once cured, our Ceramic Shield creates intense surface tension. Water, mud, and road grime instantly bead up and roll off the paint, making future washing effortless and keeping your car cleaner for much longer.",
        imageSrc: "https://images.unsplash.com/photo-1616789124449-335df7a192bb?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "interior-spa",
    title: "Interior Spa",
    subtitle: "Deep hot-water extraction, premium leather conditioning, and comprehensive sanitization to make your interior feel factory-new.",
    heroImage: "https://images.unsplash.com/photo-1616789124449-335df7a192bb?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Deep Extraction",
        description: "We utilize industrial-grade hot water extractors and specialized fabric shampoos to pull years of embedded dirt, stains, and allergens from your carpets and cloth upholstery, restoring their original texture and color.",
        imageSrc: "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Leather Rejuvenation",
        description: "Your vehicle's leather undergoes a pH-balanced deep clean to remove body oils and dye transfer. We then apply a premium conditioning serum that nourishes the hide, restoring its supple, matte factory finish and preventing future cracking.",
        imageSrc: "https://images.unsplash.com/photo-1600706432502-77a0e2e32766?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "03",
        title: "Odor Eradication",
        description: "Instead of just masking smells, we deploy an ozone generator that oxidizes and destroys odor-causing bacteria, smoke molecules, and pet smells at the molecular level, leaving the cabin smelling genuinely clean and fresh.",
        imageSrc: "https://images.unsplash.com/photo-1610647752706-3bb12232b3ab?q=80&w=2025&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "body-and-trim",
    title: "Body & Trim Restoration",
    subtitle: "Complete rejuvenation of your vehicle's exterior plastics, chrome, and trim elements to factory perfection.",
    heroImage: "https://images.unsplash.com/photo-1550524514-eb05e3f42296?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Plastic Rehydration",
        description: "Faded, sun-bleached plastics are treated with specialized ceramic trim restorers that penetrate deep into the pores of the material, returning them to a rich, deep black finish that won't wash off.",
        imageSrc: "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Chrome Polishing",
        description: "Exhaust tips, grilles, and window trims are carefully polished using micro-abrasives to remove oxidation, pitting, and exhaust carbon, restoring a brilliant mirror shine.",
        imageSrc: "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "painting",
    title: "Premium Auto Painting",
    subtitle: "From panel blending to full resprays, we deliver flawless, factory-matched finishes using the highest quality paint systems.",
    heroImage: "https://images.unsplash.com/photo-1620612185591-628d097960fc?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Digital Color Matching",
        description: "We utilize advanced spectrophotometers to read your vehicle's exact current paint code and fade level, ensuring an invisible blend between new and original panels.",
        imageSrc: "https://images.unsplash.com/photo-1610647752706-3bb12232b3ab?q=80&w=2025&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Climate-Controlled Spraying",
        description: "All painting is performed in state-of-the-art downdraft spray booths. This eliminates dust contamination and provides the perfect environment for the base coat and clear coat to atomize and lay flat.",
        imageSrc: "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?q=80&w=2069&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "steering-and-suspension",
    title: "Steering & Suspension",
    subtitle: "Restore your vehicle's handling, stability, and ride comfort with our expert suspension diagnostics and repairs.",
    heroImage: "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?q=80&w=2072&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Dynamic Diagnostics",
        description: "We inspect shocks, struts, tie rods, and ball joints for wear and play. A healthy suspension system is critical not just for ride comfort, but for safe braking distances and tire longevity.",
        imageSrc: "https://images.unsplash.com/photo-1600706432502-77a0e2e32766?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Precision Alignment",
        description: "After any suspension component replacement, we perform a laser-guided 4-wheel alignment to ensure your steering wheel is dead straight and your vehicle tracks perfectly down the highway.",
        imageSrc: "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "tyres-and-brakes",
    title: "Tyres & Brakes",
    subtitle: "High-performance stopping power and grip. We offer premium brake pad replacement, rotor resurfacing, and tire balancing.",
    heroImage: "https://images.unsplash.com/photo-1580273916550-e323be2ae537?q=80&w=1964&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Brake System Overhaul",
        description: "From ceramic, low-dust brake pads to cross-drilled rotors, we ensure your vehicle stops as well as it accelerates. We also flush and replace brake fluid to prevent vapor lock during heavy braking.",
        imageSrc: "https://images.unsplash.com/photo-1616789124449-335df7a192bb?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Road Force Balancing",
        description: "We don't just mount tires; we use Road Force balancing technology to simulate the weight of the car on the tire, eliminating micro-vibrations at highway speeds for a remarkably smooth ride.",
        imageSrc: "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "exhaust-and-transmission",
    title: "Exhaust & Transmission",
    subtitle: "Maximize your vehicle's performance and efficiency with expert transmission servicing and custom exhaust fabrication.",
    heroImage: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=2083&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Transmission Fluid Flush",
        description: "Old transmission fluid breaks down and loses its hydraulic properties. We perform complete system flushes, replacing the filter and fluid to ensure crisp, smooth gear shifts and prolong transmission life.",
        imageSrc: "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Exhaust Flow Optimization",
        description: "Whether repairing a leak or installing a high-flow performance exhaust, we ensure optimal back-pressure and flow, resulting in better throttle response and a deeper, more aggressive exhaust note.",
        imageSrc: "https://images.unsplash.com/photo-1610647752706-3bb12232b3ab?q=80&w=2025&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "air-conditioning",
    title: "Air Conditioning Service",
    subtitle: "Stay cool in the summer heat. We diagnose leaks, recharge refrigerant, and sanitize your HVAC system.",
    heroImage: "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?q=80&w=2069&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Leak Detection & Recharge",
        description: "Using UV dye and electronic sniffers, we locate microscopic leaks in your A/C system. Once repaired, we evacuate the system in a deep vacuum and recharge it with exact factory specifications of refrigerant and compressor oil.",
        imageSrc: "https://images.unsplash.com/photo-1600706432502-77a0e2e32766?q=80&w=2070&auto=format&fit=crop"
      },
      {
        step: "02",
        title: "Evaporator Sanitization",
        description: "Musty smells from the vents are caused by mold buildup on the evaporator core. We inject an anti-microbial foam directly into the HVAC housing to kill bacteria and restore crisp, clean air flow.",
        imageSrc: "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "engine-diagnostic",
    title: "Engine Diagnostic",
    subtitle: "Advanced computer diagnostics to quickly pinpoint check-engine lights, misfires, and performance issues.",
    heroImage: "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?q=80&w=2072&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "OBD2 Telemetry Scanning",
        description: "We connect to your vehicle's ECU to read live data streams, freeze-frame data, and diagnostic trouble codes (DTCs), eliminating guesswork and allowing us to pinpoint the exact failing sensor or component.",
        imageSrc: "https://images.unsplash.com/photo-1610647752706-3bb12232b3ab?q=80&w=2025&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "battery-and-electrical",
    title: "Battery & Electrical",
    subtitle: "From dead batteries to complex wiring shorts, we resolve electrical gremlins that compromise your vehicle's reliability.",
    heroImage: "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Parasitic Draw Testing",
        description: "If your battery keeps dying overnight, we use multimeters and thermal imaging to locate the module or circuit that is staying awake and draining your power.",
        imageSrc: "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "oil-change",
    title: "Premium Oil Change",
    subtitle: "More than a quick lube. We use full synthetic oils and OEM filters to maximize engine longevity and performance.",
    heroImage: "https://images.unsplash.com/photo-1620612185591-628d097960fc?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Synthetic Lubrication",
        description: "We strictly use high-grade, full-synthetic motor oils tailored to your engine's specific tolerances. This prevents sludge buildup, reduces internal friction, and ensures cold-start protection.",
        imageSrc: "https://images.unsplash.com/photo-1616789124449-335df7a192bb?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "classic-cars",
    title: "Classic Car Restoration",
    subtitle: "Specialized, delicate care for vintage and classic automobiles requiring specialized knowledge and period-correct parts.",
    heroImage: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=2083&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Sympathetic Restoration",
        description: "We understand that classic cars have single-stage paint, carburetors, and unique electrical systems. Our technicians treat vintage metal with the extreme care and expertise it deserves.",
        imageSrc: "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?q=80&w=2069&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "welding",
    title: "Custom Welding",
    subtitle: "TIG and MIG welding services for exhaust fabrication, rust repair, and structural chassis reinforcement.",
    heroImage: "https://images.unsplash.com/photo-1580273916550-e323be2ae537?q=80&w=1964&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "Precision Metalwork",
        description: "Whether patching rust on a rocker panel or fabricating custom exhaust piping, our master welders ensure strong, clean beads that look as good as they perform.",
        imageSrc: "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=2070&auto=format&fit=crop"
      }
    ]
  },
  {
    slug: "complete-car-care",
    title: "Complete Car Care",
    subtitle: "The ultimate bumper-to-bumper reset. We combine mechanical servicing with deep detailing for total vehicle rejuvenation.",
    heroImage: "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?q=80&w=2070&auto=format&fit=crop",
    features: [
      {
        step: "01",
        title: "The Reset Process",
        description: "Leave your car with us for a comprehensive overhaul. From fluid flushes and brake pad replacement to a multi-stage paint correction and interior deep clean, we return your car feeling brand new.",
        imageSrc: "https://images.unsplash.com/photo-1610647752706-3bb12232b3ab?q=80&w=2025&auto=format&fit=crop"
      }
    ]
  }
];
