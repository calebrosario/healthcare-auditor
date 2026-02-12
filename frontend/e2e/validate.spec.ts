import { test, expect } from '@playwright/test';

test.describe('Validate Page - Bill Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/validate');
  });

  test('displays all form fields', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Validate Bill');

    await expect(page.locator('label:has-text("Patient Name")')).toBeVisible();
    await expect(page.locator('input#patient_name')).toBeVisible();

    await expect(page.locator('label:has-text("Patient ID")')).toBeVisible();
    await expect(page.locator('input#patient_id')).toBeVisible();

    await expect(page.locator('label:has-text("Provider Name")')).toBeVisible();
    await expect(page.locator('input#provider_name')).toBeVisible();

    await expect(page.locator('label:has-text("Provider ID (NPI)")')).toBeVisible();
    await expect(page.locator('input#provider_id')).toBeVisible();

    await expect(page.locator('label:has-text("Service Date")')).toBeVisible();
    await expect(page.locator('input#service_date')).toBeVisible();

    await expect(page.locator('label:has-text("Bill Date")')).toBeVisible();
    await expect(page.locator('input#bill_date')).toBeVisible();

    await expect(page.locator('label:has-text("Procedure Code (CPT)")')).toBeVisible();
    await expect(page.locator('input#procedure_code')).toBeVisible();

    await expect(page.locator('label:has-text("Diagnosis Code (ICD-10)")')).toBeVisible();
    await expect(page.locator('input#diagnosis_code')).toBeVisible();

    await expect(page.locator('label:has-text("Billed Amount ($)")')).toBeVisible();
    await expect(page.locator('input#billed_amount')).toBeVisible();

    await expect(page.locator('label:has-text("Documentation Text")')).toBeVisible();
    await expect(page.locator('textarea#documentation_text')).toBeVisible();
  });

  test('initializes dates with today\'s date', async ({ page }) => {
    const today = new Date().toISOString().split('T')[0];

    await expect(page.locator('input#service_date')).toHaveValue(today);
    await expect(page.locator('input#bill_date')).toHaveValue(today);
  });

  test('allows entering all bill information', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#patient_id').fill('PATIENT-001');
    await page.locator('input#provider_name').fill('Dr. Smith');
    await page.locator('input#provider_id').fill('1234567890');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');
    await page.locator('textarea#documentation_text').fill('Routine office visit');

    await expect(page.locator('input#patient_name')).toHaveValue('John Doe');
    await expect(page.locator('input#patient_id')).toHaveValue('PATIENT-001');
    await expect(page.locator('input#provider_name')).toHaveValue('Dr. Smith');
  });

  test('submits bill for validation', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#provider_id').fill('1234567890');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');
    await page.locator('textarea#documentation_text').fill('Routine office visit');

    await page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('[data-testid="validation-results"]')).toBeVisible({ timeout: 5000 });
  });

  test('displays validation results with risk level', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');

    await page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('.card:has-text("Risk Level")')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('[data-testid="risk-level"]')).toBeVisible();
  });

  test('displays triggered rules', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');

    await page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('[data-testid="triggered-rules"]')).toBeVisible({ timeout: 5000 });
  });

  test('displays ML predictions', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');

    await page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('[data-testid="ml-predictions"]')).toBeVisible({ timeout: 5000 });
  });

  test('shows loading state during validation', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');

    await page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('button:has-text("Validating...")')).toBeVisible({ timeout: 1000 });
  });

  test('validates required fields are filled', async ({ page }) => {
    await page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('text=Please fill in all required fields')).toBeVisible({ timeout: 2000 });
  });

  test('clears form after submission', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');
    await page.locator('textarea#documentation_text').fill('Routine office visit');

    await page.locator('button:has-text("Validate Bill")').click();

    await page.locator('button:has-text("Validate Another Bill")').click();

    await expect(page.locator('input#patient_name')).toHaveValue('');
    await expect(page.locator('input#procedure_code')).toHaveValue('');
  });

  test('displays error when validation fails', async ({ page }) => {
    await expect(page.locator('.text-red-600, .bg-red-50')).toBeVisible();
  });

  test('provides navigation to alerts from validation results', async ({ page }) => {
    await page.locator('input#patient_name').fill('John Doe');
    await page.locator('input#procedure_code').fill('99214');
    await page.locator('input#diagnosis_code').fill('I10');
    await page.locator('input#billed_amount').fill('150.00');

    await page.locator('button:has-text("Validate Bill")').click();

    await expect(page.locator('a:has-text("View Alerts")')).toBeVisible({ timeout: 5000 });
  });

  test('validates billed amount is positive number', async ({ page }) => {
    const billedAmount = page.locator('input#billed_amount');

    await billedAmount.fill('-10');

    await expect(billedAmount).toHaveAttribute('min', '0');
    await expect(billedAmount).toHaveAttribute('step', '0.01');
  });

  test('validates provider ID (NPI) format', async ({ page }) => {
    const providerId = page.locator('input#provider_id');

    await expect(providerId).toHaveAttribute('minlength', '10');
    await expect(providerId).toHaveAttribute('maxlength', '10');
  });

  test('validates procedure code (CPT) format', async ({ page }) => {
    const procedureCode = page.locator('input#procedure_code');

    await expect(procedureCode).toHaveAttribute('minlength', '5');
    await expect(procedureCode).toHaveAttribute('maxlength', '5');
  });

  test('validates diagnosis code (ICD-10) format', async ({ page }) => {
    const diagnosisCode = page.locator('input#diagnosis_code');

    await expect(diagnosisCode).toHaveAttribute('minlength', '3');
    await expect(diagnosisCode).toHaveAttribute('maxlength', '10');
  });
});
