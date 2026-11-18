import json
from pathlib import Path

from ntc_templates.parse import parse_output


BASE_DIR = Path(__file__).resolve().parent.parent


def parse_router_interfaces(results):
    parsed_routers = []

    for router in results:

        if router["status"] != "success":
            continue

        # Get saved CLI output from JSON
        raw_output = router["data"]["commands"]["show ip interface brief"]

        # Parse the output into structured data
        interfaces = parse_output(
            platform="cisco_ios",
            command="show ip interface brief",
            data=raw_output
        )

        # Store each router with its interfaces
        parsed_routers.append({
            "hostname": router["hostname"],
            "host": router["host"],
            "interfaces": interfaces
        })

    return parsed_routers


def main():
    report_file = BASE_DIR / "output" / "router_data.json"

    with report_file.open("r", encoding="utf-8") as file:
        results = json.load(file)

    parsed_routers = parse_router_interfaces(results)

    # YOUR CODE:
    # Print each router and its parsed interfaces

    for router in parsed_routers:
        print(f"Router: {router['hostname']}")
        print(f"Host: {router['host']}")
        for interface in router['interfaces']:
            print(
                f"  Interface: {interface['interface']} | "
                f"IP Address: {interface['ip_address']} | "
                f"Status: {interface['status']} | "
                f"Protocol: {interface['proto']}"
            )
    print(f"number of parsed interfaces: {len(router['interfaces'])}")

if __name__ == "__main__":
    main()