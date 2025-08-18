import winston from 'winston';
import { ElasticsearchTransport } from 'winston-elasticsearch';

export class Logger {
  private logger: winston.Logger;

  constructor() {
    const transports: winston.transport[] = [
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.simple()
        )
      })
    ];

    // Add Elasticsearch transport if URL is provided
    if (process.env.ELASTICSEARCH_URL) {
      try {
        transports.push(
          new ElasticsearchTransport({
            level: 'info',
            clientOpts: { node: process.env.ELASTICSEARCH_URL },
            index: 'lyra-api-logs'
          })
        );
      } catch (error) {
        console.warn('Failed to initialize Elasticsearch transport:', error);
      }
    }

    this.logger = winston.createLogger({
      level: process.env.LOG_LEVEL || 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'lyra-api' },
      transports
    });
  }

  log(level: string, message: string, meta: any = {}): void {
    this.logger.log(level, message, {
      timestamp: new Date().toISOString(),
      ...meta
    });
  }

  info(message: string, meta: any = {}): void {
    this.log('info', message, meta);
  }

  error(error: Error | string, meta: any = {}): void {
    if (error instanceof Error) {
      this.logger.error(error.message, {
        stack: error.stack,
        timestamp: new Date().toISOString(),
        ...meta
      });
    } else {
      this.logger.error(error, {
        timestamp: new Date().toISOString(),
        ...meta
      });
    }
  }

  warn(message: string, meta: any = {}): void {
    this.log('warn', message, meta);
  }

  debug(message: string, meta: any = {}): void {
    this.log('debug', message, meta);
  }

  requestLogger() {
    return (req: any, res: any, next: any) => {
      const start = Date.now();
      
      res.on('finish', () => {
        const duration = Date.now() - start;
        this.info('HTTP Request', {
          method: req.method,
          url: req.url,
          status: res.statusCode,
          duration,
          ip: req.ip,
          userAgent: req.get('User-Agent'),
          timestamp: new Date().toISOString()
        });
      });
      
      next();
    };
  }

  // Helper method to create structured log entries
  createLogEntry(level: string, message: string, data: Record<string, any> = {}) {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      service: 'lyra-api',
      ...data
    };
  }
}