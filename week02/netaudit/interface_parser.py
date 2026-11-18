import json
from pathlib import Path
from ntc_templates.parse import parse_output, ParsingException


BASE_DIR = Path(__file__).resolve().parent.parent


def build_parse_results(router, parse_status, interfaces=None):
    return {
        "hostname": router["hostname"],
        "host": router["host"],
        "parse_status": parse_status,
        "interfaces": interfaces if interfaces is not None else []
    }


def parse_router_interfaces(results):
    parsed_routers = []

    cli_errors = [
        "% Invalid input detected",
        "% Incomplete command",
        "% Ambiguous command",
    ]

    for router in results:

        if router["status"] != "success":
            continue

        # Get saved CLI output from JSON
        commands = router["data"]["commands"]
        raw_output = commands.get("show ip interface brief")

        if raw_output is None:
            parseresult = "MISSING_COMMAND"
            parsed_routers.append(build_parse_results(router, parseresult))
            continue

        if not raw_output.strip():
            parseresult = "EMPTY_OUTPUT"
            parsed_routers.append(build_parse_results(router, parseresult))
            continue

        parseresult = "PARSED"

        for error in cli_errors:
            if error in raw_output:
                parseresult = "CLI_ERROR"
                break

        if parseresult != "PARSED":
            parsed_routers.append(build_parse_results(router, parseresult))
            continue
        
        # Parse the output into structured data
        try:
            interfaces = parse_output(
                platform="cisco_ios",
                command="show ip interface brief",
                data=raw_output
            )
        except ParsingException as e:
            parseresult = "PARSE_ERROR"
            parsed_routers.append(build_parse_results(router, parseresult))
            continue

        if not interfaces:
            parseresult = "PARSE_EMPTY"
            parsed_routers.append(build_parse_results(router, parseresult))
            continue

       
        # Store each router with its interfaces
        parsed_routers.append(build_parse_results(router, parseresult, interfaces))

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
        if router['parse_status'] != "PARSED":
            print(f"Parse Status: {router['parse_status']}")
            print("No parsed interfaces data available.")
        else:
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


