/**
 * Next.js CMS Integrations (Contentful, Sanity, Strapi)
 */

// Contentful
import { createClient } from 'contentful';

export const contentfulClient = createClient({
  space: process.env.CONTENTFUL_SPACE_ID!,
  accessToken: process.env.CONTENTFUL_ACCESS_TOKEN!,
});

export async function getContentfulEntries(contentType: string) {
  const entries = await contentfulClient.getEntries({
    content_type: contentType,
  });
  return entries.items;
}

// Sanity
import { createClient as createSanityClient } from '@sanity/client';

export const sanity = createSanityClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: '2024-01-01',
  useCdn: true,
});

export async function getSanityData(query: string) {
  return await sanity.fetch(query);
}

// Strapi
export async function getStrapiData(endpoint: string) {
  const res = await fetch(`${process.env.STRAPI_URL}/api/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${process.env.STRAPI_TOKEN}`,
    },
  });
  return res.json();
}
