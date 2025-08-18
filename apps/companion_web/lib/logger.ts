/**
 * Logger utility for Next.js applications
 */

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  meta?: Record<string, any>;
}

export class Logger {
  private context: string;

  constructor(context: string = "App") {
    this.context = context;
  }

  private log(
    level: string,
    message: string,
    meta?: Record<string, any>,
  ): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message: `[${this.context}] ${message}`,
      ...(meta && { meta }),
    };

    // In production, you might want to send this to a logging service
    console.log(JSON.stringify(entry));
  }

  info(message: string, meta?: Record<string, any>): void {
    this.log("INFO", message, meta);
  }

  warn(message: string, meta?: Record<string, any>): void {
    this.log("WARN", message, meta);
  }

  error(message: string, meta?: Record<string, any>): void {
    this.log("ERROR", message, meta);
  }

  debug(message: string, meta?: Record<string, any>): void {
    if (process.env.NODE_ENV === "development") {
      this.log("DEBUG", message, meta);
    }
  }
}

// Default logger instance
export const logger = new Logger();

// Create context-specific loggers
export function createLogger(context: string): Logger {
  return new Logger(context);
}
