# RHEL 9 Network Configuration

## 1. Network Interface Design

The NOC server uses two separate network interfaces.

| Interface | IP Address | Connection | Purpose |
|---|---|---|---|
| ens36 | 192.168.254.131/24 (observed DHCP lease) | VMware NAT / VMnet8 | External connectivity |
| ens37 | 10.10.99.10/24 (static) | GNS3-managed VMnet9 | Enterprise management |

## 2. Management Network

The ens37 interface connects the NOC server to SW1-HQ.

| Property | Value |
|---|---|
| NOC IP | 10.10.99.10/24 |
| Switch | SW1-HQ |
| Switch Port | GigabitEthernet0/1 |
| VLAN | 99 |
| VLAN Name | MGMT_NOC |
| Gateway | 10.10.99.1 |

The connection uses GNS3-managed VMware VMnet9.

## 3. NAT Network

The ens36 interface connects to VMware NAT through VMnet8.

| Property | Value |
|---|---|
| Interface | ens36 |
| Observed IP | 192.168.254.131/24 |
| Gateway | 192.168.254.2 |
| Address Assignment | DHCP |

The NAT interface provides external connectivity separately from the enterprise management network.

## 4. Routing

The default route uses the VMware NAT gateway through ens36.

Remote enterprise networks are reached through R1-HQ (10.10.99.1) using static routes.

The Cisco network uses static routing between HQ and Branch over 172.16.12.0/30.

## 5. Network Verification Commands

Display interface addresses:

`ip -br address`

Display routing table:

`ip route`

Check NetworkManager status:

`nmcli device status`

Test R1 management connectivity:

`ping -c 3 10.10.99.1`

Test SW1 management connectivity:

`ping -c 3 10.10.99.2`

## 6. Verified Connectivity

The following tests succeeded:

- RHEL ens37 to R1-HQ management address.

- RHEL ens37 to SW1-HQ management address.

- ARP resolution for both management devices.

- Management connectivity after correcting GNS3 VMware adapter integration.

The NAT and enterprise management interfaces operate on separate networks.

