# Network Architecture Design
## 1. Topology Overview
The topology models a realistic enterprise hub-and-spoke WAN connecting **Main Office (HQ)** and **Branch Office** over a dedicated Layer 3 point-to-point WAN link (`172.16.12.0/30`).
- **Main Office (HQ):**
  - **`R1-HQ` (Cisco IOSv 15.9(3)M8):** HQ edge router performing 802.1Q Router-on-a-Stick inter-VLAN routing (`Gi0/0.10`, `Gi0/0.20`, `Gi0/0.99`), DHCP server duties for HQ user VLANs, Extended ACL enforcement, and static WAN routing to Branch (`Gi0/1`).
  - **`SW1-HQ` (Cisco IOSvL2 15.2):** HQ access/distribution switch providing 802.1Q trunking to `R1-HQ`, Layer 2 access ports for HR (`VLAN 10`), Finance (`VLAN 20`), and NOC Management (`VLAN 99`), Port Security, and a managed SVI (`interface Vlan99`).
  - **`NOC-RHEL-Server` (`noc-rhel-01` - RHEL 9):** Central Network Operations & Automation server with two network interfaces. `ens37` (`Ethernet1`) uses static IP `10.10.99.10/24` and connects to `SW1-HQ Gi0/1` through GNS3-managed `VMnet9` in Management VLAN 99. `ens36` (`Ethernet0`) obtains its IPv4 address through DHCP on the separate VMware NAT network (`VMnet8`) for external connectivity. The server supports SSH-based network administration, Python/Netmiko automation, Ansible playbooks, and packet analysis.
  - **`PC1-HQ-HR` & `PC2-HQ-FIN` (VPCS):** Departmental client endpoints in `VLAN 10` and `VLAN 20`.
- **Branch Office:**
  - **`R2-Branch` (Cisco IOSv 15.9(3)M8):** Branch router providing 802.1Q inter-VLAN routing (`Gi0/0.30`, `Gi0/0.99`), Branch DHCP services, and static WAN routing back to HQ (`Gi0/1`).
  - **`SW2-Branch` (Cisco IOSvL2 15.2):** Branch access switch providing 802.1Q trunking to `R2-Branch`, managed SVI (`interface Vlan99`), and access connectivity for Branch endpoints.
  - **`PC3-Branch-OPS` (VPCS):** Branch office client endpoint in `VLAN 30`.
## 2. Routing Design Justification
Static routing is intentionally selected over OSPF for the point-to-point WAN link (`172.16.12.0/30`) because a two-router hub-and-spoke topology has a single deterministic path between HQ and Branch. Static routing eliminates hello/LSA protocol overhead, reduces CPU/RAM utilization, prevents routing protocol attack surfaces, and simplifies fault isolation.
