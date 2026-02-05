"""
CPT and ICD-10 coding validation rules.
"""
import re
from typing import List, Dict, Any
from .base import BaseRule, RuleResult


class ICD10ValidationRule(BaseRule):
    """Validates ICD-10 diagnosis code format."""

    @property
    def rule_id(self) -> str:
        return "ICD10_FORMAT_VALIDATION"

    @property
    def rule_name(self) -> str:
        return "ICD-10 Format Validation"

    @property
    def priority(self) -> int:
        return 10

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        diagnosis_code = getattr(bill, "diagnosis_code", None)

        if not diagnosis_code:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="No diagnosis code to validate"
            )

        # ICD-10 format: Letter + 2 digits + optional decimal + 0-4 digits
        icd10_pattern = r"^[A-Z]\d{2}\.?\d{0,4}$"

        is_valid = bool(re.match(icd10_pattern, diagnosis_code))

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=is_valid,
            message=f"Diagnosis code format {'valid' if is_valid else 'invalid'}",
            details={"code": diagnosis_code, "pattern": icd10_pattern},
            weight=1.0
        )


class CPTValidationRule(BaseRule):
    """Validates CPT procedure code exists and is active."""

    @property
    def rule_id(self) -> str:
        return "CPT_CODE_VALIDATION"

    @property
    def rule_name(self) -> str:
        return "CPT Code Validation"

    @property
    def priority(self) -> int:
        return 10

    def _get_required_fields(self) -> List[str]:
        return ["procedure_code"]

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        if not self._has_required_fields(bill):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message=f"Missing required fields: {self._missing_fields(bill)}"
            )

        procedure_code = getattr(bill, "procedure_code", None)

        # Check if code exists in billing codes table (via context)
        billing_codes = context.get("billing_codes", {})

        if not billing_codes:
            # If no codes loaded, assume valid for now
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="Billing codes not loaded for validation"
            )

        code_info = billing_codes.get(procedure_code)

        is_valid = code_info is not None and code_info.get("status") == "active"

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=is_valid,
            message=f"Procedure code {'valid and active' if is_valid else 'invalid or inactive'}",
            details={"code": procedure_code, "code_info": code_info},
            weight=1.0
        )


class DXPairValidationRule(BaseRule):
    """Validates CPT-ICD pairing for medical necessity."""

    @property
    def rule_id(self) -> str:
        return "DX_PAIR_VALIDATION"

    @property
    def rule_name(self) -> str:
        return "CPT-ICD Pair Validation"

    @property
    def priority(self) -> int:
        return 20

    def _get_required_fields(self) -> List[str]:
        return ["procedure_code", "diagnosis_code"]

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        if not self._has_required_fields(bill):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message=f"Missing required fields: {self._missing_fields(bill)}"
            )

        procedure_code = getattr(bill, "procedure_code", None)
        diagnosis_code = getattr(bill, "diagnosis_code", None)

        # Common valid CPT-ICD pairs (simplified for demo)
        valid_pairs = {
            "99214": ["I10", "I11", "E11.9", "J45.909"],
            "99213": ["I10", "I11", "M54.5"],
            "99212": ["I10", "J45.901", "M54.2"],
            "99203": ["I10", "M25.1", "J01.901"],
        }

        is_valid = any(diagnosis_code in valid_pairs.get(procedure_code, []) for diagnosis_code in [diagnosis_code] if diagnosis_code)

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=is_valid,
            message=f"CPT-ICD pairing {'valid' if is_valid else 'invalid'}",
            details={
                "procedure_code": procedure_code,
                "diagnosis_code": diagnosis_code,
                "valid_pairs": valid_pairs.get(procedure_code, [])
            },
            weight=0.5
        )
