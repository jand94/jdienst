import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter, Roboto } from "next/font/google";
import "./globals.css";
import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import { responsiveTokens } from "@/lib/responsive-tokens";
import { cn } from "@/lib/utils";

const robotoHeading = Roboto({subsets:['latin'],variable:'--font-heading'});

const inter = Inter({subsets:['latin'],variable:'--font-sans'});

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "jdienst",
  description: "jdienst Frontend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="de"
      className={cn("h-full", "antialiased", geistSans.variable, geistMono.variable, "font-sans", inter.variable, robotoHeading.variable)}
    >
      <body className="min-h-full flex flex-col">
        <Navbar />
        <div className={responsiveTokens.shellContainer}>
          <Sidebar />
          <main id="main-content" className={responsiveTokens.pageContentPadding}>
            {children}
          </main>
        </div>
        <Footer />
      </body>
    </html>
  );
}
