// Selenium WebDriver E2E Testing
// Comprehensive Selenium test examples

import { Builder, By, until, WebDriver } from 'selenium-webdriver';

describe('Selenium WebDriver Tests', () => {
  let driver: WebDriver;

  beforeAll(async () => {
    driver = await new Builder().forBrowser('chrome').build();
  });

  afterAll(async () => {
    await driver.quit();
  });

  test('navigates to page', async () => {
    await driver.get('https://example.com');
    const title = await driver.getTitle();
    expect(title).toContain('Example');
  });

  test('finds and clicks element', async () => {
    await driver.get('https://example.com');
    const button = await driver.findElement(By.id('submit'));
    await button.click();
    await driver.wait(until.elementLocated(By.className('success')), 5000);
  });

  test('fills form', async () => {
    await driver.get('https://example.com/form');
    await driver.findElement(By.name('email')).sendKeys('test@example.com');
    await driver.findElement(By.name('password')).sendKeys('password123');
    await driver.findElement(By.css('button[type="submit"]')).click();
    await driver.wait(until.urlContains('/dashboard'), 5000);
  });

  test('waits for element', async () => {
    await driver.get('https://example.com');
    await driver.wait(until.elementLocated(By.className('loaded')), 5000);
    const element = await driver.findElement(By.className('loaded'));
    expect(await element.isDisplayed()).toBe(true);
  });
});
