const { test, expect } = require('@playwright/test');

test('basic navigation test', async ({ page }) => {
  // Go to the homepage
  await page.goto('http://localhost:8080/');
  
  // Check that the title is correct
  await expect(page).toHaveTitle(/QA Database/);
  
  // Navigate to Test Suites page
  await page.click('text=Test Suites');
  
  // Check that we're on the Test Suites page
  await expect(page).toHaveURL(/.*test-suites/);
  await expect(page.locator('h1')).toContainText('Test Suites');
  
  // Navigate to Test Cases page
  await page.click('text=Test Cases');
  
  // Check that we're on the Test Cases page
  await expect(page).toHaveURL(/.*test-cases/);
  await expect(page.locator('h1')).toContainText('Test Cases');
  
  // Navigate to Test Runs page
  await page.click('text=Test Runs');
  
  // Check that we're on the Test Runs page
  await expect(page).toHaveURL(/.*test-runs/);
  await expect(page.locator('h1')).toContainText('Test Runs');
  
  // Navigate to Reports page
  await page.click('text=Reports');
  
  // Check that we're on the Reports page
  await expect(page).toHaveURL(/.*reports/);
  await expect(page.locator('h1')).toContainText('Test Reports');
});
