/**
 * Next.js Parallel Routes examples
 */

// Layout with parallel routes: app/layout.tsx
export default function LayoutWithParallelRoutes({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode;
  team: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return (
    <div>
      <div>{children}</div>
      <div className="grid grid-cols-2 gap-4">
        <div>{team}</div>
        <div>{analytics}</div>
      </div>
    </div>
  );
}

// app/@team/page.tsx
export function TeamSlot() {
  return (
    <div>
      <h2>Team</h2>
      <p>Team members go here</p>
    </div>
  );
}

// app/@analytics/page.tsx
export function AnalyticsSlot() {
  return (
    <div>
      <h2>Analytics</h2>
      <p>Analytics data goes here</p>
    </div>
  );
}

// Conditional rendering in parallel routes
export function ConditionalLayout({
  children,
  dashboard,
  login,
  isAuthenticated,
}: {
  children: React.ReactNode;
  dashboard: React.ReactNode;
  login: React.ReactNode;
  isAuthenticated: boolean;
}) {
  return (
    <div>
      {children}
      {isAuthenticated ? dashboard : login}
    </div>
  );
}

// Default slot: app/@team/default.tsx
export default function TeamDefault() {
  return <div>Team (default)</div>;
}
