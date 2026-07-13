import { test, expect } from '@playwright/test';
test('mvp navigation', async ({page})=>{await page.goto('/'); await expect(page.getByText('全国ため池広域監視MVP')).toBeVisible();});
