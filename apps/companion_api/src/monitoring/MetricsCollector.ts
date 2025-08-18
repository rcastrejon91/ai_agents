import { Gauge, Counter, Histogram, register } from 'prom-client';
import { Logger } from '../utils/Logger.js';

export class MetricsCollector {
  private memoryUsage: Gauge<string>;
  private requestDuration: Histogram<string>;
  private errorCounter: Counter<string>;
  private activeConnections: Gauge<string>;
  private requestCounter: Counter<string>;
  private logger: Logger;

  constructor() {
    this.logger = new Logger('MetricsCollector');

    // Fix: Add process memory metrics
    this.memoryUsage = new Gauge({
      name: 'process_memory_usage_bytes',
      help: 'Process memory usage in bytes',
      labelNames: ['type'],
      collect: this.collectMemoryMetrics.bind(this)
    });

    // Enhancement: Add request duration histogram
    this.requestDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'HTTP request duration in seconds',
      labelNames: ['method', 'route', 'status_code'],
      buckets: [0.1, 0.5, 1, 2, 5, 10, 30]
    });

    // Enhancement: Add detailed error counter
    this.errorCounter = new Counter({
      name: 'application_error_total',
      help: 'Total number of application errors',
      labelNames: ['type', 'code', 'route']
    });

    // Additional metrics
    this.activeConnections = new Gauge({
      name: 'active_connections_total',
      help: 'Total number of active connections'
    });

    this.requestCounter = new Counter({
      name: 'http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code']
    });

    this.logger.info('Metrics collector initialized');
  }

  private collectMemoryMetrics(): void {
    try {
      const usage = process.memoryUsage();
      this.memoryUsage.set({ type: 'heap_used' }, usage.heapUsed);
      this.memoryUsage.set({ type: 'heap_total' }, usage.heapTotal);
      this.memoryUsage.set({ type: 'external' }, usage.external);
      this.memoryUsage.set({ type: 'rss' }, usage.rss);
      
      if (usage.arrayBuffers) {
        this.memoryUsage.set({ type: 'array_buffers' }, usage.arrayBuffers);
      }
    } catch (error) {
      this.logger.error('Failed to collect memory metrics', { error });
    }
  }

  trackRequest(method: string, route: string, duration: number, statusCode: number): void {
    try {
      this.requestDuration.labels(method, route, statusCode.toString()).observe(duration);
      this.requestCounter.labels(method, route, statusCode.toString()).inc();
    } catch (error) {
      this.logger.error('Failed to track request metrics', { error, method, route, statusCode });
    }
  }

  trackError(type: string, code: string, route?: string): void {
    try {
      this.errorCounter.labels(type, code, route || 'unknown').inc();
    } catch (error) {
      this.logger.error('Failed to track error metrics', { error, type, code, route });
    }
  }

  incrementActiveConnections(): void {
    try {
      this.activeConnections.inc();
    } catch (error) {
      this.logger.error('Failed to increment active connections', { error });
    }
  }

  decrementActiveConnections(): void {
    try {
      this.activeConnections.dec();
    } catch (error) {
      this.logger.error('Failed to decrement active connections', { error });
    }
  }

  setActiveConnections(count: number): void {
    try {
      this.activeConnections.set(count);
    } catch (error) {
      this.logger.error('Failed to set active connections', { error });
    }
  }

  getMetrics(): Promise<string> {
    return register.metrics();
  }

  getMetricsAsJson(): Promise<any[]> {
    return register.getMetricsAsJSON();
  }

  // Middleware factory for Express
  createMiddleware() {
    return (req: any, res: any, next: any) => {
      const start = Date.now();
      
      this.incrementActiveConnections();

      // Override res.end to capture metrics
      const originalEnd = res.end;
      res.end = (...args: any[]) => {
        const duration = (Date.now() - start) / 1000; // Convert to seconds
        const route = req.route?.path || req.path || 'unknown';
        
        this.trackRequest(req.method, route, duration, res.statusCode);
        this.decrementActiveConnections();
        
        originalEnd.apply(res, args);
      };

      next();
    };
  }

  // Error tracking middleware
  createErrorMiddleware() {
    return (error: any, req: any, res: any, next: any) => {
      const route = req.route?.path || req.path || 'unknown';
      this.trackError(error.name || 'Error', error.code || 'unknown', route);
      next(error);
    };
  }

  // Health check method
  getHealthMetrics(): any {
    try {
      const usage = process.memoryUsage();
      return {
        memory: {
          heapUsed: usage.heapUsed,
          heapTotal: usage.heapTotal,
          external: usage.external,
          rss: usage.rss
        },
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      this.logger.error('Failed to get health metrics', { error });
      return null;
    }
  }

  reset(): void {
    try {
      register.clear();
      this.logger.info('Metrics registry cleared');
    } catch (error) {
      this.logger.error('Failed to reset metrics', { error });
    }
  }
}