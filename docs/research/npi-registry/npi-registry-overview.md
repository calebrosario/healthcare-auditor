# NPI Registry Research - Healthcare Provider Data Sources

## Overview
This document contains research findings about the National Provider Identifier (NPI) Registry, which is a critical data source for healthcare provider information in the United States.

**Note**: Research was conducted on February 4, 2026. Some web-based resources were temporarily inaccessible during this research session. Information is based on available documentation and industry knowledge.

## NPI Registry Basics

The National Provider Identifier (NPI) Registry is:
- **Managed by**: Centers for Medicare & Medicaid Services (CMS)
- **Purpose**: Unique identification for healthcare providers in the U.S.
- **Authority**: Established under HIPAA Administrative Simplification provisions
- **Database**: National Plan and Provider Enumeration System (NPPES)

## NPI Data Structure

### Individual/Entity Types
1. **Individual Providers** (Type 1 NPI):
   - Licensed healthcare professionals
   - Includes doctors, nurses, therapists, etc.
   
2. **Organizational Providers** (Type 2 NPI):
   - Healthcare organizations
   - Includes hospitals, clinics, group practices

### Key Data Fields (Standard)
- **NPI Number**: 10-digit unique identifier
- **Entity Type**: Individual (1) or Organization (2)
- **Provider Name**: Legal name of provider or organization
- **Practice Location**: Primary business address
- **Mailing Address**: Correspondence address
- **Provider Taxonomy Codes**: Specialization and practice area codes
- **Provider Enumeration Date**: When NPI was assigned
- **Last Update Date**: Most recent record update
- **NPI Deactivation Date**: If applicable
- **Provider Status**: Active or inactive
- **Practice Location Phone Number**
- **Provider Gender**: For individual providers (Type 1)
- **Authorized Official Name/Title**: For organizational providers (Type 2)

## API Access Methods

### Official NPI Registry API (Potential Features)
While unable to access current API documentation in this session, standard NPI Registry APIs typically provide:

#### Endpoints:
- **Provider Search**: Search by NPI, name, location, taxonomy
- **Bulk Data**: Download complete NPI dataset
- **Individual Record Lookup**: Get details for specific NPI
- **Taxonomy Code Lookup**: Standard provider specialty codes

#### Authentication:
- **Public Access**: Most NPI data is publicly available
- **API Keys**: May be required for programmatic access
- **Rate Limits**: Typically present for API endpoints

## Data Access Options

### 1. Web Interface
- **URL**: https://nppes.cms.hhs.gov/
- **Features**: Manual search, filtering, export capabilities
- **Format**: Web-based forms, CSV export options

### 2. Bulk Data Download
- **Complete NPI Dataset**: Monthly updates
- **File Format**: Typically CSV or XML
- **Size**: Several million provider records
- **Download**: Direct download from CMS website

### 3. API Integration
- **RESTful API**: Programmatic access to NPI data
- **Response Formats**: JSON or XML
- **Updates**: Real-time or near-real-time data

## Data Freshness and Quality

### Update Frequency
- **Monthly**: Standard NPI dataset updates
- **Real-time**: API access for current data
- **Weekly**: Some third-party providers offer updated extracts

### Data Quality Considerations
- **Accuracy**: Provider self-reported information
- **Completeness**: Varies by provider type and specialty
- **Timeliness**: Updates depend on provider reporting
- **Deactivation**: Important to track inactive providers

## Legal and Compliance Requirements

### Data Usage Restrictions
- **HIPAA**: NPI data is considered public and not PHI
- **Privacy**: Cannot combine with other data to re-identify individuals
- **Commercial Use**: Generally permitted with attribution
- **Redistribution**: May have restrictions on bulk redistribution

### Required Disclaimers
- **Source Attribution**: Must cite CMS as data source
- **Data Currency**: Must note data freshness dates
- **Limitations**: Must disclaim CMS endorsement

## Integration Challenges

### Entity Resolution
- **Name Variations**: Provider names may appear differently across systems
- **Location Changes**: Providers may have multiple practice locations
- **Organization Structure**: Individual providers may be part of larger organizations
- **Historical Changes**: Need to track NPI changes over time

### Data Standardization
- **Address Formatting**: Standardize to USPS format
- **Name Formatting**: Handle suffixes, prefixes, and special characters
- **Taxonomy Codes**: Map to standardized specialty classifications
- **Geocoding**: Convert addresses to coordinates for mapping

## Recommendations for Implementation

### 1. Data Collection Strategy
- **Primary Source**: Use official NPI Registry data
- **Updates**: Establish regular update schedule (monthly recommended)
- **Validation**: Implement data quality checks
- **Backup**: Maintain historical snapshots of NPI data

### 2. API Integration Approach
- **Public API**: Use CMS NPI API if available
- **Bulk Downloads**: For complete datasets
- **Caching**: Implement local caching to reduce API calls
- **Error Handling**: Handle API rate limits and downtime

### 3. Data Maintenance
- **Change Detection**: Monitor for NPI changes
- **Deactivation Tracking**: Remove inactive providers
- **Duplicate Resolution**: Identify and merge duplicate entries
- **Cross-Reference**: Link to other provider data sources

## Next Research Steps

1. Verify current NPI Registry API documentation and capabilities
2. Test actual API endpoints and response formats
3. Identify data quality issues and resolution strategies
4. Research integration with other healthcare data sources
5. Develop implementation plan for NPI data integration

---

**Research Date**: February 4, 2026  
**Researcher**: Librarian Agent  
**Status**: Initial research completed - requires verification with current CMS documentation
