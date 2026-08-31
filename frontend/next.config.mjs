/** @type {import('next').NextConfig} */
const backendOrigin = process.env.BACKEND_ORIGIN ?? "http://127.0.0.1:8000";
const isProduction = process.env.NODE_ENV === "production";

const securityHeaders = [
  { key: "Content-Security-Policy", value: `default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; form-action 'self'; img-src 'self' data: blob: https: http:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'${isProduction ? "" : " 'unsafe-eval'"}; connect-src 'self'${isProduction ? "" : " ws: http:"}` },
  { key: "Referrer-Policy", value: "same-origin" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  ...(isProduction ? [{ key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" }] : [])
];

const nextConfig = {
  // Keep the development compiler isolated from `next build`. Running a
  // production build while `next dev` is serving the app otherwise replaces
  // its chunk manifest and leaves open browser tabs requesting stale chunks.
  distDir: isProduction ? ".next" : ".next-dev",
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendOrigin}/api/:path*`
      },
      {
        source: "/uploads/:path*",
        destination: `${backendOrigin}/uploads/:path*`
      }
    ];
  }
};

export default nextConfig;
