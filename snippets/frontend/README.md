# Frontend Code Snippets Collection

## Overview
This directory contains **234 production-ready TypeScript/JavaScript code snippets** for modern frontend development.

## Categories

### 1. React (67 snippets)
Custom hooks, Context patterns, HOCs, Performance optimization, Forms, Data fetching, State management, Server components, Suspense, and Error boundaries.

**Key files:**
- `useDebounce.ts` - Debouncing hook
- `useLocalStorage.ts` - localStorage management
- `useAsync.ts` - Async operation handling
- `AuthContext.tsx` - Authentication context
- `ThemeContext.tsx` - Theme management
- `ErrorBoundary.tsx` - Error boundary component
- `FormWithValidation.tsx` - Form handling with validation
- `DataFetchingPatterns.tsx` - Various data fetching patterns
- `StateManagementPatterns.tsx` - State management with Context + useReducer
- Plus 58 more hooks and patterns!

### 2. Next.js (41 snippets)
App router, Server actions, Middleware, API routes, Dynamic routes, SSG/ISR, Image/Font optimization, Metadata, Authentication, Database integration, and more.

**Key files:**
- `app-layout.tsx` - Root layout setup
- `server-action.ts` - Server actions examples
- `middleware.ts` - Middleware patterns
- `api-route.ts` - API route handlers
- `dynamic-route.tsx` - Dynamic routing
- `static-generation.tsx` - SSG/ISR patterns
- `image-optimization.tsx` - Image optimization
- `metadata.tsx` - SEO metadata
- `authentication.tsx` - Auth patterns
- `database-integration.ts` - Database setup
- Plus 31 more Next.js patterns!

### 3. Vue (35 snippets)
Composition API, Custom composables, Pinia stores, Vue Router, Component patterns, Transitions, and Reactive patterns.

**Key files:**
- `composable-useFetch.ts` - Fetch composable
- `TodoStore.ts` - Pinia store example
- `VueRouterSetup.ts` - Router configuration
- `CompositionAPIPatterns.vue` - Composition API examples
- Plus 31 more composables and patterns!

### 4. UI Components (49 snippets)
shadcn/ui integrations, Radix UI primitives, Headless UI patterns, Forms, Data tables, Charts, Modals, Dropdowns, Toast notifications, and more.

**Key files:**
- `ShadcnButton.tsx` - shadcn/ui Button
- `RadixDialog.tsx` - Radix Dialog component
- `Button.tsx` - Generic button
- `Modal.tsx` - Modal component
- `Dropdown.tsx` - Dropdown menu
- `DataTable.tsx` - Data table component
- Plus 43 more UI components!

### 5. Animations (40 snippets)
Framer Motion, GSAP, CSS animations, Scroll animations, Page transitions, Micro-interactions, Loading states, and Animated icons.

**Key files:**
- `FramerMotionExamples.tsx` - Comprehensive Framer Motion examples
- `GSAPAnimations.tsx` - GSAP animation patterns
- `FadeIn.tsx` - Fade in animation
- `SlideIn.tsx` - Slide in animation
- `ScrollReveal.tsx` - Scroll-triggered animations
- Plus 35 more animation examples!

## Technology Stack

- **React 18+** - Modern React with hooks and Suspense
- **Next.js 14+** - App Router, Server Components, Server Actions
- **Vue 3** - Composition API, Pinia, Vue Router
- **TypeScript** - Type-safe code throughout
- **Framer Motion** - Declarative animations
- **GSAP** - Professional-grade animations
- **Radix UI** - Accessible primitives
- **shadcn/ui** - Beautiful component system
- **Tailwind CSS** - Utility-first styling

## Usage

Each file is self-contained and production-ready. Simply copy the code you need into your project and adjust imports/styling as needed.

Example:
```typescript
// Import a React hook
import { useDebounce } from './react/useDebounce';

// Use in your component
const debouncedValue = useDebounce(searchTerm, 500);
```

## Best Practices Included

- ✅ TypeScript for type safety
- ✅ Proper error handling
- ✅ Performance optimization
- ✅ Accessibility considerations
- ✅ Modern React patterns
- ✅ Server-side rendering support
- ✅ Responsive design
- ✅ Clean code principles

## Directory Structure

```
frontend/
├── react/              (67 files)
├── nextjs/             (41 files)
├── vue/                (35 files)
├── ui-components/      (49 files)
└── animations/         (40 files)
```

## Created
November 2025 - All snippets follow 2024-2025 best practices and modern patterns.
