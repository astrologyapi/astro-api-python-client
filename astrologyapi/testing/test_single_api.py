"""Single-endpoint debug runner with stale-Postman fallback behavior."""

from __future__ import annotations

import argparse
import json

from .env import QAConfig
from .invocation import build_invocation_plans
from .postman import load_postman_inventory
from .runners import run_single_endpoint_debug
from .test_data import load_test_data

SDK_TARGET = "vedic.get_birth_details"
DIRECT_TARGET_LOOKUP = ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk-target", default=SDK_TARGET)
    parser.add_argument("--direct-target-lookup", default=DIRECT_TARGET_LOOKUP)
    args = parser.parse_args()

    config = QAConfig.from_env()
    scenarios = load_test_data()
    postman_entries = load_postman_inventory(write_catalog_copy=False)
    plans = build_invocation_plans(scenarios)

    result = run_single_endpoint_debug(
        config,
        plans,
        postman_entries,
        sdk_target=args.sdk_target,
        direct_target_lookup=args.direct_target_lookup or None,
    )

    print(
        json.dumps(
            {
                "status": result.status,
                "target": result.target,
                "endpoint": result.endpoint,
                "fallbackReason": result.fallback_reason,
                "sdkRequest": result.sdk_request.to_dict(),
                "directRequest": (
                    result.direct_request.to_dict()
                    if result.direct_request
                    else None
                ),
                "sdkResponse": result.sdk_response,
                "directResponse": result.direct_response,
                "diff": result.diff,
                "errorName": result.error_name,
                "errorMessage": result.error_message,
                "statusCode": result.status_code,
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
