/**
 * Prisma Relations and Complex Queries
 */
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// One-to-Many Relations
export async function createPostWithAuthor(authorId: string, postData: any) {
  return prisma.post.create({
    data: {
      ...postData,
      author: {
        connect: { id: authorId },
      },
    },
  });
}

export async function getPostsWithAuthors() {
  return prisma.post.findMany({
    include: {
      author: {
        select: {
          id: true,
          name: true,
          email: true,
        },
      },
    },
  });
}

// Many-to-Many Relations
export async function addTagsToPost(postId: string, tagIds: string[]) {
  return prisma.post.update({
    where: { id: postId },
    data: {
      tags: {
        connect: tagIds.map(id => ({ id })),
      },
    },
  });
}

export async function getPostsWithTags() {
  return prisma.post.findMany({
    include: {
      tags: true,
    },
  });
}

// Nested Queries
export async function getAuthorWithPostsAndComments(authorId: string) {
  return prisma.user.findUnique({
    where: { id: authorId },
    include: {
      posts: {
        include: {
          comments: {
            include: {
              author: true,
            },
          },
        },
      },
    },
  });
}

// Conditional Includes
export async function getUserWithOptionalPosts(userId: string, includePosts: boolean) {
  return prisma.user.findUnique({
    where: { id: userId },
    include: {
      posts: includePosts,
    },
  });
}

// Filtering Related Records
export async function getUsersWithPublishedPosts() {
  return prisma.user.findMany({
    where: {
      posts: {
        some: {
          published: true,
        },
      },
    },
    include: {
      posts: {
        where: {
          published: true,
        },
      },
    },
  });
}

// Count Relations
export async function getUsersWithPostCount() {
  return prisma.user.findMany({
    include: {
      _count: {
        select: { posts: true },
      },
    },
  });
}

// Create with Nested Relations
export async function createUserWithPostsAndProfile(data: any) {
  return prisma.user.create({
    data: {
      email: data.email,
      name: data.name,
      posts: {
        create: data.posts,
      },
      profile: {
        create: data.profile,
      },
    },
    include: {
      posts: true,
      profile: true,
    },
  });
}
