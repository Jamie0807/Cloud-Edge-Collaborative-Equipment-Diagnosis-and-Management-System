import { expect, test } from '@playwright/test';

test('shows the diagnostics shell and health state', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Device diagnostics' })).toBeVisible();
  await expect(page.getByText('Health: checking')).toBeVisible();
});
