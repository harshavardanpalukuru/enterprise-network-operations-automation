#!/usr/bin/env python3
"""
Enterprise NOC - Python Network Health Monitor

Uses Netmiko directly to monitor Cisco IOS devices.
Does not depend on Ansible execution.
"""

import json
import logging
import os
import re
import sys
import time

from datetime import datetime, timezone
from pathlib import Path

import yaml

from dotenv import load_dotenv
from netmiko import ConnectHandler


# --------------------------------------------------
os.umask(0o077)


# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INVENTORY_FILE = PROJECT_ROOT / "automation/ansible/inventory/hosts.yml"
REPORT_DIR = PROJECT_ROOT / "reports"
LOG_DIR = PROJECT_ROOT / "logs"

REPORT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

LOG_FILE = LOG_DIR / "python_health.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# --------------------------------------------------
# ENVIRONMENT AND INVENTORY
# --------------------------------------------------

def load_credentials():
    """Load network credentials from the project .env file."""

    load_dotenv(PROJECT_ROOT / ".env")


    username = os.getenv("NOC_USERNAME")
    password = os.getenv("NOC_PASSWORD")

    if not username or not password:
        raise ValueError("NOC_USERNAME or NOC_PASSWORD is missing from .env")

    return username, password


def load_inventory():
    """Load Cisco devices from the existing YAML inventory."""

    if not INVENTORY_FILE.exists():
        raise FileNotFoundError(
            f"Inventory file not found: {INVENTORY_FILE}"
        )

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory = yaml.safe_load(file)

    hosts = (
        inventory.get("all", {})
        .get("children", {})
        .get("cisco", {})
        .get("hosts", {})
    )

    if not hosts:
        raise ValueError("No Cisco devices found in inventory.")

    devices = []

    for device_name, variables in hosts.items():
        host = variables.get("ansible_host")

        if not host:
            raise ValueError(
                f"Missing ansible_host for device {device_name}"
            )

        devices.append({
            "name": device_name,
            "host": str(host),
            "device_type": "cisco_ios",
        })

    return devices


# --------------------------------------------------
# INTERFACE OUTPUT PARSER
# --------------------------------------------------

def parse_interfaces(output):
    """Parse Cisco show ip interface brief output."""

    pattern = re.compile(
        r"^\s*(?P<interface>\S+)\s+"
        r"(?P<ip>\S+)\s+\S+\s+\S+\s+"
        r"(?P<status>administratively\s+down|up|down)\s+"
        r"(?P<protocol>up|down)\s*$",
        re.IGNORECASE,
    )

    interfaces = []

    for line in output.splitlines():
        match = pattern.match(line)

        if match:
            interfaces.append({
                "name": match.group("interface"),
                "ip_address": match.group("ip"),
                "status": match.group("status").lower(),
                "protocol": match.group("protocol").lower(),
            })

    return interfaces


def summarize_interfaces(interfaces):
    """Classify operational and administrative interface states."""

    return {
        "total": len(interfaces),
        "up_up": sum(
            1 for item in interfaces
            if item["status"] == "up"
            and item["protocol"] == "up"
        ),
        "down_down": sum(
            1 for item in interfaces
            if item["status"] == "down"
            and item["protocol"] == "down"
        ),
        "administratively_down": sum(
            1 for item in interfaces
            if item["status"] == "administratively down"
        ),
        "status_mismatch": sum(
            1 for item in interfaces
            if (
                item["status"] == "up"
                and item["protocol"] == "down"
            )
            or (
                item["status"] == "down"
                and item["protocol"] == "up"
            )
        ),
    }


# --------------------------------------------------
# DEVICE HEALTH CHECK
# --------------------------------------------------

def check_device(device, username, password):
    """Connect to one Cisco device and collect health information."""

    name = device["name"]
    host = device["host"]

    start_time = time.monotonic()
    connection = None

    result = {
        "device": name,
        "ip_address": host,
        "status": "FAIL",
        "privilege_level": None,
        "interface_summary": {},
        "interfaces": [],
        "duration_seconds": 0,
        "error": None,
    }

    try:
        logging.info("Starting health check: %s (%s)", name, host)

        connection = ConnectHandler(
            device_type=device["device_type"],
            host=host,
            username=username,
            password=password,
            ssh_strict=True,
            system_host_keys=True,
            conn_timeout=10,
            auth_timeout=15,
            banner_timeout=15,
            fast_cli=False,
        )

        # Check privilege level.
        privilege_output = connection.send_command(
            "show privilege",
            read_timeout=20,
        )

        privilege_match = re.search(
            r"Current privilege level is\s+(\d+)",
            privilege_output,
            re.IGNORECASE,
        )

        if privilege_match:
            result["privilege_level"] = int(
                privilege_match.group(1)
            )

        # Collect interface information.
        interface_output = connection.send_command(
            "show ip interface brief",
            read_timeout=30,
        )

        interfaces = parse_interfaces(interface_output)

        if not interfaces:
            raise RuntimeError(
                "Could not parse interface status output."
            )

        result["interfaces"] = interfaces
        result["interface_summary"] = summarize_interfaces(
            interfaces
        )

        if (
            result["privilege_level"] == 15
            and result["interface_summary"]["status_mismatch"] == 0
        ):
            result["status"] = "PASS"
        else:
            result["status"] = "WARNING"

        logging.info(
            "Completed health check: %s | %s",
            name,
            result["status"],
        )

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

        logging.error(
            "Health check failed: %s | %s",
            name,
            result["error"],
        )

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception as exc:
                logging.warning(
                    "Disconnect issue for %s: %s",
                    name,
                    exc,
                )

        result["duration_seconds"] = round(
            time.monotonic() - start_time,
            2,
        )

    return result


# --------------------------------------------------
# REPORT GENERATION
# --------------------------------------------------

def generate_report(results):
    """Save health-check results in JSON format."""

    timestamp = datetime.now(timezone.utc)

    report = {
        "report_type": "Python Network Health Check",
        "generated_at": timestamp.isoformat(),
        "summary": {
            "total_devices": len(results),
            "passed": sum(
                1 for item in results
                if item["status"] == "PASS"
            ),
            "warnings": sum(
                1 for item in results
                if item["status"] == "WARNING"
            ),
            "failed": sum(
                1 for item in results
                if item["status"] == "FAIL"
            ),
        },
        "devices": results,
    }

    filename = (
        "python_health_"
        + timestamp.strftime("%Y%m%d_%H%M%S")
        + ".json"
    )

    report_file = REPORT_DIR / filename

    with report_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    logging.info("Health report generated: %s", report_file)

    return report_file, report


# --------------------------------------------------
# CONSOLE SUMMARY
# --------------------------------------------------

def display_results(results, report_file, summary):
    """Display a readable health-check summary."""

    print("\n" + "=" * 65)
    print("       ENTERPRISE NOC - PYTHON NETWORK HEALTH MONITOR")
    print("=" * 65)

    for item in results:
        interface_summary = item["interface_summary"]

        print(
            f"\n{item['status']:<7} "
            f"{item['device']:<15} "
            f"{item['ip_address']}"
        )

        if interface_summary:
            print(
                f"        Interfaces: "
                f"{interface_summary['total']} total | "
                f"{interface_summary['up_up']} up/up | "
                f"{interface_summary['down_down']} down/down | "
                f"{interface_summary['administratively_down']} admin down | "
                f"{interface_summary['status_mismatch']} mismatch"
            )

        print(
            f"        Privilege: {item['privilege_level']}"
        )

        if item["error"]:
            print(f"        Error: {item['error']}")

    print("\n" + "-" * 65)
    print("TOTAL DEVICES :", summary["total_devices"])
    print("PASSED        :", summary["passed"])
    print("WARNINGS      :", summary["warnings"])
    print("FAILED        :", summary["failed"])
    print("-" * 65)

    print(f"JSON REPORT   : {report_file}")
    print(f"LOG FILE      : {LOG_FILE}")
    print("=" * 65 + "\n")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    try:
        username, password = load_credentials()
        devices = load_inventory()

        logging.info(
            "Starting Python health monitoring for %d devices",
            len(devices),
        )

        results = []

        for device in devices:
            results.append(
                check_device(device, username, password)
            )

        report_file, report = generate_report(results)

        display_results(
            results,
            report_file,
            report["summary"],
        )

        if (
            report["summary"]["failed"] > 0
            or report["summary"]["warnings"] > 0
        ):
            return 1

        return 0

    except Exception as exc:
        logging.exception("Health monitoring could not start.")
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

