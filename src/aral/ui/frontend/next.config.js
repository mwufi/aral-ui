/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Outputs static HTML/CSS/JS
  distDir: 'out',    // Output to 'out' directory
  // Ensure links work correctly when served from FastAPI
  basePath: '',
  trailingSlash: true,
}

module.exports = nextConfig 