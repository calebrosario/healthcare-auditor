"""
Billing constraint and duplicate detection rules.
"""
from typing import Dict, Any, List
from .base import BaseRule, RuleResult


class AmountLimitRule(BaseRule):
    """Checks if billed amount exceeds allowed amount."""

    @property
    def rule_id(self) -> str:
        return "AMOUNT_LIMIT"

    @property
    def rule_name(self) -> str:
        return "Billing Amount Limit"

    @property
    def priority(self) -> int:
        return 35

    def _get_required_fields(self) -> List[str]:
        return ["billed_amount", "allowed_amount"]

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        if not self._has_required_fields(bill):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message=f"Missing required fields: {self._missing_fields(bill)}"
            )

        billed_amount = getattr(bill, "billed_amount", None)
        allowed_amount = getattr(bill, "allowed_amount", None)

        if not billed_amount:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="No billed amount provided"
            )

        if allowed_amount is None:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="No allowed amount determined"
            )

        # Check if billed amount exceeds allowed amount by more than 20%
        overage = billed_amount - allowed_amount
        overage_threshold = allowed_amount * 0.20

        is_valid = overage <= overage_threshold

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=is_valid,
            message=f"Billed amount {billed_amount:.2f} vs allowed {allowed_amount:.2f}: {'within limit' if is_valid else f'exceeds by ${overage:.2f}'}",
            details={
                "billed_amount": billed_amount,
                "allowed_amount": allowed_amount,
                "overage": overage,
                "overage_threshold": overage_threshold
            },
            score=0.0 if is_valid else min(overage / overage_threshold, 1.0),
            weight=1.0
        )


class DuplicateDetectionRule(BaseRule):
    """Detects duplicate or near-duplicate bills."""

    @property
    def rule_id(self) -> str:
        return "DUPLICATE_DETECTION"

    @property
    def rule_name(self) -> str:
        return "Duplicate Bill Detection"

    @property
    def priority(self) -> int:
        return 10

    @property
    def is_critical(self) -> bool:
        return True

    @property
    def is_fatal(self) -> bool:
        return True

    def _get_required_fields(self) -> List[str]:
        return ["patient_id", "provider_id", "procedure_code", "bill_date", "billed_amount"]

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        if not self._has_required_fields(bill):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message=f"Missing required fields: {self._missing_fields(bill)}"
            )

        claim_id = getattr(bill, "claim_id", None)
        patient_id = getattr(bill, "patient_id", None)
        provider_id = getattr(bill, "provider_id", None)
        procedure_code = getattr(bill, "procedure_code", None)
        bill_date = getattr(bill, "bill_date", None)
        billed_amount = getattr(bill, "billed_amount", None)

        if not all([claim_id, patient_id, provider_id, procedure_code, bill_date, billed_amount]):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="Missing key fields for duplicate detection"
            )

        # Check for exact duplicates (same patient, provider, procedure, date)
        historical_bills = context.get("historical_bills", [])

        exact_duplicates = [
            b for b in historical_bills
            if getattr(b, "claim_id") != claim_id  # Exclude current bill
            and getattr(b, "patient_id") == patient_id
            and getattr(b, "provider_id") == provider_id
            and getattr(b, "procedure_code") == procedure_code
            and getattr(b, "bill_date") == bill_date
        ]

        if exact_duplicates:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                is_fatal=True,
                is_critical=True,
                message=f"Exact duplicate bill found: {len(exact_duplicates)} existing bill(s)",
                details={
                    "duplicate_count": len(exact_duplicates),
                    "duplicate_claim_ids": [getattr(b, "claim_id") for b in exact_duplicates]
                },
                weight=1.0,
                score=1.0
            )

        # Check for near-duplicates (same patient, provider, procedure, within 7 days)
        from datetime import timedelta
        cutoff_date = bill_date - timedelta(days=7)
        near_duplicates = [
            b for b in historical_bills
            if getattr(b, "claim_id") != claim_id
            and getattr(b, "patient_id") == patient_id
            and getattr(b, "provider_id") == provider_id
            and getattr(b, "procedure_code") == procedure_code
            and getattr(b, "bill_date", datetime.min) >= cutoff_date
            and abs((getattr(b, "bill_date", datetime.min) - bill_date).days) <= 7
        ]

        if near_duplicates:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                is_fatal=False,
                message=f"Near-duplicate bill found: {len(near_duplicates)} bill(s) within 7 days",
                details={
                    "near_duplicate_count": len(near_duplicates),
                    "near_duplicate_claim_ids": [getattr(b, "claim_id") for b in near_duplicates]
                },
                weight=0.5,
                score=0.3
            )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            message="No duplicate bills found",
            details={"exact_duplicates": 0, "near_duplicates": 0},
            weight=1.0,
            score=0.0
        )
