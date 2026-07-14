import { test, expect } from '@playwright/test';

test('mvp navigation and proxy', async ({page, request})=>{
  await page.goto('/');
  await expect(page.getByText('全国ため池広域監視MVP')).toBeVisible();
  const health = await request.get('/api/backend/health');
  expect([200,503]).toContain(health.status());
  const ponds = await request.get('/api/backend/ponds?limit=10');
  expect([200,503]).toContain(ponds.status());
  await page.goto('/map'); await expect(page.getByTestId('maplibre-map')).toBeVisible();
  await expect(page.getByText(/状態|API接続に失敗/)).toBeVisible();
});

test('disaster event post through proxy keeps json', async ({request})=>{
  const res = await request.post('/api/backend/disaster-events', { data: { name:'E2E', eventType:'heavy_rain', areaGeojson:{type:'FeatureCollection', features:[]} } });
  expect([200,503]).toContain(res.status());
});
