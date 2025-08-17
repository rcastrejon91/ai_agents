import fs from 'fs';
import path from 'path';

export class FileSecurityManager {
  static async secureDirectory(dirPath: string): Promise<void> {
    // Ensure directory exists
    await fs.promises.mkdir(dirPath, { recursive: true });
    
    // Set secure permissions (readable/writable only by owner)
    await fs.promises.chmod(dirPath, 0o700);
  }

  static async secureFile(filePath: string): Promise<void> {
    // Ensure parent directory is secure
    await this.secureDirectory(path.dirname(filePath));
    
    // Set secure file permissions (readable/writable only by owner)
    await fs.promises.chmod(filePath, 0o600);
  }

  static async writeSecureFile(
    filePath: string,
    data: string | Buffer
  ): Promise<void> {
    await fs.promises.writeFile(filePath, data, { mode: 0o600 });
  }
}