import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import React from 'react';
import Navigation from "../components/Navigation";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Healthcare Auditor",
  description: "Healthcare billing fraud detection and compliance verification system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return React.createElement('html', {
    lang: 'en',
  }, [
    React.createElement('body', {
      className: `${inter.className} bg-gray-50`,
    }, [
      React.createElement(Navigation, null),
      React.createElement('main', {
        className: 'min-h-screen',
      }, children),
    ]),
  ]);
}
