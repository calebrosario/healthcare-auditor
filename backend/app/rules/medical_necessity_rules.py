"""
Medical necessity evidence validation rules.
"""
from typing import Dict, Any, List
from .base import BaseRule, RuleResult


class DocumentationCompletenessRule(BaseRule):
    """Checks if clinical documentation is complete."""

    @property
    def rule_id(self) -> str:
        return "DOCUMENTATION_COMPLETENESS"

    @property
    def rule_name(self) -> str:
        return "Documentation Completeness Check"

    @property
    def priority(self) -> int:
        return 15

    def _get_required_fields(self) -> List[str]:
        return ["documentation_text"]

    async def evaluate(self, bill: Any, context: Dict[str, Any]) -> RuleResult:
        if not self._has_required_fields(bill):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=None,
                skipped=True,
                message=f"Missing required fields: {self._missing_fields(bill)}"
            )

        documentation = getattr(bill, "documentation_text", None)

        if not documentation:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                message="Clinical documentation is missing",
                details={"documentation_length": 0},
                weight=1.0
            )

        doc_length = len(documentation.strip())

        # Check for minimum documentation length
        is_complete = doc_length >= 50

        if is_complete:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=True,
                message="Clinical documentation is present",
                details={"documentation_length": doc_length},
                weight=0.5
            )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=False,
            message="Clinical documentation is too brief (<50 characters)",
            details={"documentation_length": doc_length},
            weight=1.0
        )


class MedicalNecessityScoreRule(BaseRule):
    """Calculates medical necessity score based on CPT-ICD pairing."""

    @property
    def rule_id(self) -> str:
        return "MEDICAL_NECESSITY_SCORE"

    @property
    def rule_name(self) -> str:
        return "Medical Necessity Score"

    @property
    def priority(self) -> int:
        return 25

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
        medical_necessity_score = getattr(bill, "medical_necessity_score", None)

        # If score already calculated, use it
        if medical_necessity_score is not None:
            is_valid = medical_necessity_score >= 0.7

            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=is_valid,
                message=f"Medical necessity score: {medical_necessity_score:.2f}",
                details={"medical_necessity_score": medical_necessity_score},
                score=medical_necessity_score,
                weight=0.5
            )

        # Calculate score based on CPT-ICD pairing
        # High-priority procedures (99214) + valid diagnosis = higher necessity
        necessity_scores = {
            "99214": 0.9,
            "99213": 0.8,
            "99212": 0.8,
            "99203": 0.7,
        }

        score = necessity_scores.get(procedure_code, 0.5)

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=score >= 0.7,
            message=f"Medical necessity score: {score:.2f}",
            details={"medical_necessity_score": score},
            score=score,
            weight=0.5
        )
