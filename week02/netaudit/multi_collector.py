import argparse
import json
from getpass import getpass
from pathlib import Path
from time import sleep
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
    ReadTimeout,
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
        "conn_timeout": 10,      
    }

def collect_all_routers(routers, username, password, commands, logger):
    results = []
    max_attempts = 3
    retry_delay = 2 #seconds


    for router in routers:
        device = build_connection(router, username, password)

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(
                    "Collection attempt | host=%s attempt=%d/%d",
                    router["host"],
                    attempt,
                    max_attempts
                )
                output = collect_router_data(device, commands, logger)
                results.append({
                    "hostname": router["hostname"],
                    "site": router["site"],
                    "host": router["host"],
                    "status": "success",
                    "attempt": attempt,
                    "data": output
                })
                break  # Exit the retry loop if successful
            except NetmikoAuthenticationException as e:
                logger.error(
                    "SSH connection failed | host=%s error=%s",
                    router["host"],
                    str(e)
                )
                results.append({
                    "hostname": router["hostname"],
                    "site": router["site"],
                    "host": router["host"],
                    "status": "failed",
                    "attempt": attempt,
                    "error": str(e),
                    "error_type": "authentication"
                })
                break  # No point in retrying authentication errors
            except NetmikoTimeoutException as e:
                logger.error(
                    "SSH connection timed out | host=%s error=%s",
                    router["host"],
                    str(e)
                )
                if attempt < max_attempts and "TCP connection to device failed" in str(e):
                    logger.info(
                        "Retrying SSH connection | host=%s attempt=%d",
                        router["host"],
                        attempt + 1
                    )
                    sleep(retry_delay)
                    continue
                else: 
                    results.append({
                        "hostname": router["hostname"],
                        "site": router["site"],
                        "host": router["host"],
                        "status": "failed",
                        "attempt": attempt,
                        "error": str(e),
                        "error_type": "connection_timeout"
                    })
                    break
            except ReadTimeout as e:
                logger.error(
                    "SSH read timeout | host=%s error=%s",
                    router["host"],
                    str(e)
                )
                if attempt < max_attempts:
                    logger.info(
                        "Retrying SSH read | host=%s attempt=%d",
                        router["host"],
                        attempt + 1
                    )
                    sleep(retry_delay)
                    continue
                else:
                    results.append({
                        "hostname": router["hostname"],
                        "site": router["site"],
                        "host": router["host"],
                        "status": "failed",
                        "attempt": attempt,
                        "error": str(e),
                        "error_type": "read_timeout"
                    })
                    break
              
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
        "show ip route summary",
    ]

    # Collect data from all routers
    results = collect_all_routers(routers, username, password, commands, logger)

    # Save results to a JSON file
    output_file = BASE_DIR / "output" / "router_data.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    logger.info("Data collection completed. Results saved to %s", output_file)

    print("Data collection completed. Results saved to", output_file)
    print("======= Summary ======")
    print(f"total routers: {len(results)}")
    print(f"successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"failed: {sum(1 for r in results if r['status'] == 'failed')}")
    print(f"retries: {sum(1 for r in results if r['attempt'] > 1)}")
    print("-----------------------")

if __name__ == "__main__":
    main()