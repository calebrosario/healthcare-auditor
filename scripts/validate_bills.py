#!/usr/bin/env python3
"""
Standlone script for validating bills using rules engine.

Usage:
    python scripts/validate_bills.py --claim-id <CLAIM_ID>
    python scripts/validate_bills.py --batch --input <INPUT_FILE>
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import get_db
from backend.app.core.neo4j import get_neo4j
from backend.app.core.rules_engine import RuleEngine
from backend.models.bill import Bill
from sqlalchemy import select


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def validate_single_bill(claim_id: str) -> None:
    """Validate a single bill claim."""

    from backend.app.config import settings

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        async with async_session_maker() as db:
            # Get Neo4j session if available
            try:
                from neo4j import AsyncGraphDatabase

                neo4j_driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                )
                neo4j_session = await neo4j_driver.session(
                    database=settings.NEO4J_DATABASE
                )
                logger.info("Connected to Neo4j for context enrichment")
            except Exception as e:
                logger.warning(f"Neo4j not available: {e}")
                neo4j_session = None

            # Create rules engine
            engine = RuleEngine(db, neo4j_session)

            # Evaluate bill
            logger.info(f"Validating bill: {claim_id}")
            result = await engine.evaluate_bill(claim_id)

            # Display results
            print(f"\n{'=' * 60}")
            print(f"Bill: {result.chain_result.claim_id}")
            print(f"Final Decision: {result.chain_result.final_decision}")
            print(f"Fraud Score: {result.chain_result.fraud_score:.2f}")
            print(f"Compliance Score: {result.chain_result.compliance_score:.2f}")
            print(
                f"Execution Time: {result.chain_result.total_execution_time_ms:.0f}ms"
            )
            print(f"\nIssues:")
            for issue in result.chain_result.issues:
                print(f"  - {issue}")
            print(f"\nWarnings:")
            for warning in result.chain_result.warnings:
                print(f"  - {warning}")
            print(f"\nRule Results:")
            for rule_result in result.chain_result.results:
                status_icon = "PASS" if rule_result.passed else "FAIL"
                skip_indicator = " (SKIPPED)" if rule_result.skipped else ""
                print(
                    f"  [{status_icon}] {rule_result.rule_id}: {rule_result.message}{skip_indicator}"
                )

            if neo4j_session:
                await neo4j_session.close()
                await neo4j_driver.close()

    except ValueError as e:
        logger.error(f"Bill not found or validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


async def validate_batch(input_file: Path) -> None:
    """Validate bills from input file in batch."""

    from backend.app.config import settings
    import json

    # Load claim IDs from input file
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
            claim_ids = data.get("claim_ids", [])
    except Exception as e:
        logger.error(f"Failed to load input file: {e}")
        sys.exit(1)

    if not claim_ids:
        logger.error("No claim IDs found in input file")
        sys.exit(1)

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        async with async_session_maker() as db:
            # Get Neo4j session if available
            try:
                from neo4j import AsyncGraphDatabase

                neo4j_driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                )
                neo4j_session = await neo4j_driver.session(
                    database=settings.NEO4J_DATABASE
                )
                logger.info("Connected to Neo4j for context enrichment")
            except Exception as e:
                logger.warning(f"Neo4j not available: {e}")
                neo4j_session = None

            # Create rules engine
            engine = RuleEngine(db, neo4j_session)

            # Batch evaluate
            logger.info(f"Validating {len(claim_ids)} bills in batch")
            results = await engine.batch_evaluate(claim_ids, batch_size=10)

            # Display summary
            print(f"\n{'=' * 60}")
            print(f"Batch Validation Summary")
            print(f"{'=' * 60}")
            print(f"Total Bills: {len(results)}")

            approved = sum(
                1 for r in results if r.chain_result.final_decision == "APPROVED"
            )
            rejected = sum(
                1 for r in results if r.chain_result.final_decision == "REJECTED"
            )
            review = sum(
                1 for r in results if r.chain_result.final_decision == "REVIEW_REQUIRED"
            )
            pending = sum(
                1 for r in results if r.chain_result.final_decision == "PENDING"
            )

            print(f"Approved: {approved}")
            print(f"Rejected: {rejected}")
            print(f"Review Required: {review}")
            print(f"Pending: {pending}")

            avg_fraud = sum(r.chain_result.fraud_score for r in results) / len(results)
            avg_compliance = sum(
                r.chain_result.compliance_score for r in results
            ) / len(results)

            print(f"\nAverage Fraud Score: {avg_fraud:.3f}")
            print(f"Average Compliance Score: {avg_compliance:.3f}")

            # Show statistics
            stats = engine.get_stats()
            print(f"\nRule Engine Statistics:")
            print(f"  Bills Evaluated: {stats['bills_evaluated']}")
            print(f"  Rules Executed: {stats['rules_executed']}")
            print(f"  Errors: {stats['errors']}")

            if neo4j_session:
                await neo4j_session.close()
                await neo4j_driver.close()

    except Exception as e:
        logger.error(f"Batch validation error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Validate healthcare bills using rules engine"
    )
    parser.add_argument("--claim-id", type=str, help="Validate single bill by claim ID")
    parser.add_argument(
        "--batch", action="store_true", help="Batch validate bills from input file"
    )
    parser.add_argument(
        "--input", type=Path, help="Input file with claim_ids (JSON format)"
    )

    args = parser.parse_args()

    if args.claim_id:
        asyncio.run(validate_single_bill(args.claim_id))
    elif args.batch:
        if not args.input:
            logger.error("--input required for batch validation")
            sys.exit(1)
        asyncio.run(validate_batch(args.input))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
