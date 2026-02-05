"""
Rule engine orchestrator for healthcare billing compliance validation.

This module provides the RuleEngine class that coordinates rule execution,
aggregates results, and integrates with PostgreSQL and Neo4j.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from neo4j import AsyncSession as Neo4jSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models.bill import Bill
from ..models.compliance_check import ComplianceCheck, ComplianceStatus
from .base import BaseRule, RuleResult, ChainResult, EvaluationResult
from .coding_rules import ICD10ValidationRule, CPTValidationRule, DXPairValidationRule
from .medical_necessity_rules import DocumentationCompletenessRule, MedicalNecessityScoreRule
from .frequency_rules import ProcedureFrequencyRule, PatientFrequencyRule
from .billing_rules import AmountLimitRule, DuplicateDetectionRule


# Configure logging
logger = logging.getLogger(__name__)


class RuleChain:
    """Manages rule execution with prioritization and early termination."""

    def __init__(self):
        self.rules: List[BaseRule] = []

    def add_rule(self, rule: BaseRule) -> None:
        """
        Add rule to chain.

        Args:
            rule: Rule instance to add
        """
        self.rules.append(rule)
        # Sort rules by priority (lower = earlier)
        self.rules.sort(key=lambda r: r.priority)

    async def execute(self, bill: Any, context: Dict[str, Any]) -> ChainResult:
        """
        Execute rules in priority order with early termination.

        Args:
            bill: Bill object or dict to evaluate
            context: Enriched context (provider, regulations, historical data)

        Returns:
            ChainResult with all rule results and final decision
        """
        results = []
        context_updates = {}

        for rule in self.rules:
            try:
                rule_start = datetime.utcnow()
                result = await rule.evaluate(bill, context)
                rule_end = datetime.utcnow()
                result.execution_time_ms = (rule_end - rule_start).total_seconds() * 1000

                results.append(result)

                # Update context for subsequent rules
                context_updates.update(result.context_updates)

                # Early termination for critical decisions
                if result.is_critical and result.passed:
                    logger.info(f"Critical approval by {rule.rule_id}: {result.message}")
                    break
                elif result.is_fatal and not result.passed:
                    logger.warning(f"Fatal rejection by {rule.rule_id}: {result.message}")
                    break

            except Exception as e:
                logger.error(f"Error executing rule {rule.rule_id}: {e}")
                results.append(RuleResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.rule_name,
                    passed=None,
                    skipped=True,
                    message=f"Rule execution error: {str(e)}",
                    details={"error": str(e), "exception_type": type(e).__name__}
                ))

        final_decision = self._determine_final_decision(results, context)

        return ChainResult(
            claim_id=getattr(bill, "claim_id", bill.get("claim_id", "unknown")),
            results=results,
            final_decision=final_decision,
            fraud_score=self._calculate_fraud_score(results, context),
            compliance_score=self._calculate_compliance_score(results, context),
            total_execution_time_ms=sum(r.execution_time_ms for r in results),
            issues=[r.message for r in results if not r.passed and r.is_fatal],
            warnings=[r.message for r in results if not r.passed and not r.is_fatal]
        )

    def _determine_final_decision(self, results: List[RuleResult], context: Dict[str, Any]) -> str:
        """
        Determine final decision based on rule results.

        Decision hierarchy:
        1. Fatal failure → REJECTED
        2. No fatal failures, warnings present → REVIEW_REQUIRED
        3. All passed → APPROVED
        4. Non-fatal failures → REVIEW_REQUIRED
        """
        # Check for fatal failures
        fatal_failures = [r for r in results if not r.passed and r.is_fatal]
        if fatal_failures:
            return "REJECTED"

        # Check for skipped rules (missing data)
        skipped_rules = [r for r in results if r.skipped]
        if skipped_rules:
            return "PENDING"

        # Check for warnings
        non_fatal_failures = [r for r in results if not r.passed and not r.is_fatal]
        passed_rules = [r for r in results if r.passed]

        if non_fatal_failures and passed_rules:
            # Mix of passed and failed rules → review
            if len(non_fatal_failures) <= len(passed_rules):
                return "REVIEW_REQUIRED"
            return "REJECTED"

        if passed_rules:
            return "APPROVED"

        return "REJECTED"

    def _calculate_fraud_score(self, results: List[RuleResult], context: Dict[str, Any]) -> float:
        """
        Calculate composite fraud score from rule results.

        Higher fraud score = higher fraud risk (0-1 scale).

        Args:
            results: List of rule execution results
            context: Enriched context

        Returns:
            Fraud score between 0 and 1
        """
        # Start with base score
        fraud_score = 0.0

        # Weight contributions from failed rules
        for result in results:
            if not result.passed and result.score is not None:
                fraud_score += result.weight * result.score

        # Cap at 1.0
        return min(fraud_score, 1.0)

    def _calculate_compliance_score(self, results: List[RuleResult], context: Dict[str, Any]) -> float:
        """
        Calculate composite compliance score from rule results.

        Higher compliance score = more compliant (0-1 scale).

        Args:
            results: List of rule execution results
            context: Enriched context

        Returns:
            Compliance score between 0 and 1
        """
        # Start with perfect score
        compliance_score = 1.0

        # Deduct for failed rules
        for result in results:
            if not result.passed and result.score is not None:
                compliance_score -= result.weight * result.score

        # Ensure minimum 0
        return max(compliance_score, 0.0)


class RuleEngine:
    """
    Main orchestrator for healthcare billing rules engine.

    Manages rule loading, execution, and result aggregation.
    Integrates with PostgreSQL for persistence and Neo4j for context enrichment.
    """

    def __init__(self, db: AsyncSession, neo4j: Optional[Neo4jSession] = None):
        """
        Initialize rules engine.

        Args:
            db: PostgreSQL async session
            neo4j: Neo4j async session (optional, for context enrichment)
        """
        self.db = db
        self.neo4j = neo4j
        self.rule_chain = RuleChain()
        self._initialize_rules()
        self.stats = {
            "bills_evaluated": 0,
            "rules_executed": 0,
            "errors": 0
        }

    def _initialize_rules(self):
        """
        Initialize all rule types in priority order.

        Rules are loaded from highest priority (earliest execution) to lowest.
        """
        # Priority 1-10: Fast validation rules
        self.rule_chain.add_rule(ICD10ValidationRule())
        self.rule_chain.add_rule(CPTValidationRule())
        self.rule_chain.add_rule(DuplicateDetectionRule())

        # Priority 11-30: Medical necessity rules
        self.rule_chain.add_rule(DocumentationCompletenessRule())
        self.rule_chain.add_rule(MedicalNecessityScoreRule())
        self.rule_chain.add_rule(DXPairValidationRule())

        # Priority 31-50: Business logic rules
        self.rule_chain.add_rule(ProcedureFrequencyRule())
        self.rule_chain.add_rule(PatientFrequencyRule())
        self.rule_chain.add_rule(AmountLimitRule())

        logger.info(f"Initialized {len(self.rule_chain.rules)} rules")

    async def enrich_context(self, bill: Bill) -> Dict[str, Any]:
        """
        Enrich bill context with Neo4j data.

        Queries provider network, regulations, and other context.

        Args:
            bill: Bill object to enrich

        Returns:
            Dictionary with enriched context data
        """
        context = {"bill": bill}

        if not self.neo4j:
            return context

        try:
            # Query provider network and relationships
            provider_query = """
            MATCH (p:Provider {npi: $npi})-[:PROVIDES_AT]->(h:Hospital)
            OPTIONAL MATCH (p)-[:INSURES]->(i:Insurer)
            OPTIONAL MATCH (p)-[:CONTRACT_WITH]->(c2:Hospital)
            OPTIONAL MATCH (p)-[:OWNS_FACILITY]->(o:Hospital)
            RETURN p.name AS provider_name, p.specialty, h.name AS hospital_name,
                   i.name AS insurer_name, c2.name AS contracted_hospital,
                   o.name AS owned_hospital
            LIMIT 10
            """

            result = await self.neo4j.run(provider_query, parameters={"npi": bill.provider.npi if hasattr(bill.provider, 'npi') else None})
            provider_data = [record.data() for record in await result.data()]

            if provider_data:
                context["provider_network"] = provider_data[0]

            # Query regulations applicable to this bill
            regulation_query = """
            MATCH (r:Regulation)-[:APPLIES_TO]->(:Bill {claim_id: $claim_id})
            RETURN r.code, r.name, r.category, r.is_active
            ORDER BY r.category
            """

            result = await self.neo4j.run(regulation_query, parameters={"claim_id": bill.claim_id})
            regulation_data = [record.data() for record in await result.data()]

            if regulation_data:
                context["applicable_regulations"] = regulation_data

            logger.debug(f"Enriched context for bill {bill.claim_id}")

        except Exception as e:
            logger.warning(f"Failed to enrich context for bill {bill.claim_id}: {e}")

        return context

    async def evaluate_bill(self, bill_id: str) -> EvaluationResult:
        """
        Evaluate a single bill against all rules.

        Args:
            bill_id: Claim ID to evaluate

        Returns:
            EvaluationResult with chain result and enriched context
        """
        try:
            # Load bill from database
            stmt = select(Bill).where(Bill.claim_id == bill_id).options(selectinload(Bill.provider))
            result = await self.db.execute(stmt)
            bill = result.scalar_one_or_none()

            if not bill:
                logger.error(f"Bill not found: {bill_id}")
                raise ValueError(f"Bill not found: {bill_id}")

            # Enrich context
            enriched_context = await self.enrich_context(bill)

            # Execute rule chain
            chain_result = await self.rule_chain.execute(bill, enriched_context)

            # Save compliance checks to database
            await self._save_compliance_checks(bill, chain_result.results)

            # Update statistics
            self.stats["bills_evaluated"] += 1
            self.stats["rules_executed"] += len(chain_result.results)
            self.stats["errors"] += len([r for r in chain_result.results if r.skipped])

            logger.info(
                f"Evaluated bill {bill_id}: {chain_result.final_decision}, "
                f"fraud_score={chain_result.fraud_score:.2f}, "
                f"compliance_score={chain_result.compliance_score:.2f}"
            )

            return EvaluationResult(
                claim_id=bill_id,
                chain_result=chain_result,
                enriched_context=enriched_context,
                created_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error evaluating bill {bill_id}: {e}")
            self.stats["errors"] += 1
            raise

    async def batch_evaluate(self, bill_ids: List[str], batch_size: int = 10) -> List[EvaluationResult]:
        """
        Evaluate multiple bills in batches for performance.

        Args:
            bill_ids: List of claim IDs to evaluate
            batch_size: Number of bills to process concurrently

        Returns:
            List of EvaluationResults for all bills
        """
        import asyncio

        results = []
        total_bills = len(bill_ids)

        for i in range(0, total_bills, batch_size):
            batch = bill_ids[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_bills - 1)//batch_size + 1}: {len(batch)} bills")

            # Evaluate bills in batch concurrently
            tasks = [self.evaluate_bill(bid) for bid in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch evaluation failed for bill: {result}")
                else:
                    results.append(result)

        logger.info(f"Batch evaluation complete: {len(results)}/{total_bills} bills processed")
        return results

    async def _save_compliance_checks(self, bill: Bill, rule_results: List[RuleResult]) -> None:
        """
        Save rule results to database as compliance checks.

        Args:
            bill: Bill object
            rule_results: List of rule execution results
        """
        from ..models.regulation import Regulation

        for result in rule_results:
            if result.skipped or result.passed is None:
                continue

            # Create compliance check record
            check = ComplianceCheck(
                bill_id=bill.id,
                regulation_id=None,  # Can be linked to specific regulation if needed
                check_type=result.rule_id,
                description=result.message,
                status=(
                    ComplianceStatus.PASSED if result.passed
                    else ComplianceStatus.FAILED
                ),
                details=str(result.details),
                checked_at=datetime.utcnow(),
                checked_by="rules_engine"
            )

            self.db.add(check)

        await self.db.commit()
        logger.debug(f"Saved {len([r for r in rule_results if not r.skipped])} compliance checks")

    def get_stats(self) -> Dict[str, int]:
        """Get rule engine statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset rule engine statistics."""
        self.stats = {
            "bills_evaluated": 0,
            "rules_executed": 0,
            "errors": 0
        }
