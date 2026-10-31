import ipaddress
from pathlib import Path
import csv
import json


site_subnets = {
    "HQ": "10.10.10.0/24",
    "DR": "10.20.20.0/24",
    "Branch": "10.30.30.0/24"
}

devices = [
    {"hostname": "R1", "ip": "10.10.10.11", "site": "HQ"},
    {"hostname": "R2", "ip": "10.10.20.12", "site": "HQ"},
    {"hostname": "R3", "ip": "10.20.20.10", "site": "DR"},
    {"hostname": "R4", "ip": "10.30.30.5", "site": "Branch"},
    {"hostname": "R5", "ip": "10.20.20.999", "site": "DR"},
    {"hostname": "R6", "ip": "10.40.40.10", "site": "DC2"}
]


def validate_router_ip(router, site_subnets):
    
    if router["site"] not in site_subnets:
        return  "UNKNOWN_SITE"
    
    try:
        ip = ipaddress.ip_address(router["ip"])
    except ValueError:
        return "INVALID_IP"
    
    subnet = ipaddress.ip_network(site_subnets[router["site"]])
    if ip in subnet:
        return "VALID_IP"
    else:
        return "WRONG_SUBNET"

results = []

for router in devices:
    status = validate_router_ip(router, site_subnets)

    record = {
        "hostname": router["hostname"],
        "ip": router["ip"],
        "site": router["site"],
        "validation": status
    }

    results.append(record)

# Write results to a CSV file
report_dir = Path("reports")
report_dir.mkdir(exist_ok=True)
ip_validation_csv = report_dir / "ip_validation.csv"
ip_validation_jason = report_dir / "ip_validation.json"

with open(ip_validation_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["hostname", "ip", "site", "validation"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

# Write results to a JSON file
with open(ip_validation_jason, "w", encoding="utf-8") as jsonfile:
    json.dump(results, jsonfile, indent=4)

# Read results from the json file:
with open(ip_validation_jason, "r", encoding="utf-8") as jsonfile:
    loaded_results = json.load(jsonfile)

valid = 0 
failed = 0 
total_routers = len(loaded_results)

for router in loaded_results:

    if router["validation"] == "VALID_IP":
        valid += 1
    else:
        failed += 1

print("===Validation Summary===")
print(f"Total Routers: {total_routers}")
print(f"Valid IPs: {valid}")
print(f"Failed Validations: {failed}")


