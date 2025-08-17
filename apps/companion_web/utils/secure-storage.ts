import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';
import { SecureConfig } from '../config/secure_config';

const config = SecureConfig.getInstance();
const ALGORITHM = 'aes-256-gcm';

export class SecureStorage {
  private static instance: SecureStorage;
  private constructor() {}

  static getInstance(): SecureStorage {
    if (!SecureStorage.instance) {
      SecureStorage.instance = new SecureStorage();
    }
    return SecureStorage.instance;
  }

  async encrypt(data: any): Promise<string> {
    const key = Buffer.from(config.get('ENCRYPTION_KEY'), 'base64');
    const iv = randomBytes(16);
    const cipher = createCipheriv(ALGORITHM, key, iv);
    
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return JSON.stringify({
      iv: iv.toString('hex'),
      data: encrypted,
      tag: authTag.toString('hex')
    });
  }

  async decrypt(encryptedData: string): Promise<any> {
    const { iv, data, tag } = JSON.parse(encryptedData);
    const key = Buffer.from(config.get('ENCRYPTION_KEY'), 'base64');
    
    const decipher = createDecipheriv(
      ALGORITHM,
      key,
      Buffer.from(iv, 'hex')
    );
    
    decipher.setAuthTag(Buffer.from(tag, 'hex'));
    
    let decrypted = decipher.update(data, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return JSON.parse(decrypted);
  }
}