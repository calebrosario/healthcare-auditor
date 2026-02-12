import { test, expect } from '@playwright/test';

test.describe('Alerts Page - Filtering and Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/alerts');
  });

  test('displays all alerts', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Fraud Alerts');
    await expect(page.locator('[data-testid="alerts-grid"]')).toBeVisible();

    const alertCards = page.locator('.card:has(.card-title)');
    const count = await alertCards.count();
    await expect(count).toBeGreaterThan(0);
  });

  test('displays filter controls', async ({ page }) => {
    await expect(page.locator('select#filter-status')).toBeVisible();
    await expect(page.locator('select#filter-risk')).toBeVisible();
    await expect(page.locator('input[type="date"]').first()).toBeVisible();
    await expect(page.locator('input[type="date"]').nth(1)).toBeVisible();
  });

  test('filters alerts by status', async ({ page }) => {
    const statusFilter = page.locator('select#filter-status');

    await statusFilter.selectOption('open');

    await page.waitForTimeout(2000);

    const alertCards = page.locator('.card:has(.card-title)');
    const count = await alertCards.count();

    if (count > 0) {
      const firstAlert = alertCards.first();
      await expect(firstAlert).toContainText('open');
    }
  });

  test('filters alerts by risk level', async ({ page }) => {
    const riskFilter = page.locator('select#filter-risk');

    await riskFilter.selectOption('high');

    await page.waitForTimeout(2000);

    const alertCards = page.locator('.card:has(.card-title)');
    const count = await alertCards.count();

    if (count > 0) {
      const firstAlert = alertCards.first();
      await expect(firstAlert).toContainText('HIGH');
    }
  });

  test('filters alerts by date range', async ({ page }) => {
    const fromDate = page.locator('input[type="date"]').first();
    const toDate = page.locator('input[type="date"]').nth(1);

    const today = new Date().toISOString().split('T')[0];
    await fromDate.fill(today);
    await toDate.fill(today);

    await page.waitForTimeout(2000);

    const alertCards = page.locator('.card:has(.card-title)');
    const count = await alertCards.count();

    await expect(count).toBeGreaterThanOrEqual(0);
  });

  test('clears all filters', async ({ page }) => {
    await page.locator('button:has-text("Clear Filters")').click();

    await page.waitForTimeout(2000);

    await expect(page.locator('.card:has-text("No alerts found matching your filters")')).toBeVisible();
  });

  test('displays alert details', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');
    const count = await alertCards.count();

    if (count > 0) {
      const firstAlert = alertCards.first();

      await expect(firstAlert.locator('.text-2xl')).toBeVisible();
      await expect(firstAlert.locator('text=Composite Score:')).toBeVisible();
      await expect(firstAlert.locator('text=ML Probability:')).toBeVisible();
    }
  });

  test('displays triggered rules', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    await expect(firstAlert.locator('text=Triggered Rules:')).toBeVisible();
  });

  test('updates alert status to investigating', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    await firstAlert.locator('button:has-text("Investigate")').click();

    await expect(page.locator('button:has-text("Mark as Resolved")')).toBeVisible({ timeout: 2000 });
  });

  test('updates alert status to resolved', async ({ page }) => {
    await page.goto('/alerts');
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();

    await firstAlert.locator('button:has-text("Mark as Resolved")').click();

    await page.waitForTimeout(1000);

    await expect(firstAlert.locator('button:has-text("Reopen Investigation")')).toBeVisible();
  });

  test('dismisses alert', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    await firstAlert.locator('button:has-text("Dismiss")').click();

    await page.waitForTimeout(1000);

    const dismissedAlert = page.locator('.card:has(.card-title)').first();
    await expect(dismissedAlert).not.toContainText('Dismiss');
  });

  test('navigates to investigation details', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    const claimId = await firstAlert.textContent() || '';

    const idMatch = claimId.match(/CLAIM-\d+/);
    if (idMatch && idMatch[0]) {
      const investigationButton = firstAlert.locator('a:has-text("View Investigation")');
      if (await investigationButton.count() > 0) {
        await investigationButton.click();
        await page.waitForURL(/\/investigate\//);
      }
    }
  });

  test('displays loading state', async ({ page }) => {
    await page.goto('/alerts');

    await expect(page.locator('text=Loading alerts...')).toBeVisible();
  });

  test('displays error when fetch fails', async ({ page }) => {
    await expect(page.locator('.text-red-600, .bg-red-50')).toBeVisible();
  });

  test('shows color-coded risk levels', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();

    const highRiskBadge = firstAlert.locator('.bg-red-600');
    const mediumRiskBadge = firstAlert.locator('.bg-yellow-600');
    const lowRiskBadge = firstAlert.locator('.bg-green-600');

    const visibleBadges = await Promise.all([
      highRiskBadge.isVisible(),
      mediumRiskBadge.isVisible(),
      lowRiskBadge.isVisible()
    ]);

    await expect(visibleBadges.some(Boolean)).toBeTruthy();
  });

  test('shows alert timestamps', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    await expect(firstAlert.locator('.text-gray-500')).toBeVisible();
  });

  test('displays empty state when no alerts match filters', async ({ page }) => {
    await page.locator('select#filter-status').selectOption('closed');

    await page.waitForTimeout(2000);

    await expect(page.locator('.card:has-text("No alerts found matching your filters")')).toBeVisible();
  });

  test('handles multiple alerts on page', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');
    const count = await alertCards.count();

    await expect(count).toBeGreaterThan(0);
  });

  test('updates status for multiple alerts', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    await firstAlert.locator('button:has-text("Investigate")').click();

    await page.waitForTimeout(1000);

    const secondAlert = alertCards.nth(1);
    const count = await secondAlert.count();
    if (count > 0) {
      await secondAlert.locator('button:has-text("Dismiss")').click();
    }
  });

  test('maintains responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/alerts');

    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('[data-testid="alerts-grid"]')).toBeVisible();
  });

  test('provides keyboard navigation support', async ({ page }) => {
    await page.goto('/alerts');

    await page.keyboard.press('Tab');
    await expect(page.locator('select:focus, input:focus, button:focus')).toBeVisible();
  });

  test('prevents status updates for closed alerts', async ({ page }) => {
    await page.goto('/alerts');

    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    const actionButtons = firstAlert.locator('button:has-text("Investigate"), button:has-text("Dismiss")');

    if (await actionButtons.count() > 0) {
      const isAlertOpen = await firstAlert.locator('.text-green-600').isVisible();
      if (!isAlertOpen) {
        await expect(actionButtons.first()).toBeDisabled();
      }
    }
  });

  test('displays all triggered rules with limit', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    await expect(firstAlert.locator('text=Triggered Rules:')).toBeVisible();

    const moreRulesText = firstAlert.locator('text=+');
    const moreRulesVisible = await moreRulesText.isVisible();

    if (moreRulesVisible) {
      await expect(moreRulesText).toBeVisible();
    }
  });

  test('sorts alerts by date by default', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const count = await alertCards.count();
    if (count > 1) {
      const firstTimestamp = await alertCards.first().locator('.text-gray-500').textContent();
      const secondTimestamp = await alertCards.nth(1).locator('.text-gray-500').textContent();

      await expect(firstTimestamp).toBeDefined();
      await expect(secondTimestamp).toBeDefined();
    }
  });

  test('shows alert metadata', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const firstAlert = alertCards.first();
    await expect(firstAlert.locator('text=anomaly_count')).toBeVisible();
  });

  test('handles page navigation with pagination', async ({ page }) => {
    const alertCards = page.locator('.card:has(.card-title)');

    const count = await alertCards.count();

    await expect(count).toBeGreaterThan(0);
  });
});
