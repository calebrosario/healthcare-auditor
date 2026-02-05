# NDC (National Drug Code) Research

## Overview
NDCs are universal product identifiers for human drugs in the US. Maintained by the FDA and used for drug identification, billing, and reimbursement.

## Code Structure
- Format: 11-digit code in three segments:
  - Labeler code (4-5 digits) - manufacturer/packager
  - Product code (3-4 digits) - specific drug/strength/dosage form
  - Package code (1-2 digits) - package size/type
- Display formats: 4-4-2, 5-3-2, or 5-4-2
- NDC Directory contains all registered NDCs

## Update Process
- Daily updates to NDC Directory
- FDA maintains the master file
- New drugs added upon approval
- Discontinued drugs marked as inactive
- Manufacturers submit updates directly

## Common Errors
1. Invalid NDC format
2. Using inactive/discontinued NDCs
3. Incorrect unit of measure billing
4. Missing NDC for compounded drugs
5. Package size vs. billing unit confusion

## Data Sources
- FDA NDC Directory (public)
- First Data Bank (commercial)
- Medi-Span (commercial)
- Red Book (commercial)
- Payer formularies
- Pharmacy benefit managers

## Implementation Considerations
- Public domain information
- Daily updates recommended
- Integration with drug pricing databases
- Validation against FDA master file
- Cross-referencing with HCPCS J-codes
- Unit of measure conversion critical
- Compounded drug handling

