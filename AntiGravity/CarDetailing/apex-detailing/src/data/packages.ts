export const packages = [
  {
    id: "express",
    name: "Express Refresh",
    price: "₹1,499",
    positioning: "Quick, essential maintenance.",
    isPopular: false,
  },
  {
    id: "signature",
    name: "Signature Spa",
    price: "₹3,999",
    positioning: "Comprehensive deep clean.",
    isPopular: true,
  },
  {
    id: "ultimate",
    name: "Ultimate Ceramic",
    price: "₹14,999",
    positioning: "Flawless correction & 9H coating.",
    isPopular: false,
  }
];

export const features = [
  {
    category: "Exterior & Paint",
    items: [
      { name: "Hand Wash & Chamois Dry", values: [true, true, true] },
      { name: "Wheel & Tire Clean", values: [true, true, true] },
      { name: "Paste Wax / Sealant", values: [false, true, true] },
      { name: "1-Step Paint Correction", values: [false, false, true] },
      { name: "9H Ceramic Coating", values: [false, false, true] },
      { name: "Touchless Laser Finish", values: [false, false, true] },
    ]
  },
  {
    category: "Interior & Upholstery",
    items: [
      { name: "Quick Vacuum", values: [true, true, true] },
      { name: "Interior Wipe Down", values: [true, true, true] },
      { name: "Window Clean", values: [true, true, true] },
      { name: "Deep Seat & Floor Extraction", values: [false, true, true] },
      { name: "Leather Conditioning", values: [false, true, true] },
    ]
  },
  {
    category: "Specialized",
    items: [
      { name: "Door Jambs", values: [false, true, true] },
      { name: "Engine Bay Detail", values: [false, false, true] },
    ]
  }
];
