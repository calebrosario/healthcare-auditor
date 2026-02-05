"""
Frequency and geographic constraint validation rules.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseRule, RuleResult


class ProcedureFrequencyRule(BaseRule):
    """Checks if provider has billed same procedure too frequently."""

    @property
    def rule_id(self) -> str:
        return "PROCEDURE_FREQUENCY"

    @property
    def rule_name(self) -> str:
        return "Procedure Frequency Limit"

    @property
    def priority(self) -> int:
        return 30

    def _get_required_fields(self) -> List[str]:
        return ["provider", "procedure_code", "bill_date"]

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        if not self._has_required_fields(bill):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message=f"Missing required fields: {self._missing_fields(bill)}"
            )

        provider = getattr(bill, "provider", None)
        procedure_code = getattr(bill, "procedure_code", None)
        bill_date = getattr(bill, "bill_date", None)

        if not provider or not procedure_code or not bill_date:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="Missing provider, procedure code, or bill date"
            )

        # Check historical bills for same provider and procedure
        historical_bills = context.get("historical_bills", [])

        if not historical_bills:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="No historical billing data available"
            )

        # Count bills with same procedure from this provider in last 30 days
        cutoff_date = bill_date - timedelta(days=30)
        recent_bills = [
            b for b in historical_bills
            if getattr(b, "procedure_code") == procedure_code
            and getattr(b, "provider_id") == getattr(provider, "id", None)
            and getattr(b, "bill_date", datetime.min) >= cutoff_date
        ]

        frequency_limit = 50  # Max 50 same procedures per 30 days

        is_valid = len(recent_bills) <= frequency_limit

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=is_valid,
            message=f"Procedure frequency: {len(recent_bills)}/30 days (limit: {frequency_limit})",
            details={
                "frequency": len(recent_bills),
                "frequency_limit": frequency_limit,
                "recent_bills": len(recent_bills)
            },
            score=0.0 if is_valid else min(len(recent_bills) / frequency_limit, 1.0),
            weight=0.5
        )


class PatientFrequencyRule(BaseRule):
    """Checks if patient has received same procedure too frequently."""

    @property
    def rule_id(self) -> str:
        return "PATIENT_FREQUENCY"

    @property
    def rule_name(self) -> str:
        return "Patient Frequency Limit"

    @property
    def priority(self) -> int:
        return 30

    def _get_required_fields(self) -> List[str]:
        return ["patient_id", "procedure_code", "bill_date"]

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        if not self._has_required_fields(bill):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message=f"Missing required fields: {self._missing_fields(bill)}"
            )

        patient_id = getattr(bill, "patient_id", None)
        procedure_code = getattr(bill, "procedure_code", None)
        bill_date = getattr(bill, "bill_date", None)

        if not patient_id or not procedure_code or not bill_date:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="Missing patient ID, procedure code, or bill date"
            )

        # Check historical bills for same patient and procedure
        historical_bills = context.get("historical_bills", [])

        if not historical_bills:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message="No historical billing data available"
            )

        # Count bills with same procedure for this patient in last 90 days
        cutoff_date = bill_date - timedelta(days=90)
        recent_bills = [
            b for b in historical_bills
            if getattr(b, "procedure_code") == procedure_code
            and getattr(b, "patient_id") == patient_id
            and getattr(b, "bill_date", datetime.min) >= cutoff_date
        ]

        frequency_limit = 10  # Max 10 same procedures per 90 days

        is_valid = len(recent_bills) <= frequency_limit

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=is_valid,
            message=f"Patient procedure frequency: {len(recent_bills)}/90 days (limit: {frequency_limit})",
            details={
                "frequency": len(recent_bills),
                "frequency_limit": frequency_limit,
                "recent_bills": len(recent_bills)
            },
            score=0.0 if is_valid else min(len(recent_bills) / frequency_limit, 1.0),
            weight=0.3
        )
