"""
HCPCS code ingestion from CMS.
"""
import asyncio
import logging
import httpx
from typing import List, Optional
from datetime import datetime
from .base import BaseIngestor

logger = logging.getLogger(__name__)


class HCPCSIngestor(BaseIngestor):
    """Ingest HCPCS codes from CMS."""
    
    CMS_HCPCS_URL = "https://www.cms.gov/Medicare/Coding/HCPCSReleaseInfoFiles"
    
    async def fetch_data(self, session: httpx.AsyncClient) -> List[dict]:
        """Fetch HCPCS codes from CMS."""
        logger.info("Fetching HCPCS codes from CMS...")
        
        # CMS provides HCPCS files as downloadable Excel/CSV files
        # Main files:
        # - Quarterly release files
        # - Long descriptions
        
        # For this implementation, we'll simulate the file structure
        # In production, you would download and parse the actual CMS files
        
        # Sample HCPCS codes for demonstration
        codes = []
        
        # Level II codes (common codes)
        sample_codes = [
            {"code": "G0001", "description": "Wheelchair standard issue", "category": "Durable Medical Equipment"},
            {"code": "G0002", "description": "Power-operated vehicle", "category": "Durable Medical Equipment"},
            {"code": "G0003", "description": "Hospital bed", "category": "Durable Medical Equipment"},
            {"code": "G0004", "description": "Crutch", "category": "Durable Medical Equipment"},
            {"code": "J3303", "description": "Pulmonary rehab", "category": "Physical Therapy"},
        ]
        
        for code in sample_codes:
            codes.append({
                "code": code["code"],
                "description": code["description"],
                "code_type": "HCPCS",
                "effective_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "active",
                "category": code["category"],
                "source": "CMS"
            })
            
            if len(codes) >= self.batch_size:
                break
        
        return codes
    
    async def process_item(self, item: dict, db: AsyncSession) -> Optional[any]:
        """Process a single HCPCS code."""
        from ..backend.app.core.database import get_db
        from ..backend.app.models.billing_code import BillingCode
        
        result = await db.execute(
            select(BillingCode).where(BillingCode.code == item["code"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.debug(f"HCPCS code {item['code']} already exists, skipping")
            return None
        
        return BillingCode(
            code=item["code"],
            code_type=CodeType.HCPCS,
            description=item.get("description"),
            effective_date=datetime.strptime(item["effective_date"], "%Y-%m-%d"),
            termination_date=None,
            category=item.get("category"),
            status=item["status"]
        )


async def main():
    """Main ingestion function for HCPCS."""
    logger.info("Starting HCPCS ingestion...")
    
    from ..backend.app.core.database import get_db
    
    ingestor = HCPCSIngestor(batch_size=1000)
    
    async with get_db() as db:
        result = await ingestor.ingest(db)
        
        logger.info(f"HCPCS ingestion complete: {result}")
        
        return result


if __name__ == "__main__":
    asyncio.run(main())
