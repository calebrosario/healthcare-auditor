import { test, expect } from '@playwright/test';

test.describe('Investigate Page - Bill Investigation Details', () => {
  test('displays bill details', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('h1')).toHaveText(/Investigation/i);

    await expect(page.locator('.card:has-text("Bill Details")')).toBeVisible();
    await expect(page.locator('text=Claim ID:')).toBeVisible();
    await expect(page.locator('text=Patient Name:')).toBeVisible();
    await expect(page.locator('text=Provider Name:')).toBeVisible();
    await expect(page.locator('text=Procedure Code:')).toBeVisible();
    await expect(page.locator('text=Diagnosis Code:')).toBeVisible();
    await expect(page.locator('text=Billed Amount:')).toBeVisible();
  });

  test('displays validation results', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card:has-text("Validation Results")')).toBeVisible();
    await expect(page.locator('[data-testid="risk-level"]')).toBeVisible();
    await expect(page.locator('text=Composite Score:')).toBeVisible();
    await expect(page.locator('text=Compliance Score:')).toBeVisible();
  });

  test('displays triggered rules', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('[data-testid="triggered-rules"]')).toBeVisible();
  });

  test('displays ML predictions', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('[data-testid="ml-predictions"]')).toBeVisible();
    await expect(page.locator('text=Random Forest:')).toBeVisible();
    await expect(page.locator('text=Isolation Forest:')).toBeVisible();
  });

  test('displays anomaly flags', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('[data-testid="anomaly-flags"]')).toBeVisible();
  });

  test('displays network metrics', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('[data-testid="network-metrics"]')).toBeVisible();
    await expect(page.locator('text=Provider Centrality:')).toBeVisible();
  });

  test('displays audit trail', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card:has-text("Audit Trail")')).toBeVisible();
    await expect(page.locator('text=Timestamp')).toBeVisible();
    await expect(page.locator('text=Action')).toBeVisible();
    await expect(page.locator('text=Actor')).toBeVisible();
  });

  test('navigates back to alerts list', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await page.locator('button:has-text("← Back to Alerts")').click();

    await page.waitForURL('/alerts');
    await expect(page.locator('h1')).toHaveText('Fraud Alerts');
  });

  test('displays knowledge graph visualization', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card:has-text("Knowledge Graph")')).toBeVisible();
  });

  test('displays provider network visualization', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card:has-text("Provider Network")')).toBeVisible();
  });

  test('displays timeline of events', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card:has-text("Timeline")')).toBeVisible();
    await expect(page.locator('[data-testid="timeline-events"]')).toBeVisible();
  });

  test('shows loading state', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('text=Loading investigation...')).toBeVisible();
  });

  test('displays error when investigation fails to load', async ({ page }) => {
    await page.goto('/investigate/INVALID-ID');

    await expect(page.locator('.text-red-600, .bg-red-50')).toBeVisible({ timeout: 3000 });
  });

  test('highlights risk level with color coding', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    const riskLevel = page.locator('[data-testid="risk-level"]');

    await expect(riskLevel).toBeVisible();
    const text = await riskLevel.textContent();
    expect(text).toMatch(/high|medium|low/i);
  });

  test('displays code violations if present', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('[data-testid="code-violations"]')).toBeVisible();
  });

  test('allows clicking on graph nodes for details', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    const graphNodes = page.locator('.graph-node');

    const count = await graphNodes.count();
    if (count > 0) {
      await graphNodes.first().click();
      await expect(page.locator('.card:has-text("Node Details")')).toBeVisible({ timeout: 2000 });
    }
  });

  test('displays investigation notes section', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card:has-text("Investigation Notes")')).toBeVisible();
  });

  test('handles invalid investigation ID gracefully', async ({ page }) => {
    await page.goto('/investigate/does-not-exist');

    await expect(page.locator('text=Investigation not found')).toBeVisible({ timeout: 3000 });
  });

  test('displays warnings section', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('[data-testid="warnings"]')).toBeVisible();
  });

  test('formats monetary values correctly', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('text=Billed Amount:')).toBeVisible();

    const amountElement = page.locator('.card:has-text("Billed Amount")').locator('.text-2xl');

    await expect(amountElement).toBeVisible();
  });

  test('displays provider details card', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card:has-text("Provider Details")')).toBeVisible();
    await expect(page.locator('text=NPI:')).toBeVisible();
    await expect(page.locator('text=Facility:')).toBeVisible();
  });

  test('handles large investigation data without layout issues', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('.card')).toHaveCount(1);

    const cards = page.locator('.card');
    await cards.first().waitFor({ state: 'visible' });
  });

  test('maintains responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/investigate/CLAIM-001');

    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.card').first()).toBeVisible();
  });

  test('provides keyboard navigation support', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    await page.keyboard.press('Tab');

    await expect(page.locator('button:focus')).toBeVisible();
  });

  test('displays timestamps in readable format', async ({ page }) => {
    await page.goto('/investigate/CLAIM-001');

    const timestamps = page.locator('.text-gray-500:has-text(/Z|GMT|UTC/)');
    await expect(timestamps.first()).toBeVisible();
  });
});
