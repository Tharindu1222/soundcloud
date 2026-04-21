import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SC Downloader (web)",
  description: "Resolve SoundCloud tracks for download in the browser",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="topbar" />
        {children}
      </body>
    </html>
  );
}
