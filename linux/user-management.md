# RHEL 9 User and Project Access Management

## 1. NOC Operator Account

The primary project operator is `nocadmin`.

Project directory:

`/home/nocadmin/enterprise-network-operations-automation`

Python virtual environment:

`/home/nocadmin/enterprise-network-operations-automation/.venv`

## 2. Project Directory Protection

The project handles network credentials, configuration backups, logs and reports.

| Resource | Permission |
|---|---|
| .env | 600 |
| Configuration backup files | 600 |
| Backup directories | 700 |
| Initial baseline files | 600 |
| Baseline directory | 700 |
| Generated JSON reports | 600 |
| Automation log files | 600 |

These permissions restrict access to sensitive operational data.

## 3. Credential Protection

Cisco credentials are stored in the `.env` file.

The `.env` file is excluded from source publication through `.gitignore`.

The `.env.example` file contains placeholder values and must not contain real credentials.

## 4. SSH Trust Data

Trusted SSH host fingerprints are maintained in:

`~/.ssh/known_hosts`

Host-key checking remains enabled for Ansible connections.

## 5. Verification Commands

Inspect the current operator identity:

`id`

Inspect the operator account:

`getent passwd nocadmin`

Inspect project permissions:

`ls -ld /home/nocadmin/enterprise-network-operations-automation`

Inspect credential file permissions:

`ls -l /home/nocadmin/enterprise-network-operations-automation/.env`

Actual sudo privileges and group memberships should be verified before documenting them as specific security controls.


