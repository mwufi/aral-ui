/** @type {import('next').NextConfig} */
const nextConfig = {
  // Only use static export in production mode
  ...(process.env.NODE_ENV === 'production' ? {
    output: 'export',  // Outputs static HTML/CSS/JS
    distDir: 'out',    // Output to 'out' directory
  } : {}),
  
  // Ensure links work correctly when served from FastAPI
  basePath: '',
  trailingSlash: true,
  
  // Configure for dynamic routes
  exportPathMap: async function (
    defaultPathMap,
    { dev, dir, outDir, distDir, buildId }
  ) {
    return {
      '/': { page: '/' },
    };
  },
}

module.exports = nextConfig 