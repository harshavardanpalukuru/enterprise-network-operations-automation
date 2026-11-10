# RHEL 9 Server Setup and Automation Environment

## 1. Host Identity

| Property | Value |
|---|---|
| Hostname | noc-rhel-01 |
| OS | Red Hat Enterprise Linux 9.8 |
| VM | NOC-RHEL-Server |
| CPU | 2 vCPUs |
| Memory | 2048 MB |
| Operator | nocadmin |

## 2. Project Environment

Project directory: `/home/nocadmin/enterprise-network-operations-automation`

Python virtual environment: `.venv`

Activate:

`source .venv/bin/activate`

## 3. Software Versions

| Component | Version |
|---|---|
| Python | 3.9.25 |
| pip | 21.3.1 |
| ansible-core | 2.15.13 |
| Netmiko | 4.6.0 |
| Paramiko | 4.0.0 |
| PyYAML | 6.0.3 |
| python-dotenv | 1.2.1 |
| ansible-pylibssh | 1.4.0 |

Ansible collections:

- cisco.ios 5.3.0

- ansible.netcommon 5.3.0

- ansible.utils 3.1.0

## 4. Python Automation

Three Python applications are implemented.

**Network health check**

`PYTHONPATH=automation/python .venv/bin/python -m noc_automation.health_check`

**Configuration backup**

`PYTHONPATH=automation/python .venv/bin/python -m noc_automation.config_backup`

**Configuration drift detection**

`PYTHONPATH=automation/python .venv/bin/python -m noc_automation.config_drift`

## 5. Ansible Compliance Audit

Execute:

bash automation/ansible/run-compliance

The read-only audit validates:

- Management SSH ACLs.

- VTY SSH restrictions.

- Switch VLAN and access-port assignments.

- 802.1Q trunks.

- Router interface ACL assignments.

- Expected static routes.

Recorded result: 4 devices compliant, 16 of 16 checks passed.

## 6. Unit Testing

Execute:

`PYTHONPATH=automation/python .venv/bin/python -m unittest discover -s automation/python/tests -v`

Recorded result: 10 tests passed.

## 7. Package Integrity

Execute:

`.venv/bin/python -m pip check`

Recorded result: No broken requirements found.

## 8. Operational Security

- Cisco credentials are stored in `.env`.

- `.env` is excluded from source publication.

- SSH host-key checking remains enabled.

- Sensitive files use permission 600.

- Protected directories use permission 700.

- Ansible compliance checks are read-only.

## 9. Project Output Directories

| Directory | Purpose |
|---|---|
| automation/python/noc_automation/ | Python applications |
| automation/ansible/ | Inventory and playbooks |
| configs/backups/ | Configuration backups |
| configs/baselines/ | Initial baselines |
| configs/drift/ | Drift differences |
| reports/ | JSON reports |
| logs/ | Execution logs |
| automation/python/tests/ | Unit tests |


