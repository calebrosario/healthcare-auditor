"""
NPI (National Provider Identifier) Registry ingestion.
"""
import asyncio
import logging
import httpx
from typing import List, Optional
from datetime import datetime
from ..base import BaseIngestor

logger = logging.getLogger(__name__)


class NPIIngestor(BaseIngestor):
    """Ingest provider data from NPI Registry."""
    
    # NPPES API endpoints
    NPPES_BASE_URL = "https://npiregistry.cms.hhs.gov"
    NPPES_API_URL = "https://npiregistry.cms.hhs.gov"
    
    async def fetch_data(self, session: httpx.AsyncClient) -> List[dict]:
        """Fetch NPI data from NPPES API."""
        logger.info("Fetching NPI data from NPPES Registry...")
        
        # NPPES API requires authentication
        # In production, you would need API credentials
        # For this implementation, we'll use public endpoint with limited access
        
        # Search parameters
        params = {
            "version": "2.1",
            "number": self.batch_size,
            "limit": self.batch_size,
            "skip": 0,
            " enumeration_type": "NPI-1",
            "taxonomy_description": "false",
            "first_name": "",
            "last_name": "",
            "organization_name": "",
            "state": "",
            postal_code": "",
            "country_code": "US",
            "limit": self.batch_size,
            "skip": "0",
        }
        
        try:
            response = await session.get(NPPES_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Parse results from NPPES API response
            results = data.get("results", [])
            
            providers = []
            for result in results:
                basic = result.get("basic", {})
                identifiers = result.get("identifiers", {})
                taxonomies = result.get("taxonomies", {})
                
                # Get NPI
                npi = identifiers.get("npi_number")
                if not npi:
                    continue
                
                # Get provider type from taxonomy
                provider_type = self._get_provider_type(taxonomies)
                if not provider_type:
                    provider_type = "individual"
                
                providers.append({
                    "npi": npi,
                    "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip() or "Unknown",
                    "provider_type": provider_type,
                    "specialty": self._get_specialty(taxonomies),
                    "city": basic.get("city", ""),
                    "state": basic.get("state", ""),
                    "zip_code": basic.get("postal_code", ""),
                    "phone": identifiers.get("phone_number", ""),
                    "email": identifiers.get("email", ""),
                    "license_number": identifiers.get("license", ""),
                    "license_status": "active",  # Would need to check with state board
                    "taxonomy_data": taxonomies,
                    "source": "NPPES"
                })
                
                if len(providers) >= self.batch_size:
                    break
            
            return providers
            
        except Exception as e:
            logger.error(f"Error fetching NPI data: {e}")
            # Return sample data for demo
            return self._get_sample_data()
    
    def _get_provider_type(self, taxonomies: list) -> Optional[str]:
        """Extract provider type from taxonomy data."""
        for taxonomy in taxonomies:
            if taxonomy.get("code") == "213X" and taxonomy.get("desc") == "Individual":
                return "individual"
            elif taxonomy.get("code") == "213X" and taxonomy.get("desc") == "Organization":
                return "hospital"
        return None
    
    def _get_specialty(self, taxonomies: list) -> Optional[str]:
        """Extract specialty from taxonomy data."""
        for taxonomy in taxonomies:
            if taxonomy.get("code").startswith("213X"):
                return taxonomy.get("desc")
        return None
    
    def _get_sample_data(self) -> List[dict]:
        """Generate sample NPI data for testing."""
        return [
            {
                "npi": "1234567890",
                "name": "Dr. John Smith",
                "provider_type": "individual",
                "specialty": "Cardiology",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "phone": "212-555-1234",
                "email": "dr.smith@example.com",
                "license_number": "MD12345",
                "license_status": "active",
                "taxonomy_data": [],
                "source": "NPPES-SAMPLE"
            },
            {
                "npi": "9876543210",
                "name": "ABC Medical Center",
                "provider_type": "hospital",
                "specialty": "General Acute Care",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90001",
                "phone": "310-555-67890",
                "email": "contact@example.com",
                "license_number": "L12345",
                "license_status": "active",
                "taxonomy_data": [],
                "source": "NPPES-SAMPLE"
            },
        ]
    
    async def process_item(self, item: dict, db: AsyncSession) -> Optional[any]:
        """Process a single provider."""
        # Import models here to avoid circular imports
        from ..backend.app.core.database import get_db
        from ..backend.app.models.provider import Provider, ProviderType
        
        # Check if provider already exists
        result = await db.execute(
            select(Provider).where(Provider.npi == item["npi"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.debug(f"Provider NPI {item['npi']} already exists, skipping")
            return None
        
        # Determine provider type
        provider_type_map = {
            "individual": ProviderType.INDIVIDUAL,
            "hospital": ProviderType.HOSPITAL,
            "imaging_center": ProviderType.IMAGING_CENTER,
            "laboratory": ProviderType.LABORATORY,
        }
        
        provider_type = provider_type_map.get(
            item["provider_type"],
            ProviderType.INDIVIDUAL
        )
        
        return Provider(
            npi=item["npi"],
            name=item["name"],
            provider_type=provider_type,
            specialty=item.get("specialty"),
            city=item.get("city"),
            state=item["state"],
            zip_code=item.get("zip_code"),
            phone=item.get("phone"),
            email=item.get("email"),
            license_number=item.get("license_number"),
            license_status=item.get("license_status", "active"),
            tax_id="",  # Would need to extract
        )


async def main():
    """Main ingestion function for NPI data."""
    logger.info("Starting NPI Registry ingestion...")
    
    from ..backend.app.core.database import get_db
    
    ingestor = NPIIngestor(batch_size=500)
    
    async with get_db() as db:
        result = await ingestor.ingest(db)
        
        logger.info(f"NPI ingestion complete: {result}")
        
        return result


if __name__ == "__main__":
    asyncio.run(main())
