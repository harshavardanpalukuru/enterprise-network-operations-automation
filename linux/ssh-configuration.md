# SSH Configuration and Secure Cisco Device Access

## 1. Overview

The RHEL NOC server initiates SSH connections to Cisco routers and switches for network monitoring, configuration collection and compliance auditing.

The project uses:

- Netmiko with Paramiko for Python automation.
- Ansible network_cli for Cisco device automation.
- LibSSH as the Ansible persistent connection backend.

## 2. Cisco Device Management

| Device | Management IP |
|---|---|
| R1-HQ | 10.10.99.1 |
| SW1-HQ | 10.10.99.2 |
| R2-Branch | 10.20.99.1 |
| SW2-Branch | 10.20.99.2 |

NOC management IP: 10.10.99.10.

Cisco VTY access is restricted through management ACLs.

## 3. Credential Management

Cisco credentials are retrieved from environment variables loaded through the project's .env file.

Variable names:

- NOC_USERNAME
- NOC_PASSWORD

The .env file must never be published.

The .env.example file contains placeholder credentials.

## 4. SSH Host-Key Verification

Ansible SSH host-key checking is enabled.

Trusted device fingerprints are maintained in:

`~/.ssh/known_hosts`

Host-key checking must not be disabled to bypass connection errors.

## 5. Legacy Cisco SSH Compatibility

The Cisco IOS lab images require compatibility with older SSH algorithms.

The tested environment uses:

- Diffie-Hellman group14 SHA-1 compatibility.
- ssh-rsa compatibility.
- Paramiko 4.0.0 for direct Netmiko connections.

These compatibility settings are specific to the legacy lab devices and should not be applied globally to modern SSH environments.

## 6. SSH Validation

Successful SSH connectivity was verified between the NOC server and Cisco network devices.

The tested administrative session returned privilege level 15.

Wireshark packet analysis confirmed:

- TCP three-way handshake.
- SSH connection negotiation.
- SSH traffic exchange.


A separate live SSH session verified administrative access and privilege level 15. The SSH packet capture is documented separately in the packet analysis section.


