# IPv4 Addressing & VLAN Plan
## 1. Subnets and VLAN Assignments
| Site | VLAN ID | VLAN Name | IPv4 Subnet | Subnet Mask | Default Gateway | DHCP Pool Range |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HQ** | `10` | `HR_USERS` | `10.10.10.0/24` | `255.255.255.0` | `10.10.10.1` (`R1-HQ Gi0/0.10`) | `10.10.10.11 - 10.10.10.254` |
| **HQ** | `20` | `FINANCE` | `10.10.20.0/24` | `255.255.255.0` | `10.10.20.1` (`R1-HQ Gi0/0.20`) | `10.10.20.11 - 10.10.20.254` |
| **HQ** | `99` | `MGMT_NOC` | `10.10.99.0/24` | `255.255.255.0` | `10.10.99.1` (`R1-HQ Gi0/0.99`) | Static Only (Mgmt Subnet) |
| **WAN** | N/A | `WAN_LINK` | `172.16.12.0/30` | `255.255.255.252` | Point-to-Point | Static (`172.16.12.1` / `.2`) |
| **Branch** | `30` | `BRANCH_OPS` | `10.20.30.0/24` | `255.255.255.0` | `10.20.30.1` (`R2-Branch Gi0/0.30`) | `10.20.30.11 - 10.20.30.254` |
| **Branch** | `99` | `BRANCH_MGMT` | `10.20.99.0/24` | `255.255.255.0` | `10.20.99.1` (`R2-Branch Gi0/0.99`) | Static Only (Mgmt Subnet) |
## 2. Device Interface IP Table
| Device | Interface | IPv4 Address | Subnet Mask | Connected To / Role |
| :--- | :--- | :--- | :--- | :--- |
| **`R1-HQ`** | `Gi0/0.10` | `10.10.10.1` | `255.255.255.0` | HQ `VLAN 10` (`HR_USERS`) Gateway |
| **`R1-HQ`** | `Gi0/0.20` | `10.10.20.1` | `255.255.255.0` | HQ `VLAN 20` (`FINANCE`) Gateway |
| **`R1-HQ`** | `Gi0/0.99` | `10.10.99.1` | `255.255.255.0` | HQ `VLAN 99` (`MGMT_NOC`) Gateway |
| **`R1-HQ`** | `Gi0/1` | `172.16.12.1` | `255.255.255.252` | WAN Link to `R2-Branch Gi0/1` |
| **`SW1-HQ`** | `Vlan99` | `10.10.99.2` | `255.255.255.0` | HQ Switch Management SVI (GW: `10.10.99.1`) |
| **`NOC-RHEL-Server`** | `ens37` (`Ethernet1`) | `10.10.99.10` (Static) | `255.255.255.0` | Connected to `SW1-HQ Gi0/1` through GNS3-managed `VMnet9`, Access VLAN 99 |
| **`NOC-RHEL-Server`** | `ens36` (`Ethernet0`) | DHCP (observed lease: `192.168.254.131`) | `255.255.255.0` | VMware NAT (`VMnet8`), gateway: `192.168.254.2` |
| **`PC1-HQ-HR`** | `eth0` | `10.10.10.11` (DHCP) | `255.255.255.0` | Connected to `SW1-HQ Gi0/2` (`VLAN 10`) |
| **`PC2-HQ-FIN`** | `eth0` | `10.10.20.11` (DHCP) | `255.255.255.0` | Connected to `SW1-HQ Gi0/3` (`VLAN 20`) |
| **`R2-Branch`** | `Gi0/1` | `172.16.12.2` | `255.255.255.252` | WAN Link to `R1-HQ Gi0/1` |
| **`R2-Branch`** | `Gi0/0.30` | `10.20.30.1` | `255.255.255.0` | Branch `VLAN 30` (`BRANCH_OPS`) Gateway |
| **`R2-Branch`** | `Gi0/0.99` | `10.20.99.1` | `255.255.255.0` | Branch `VLAN 99` (`BRANCH_MGMT`) Gateway |
| **`SW2-Branch`** | `Vlan99` | `10.20.99.2` | `255.255.255.0` | Branch Switch Management SVI (GW: `10.20.99.1`) |
| **`PC3-Branch-OPS`** | `eth0` | `10.20.30.11` (DHCP) | `255.255.255.0` | Connected to `SW2-Branch Gi0/1` (`VLAN 30`) |
