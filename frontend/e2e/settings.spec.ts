import { test, expect } from '@playwright/test';

test.describe('Settings Page - Configuration Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
  });

  test('displays all ML detection settings', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Settings');

    await expect(page.locator('label:has-text("Low Fraud Probability Threshold (%)")')).toBeVisible();
    await expect(page.locator('input#ml_threshold_low')).toBeVisible();
    await expect(page.locator('label:has-text("High Fraud Probability Threshold (%)")')).toBeVisible();
    await expect(page.locator('input#ml_threshold_high')).toBeVisible();
    await expect(page.locator('label:has-text("Anomaly Detection Sensitivity")')).toBeVisible();
    await expect(page.locator('select#anomaly_sensitivity')).toBeVisible();
  });

  test('displays all risk scoring weights', async ({ page }) => {
    await expect(page.locator('label:has-text("Risk Scoring Weights")')).toBeVisible();

    await expect(page.locator('label:has-text("Anomaly Score Weight (%)")')).toBeVisible();
    await expect(page.locator('input#anomaly_score')).toBeVisible();
    await expect(page.locator('label:has-text("ML Probability Weight (%)")')).toBeVisible();
    await expect(page.locator('input#ml_probability')).toBeVisible();
    await expect(page.locator('label:has-text("Code Violations Weight (%)")')).toBeVisible();
    await expect(page.locator('input#code_violations')).toBeVisible();
    await expect(page.locator('label:has-text("Network Centrality Weight (%)")')).toBeVisible();
    await expect(page.locator('input#network_centrality')).toBeVisible();
  });

  test('displays notification preferences', async ({ page }) => {
    await expect(page.locator('label:has-text("Notification Preferences")')).toBeVisible();

    await expect(page.locator('label:has-text("Email Alerts")')).toBeVisible();
    await expect(page.locator('input#email_alerts')).toBeVisible();
    await expect(page.locator('label:has-text("SMS Alerts")')).toBeVisible();
    await expect(page.locator('input#sms_alerts')).toBeVisible();
    await expect(page.locator('label:has-text("Alert Threshold")')).toBeVisible();
    await expect(page.locator('select#alert_threshold')).toBeVisible();
  });

  test('allows changing ML threshold values', async ({ page }) => {
    const lowThreshold = page.locator('input#ml_threshold_low');
    const highThreshold = page.locator('input#ml_threshold_high');

    await lowThreshold.fill('65');
    await highThreshold.fill('90');

    await expect(lowThreshold).toHaveValue('65');
    await expect(highThreshold).toHaveValue('90');
  });

  test('allows changing anomaly sensitivity', async ({ page }) => {
    const sensitivity = page.locator('select#anomaly_sensitivity');

    await sensitivity.selectOption('high');

    await expect(sensitivity).toHaveValue('high');
  });

  test('allows changing risk weights', async ({ page }) => {
    const anomalyScore = page.locator('input#anomaly_score');
    const mlProbability = page.locator('input#ml_probability');

    await anomalyScore.fill('40');
    await mlProbability.fill('35');

    await expect(anomalyScore).toHaveValue('40');
    await expect(mlProbability).toHaveValue('35');
  });

  test('allows toggling email alerts checkbox', async ({ page }) => {
    const emailCheckbox = page.locator('input#email_alerts');

    await expect(emailCheckbox).toBeChecked();
    await emailCheckbox.click();
    await expect(emailCheckbox).not.toBeChecked();
    await emailCheckbox.click();
    await expect(emailCheckbox).toBeChecked();
  });

  test('allows toggling SMS alerts checkbox', async ({ page }) => {
    const smsCheckbox = page.locator('input#sms_alerts');

    await expect(smsCheckbox).not.toBeChecked();
    await smsCheckbox.click();
    await expect(smsCheckbox).toBeChecked();
    await smsCheckbox.click();
    await expect(smsCheckbox).not.toBeChecked();
  });

  test('saves settings successfully', async ({ page }) => {
    await page.locator('button:has-text("Save Settings")').click();

    await expect(page.locator('[data-testid="success-message"]')).toBeVisible({ timeout: 5000 });
    await page.waitForTimeout(3000);

    await expect(page.locator('.card:has-text("Settings saved successfully!")')).toBeVisible();
  });

  test('resets to default settings', async ({ page }) => {
    await page.locator('input#ml_threshold_low').fill('65');

    await page.locator('button:has-text("Reset to Defaults")').click();

    await expect(page.locator('[data-testid="settings-reset"]')).toBeVisible({ timeout: 5000 });

    await expect(page.locator('input#ml_threshold_low')).toHaveValue('70');
  });

  test('validates weight inputs prevent negative values', async ({ page }) => {
    const anomalyScore = page.locator('input#anomaly_score');

    await anomalyScore.fill('-10');

    const minValue = await anomalyScore.getAttribute('min');
    await expect(minValue).toBe('0');
  });

  test('validates threshold inputs are within range', async ({ page }) => {
    const lowThreshold = page.locator('input#ml_threshold_low');

    await expect(lowThreshold).toHaveAttribute('min', '0');
    await expect(lowThreshold).toHaveAttribute('max', '100');
  });

  test('shows loading state on save', async ({ page }) => {
    await page.locator('button:has-text("Save Settings")').click();

    await expect(page.locator('button:has-text("Saving...")')).toBeVisible({ timeout: 2000 });
  });

  test('displays error when save fails', async ({ page }) => {
    await expect(page.locator('.text-red-600, .bg-red-50')).toBeVisible();
  });
});
