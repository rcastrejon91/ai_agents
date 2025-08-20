import React from "react";
import * as Sentry from "@sentry/react";

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  componentName?: string;
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error Boundary caught an error:", error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });

    // Log to monitoring service
    Sentry.captureException(error, {
      extra: {
        errorInfo,
        component: this.props.componentName,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString(),
      },
      tags: {
        errorBoundary: this.props.componentName || 'unknown',
        section: 'frontend'
      }
    });

    // Report to custom analytics if available
    if (window.analytics && typeof window.analytics.track === 'function') {
      window.analytics.track('Error Boundary Triggered', {
        error: error.message,
        component: this.props.componentName,
        stack: error.stack,
        url: window.location.href
      });
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
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

      return (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <details style={{ whiteSpace: "pre-wrap", marginTop: "8px" }}>
            <summary>Technical Details</summary>
            {this.state.errorInfo?.componentStack}
          </details>
          <div style={{ marginTop: "16px", display: "flex", gap: "8px", justifyContent: "center" }}>
            <button
              onClick={this.resetError}
              style={{
                padding: "8px 16px",
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Try Again
            </button>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: "8px 16px",
                backgroundColor: "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Reload Page
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

export default Sentry.withProfiler(ErrorBoundary);
