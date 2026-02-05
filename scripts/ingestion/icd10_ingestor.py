"""
ICD-10-CM code ingestion from CDC.
"""
import asyncio
import logging
import httpx
from typing import List, Optional
from datetime import datetime
from .base import BaseIngestor

logger = logging.getLogger(__name__)


class ICD10Ingestor(BaseIngestor):
    """Ingest ICD-10-CM diagnosis codes from CDC."""
    
    CDC_ICD10_URL = "https://www.cdc.gov/nchs/icd/10cm"
    
    async def fetch_data(self, session: httpx.AsyncClient) -> List[dict]:
        """Fetch ICD-10-CM codes from CDC."""
        logger.info("Fetching ICD-10-CM codes from CDC...")
        
        # CDC provides ICD-10-CM as public domain files
        # Main files:
        # - icd10cm_tabular_2025.xml (code descriptions)
        # - icd10cm_tabular_2025_order_2025.xml (order file)
        # - icd10cm_tabular_2025_descriptions.xml (long descriptions)
        
        files = [
            "icd10cm_tabular_2025.xml",  # Latest year code file
            "icd10cm_tabular_2025_order_2025.xml",
        ]
        
        codes = []
        
        for filename in files:
            url = f"{self.CDC_ICD10_URL}/{filename}"
            logger.info(f"Fetching: {url}")
            
            try:
                response = await session.get(url)
                response.raise_for_status()
                
                # Parse XML response
                # Note: This is a simplified parser
                # Real implementation would parse the complex CDC XML structure
                import xml.etree.ElementTree as ET
                
                root = ET.fromstring(response.text)
                
                # Navigate to diagnosis codes
                # XML structure: <ICD10CM><diag>...</diag>...</ICD10CM>
                for diag in root.findall('.//diag'):
                    code = diag.find('name').text
                    description = diag.find('desc').text
                    
                    codes.append({
                        "code": code,
                        "description": description,
                        "code_type": "ICD-10",
                        "effective_date": datetime.now().strftime("%Y-%m-%d"),
                        "status": "active",
                        "category": "Diagnosis",
                        "source": "CDC"
                    })
                    
                    if len(codes) >= self.batch_size:
                        break
                        
            except Exception as e:
                logger.error(f"Error fetching {filename}: {e}")
        
        return codes
    
    async def process_item(self, item: dict, db: AsyncSession) -> Optional[any]:
        """Process a single ICD-10 code."""
        # Check if code already exists
        from ..backend.app.core.database import get_db
        from ..backend.app.models.billing_code import BillingCode
        
        result = await db.execute(
            select(BillingCode).where(Billing_code.code == item["code"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.debug(f"ICD-10 code {item['code']} already exists, skipping")
            return None
        
        # Create new billing code
        from ..backend.app.models.billing_code import BillingCode
        
        return BillingCode(
            code=item["code"],
            code_type=CodeType.ICD10,
            description=item.get("description"),
            effective_date=datetime.strptime(item["effective_date"], "%Y-%m-%d"),
            termination_date=None,
            category=item.get("category"),
            status=item["status"]
        )


async def main():
    """Main ingestion function for ICD-10-CM."""
    logger.info("Starting ICD-10-CM ingestion...")
    
    from ..backend.app.core.database import get_db
    
    ingestor = ICD10Ingestor(batch_size=1000)
    
    async with get_db() as db:
        result = await ingestor.ingest(db)
        
        logger.info(f"ICD-10-CM ingestion complete: {result}")
        
        # Return result for testing
        return result


if __name__ == "__main__":
    asyncio.run(main())
