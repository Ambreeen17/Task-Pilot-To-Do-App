import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TaskPilot - Your Smart Copilot for Tasks",
  description: "AI-powered autonomous task management that learns your habits, suggests optimizations, and helps you stay productive.",
  keywords: ["task management", "AI", "productivity", "todo", "autonomous"],
  authors: [{ name: "TaskPilot" }],
  openGraph: {
    title: "TaskPilot - Your Smart Copilot for Tasks",
    description: "AI-powered autonomous task management",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
