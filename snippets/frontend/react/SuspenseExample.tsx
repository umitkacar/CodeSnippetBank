import React, { Suspense, lazy } from 'react';

/**
 * React Suspense examples with lazy loading
 */

// 1. Basic lazy loading
const LazyComponent = lazy(() => import('./SomeComponent'));

export const BasicSuspense: React.FC = () => {
  return (
    <Suspense fallback={<div>Loading component...</div>}>
      <LazyComponent />
    </Suspense>
  );
};

// 2. Multiple lazy components
const LazyDashboard = lazy(() => import('./Dashboard'));
const LazyProfile = lazy(() => import('./Profile'));
const LazySettings = lazy(() => import('./Settings'));

export const MultipleSuspense: React.FC<{ view: string }> = ({ view }) => {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      {view === 'dashboard' && <LazyDashboard />}
      {view === 'profile' && <LazyProfile />}
      {view === 'settings' && <LazySettings />}
    </Suspense>
  );
};

// 3. Nested Suspense boundaries
export const NestedSuspense: React.FC = () => {
  return (
    <Suspense fallback={<div>Loading page...</div>}>
      <Header />
      <Suspense fallback={<div>Loading sidebar...</div>}>
        <Sidebar />
      </Suspense>
      <Suspense fallback={<div>Loading content...</div>}>
        <MainContent />
      </Suspense>
    </Suspense>
  );
};

// 4. Suspense with error boundary
export const SuspenseWithErrorBoundary: React.FC = () => {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <Suspense fallback={<LoadingSpinner />}>
        <LazyComponent />
      </Suspense>
    </ErrorBoundary>
  );
};

// 5. Custom loading skeleton
const LoadingSkeleton: React.FC = () => {
  return (
    <div className="loading-skeleton">
      <div className="skeleton-header" />
      <div className="skeleton-content">
        <div className="skeleton-line" />
        <div className="skeleton-line" />
        <div className="skeleton-line" />
      </div>
    </div>
  );
};

// 6. Loading spinner
const LoadingSpinner: React.FC = () => {
  return (
    <div className="spinner-container">
      <div className="spinner" />
    </div>
  );
};

// Placeholder components
const Header: React.FC = () => <div>Header</div>;
const Sidebar: React.FC = () => <div>Sidebar</div>;
const MainContent: React.FC = () => <div>Main Content</div>;

// Simple ErrorBoundary for this example
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

/**
 * Preloading technique
 */
export const preloadComponent = (factory: () => Promise<any>) => {
  const Component = lazy(factory);
  // @ts-ignore
  Component.preload = factory;
  return Component;
};

// Usage:
// const LazyComponent = preloadComponent(() => import('./Component'));
// <button onMouseEnter={() => LazyComponent.preload()}>Hover to preload</button>
