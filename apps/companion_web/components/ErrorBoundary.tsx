import React from "react";
import * as Sentry from "@sentry/react";

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
  errorId?: string;
  retryCount?: number;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  componentName?: string;
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>;
  maxRetries?: number;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  enableMetrics?: boolean;
}

// Error metrics collector
class ErrorMetrics {
  private static instance: ErrorMetrics;
  private errors: Array<{
    timestamp: number;
    component: string;
    error: string;
    errorId: string;
  }> = [];

  static getInstance(): ErrorMetrics {
    if (!ErrorMetrics.instance) {
      ErrorMetrics.instance = new ErrorMetrics();
    }
    return ErrorMetrics.instance;
  }

  recordError(component: string, error: Error, errorId: string) {
    this.errors.push({
      timestamp: Date.now(),
      component,
      error: error.message,
      errorId
    });

    // Keep only last 100 errors
    if (this.errors.length > 100) {
      this.errors = this.errors.slice(-100);
    }
  }

  getErrorStats() {
    const now = Date.now();
    const last24h = this.errors.filter(e => now - e.timestamp < 24 * 60 * 60 * 1000);
    const lastHour = this.errors.filter(e => now - e.timestamp < 60 * 60 * 1000);
    
    return {
      total: this.errors.length,
      last24h: last24h.length,
      lastHour: lastHour.length,
      recentErrors: last24h.slice(-10)
    };
  }
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  private retryTimeouts: Set<NodeJS.Timeout> = new Set();
  private errorMetrics = ErrorMetrics.getInstance();

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { 
      hasError: false,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Generate unique error ID for tracking
    const errorId = `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      hasError: true,
      error,
      errorId,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const { componentName = 'Unknown', onError, enableMetrics = true } = this.props;
    const errorId = this.state.errorId || 'unknown';

    // Enhanced error logging
    console.group(`🚨 Error Boundary Triggered: ${componentName}`);
    console.error("Error:", error);
    console.error("Error Info:", errorInfo);
    console.error("Error ID:", errorId);
    console.error("Stack:", error.stack);
    console.groupEnd();

    // Update state with error info
    this.setState({
      error,
      errorInfo,
    });

    // Record metrics
    if (enableMetrics) {
      this.errorMetrics.recordError(componentName, error, errorId);
    }

    // Call custom error handler
    if (onError) {
      try {
        onError(error, errorInfo);
      } catch (handlerError) {
        console.error("Error in custom error handler:", handlerError);
      }
    }

    // Enhanced Sentry reporting
    Sentry.withScope((scope) => {
      scope.setTag("errorBoundary", componentName);
      scope.setTag("errorId", errorId);
      scope.setLevel("error");
      scope.setContext("errorInfo", {
        componentStack: errorInfo.componentStack,
        errorBoundary: componentName,
        retryCount: this.state.retryCount || 0,
      });
      scope.setContext("errorMetrics", this.errorMetrics.getErrorStats());
      
      Sentry.captureException(error);
    });

    // Security: Check for potential XSS in error messages
    this.sanitizeErrorData(error, errorInfo);
  }

  /**
   * Sanitize error data to prevent XSS attacks
   */
  private sanitizeErrorData(error: Error, errorInfo: React.ErrorInfo) {
    const suspiciousPatterns = [
      /<script/i,
      /javascript:/i,
      /on\w+\s*=/i,
      /data:text\/html/i
    ];

    const errorMessage = error.message || '';
    const componentStack = errorInfo.componentStack || '';

    const isSuspicious = suspiciousPatterns.some(pattern => 
      pattern.test(errorMessage) || pattern.test(componentStack)
    );

    if (isSuspicious) {
      console.warn("🔒 Suspicious content detected in error data - potential XSS attempt");
      Sentry.captureMessage("Suspicious error content detected", "warning");
      
      // Sanitize the error message
      this.setState(prevState => ({
        ...prevState,
        error: {
          ...prevState.error!,
          message: "Error message sanitized for security"
        }
      }));
    }
  }

  resetError = () => {
    // Clear any pending retry timeouts
    this.retryTimeouts.forEach(timeout => clearTimeout(timeout));
    this.retryTimeouts.clear();

    this.setState({ 
      hasError: false, 
      error: undefined, 
      errorInfo: undefined,
      errorId: undefined,
      retryCount: 0
    });

    // Log recovery
    console.log("🔄 Error boundary reset - component recovered");
  };

  /**
   * Auto-retry mechanism with exponential backoff
   */
  private autoRetry = () => {
    const { maxRetries = 3 } = this.props;
    const currentRetryCount = this.state.retryCount || 0;

    if (currentRetryCount < maxRetries) {
      const delay = Math.pow(2, currentRetryCount) * 1000; // Exponential backoff
      
      console.log(`🔄 Auto-retrying in ${delay}ms (attempt ${currentRetryCount + 1}/${maxRetries})`);
      
      const timeout = setTimeout(() => {
        this.setState(prevState => ({
          hasError: false,
          error: undefined,
          errorInfo: undefined,
          retryCount: (prevState.retryCount || 0) + 1
        }));
        
        this.retryTimeouts.delete(timeout);
      }, delay);

      this.retryTimeouts.add(timeout);
    }
  };

  componentWillUnmount() {
    // Cleanup timeouts
    this.retryTimeouts.forEach(timeout => clearTimeout(timeout));
    this.retryTimeouts.clear();
  }

  render() {
    if (this.state.hasError) {
      const { fallback: FallbackComponent } = this.props;
      const { error, errorInfo, errorId, retryCount } = this.state;

      if (FallbackComponent) {
        return (
          <FallbackComponent
            error={error}
            resetError={this.resetError}
          />
        );
      }

      // Enhanced error UI with security features
      return (
        <div className="error-container" style={{
          padding: '20px',
          border: '2px solid #dc3545',
          borderRadius: '8px',
          backgroundColor: '#f8f9fa',
          margin: '20px',
          fontFamily: 'Arial, sans-serif'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            <span style={{ fontSize: '24px', marginRight: '8px' }}>🚨</span>
            <h2 style={{ margin: 0, color: '#dc3545' }}>Something went wrong</h2>
          </div>

          {/* Error ID for tracking */}
          {errorId && (
            <div style={{ 
              fontSize: '12px', 
              color: '#6c757d',
              marginBottom: '12px',
              fontFamily: 'monospace'
            }}>
              Error ID: {errorId}
            </div>
          )}

          {/* Sanitized error message */}
          <div style={{ 
            backgroundColor: '#fff',
            padding: '12px',
            borderRadius: '4px',
            border: '1px solid #dee2e6',
            marginBottom: '16px'
          }}>
            <strong>Error:</strong> {error?.message || 'Unknown error occurred'}
          </div>

          {/* Retry information */}
          {retryCount! > 0 && (
            <div style={{ 
              color: '#856404',
              backgroundColor: '#fff3cd',
              padding: '8px 12px',
              borderRadius: '4px',
              marginBottom: '16px',
              fontSize: '14px'
            }}>
              ⚠️ Retry attempt {retryCount} failed
            </div>
          )}

          {/* Component stack (truncated for security) */}
          {errorInfo && (
            <details style={{ marginBottom: '16px' }}>
              <summary style={{ cursor: 'pointer', color: '#495057' }}>
                Technical Details
              </summary>
              <pre style={{
                whiteSpace: 'pre-wrap',
                fontSize: '12px',
                backgroundColor: '#f8f9fa',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #dee2e6',
                maxHeight: '200px',
                overflow: 'auto',
                marginTop: '8px'
              }}>
                {errorInfo.componentStack?.slice(0, 500)}
                {errorInfo.componentStack && errorInfo.componentStack.length > 500 && '...'}
              </pre>
            </details>
          )}

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={this.resetError}
              style={{
                padding: '8px 16px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#0056b3';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#007bff';
              }}
            >
              🔄 Try Again
            </button>

            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '8px 16px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#1e7e34';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#28a745';
              }}
            >
              🔃 Reload Page
            </button>

            <button
              onClick={this.autoRetry}
              disabled={retryCount! >= (this.props.maxRetries || 3)}
              style={{
                padding: '8px 16px',
                backgroundColor: retryCount! >= (this.props.maxRetries || 3) ? '#6c757d' : '#ffc107',
                color: retryCount! >= (this.props.maxRetries || 3) ? '#ffffff' : '#212529',
                border: 'none',
                borderRadius: '4px',
                cursor: retryCount! >= (this.props.maxRetries || 3) ? 'not-allowed' : 'pointer',
                fontSize: '14px'
              }}
            >
              ⏱️ Auto Retry
            </button>
          </div>

          {/* Help text */}
          <div style={{
            marginTop: '16px',
            fontSize: '12px',
            color: '#6c757d',
            lineHeight: '1.4'
          }}>
            If this error persists, please contact support with the Error ID above.
            Your session data has been preserved.
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Custom fallback component for chat interfaces
export const ChatErrorFallback: React.FC<{
  error?: Error;
  resetError: () => void;
}> = ({ error, resetError }) => (
  <div
    style={{
      padding: "16px",
      textAlign: "center",
      border: "1px solid #ff6b6b",
      borderRadius: "8px",
      backgroundColor: "rgba(255, 107, 107, 0.1)",
      color: "#d32f2f",
    }}
  >
    <h3>Chat Error</h3>
    <p>The chat interface encountered an error.</p>
    {error && (
      <details style={{ marginTop: "8px", textAlign: "left" }}>
        <summary>Error Details</summary>
        <code style={{ fontSize: "12px" }}>{error.message}</code>
      </details>
    )}
    <button
      onClick={resetError}
      style={{
        marginTop: "8px",
        padding: "6px 12px",
        backgroundColor: "#007bff",
        color: "white",
        border: "none",
        borderRadius: "4px",
        cursor: "pointer",
      }}
    >
      Restart Chat
    </button>
  </div>
);

export default Sentry.withProfiler(ErrorBoundary);
