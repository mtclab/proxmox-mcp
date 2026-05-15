# proxmox-mcp

Python MCP server for Proxmox VE — full API coverage, dual-token auth, SSL handling, node discovery.

## Features

- **70+ tools** covering full PVE API (VMs, LXC, storage, templates, snapshots, backups, networking, ACL)
- **Dual-token auth** — read-only monitor token (PVEAuditor) + admin token (PVEAdmin)
- **Read-only by default** — elevated ops require `PROXMOX_ALLOW_ELEVATED=true` AND `confirm=true`
- **Auto node discovery** — queries `/nodes`, never assumes node name
- **SSL flexible** — `verify=True/False/path/to/ca.pem`
- **Task tracking** — UPID polling with exitstatus checking
- **Error aware** — handles PVE 595, SSL mismatch, token permission errors

## Installation

```bash
pip install proxmox-mcp
```

## Configuration

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "proxmox-mcp",
      "env": {
        "PROXMOX_URL": "https://10.96.16.19:8006",
        "PROXMOX_VERIFY": "false",
        "PROXMOX_MONITOR_TOKEN_ID": "zabbix@pve!zabbix",
        "PROXMOX_MONITOR_TOKEN_SECRET": "",
        "PROXMOX_ADMIN_TOKEN_ID": "homepilot@pve!homepilot",
        "PROXMOX_ADMIN_TOKEN_SECRET": "",
        "PROXMOX_ALLOW_ELEVATED": "false",
        "PROXMOX_DEFAULT_NODE": "pve"
      }
    }
  }
}
```

## Development

```bash
git clone https://github.com/mtclab/proxmox-mcp.git
cd proxmox-mcp
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Architecture

```
proxmox_mcp/
├── server.py          # MCP server, tool registration
├── client.py          # PVE API client (dual token, node discovery, SSL)
├── config.py          # Environment config, validation
├── discovery.py       # Read-only discovery tools
├── lifecycle.py       # VM/LXC create/start/stop/delete
├── templates.py       # Template catalog, download, upload
├── snapshots.py       # Snapshot management
├── backups.py         # Backup/restore
├── networking.py      # Network config
├── permissions.py     # ACL/roles/users/tokens
├── storage.py         # Storage content, ISOs
└── utils.py           # confirm_required, node_resolver, error handling
```