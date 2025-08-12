const nextConfig = {
  experimental: { externalDir: true },
  env: {
    NEXT_PUBLIC_TTS_MODE: process.env.NEXT_PUBLIC_TTS_MODE || 'browser',
  },
};
export default nextConfig;
