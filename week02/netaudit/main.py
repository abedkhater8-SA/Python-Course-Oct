import json
from pathlib import Path
from .inventory import load_json_file
from .validators import (
    validate_router_ip,
    SiteSubnetConfigurationError
)
from .reports import export_json, export_csv
BASE_DIR = Path(__file__).resolve().parent.parent

def main():

    config_dir = BASE_DIR / "config"
    devices_file = config_dir / "devices.json"
    site_subnets_file = config_dir / "site_subnets.json"
    results = []
    try:

        devices = load_json_file(devices_file)
        site_subnets = load_json_file(site_subnets_file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Error loading configuration files: {error}")
        raise SystemExit(1)

    for router in devices:

        try:
            status = validate_router_ip(router, site_subnets) 
        except SiteSubnetConfigurationError as error:
            print(f"Error validating router {router['hostname']}: {error}")
            status = "CONFIG_ERROR"
        
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


if __name__ == "__main__":
    main()