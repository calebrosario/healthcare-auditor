# Settings Page - TDD Specification

## User Journeys

### Journey 1: View and Configure ML Detection Settings
**As an administrator, I want to view and configure ML detection thresholds, so that I can adjust the sensitivity of fraud detection.**

### Journey 2: Configure Risk Scoring Weights
**As an administrator, I want to configure risk scoring weights, so that I can prioritize different fraud signals according to organizational priorities.**

### Journey 3: Set Up Notification Preferences
**As an administrator, I want to configure notification preferences, so that I receive alerts at appropriate risk levels and through preferred channels.**

### Journey 4: Save Settings Changes
**As an administrator, I want to save my settings changes, so that my configuration takes effect immediately.**

### Journey 5: Reset to Default Settings
**As an administrator, I want to reset settings to defaults, so that I can quickly restore the initial configuration.**

---

## Test Cases

### Unit Tests - SettingsPage Component

```typescript
describe('SettingsPage Component', () => {
  describe('Initial State', () => {
    it('renders with default settings values', () => {
      render(<SettingsPage />)
      expect(screen.getByLabelText('Low Fraud Probability Threshold (%)')).toHaveValue('70')
      expect(screen.getByLabelText('High Fraud Probability Threshold (%)')).toHaveValue('85')
      expect(screen.getByLabelText('Anomaly Detection Sensitivity')).toHaveValue('medium')
    })

    it('shows loading state initially', () => {
      render(<SettingsPage />)
      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    it('fetches settings from API on mount', async () => {
      const mockSettings = {
        ml_threshold_low: 0.75,
        ml_threshold_high: 0.9,
        anomaly_sensitivity: 'high',
        risk_weights: { anomaly_score: 40, ml_probability: 30, code_violations: 20, network_centrality: 10 },
        notification_preferences: { email_alerts: true, sms_alerts: true, slack_webhook: '', alert_threshold: 'high' }
      }
      jest.spyOn(api, 'getSettings').mockResolvedValue(mockSettings)

      render(<SettingsPage />)
      await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument())

      expect(api.getSettings).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText('Low Fraud Probability Threshold (%)')).toHaveValue('75')
    })
  })

  describe('ML Detection Thresholds', () => {
    it('allows changing ml_threshold_low value', async () => {
      render(<SettingsPage />)
      const input = screen.getByLabelText('Low Fraud Probability Threshold (%)')

      await user.clear(input)
      await user.type(input, '0.6')

      expect(input).toHaveValue('60')  // Displayed as percentage
    })

    it('allows changing ml_threshold_high value', async () => {
      render(<SettingsPage />)
      const input = screen.getByLabelText('High Fraud Probability Threshold (%)')

      await user.clear(input)
      await user.type(input, '0.9')

      expect(input).toHaveValue('90')  // Displayed as percentage
    })

    it('allows changing anomaly_sensitivity', async () => {
      render(<SettingsPage />)
      const select = screen.getByLabelText('Anomaly Detection Sensitivity')

      await user.selectOptions(select, 'high')

      expect(select).toHaveValue('high')
    })

    it('validates ml_threshold_low is between 0 and 1', () => {
      render(<SettingsPage />)
      const input = screen.getByLabelText('Low Fraud Probability Threshold (%)')

      // Test minimum
      expect(input).toHaveAttribute('min', '0')
      expect(input).toHaveAttribute('max', '1')
    })
  })

  describe('Risk Scoring Weights', () => {
    it('allows changing anomaly_score weight', async () => {
      render(<SettingsPage />)
      const input = screen.getByLabelText('Anomaly Score Weight (%)')

      await user.clear(input)
      await user.type(input, '40')

      expect(input).toHaveValue('40')
    })

    it('allows changing ml_probability weight', async () => {
      render(<SettingsPage />)
      const input = screen.getByLabelText('ML Probability Weight (%)')

      await user.clear(input)
      await user.type(input, '35')

      expect(input).toHaveValue('35')
    })

    it('allows changing code_violations weight', async () => {
      render(<SettingsPage />)
      const input = screen.getByLabelText('Code Violations Weight (%)')

      await user.clear(input)
      await user.type(input, '25')

      expect(input).toHaveValue('25')
    })

    it('allows changing network_centrality weight', async () => {
      render(<SettingsPage />)
      const input = screen.getByLabelText('Network Centrality Weight (%)')

      await user.clear(input)
      await user.type(input, '15')

      expect(input).toHaveValue('15')
    })
  })

  describe('Notification Preferences', () => {
    it('allows toggling email_alerts', async () => {
      render(<SettingsPage />)
      const checkbox = screen.getByLabelText('Email Alerts')

      expect(checkbox).toBeChecked()

      await user.click(checkbox)

      expect(checkbox).not.toBeChecked()
    })

    it('allows toggling sms_alerts', async () => {
      render(<SettingsPage />)
      const checkbox = screen.getByLabelText('SMS Alerts')

      expect(checkbox).not.toBeChecked()

      await user.click(checkbox)

      expect(checkbox).toBeChecked()
    })

    it('allows changing alert_threshold', async () => {
      render(<SettingsPage />)
      const select = screen.getByLabelText('Alert Threshold')

      await user.selectOptions(select, 'high')

      expect(select).toHaveValue('high')
    })

    it('renders all alert threshold options', () => {
      render(<SettingsPage />)
      const select = screen.getByLabelText('Alert Threshold')

      const options = within(select).getAllByRole('option')
      expect(options).toHaveLength(4)  // 'all', 'high', 'medium', 'low'
      expect(options.map(o => o.textContent)).toEqual(expect.arrayContaining([
        'All Alerts',
        'High & Critical',
        'Medium & Above',
        'Low'
      ]))
    })
  })

  describe('Save Functionality', () => {
    it('calls api.updateSettings with current settings when Save is clicked', async () => {
      const mockUpdatedSettings = {
        ml_threshold_low: 0.6,
        ml_threshold_high: 0.85,
        anomaly_sensitivity: 'medium',
        risk_weights: { anomaly_score: 30, ml_probability: 40, code_violations: 20, network_centrality: 10 },
        notification_preferences: { email_alerts: false, sms_alerts: false, slack_webhook: '', alert_threshold: 'medium' }
      }
      jest.spyOn(api, 'updateSettings').mockResolvedValue(mockUpdatedSettings)

      render(<SettingsPage />)

      // Change a value
      const input = screen.getByLabelText('Low Fraud Probability Threshold (%)')
      await user.clear(input)
      await user.type(input, '60')

      // Save
      const saveButton = screen.getByRole('button', { name: 'Save Settings' })
      await user.click(saveButton)

      await waitFor(() => {
        expect(api.updateSettings).toHaveBeenCalledWith(
          expect.objectContaining({ ml_threshold_low: 0.6 })
        )
      })
    })

    it('shows success message after successful save', async () => {
      jest.spyOn(api, 'updateSettings').mockResolvedValue({} as Settings)

      render(<SettingsPage />)

      const saveButton = screen.getByRole('button', { name: 'Save Settings' })
      await user.click(saveButton)

      await waitFor(() => {
        expect(screen.getByText('Settings saved successfully!')).toBeInTheDocument()
      })
    })

    it('hides success message after 3 seconds', async () => {
      jest.spyOn(api, 'updateSettings').mockResolvedValue({} as Settings)
      jest.useFakeTimers()

      render(<SettingsPage />)

      const saveButton = screen.getByRole('button', { name: 'Save Settings' })
      await user.click(saveButton)

      await waitFor(() => {
        expect(screen.getByText('Settings saved successfully!')).toBeInTheDocument()
      })

      act(() => {
        jest.advanceTimersByTime(3000)
      })

      expect(screen.queryByText('Settings saved successfully!')).not.toBeInTheDocument()

      jest.useRealTimers()
    })

    it('shows error message when save fails', async () => {
      const errorMessage = 'Failed to save settings'
      jest.spyOn(api, 'updateSettings').mockRejectedValue(new Error(errorMessage))

      render(<SettingsPage />)

      const saveButton = screen.getByRole('button', { name: 'Save Settings' })
      await user.click(saveButton)

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })

    it('disables save button while loading', async () => {
      let resolveSave: (value: Settings) => void
      jest.spyOn(api, 'updateSettings').mockImplementation(
        () => new Promise(resolve => { resolveSave = resolve })
      )

      render(<SettingsPage />)

      const saveButton = screen.getByRole('button', { name: 'Save Settings' })
      await user.click(saveButton)

      expect(saveButton).toBeDisabled()

      await act(async () => {
        resolveSave!({} as Settings)
      })

      await waitFor(() => {
        expect(saveButton).not.toBeDisabled()
      })
    })
  })

  describe('Reset Functionality', () => {
    it('calls api.updateSettings with default values when Reset is clicked', async () => {
      jest.spyOn(api, 'updateSettings').mockResolvedValue({} as Settings)

      render(<SettingsPage />)

      const resetButton = screen.getByRole('button', { name: 'Reset to Defaults' })
      await user.click(resetButton)

      await waitFor(() => {
        expect(api.updateSettings).toHaveBeenCalledWith(
          expect.objectContaining({
            ml_threshold_low: 0.7,
            ml_threshold_high: 0.85,
            anomaly_sensitivity: 'medium'
          })
        )
      })
    })

    it('resets all form fields to default values', async () => {
      jest.spyOn(api, 'updateSettings').mockResolvedValue({} as Settings)

      render(<SettingsPage />)

      // Change values
      const lowInput = screen.getByLabelText('Low Fraud Probability Threshold (%)')
      await user.clear(lowInput)
      await user.type(lowInput, '90')

      const emailCheckbox = screen.getByLabelText('Email Alerts')
      await user.click(emailCheckbox)

      // Reset
      const resetButton = screen.getByRole('button', { name: 'Reset to Defaults' })
      await user.click(resetButton)

      await waitFor(() => {
        expect(lowInput).toHaveValue('70')
        expect(emailCheckbox).toBeChecked()
      })
    })

    it('shows success message after successful reset', async () => {
      jest.spyOn(api, 'updateSettings').mockResolvedValue({} as Settings)

      render(<SettingsPage />)

      const resetButton = screen.getByRole('button', { name: 'Reset to Defaults' })
      await user.click(resetButton)

      await waitFor(() => {
        expect(screen.getByText('Settings saved successfully!')).toBeInTheDocument()
      })
    })

    it('hides reset success message after 2 seconds', async () => {
      jest.spyOn(api, 'updateSettings').mockResolvedValue({} as Settings)
      jest.useFakeTimers()

      render(<SettingsPage />)

      const resetButton = screen.getByRole('button', { name: 'Reset to Defaults' })
      await user.click(resetButton)

      await waitFor(() => {
        expect(screen.getByText('Settings saved successfully!')).toBeInTheDocument()
      })

      act(() => {
        jest.advanceTimersByTime(2000)
      })

      expect(screen.queryByText('Settings saved successfully!')).not.toBeInTheDocument()

      jest.useRealTimers()
    })

    it('shows error message when reset fails', async () => {
      const errorMessage = 'Failed to reset settings'
      jest.spyOn(api, 'updateSettings').mockRejectedValue(new Error(errorMessage))

      render(<SettingsPage />)

      const resetButton = screen.getByRole('button', { name: 'Reset to Defaults' })
      await user.click(resetButton)

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('shows error when api.getSettings fails', async () => {
      const errorMessage = 'Failed to load settings'
      jest.spyOn(api, 'getSettings').mockRejectedValue(new Error(errorMessage))

      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })

    it('shows error message in prominent location', async () => {
      jest.spyOn(api, 'getSettings').mockRejectedValue(new Error('API Error'))

      render(<SettingsPage />)

      await waitFor(() => {
        const errorElement = screen.getByText('API Error')
        expect(errorElement).toBeInTheDocument()
        expect(errorElement.closest('.mb-4')).toBeInTheDocument()
      })
    })
  })
})
```

---

## Implementation Requirements

### Component Structure
1. **Main SettingsPage component** - Client component using 'use client'
2. **State management** using React.useState for:
   - `settings`: Settings object with current configuration
   - `loading`: boolean for loading state
   - `error`: string for error messages
   - `success`: boolean for success feedback

### Functional Requirements
1. **Data Fetching**
   - Call `api.getSettings()` on component mount using useEffect
   - Update settings state with fetched data
   - Handle loading, error, and success states appropriately

2. **Form State Management**
   - All form inputs must be controlled components
   - Update settings state on input changes using appropriate state updates:
     - Flat fields: `setSettings(prev => ({ ...prev, field: newValue }))`
     - Nested objects: `setSettings(prev => ({ ...prev, nested: { ...prev.nested, field: newValue }}))`

3. **Save Handler**
   - Prevent default form submission
   - Call `api.updateSettings(settings)`
   - Update settings with response data
   - Show success message for 3 seconds
   - Handle errors and show error messages
   - Set loading state during API call

4. **Reset Handler**
   - Call `api.updateSettings(defaultSettings)`
   - Reset all settings to default values:
     - `ml_threshold_low: 0.7`
     - `ml_threshold_high: 0.85`
     - `anomaly_sensitivity: 'medium'`
     - `risk_weights: { anomaly_score: 30, ml_probability: 40, code_violations: 20, network_centrality: 10 }`
     - `notification_preferences: { email_alerts: true, sms_alerts: false, slack_webhook: '', alert_threshold: 'medium' }`
   - Show success message for 2 seconds
   - Handle errors and show error messages

### JSX Requirements
1. **Use JSX syntax** instead of React.createElement
2. **Proper element nesting** with opening/closing tags
3. **Fragment usage** where appropriate
4. **Correct prop passing** to Card and Button components
5. **Event handlers** with proper typing:
   - `onChange: (e: React.ChangeEvent<HTMLInputElement>) => void`
   - `onClick: () => void`

### Styling Requirements
- Use Tailwind CSS classes
- Maintain consistent spacing and layout
- Responsive design with mobile-first approach
- Proper focus states for accessibility

### Type Safety
- All state must be properly typed with Settings interface
- Event handlers must have correct TypeScript types
- No `as any` or type suppression

---

## Edge Cases to Test

1. **Empty API response** - Handle when getSettings returns empty or undefined data
2. **Partial settings data** - Handle when some settings fields are missing
3. **Invalid API response** - Handle malformed or unexpected API responses
4. **Network timeout** - Handle slow or failed network requests
5. **Rapid form changes** - Handle user making multiple rapid changes
6. **Save while loading** - Prevent multiple simultaneous save requests
7. **Reset with unsaved changes** - Confirm or handle reset when user has unsaved changes
8. **Invalid number inputs** - Handle non-numeric input in number fields
9. **Threshold constraints** - Validate low < high threshold relationship
10. **Browser back/forward** - Maintain settings state across navigation

---

## Success Criteria

1. ✅ All unit tests pass (0 failures)
2. ✅ Test coverage ≥ 80%
3. ✅ No TypeScript compilation errors
4. ✅ All form inputs are controlled components
5. ✅ All event handlers properly typed
6. ✅ JSX syntax used throughout (no React.createElement)
7. ✅ Loading, error, and success states properly handled
8. ✅ API integration works correctly with mocked responses
9. ✅ Form state management preserves user changes
10. ✅ Reset functionality restores all defaults correctly
