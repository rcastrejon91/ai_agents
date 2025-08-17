export const environment = {
  development: {
    backendUrl: 'http://localhost:5000',
  },
  production: {
    backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.yourdomain.com',
  }
};