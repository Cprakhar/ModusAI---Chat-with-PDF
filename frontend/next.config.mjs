/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
      source: '/api/auth/:path*',
      destination: 'http://localhost:8000/api/v1/auth/:path*',
    },
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/v1/:path*',
    },
    ];
  },
};

export default nextConfig
