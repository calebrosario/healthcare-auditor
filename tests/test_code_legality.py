# tests/test_code_legality.py
import pytest
import sys

sys.path.insert(0, "/Users/calebrosario/Documents/sandbox/healthcare-auditor/backend")

from app.core.code_legality import CodeLegalityAnalyzer
from unittest.mock import AsyncMock, MagicMock
from dataclasses import dataclass


@dataclass
class MockBill:
    procedure_code: str = "99214"
    diagnosis_code: str = "I10"
    billed_amount: float = 150.0


@pytest.mark.asyncio
async def test_verify_code_compatibility():
    analyzer = CodeLegalityAnalyzer(db=AsyncMock())
    result = await analyzer.verify_code_compatibility(
        procedure_code="99214", diagnosis_code="I10", payer_id=1
    )
    assert "is_compatible" in result
    assert result["is_compatible"] == True


@pytest.mark.asyncio
async def test_check_bundling_rules():
    analyzer = CodeLegalityAnalyzer(db=AsyncMock())
    result = await analyzer.check_bundling_rules(
        procedure_codes=["99213", "99214"], payer_id=1
    )
    assert "should_bundle" in result
    assert result["should_bundle"] == False


@pytest.mark.asyncio
async def test_validate_allowed_amounts():
    analyzer = CodeLegalityAnalyzer(db=AsyncMock())
    result = await analyzer.validate_allowed_amounts(
        procedure_code="99214", billed_amount=150.0, payer_id=1, locality="CA"
    )
    assert "is_within_range" in result
    assert result["is_within_range"] == True
