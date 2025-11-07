// ============================================================================
// Prisma Schema and Queries - Production Examples
// ============================================================================

// schema.prisma file content (paste into schema.prisma):
/*
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(uuid())
  email         String    @unique
  name          String
  role          Role      @default(USER)
  posts         Post[]
  profile       Profile?
  orders        Order[]
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@index([email])
  @@map("users")
}

model Profile {
  id        String   @id @default(uuid())
  bio       String?
  avatar    String?
  userId    String   @unique
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("profiles")
}

model Post {
  id          String     @id @default(uuid())
  title       String
  content     String?
  published   Boolean    @default(false)
  authorId    String
  author      User       @relation(fields: [authorId], references: [id], onDelete: Cascade)
  categories  Category[]
  tags        Tag[]
  createdAt   DateTime   @default(now())
  updatedAt   DateTime   @updatedAt

  @@index([authorId])
  @@index([published])
  @@map("posts")
}

model Category {
  id    String @id @default(uuid())
  name  String @unique
  posts Post[]

  @@map("categories")
}

model Tag {
  id    String @id @default(uuid())
  name  String @unique
  posts Post[]

  @@map("tags")
}

model Order {
  id          String      @id @default(uuid())
  orderNumber String      @unique @default(cuid())
  status      OrderStatus @default(PENDING)
  totalAmount Decimal     @db.Decimal(10, 2)
  userId      String
  user        User        @relation(fields: [userId], references: [id])
  items       OrderItem[]
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt

  @@index([userId])
  @@index([status])
  @@map("orders")
}

model OrderItem {
  id        String   @id @default(uuid())
  quantity  Int
  price     Decimal  @db.Decimal(10, 2)
  orderId   String
  order     Order    @relation(fields: [orderId], references: [id], onDelete: Cascade)
  productId String
  product   Product  @relation(fields: [productId], references: [id])

  @@map("order_items")
}

model Product {
  id          String      @id @default(uuid())
  name        String
  description String?
  price       Decimal     @db.Decimal(10, 2)
  stock       Int         @default(0)
  isActive    Boolean     @default(true)
  orderItems  OrderItem[]
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt

  @@index([name])
  @@index([isActive])
  @@map("products")
}

enum Role {
  USER
  ADMIN
  MODERATOR
}

enum OrderStatus {
  PENDING
  PROCESSING
  SHIPPED
  DELIVERED
  CANCELLED
}
*/

import { PrismaClient, Prisma } from '@prisma/client';

const prisma = new PrismaClient();

// Snippet 1: Create user with nested relations
async function createUserWithProfile() {
  const user = await prisma.user.create({
    data: {
      email: 'john@example.com',
      name: 'John Doe',
      role: 'USER',
      profile: {
        create: {
          bio: 'Software developer',
          avatar: 'https://example.com/avatar.jpg'
        }
      }
    },
    include: {
      profile: true
    }
  });

  return user;
}

// Snippet 2: Find with complex filters
async function findActiveUsers() {
  const users = await prisma.user.findMany({
    where: {
      AND: [
        { role: { in: ['USER', 'ADMIN'] } },
        { createdAt: { gte: new Date('2024-01-01') } },
        {
          OR: [
            { posts: { some: { published: true } } },
            { orders: { some: { status: 'DELIVERED' } } }
          ]
        }
      ]
    },
    include: {
      _count: {
        select: { posts: true, orders: true }
      }
    },
    orderBy: { createdAt: 'desc' },
    take: 50
  });

  return users;
}

// Snippet 3: Update with relation
async function updateUserAndProfile(userId: string, data: any) {
  const user = await prisma.user.update({
    where: { id: userId },
    data: {
      name: data.name,
      profile: {
        upsert: {
          create: {
            bio: data.bio,
            avatar: data.avatar
          },
          update: {
            bio: data.bio,
            avatar: data.avatar
          }
        }
      }
    },
    include: {
      profile: true
    }
  });

  return user;
}

// Snippet 4: Create post with many-to-many relations
async function createPostWithCategories(authorId: string, postData: any) {
  const post = await prisma.post.create({
    data: {
      title: postData.title,
      content: postData.content,
      published: postData.published,
      author: {
        connect: { id: authorId }
      },
      categories: {
        connectOrCreate: postData.categories.map((name: string) => ({
          where: { name },
          create: { name }
        }))
      },
      tags: {
        connectOrCreate: postData.tags.map((name: string) => ({
          where: { name },
          create: { name }
        }))
      }
    },
    include: {
      categories: true,
      tags: true,
      author: {
        select: { id: true, name: true, email: true }
      }
    }
  });

  return post;
}

// Snippet 5: Transaction example
async function createOrder(userId: string, items: any[]) {
  const result = await prisma.$transaction(async (tx) => {
    // Create order
    const order = await tx.order.create({
      data: {
        userId,
        status: 'PENDING',
        totalAmount: 0
      }
    });

    // Create order items and update stock
    let totalAmount = 0;
    for (const item of items) {
      const product = await tx.product.findUniqueOrThrow({
        where: { id: item.productId }
      });

      if (product.stock < item.quantity) {
        throw new Error(`Insufficient stock for product ${product.name}`);
      }

      await tx.orderItem.create({
        data: {
          orderId: order.id,
          productId: item.productId,
          quantity: item.quantity,
          price: product.price
        }
      });

      await tx.product.update({
        where: { id: item.productId },
        data: { stock: { decrement: item.quantity } }
      });

      totalAmount += Number(product.price) * item.quantity;
    }

    // Update order total
    const updatedOrder = await tx.order.update({
      where: { id: order.id },
      data: { totalAmount },
      include: {
        items: {
          include: { product: true }
        }
      }
    });

    return updatedOrder;
  });

  return result;
}

// Snippet 6: Aggregation queries
async function getUserStatistics() {
  const stats = await prisma.user.aggregate({
    _count: { id: true },
    _avg: { orders: { totalAmount: true } },
    where: {
      createdAt: {
        gte: new Date('2024-01-01')
      }
    }
  });

  return stats;
}

// Snippet 7: Group by query
async function getOrdersByStatus() {
  const orderStats = await prisma.order.groupBy({
    by: ['status'],
    _count: { id: true },
    _sum: { totalAmount: true },
    _avg: { totalAmount: true },
    orderBy: {
      _sum: {
        totalAmount: 'desc'
      }
    }
  });

  return orderStats;
}

// Snippet 8: Raw query with type safety
async function getTopCustomers(limit: number = 10) {
  const customers = await prisma.$queryRaw<Array<{
    userId: string;
    name: string;
    totalOrders: bigint;
    totalSpent: Prisma.Decimal;
  }>>`
    SELECT
      u.id as "userId",
      u.name,
      COUNT(o.id)::int as "totalOrders",
      COALESCE(SUM(o.total_amount), 0) as "totalSpent"
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name
    ORDER BY "totalSpent" DESC
    LIMIT ${limit}
  `;

  return customers;
}

// Snippet 9: Upsert operation
async function upsertCategory(name: string, description?: string) {
  const category = await prisma.category.upsert({
    where: { name },
    update: {},
    create: { name }
  });

  return category;
}

// Snippet 10: Delete with cascade
async function deleteUser(userId: string) {
  const deletedUser = await prisma.user.delete({
    where: { id: userId }
  });

  return deletedUser;
}

// Snippet 11: Pagination with cursor
async function getPaginatedPosts(cursor?: string, limit: number = 20) {
  const posts = await prisma.post.findMany({
    take: limit,
    skip: cursor ? 1 : 0,
    cursor: cursor ? { id: cursor } : undefined,
    where: { published: true },
    orderBy: { createdAt: 'desc' },
    include: {
      author: {
        select: { id: true, name: true }
      },
      _count: {
        select: { categories: true, tags: true }
      }
    }
  });

  return {
    posts,
    nextCursor: posts.length === limit ? posts[posts.length - 1].id : null
  };
}

// Snippet 12: Batch operations
async function batchUpdateProducts(updates: Array<{ id: string; price: number }>) {
  const updatePromises = updates.map(({ id, price }) =>
    prisma.product.update({
      where: { id },
      data: { price }
    })
  );

  return await Promise.all(updatePromises);
}

// Snippet 13: Find unique or throw
async function getProductById(productId: string) {
  const product = await prisma.product.findUniqueOrThrow({
    where: { id: productId },
    include: {
      orderItems: {
        take: 10,
        orderBy: { createdAt: 'desc' }
      }
    }
  });

  return product;
}

// Snippet 14: Select specific fields
async function getUserList() {
  const users = await prisma.user.findMany({
    select: {
      id: true,
      name: true,
      email: true,
      _count: {
        select: {
          posts: true,
          orders: true
        }
      }
    }
  });

  return users;
}

// Snippet 15: Disconnect and reconnect
export async function disconnectPrisma() {
  await prisma.$disconnect();
}

export async function connectPrisma() {
  await prisma.$connect();
}
