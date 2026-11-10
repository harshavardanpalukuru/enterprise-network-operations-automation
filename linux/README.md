# RHEL 9 Linux Administration — NOC Automation Server
## Overview
This project uses a Red Hat Enterprise Linux 9 virtual machine as its central Network Operations Center (NOC) and network automation node.
The server provides management connectivity to Cisco HQ and Branch network devices and executes Python/Netmiko and Ansible automation.
## System Information
| Property | Configuration |
|---|---|
| Hostname | noc-rhel-01 |
| Operating System | RHEL 9.8 |
| VM Name | NOC-RHEL-Server |
| CPU | 2 vCPUs |
| Memory | 2 GB |
| Primary User | nocadmin |
| Project Directory | /home/nocadmin/enterprise-network-operations-automation |
## Network Configuration
| Interface | IPv4 Address | Connection | Purpose |
|---|---|---|---|
| ens36 | 192.168.254.131/24 (observed DHCP lease) | VMware NAT / VMnet8 | External connectivity |
| ens37 | 10.10.99.10/24 (static) | GNS3-managed VMnet9 | Enterprise management |
Default route: 192.168.254.2 through ens36.
The enterprise management interface connects to SW1-HQ through VLAN 99.
## Automation Capabilities
- Python and Netmiko network health checks.
- Automated Cisco configuration backups.
- SHA-256 backup integrity verification.
- Configuration drift detection.
- Ansible-based Cisco compliance auditing.
- Python unit testing.
## Documentation Index
| Document | Description |
|---|---|
| rhel9-setup.md | Host environment and automation dependencies |
| network-configuration.md | Network interfaces, addressing and routing |
| ssh-configuration.md | SSH and Cisco device connectivity |
| user-management.md | NOC operator and project permissions |
## Validation Results
- Successful RHEL management connectivity.
- Successful SSH access to Cisco devices.
- Four Cisco devices passed Python health checks.
- Four configuration backups successfully generated.
- All four backup checksums verified.
- Four devices reported CLEAN by configuration drift detection.
- Ansible compliance audit: 16 of 16 checks passed.
- Python unit tests: ten passed.
## Security
- Cisco credentials are stored in the protected .env file.
- The .env file must never be published.
- SSH host-key checking remains enabled.
- Generated reports, logs and configuration backups use restricted permissions.
- Cisco management access is restricted through management ACLs.
This documentation describes the tested lab environment. Unverified host-hardening controls are not claimed as implemented.
