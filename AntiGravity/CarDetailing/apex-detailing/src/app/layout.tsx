import type { Metadata } from "next";
import { Montserrat, Oswald } from "next/font/google";
import "./globals.css";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
});

const oswald = Oswald({
  variable: "--font-oswald",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "King of Detailing",
  description: "Elite Auto Detailing & Ceramic Coating in Bengaluru",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${montserrat.variable} ${oswald.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground overflow-x-hidden font-sans">
        {children}
      </body>
    </html>
  );
}
