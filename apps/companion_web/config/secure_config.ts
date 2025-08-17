import { randomBytes } from 'crypto';

export class SecureConfig {
  private static instance: SecureConfig;
  private config: Map<string, string>;

  private constructor() {
    this.config = new Map();
    this.loadConfig();
  }

  static getInstance(): SecureConfig {
    if (!SecureConfig.instance) {
      SecureConfig.instance = new SecureConfig();
    }
    return SecureConfig.instance;
  }

  private loadConfig(): void {
    // Load from environment variables
    this.config.set('ENCRYPTION_KEY', process.env.ENCRYPTION_KEY || this.generateEncryptionKey());
    this.config.set('REDIS_URL', process.env.REDIS_URL || 'redis://localhost:6379');
    this.config.set('LOG_LEVEL', process.env.LOG_LEVEL || 'info');
    this.config.set('SESSION_DURATION', process.env.SESSION_DURATION || '86400'); // 24 hours
  }

  private generateEncryptionKey(): string {
    // Generate a 32-byte (256-bit) key and encode as base64
    const key = randomBytes(32).toString('base64');
    console.warn('Warning: Generated new encryption key. Set ENCRYPTION_KEY environment variable for production.');
    return key;
  }

  get(key: string): string {
    const value = this.config.get(key);
    if (!value) {
      throw new Error(`Configuration key '${key}' not found`);
    }
    return value;
  }

  set(key: string, value: string): void {
    this.config.set(key, value);
  }

  has(key: string): boolean {
    return this.config.has(key);
  }
}