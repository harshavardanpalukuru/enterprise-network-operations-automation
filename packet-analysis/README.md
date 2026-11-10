# Packet Capture Evidence

This directory contains seven filtered PCAPNG files selected from the original GNS3/Wireshark captures. The original captures are retained separately on the lab workstation; these repository copies are filtered evidence extracts.

## Capture Inventory

| File | Packets | Demonstrates |
|---|---:|---|
| `acl_finance_to_hr_block-filtered.pcapng` | 10 | Five Finance-to-HR ICMP echo requests and five administratively prohibited responses. |
| `acl_hr_to_finance_block-filtered.pcapng` | 10 | Five HR-to-Finance ICMP echo requests and five administratively prohibited responses. |
| `acl_ops_to_branch_management_block-filtered.pcapng` | 10 | Five Branch Operations-to-Branch Management ICMP echo requests and five administratively prohibited responses. |
| `acl_ops_to_hq_management_block-filtered.pcapng` | 10 | Five Branch Operations-to-HQ Management ICMP echo requests and five administratively prohibited responses. |
| `acl_ops_to_hr_permit-filtered.pcapng` | 10 | Five Branch Operations-to-HR ICMP echo requests and five echo replies. |
| `icmp_r1_r2-filtered.pcapng` | 10 | Five ICMP echo requests from R1 to R2 over the `172.16.12.0/30` transit link and five replies. |
| `ssh_rhel_to_r1-filtered.pcapng` | 131 | SSH/TCP session traffic between the RHEL NOC host (`10.10.99.10`) and R1 (`10.10.99.1`), including connection establishment, key exchange and encrypted session packets. |

## Filtering and Validation

Original network traffic was captured and initially inspected using Wireshark. The six ICMP evidence files included in this repository were subsequently filtered using TShark, Wireshark's command-line packet analyzer, with Wireshark display-filter syntax. The SSH evidence file was also filtered using TShark to TCP port 22 traffic between `10.10.99.10` and `10.10.99.1`; its decoded protocol columns include TCP, SSH and SSHv2.

The filtered files were reopened with TShark and checked for packet counts and expected protocol content. All seven files passed that validation. The source captures were checked to remain present after filtering.

## Interpretation Notes

- ICMP type `8`, code `0` represents an echo request.
- ICMP type `0`, code `0` represents an echo reply.
- ICMP type `3`, code `13` represents communication administratively prohibited.
- The SSH capture exposes connection and protocol-negotiation metadata, including the OpenSSH 9.9 client and Cisco SSH server identification strings. SSH session data after key establishment is encrypted; the capture does not show decrypted authentication credentials.
- A single TCP retransmission was observed in the SSH source capture. The earlier packet-level review found subsequent acknowledgement of the retransmitted data. The capture should not be interpreted as proof of persistent packet loss.

## Scope and Privacy

These are lab captures from private IPv4 address ranges and contain internal lab addressing and network metadata. They are filtered to the scenarios described above, but filtering is not equivalent to anonymization. Review the files and their metadata before publishing them publicly. Do not add captures from real or third-party networks, or captures containing real credentials, private keys, personal data or unrelated traffic.

The PCAPNG files are supporting evidence for the documented lab tests. They do not, on their own, prove every aspect of device configuration or successful SSH authorization. The SSH privilege-level check was separately performed on the live device and recorded in the project validation notes.
