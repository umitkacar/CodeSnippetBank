# ⚙️ Modern Backend Snippets

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

</div>

## 🚀 Modern APIs

### FastAPI + Pydantic

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import asyncio
from datetime import datetime

app = FastAPI(
    title="Modern API",
    description="Production-ready FastAPI with best practices",
    version="1.0.0"
)

# Models
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

# Database dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with validation"""
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = hash_password(user.password)

    # Create user
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# WebSocket support
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
```

### tRPC Type-Safety

```typescript
// server/routers/_app.ts
import { z } from 'zod'
import { router, publicProcedure, protectedProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'

export const appRouter = router({
  // Query
  getUser: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input, ctx }) => {
      const user = await ctx.prisma.user.findUnique({
        where: { id: input.id },
      })

      if (!user) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'User not found',
        })
      }

      return user
    }),

  // Mutation
  createPost: protectedProcedure
    .input(z.object({
      title: z.string().min(3).max(100),
      content: z.string().min(10),
    }))
    .mutation(async ({ input, ctx }) => {
      const post = await ctx.prisma.post.create({
        data: {
          title: input.title,
          content: input.content,
          authorId: ctx.session.user.id,
        },
      })

      return post
    }),

  // Subscription (real-time)
  onPostAdd: publicProcedure
    .subscription(async ({ ctx }) => {
      return observable<Post>((emit) => {
        const onAdd = (data: Post) => {
          emit.next(data)
        }

        ctx.ee.on('add', onAdd)

        return () => {
          ctx.ee.off('add', onAdd)
        }
      })
    }),
})

export type AppRouter = typeof appRouter

// client/trpc.ts
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client'
import type { AppRouter } from '../server/routers/_app'

export const trpc = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: 'http://localhost:3000/api/trpc',
    }),
  ],
})

// Usage
const user = await trpc.getUser.query({ id: '123' })
const post = await trpc.createPost.mutate({
  title: 'Hello World',
  content: 'This is my first post',
})
```

### GraphQL with Apollo

```typescript
// schema.ts
import { gql } from 'apollo-server-express'

export const typeDefs = gql`
  type User {
    id: ID!
    email: String!
    username: String!
    posts: [Post!]!
    createdAt: DateTime!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
    published: Boolean!
    createdAt: DateTime!
  }

  type Query {
    me: User
    user(id: ID!): User
    posts(published: Boolean): [Post!]!
    post(id: ID!): Post
  }

  type Mutation {
    signup(email: String!, username: String!, password: String!): AuthPayload!
    login(email: String!, password: String!): AuthPayload!
    createPost(title: String!, content: String!): Post!
    publishPost(id: ID!): Post!
    deletePost(id: ID!): Boolean!
  }

  type AuthPayload {
    token: String!
    user: User!
  }

  type Subscription {
    postAdded: Post!
  }

  scalar DateTime
`

// resolvers.ts
import { PubSub } from 'graphql-subscriptions'

const pubsub = new PubSub()
const POST_ADDED = 'POST_ADDED'

export const resolvers = {
  Query: {
    me: async (_parent, _args, context) => {
      if (!context.user) throw new Error('Not authenticated')
      return context.prisma.user.findUnique({
        where: { id: context.user.id },
      })
    },

    posts: async (_parent, args, context) => {
      return context.prisma.post.findMany({
        where: args.published !== undefined
          ? { published: args.published }
          : undefined,
        orderBy: { createdAt: 'desc' },
      })
    },
  },

  Mutation: {
    createPost: async (_parent, args, context) => {
      if (!context.user) throw new Error('Not authenticated')

      const post = await context.prisma.post.create({
        data: {
          title: args.title,
          content: args.content,
          authorId: context.user.id,
        },
      })

      pubsub.publish(POST_ADDED, { postAdded: post })

      return post
    },
  },

  Subscription: {
    postAdded: {
      subscribe: () => pubsub.asyncIterator([POST_ADDED]),
    },
  },

  User: {
    posts: async (parent, _args, context) => {
      return context.prisma.post.findMany({
        where: { authorId: parent.id },
      })
    },
  },
}
```

## 🔐 Authentication

### NextAuth.js

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import GithubProvider from 'next-auth/providers/github'
import CredentialsProvider from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@auth/prisma-adapter'
import { prisma } from '@/lib/prisma'
import bcrypt from 'bcrypt'

export const authOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GithubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email },
        })

        if (!user || !user.hashedPassword) {
          return null
        }

        const isValid = await bcrypt.compare(
          credentials.password,
          user.hashedPassword
        )

        if (!isValid) {
          return null
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
        }
      },
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
      }
      return session
    },
  },
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
```

## 💾 Databases

### Prisma ORM

```prisma
// schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  username      String    @unique
  hashedPassword String?
  name          String?
  image         String?
  posts         Post[]
  comments      Comment[]
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@index([email])
}

model Post {
  id        String    @id @default(cuid())
  title     String
  content   String
  published Boolean   @default(false)
  author    User      @relation(fields: [authorId], references: [id])
  authorId  String
  comments  Comment[]
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt

  @@index([authorId])
  @@index([published])
}

model Comment {
  id        String   @id @default(cuid())
  content   String
  post      Post     @relation(fields: [postId], references: [id])
  postId    String
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  createdAt DateTime @default(now())

  @@index([postId])
  @@index([authorId])
}
```

```typescript
// lib/prisma.ts
import { PrismaClient } from '@prisma/client'

const globalForPrisma = global as unknown as { prisma: PrismaClient }

export const prisma = globalForPrisma.prisma || new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

// Usage examples
export async function createUser(data: { email: string; username: string }) {
  return await prisma.user.create({
    data,
  })
}

export async function getPosts({ skip = 0, take = 10, published = true }) {
  return await prisma.post.findMany({
    where: { published },
    include: {
      author: {
        select: { id: true, username: true, image: true },
      },
      _count: {
        select: { comments: true },
      },
    },
    orderBy: { createdAt: 'desc' },
    skip,
    take,
  })
}
```

### Redis Caching

```typescript
// lib/redis.ts
import { Redis } from '@upstash/redis'

export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})

// Cache helper
export async function getCached<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 3600 // 1 hour
): Promise<T> {
  const cached = await redis.get(key)

  if (cached) {
    return cached as T
  }

  const data = await fetcher()
  await redis.set(key, data, { ex: ttl })

  return data
}

// Usage
const posts = await getCached(
  'posts:recent',
  async () => {
    return await prisma.post.findMany({
      where: { published: true },
      take: 10,
    })
  },
  3600 // Cache for 1 hour
)

// Rate limiting
export async function rateLimit(
  identifier: string,
  limit: number = 10,
  window: number = 60
): Promise<boolean> {
  const key = `rate_limit:${identifier}`
  const current = await redis.incr(key)

  if (current === 1) {
    await redis.expire(key, window)
  }

  return current <= limit
}
```

## 📚 Popular Repositories

- **[FastAPI](https://github.com/tiangolo/fastapi)** ⭐ 70k+ - Modern Python web framework
- **[tRPC](https://github.com/trpc/trpc)** ⭐ 33k+ - End-to-end typesafe APIs
- **[Prisma](https://github.com/prisma/prisma)** ⭐ 37k+ - Next-generation ORM
- **[NextAuth.js](https://github.com/nextauthjs/next-auth)** ⭐ 22k+ - Authentication
- **[Apollo GraphQL](https://github.com/apollographql/apollo-server)** ⭐ 14k+

---

<div align="center">

**[⬅️ Back: Frontend](../frontend/README.md)** | **[Next: Web3 →](../web3/README.md)**

</div>
