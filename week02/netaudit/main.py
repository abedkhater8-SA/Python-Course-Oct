import json
import argparse
from pathlib import Path
from .inventory import load_json_file
from .validators import (
    validate_router_ip,
    SiteSubnetConfigurationError
)
from .reports import export_json, export_csv
from .logging_config import configure_logging
from time import perf_counter
BASE_DIR = Path(__file__).resolve().parent.parent
def parse_arguments():
    parser = argparse.ArgumentParser(description="Network IP Validation Tool")
    parser.add_argument("--site", type=str, help="Select Site to Edit")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def main():
    start_time = perf_counter()
    args = parse_arguments()
    logger = configure_logging(BASE_DIR, verbose=args.verbose)
    logger.info("Audit started | site: %s | verbose: %s", args.site, args.verbose)

    config_dir = BASE_DIR / "config"
    devices_file = config_dir / "devices.json"
    site_subnets_file = config_dir / "site_subnets.json"
    results = []
    try:

        devices = load_json_file(devices_file)
        site_subnets = load_json_file(site_subnets_file)
        logger.info("Loaded configuration files successfully")
    except (OSError, json.JSONDecodeError) as error:
        logger.error("Error loading configuration files: %s", error)
        raise SystemExit(1)
    if args.site:
        devices = [router for router in devices if router["site"] == args.site]
        if not devices:
            logger.error("No devices found for site: %s", args.site)
            raise SystemExit(1)

    for router in devices:

        try:
            status = validate_router_ip(router, site_subnets) 
        except SiteSubnetConfigurationError as error:
            logger.error("Error validating router %s: %s", router['hostname'], error)
            status = "CONFIG_ERROR"

        if status == "VALID":
            logger.debug("Router %s IP is valid", router['hostname'])
        elif status == "CONFIG_ERROR":
            logger.error("Router %s has configuration error", router['hostname'])
        else:
            logger.warning("Validation findings | hostname: %s | ip: %s | site: %s | status: %s", router['hostname'], router['ip'], router['site'], status)
        
        
        record = {
                "hostname": router["hostname"],
                "ip": router["ip"],
                "site": router["site"],
                "validation": status
            }

        results.append(record)

    report_dir = BASE_DIR / "reports"
    report_dir.mkdir(exist_ok=True)

    export_json(results, report_dir / "ip_validation.json")
    export_csv(results, report_dir / "ip_validation.csv")

    for router in results:
        print(f"{router['hostname']}: {router['validation']}")
    duration = perf_counter() - start_time

    logger.info(
        "Audit completed | devices=%d duration=%.2fs",
        len(results),
        duration)
    


if __name__ == "__main__":
    main()