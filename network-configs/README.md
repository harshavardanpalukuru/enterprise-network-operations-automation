# Device Configurations

Exact running-configuration exports of the four lab devices. They are the approved baselines used by the drift-detection tool.

| File | Device | Platform |
|---|---|---|
| [`routers/R1-HQ.cfg`](routers/R1-HQ.cfg) | R1-HQ | Cisco IOSv 15.9 |
| [`routers/R2-Branch.cfg`](routers/R2-Branch.cfg) | R2-Branch | Cisco IOSv 15.9 |
| [`switches/SW1-HQ.cfg`](switches/SW1-HQ.cfg) | SW1-HQ | Cisco IOSvL2 15.2 |
| [`switches/SW2-Branch.cfg`](switches/SW2-Branch.cfg) | SW2-Branch | Cisco IOSvL2 15.2 |

Notes:

- The files are published exactly as exported, with nothing removed.
- The `nocadmin` and `admin` accounts use lab-only sample passwords, and the exports contain their hashed secrets (type 9). Do not reuse these passwords anywhere else.
- The header lines `Current configuration` and `Last configuration change` change on every save or restart. The drift tool ignores them.
- IOSvL2 does not list VLAN definitions in the exported configuration.
