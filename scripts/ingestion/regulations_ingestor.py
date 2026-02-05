"""
Regulatory data ingestion for healthcare compliance rules.
"""
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from .base import BaseIngestor
from ..backend.app.models.regulation import Regulation, RegulationType, RegulationCategory

logger = logging.getLogger(__name__)


class RegulationsIngestor(BaseIngestor):
    """Ingest healthcare regulations from various sources."""
    
    # Regulation sources
    CMS_URL = "https://www.cms.gov"
    HHS_OCR_URL = "https://ocrportal.hhs.gov/ocrportal"
    
    async def fetch_data(self, session: httpx.AsyncClient) -> List[dict]:
        """Fetch regulatory data from various sources."""
        logger.info("Fetching regulatory data...")
        
        regulations = []
        
        # Sample regulations based on research
        # HIPAA
        regulations.append({
            "code": "HIPAA_2003_164",
            "name": "HIPAA Privacy Rule",
            "regulation_type": "federal",
            "category": "privacy",
            "description": "Standards for privacy of individually identifiable health information",
            "requirements": "Administrative safeguards, physical safeguards, technical security",
            "effective_date": "2003-04-14",
            "is_active": True,
            "source": "HHS",
            "source_url": "https://www.hhs.gov/hipaa/index.html"
        })
        
        # ACA - No Surprises Act
        regulations.append({
            "code": "ACA_NSA_2021_001",
            "name": "No Surprises Act",
            "regulation_type": "federal",
            "category": "billing",
            "description": "Protection against surprise medical bills",
            "requirements": "Provider must provide good faith estimate, out-of-pocket cost estimate",
            "effective_date": "2022-01-01",
            "is_active": True,
            "source": "HHS",
            "source_url": "https://www.cms.gov/nosurprises/"
        })
        
        # Stark Law
        regulations.append({
            "code": "STARK_LAW_Section_1877",
            "name": "Physician Self-Referral",
            "regulation_type": "federal",
            "category": "anti_kickback",
            "description": "Prohibits physicians from referring patients to entities they have financial relationship with",
            "effective_date": "1972-10-26",
            "is_active": True,
            "source": "HHS",
            "source_url": "https://www.hhs.gov/stark-law/"
        })
        
        # Anti-Kickback Statute
        regulations.append({
            "code": "ANTI_KICKBACK_STATUTE_42_USC_1320a-7b",
            "name": "Anti-Kickback Statute",
            "regulation_type": "federal",
            "category": "anti_kickback",
            "description": "Prohibits offering remuneration for referrals",
            "effective_date": "1972-10-26",
            "is_active": True,
            "source": "DOJ",
            "source_url": "https://www.justice.gov/atr/criminal/antitrust/atro/guide/antitrust_laws/antitrust_act.pdf"
        })
        
        # Medicare Local Coverage Determinations
        regulations.append({
            "code": "NCD_LCD_10_240.1",
            "name": "Medicare LCD 10.240.1 - Hospital Inpatient Services",
            "regulation_type": "federal",
            "category": "billing",
            "description": "Coverage for hospital inpatient services",
            "effective_date": "2025-01-01",
            "is_active": True,
            "source": "CMS",
            "source_url": "https://www.cms.gov/medicare-coverage-database/details/lcds/2025/10.240.1"
        })
        
        return regulations
    
    async def process_item(self, item: dict, db: AsyncSession) -> Optional[any]:
        """Process a single regulation."""
        from ..backend.app.core.database import get_db
        from ..backend.app.models.regulation import Regulation
        
        result = await db.execute(
            select(Regulation).where(Regulation.code == item["code"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.debug(f"Regulation {item['code']} already exists, skipping")
            return None
        
        # Map category string to enum
        category_map = {
            "billing": RegulationCategory.BILLING,
            "privacy": RegulationCategory.PRIVACY,
            "security": RegulationCategory.SECURITY,
            "anti_kickback": RegulationCategory.ANTI_KICKBACK,
            "stark_law": RegulationCategory.STARK_LAW,
            "hipaa": RegulationCategory.HIPAA,
            "aca": RegulationCategory.ACA,
            "no_surprises": RegulationCategory.NO_SURPRISES,
        }
        
        # Map regulation type to enum
        type_map = {
            "federal": RegulationType.FEDERAL,
            "state": RegulationType.STATE,
            "local": RegulationType.LOCAL,
            "industry_standard": RegulationType.INDUSTRY_STANDARD,
        }
        
        try:
            category = category_map.get(item["category"].lower(), RegulationCategory.BILLING)
            reg_type = type_map.get(item["regulation_type"].lower(), RegulationType.FEDERAL)
        except KeyError as e:
            logger.warning(f"Unknown category {item.get('category')}, defaulting to billing")
            category = RegulationCategory.BILLING
            reg_type = RegulationType.FEDERAL
        
        effective_date = datetime.strptime(item["effective_date"], "%Y-%m-%d")
        
        return Regulation(
            code=item["code"],
            name=item["name"],
            regulation_type=reg_type,
            category=category,
            description=item.get("description"),
            requirements=item.get("requirements", ""),
            effective_date=effective_date,
            termination_date=None,
            is_active=item.get("is_active", True),
            source_url=item.get("source_url", ""),
            graph_id="",  # Will be created when knowledge graph is built
        )


async def main():
    """Main ingestion function for regulations."""
    logger.info("Starting regulatory data ingestion...")
    
    from ..backend.app.core.database import get_db
    
    ingestor = RegulationsIngestor(batch_size=100)
    
    async with get_db() as db:
        result = await ingestor.ingest(db)
        
        logger.info(f"Regulatory ingestion complete: {result}")
        
        return result


if __name__ == "__main__":
    asyncio.run(main())
