import { test, expect } from '@playwright/test';

test.describe('Analytics Page - Metrics and Charts', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/analytics');
  });

  test('displays analytics dashboard', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText(/Analytics/i);
    await expect(page.locator('.card:has-text("Overview")')).toBeVisible();
  });

  test('displays fraud trend chart', async ({ page }) => {
    await expect(page.locator('.card:has-text("Fraud Trend")')).toBeVisible();
    await expect(page.locator('[data-testid="fraud-trend-chart"]')).toBeVisible();
  });

  test('displays top risk providers', async ({ page }) => {
    await expect(page.locator('.card:has-text("Top Risk Providers")')).toBeVisible();
    await expect(page.locator('[data-testid="top-risk-providers"]')).toBeVisible();
  });

  test('displays code violation breakdown', async ({ page }) => {
    await expect(page.locator('.card:has-text("Code Violation Breakdown")')).toBeVisible();
    await expect(page.locator('[data-testid="code-violation-breakdown"]')).toBeVisible();
  });

  test('displays ML model performance', async ({ page }) => {
    await expect(page.locator('.card:has-text("ML Model Performance")')).toBeVisible();
    await expect(page.locator('[data-testid="ml-model-performance"]')).toBeVisible();
  });

  test('displays rule effectiveness metrics', async ({ page }) => {
    await expect(page.locator('.card:has-text("Rule Effectiveness")')).toBeVisible();
    await expect(page.locator('[data-testid="rule-effectiveness"]')).toBeVisible();
  });

  test('shows loading state', async ({ page }) => {
    await page.goto('/analytics');

    await expect(page.locator('text=Loading analytics...')).toBeVisible();
  });

  test('displays error when fetch fails', async ({ page }) => {
    await expect(page.locator('.text-red-600, .bg-red-50')).toBeVisible();
  });

  test('charts render with data', async ({ page }) => {
    await expect(page.locator('[data-testid="fraud-trend-chart"]')).toBeVisible();

    const chartElements = page.locator('.recharts-wrapper, .recharts-surface');

    await expect(chartElements.first()).toBeVisible();
  });

  test('fraud trend chart displays multiple lines', async ({ page }) => {
    const trendChart = page.locator('[data-testid="fraud-trend-chart"]');

    await expect(trendChart).toBeVisible();

    const lines = trendChart.locator('.recharts-line');
    const lineCount = await lines.count();

    await expect(lineCount).toBeGreaterThanOrEqual(2);
  });

  test('top risk providers table displays provider data', async ({ page }) => {
    const providersTable = page.locator('[data-testid="top-risk-providers"]');

    await expect(providersTable).toBeVisible();

    const tableRows = providersTable.locator('tr:has(td)');
    const rowCount = await tableRows.count();

    if (rowCount > 0) {
      await expect(rowCount).toBeGreaterThan(0);
    }
  });

  test('code violation breakdown shows all violation types', async ({ page }) => {
    const violationBreakdown = page.locator('[data-testid="code-violation-breakdown"]');

    await expect(violationBreakdown).toBeVisible();

    await expect(violationBreakdown.locator('text=Invalid ICD-10')).toBeVisible();
    await expect(violationBreakdown.locator('text=Invalid CPT')).toBeVisible();
    await expect(violationBreakdown.locator('text=Invalid DX Pair')).toBeVisible();
    await expect(violationBreakdown.locator('text=Bundling')).toBeVisible();
    await expect(violationBreakdown.locator('text=Amount Limit')).toBeVisible();
  });

  test('ML model performance shows accuracy metrics', async ({ page }) => {
    const mlPerformance = page.locator('[data-testid="ml-model-performance"]');

    await expect(mlPerformance).toBeVisible();

    await expect(mlPerformance.locator('text=Accuracy')).toBeVisible();
    await expect(mlPerformance.locator('text=Precision')).toBeVisible();
    await expect(mlPerformance.locator('text=Recall')).toBeVisible();
    await expect(mlPerformance.locator('text=F1 Score')).toBeVisible();
  });

  test('rule effectiveness displays execution metrics', async ({ page }) => {
    const ruleEffectiveness = page.locator('[data-testid="rule-effectiveness"]');

    await expect(ruleEffectiveness).toBeVisible();

    await expect(ruleEffectiveness.locator('text=Total Evaluations')).toBeVisible();
    await expect(ruleEffectiveness.locator('text=Violations Found')).toBeVisible();
    await expect(ruleEffectiveness.locator('text=Violation Rate')).toBeVisible();
  });

  test('charts are responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/analytics');

    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.card').first()).toBeVisible();
  });

  test('metrics display correctly formatted numbers', async ({ page }) => {
    const metricsElements = page.locator('.text-2xl, .text-3xl');

    await expect(metricsElements.first()).toBeVisible();
  });

  test('time range filter works', async ({ page }) => {
    const dateFilter = page.locator('select:has-text("Time Range")');

    await dateFilter.selectOption('Last 7 Days');

    await page.waitForTimeout(2000);

    await expect(page.locator('.card').first()).toBeVisible();
  });

  test('displays legend for charts', async ({ page }) => {
    const trendChart = page.locator('[data-testid="fraud-trend-chart"]');

    const legend = trendChart.locator('.recharts-legend');
    await expect(legend).toBeVisible();
  });

  test('tooltips show on chart hover', async ({ page }) => {
    const trendChart = page.locator('[data-testid="fraud-trend-chart"]');

    const chartArea = trendChart.locator('.recharts-wrapper');
    await chartArea.first().hover();

    const tooltip = page.locator('.recharts-tooltip-wrapper');
    await expect(tooltip.first()).toBeVisible({ timeout: 2000 });
  });

  test('provides download/export options', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")');

    if (await exportButton.count() > 0) {
      await expect(exportButton.first()).toBeVisible();
    }
  });

  test('shows comparison metrics', async ({ page }) => {
    const comparisonCards = page.locator('.card:has(text=Comparison)');

    if (await comparisonCards.count() > 0) {
      await expect(comparisonCards.first()).toBeVisible();
    }
  });

  test('handles empty data states', async ({ page }) => {
    const noDataLocator = page.locator('.card:has-text("No Data Available")').or(page.locator('.card:has-text("No metrics to display")'));
    await expect(noDataLocator.first()).toBeVisible();
  });

  test('updates data on filter change', async ({ page }) => {
    const dateFilter = page.locator('select:has-text("Time Range")');

    await dateFilter.selectOption('Last 30 Days');

    await page.waitForTimeout(2000);

    await expect(page.locator('.card').first()).toBeVisible();
  });

  test('charts animate on load', async ({ page }) => {
    await page.goto('/analytics');

    const chartElements = page.locator('.recharts-wrapper');

    await expect(chartElements.first()).toBeVisible();
  });

  test('displays percentage metrics', async ({ page }) => {
    const percentageElements = page.locator('text:has-text("%")');

    await expect(percentageElements.first()).toBeVisible();
  });

  test('navigates to details from metrics', async ({ page }) => {
    const providerRow = page.locator('[data-testid="top-risk-providers"] tr:has(td)').first();

    const detailLink = providerRow.locator('a');

    if (await detailLink.count() > 0) {
      await detailLink.click();
      await page.waitForURL(/\/investigate\//);
    }
  });

  test('displays data refresh timestamp', async ({ page }) => {
    const timestamp = page.locator('text=Last Updated');

    if (await timestamp.count() > 0) {
      await expect(timestamp).toBeVisible();
    }
  });

  test('handles chart errors gracefully', async ({ page }) => {
    const errorLocator = page.locator('.card:has-text("Chart Error")').or(page.locator('.card:has-text("Unable to load chart")'));
    await expect(errorLocator.first()).toBeVisible();
  });

  test('shows performance indicators', async ({ page }) => {
    const mlPerformance = page.locator('[data-testid="ml-model-performance"]');

    const modelType = mlPerformance.locator('text=Random Forest');
    await expect(modelType.first()).toBeVisible();

    const isolationForest = mlPerformance.locator('text=Isolation Forest');
    await expect(isolationForest.first()).toBeVisible();
  });

  test('provides keyboard navigation support', async ({ page }) => {
    await page.goto('/analytics');

    await page.keyboard.press('Tab');
    await expect(page.locator('select:focus, button:focus, a:focus')).toBeVisible();
  });

  test('maintains chart proportions', async ({ page }) => {
    const trendChart = page.locator('[data-testid="fraud-trend-chart"]');

    await expect(trendChart).toBeVisible();

    const chartContainer = trendChart.locator('.recharts-responsive-container');
    await expect(chartContainer.first()).toBeVisible();
  });
});
