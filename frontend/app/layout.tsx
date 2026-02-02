import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Aethel Studio - Correct-by-Construction Software",
  description: "Interactive playground for the Aethel programming language. Write code that is mathematically proved to be correct.",
  keywords: ["aethel", "formal verification", "programming language", "correct by construction", "z3 solver"],
  authors: [{ name: "Aethel Lang Team" }],
  openGraph: {
    title: "Aethel Studio",
    description: "Write software that is mathematically proved to be correct",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
