# Validate Page - TDD Specification

## User Journeys

### Journey 1: Submit Bill for Validation
**As a healthcare auditor, I want to submit a medical bill for validation, so that I can detect potential fraud or compliance issues.**

### Journey 2: View Validation Results
**As a healthcare auditor, I want to view comprehensive validation results, so that I can understand fraud risk, rule violations, anomalies, and ML predictions.**

### Journey 3: Navigate Between Alerts and Investigation
**As a healthcare auditor, I want to navigate between alerts and investigation details, so that I can efficiently review flagged bills.**

---

## Test Cases

### Unit Tests - ValidatePage Component

```typescript
describe('ValidatePage Component', () => {
  describe('Initial State', () => {
    it('renders with default bill form values', () => {
      render(<ValidatePage />)
      expect(screen.getByLabelText('Patient Name')).toHaveValue('')
      expect(screen.getByLabelText('Patient ID')).toHaveValue('')
      expect(screen.getByLabelText('Provider Name')).toHaveValue('')
      expect(screen.getByLabelText('Provider ID (NPI)')).toHaveValue('')
      expect(screen.getByLabelText('Billed Amount ($)')).toHaveValue('0')
      expect(screen.getByLabelText('Procedure Code (CPT)')).toHaveValue('')
      expect(screen.getByLabelText('Diagnosis Code (ICD-10)')).toHaveValue('')
    })

    it('initializes service_date and bill_date with today', () => {
      const today = new Date().toISOString().split('T')[0]
      render(<ValidatePage />)
      expect(screen.getByLabelText('Service Date')).toHaveValue(today)
      expect(screen.getByLabelText('Bill Date')).toHaveValue(today)
    })

    it('does not show validation results initially', () => {
      render(<ValidatePage />)
      expect(screen.queryByText('Validation Results')).not.toBeInTheDocument()
    })
  })

  describe('Form Fields', () => {
    it('allows entering patient name', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Patient Name')
      await user.type(input, 'John Doe')
      expect(input).toHaveValue('John Doe')
    })

    it('allows entering patient ID', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Patient ID')
      await user.type(input, 'PATIENT-001')
      expect(input).toHaveValue('PATIENT-001')
    })

    it('allows entering provider name', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Provider Name')
      await user.type(input, 'Dr. Smith')
      expect(input).toHaveValue('Dr. Smith')
    })

    it('allows entering provider ID (NPI)', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Provider ID (NPI)')
      await user.type(input, '1234567890')
      expect(input).toHaveValue('1234567890')
    })

    it('allows entering procedure code', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Procedure Code (CPT)')
      await user.type(input, '99214')
      expect(input).toHaveValue('99214')
    })

    it('allows entering diagnosis code', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Diagnosis Code (ICD-10)')
      await user.type(input, 'I10')
      expect(input).toHaveValue('I10')
    })

    it('allows entering billed amount', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Billed Amount ($)')
      await user.clear(input)
      await user.type(input, '150.00')
      expect(input).toHaveValue('150.00')
    })

    it('allows entering facility name', async () => {
      render(<ValidatePage />)
      const input = screen.getByLabelText('Facility Name')
      await user.type(input, 'City Hospital')
      expect(input).toHaveValue('City Hospital')
    })

    it('allows entering documentation text', async () => {
      render(<ValidatePage />)
      const textarea = screen.getByLabelText('Documentation Text')
      await user.type(textarea, 'Patient was examined for hypertension.')
      expect(textarea).toHaveValue('Patient was examined for hypertension.')
    })

    it('marks required fields as required', () => {
      render(<ValidatePage />)
      expect(screen.getByLabelText('Patient Name')).toBeRequired()
      expect(screen.getByLabelText('Patient ID')).toBeRequired()
      expect(screen.getByLabelText('Provider Name')).toBeRequired()
      expect(screen.getByLabelText('Provider ID (NPI)')).toBeRequired()
      expect(screen.getByLabelText('Service Date')).toBeRequired()
      expect(screen.getByLabelText('Bill Date')).toBeRequired()
      expect(screen.getByLabelText('Procedure Code (CPT)')).toBeRequired()
      expect(screen.getByLabelText('Diagnosis Code (ICD-10)')).toBeRequired()
      expect(screen.getByLabelText('Billed Amount ($)')).toBeRequired()
    })

    it('facility_name and documentation_text are optional', () => {
      render(<ValidatePage />)
      expect(screen.getByLabelText('Facility Name')).not.toBeRequired()
      expect(screen.getByLabelText('Documentation Text')).not.toBeRequired()
    })
  })

  describe('Form Submission', () => {
    it('calls api.validateBill with bill data on submit', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue(mockValidationReport)

      render(<ValidatePage />)

      // Fill form
      await user.type(screen.getByLabelText('Patient Name'), 'John Doe')
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Provider Name'), 'Dr. Smith')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '1234567890')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '150')

      // Submit
      const submitButton = screen.getByRole('button', { name: 'Validate Bill' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(api.validateBill).toHaveBeenCalledWith(
          expect.objectContaining({
            patient_name: 'John Doe',
            patient_id: 'PAT-001',
            provider_name: 'Dr. Smith',
            provider_id: '1234567890',
            procedure_code: '99214',
            diagnosis_code: 'I10',
            billed_amount: 150,
          })
        )
      })
    })

    it('shows loading state during validation', async () => {
      let resolveValidation: (value: ValidationReport) => void
      jest.spyOn(api, 'validateBill').mockImplementation(
        () => new Promise(resolve => { resolveValidation = resolve })
      )

      render(<ValidatePage />)
      const submitButton = screen.getByRole('button', { name: 'Validate Bill' })
      await user.click(submitButton)

      expect(submitButton).toBeDisabled()
      expect(submitButton).toHaveTextContent('Validating...')

      await act(async () => {
        resolveValidation!(mockValidationReport)
      })
    })

    it('displays validation results after successful validation', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue(mockValidationReport)

      render(<ValidatePage />)

      // Fill and submit minimal form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('Validation Results')).toBeInTheDocument()
      })
    })

    it('shows error message when validation fails', async () => {
      const errorMessage = 'Failed to validate bill'
      jest.spyOn(api, 'validateBill').mockRejectedValue(new Error(errorMessage))

      render(<ValidatePage />)

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })

    it('clears previous results on new submission', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue(mockValidationReport)

      render(<ValidatePage />)

      // First validation
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('Validation Results')).toBeInTheDocument()
      })

      // Second validation
      jest.spyOn(api, 'validateBill').mockResolvedValueOnce(mockValidationReport)
      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      // Should only have one results section
      await waitFor(() => {
        const resultCards = screen.getAllByText('Validation Results')
        expect(resultCards).toHaveLength(1)
      })
    })
  })

  describe('Validation Results Display', () => {
    it('shows high risk level with red styling', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        risk_level: 'high',
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('Risk Level: HIGH')).toBeInTheDocument()
        expect(screen.getByText('Risk Level: HIGH').closest('.bg-red-50')).toBeInTheDocument()
      })
    })

    it('shows medium risk level with yellow styling', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        risk_level: 'medium',
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('Risk Level: MEDIUM')).toBeInTheDocument()
      })
    })

    it('displays composite score when available', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        composite_score: 0.85,
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('0.85')).toBeInTheDocument()
      })
    })

    it('displays N/A when composite score is not available', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        composite_score: null,
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('N/A')).toBeInTheDocument()
      })
    })

    it('displays execution time', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        execution_time_ms: 1234.56,
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText(/1234ms/)).toBeInTheDocument()
      })
    })

    it('displays code violations when present', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        code_violations: [
          {
            violation_type: 'Invalid CPT Code',
            message: 'CPT code 99999 is not valid',
            severity: 'error',
          },
        ],
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('Rule Violations')).toBeInTheDocument()
        expect(screen.getByText('Invalid CPT Code')).toBeInTheDocument()
        expect(screen.getByText('CPT code 99999 is not valid')).toBeInTheDocument()
      })
    })

    it('displays anomaly flags when present', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        anomaly_flags: [
          {
            type: 'z_score_outlier',
            message: 'Amount is 3 standard deviations above mean',
            anomaly_score: 0.9,
            threshold: 0.8,
          },
        ],
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('Anomaly Flags')).toBeInTheDocument()
        expect(screen.getByText('z_score_outlier:')).toBeInTheDocument()
        expect(screen.getByText('Amount is 3 standard deviations above mean')).toBeInTheDocument()
        expect(screen.getByText('Score: 0.90 (Threshold: 0.80)')).toBeInTheDocument()
      })
    })

    it('displays ML predictions when present', async () => {
      jest.spyOn(api, 'validateBill').mockResolvedValue({
        ...mockValidationReport,
        ml_predictions: [
          {
            model_type: 'RandomForest',
            is_fraud: true,
            fraud_probability: 0.85,
            confidence: 0.92,
          },
        ],
      })

      render(<ValidatePage />)

      // Submit form
      await user.type(screen.getByLabelText('Patient ID'), 'PAT-001')
      await user.type(screen.getByLabelText('Patient Name'), 'Test')
      await user.type(screen.getByLabelText('Provider ID (NPI)'), '123')
      await user.type(screen.getByLabelText('Provider Name'), 'Test')
      await user.type(screen.getByLabelText('Service Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Bill Date'), '2026-01-01')
      await user.type(screen.getByLabelText('Procedure Code (CPT)'), '99214')
      await user.type(screen.getByLabelText('Diagnosis Code (ICD-10)'), 'I10')
      await user.type(screen.getByLabelText('Billed Amount ($)'), '100')

      await user.click(screen.getByRole('button', { name: 'Validate Bill' }))

      await waitFor(() => {
        expect(screen.getByText('ML Predictions')).toBeInTheDocument()
        expect(screen.getByText('RandomForest:')).toBeInTheDocument()
        expect(screen.getByText('Is Fraud: Yes')).toBeInTheDocument()
        expect(screen.getByText('Probability: 85.0%')).toBeInTheDocument()
        expect(screen.getByText('Confidence: 92.0%')).toBeInTheDocument()
      })
    })
  })
})
```

---

## Implementation Requirements

### Component Structure
1. **Main ValidatePage component** - Client component using 'use client'
2. **State management** using React.useState for:
   - `bill`: BillSubmission object with form data
   - `loading`: boolean for submission state
   - `result`: ValidationReport | null for validation results
   - `error`: string for error messages

### Functional Requirements
1. **Form State Management**
   - All form inputs must be controlled components
   - Update bill state on input changes
   - Handle number vs string type conversion for billed_amount

2. **Form Submission**
   - Prevent default form submission
   - Call `api.validateBill(bill)`
   - Set loading state during API call
   - Set result state with validation data
   - Handle errors and show error messages

3. **Results Display**
   - Show validation results only when result is not null
   - Display risk level with appropriate color coding (red/yellow/green)
   - Display composite score (or N/A if not available)
   - Display execution time
   - List code violations with severity styling
   - List anomaly flags with scores and thresholds
   - List ML predictions with fraud probabilities

### JSX Requirements
1. **Use JSX syntax** instead of React.createElement
2. **Proper element nesting** with opening/closing tags
3. **Fragment usage** where appropriate
4. **Correct prop passing** to Card, Button, and Alert components
5. **Event handlers** with proper typing:
   - `onChange: (e: React.ChangeEvent<HTMLInputElement>) => void`
   - `onSubmit: (e: React.FormEvent) => void`

### Styling Requirements
- Use Tailwind CSS classes
- Responsive grid layout for form fields
- Proper spacing and visual hierarchy
- Risk level color coding (red=high, yellow=medium, green=low)
- Severity-based styling for violations

### Type Safety
- All state must be properly typed with BillSubmission and ValidationReport interfaces
- Event handlers must have correct TypeScript types
- No `as any` or type suppression

---

## Edge Cases to Test

1. **Empty required fields** - Browser should show validation errors
2. **Invalid date formats** - Date inputs should prevent invalid dates
3. **Negative amounts** - Billed amount should not accept negative values
4. **Very long text inputs** - Handle excessive text in documentation field
5. **API timeout** - Handle slow or unresponsive API
6. **Malformed API response** - Handle unexpected API response structure
7. **Empty results arrays** - Handle violations/flags/predictions arrays with no items
8. **Multiple violations** - Display multiple violations correctly
9. **Rapid form submissions** - Prevent multiple simultaneous submissions
10. **Partial validation results** - Handle missing optional fields in ValidationReport

---

## Success Criteria

1. ✅ All unit tests pass (0 failures)
2. ✅ Test coverage ≥ 80%
3. ✅ No TypeScript compilation errors
4. ✅ All form inputs are controlled components
5. ✅ All event handlers properly typed
6. ✅ JSX syntax used throughout (no React.createElement)
7. ✅ Loading, error, and success states properly handled
8. ✅ Validation results display correctly for all risk levels
9. ✅ Form properly submits bill data to API
10. ✅ Results display all fraud detection layers
