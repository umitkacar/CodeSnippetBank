# 🌐 Modern Frontend Snippets

<div align="center">

![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Next.js](https://img.shields.io/badge/Next.js_14-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

</div>

## ⚛️ React Ecosystem (2024-2025)

### Next.js 14 App Router

```typescript
// app/page.tsx - Server Component with Suspense
import { Suspense } from 'react'
import { getData } from '@/lib/api'

export default async function Page() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-8">Modern Next.js 14</h1>

      <Suspense fallback={<LoadingSkeleton />}>
        <DataDisplay />
      </Suspense>
    </div>
  )
}

async function DataDisplay() {
  const data = await getData() // Server-side data fetching

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {data.map((item) => (
        <Card key={item.id} data={item} />
      ))}
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {[1, 2, 3].map((i) => (
        <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
      ))}
    </div>
  )
}
```

### React Server Actions

```typescript
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'

const schema = z.object({
  name: z.string().min(3),
  email: z.string().email(),
  message: z.string().min(10)
})

export async function submitForm(formData: FormData) {
  const validatedFields = schema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message')
  })

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    }
  }

  // Process the form data
  await saveToDatabase(validatedFields.data)

  revalidatePath('/') // Revalidate the page cache

  return { success: true }
}

// app/contact/page.tsx
'use client'

import { submitForm } from '@/app/actions'
import { useFormState } from 'react-dom'

export default function ContactForm() {
  const [state, formAction] = useFormState(submitForm, null)

  return (
    <form action={formAction} className="space-y-4">
      <input
        type="text"
        name="name"
        className="w-full p-2 border rounded"
        placeholder="Name"
      />
      {state?.errors?.name && (
        <p className="text-red-500">{state.errors.name}</p>
      )}

      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Submit
      </button>
    </form>
  )
}
```

### Zustand State Management

```typescript
// store/useStore.ts
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

interface Todo {
  id: string
  text: string
  completed: boolean
}

interface TodoStore {
  todos: Todo[]
  addTodo: (text: string) => void
  toggleTodo: (id: string) => void
  deleteTodo: (id: string) => void
  clearCompleted: () => void
}

export const useTodoStore = create<TodoStore>()(
  persist(
    immer((set) => ({
      todos: [],

      addTodo: (text) =>
        set((state) => {
          state.todos.push({
            id: crypto.randomUUID(),
            text,
            completed: false
          })
        }),

      toggleTodo: (id) =>
        set((state) => {
          const todo = state.todos.find((t) => t.id === id)
          if (todo) todo.completed = !todo.completed
        }),

      deleteTodo: (id) =>
        set((state) => {
          state.todos = state.todos.filter((t) => t.id !== id)
        }),

      clearCompleted: () =>
        set((state) => {
          state.todos = state.todos.filter((t) => !t.completed)
        })
    })),
    {
      name: 'todo-storage',
      storage: createJSONStorage(() => localStorage)
    }
  )
)

// components/TodoList.tsx
'use client'

import { useTodoStore } from '@/store/useStore'

export default function TodoList() {
  const { todos, addTodo, toggleTodo, deleteTodo } = useTodoStore()
  const [input, setInput] = useState('')

  return (
    <div className="max-w-md mx-auto p-4">
      <form onSubmit={(e) => {
        e.preventDefault()
        addTodo(input)
        setInput('')
      }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="Add todo..."
        />
      </form>

      <ul className="mt-4 space-y-2">
        {todos.map((todo) => (
          <li key={todo.id} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span className={todo.completed ? 'line-through' : ''}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
```

### TanStack Query (React Query)

```typescript
// lib/api.ts
export const fetchPosts = async () => {
  const res = await fetch('https://api.example.com/posts')
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

export const createPost = async (data: { title: string; content: string }) => {
  const res = await fetch('https://api.example.com/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return res.json()
}

// app/providers.tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
})

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

// components/Posts.tsx
'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchPosts, createPost } from '@/lib/api'

export default function Posts() {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['posts'],
    queryFn: fetchPosts,
  })

  const mutation = useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] })
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      <button
        onClick={() => mutation.mutate({
          title: 'New Post',
          content: 'Content here...'
        })}
        disabled={mutation.isPending}
      >
        Add Post
      </button>

      {data.map((post) => (
        <div key={post.id}>{post.title}</div>
      ))}
    </div>
  )
}
```

## 🎨 UI Components

### shadcn/ui Integration

```bash
# Install shadcn/ui
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
```

```typescript
// components/ui/animated-button.tsx
'use client'

import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'

export function AnimatedButton({ children, ...props }: any) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Button {...props}>{children}</Button>
    </motion.div>
  )
}
```

### Framer Motion Animations

```typescript
// components/AnimatedCard.tsx
'use client'

import { motion } from 'framer-motion'

export function AnimatedCard({ children, index }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay: index * 0.1,
        ease: [0.25, 0.1, 0.25, 1]
      }}
      whileHover={{
        scale: 1.05,
        boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
      }}
      className="bg-white rounded-lg p-6 shadow-lg"
    >
      {children}
    </motion.div>
  )
}

// Stagger children animation
export function AnimatedList({ children }: any) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0 },
        show: {
          opacity: 1,
          transition: {
            staggerChildren: 0.1
          }
        }
      }}
      initial="hidden"
      animate="show"
    >
      {children}
    </motion.div>
  )
}
```

### Tailwind CSS Utilities

```typescript
// lib/utils.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Usage
<div className={cn(
  'base-classes',
  condition && 'conditional-classes',
  'more-classes'
)} />
```

```css
/* globals.css - Custom animations */
@layer utilities {
  .animate-gradient {
    background-size: 200% 200%;
    animation: gradient 3s ease infinite;
  }

  @keyframes gradient {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  }

  .glass-morphism {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
}
```

## 📱 Mobile Development

### React Native with Expo

```typescript
// app/(tabs)/index.tsx
import { StyleSheet, View, Text, Pressable } from 'react-native'
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated'

export default function HomeScreen() {
  const scale = useSharedValue(1)

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }))

  const handlePress = () => {
    scale.value = withSpring(scale.value === 1 ? 1.2 : 1)
  }

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.box, animatedStyle]}>
        <Pressable onPress={handlePress}>
          <Text style={styles.text}>Tap Me!</Text>
        </Pressable>
      </Animated.View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  box: {
    width: 200,
    height: 200,
    backgroundColor: '#4ECDC4',
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
})
```

## 📚 Popular Repositories

- **[Next.js](https://github.com/vercel/next.js)** ⭐ 120k+ - React framework
- **[shadcn/ui](https://github.com/shadcn/ui)** ⭐ 65k+ - Component library
- **[Zustand](https://github.com/pmndrs/zustand)** ⭐ 45k+ - State management
- **[TanStack Query](https://github.com/TanStack/query)** ⭐ 40k+ - Data fetching
- **[Framer Motion](https://github.com/framer/motion)** ⭐ 22k+ - Animations

---

<div align="center">

**[⬅️ Back: AI/ML](../ai-ml/README.md)** | **[Next: Backend →](../backend/README.md)**

</div>
