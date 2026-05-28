import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rohit Nikam — AI Systems Builder",
  description: "Talk to Rohit's AI digital twin. Ask about AI consulting, content strategy, or anything about his work.",
  icons: {
    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%237c3aed'/><text y='.9em' font-size='60' x='50%' text-anchor='middle' font-family='system-ui' font-weight='700' fill='white'>R</text></svg>",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
