import { notFound } from "next/navigation";
import { servicesData } from "@/data/services";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ServiceDetailHero from "@/components/ServiceDetailHero";
import ServiceFeatureSlide from "@/components/ServiceFeatureSlide";
import ServiceClientWrapper from "./ServiceClientWrapper";

interface PageProps {
  params: {
    slug: string;
  };
}

// Generate static params for all services during build
export function generateStaticParams() {
  return servicesData.map((service) => ({
    slug: service.slug,
  }));
}

export default async function ServiceDynamicPage({ params }: PageProps) {
  const resolvedParams = await params;
  const service = servicesData.find((s) => s.slug === resolvedParams.slug);

  if (!service) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col relative">
      <Navbar />
      
      <ServiceDetailHero 
        title={service.title}
        subtitle={service.subtitle}
        imageSrc={service.heroImage}
      />

      <div className="py-12" />

      {service.features.map((feature, idx) => (
        <ServiceFeatureSlide 
          key={feature.step}
          step={feature.step}
          title={feature.title}
          description={feature.description}
          imageSrc={feature.imageSrc}
          reverse={idx % 2 !== 0}
        />
      ))}

      {/* The Booking CTA and Modal logic are handled in this Client Component */}
      <ServiceClientWrapper serviceTitle={service.title} />

      <Footer />
    </main>
  );
}
