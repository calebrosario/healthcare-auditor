# ACA Billing Transparency Requirements Research

## Overview

The Affordable Care Act (ACA) of 2010 includes several provisions aimed at increasing transparency in healthcare billing and costs. These requirements are designed to help patients understand their healthcare costs and make informed decisions.

## Key Transparency Requirements

### 1. Price Transparency Rule

**Effective Date**: January 1, 2021 (with ongoing updates)

**Requirements**:
- Hospitals must provide clear, accessible pricing information online about items and services
- Must provide a list of standard charges in machine-readable format
- Must display shoppable services in consumer-friendly format
- Must provide good faith estimates to uninsured and self-pay patients

### 2. Machine Readable Files (Section 2718)

**Requirements**:
- Hospitals must make available a machine-readable file with all standard charges
- File must include:
  - Gross charges
  - Discounted cash prices
  - Payer-specific negotiated charges
  - Minimum and maximum negotiated charges
  - De-identified negotiated charges

### 3. Shoppable Services Display

**Requirements**:
- At least 300 shoppable services must be displayed
- Must include:
  - Gross charge
  - Discounted cash price
  - Payer-specific negotiated charge
  - Minimum and maximum negotiated charges
  - De-identified minimum and maximum negotiated charges

### 4. No Surprises Act (Part of ACA Enhancement)

**Effective Date**: January 1, 2022

**Requirements**:
- Bans surprise billing for emergency services
- Bans out-of-network cost-sharing for emergency and non-emergency services
- Requires advance consent and cost estimate for non-emergency services
- Establishes independent dispute resolution process for payment disputes

## Implementation Considerations

### Data Elements Required

1. **Pricing Information**
   - CPT/HCPCS codes
   - Description of services
   - Gross charges
   - Discounted cash prices
   - Payer-specific negotiated rates
   - De-identified maximum negotiated charge

2. **Payer Information**
   - Payer names and identifiers
   - Plan types and networks
   - Contract effective dates

3. **Service Categories**
   - Emergency services
   - Non-emergency services
   - Diagnostic services
   - Therapeutic services
   - Surgical services

## Compliance Verification

### Required Documentation
- Publicly available price transparency files
- Documentation of file updates (at least annually)
- Consumer-facing display verification
- Good faith estimate procedures
- Surprise billing compliance documentation

### Audit Requirements
- Annual review of price transparency compliance
- Verification of machine-readable file accuracy
- Testing of consumer-friendly display functionality
- Review of good faith estimate processes

## Official Sources

1. **CMS Price Transparency**: https://www.cms.gov/price-transparency
2. **Federal Register**: ACA provisions and updates
3. **HHS Healthcare.gov**: Consumer resources and provider requirements

## Penalties for Non-Compliance

- **Civil Monetary Penalties**: Up to $300 per day for hospitals failing to comply
- **Public Disclosure**: Non-compliant hospitals may be publicly identified
- **Medicare/Medicaid Participation**: Repeated violations may affect program participation

## Next Steps for Research

1. Obtain full text of ACA price transparency requirements
2. Research CMS implementation guidelines
3. Identify specific data format requirements
4. Research state-level price transparency laws
5. Develop compliance checklist and implementation guide

## Data Model Considerations

### Price Transparency Data Structure
```typescript
interface PriceTransparencyData {
  hospital: {
    id: string;
    name: string;
    npi: string;
    location: Address;
  };
  services: ServicePricing[];
  payers: PayerInformation[];
  effectiveDate: Date;
  lastUpdated: Date;
}

interface ServicePricing {
  code: string; // CPT/HCPCS
  description: string;
  grossCharge: number;
  discountedCashPrice: number;
  payerNegotiatedRates: PayerRate[];
  minNegotiatedRate: number;
  maxNegotiatedRate: number;
  isShoppable: boolean;
  category: ServiceCategory;
}
```

## References

- CMS Price Transparency Requirements
- ACA Section 2718
- No Surprises Act Implementation
- Hospital Price Transparency Final Rule

---
**Research Date**: February 4, 2026  
**Last Updated**: February 4, 2026  
**Status**: Initial Research Complete - Official Sources Needed
