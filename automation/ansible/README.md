# Ansible Cisco Network Compliance Audit
## 1. Overview
The project uses Ansible to perform read-only configuration and security compliance checks against four Cisco network devices.
The automation runs from the RHEL 9 NOC server.
## 2. Ansible Environment
| Component | Configuration |
|---|---|
| Ansible Core | 2.15.13 |
| Network Collection | cisco.ios 5.3.0 |
| Connection Plugin | ansible.netcommon.network_cli |
| SSH Backend | LibSSH |
| Network OS | cisco.ios.ios |
## 3. Device Inventory
| Device | Management IP |
|---|---|
| R1-HQ | 10.10.99.1 |
| SW1-HQ | 10.10.99.2 |
| R2-Branch | 10.20.99.1 |
| SW2-Branch | 10.20.99.2 |
Device credentials are loaded from environment variables rather than stored directly in the inventory.
## 4. Compliance Checks
### Management Access
- Management SSH ACL configuration.
- Permitted NOC management source.
- VTY SSH restrictions.
- Local login configuration.
- SSH-only transport access.
### Switch Configuration
- Expected VLANs.
- Access-port assignments.
- 802.1Q trunk configuration.
- Allowed VLANs on trunks.
### Router Configuration
- Interface ACL assignments.
- Expected static routes between HQ and Branch.
## 5. Execution
Run the compliance audit from the RHEL project root:
`bash automation/ansible/run-compliance`
The shortcut loads the project environment and executes the Ansible compliance playbook.
## 6. Reporting
The audit generates a timestamped JSON report in:
`reports/`
The report contains:
- Generation timestamp.
- Device compliance status.
- Individual control results.
- Total compliant devices.
- Total non-compliant devices.
## 7. Recorded Validation Results
| Device | Checks Passed |
|---|---|
| R1-HQ | 4/4 |
| SW1-HQ | 4/4 |
| R2-Branch | 4/4 |
| SW2-Branch | 4/4 |
| Total | 16/16 |
Final recorded result:
- Total devices: 4.
- Compliant devices: 4.
- Non-compliant devices: 0.
- Failed Ansible tasks: 0.
- Unreachable devices: 0.
## 8. Operational Safety
The compliance playbook uses read-only network commands.
It does not deploy configuration changes to routers or switches.
SSH host-key checking remains enabled.
Device credentials are excluded from source publication.
## 9. Implementation Files
| File | Purpose |
|---|---|
| automation/ansible/ansible.cfg | Ansible connection configuration |
| automation/ansible/inventory/hosts.yml | Cisco device inventory |
| automation/ansible/inventory/group_vars/cisco.yml | Cisco connection variables |
| automation/ansible/vars/compliance_policy.yml | Expected compliance policy |
| automation/ansible/playbooks/compliance_audit.yml | Compliance audit playbook |
| automation/ansible/run-compliance | One-command execution shortcut |
