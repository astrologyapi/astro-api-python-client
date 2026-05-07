"""Randomized SDK-vs-direct comparison entrypoint."""

from __future__ import annotations

import argparse

from .env import QAConfig
from .invocation import build_invocation_plans
from .postman import load_postman_inventory
from .reporting import split_compare_results, write_inconsistent_responses_report
from .runners import run_randomized_compare
from .test_data import load_test_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    config = QAConfig.from_env()
    scenarios = load_test_data()
    postman_entries = load_postman_inventory(write_catalog_copy=False)
    plans = build_invocation_plans(scenarios)
    results = run_randomized_compare(
        config,
        plans,
        postman_entries,
        sample_size=args.sample_size,
        seed=args.seed,
    )
    write_inconsistent_responses_report(results)

    success = sum(result.status == "success" for result in results)
    mismatches, execution_failures = split_compare_results(results)
    not_testable = sum(result.status == "not-testable" for result in results)
    print(
        "Comparison QA complete: "
        f"{success} success, {len(mismatches)} response-mismatch, "
        f"{len(execution_failures)} compare-failure, "
        f"{not_testable} not-testable"
    )
    if execution_failures:
        sample_targets = ", ".join(
            result.target
            for result in execution_failures[:100]
        )
        suffix = " ..." if len(execution_failures) > 100 else ""
        print(
            "Compare failures are excluded from "
            "`testing/results/inconsistent-responses.md` because no "
            "comparable payload pair was produced."
        )
        print(f"Compare failure targets: {sample_targets}{suffix}")


if __name__ == "__main__":
    main()
