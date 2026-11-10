# Network Automation Testing and Validation Matrix
## 1. Overview
This document records functional tests performed in the Enterprise NOC lab using Cisco IOSv, Cisco IOSvL2, RHEL 9, Python, Ansible and Wireshark.
## 2. Network Connectivity Tests
| Test | Expected Result | Actual Result | Status |
|---|---|---|---|
| RHEL to R1-HQ management | Reachable | Successful | PASS |
| RHEL to SW1-HQ management | Reachable | Successful | PASS |
| Endpoint to local gateway | Reachable | Successful | PASS |
| R1-HQ to R2-Branch transit | ICMP replies | 5 requests and replies | PASS |
| HR to Branch Operations | Permitted | 5/5 successful | PASS |
| Branch Operations to HR | Permitted | 5/5 successful | PASS |
| Branch Operations to Finance | Permitted (no deny by design) | 5/5 successful | PASS |
## 3. ACL Enforcement Tests
| Source | Destination | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| HR | Finance | Deny | 5 packets denied | PASS |
| Finance | HR | Deny | 5 packets denied | PASS |
| Branch Operations | Branch Management | Deny | 5 packets denied | PASS |
| Branch Operations | HQ Management | Deny | 5 packets denied | PASS |
Blocked traffic generated ICMP destination-unreachable responses with code 13 (administratively prohibited).
ACL hit counters increased for the corresponding deny entries.
## 4. SSH Validation
| Test | Result | Status |
|---|---|---|
| RHEL to Cisco SSH connectivity | Successful | PASS |
| TCP three-way handshake | Observed | PASS |
| SSH negotiation | Observed | PASS |
| Administrative privilege | Level 15 | PASS |
Wireshark was used to inspect the SSH connection.
One TCP retransmission was observed during packet analysis. The subsequent data was acknowledged, and the SSH session completed successfully.
## 5. Python Automation Tests
| Application | Expected Result | Actual Result | Status |
|---|---|---|---|
| Network health check | Four devices checked | 4 passed, 0 failed | PASS |
| Configuration backup | Four backups created | 4 successful, 0 failed | PASS |
| Backup checksum validation | Hashes match | 4 verified | PASS |
| Configuration drift detection | No unexpected changes | 4 CLEAN | PASS |
## 6. Ansible Compliance Tests
| Control | Result |
|---|---|
| R1-HQ | 4/4 checks passed |
| SW1-HQ | 4/4 checks passed |
| R2-Branch | 4/4 checks passed |
| SW2-Branch | 4/4 checks passed |
| Total | 16/16 checks passed |
Final audit result:
- Compliant devices: 4
- Non-compliant devices: 0
- Unreachable devices: 0
- Failed tasks: 0
The audit uses read-only network commands.
## 7. Python Unit Tests
The unit test suite contains ten tests covering:
- Configuration comparison.
- Configuration line-ending normalization.
- Drift detection.
- Volatile IOS header lines (byte count, last-change timestamps) ignored, while real changes are still detected.
- Interface classification.
- Interface parsing.
- Empty command output.
- Operational interface status.
Recorded result: 10 tests passed.
## 8. Backup Integrity and File Security
| Verification | Result |
|---|---|
| Four configuration backups exist | PASS |
| SHA-256 checksums match | PASS |
| Backup file permissions | 600 |
| Backup directory permission | 700 |
| Manifest permission | 600 |
| Drift JSON report permission | 600 |
| Drift log permission | 600 |
| Ansible JSON report permission | 600 |
## 9. Packet Analysis Evidence
Packet-level validation was performed using Wireshark.
The captured traffic included:
- R1-to-R2 ICMP routing.
- RHEL-to-R1 SSH communication.
- Permitted HR-to-Branch Operations traffic.
- Blocked HR-to-Finance traffic.
- Blocked Finance-to-HR traffic.
- Blocked Branch Operations-to-Branch Management traffic.
- Blocked Branch Operations-to-HQ Management traffic.
- Permitted Branch Operations-to-HR traffic.
Seven filtered capture files are included in `packet-analysis/captures/`; see [Packet Capture Evidence](../packet-analysis/README.md).
## 10. Port Security Test
Target: `SW1-HQ` GigabitEthernet0/2 (HR access port, VLAN 10), configured with port security, sticky MAC binding, a maximum of one MAC address and `violation restrict`. The authorized device is `PC1-HQ-HR` (`0050.7966.6800`).

Baseline before the test: port status `Secure-up`, violation count 0, one SecureSticky address (`0050.7966.6800`, VLAN 10).

Procedure: `PC1-HQ-HR` was disconnected from Gi0/2 and a second VPCS with MAC `0050.7966.6803` was connected in its place.

| Check | Result |
|---|---|
| Unknown device requests an address by DHCP | `Can't find dhcp server` |
| Unknown device with static `10.10.10.50/24`, ping to gateway `10.10.10.1` | `host (10.10.10.1) not reachable` |
| Security violation count | Rose from 0 to 4, then to 10 as the tests ran |
| Last source address | `0050.7966.6803`, VLAN 10 |
| Port state | `Secure-up`; interface status `connected` (not shut down) |
| Log | `%PORT_SECURITY-2-PSECURE_VIOLATION` naming `0050.7966.6803` on GigabitEthernet0/2 (two messages logged) |
| Authorized device after the lab was restarted | `PC1-HQ-HR` (`0050.7966.6800`) received `10.10.10.11` by DHCP |

Notes:
- The test was run on `SW1-HQ` Gi0/2 only. Gi0/3 and `SW2-Branch` Gi0/1 use the same port-security configuration but were not tested separately.
- GNS3 assigns VPCS MAC addresses, and they changed between sessions. After the project was reopened, `PC1-HQ-HR` presented `0050.7966.6802` and was blocked in the same way. Restarting the GNS3 server and starting the PCs in the order PC1, PC2, PC3 restored the original `…6800`, `…6801` and `…6802`. The sticky bindings in the saved switch configurations depend on this.
- Violation counters and the log buffer are not kept across a device restart. The evidence is the console output recorded during the test session.

## 11. Validation Summary
The recorded testing confirms:
- Network connectivity between the tested endpoints.
- Correctly enforced ACL permit and deny policies.
- Successful SSH management access.
- Python automation across four Cisco devices.
- Successful configuration backups and integrity checks.
- No configuration drift detected.
- An unknown device on a secured access port was blocked in restrict mode while the port stayed up.
- All 16 Ansible compliance checks passed.
- Ten Python unit tests passed.
These results describe the tested lab environment and do not represent production-network certification.
