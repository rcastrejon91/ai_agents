import React from "react";

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
  errorId?: string;
  retryCount?: number;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo, errorId: string) => void;
  maxRetries?: number;
  enableReporting?: boolean;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, retryCount: 0 };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    const errorId = `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return {
      hasError: true,
      error,
      errorId,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const errorId = this.state.errorId || `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    console.error("Error Boundary caught an error:", error, errorInfo);
    console.error("Error ID:", errorId);
    
    this.setState({
      error,
      errorInfo,
      errorId,
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo, errorId);
    }

    // Report error to monitoring service if enabled
    if (this.props.enableReporting) {
      this.reportError(error, errorInfo, errorId);
    }
  }

  reportError = (error: Error, errorInfo: React.ErrorInfo, errorId: string) => {
    // Report to monitoring service (e.g., Sentry, LogRocket, etc.)
    const errorData = {
      errorId,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: this.getUserId(),
    };

    // Send to your error reporting service
    this.sendErrorReport(errorData);
  };

  getUserId = (): string | null => {
    // Try to get user ID from various sources
    if (typeof window !== 'undefined') {
      return localStorage.getItem('userId') || 
             sessionStorage.getItem('userId') || 
             null;
    }
    return null;
  };

  sendErrorReport = async (errorData: any) => {
    try {
      await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorData),
      });
    } catch (reportError) {
      console.error('Failed to report error:', reportError);
    }
  };

  resetError = () => {
    const retryCount = (this.state.retryCount || 0) + 1;
    const maxRetries = this.props.maxRetries || 3;
    
    if (retryCount <= maxRetries) {
      this.setState({ 
        hasError: false, 
        error: undefined, 
        errorInfo: undefined,
        retryCount
      });
    } else {
      console.warn('Maximum retry attempts reached');
    }
  };

  getErrorCategory = (error: Error): string => {
    if (error.name === 'ChunkLoadError') return 'Network';
    if (error.message.includes('Network')) return 'Network';
    if (error.message.includes('timeout')) return 'Timeout';
    if (error.name === 'TypeError') return 'Type Error';
    if (error.name === 'ReferenceError') return 'Reference Error';
    return 'Unknown';
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return (
          <FallbackComponent
            error={this.state.error}
            resetError={this.resetError}
          />
        );
      }

      const retryCount = this.state.retryCount || 0;
      const maxRetries = this.props.maxRetries || 3;
      const errorCategory = this.state.error ? this.getErrorCategory(this.state.error) : 'Unknown';

      return (
        <div
          style={{
            padding: "20px",
            margin: "20px",
            border: "2px solid #ff6b6b",
            borderRadius: "8px",
            backgroundColor: "#ffe0e0",
            color: "#d32f2f",
          }}
        >
          <h2>🚨 Something went wrong</h2>
          <p>We're sorry, but something unexpected happened.</p>
          
          <div style={{ marginTop: "10px", fontSize: "14px", color: "#666" }}>
            <p><strong>Error ID:</strong> {this.state.errorId}</p>
            <p><strong>Category:</strong> {errorCategory}</p>
            {retryCount > 0 && <p><strong>Retry attempts:</strong> {retryCount}/{maxRetries}</p>}
          </div>

          <details style={{ marginTop: "10px", textAlign: "left" }}>
            <summary style={{ cursor: "pointer", fontWeight: "bold" }}>
              Error Details
            </summary>
            <pre
              style={{
                marginTop: "10px",
                padding: "10px",
                backgroundColor: "#f5f5f5",
                color: "#333",
                overflow: "auto",
                fontSize: "12px",
                borderRadius: "4px",
                maxHeight: "200px",
              }}
            >
              {this.state.error && this.state.error.toString()}
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </pre>
          </details>
          
          <div style={{ marginTop: "15px" }}>
            {retryCount < maxRetries ? (
              <button
                onClick={this.resetError}
                style={{
                  marginRight: "10px",
                  padding: "8px 16px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Try Again ({maxRetries - retryCount} attempts left)
              </button>
            ) : (
              <button
                onClick={() => window.location.reload()}
                style={{
                  marginRight: "10px",
                  padding: "8px 16px",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Refresh Page
              </button>
            )}
            
            <button
              onClick={() => window.history.back()}
              style={{
                padding: "8px 16px",
                backgroundColor: "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Go Back
            </button>
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

export default ErrorBoundary;
