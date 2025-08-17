import { environment } from './environment';

const env = process.env.NODE_ENV || 'development';
export const config = environment[env];