import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rohit Nikam — AI Systems Builder",
  description: "Talk to Rohit's AI digital twin. Ask about AI consulting, content strategy, or anything about his work.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
