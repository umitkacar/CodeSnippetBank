// Playwright E2E Testing
// Comprehensive Playwright test examples

import { test, expect, Page } from '@playwright/test';

test.describe('Playwright Basic Tests', () => {
  test('navigates to page', async ({ page }) => {
    await page.goto('https://example.com');
    await expect(page).toHaveTitle(/Example/);
  });

  test('clicks button', async ({ page }) => {
    await page.goto('https://example.com');
    await page.click('button#submit');
    await expect(page.locator('.success')).toBeVisible();
  });

  test('fills form', async ({ page }) => {
    await page.goto('https://example.com/form');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('takes screenshot', async ({ page }) => {
    await page.goto('https://example.com');
    await page.screenshot({ path: 'screenshot.png' });
  });

  test('waits for element', async ({ page }) => {
    await page.goto('https://example.com');
    await page.waitForSelector('.loaded', { timeout: 5000 });
    expect(await page.locator('.loaded').isVisible()).toBe(true);
  });
});

test.describe('Playwright Advanced', () => {
  test('handles multiple tabs', async ({ context }) => {
    const page1 = await context.newPage();
    await page1.goto('https://example.com');

    const [page2] = await Promise.all([
      context.waitForEvent('page'),
      page1.click('a[target="_blank"]'),
    ]);

    await page2.waitForLoadState();
    expect(page2.url()).toContain('new-page');
  });

  test('intercepts network requests', async ({ page }) => {
    await page.route('**/api/data', (route) => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ data: 'mocked' }),
      });
    });

    await page.goto('https://example.com');
    const data = await page.evaluate(() => fetch('/api/data').then((r) => r.json()));
    expect(data.data).toBe('mocked');
  });
});
