# Business Requirements and Technical Mapping

This document maps operational requirements to implemented functionality and recorded validation evidence.

| ID | Operational Problem | Technical Solution | Status |
|---|---|---|---|
| BR-01 | Departments require network segmentation and traffic control. | HQ VLAN 10, 20 and 99; Branch VLAN 30 and 99; inter-VLAN routing and extended ACLs. | Validated |
| BR-02 | Network devices require secure administrative access. | SSHv2, local authentication, SSH-only VTY access and management-source ACL restrictions. | Validated |
| BR-03 | Manual network checks are repetitive. | Python/Netmiko health checks, configuration drift detection and Ansible compliance auditing. | Validated |
| BR-04 | Configuration backups must be consistent and verifiable. | Timestamped Python backups, SHA-256 manifests and restricted file permissions. | Validated |
| BR-05 | Connectivity and access-control behavior must be verifiable at packet level. | Connectivity testing, ACL counter inspection and Wireshark packet analysis. | Validated |
| BR-06 | Unauthorized endpoints must be restricted on access switch ports. | Switch port security with MAC learning and violation controls. | Validated |

## Validation Evidence

### BR-01: Network Segmentation

- HQ and Branch VLAN assignments verified.
- Router interface ACL assignments verified.
- Permitted HR-to-Branch Operations traffic tested.
- Permitted Branch Operations-to-HR traffic tested.
- Restricted inter-department and management traffic tested.

### BR-02: Secure Administration

- Management SSH ACL checks passed on four devices.
- VTY SSH restriction checks passed on four devices.
- Successful RHEL-to-Cisco SSH session verified.
- Administrative privilege level 15 confirmed.

### BR-03: Network Automation

- Python health check completed against four devices.
- Configuration drift detection completed against four devices.
- Ansible compliance audit completed successfully.
- Ten Python unit tests passed.

### BR-04: Configuration Backup

- Four Cisco running configurations backed up.
- Four SHA-256 checksums verified.
- Sensitive backup files and directories use restricted permissions.

### BR-05: Packet-Level Verification

- ICMP routing traffic captured.
- SSH traffic captured and inspected.
- ACL permit and deny behavior validated through packet captures.

### BR-06: Switch Port Security

- Port security with sticky MAC binding and `violation restrict` configured on the access ports.
- An unknown device on `SW1-HQ` Gi0/2 received no DHCP lease and could not reach its gateway.
- The violation counter and log recorded the unknown MAC, and the port stayed up.
- Tested on `SW1-HQ` Gi0/2 only; see the [validation matrix](../testing/validation-matrix.md).

## Status Definitions

- Validated: Functionality passed its corresponding recorded tests.
- Pending verification: Implementation or operational behavior has not been demonstrated through sufficient evidence.

Only verified functionality is marked as validated.
