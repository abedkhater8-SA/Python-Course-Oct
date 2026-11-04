
"""Collect Cisco router information using Netmiko."""

import argparse
import json
from getpass import getpass
from pathlib import Path
from time import perf_counter

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from .logging_config import configure_logging


BASE_DIR = Path(__file__).resolve().parent.parent


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Cisco SSH Information Collector"
    )

    parser.add_argument(
        "--host",
        required=True,
        help="Cisco router management IP"
    )

    parser.add_argument(
        "--username",
        required=True,
        help="SSH username"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed terminal logging"
    )

    return parser.parse_args()


def collect_router_data(device, commands, logger):
    """Connect to a router and collect command outputs."""

    outputs = {}

    with ConnectHandler(**device) as connection:

        prompt = connection.find_prompt()

        logger.info(
            "SSH connected | host=%s prompt=%s",
            device["host"],
            prompt
        )

        for command in commands:

            logger.debug(
                "Executing command | host=%s command=%s",
                device["host"],
                command
            )

            output = connection.send_command(
                command,
                read_timeout=30
            )

            outputs[command] = output

            if "% Invalid input" in output:
                logger.warning(
                    "Unsupported command | host=%s command=%s",
                    device["host"],
                    command
                )

    logger.info(
        "SSH session closed | host=%s",
        device["host"]
    )

    return {
        "host": device["host"],
        "prompt": prompt,
        "commands": outputs
    }


def main():
    start_time = perf_counter()

    args = parse_arguments()
    logger = configure_logging(BASE_DIR, args.verbose)

    commands = [
        "show version",
        "show ip interface brief",
        "show ip route summary",
        "show ip ospf neighbor"
    ]

    device = {
        "device_type": "cisco_ios",
        "host": args.host,
        "username": args.username,
        "password": getpass("SSH password: "),
        "conn_timeout": 10,
    }

    logger.info(
        "Collection started | host=%s commands=%d",
        args.host,
        len(commands)
    )

    try:
        result = collect_router_data(
            device,
            commands,
            logger
        )

    except NetmikoAuthenticationException as error:
        logger.error(
            "SSH authentication failed | host=%s error=%s",
            args.host,
            error
        )
        raise SystemExit(1) from error

    except NetmikoTimeoutException as error:
        logger.error(
            "SSH connection failed | host=%s error=%s",
            args.host,
            error
        )
        raise SystemExit(1) from error

    # Export collected data to JSON
    try:
        report_dir = BASE_DIR / "reports" / "cli"
        report_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{args.host.replace('.', '_')}.json"
        report_file = report_dir / filename

        with report_file.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(result, file, indent=4)

    except OSError:
        logger.exception("Failed to export CLI report")
        raise SystemExit(1)

    # Display collection summary
    print("\n=== ROUTER COLLECTION SUMMARY ===")
    print(f"Router: {result['prompt']}")
    print(f"Management IP: {result['host']}")

    for command, output in result["commands"].items():
        print(
            f"{command}: {len(output)} characters collected"
        )

    print(f"\nReport saved: {report_file}")

    duration = perf_counter() - start_time

    logger.info(
        "Collection completed | host=%s commands=%d duration=%.2fs",
        args.host,
        len(commands),
        duration
    )


if __name__ == "__main__":
    main()
