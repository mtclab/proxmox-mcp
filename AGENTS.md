# Proxmox MCP Server — Agent Conventions

## Session Start
Read `~/.config/opencode/handoffs/session-state.md` FIRST. Check `git log` and `gh issue list`.

## Code Conventions
- Python 3.12+, async/await
- Proxmoxer for PVE API client
- Two-tier auth: monitor token (PVEAuditor) vs elevated token (Administrator)
- Pydantic models for all tool inputs
- Ruff for linting: `uv run ruff check src/ tests/`
- Tests: `uv run pytest tests/ -q -x`

## Architecture
- `src/proxmox_mcp/server.py` — MCP server, tool registry
- `src/proxmox_mcp/client.py` — Proxmoxer client wrapper, elevated/monitor token handling
- `src/proxmox_mcp/lifecycle.py` — VM/LXC create, configure, delete, migrate
- `src/proxmox_mcp/discovery.py` — VM/LXC info, status, metrics
- `src/proxmox_mcp/storage.py` — Storage pools, ISOs, volumes
- `src/proxmox_mcp/permissions.py` — ACLs, roles, users, tokens
- `src/proxmox_mcp/firewall.py` — Firewall rules, IPSets, aliases
- `src/proxmox_mcp/ha.py` — HA groups, resources, rules
- `src/proxmox_mcp/snapshots.py` — Snapshot create, delete, rollback
- `src/proxmox_mcp/ceph.py` — Ceph status, pools, OSDs
- `src/proxmox_mcp/sdn.py` — SDN zones, VNets, subnets

## Key Patterns
- All tool functions call `_api(client)` for monitor token or `_elevated(client)` for admin token
- `safe_api_call()` wraps all PVE API calls with error handling
- `ProxmoxNotFoundError` for 404/500 "does not exist" errors
- `ProxmoxPermissionError` for 403 errors
- `validate_disk_size()` strips G/GiB/T/TiB suffixes
- `dptype` defaults to `"in"` for firewall rules (PVE requires direction)
- `list_usb` uses elevated token (requires Sys.Modify)

## PVE Cluster
- Single node `pve` at 192.168.100.2
- VM 101 (running), LXC 100 (stopped)
- API token: `homepilot@pve!homepilot` (Administrator role)