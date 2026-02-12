# Investigate Page - TDD Specification

## User Journeys

### Journey 1: View Bill Investigation Details
**As a healthcare auditor, I want to view comprehensive investigation details for a flagged bill, so that I can understand the fraud risk, validation results, and audit trail.**

### Journey 2: Navigate Back to Alerts
**As a healthcare auditor, I want to navigate back to the alerts list, so that I can continue reviewing other flagged bills.**

### Journey 3: Review All Investigation Data
**As a healthcare auditor, I want to see bill details, validation results, and audit trail in a single view, so that I have complete context for making decisions.**

---

## Test Cases

### Unit Tests - InvestigatePage Component

```typescript
describe('InvestigatePage Component', () => {
  const mockInvestigationData: InvestigationResult = {
    bill: {
      claim_id: 'CLAIM-001',
      patient_id: 'PAT-001',
      patient_name: 'John Doe',
      provider_id: '1234567890',
      provider_name: 'Dr. Smith',
      service_date: '2026-01-15',
      bill_date: '2026-01-15',
      procedure_code: '99214',
      diagnosis_code: 'I10',
      billed_amount: 150.00,
      facility_name: 'City Hospital',
      facility_type: 'Hospital',
      documentation_text: 'Patient examination',
    },
    validation: {
      claim_id: 'CLAIM-001',
      fraud_score: 0.85,
      fraud_risk_level: 'high',
      compliance_score: 0.65,
      issues: ['Anomaly detected'],
      warnings: ['Documentation is brief'],
      code_violations: [],
      ml_fraud_probability: 0.9,
      network_risk_score: 0.75,
      anomaly_flags: [
        {
          type: 'z_score_outlier',
          message: 'Amount is 3 SD above mean',
          anomaly_score: 0.9,
          threshold: 0.8,
        }
      ],
      ml_predictions: [
        {
          model_type: 'RandomForest',
          is_fraud: true,
          fraud_probability: 0.9,
          confidence: 0.95,
        }
      ],
      phase4_stats: null,
      composite_score: 0.85,
      execution_time_ms: 1234,
    },
    knowledge_graph: {
      nodes: [],
      links: [],
    },
    timeline: [],
    provider_network: {
      nodes: [],
      links: [],
    },
    audit_trail: [
      {
        timestamp: '2026-01-15T10:00:00Z',
        action: 'Bill validated',
        actor: 'system',
        details: 'Initial validation completed',
      },
    ],
  }

  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
  }

  describe('Initial State', () => {
    it('shows loading state initially', () => {
      render(<InvestigatePage />, { wrapper: Router })
      expect(screen.getByText('Loading investigation...')).toBeInTheDocument()
    })

    it('fetches investigation data on mount with id param', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)
      const mockParams = { id: 'CLAIM-001' }

      render(<InvestigatePage />, {
        wrapper: ({ children }) => (
          <Route path="/investigate/:id" element={children}>
            <MemoryRouter initialEntries={['/investigate/CLAIM-001']}>
              <Routes />
            </MemoryRouter>
          </Route>
        ),
      })

      await waitFor(() => {
        expect(api.getInvestigation).toHaveBeenCalledWith('CLAIM-001')
      })
    })
  })

  describe('Loading State', () => {
    it('renders loading message', () => {
      jest.spyOn(api, 'getInvestigation').mockImplementation(
        () => new Promise(() => {})
      )

      render(<InvestigatePage />)

      expect(screen.getByText('Loading investigation...')).toBeInTheDocument()
    })

    it('does not render investigation data while loading', () => {
      jest.spyOn(api, 'getInvestigation').mockImplementation(
        () => new Promise(() => {})
      )

      render(<InvestigatePage />)

      expect(screen.queryByText('Bill Details')).not.toBeInTheDocument()
    })
  })

  describe('Bill Details Section', () => {
    beforeEach(() => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)
    })

    it('displays claim ID', async () => {
      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('CLAIM-001')).toBeInTheDocument()
      })
    })

    it('displays patient information', async () => {
      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Patient:')).toBeInTheDocument()
        expect(screen.getByText('John Doe (PAT-001)')).toBeInTheDocument()
      })
    })

    it('displays provider information', async () => {
      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Provider:')).toBeInTheDocument()
        expect(screen.getByText('Dr. Smith (1234567890)')).toBeInTheDocument()
      })
    })

    it('displays service and bill dates', async () => {
      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Service Date:')).toBeInTheDocument()
        expect(screen.getByText('Bill Date:')).toBeInTheDocument()
      })
    })

    it('displays procedure and diagnosis codes', async () => {
      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Procedure:')).toBeInTheDocument()
        expect(screen.getByText('99214')).toBeInTheDocument()
        expect(screen.getByText('Diagnosis:')).toBeInTheDocument()
        expect(screen.getByText('I10')).toBeInTheDocument()
      })
    })

    it('displays billed amount', async () => {
      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Amount:')).toBeInTheDocument()
        expect(screen.getByText('$150.00')).toBeInTheDocument()
      })
    })
  })

  describe('Validation Results Section', () => {
    it('displays risk level with correct color', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Risk Level: HIGH')).toBeInTheDocument()
        const riskLevelContainer = screen.getByText('Risk Level: HIGH').closest('.bg-red-50')
        expect(riskLevelContainer).toBeInTheDocument()
      })
    })

    it('displays composite score', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('0.85')).toBeInTheDocument()
      })
    })

    it('displays N/A when composite score is null', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue({
        ...mockInvestigationData,
        validation: { ...mockInvestigationData.validation, composite_score: null },
      })

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('N/A')).toBeInTheDocument()
      })
    })

    it('displays anomaly flags when present', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Anomaly Flags')).toBeInTheDocument()
        expect(screen.getByText('z_score_outlier')).toBeInTheDocument()
        expect(screen.getByText('Amount is 3 SD above mean')).toBeInTheDocument()
      })
    })

    it('displays ML predictions when present', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('ML Predictions')).toBeInTheDocument()
        expect(screen.getByText('RandomForest')).toBeInTheDocument()
        expect(screen.getByText('Is Fraud: Yes')).toBeInTheDocument()
      })
    })

    it('displays code violations when present', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue({
        ...mockInvestigationData,
        validation: {
          ...mockInvestigationData.validation,
          code_violations: [
            {
              violation_type: 'Invalid CPT',
              message: 'CPT code not valid',
              severity: 'error',
            },
          ],
        },
      })

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Code Violations')).toBeInTheDocument()
        expect(screen.getByText('Invalid CPT')).toBeInTheDocument()
      })
    })
  })

  describe('Audit Trail Section', () => {
    it('displays audit trail entries', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Audit Trail')).toBeInTheDocument()
        expect(screen.getByText('Bill validated')).toBeInTheDocument()
        expect(screen.getByText('Initial validation completed')).toBeInTheDocument()
      })
    })

    it('displays timestamp for each entry', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText(/2026-01-15/)).toBeInTheDocument()
      })
    })

    it('displays actor and action for each entry', async () => {
      jest.spyOn(api, 'getInvestigation').mockResolvedValue(mockInvestigationData)

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('system')).toBeInTheDocument()
        expect(screen.getByText('Bill validated')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('shows error message when API call fails', async () => {
      jest.spyOn(api, 'getInvestigation').mockRejectedValue(
        new Error('Failed to load investigation')
      )

      render(<InvestigatePage />)

      await waitFor(() => {
        expect(screen.getByText('Failed to load investigation')).toBeInTheDocument()
      })
    })

    it('handles missing id parameter', async () => {
      const mockParams = { id: undefined }

      render(<InvestigatePage />, {
        wrapper: ({ children }) => (
          <Route path="/investigate/:id" element={children}>
            <MemoryRouter initialEntries={['/investigate']}>
              <Routes />
            </MemoryRouter>
          </Route>
        ),
      })

      // Should not crash or attempt API call without id
      expect(api.getInvestigation).not.toHaveBeenCalled()
    })
  })
})
```

---

## Implementation Requirements

### Component Structure
1. **Main InvestigatePage component** - Client component using 'use client'
2. **State management** using React.useState for:
   - `investigation`: InvestigationResult | null for investigation data
   - `loading`: boolean for loading state
   - `error`: string for error messages
3. **URL parameter extraction** using `useParams()` hook

### Functional Requirements
1. **Data Fetching**
   - Extract `id` parameter from URL using `useParams()`
   - Call `api.getInvestigation(id)` on mount if id exists
   - Update investigation state with fetched data
   - Handle loading, error, and success states appropriately

2. **Conditional Rendering**
   - Show loading state when `loading` is true
   - Return null if no investigation data
   - Show investigation details when data is available

3. **Back Navigation**
   - Use `history.back()` or Next.js router to navigate back
   - Provide clear visual indicator (← Back to Alerts)

4. **Section Display**
   - Bill Details: Show all bill information in a Card
   - Validation Results: Show risk level, scores, anomalies, ML predictions, violations
   - Audit Trail: Show timeline of actions with timestamps, actors, and details

### JSX Requirements
1. **Use JSX syntax** instead of React.createElement
2. **Proper element nesting** with opening/closing tags
3. **Fragment usage** where appropriate
4. **Correct prop passing** to Card and Button components
5. **Event handlers** with proper typing:
   - `onClick: () => void`
6. **Dynamic route handling** with `useParams()` hook

### Styling Requirements
- Use Tailwind CSS classes
- Responsive grid layout for details and results
- Proper spacing and visual hierarchy
- Risk level color coding (red=high, yellow=medium, green=low)
- Severity-based styling for violations
- Audit trail with timestamp formatting

### Type Safety
- All state must be properly typed with InvestigationResult interface
- Event handlers must have correct TypeScript types
- URL parameter must be typed as string or undefined
- No `as any` or type suppression

### Data Display Requirements
1. **Bill Information**
   - Claim ID
   - Patient name and ID
   - Provider name and ID (NPI)
   - Service date (formatted)
   - Bill date (formatted)
   - Procedure code
   - Diagnosis code
   - Billed amount (formatted as currency)

2. **Validation Results**
   - Risk level (HIGH/MEDIUM/LOW) with color coding
   - Composite score (or N/A if not available)
   - Anomaly flags with scores and thresholds
   - ML predictions with fraud probability and confidence
   - Code violations with severity and messages

3. **Audit Trail**
   - Timestamp (formatted as locale date string)
   - Action performed
   - Actor who performed action
   - Details of the action

---

## Edge Cases to Test

1. **Missing ID parameter** - Handle when id is undefined
2. **Invalid ID parameter** - Handle API errors for non-existent investigation
3. **Empty investigation data** - Handle when API returns incomplete data
4. **Null/undefined values** - Handle missing optional fields
5. **Large audit trail** - Handle many audit entries without performance issues
6. **No validation results** - Handle when validation data is missing
7. **Empty arrays** - Handle empty violations, flags, predictions
8. **Date formatting errors** - Handle invalid date strings
9. **API timeout** - Handle slow or unresponsive API
10. **Network errors** - Handle failed API calls gracefully

---

## Success Criteria

1. ✅ All unit tests pass (0 failures)
2. ✅ Test coverage ≥ 80%
3. ✅ No TypeScript compilation errors
4. ✅ All sections display data correctly
5. ✅ Loading state shows appropriately
6. ✅ Error messages display correctly
7. ✅ JSX syntax used throughout (no React.createElement)
8. ✅ Back navigation works correctly
9. ✅ Dynamic route parameter extraction works
10. ✅ All investigation data types handled correctly
