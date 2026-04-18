import { Inter } from "next/font/google";
import "./globals.css";
import Shell from "@/components/Layout/Shell";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Skylark 6:10 Assistant",
  description: "Operational Intelligence for Site Security",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className={`${inter.className} min-h-full flex flex-col`}>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
