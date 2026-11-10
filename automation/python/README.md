# Python Network Automation — Netmiko
## 1. Overview
The project uses Python and Netmiko to automate routine Cisco network operations from the RHEL 9 NOC server.
Three applications are implemented.
## 2. Network Health Check
File: `automation/python/noc_automation/health_check.py`
Functions:
- Connects to Cisco routers and switches through SSH.
- Checks administrative privilege level.
- Collects interface status using show ip interface brief.
- Classifies interface states.
- Generates JSON reports and execution logs.
Execution:
`PYTHONPATH=automation/python .venv/bin/python -m noc_automation.health_check`
## 3. Configuration Backup
File: `automation/python/noc_automation/config_backup.py`
Functions:
- Collects running configurations from Cisco devices.
- Verifies device privilege and hostname.
- Creates timestamped configuration backups.
- Generates a SHA-256 checksum manifest.
- Records execution results in logs.
Execution:
`PYTHONPATH=automation/python .venv/bin/python -m noc_automation.config_backup`
## 4. Configuration Drift Detection
File: `automation/python/noc_automation/config_drift.py`
Functions:
- Collects live running configurations.
- Validates initial baseline checksums.
- Compares running configurations against approved baselines.
- Ignores header lines that IOS regenerates on every save or restart (byte count, last-change timestamps), so they are not reported as drift. Baseline checksums are still calculated on the raw text.
- Identifies configuration differences.
- Generates unified diff files and JSON reports.
Execution:
`PYTHONPATH=automation/python .venv/bin/python -m noc_automation.config_drift`
## 5. Device Inventory
The automation covers four Cisco devices.
| Device | Management IP |
|---|---|
| R1-HQ | 10.10.99.1 |
| SW1-HQ | 10.10.99.2 |
| R2-Branch | 10.20.99.1 |
| SW2-Branch | 10.20.99.2 |
## 6. Testing
The Python test suite contains ten unit tests.
Execution:
`PYTHONPATH=automation/python .venv/bin/python -m unittest discover -s automation/python/tests -v`
Recorded result: ten tests passed.
## 7. Security
- Credentials are loaded from environment variables.
- The .env file is excluded from source publication.
- SSH host-key checking remains enabled.
- Generated reports and backups use restricted permissions.
- Configuration backups include SHA-256 integrity verification.
## 8. Validation Results
Recorded operational results:
| Application | Result |
|---|---|
| Health check | 4 devices passed |
| Configuration backup | 4 devices backed up |
| Backup integrity | 4 checksums verified |
| Drift detection | 4 devices CLEAN |
| Unit tests | 10 passed |
## 9. Output Directories
| Directory | Purpose |
|---|---|
| configs/backups/ | Timestamped configuration backups |
| configs/baselines/ | Initial configuration baselines |
| configs/drift/ | Configuration differences |
| reports/ | JSON execution reports |
| logs/ | Application logs |
| automation/python/tests/ | Unit tests (source, not generated output) |
