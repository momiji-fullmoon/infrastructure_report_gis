const apiInternalUrl = process.env.API_INTERNAL_URL || 'http://localhost:8000';
module.exports = {
  output: 'standalone',
  async rewrites() { return [{ source: '/api/backend/:path*', destination: `${apiInternalUrl}/:path*` }]; },
};
