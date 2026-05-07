"""Deterministic full SDK QA sweep entrypoint."""

from __future__ import annotations

from .env import QAConfig
from .invocation import build_invocation_plans
from .postman import load_postman_inventory
from .reporting import (
    write_failing_apis_report,
    write_missing_apis_report,
    write_not_testable_report,
    write_parameter_mismatches_report,
    write_sdk_modules_catalog,
)
from .runners import run_deterministic_sweep
from .sdk_inventory import build_sdk_inventory, compare_inventories
from .test_data import load_test_data


def main() -> None:
    config = QAConfig.from_env()
    scenarios = load_test_data()
    postman_entries = load_postman_inventory(write_catalog_copy=True)
    plans = build_invocation_plans(scenarios)
    sdk_records = build_sdk_inventory(plans, postman_entries, api_key=config.api_key)

    missing_in_sdk, missing_in_postman, mismatches = compare_inventories(
        sdk_records,
        postman_entries,
    )
    write_missing_apis_report(missing_in_sdk, missing_in_postman)
    write_parameter_mismatches_report(mismatches)

    results = run_deterministic_sweep(config, plans)
    write_failing_apis_report(results)
    write_not_testable_report(results)
    write_sdk_modules_catalog(sdk_records, results)

    success = sum(result.status == "success" for result in results)
    failure = sum(result.status == "failure" for result in results)
    not_testable = sum(result.status == "not-testable" for result in results)
    print(
        "Deterministic QA complete: "
        f"{success} success, {failure} failure, {not_testable} not-testable"
    )


if __name__ == "__main__":
    main()
