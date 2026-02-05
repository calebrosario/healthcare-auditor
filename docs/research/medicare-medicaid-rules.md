# Medicare/Medicaid Rules and Billing Guidelines

## Overview

Medicare and Medicaid are federal health insurance programs with specific billing and compliance requirements. Medicare primarily serves individuals aged 65 and older, while Medicaid serves low-income individuals and families.

## Medicare Program Structure

### 1. Medicare Parts

#### Part A - Hospital Insurance
- Covers inpatient hospital stays
- Skilled nursing facility care
- Hospice care
- Home health care

#### Part B - Medical Insurance
- Covers doctor visits
- Outpatient care
- Medical supplies
- Preventive services

#### Part C - Medicare Advantage
- Private health plan alternatives to Original Medicare
- Must cover all Part A and Part B services
- May include additional benefits

#### Part D - Prescription Drug Coverage
- Standalone prescription drug plans
- Medicare Advantage prescription drug plans

### 2. Key Medicare Billing Requirements

#### Face-to-Face Encounter Requirements
**Reference**: CMS-2026-0001-0001 (January 2026)

**Requirements**:
- Certain items and services require face-to-face encounters
- Written orders prior to delivery may be required
- Prior authorization requirements apply to specific services
- Documentation must be maintained in patient records

#### Provider Enrollment and Certification
- Must be enrolled in Medicare program
- Maintain valid National Provider Identifier (NPI)
- Meet specific licensure and certification requirements
- Comply with Medicare enrollment standards

#### Medicare Plan Finder Data Requirements
**Reference**: CMS-2026-0067-0001 (January 2026)

**Requirements**:
- Provider directory data must be accurate and current
- Plan information must be updated regularly
- Provider network status must be accurately reflected
- Service area information must be maintained

## Medicaid Program Structure

### 1. Federal-State Partnership
- Federal government establishes minimum requirements
- States administer programs within federal guidelines
- State-specific variations in coverage and eligibility

### 2. Key Medicaid Billing Requirements

#### Medicaid Managed Care
- States may contract with managed care organizations
- Must meet federal quality and access standards
- Provider networks must be adequate
- Prior authorization requirements apply

#### Medicaid Eligibility Verification
- Must verify patient eligibility for each service
- Real-time eligibility verification preferred
- Documentation of eligibility verification required
- Coordination with other insurance programs (Medicare third-party liability)

## Common Compliance Requirements

### 1. Documentation Requirements
- Medical necessity documentation
- Provider credentials and certifications
- Patient consent forms
- Prior authorization approvals
- Coordination of benefits documentation

### 2. Coding and Billing Standards
- Use of appropriate CPT, HCPCS, and ICD-10 codes
- Proper modifier usage
- Correct coding initiative (CCI) compliance
- Bundling and unbundling rules

### 3. Fraud, Waste, and Abuse Prevention
- Implementation of compliance programs
- Regular audits and monitoring
- Employee training on fraud prevention
- Reporting procedures for suspected fraud

## Specific Billing Guidelines

### 1. Prior Authorization
- Required for certain services and equipment
- Must be obtained before service delivery
- Documentation of medical necessity required
- Time limits for authorization requests

### 2. Medical Necessity
- Services must be medically necessary
- Documentation must support medical necessity
- Local Coverage Determinations (LCDs) apply
- National Coverage Determinations (NCDs) apply

### 3. Timely Filing
- Medicare: 12 months from date of service
- Medicaid: Varies by state (typically 6-12 months)
- timely filing limits may be extended in certain circumstances
- Documentation of timely submission required

## Compliance Verification

### Required Documentation
- Provider enrollment records
- Prior authorization approvals
- Medical necessity documentation
- Patient eligibility verification
- Coding and billing records
- Audit trail documentation

### Audit Requirements
- Regular internal audits
- External audits by CMS or state Medicaid agencies
- Recovery Audit Contractor (RAC) reviews
- Zone Program Integrity Contractor (ZPIC) reviews

## Official Sources

### Medicare Sources
1. **CMS.gov**: https://www.cms.gov
2. **Medicare.gov**: https://www.medicare.gov
3. **Federal Register**: Medicare rules and regulations
4. **CMS Program Memoranda**: Implementation guidance

### Medicaid Sources
1. **CMS Medicaid.gov**: https://www.medicaid.gov
2. **State Medicaid Agencies**: Individual state requirements
3. **Medicaid Managed Care Regulations**: Federal and state requirements

## Penalties for Non-Compliance

### Medicare Penalties
- Civil monetary penalties
- Program exclusion
- Overpayment recovery
- Criminal prosecution for fraud

### Medicaid Penalties
- Civil monetary penalties
- Program exclusion
- Overpayment recovery
- State-specific penalties

## Data Model Considerations

### Medicare/Medicaid Compliance Tracking
```typescript
interface MedicareMedicaidCompliance {
  provider: {
    npi: string;
    medicareEnrolled: boolean;
    medicaidEnrolled: boolean[];
    stateMedicaidIds: string[];
  };
  services: ServiceCompliance[];
  authorizations: PriorAuthorization[];
  audits: ComplianceAudit[];
}

interface ServiceCompliance {
  serviceCode: string;
  medicareCoverage: CoverageStatus;
  medicaidCoverage: StateCoverageStatus[];
  priorAuthRequired: boolean;
  medicalNecessityCriteria: string[];
  documentationRequirements: string[];
}
```

## Next Steps for Research

1. Obtain full text of Medicare Program Integrity Manual
2. Research state-specific Medicaid requirements
3. Identify specific Local Coverage Determinations
4. Research recent Medicare/Medicaid program changes
5. Develop comprehensive compliance checklists

## References

- CMS-2026-0001-0001: Face-to-Face Encounter Requirements
- CMS-2026-0067-0001: Medicare Plan Finder Data Requirements
- Medicare Program Integrity Manual
- Medicaid Managed Care Regulations
- State Medicaid Program Manuals

---
**Research Date**: February 4, 2026  
**Last Updated**: February 4, 2026  
**Status**: Initial Research Complete - Additional Sources Needed
