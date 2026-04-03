import type { Metadata } from "next";
import { Jost, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import PasswordProtection from "@/components/auth/PasswordProtection";

export const dynamic = "force-dynamic";

const jost = Jost({
  variable: "--font-jost",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ClosingSHIN Dashboard",
  description: "Advanced Stock Analysis Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body
        className={`${jost.variable} ${jetbrainsMono.variable} antialiased`}
        suppressHydrationWarning
      >
        <PasswordProtection>
          {children}
        </PasswordProtection>
      </body>
    </html>
  );
}
