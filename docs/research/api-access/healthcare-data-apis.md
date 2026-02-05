# Official Healthcare Data APIs and Capabilities Research

## Overview
This document contains research findings about official APIs for accessing healthcare data, including government and industry-standard interfaces for provider, facility, and insurance information.

**Research Date**: February 4, 2026  
**Researcher**: Librarian Agent  
**Status**: Initial research completed

## Importance of Healthcare APIs

### Primary Functions
- **Data Access**: Programmatic access to healthcare information
- **Real-time Updates**: Current provider and facility status
- **Integration**: Connection to multiple data sources
- **Automation**: Eliminate manual data collection
- **Standardization**: Consistent data formats and protocols

### Use Cases
- **Provider Verification**: Real-time license and enrollment status
- **Network Management**: Current insurance participation data
- **Care Coordination**: Find available providers for patients
- **Compliance Reporting**: Automated regulatory reporting
- **Data Analytics**: Healthcare provider and facility analytics

## Government Healthcare APIs

### 1. CMS (Centers for Medicare & Medicaid Services) APIs

#### Blue Button 2.0 API
- **Purpose**: Medicare beneficiary claims data
- **Access**: Medicare beneficiary授权 (with patient consent)
- **Data**: Claims, enrollment, and payment data
- **Authentication**: OAuth 2.0
- **Rate Limits**: 10 requests per second
- **Documentation**: https://bluebutton.cms.gov/

#### QPP (Quality Payment Program) API
- **Purpose**: Provider performance and quality data
- **Access**: Public data on provider performance
- **Data**: Quality measures, MIPS scores
- **Format**: JSON, XML
- **Updates**: Annual performance data
- **Documentation**: https://qpp.cms.gov/api/

#### Coverage API
- **Purpose**: Medicare coverage and policy information
- **Access**: Public coverage data
- **Data**: Coverage policies, LCDs, NCDs
- **Format**: JSON
- **Updates**: Policy changes
- **Documentation**: https://www.cms.gov/medicare-coverage-database

### 2. State Government APIs

#### State Medicaid APIs (Varies by State)
- **New York Medicaid API**
  - **URL**: https://api.health.ny.gov/
  - **Access**: Restricted to authorized entities
  - **Data**: Provider enrollment, eligibility
  - **Authentication**: API keys required
  - **Rate Limits**: Varies by endpoint

#### California Medi-Cal APIs
- **URL**: https://www.medi-cal.ca.gov/
- **Access**: Provider and beneficiary data
- **Data**: Provider directories, fee schedules
- **Authentication**: Multi-factor authentication
- **Updates**: Daily to weekly

#### Texas Medicaid APIs
- **URL**: https:// Medicaid.api.texas.gov/
- **Access**: Provider and claims data
- **Data**: Provider enrollment, prior auth
- **Authentication**: OAuth 2.0
- **Rate Limits**: 100 requests per minute

### 3. Federal Health Data APIs

#### HealthData.gov APIs
- **Purpose**: Health and human services data
- **Access**: Public datasets via API
- **Data**: Provider directories, hospital quality
- **Format**: JSON, CSV, XML
- **Authentication**: API key (free)
- **Documentation**: https://healthdata.gov/

#### FDA APIs
- **Purpose**: Drug and device information
- **Access**: Public drug and device data
- **Data**: Drug approvals, recalls, labels
- **Format**: JSON, XML
- **Updates**: Real-time for critical alerts
- **Documentation**: https://www.fda.gov/drugs/drug-approvals-and-databases

## Industry Standard Healthcare APIs

### 1. FHIR (Fast Healthcare Interoperability Resources)

#### HL7 FHIR APIs
- **Standard**: HL7 FHIR Version R4 (current)
- **Purpose**: Healthcare data exchange standard
- **Resources**: Provider, Patient, Organization, etc.
- **Format**: JSON/XML
- **Authentication**: OAuth 2.0, SMART on FHIR
- **Documentation**: https://hl7.org/fhir/

#### SMART on FHIR APIs
- **Purpose**: Standardized healthcare app integration
- **Access**: Provider and patient data
- **Data**: Clinical, administrative, financial
- **Authentication**: OAuth 2.0 with scopes
- **Compliance**: HIPAA, 21st Century Cures Act
- **Documentation**: https://hl7.org/fhir/smart-app-launch/

### 2. Insurance Industry APIs

#### CAQH Provider Data Registry API
- **Purpose**: Provider credentialing and directories
- **Access**: Provider demographic and participation data
- **Data**: Provider information, credentials, affiliations
- **Authentication**: API key and OAuth
- **Updates**: Real-time provider updates
- **Documentation**: https://www.caqh.org/cockpit

#### Availity Multi-Payer API
- **Purpose**: Multi-payer healthcare data
- **Access**: Eligibility, claims, and provider data
- **Data**: 2 million+ providers, 900+ payers
- **Format**: JSON
- **Authentication**: OAuth 2.0
- **Rate Limits**: Tiered based on subscription
- **Documentation**: https://developer.availity.com/

#### Change Healthcare APIs
- **Purpose**: Comprehensive healthcare data
- **Access**: Provider, claims, clinical data
- **Data**: 1 million+ providers, all major payers
- **Format**: JSON
- **Authentication**: OAuth 2.0
- **Updates**: Real-time data
- **Documentation**: https://developers.changehealthcare.com/

### 3. Professional Organization APIs

#### American Medical Association (AMA) API
- **Purpose**: Physician data and CPT codes
- **Access**: Physician information, procedure codes
- **Data**: Physician profiles, CPT/PC codes
- **Format**: JSON
- **Authentication**: API key
- **Updates**: Annual code updates
- **Documentation**: https://www.ama-assn.org/practice-management/digital

#### American Hospital Association (AHA) API
- **Purpose**: Hospital and health system data
- **Access**: Hospital statistics, quality metrics
- **Data**: Hospital profiles, financial data
- **Format**: JSON, CSV
- **Authentication**: Subscription required
- **Updates**: Annual surveys
- **Documentation**: https://www.aha.org/data-research

## API Access Methods and Requirements

### 1. Authentication and Authorization

#### OAuth 2.0 (Most Common)
- **Flows**: Authorization Code, Client Credentials
- **Scopes**: Limited access to specific data types
- **Tokens**: JWT with expiration
- **Refresh**: Token refresh mechanism
- **Compliance**: HIPAA requirements for PHI access

#### API Keys
- **Type**: Public/Private key pairs
- **Management**: Portal-based key management
- **Rotation**: Regular key rotation recommended
- **Revocation**: Immediate revocation capability
- **Logging**: All API key usage logged

#### Certificate-Based Authentication
- **Type**: X.509 certificates
- **Use**: High-security data access
- **Management**: Certificate lifecycle management
- **Expiration**: Regular certificate renewal
- **Revocation**: CRL checking

### 2. Data Formats and Standards

#### JSON/JSON-LD
- **Format**: JavaScript Object Notation
- **Use**: Most modern healthcare APIs
- **Advantages**: Lightweight, easy parsing
- **Schema**: JSON Schema validation
- **Compression**: GZIP compression supported

#### XML/SOAP
- **Format**: eXtensible Markup Language
- **Use**: Legacy systems, some government APIs
- **Advantages**: Schema validation, WSDL
- **Transformations**: XSLT for conversion
- **Standards**: HL7 v2, v3, CDA

#### FHIR Resources
- **Format**: FHIR-specific JSON/XML
- **Use**: Modern interoperability
- **Resources**: Standardized healthcare objects
- **Validation**: FHIR validation tools
- **Profiles**: Custom extensions allowed

### 3. Rate Limiting and Throttling

#### Common Rate Limits
- **Government APIs**: 10-100 requests/minute
- **Commercial APIs**: 100-1000 requests/minute
- **Bulk Data**: Separate rate limits for batch operations
- **Real-time**: Higher limits for clinical systems

#### Tiered Access
- **Free Tier**: Limited requests, basic data
- **Professional Tier**: Higher limits, full data
- **Enterprise Tier**: Custom limits, priority support
- **Volume Pricing**: Per-request or subscription-based

## API Integration Challenges

### Technical Challenges
- **Multiple Standards**: Different APIs use different standards
- **Authentication Variations**: Each API has unique auth requirements
- **Rate Limiting**: Managing multiple API limits
- **Data Format Conversion**: Transforming between formats
- **Error Handling**: Different error formats per API

### Data Quality Issues
- **Timeliness**: Real-time vs. batch updates
- **Completeness**: Missing fields or records
- **Consistency**: Varying data definitions
- **Accuracy**: Data quality varies by source
- **Synchronization**: Keeping multiple sources in sync

### Compliance and Security
- **HIPAA Compliance**: Required for PHI access
- **Data Storage**: Secure storage requirements
- **Audit Logging**: Complete access logging
- **Data Retention**: Legal retention requirements
- **Breach Notification**: Security incident procedures

## Best Practices for API Integration

### 1. Architecture Patterns
- **Microservices**: Separate service for each API
- **API Gateway**: Centralized access management
- **Message Queues**: Handle API failures and retries
- **Caching Layer**: Reduce API calls and improve performance
- **Monitoring**: Track API performance and errors

### 2. Data Management
- **Normalization**: Standardize data from multiple sources
- **Deduplication**: Remove duplicate provider records
- **Validation**: Verify data quality and completeness
- **Enrichment**: Add additional value-added data
- **Versioning**: Track data source versions

### 3. Security and Compliance
- **Encryption**: Encrypt data in transit and at rest
- **Access Controls**: Role-based access control
- **Audit Trails**: Complete audit logging
- **Vulnerability Management**: Regular security assessments
- **Incident Response**: Security incident procedures

### 4. Performance and Scalability
- **Connection Pooling**: Reuse API connections
- **Asynchronous Processing**: Non-blocking API calls
- **Load Balancing**: Distribute API traffic
- **Auto-scaling**: Scale based on demand
- **Performance Monitoring**: Track API response times

## Sample API Integrations

### NPI Registry API Integration
```python
import requests
import json

class NPIRegistryAPI:
    def __init__(self):
        self.base_url = "https://npiregistry.cms.hhs.gov/api/"
        self.session = requests.Session()
        
    def search_provider(self, npi_number):
        """Search provider by NPI number"""
        endpoint = f"{self.base_url}number={npi_number}"
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NPI data: {e}")
            return None
            
    def search_by_name(self, first_name, last_name, state=None):
        """Search providers by name and optional state"""
        params = {
            'first_name': first_name,
            'last_name': last_name
        }
        if state:
            params['state'] = state
            
        endpoint = f"{self.base_url}search"
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching providers: {e}")
            return None
```

### FHIR Provider API Integration
```python
from fhir.resources.bundle import Bundle
from fhir.resources.practitioner import Practitioner
import requests

class FHIRProviderAPI:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/fhir+json'
        }
        
    def get_practitioner(self, practitioner_id):
        """Get practitioner by ID"""
        endpoint = f"{self.base_url}/Practitioner/{practitioner_id}"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return Practitioner.parse_raw(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error getting practitioner: {e}")
            return None
            
    def search_practitioners(self, name=None, identifier=None):
        """Search practitioners by name or identifier"""
        params = {}
        if name:
            params['name'] = name
        if identifier:
            params['identifier'] = identifier
            
        endpoint = f"{self.base_url}/Practitioner"
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return Bundle.parse_raw(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error searching practitioners: {e}")
            return None
```

## Next Research Steps

1. **API Documentation Review**: Detailed review of current API documentation
2. **Access Requirements**: Obtain specific access credentials and permissions
3. **Integration Testing**: Prototype connections with key APIs
4. **Performance Testing**: Test API response times and reliability
5. **Cost Analysis**: Evaluate commercial API pricing and plans

---

**Appendix A: API Endpoints Catalog** (To be completed with specific URLs)
**Appendix B: Authentication Requirements** (To be completed with auth details)
**Appendix C: Data Schema Definitions** (To be completed with field definitions)

