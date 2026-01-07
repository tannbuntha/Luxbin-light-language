const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { unoptimized: true },
  // Explicitly set the root for Vercel deployment
  experimental: {
    outputFileTracingRoot: path.join(__dirname),
  },
}

module.exports = nextConfig