"""
Unit tests for rules engine and all rule types.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from backend.app.rules.base import BaseRule, RuleResult, ChainResult, EvaluationResult
from backend.app.rules.coding_rules import (
    ICD10ValidationRule,
    CPTValidationRule,
    DXPairValidationRule,
)
from backend.app.rules.medical_necessity_rules import (
    DocumentationCompletenessRule,
    MedicalNecessityScoreRule,
)
from backend.app.rules.frequency_rules import (
    ProcedureFrequencyRule,
    PatientFrequencyRule,
)
from backend.app.rules.billing_rules import AmountLimitRule, DuplicateDetectionRule


@pytest.fixture
async def neo4j_session():
    """Mock Neo4j session for testing."""
    return AsyncMock()


@pytest.fixture
async def db_session():
    """Mock database session for testing."""
    return AsyncMock()


class MockProvider:
    """Mock provider object for testing."""

    def __init__(self, id=1, npi="1234567890", name="Test Provider"):
        self.id = id
        self.npi = npi
        self.name = name


class MockBill:
    """Mock bill object for testing."""

    def __init__(
        self,
        claim_id="TEST-001",
        patient_id="PATIENT-001",
        provider_id=1,
        provider=None,
        procedure_code="99214",
        diagnosis_code="I10",
        billed_amount=150.0,
        allowed_amount=150.0,
        bill_date=datetime.utcnow(),
        documentation_text="Patient presented with hypertension and headache.",
        medical_necessity_score=0.85,
    ):
        self.claim_id = claim_id
        self.patient_id = patient_id
        self.provider_id = provider_id
        self.provider = (
            provider if provider is not None else MockProvider(id=provider_id)
        )
        self.procedure_code = procedure_code
        self.diagnosis_code = diagnosis_code
        self.billed_amount = billed_amount
        self.allowed_amount = allowed_amount
        self.bill_date = bill_date
        self.documentation_text = documentation_text
        self.medical_necessity_score = medical_necessity_score


class TestICD10ValidationRule:
    """Tests for ICD-10 format validation rule."""

    @pytest.mark.asyncio
    async def test_valid_icd10_code(self, neo4j_session):
        rule = ICD10ValidationRule()
        bill = MockBill(diagnosis_code="I10")

        result = await rule.evaluate(bill, {})

        assert result.rule_id == "ICD10_FORMAT_VALIDATION"
        assert result.rule_name == "ICD-10 Format Validation"
        assert rule.priority == 10
        assert result.passed is True
        assert "valid" in result.message.lower()

    @pytest.mark.asyncio
    async def test_invalid_icd10_format(self, neo4j_session):
        rule = ICD10ValidationRule()
        bill = MockBill(diagnosis_code="12345")

        result = await rule.evaluate(bill, {})

        assert result.passed is False
        assert "invalid" in result.message.lower()

    @pytest.mark.asyncio
    async def test_icd10_with_decimal(self, neo4j_session):
        rule = ICD10ValidationRule()
        bill = MockBill(diagnosis_code="I10.9")

        result = await rule.evaluate(bill, {})

        assert result.passed is True

    @pytest.mark.asyncio
    async def test_missing_diagnosis_code(self, neo4j_session):
        rule = ICD10ValidationRule()
        bill = MockBill(diagnosis_code=None)

        result = await rule.evaluate(bill, {})

        assert result.passed is None
        assert result.skipped is True
        assert "No diagnosis code" in result.message


class TestCPTValidationRule:
    """Tests for CPT code validation rule."""

    @pytest.mark.asyncio
    async def test_valid_cpt_code(self, neo4j_session, db_session):
        rule = CPTValidationRule()
        bill = MockBill(procedure_code="99214")
        context = {"billing_codes": {"99214": {"code": "99214", "status": "active"}}}

        result = await rule.evaluate(bill, context)

        assert result.rule_id == "CPT_CODE_VALIDATION"
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_missing_procedure_code(self, neo4j_session):
        rule = CPTValidationRule()
        bill = MockBill(procedure_code=None)

        result = await rule.evaluate(bill, {})

        assert result.passed is None
        assert result.skipped is True


class TestDXPairValidationRule:
    """Tests for CPT-ICD pair validation rule."""

    @pytest.mark.asyncio
    async def test_valid_dx_pair(self, neo4j_session):
        rule = DXPairValidationRule()
        bill = MockBill(procedure_code="99214", diagnosis_code="I10")

        result = await rule.evaluate(bill, {})

        assert result.rule_id == "DX_PAIR_VALIDATION"
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_invalid_dx_pair(self, neo4j_session):
        rule = DXPairValidationRule()
        bill = MockBill(procedure_code="99214", diagnosis_code="Z99")  # Invalid pairing

        result = await rule.evaluate(bill, {})

        assert result.passed is False


class TestDocumentationCompletenessRule:
    """Tests for documentation completeness rule."""

    @pytest.mark.asyncio
    async def test_complete_documentation(self, neo4j_session):
        rule = DocumentationCompletenessRule()
        bill = MockBill(
            documentation_text="Patient presented with hypertension and headache. Thorough examination performed."
        )

        result = await rule.evaluate(bill, {})

        assert result.passed is True

    @pytest.mark.asyncio
    async def test_incomplete_documentation(self, neo4j_session):
        rule = DocumentationCompletenessRule()
        bill = MockBill(documentation_text="Brief visit.")

        result = await rule.evaluate(bill, {})

        assert result.passed is False
        assert "too brief" in result.message.lower()

    @pytest.mark.asyncio
    async def test_missing_documentation(self, neo4j_session):
        rule = DocumentationCompletenessRule()
        bill = MockBill(documentation_text="")

        result = await rule.evaluate(bill, {})

        assert result.passed is False
        assert "missing" in result.message.lower()


class TestMedicalNecessityScoreRule:
    """Tests for medical necessity score rule."""

    @pytest.mark.asyncio
    async def test_high_necessity_score(self, neo4j_session):
        rule = MedicalNecessityScoreRule()
        bill = MockBill(
            procedure_code="99214", diagnosis_code="I10", medical_necessity_score=0.85
        )

        result = await rule.evaluate(bill, {})

        assert result.passed is True
        assert result.score == 0.85

    @pytest.mark.asyncio
    async def test_low_necessity_score(self, neo4j_session):
        rule = MedicalNecessityScoreRule()
        bill = MockBill(
            procedure_code="99214", diagnosis_code="I10", medical_necessity_score=0.5
        )

        result = await rule.evaluate(bill, {})

        assert result.passed is False
        assert result.score == 0.5

    @pytest.mark.asyncio
    async def test_pre_calculated_score_used(self, neo4j_session):
        rule = MedicalNecessityScoreRule()
        # When score is already calculated, it should be used
        bill = MockBill(
            procedure_code="99214", diagnosis_code="I10", medical_necessity_score=0.9
        )

        result = await rule.evaluate(bill, {})

        assert result.passed is True
        assert result.score == 0.9


class TestProcedureFrequencyRule:
    """Tests for procedure frequency rule."""

    @pytest.mark.asyncio
    async def test_normal_frequency(self, neo4j_session):
        rule = ProcedureFrequencyRule()
        bill = MockBill(procedure_code="99214")

        historical_bills = [MockBill(procedure_code="99214") for _ in range(10)]
        context = {"historical_bills": historical_bills}

        result = await rule.evaluate(bill, context)

        assert result.passed is True

    @pytest.mark.asyncio
    async def test_excessive_frequency(self, neo4j_session):
        rule = ProcedureFrequencyRule()
        bill = MockBill(procedure_code="99214")

        historical_bills = [MockBill(procedure_code="99214") for _ in range(51)]
        context = {"historical_bills": historical_bills}

        result = await rule.evaluate(bill, context)

        assert result.passed is False
        assert "51" in result.message  # Check that frequency count is in message

    @pytest.mark.asyncio
    async def test_missing_historical_data(self, neo4j_session):
        rule = ProcedureFrequencyRule()
        bill = MockBill(procedure_code="99214")
        context = {}

        result = await rule.evaluate(bill, context)

        assert result.passed is None
        assert result.skipped is True


class TestPatientFrequencyRule:
    """Tests for patient frequency rule."""

    @pytest.mark.asyncio
    async def test_normal_frequency(self, neo4j_session):
        rule = PatientFrequencyRule()
        bill = MockBill(procedure_code="99214")

        historical_bills = [MockBill(procedure_code="99214") for _ in range(5)]
        context = {"historical_bills": historical_bills}

        result = await rule.evaluate(bill, context)

        assert result.passed is True

    @pytest.mark.asyncio
    async def test_excessive_patient_frequency(self, neo4j_session):
        rule = PatientFrequencyRule()
        bill = MockBill(procedure_code="99214")

        historical_bills = [MockBill(procedure_code="99214") for _ in range(11)]
        context = {"historical_bills": historical_bills}

        result = await rule.evaluate(bill, context)

        assert result.passed is False
        assert "11" in result.message  # Check frequency count


class TestAmountLimitRule:
    """Tests for amount limit rule."""

    @pytest.mark.asyncio
    async def test_within_limit(self, neo4j_session):
        rule = AmountLimitRule()
        bill = MockBill(billed_amount=150.0, allowed_amount=150.0)

        result = await rule.evaluate(bill, {})

        assert result.passed is True
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_exceeds_limit(self, neo4j_session):
        rule = AmountLimitRule()
        bill = MockBill(billed_amount=200.0, allowed_amount=150.0)

        result = await rule.evaluate(bill, {})

        assert result.passed is False
        assert "exceeds" in result.message.lower()
        assert result.score == 1.0  # min(50/30, 1.0) = 1.0

    @pytest.mark.asyncio
    async def test_missing_allowed_amount(self, neo4j_session):
        rule = AmountLimitRule()
        bill = MockBill(billed_amount=150.0, allowed_amount=None)

        result = await rule.evaluate(bill, {})

        assert result.passed is None
        assert result.skipped is True


class TestDuplicateDetectionRule:
    """Tests for duplicate detection rule."""

    @pytest.mark.asyncio
    async def test_no_duplicates(self, neo4j_session):
        rule = DuplicateDetectionRule()
        bill = MockBill(claim_id="TEST-001")

        historical_bills = [
            MockBill(
                claim_id="OTHER-001", patient_id="PATIENT-002", procedure_code="99214"
            )
        ]
        context = {"historical_bills": historical_bills}

        result = await rule.evaluate(bill, context)

        assert result.passed is True
        assert "No duplicate" in result.message

    @pytest.mark.asyncio
    async def test_exact_duplicate(self, neo4j_session):
        rule = DuplicateDetectionRule()
        shared_date = datetime.utcnow()
        bill = MockBill(
            claim_id="TEST-001", procedure_code="99214", bill_date=shared_date
        )

        duplicate = MockBill(
            claim_id="OTHER-001", procedure_code="99214", bill_date=shared_date
        )
        context = {"historical_bills": [duplicate]}

        result = await rule.evaluate(bill, context)

        assert result.passed is False
        assert result.is_fatal is True
        assert result.is_critical is True
        assert "duplicate" in result.message.lower()

    @pytest.mark.asyncio
    async def test_near_duplicate(self, neo4j_session):
        rule = DuplicateDetectionRule()
        bill = MockBill(
            claim_id="TEST-001", procedure_code="99214", bill_date=datetime.utcnow()
        )

        near_duplicate = MockBill(
            claim_id="OTHER-002",
            procedure_code="99214",
            bill_date=datetime.utcnow() - timedelta(days=3),
        )
        context = {"historical_bills": [near_duplicate]}

        result = await rule.evaluate(bill, context)

        assert result.passed is False
        assert "near-duplicate" in result.message.lower()
        assert result.score == 0.3


class TestRuleChain:
    """Tests for rule chain execution."""

    @pytest.mark.asyncio
    async def test_rule_ordering(self, neo4j_session):
        from backend.app.core.rules_engine import RuleChain

        chain = RuleChain()
        chain.add_rule(ICD10ValidationRule())
        chain.add_rule(CPTValidationRule())
        chain.add_rule(DuplicateDetectionRule())

        assert len(chain.rules) == 3
        assert chain.rules[0].priority == 10
        assert chain.rules[1].priority == 10
        assert chain.rules[2].priority == 10

    @pytest.mark.asyncio
    async def test_full_chain_execution(self, neo4j_session):
        from backend.app.core.rules_engine import RuleChain

        chain = RuleChain()
        chain.add_rule(ICD10ValidationRule())
        chain.add_rule(DuplicateDetectionRule())

        bill = MockBill()

        result = await chain.execute(bill, {})

        assert isinstance(result, ChainResult)
        assert result.final_decision in [
            "APPROVED",
            "REJECTED",
            "REVIEW_REQUIRED",
            "PENDING",
        ]
        assert len(result.results) == 2
