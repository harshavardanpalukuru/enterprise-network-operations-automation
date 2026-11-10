# Enterprise Network Operations & Automation Lab

A two-site enterprise network lab built with **GNS3, Cisco IOS, and RHEL 9**, with **Python/Netmiko** and **Ansible** automating day-to-day network operations. The project brings together network segmentation, secure device management, configuration backups, drift detection, compliance checks, and packet-level validation.

## Table of Contents

- [Overview](#overview)
- [Network topology](#network-topology)
- [Key features](#key-features)
- [Validation results](#validation-results)
- [Packet analysis and evidence](#packet-analysis-and-evidence)
- [Repository structure](#repository-structure)
- [Getting started](#getting-started)
- [Technology stack](#technology-stack)
- [Documentation](#documentation)
- [Author and license](#author-and-license)

## Overview

A fictional organization operates a head office (HQ) and a branch office. HR and Finance teams work at HQ, Operations works at the branch, and a Network Operations Center (NOC) manages the infrastructure. This lab models the network, applies access controls between departments, and uses a RHEL 9 server to automate device checks and configuration-management tasks.

### At a glance

- **Network:** HQ and Branch connected over a point-to-point WAN link.
- **Routing and switching:** VLANs, 802.1Q trunks, router-on-a-stick inter-VLAN routing, and static routing.
- **Security:** Extended ACLs, SSHv2-only device management, management-source restrictions, and switch port security.
- **Automation:** Python/Netmiko health checks, configuration backups, and configuration drift detection.
- **Compliance:** Ansible read-only audit across four Cisco devices.
- **Validation:** Connectivity tests, ACL counters, Wireshark/TShark captures, and Python unit tests.

## Network topology

![Logical network topology showing the HQ, Branch, VLANs, WAN link, and RHEL NOC server](topology/network-topology.png)

The lab contains two sites connected through a `/30` point-to-point WAN link. The RHEL 9 NOC server is connected to the HQ management VLAN and provides the administration and automation environment.

The original GNS3 layout is available in [`topology/gns3-topology.png`](topology/gns3-topology.png), and physical/logical links are documented in [`topology/device-connections.md`](topology/device-connections.md).

### Network addressing

| Site | VLAN | Purpose | Network | Default gateway |
|---|---:|---|---|---|
| HQ | 10 | HR | `10.10.10.0/24` | `10.10.10.1` |
| HQ | 20 | Finance | `10.10.20.0/24` | `10.10.20.1` |
| HQ | 99 | Management | `10.10.99.0/24` | `10.10.99.1` |
| Branch | 30 | Operations | `10.20.30.0/24` | `10.20.30.1` |
| Branch | 99 | Management | `10.20.99.0/24` | `10.20.99.1` |
| WAN | — | Router transit | `172.16.12.0/30` | R1-HQ: `172.16.12.1`; R2-Branch: `172.16.12.2` |

### Design choices

- **Static routing:** Used for the two-router, single-path WAN topology; a dynamic routing protocol would add complexity without a practical benefit in this lab.
- **Router-on-a-stick:** Each site's router provides inter-VLAN routing through 802.1Q subinterfaces.
- **Dedicated management VLANs:** Network-device management is separated from user VLANs.
- **Inbound extended ACLs:** User traffic is filtered as it enters the router from each user VLAN.

See [`docs/02-network-architecture.md`](docs/02-network-architecture.md) and [`docs/03-ip-addressing-plan.md`](docs/03-ip-addressing-plan.md) for the detailed design.

## Key features

### Network security

- Departmental VLAN segmentation at HQ and the Branch.
- Extended ACLs controlling traffic between user and management networks.
- SSHv2-only administration with VTY access restricted to the NOC host.
- Switch port security using sticky MAC learning and `violation restrict` on designated access ports.

### Python network automation

Three Python applications run from the RHEL 9 NOC server:

| Application | What it does | Output |
|---|---|---|
| `health_check.py` | Connects to devices over SSH, checks privilege level, collects interface status, and classifies interface states. | JSON report and log |
| `config_backup.py` | Retrieves running configurations, verifies device identity and privilege, and creates timestamped backups with SHA-256 checksums. | Configuration files, checksum manifest, and log |
| `config_drift.py` | Validates baseline checksums and compares live configurations against approved baselines. | Unified diffs, JSON report, and log |

Implementation details are in [`automation/python/README.md`](automation/python/README.md).

### Ansible compliance audit

An Ansible playbook performs read-only checks across four Cisco devices, including:

- SSH and VTY management settings.
- Management access restrictions.
- VLAN and access-port assignments.
- Trunk configuration and allowed VLANs.
- Router interface ACL assignments and static routes.

The playbook does not push configuration changes. It generates a timestamped JSON report. See [`automation/ansible/README.md`](automation/ansible/README.md).

## Validation results

The following results were recorded during testing in the simulated lab:

| Test | Result |
|---|---:|
| Python device health check | 4/4 devices passed |
| Configuration backups | 4/4 successful |
| SHA-256 backup verification | 4/4 verified |
| Configuration drift detection | 4/4 reported `CLEAN` against the supplied baselines |
| Ansible compliance audit | 16/16 checks passed across 4 devices |
| Python unit tests | 10 passed |
| NOC-to-router SSH | Successful; privilege level 15 confirmed |

### Network policy verification

The validation matrix records the following tested traffic behavior:

| Source | Destination | Expected behavior | Recorded result |
|---|---|---|---|
| HQ HR | HQ Finance | Denied | 5 packets denied |
| HQ Finance | HQ HR | Denied | 5 packets denied |
| Branch Operations | Branch Management | Denied | 5 packets denied |
| Branch Operations | HQ Management | Denied | 5 packets denied |
| HQ HR | Branch Operations | Permitted | 5/5 successful |
| Branch Operations | HQ HR | Permitted | 5/5 successful |
| Branch Operations | HQ Finance | Permitted by policy | 5/5 successful |

Denied ICMP traffic returned an administratively prohibited response (ICMP type 3, code 13), and the corresponding ACL counters increased. The port-security test on `SW1-HQ` `Gi0/2` blocked an unknown endpoint, recorded a violation, and kept the port up. Other configured ports were not individually tested.

Full procedures and results are documented in [`testing/validation-matrix.md`](testing/validation-matrix.md).

## Packet analysis and evidence

Seven filtered PCAPNG files are included in [`packet-analysis/captures/`](packet-analysis/captures/): six ICMP captures covering WAN, permitted, and denied traffic, plus one SSH session between the NOC host and R1-HQ. Capture details and interpretation notes are in [`packet-analysis/README.md`](packet-analysis/README.md).

Selected screenshots from the lab:

<details>
<summary>Device health check — 4/4 devices passed</summary>

![Health check showing four devices passed](evidence/01-health-check.png)

</details>

<details>
<summary>Configuration backup — 4/4 successful</summary>

![Configuration backup output](evidence/02-config-backup.png)

</details>

<details>
<summary>Configuration drift — 4/4 clean</summary>

![Drift detection output](evidence/03-drift-detection.png)

</details>

<details>
<summary>Ansible compliance audit — 16/16 checks passed</summary>

![Ansible compliance audit output](evidence/04-ansible-compliance.png)

</details>

<details>
<summary>ACL denial verified in Wireshark</summary>

![Wireshark capture of an ACL denial](evidence/05-acl-denial-wireshark.png)

</details>

## Repository structure

```text
enterprise-network-operations-automation/
├── docs/                    Business requirements, architecture, and IP addressing
├── topology/                Network diagram, GNS3 project, and device connections
├── network-configs/         Reference router and switch configurations
├── linux/                   RHEL 9 NOC server documentation
├── automation/
│   ├── python/              Netmiko applications and unit tests
│   └── ansible/             Inventory, compliance playbook, and runner
├── testing/                 Network validation matrix
├── evidence/                Screenshots of automation and packet tests
├── packet-analysis/         Capture documentation and filtered PCAPNG files
├── .env.example             Environment-variable template
├── requirements.txt         Python dependencies
└── README.md
```

## Getting started

### Prerequisites

- RHEL 9 with Python 3.9.
- GNS3 and a compatible GNS3 VM or local installation.
- Your own licensed Cisco IOSv and IOSvL2 images; device images are not included.
- A RHEL 9 NOC VM connected to the lab management network.
- SSH connectivity from the NOC host to the four Cisco devices.

The recorded environment used Ansible Core `2.15.13`, the `cisco.ios` collection `5.3.0`, Netmiko `4.6.0`, and Paramiko `4.0.0`.

### 1. Clone the repository

```bash
git clone https://github.com/harshavardanpalukuru/enterprise-network-operations-automation.git
cd enterprise-network-operations-automation
```

### 2. Prepare the GNS3 lab

1. Open [`topology/enterprise-noc-automation-lab.gns3`](topology/enterprise-noc-automation-lab.gns3) in GNS3.
2. Map the Cisco nodes to your locally installed IOSv and IOSvL2 images.
3. Recreate or remap the RHEL 9 NOC VM. The project file contains a VM path from the author's workstation, so it must be updated on another machine.
4. Check the links against [`topology/device-connections.md`](topology/device-connections.md).
5. Apply or verify the device configurations and confirm management reachability from the NOC host.

### 3. Install dependencies

Run from the repository root on the RHEL 9 NOC server:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r automation/ansible/requirements.yml
```

### 4. Configure credentials and inventory

```bash
cp .env.example .env
chmod 600 .env
```

Add your lab credentials to `.env`, then review `automation/ansible/inventory/hosts.yml` and confirm the device management addresses. Ensure the devices' SSH host keys are trusted; SSH host-key checking is enabled. Do not commit `.env` or real credentials.

### 5. Prepare drift-detection baselines

Before running `config_drift.py`, provide approved device baseline configurations and a `baseline_manifest.json` in `configs/baselines/initial/`. These runtime baselines are not included in the repository. The files in `network-configs/` are published reference configurations; they are separate from the runtime baseline directory used by the drift-detection tool.

### 6. Run the tools

```bash
# Python automation
PYTHONPATH=automation/python .venv/bin/python -m noc_automation.health_check
PYTHONPATH=automation/python .venv/bin/python -m noc_automation.config_backup
PYTHONPATH=automation/python .venv/bin/python -m noc_automation.config_drift

# Read-only Ansible compliance audit
bash automation/ansible/run-compliance

# Python unit tests
PYTHONPATH=automation/python .venv/bin/python -m unittest discover -s automation/python/tests -v
```

Generated backups, drift reports, JSON reports, and logs are written to runtime directories such as `configs/backups/`, `configs/drift/`, `reports/`, and `logs/`. These are excluded from version control.

## Technology stack

**Networking:** GNS3, Cisco IOSv, Cisco IOSvL2, VLANs, 802.1Q, ACLs, static routing, SSH  
**Automation:** Python, Netmiko, Paramiko, Ansible, `cisco.ios`  
**Linux:** RHEL 9, NetworkManager, SSH  
**Analysis and reporting:** Wireshark, TShark, YAML, JSON

## Documentation

- [Business requirements](docs/01-business-requirements.md)
- [Network architecture](docs/02-network-architecture.md)
- [IP addressing plan](docs/03-ip-addressing-plan.md)
- [RHEL 9 NOC server](linux/README.md)
- [Python automation](automation/python/README.md)
- [Ansible compliance audit](automation/ansible/README.md)
- [Validation matrix](testing/validation-matrix.md)
- [Packet analysis](packet-analysis/README.md)

## Author and license

**Palukuru Harsha Vardan**  
Released under the [MIT License](LICENSE).
