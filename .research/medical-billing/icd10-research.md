# ICD-10 (International Classification of Diseases) Research

## Overview
ICD-10 is maintained by the World Health Organization (WHO) and used internationally for diagnosis classification. In the US, it's maintained by CMS with clinical modifications (ICD-10-CM).

## Code Structure
- Format: Alphanumeric codes
- Structure: 
  - Category (1st character: A-Z, except U)
  - Etiology (2nd character: 0-9)
  - Anatomical site (3rd-7th characters)
  - Severity, extension, cause, etc. (later characters)
- Example: I10 (Essential hypertension)
- Extension codes for additional specificity

## Update Process
- Annual updates on October 1st
- Coordinated by CMS in the US
- Public comment period for proposed changes
- ICD-11 being developed but not yet implemented in US

## Common Errors
1. Insufficient specificity (not using all required digits)
2. Incorrect code sequencing (primary vs. secondary diagnoses)
3. Using codes that don't match clinical documentation
4. Exclusionary condition violations

## Data Sources
- CDC National Center for Health Statistics
- CMS ICD-10-CM Official Guidelines
- WHO ICD-10 online browser
- Public domain tables (no licensing restrictions)

## Implementation Considerations
- Public domain (no license required)
- Regular updates needed
- Hierarchical structure for validation
- Mapping to CPT for procedure-diagnosis pairs
- Integration with clinical documentation

