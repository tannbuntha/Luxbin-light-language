"use client";

import { LuxbinMultiWaveTranslator } from '@/components/LuxbinMultiWaveTranslator';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 relative">
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
        style={{ backgroundImage: 'url(/preview_image.jpg)' }}
      />
      <div className="relative z-10">
        <LuxbinMultiWaveTranslator />
      </div>
    </main>
  );
}