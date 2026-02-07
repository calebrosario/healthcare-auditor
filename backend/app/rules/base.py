"""
Base classes and data structures for rules engine.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class RuleResult:
    """
    Result of a single rule evaluation.
    """
    rule_id: str
    rule_name: str
    passed: Optional[bool]  # None means rule was skipped
    skipped: bool = False
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    is_critical: bool = False  # Critical rule that determines final decision
    is_fatal: bool = False  # Fatal failure that rejects claim
    weight: float = 1.0  # Weight for aggregated scoring
    score: Optional[float] = None  # Score if applicable (0-1)
    context_updates: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChainResult:
    """
    Result of rule chain execution.
    """
    claim_id: str
    results: List[RuleResult]
    final_decision: str  # APPROVED, REJECTED, REVIEW_REQUIRED, PENDING
    fraud_score: float  # 0-1, higher = more fraud risk
    compliance_score: float  # 0-1, higher = more compliant
    total_execution_time_ms: float
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """
    Final result of bill evaluation including all context.
    """
    claim_id: str
    chain_result: ChainResult
    enriched_context: Dict[str, Any] = field(default_factory=dict)
    phase4_results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class BaseRule(ABC):
    """
    Abstract base class for all rule types.
    All rule implementations must inherit from this class.
    """

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique rule identifier."""
        pass

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable rule name."""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Rule execution priority (lower = earlier execution).
        Priority ranges: 1-100.
        - 1-10: Fast validation rules (format checks)
        - 11-30: Medical necessity rules
        - 31-50: Business logic rules
        - 51-100: Optional/enhancement rules
        """
        pass

    @property
    def is_critical(self) -> bool:
        """Whether this rule determines final decision."""
        return False

    @property
    def is_fatal(self) -> bool:
        """Whether this rule is a fatal rejection."""
        return False

    @abstractmethod
    async def evaluate(
        self,
        bill: Any,  # Bill model or dict
        context: Dict[str, Any]
    ) -> RuleResult:
        """
        Evaluate bill against this rule.

        Args:
            bill: The bill/claim to validate
            context: Enriched context (provider, regulations, historical data)

        Returns:
            RuleResult with evaluation outcome
        """
        pass

    async def _get_required_fields(self) -> List[str]:
        """
        Get list of required fields for this rule.
        Override in subclasses.
        """
        return []

    def _has_required_fields(self, bill: Any) -> bool:
        """
        Check if bill has all required fields.
        """
        required_fields = self._get_required_fields()
        if not required_fields:
            return True

        # Handle both dict and object types
        if isinstance(bill, dict):
            return all(field in bill and bill[field] is not None for field in required_fields)
        else:
            return all(hasattr(bill, field) and getattr(bill, field) is not None for field in required_fields)

    def _missing_fields(self, bill: Any) -> List[str]:
        """Get list of missing required fields."""
        required_fields = self._get_required_fields()
        if isinstance(bill, dict):
            return [field for field in required_fields if field not in bill or bill[field] is None]
        else:
            return [field for field in required_fields if not hasattr(bill, field) or getattr(bill, field) is None]
