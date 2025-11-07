/**
 * Prisma Basic Operations
 */
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Create
export async function createUser(data: {
  email: string;
  name: string;
  password: string;
}) {
  return prisma.user.create({
    data,
  });
}

// Read
export async function getUser(id: string) {
  return prisma.user.findUnique({
    where: { id },
  });
}

export async function getUsers() {
  return prisma.user.findMany();
}

// Update
export async function updateUser(
  id: string,
  data: { name?: string; email?: string }
) {
  return prisma.user.update({
    where: { id },
    data,
  });
}

// Delete
export async function deleteUser(id: string) {
  return prisma.user.delete({
    where: { id },
  });
}

// Relations
export async function getUserWithPosts(id: string) {
  return prisma.user.findUnique({
    where: { id },
    include: {
      posts: true,
    },
  });
}

// Pagination
export async function getPaginatedUsers(page: number = 1, pageSize: number = 10) {
  const skip = (page - 1) * pageSize;

  const [users, total] = await Promise.all([
    prisma.user.findMany({
      skip,
      take: pageSize,
    }),
    prisma.user.count(),
  ]);

  return {
    users,
    total,
    page,
    totalPages: Math.ceil(total / pageSize),
  };
}

// Filtering
export async function searchUsers(query: string) {
  return prisma.user.findMany({
    where: {
      OR: [
        { name: { contains: query, mode: 'insensitive' } },
        { email: { contains: query, mode: 'insensitive' } },
      ],
    },
  });
}

// Transactions
export async function createUserWithProfile(userData: any, profileData: any) {
  return prisma.$transaction(async (tx) => {
    const user = await tx.user.create({
      data: userData,
    });

    const profile = await tx.profile.create({
      data: {
        ...profileData,
        userId: user.id,
      },
    });

    return { user, profile };
  });
}

// Aggregations
export async function getUserStats() {
  return prisma.user.aggregate({
    _count: true,
    _avg: { age: true },
    _min: { age: true },
    _max: { age: true },
  });
}

// Cleanup
export async function disconnect() {
  await prisma.$disconnect();
}
