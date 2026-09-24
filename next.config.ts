import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  output: process.env.VERCEL ? undefined : "standalone",
  outputFileTracingRoot: process.cwd(),
  turbopack: { root: process.cwd() },
  experimental: { cpus: 1 },
  poweredByHeader: false,
  devIndicators: false,
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "Referrer-Policy", value: "same-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },
};
export default nextConfig;
