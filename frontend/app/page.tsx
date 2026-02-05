"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <main className="min-h-screen flex items-center justify-center p-24">
      <div className="max-w-7xl w-full">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            Healthcare Auditor
          </h1>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            Healthcare billing fraud detection and compliance verification system
          </p>
          <div className="mt-8 flex gap-4 justify-center">
            <Link
              href="/dashboard"
              className="rounded-md bg-primary-600 px-4 py-2 text-white hover:bg-primary-700"
            >
              Go to Dashboard
            </Link>
            <Link
              href="/api-docs"
              className="rounded-md border border-gray-300 px-4 py-2 hover:bg-gray-50"
            >
              API Documentation
            </Link>
          </div>
          <div className="mt-12 grid gap-8 text-left sm:grid-cols-2">
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Features</h2>
              <ul className="mt-4 space-y-2">
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Billing Code Validation
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Fraud Detection
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Compliance Checks
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Knowledge Graph Visualization
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Technology Stack</h2>
              <ul className="mt-4 space-y-2">
                <li className="flex items-center">
                  <span className="mr-2">⚛</span>
                  Next.js 15 + React 18
                </li>
                <li className="flex items-center">
                  <span className="mr-2">🐍</span>
                  TypeScript 5
                </li>
                <li className="flex items-center">
                  <span className="mr-2">⚡</span>
                  FastAPI (Python 3.11)
                </li>
                <li className="flex items-center">
                  <span className="mr-2">🗄</span>
                  PostgreSQL + Neo4j
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
