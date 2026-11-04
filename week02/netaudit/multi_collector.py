import argparse
import json
from getpass import getpass
from pathlib import Path

from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from .inventory import load_json_file
from .logging_config import configure_logging
from .ssh_client import collect_router_data

BASE_DIR = Path(__file__).resolve().parent.parent

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Multi-router SSH collector"
    )

    parser.add_argument("--username", required=True)
    parser.add_argument("--verbose", action="store_true")

    return parser.parse_args()

def build_connection(router, username, password):
    return { 
        "device_type": "cisco_ios",
        "host": router["host"],
        "username": username,
        "password": password,
        "secret": password,       
    }

def collect_all_routers(routers, username, password, commands, logger):
    results = []

    for router in routers:
        device = build_connection(router, username, password)
        try:
            output = collect_router_data(device, commands, logger)
            results.append({
                "hostname": router["hostname"],
                "site": router["site"],
                "status": "success",
                "data": output
            })
            
        except (NetmikoAuthenticationException, NetmikoTimeoutException) as e:
            logger.error(
                "SSH connection failed | host=%s error=%s",
                router["host"],
                str(e)
            )
            results.append({
                "hostname": router["hostname"],
                "site": router["site"],
                "status": "failed",
                "error": str(e),
            })
        except Exception as e:
            logger.error(
                "Unexpected error | host=%s error=%s",
                router["host"],
                str(e)
            )   
            results.append({
                "hostname": router["hostname"],
                "site": router["site"],
                "status": "failed",
                "error": str(e),
            })
    return results

def main():
    args = parse_arguments()
    logger = configure_logging(BASE_DIR, verbose=args.verbose)

    # Load router inventory
    routers_file = BASE_DIR / "config" / "ssh_devices.json"
    routers = load_json_file(routers_file)

    # Prompt for SSH credentials
    username = args.username
    password = getpass("Enter SSH password: ")

    # Define commands to collect
    commands = [
        "show version",
        "show ip interface brief",
        "show run",
    ]

    # Collect data from all routers
    results = collect_all_routers(routers, username, password, commands, logger)

    # Save results to a JSON file
    output_file = BASE_DIR / "output" / "router_data.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    logger.info("Data collection completed. Results saved to %s", output_file)

if __name__ == "__main__":
    main()