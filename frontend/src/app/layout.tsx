import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Research Funding & Innovation Intelligence Platform",
  description: "AI-powered intelligence platform connecting research, intellectual property, grants, and commercialization pathways.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-blue-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
