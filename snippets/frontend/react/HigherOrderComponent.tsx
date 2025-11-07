import React, { ComponentType } from 'react';

/**
 * Higher-Order Component that adds loading functionality
 */
export function withLoading<P extends object>(
  Component: ComponentType<P>,
  loadingMessage: string = 'Loading...'
) {
  return function WithLoadingComponent(
    props: P & { isLoading: boolean }
  ) {
    const { isLoading, ...rest } = props;

    if (isLoading) {
      return (
        <div className="loading-container">
          <p>{loadingMessage}</p>
        </div>
      );
    }

    return <Component {...(rest as P)} />;
  };
}

/**
 * HOC for adding authentication check
 */
export function withAuth<P extends object>(
  Component: ComponentType<P>,
  redirectTo: string = '/login'
) {
  return function WithAuthComponent(props: P) {
    const isAuthenticated = true; // Replace with actual auth check

    if (!isAuthenticated) {
      if (typeof window !== 'undefined') {
        window.location.href = redirectTo;
      }
      return null;
    }

    return <Component {...props} />;
  };
}

/**
 * HOC for error handling
 */
export function withErrorBoundary<P extends object>(
  Component: ComponentType<P>,
  FallbackComponent?: ComponentType<{ error: Error }>
) {
  return class WithErrorBoundary extends React.Component<
    P,
    { hasError: boolean; error: Error | null }
  > {
    constructor(props: P) {
      super(props);
      this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error) {
      return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
      console.error('Error caught by boundary:', error, errorInfo);
    }

    render() {
      if (this.state.hasError && this.state.error) {
        if (FallbackComponent) {
          return <FallbackComponent error={this.state.error} />;
        }
        return (
          <div>
            <h1>Something went wrong.</h1>
            <p>{this.state.error.message}</p>
          </div>
        );
      }

      return <Component {...this.props} />;
    }
  };
}
