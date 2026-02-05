# HCPCS (Healthcare Common Procedure Coding System) Research

## Overview
HCPCS is maintained by CMS and used primarily for Medicare and Medicaid billing. It supplements CPT codes and includes non-physician services, equipment, and supplies.

## Code Structure
Two levels:
1. **Level I**: CPT codes (10000-99999) - same as AMA CPT
2. **Level II**: Alphanumeric codes (A0000-V9999) - for non-physician services
   - DME (Durable Medical Equipment): E0000-E9999
   - Ambulance: A0000-A9999
   - Drugs/Supplies: J0000-J9999
   - Temporary codes: C0000-C9999, S0000-S9999
   - Dental: D0000-D9999
3. **Level III**: Local codes (W0000-W9999, etc.) - payer-specific

## Update Process
- Level I: Same as CPT (annual January updates)
- Level II: Quarterly updates (January, April, July, October)
- Public notice and comment period
- CMS maintains the code set

## Common Errors
1. Using Level I codes when Level II required
2. Incorrect modifier combinations
3. Using temporary codes beyond expiration
4. Missing required documentation for DME/Supplies

## Data Sources
- CMS HCPCS website
- Medicare Coverage Database
- Local Coverage Determinations (LCDs)
- NCCI (National Correct Coding Initiative) edits
- Public domain (no licensing restrictions)

## Implementation Considerations
- Public domain for Level II and III
- Integration with NCCI for edit validation
- Regular quarterly updates needed
- Cross-walking with CPT for comprehensive coding
- LCD/NCD validation for coverage

