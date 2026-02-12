import { test, expect, Page } from '@playwright/test';

test.describe('Healthcare Auditor - Critical User Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('Dashboard loads and displays statistics', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('h1')).toHaveText(/Healthcare Auditor Dashboard/i);
    await expect(page.locator('text=Healthcare billing fraud detection')).toBeVisible();
    await expect(page.locator('[data-testid="stats-grid"]')).toBeVisible();

    await expect(page.locator('.card:has-text("Overview")')).toBeVisible();
    await expect(page.locator('.card:has-text("Total Bills")')).toBeVisible();
    await expect(page.locator('.card:has-text("Fraud Detected")')).toBeVisible();
  });

  test('Validate bill page shows form and submits successfully', async ({ page }) => {
    await page.goto('/validate');

    await expect(page.locator('h1')).toHaveText('Validate Bill');
    await expect(page.locator('input#patient_name')).toBeVisible();
    await expect(page.locator('input#provider_name')).toBeVisible();
    await expect(page.locator('input#provider_id')).toBeVisible();
    await expect(page.locator('input#service_date')).toBeVisible();
    await expect(page.locator('input#bill_date')).toBeVisible();
    await expect(page.locator('input#procedure_code')).toBeVisible();
    await expect(page.locator('input#diagnosis_code')).toBeVisible();
    await expect(page.locator('input#billed_amount')).toBeVisible();
    await expect(page.locator('input#documentation_text')).toBeVisible();

    page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('[data-testid="validation-results"]')).toBeVisible({ timeout: 5000 });

    await expect(page.locator('.card:has-text("Risk Level")')).toBeVisible();
    await expect(page.locator('[data-testid="risk-level"]')).toBeVisible();
  });

  test('Alerts page displays list and filtering works', async ({ page }) => {
    await page.goto('/alerts');

    await expect(page.locator('h1')).toHaveText('Fraud Alerts');
    await expect(page.locator('[data-testid="alerts-grid"]')).toBeVisible();

    await expect(page.locator('select#filter-status')).toBeVisible();
    await expect(page.locator('select#filter-risk')).toBeVisible();

    page.locator('button:has-text("Clear Filters")').click();

    await page.waitForTimeout(2000);

    await expect(page.locator('.card:has-text("No alerts found matching your filters")')).toBeVisible();
  });

  test('Settings page allows configuration', async ({ page }) => {
    await page.goto('/settings');

    await expect(page.locator('h1')).toHaveText('Settings');

    await expect(page.locator('label:has-text("Low Fraud Probability Threshold (%)")')).toBeVisible();
    await expect(page.locator('input#ml_threshold_low')).toBeVisible();
    await expect(page.locator('input#ml_threshold_high')).toBeVisible();

    await expect(page.locator('label:has-text("Anomaly Detection Sensitivity")')).toBeVisible();
    await expect(page.locator('select#anomaly_sensitivity')).toBeVisible();

    await expect(page.locator('label:has-text("Risk Scoring Weights")')).toBeVisible();

    await expect(page.locator('input#anomaly_score')).toBeVisible();
    await expect(page.locator('input#ml_probability')).toBeVisible();
    await expect(page.locator('input#code_violations')).toBeVisible();
    await expect(page.locator('input#network_centrality')).toBeVisible();

    await expect(page.locator('input#email_alerts')).toBeVisible();

    await expect(page.locator('button:has-text("Save Settings")')).toBeVisible();

    await expect(page.locator('[data-testid="success-message"]')).toBeVisible({ timeout: 5000 });

    await page.waitForTimeout(3000);

    await expect(page.locator('.card:has-text("Settings saved successfully!")')).toBeVisible();

    page.locator('button:has-text("Reset to Defaults")').click();

    await expect(page.locator('[data-testid="settings-reset"]')).toBeVisible({ timeout: 5000 });
  });
});
