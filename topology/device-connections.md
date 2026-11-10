# Physical & Logical Device Connections
| Source Device | Source Interface | Destination Device | Destination Interface | Mode / Encapsulation | Allowed / Assigned VLANs |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`R1-HQ`** | `GigabitEthernet0/1` | **`R2-Branch`** | `GigabitEthernet0/1` | Routed Layer 3 | N/A (`172.16.12.0/30`) |
| **`R1-HQ`** | `GigabitEthernet0/0` | **`SW1-HQ`** | `GigabitEthernet0/0` | 802.1Q Trunk | `VLAN 10, 20, 99` |
| **`SW1-HQ`** | `GigabitEthernet0/1` | **`NOC-RHEL-Server`** | `Ethernet1` (`ens37`) | Access | `VLAN 99` (`MGMT_NOC`) |
| **`SW1-HQ`** | `GigabitEthernet0/2` | **`PC1-HQ-HR`** | `Ethernet0` | Access | `VLAN 10` (`HR_USERS`) |
| **`SW1-HQ`** | `GigabitEthernet0/3` | **`PC2-HQ-FIN`** | `Ethernet0` | Access | `VLAN 20` (`FINANCE`) |
| **`R2-Branch`** | `GigabitEthernet0/0` | **`SW2-Branch`** | `GigabitEthernet0/0` | 802.1Q Trunk | `VLAN 30, 99` |
| **`SW2-Branch`** | `GigabitEthernet0/1` | **`PC3-Branch-OPS`** | `Ethernet0` | Access | `VLAN 30` (`BRANCH_OPS`) |
### NOC Server VMware Connectivity

The NOC-RHEL-Server has two network interfaces:

- **Ethernet1 (ens37):** Connected to SW1-HQ Gi0/1 through GNS3-managed VMnet9. Uses static IP `10.10.99.10/24` for enterprise network management.
- **Ethernet0 (ens36):** Connected to VMware NAT (VMnet8). Obtains its IPv4 address through DHCP and provides external network connectivity.

The VMware NAT interface is not a connection to the enterprise switch.