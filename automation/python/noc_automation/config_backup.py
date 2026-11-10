#!/usr/bin/env python3
"""
Enterprise NOC - Python Configuration Backup

Collects Cisco IOS running configurations using Netmiko.
"""

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
BACKUP_ROOT = PROJECT_ROOT / "configs/backups"
LOG_DIR = PROJECT_ROOT / "logs"


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "python_backup.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# --------------------------------------------------
# CREDENTIALS
# --------------------------------------------------

def load_credentials():
    """Load credentials from the project environment file."""

    load_dotenv(PROJECT_ROOT / ".env")

    username = os.getenv("NOC_USERNAME")
    password = os.getenv("NOC_PASSWORD")

    if not username or not password:
        raise ValueError("NOC_USERNAME or NOC_PASSWORD is missing.")

    return username, password


# --------------------------------------------------
# INVENTORY
# --------------------------------------------------

def load_inventory():
    """Load Cisco devices from the existing Ansible inventory."""

    if not INVENTORY_FILE.exists():
        raise FileNotFoundError(f"Inventory not found: {INVENTORY_FILE}")

    with INVENTORY_FILE.open(encoding="utf-8") as file:
        inventory = yaml.safe_load(file)

    devices = (
        inventory.get("all", {})
        .get("children", {})
        .get("cisco", {})
        .get("hosts", {})
    )

    if not devices:
        raise ValueError("No Cisco devices found in inventory.")

    result = []

    for name, variables in devices.items():
        address = variables.get("ansible_host")

        if not address:
            raise ValueError(f"Missing management IP for {name}.")

        result.append({
            "name": name,
            "host": str(address),
            "device_type": "cisco_ios",
        })

    return result


# --------------------------------------------------
# CONFIGURATION COLLECTION
# --------------------------------------------------

def backup_device(device, username, password, backup_dir):
    """Connect to a Cisco device and save its running configuration."""

    name = device["name"]
    connection = None

    result = {
        "device": name,
        "management_ip": device["host"],
        "status": "FAILED",
        "backup_file": None,
        "sha256": None,
        "size_bytes": 0,
        "error": None,
    }

    try:
        logging.info("Starting backup: %s", name)

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

        # Verify privilege level.
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

        # Collect the running configuration.
        config = connection.send_command(
            "show running-config",
            read_timeout=90,
        )

        if not config.strip():
            raise RuntimeError("Running configuration is empty.")

        # Verify that the configuration belongs to the expected device.
        hostname_match = re.search(
            r"(?mi)^\s*hostname\s+(\S+)\s*$",
            config,
        )

        if not hostname_match:
            raise RuntimeError("Hostname not found in configuration.")

        actual_hostname = hostname_match.group(1)

        if actual_hostname != name:
            raise RuntimeError(
                f"Hostname mismatch: expected {name}, "
                f"received {actual_hostname}."
            )

        # Save the configuration with owner-only permissions.
        backup_file = backup_dir / f"{name}.cfg"

        temporary_file = backup_dir / f"{name}.cfg.tmp"

        temporary_file.write_text(
            config.rstrip() + "\n",
            encoding="utf-8",
        )

        temporary_file.chmod(0o600)
        temporary_file.replace(backup_file)

        backup_file.chmod(0o600)

        # Calculate SHA-256 checksum.
        content = backup_file.read_bytes()
        checksum = hashlib.sha256(content).hexdigest()

        result.update({
            "status": "SUCCESS",
            "backup_file": str(backup_file.relative_to(PROJECT_ROOT)),
            "sha256": checksum,
            "size_bytes": len(content),
        })

        logging.info(
            "Backup successful: %s | SHA256: %s",
            name,
            checksum,
        )

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

        logging.error(
            "Backup failed: %s | %s",
            name,
            result["error"],
        )

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception:
                logging.warning("Disconnect issue: %s", name)

    return result


# --------------------------------------------------
# BACKUP MANIFEST
# --------------------------------------------------

def generate_manifest(results, backup_dir, timestamp):
    """Generate a JSON record of the backup operation."""

    successful = sum(
        1 for item in results
        if item["status"] == "SUCCESS"
    )

    manifest = {
        "report_type": "Python Cisco Configuration Backup",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backup_timestamp": timestamp,
        "summary": {
            "total_devices": len(results),
            "successful": successful,
            "failed": len(results) - successful,
        },
        "devices": results,
    }

    manifest_file = backup_dir / "backup_manifest.json"

    manifest_file.write_text(
        json.dumps(manifest, indent=4) + "\n",
        encoding="utf-8",
    )

    manifest_file.chmod(0o600)

    return manifest_file, manifest


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    try:
        # Restrict permissions for newly created files.
        os.umask(0o077)

        username, password = load_credentials()
        devices = load_inventory()

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )

        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        BACKUP_ROOT.chmod(0o700)

        backup_dir = BACKUP_ROOT / timestamp
        backup_dir.mkdir(mode=0o700)
        backup_dir.chmod(0o700)

        results = []

        print("\nENTERPRISE NOC - CONFIGURATION BACKUP")
        print("=" * 55)

        for device in devices:
            print(
                f"\nBacking up {device['name']} "
                f"({device['host']})..."
            )

            result = backup_device(
                device,
                username,
                password,
                backup_dir,
            )

            results.append(result)

            print(f"Status: {result['status']}")

            if result["status"] == "SUCCESS":
                print(f"File: {result['backup_file']}")
                print(f"Size: {result['size_bytes']} bytes")
                print(f"SHA256: {result['sha256']}")
            else:
                print(f"Error: {result['error']}")

        manifest_file, manifest = generate_manifest(
            results,
            backup_dir,
            timestamp,
        )

        summary = manifest["summary"]

        print("\n" + "=" * 55)
        print("BACKUP SUMMARY")
        print("=" * 55)
        print("Total devices :", summary["total_devices"])
        print("Successful    :", summary["successful"])
        print("Failed        :", summary["failed"])
        print("Backup folder :", backup_dir)
        print("Manifest      :", manifest_file)
        print("Log file      :", LOG_FILE)
        print("=" * 55)

        return 1 if summary["failed"] else 0

    except Exception as exc:
        logging.exception("Configuration backup could not start.")
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
