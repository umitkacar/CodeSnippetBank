/**
 * Next.js Database Integration patterns
 */

// Prisma setup
// lib/prisma.ts
import { PrismaClient } from '@prisma/client';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: ['query'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// Database query in server component
export async function UsersPage() {
  const users = await prisma.user.findMany({
    select: {
      id: true,
      name: true,
      email: true,
    },
    orderBy: {
      createdAt: 'desc',
    },
  });

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          {user.name} - {user.email}
        </li>
      ))}
    </ul>
  );
}

// CRUD operations with server actions
'use server';

import { revalidatePath } from 'next/cache';

export async function createUser(formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;

  await prisma.user.create({
    data: { name, email },
  });

  revalidatePath('/users');
}

export async function updateUser(id: string, formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;

  await prisma.user.update({
    where: { id },
    data: { name, email },
  });

  revalidatePath('/users');
}

export async function deleteUser(id: string) {
  await prisma.user.delete({
    where: { id },
  });

  revalidatePath('/users');
}

// Complex query with relations
export async function getPostWithAuthor(id: string) {
  return await prisma.post.findUnique({
    where: { id },
    include: {
      author: {
        select: {
          name: true,
          email: true,
        },
      },
      comments: {
        include: {
          author: true,
        },
        orderBy: {
          createdAt: 'desc',
        },
      },
    },
  });
}

// Pagination
export async function getPaginatedPosts(page: number = 1, pageSize: number = 10) {
  const skip = (page - 1) * pageSize;

  const [posts, total] = await Promise.all([
    prisma.post.findMany({
      skip,
      take: pageSize,
      orderBy: { createdAt: 'desc' },
      include: { author: true },
    }),
    prisma.post.count(),
  ]);

  return {
    posts,
    pagination: {
      page,
      pageSize,
      total,
      totalPages: Math.ceil(total / pageSize),
    },
  };
}

// Search functionality
export async function searchPosts(query: string) {
  return await prisma.post.findMany({
    where: {
      OR: [
        { title: { contains: query, mode: 'insensitive' } },
        { content: { contains: query, mode: 'insensitive' } },
      ],
    },
    include: { author: true },
  });
}

// Transaction
export async function createPostWithTags(data: {
  title: string;
  content: string;
  authorId: string;
  tags: string[];
}) {
  return await prisma.$transaction(async (tx) => {
    const post = await tx.post.create({
      data: {
        title: data.title,
        content: data.content,
        authorId: data.authorId,
      },
    });

    await tx.tag.createMany({
      data: data.tags.map((name) => ({
        name,
        postId: post.id,
      })),
    });

    return post;
  });
}

// MongoDB with Prisma
export async function createDocument(data: any) {
  return await prisma.document.create({
    data: {
      ...data,
      metadata: {
        createdAt: new Date(),
        version: 1,
      },
    },
  });
}

// Drizzle ORM alternative
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const db = drizzle(pool);

// Query with Drizzle
import { users } from './schema';
import { eq } from 'drizzle-orm';

export async function getUserById(id: string) {
  return await db.select().from(users).where(eq(users.id, id));
}
