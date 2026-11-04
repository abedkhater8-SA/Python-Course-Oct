
"""Run the network IP validation audit and generate reports."""

import argparse
import json
import os
from pathlib import Path
from time import perf_counter

from .inventory import load_json_file
from .logging_config import configure_logging
from .reports import export_csv, export_json
from .validators import (
    SiteSubnetConfigurationError,
    validate_router_ip,
)


BASE_DIR = Path(__file__).resolve().parent.parent


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Network IP Validation Tool"
    )

    parser.add_argument(
        "--site",
        default=os.getenv("NETAUDIT_SITE"),
        help="Select site to audit"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main():
    start_time = perf_counter()

    args = parse_arguments()
    logger = configure_logging(BASE_DIR, verbose=args.verbose)

    logger.info(
        "Audit started | site=%s",
        args.site or "ALL"
    )

    # Configuration paths
    config_dir = BASE_DIR / "config"
    devices_file = config_dir / "devices.json"
    site_subnets_file = config_dir / "site_subnets.json"

    results = []

    # Load inventory and site subnets
    try:
        devices = load_json_file(devices_file)
        site_subnets = load_json_file(site_subnets_file)

        logger.info(
            "Inventory loaded | devices=%d sites=%d",
            len(devices),
            len(site_subnets)
        )

    except (OSError, json.JSONDecodeError) as error:
        logger.error(
            "Error loading configuration files: %s",
            error
        )
        raise SystemExit(1) from error

    # Filter devices by site
    if args.site:
        devices = [
            router for router in devices
            if router["site"] == args.site
        ]

        if not devices:
            logger.error(
                "No devices found for site: %s",
                args.site
            )
            raise SystemExit(1)

    # Validate router IP addresses
    for router in devices:
        try:
            status = validate_router_ip(
                router,
                site_subnets
            )

        except SiteSubnetConfigurationError as error:
            logger.error(
                "Error validating router %s: %s",
                router["hostname"],
                error
            )
            status = "CONFIG_ERROR"

        # Log validation results
        if status == "VALID":
            logger.debug(
                "Router %s IP is valid",
                router["hostname"]
            )

        elif status != "CONFIG_ERROR":
            logger.warning(
                "Validation finding | hostname=%s "
                "ip=%s site=%s status=%s",
                router["hostname"],
                router["ip"],
                router["site"],
                status
            )

        # Build report record
        record = {
            "hostname": router["hostname"],
            "ip": router["ip"],
            "site": router["site"],
            "validation": status
        }

        results.append(record)

    # Export reports
    try:
        report_dir = BASE_DIR / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        export_json(
            results,
            report_dir / "ip_validation.json"
        )

        export_csv(
            results,
            report_dir / "ip_validation.csv"
        )

    except OSError as error:
        logger.exception(
            "Failed to export network audit reports"
        )
        raise SystemExit(1) from error

    # Display report summary
    print("\n=== NETWORK IP VALIDATION ===")

    for router in results:
        print(
            f"{router['hostname']}: "
            f"{router['validation']}"
        )

    # Execution summary
    duration = perf_counter() - start_time

    valid_count = sum(
        1 for router in results
        if router["validation"] == "VALID"
    )

    logger.info(
        "Audit completed | checked=%d valid=%d "
        "findings=%d duration=%.2fs",
        len(results),
        valid_count,
        len(results) - valid_count,
        duration
    )


if __name__ == "__main__":
    main()
