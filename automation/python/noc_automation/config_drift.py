#!/usr/bin/env python3
"""Enterprise NOC - Python Configuration Drift Detection."""

import difflib
import hashlib
import json
import logging
import os
import re
import sys

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
BASELINE_DIR = PROJECT_ROOT / "configs/baselines/initial"
DRIFT_DIR = PROJECT_ROOT / "configs/drift"
REPORT_DIR = PROJECT_ROOT / "reports"
LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "python_drift.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# --------------------------------------------------
# CREDENTIALS AND INVENTORY
# --------------------------------------------------

def load_credentials():
    """Load SSH credentials from the project .env file."""

    load_dotenv(PROJECT_ROOT / ".env")

    username = os.getenv("NOC_USERNAME")
    password = os.getenv("NOC_PASSWORD")

    if not username or not password:
        raise ValueError("NOC_USERNAME or NOC_PASSWORD is missing.")

    return username, password


def load_inventory():
    """Load Cisco devices from the shared Ansible inventory."""

    with INVENTORY_FILE.open(encoding="utf-8") as file:
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

    for name, variables in hosts.items():
        address = variables.get("ansible_host")

        if not address:
            raise ValueError(f"Missing management IP for {name}.")

        devices.append({
            "name": name,
            "host": str(address),
            "device_type": "cisco_ios",
        })

    return devices


# --------------------------------------------------
# BASELINE VALIDATION
# --------------------------------------------------

def calculate_sha256(content):
    """Calculate SHA-256 checksum."""

    return hashlib.sha256(content).hexdigest()


def normalize_config(config):
    """Normalize line endings without changing configuration content."""

    config = config.replace("\r\n", "\n").replace("\r", "\n")
    return config.rstrip("\n") + "\n"


def load_baseline_manifest():
    """Load and validate the approved baseline manifest."""

    manifest_file = BASELINE_DIR / "baseline_manifest.json"

    if not manifest_file.exists():
        raise FileNotFoundError("Initial baseline manifest not found.")

    manifest = json.loads(
        manifest_file.read_text(encoding="utf-8")
    )

    records = {
        item["device"]: item
        for item in manifest.get("devices", [])
    }

    if not records:
        raise ValueError("Baseline contains no device records.")

    return records


def read_verified_baseline(device_name, records):
    """Read a baseline only after verifying its checksum."""

    if device_name not in records:
        raise ValueError(
            f"No baseline record exists for {device_name}."
        )

    record = records[device_name]
    filename = record.get("filename", "")

    if Path(filename).name != filename:
        raise ValueError("Invalid baseline filename.")

    baseline_file = BASELINE_DIR / filename

    if not baseline_file.is_file():
        raise FileNotFoundError(
            f"Baseline file missing for {device_name}."
        )

    content = normalize_config(
        baseline_file.read_text(encoding="utf-8")
    )

    actual_hash = calculate_sha256(content.encode("utf-8"))

    if actual_hash != record.get("sha256"):
        raise ValueError(
            f"Baseline checksum verification failed for {device_name}."
        )

    return content, actual_hash


# --------------------------------------------------
# LIVE CONFIGURATION COLLECTION
# --------------------------------------------------

def collect_running_config(device, username, password):
    """Collect running configuration from a Cisco IOS device."""

    connection = None

    try:
        connection = ConnectHandler(
            device_type=device["device_type"],
            host=device["host"],
            username=username,
            password=password,
            ssh_strict=True,
            system_host_keys=True,
            conn_timeout=10,
            auth_timeout=15,
            banner_timeout=15,
            fast_cli=False,
        )

        privilege = connection.send_command(
            "show privilege",
            read_timeout=20,
        )

        match = re.search(
            r"Current privilege level is\s+(\d+)",
            privilege,
            re.IGNORECASE,
        )

        if not match or int(match.group(1)) != 15:
            raise RuntimeError("Device is not at privilege level 15.")

        config = connection.send_command(
            "show running-config",
            read_timeout=90,
        )

        if not config.strip():
            raise RuntimeError("Running configuration is empty.")

        hostname_match = re.search(
            r"(?mi)^\s*hostname\s+(\S+)\s*$",
            config,
        )

        if not hostname_match:
            raise RuntimeError("Hostname missing from running configuration.")

        if hostname_match.group(1) != device["name"]:
            raise RuntimeError("Device hostname does not match inventory.")

        return normalize_config(config)

    finally:
        if connection is not None:
            connection.disconnect()


# --------------------------------------------------
# DRIFT COMPARISON
# --------------------------------------------------

VOLATILE_LINE_PATTERNS = (
    re.compile(r"^Building configuration\.\.\.$"),
    re.compile(r"^Current configuration : \d+ bytes$"),
    re.compile(r"^! Last configuration change at .*$"),
    re.compile(r"^! NVRAM config last updated at .*$"),
    re.compile(r"^! No configuration change since last restart$"),
)


def strip_volatile_lines(config):
    """Remove header lines that IOS regenerates on every save or restart.

    These lines (byte count, last-change timestamps) change without any
    configuration change, so comparing them reports false drift. Consecutive
    bare "!" separators left behind are collapsed into one. This is used only
    for comparison; baseline checksums are still calculated on the raw text.
    """

    kept = []

    for line in config.splitlines():
        if any(pattern.match(line) for pattern in VOLATILE_LINE_PATTERNS):
            continue

        if line == "!" and kept and kept[-1] == "!":
            continue

        kept.append(line)

    return "\n".join(kept) + "\n"


def compare_configurations(baseline, current, device_name):
    """Compare two configurations without requiring a network connection."""

    baseline = strip_volatile_lines(normalize_config(baseline))
    current = strip_volatile_lines(normalize_config(current))

    if baseline == current:
        return {
            "status": "CLEAN",
            "diff": "",
        }

    differences = difflib.unified_diff(
        baseline.splitlines(keepends=True),
        current.splitlines(keepends=True),
        fromfile=f"{device_name}.baseline",
        tofile=f"{device_name}.current",
    )

    return {
        "status": "DRIFT_DETECTED",
        "diff": "".join(differences),
    }


def check_device_drift(device, username, password, records, timestamp):
    """Compare one live configuration against its baseline."""

    name = device["name"]

    result = {
        "device": name,
        "management_ip": device["host"],
        "status": "FAILED",
        "baseline_sha256": None,
        "current_sha256": None,
        "diff_file": None,
        "error": None,
    }

    try:
        baseline, baseline_hash = read_verified_baseline(
            name,
            records,
        )

        logging.info("Checking configuration drift: %s", name)

        current = collect_running_config(
            device,
            username,
            password,
        )

        current_hash = calculate_sha256(
            current.encode("utf-8")
        )

        result["baseline_sha256"] = baseline_hash
        result["current_sha256"] = current_hash

        comparison = compare_configurations(
            baseline,
            current,
            name,
        )

        if comparison["status"] == "CLEAN":
            result["status"] = "CLEAN"
            logging.info("No configuration drift: %s", name)

        else:
            diff_content = comparison["diff"]

            DRIFT_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
            DRIFT_DIR.chmod(0o700)

            diff_file = DRIFT_DIR / f"{name}_{timestamp}.diff"

            diff_file.write_text(
                diff_content,
                encoding="utf-8",
            )

            diff_file.chmod(0o600)

            result["status"] = "DRIFT_DETECTED"
            result["diff_file"] = str(
                diff_file.relative_to(PROJECT_ROOT)
            )

            logging.warning("Configuration drift detected: %s", name)

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

        logging.error(
            "Drift check failed: %s | %s",
            name,
            result["error"],
        )

    return result


# --------------------------------------------------
# JSON REPORT
# --------------------------------------------------

def generate_report(results, timestamp):
    """Generate a consolidated JSON drift report."""

    summary = {
        "total_devices": len(results),
        "clean": sum(
            item["status"] == "CLEAN" for item in results
        ),
        "drift_detected": sum(
            item["status"] == "DRIFT_DETECTED" for item in results
        ),
        "failed": sum(
            item["status"] == "FAILED" for item in results
        ),
    }

    report = {
        "report_type": "Python Configuration Drift Detection",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "devices": results,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report_file = REPORT_DIR / f"python_drift_{timestamp}.json"

    report_file.write_text(
        json.dumps(report, indent=4) + "\n",
        encoding="utf-8",
    )

    report_file.chmod(0o600)

    return report_file, summary


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    try:
        os.umask(0o077)

        username, password = load_credentials()
        devices = load_inventory()
        baselines = load_baseline_manifest()

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )

        results = []

        print("\nENTERPRISE NOC - CONFIGURATION DRIFT DETECTION")
        print("=" * 60)

        for device in devices:
            print(f"\nChecking {device['name']} ({device['host']})...")

            result = check_device_drift(
                device,
                username,
                password,
                baselines,
                timestamp,
            )

            results.append(result)

            print("Status:", result["status"])

            if result["diff_file"]:
                print("Difference file:", result["diff_file"])

            if result["error"]:
                print("Error:", result["error"])

        report_file, summary = generate_report(
            results,
            timestamp,
        )

        print("\n" + "=" * 60)
        print("DRIFT DETECTION SUMMARY")
        print("=" * 60)
        print("Total devices  :", summary["total_devices"])
        print("Clean          :", summary["clean"])
        print("Drift detected :", summary["drift_detected"])
        print("Failed         :", summary["failed"])
        print("JSON report    :", report_file)
        print("Log file       :", LOG_DIR / "python_drift.log")
        print("=" * 60)

        if summary["failed"] or summary["drift_detected"]:
            return 1

        return 0

    except Exception as exc:
        logging.exception("Drift detection could not start.")
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
