/**
 * Next.js Server Actions examples
 */
'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { redirect } from 'next/navigation';

// Basic server action
export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  // Validate input
  if (!title || !content) {
    return { error: 'Title and content are required' };
  }

  try {
    // Perform database operation
    // await db.post.create({ title, content });

    // Revalidate the posts page
    revalidatePath('/posts');

    return { success: true };
  } catch (error) {
    return { error: 'Failed to create post' };
  }
}

// Server action with redirect
export async function createPostAndRedirect(formData: FormData) {
  const result = await createPost(formData);

  if (result.success) {
    redirect('/posts');
  }

  return result;
}

// Server action with tag revalidation
export async function updatePost(id: string, formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  try {
    // await db.post.update({ where: { id }, data: { title, content } });

    // Revalidate specific tag
    revalidateTag('posts');
    revalidateTag(`post-${id}`);

    return { success: true };
  } catch (error) {
    return { error: 'Failed to update post' };
  }
}

// Server action with cookies
import { cookies } from 'next/headers';

export async function setTheme(theme: 'light' | 'dark') {
  cookies().set('theme', theme, {
    maxAge: 60 * 60 * 24 * 365, // 1 year
    path: '/',
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
  });

  revalidatePath('/');
}

// Server action with headers
import { headers } from 'next/headers';

export async function logRequest() {
  const headersList = headers();
  const userAgent = headersList.get('user-agent');
  const referer = headersList.get('referer');

  console.log('Request info:', { userAgent, referer });
}

// Optimistic update pattern
export async function toggleLike(postId: string) {
  try {
    // const post = await db.post.update({
    //   where: { id: postId },
    //   data: { likes: { increment: 1 } },
    // });

    revalidateTag(`post-${postId}`);
    return { success: true };
  } catch (error) {
    return { error: 'Failed to toggle like' };
  }
}

// Form validation with Zod
import { z } from 'zod';

const postSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string().min(10),
  published: z.boolean().default(false),
});

export async function createPostWithValidation(formData: FormData) {
  const data = {
    title: formData.get('title'),
    content: formData.get('content'),
    published: formData.get('published') === 'true',
  };

  const result = postSchema.safeParse(data);

  if (!result.success) {
    return {
      error: result.error.flatten().fieldErrors,
    };
  }

  try {
    // await db.post.create({ data: result.data });
    revalidatePath('/posts');
    return { success: true };
  } catch (error) {
    return { error: 'Failed to create post' };
  }
}
