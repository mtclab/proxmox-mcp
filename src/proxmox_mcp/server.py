import sys

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.config import Config

mcp = FastMCP("proxmox-mcp")


def main() -> None:
    try:
        config = Config.from_env()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    ProxmoxClient(config)

    # Tool registrations will be added in subsequent issues:
    # - VM/LXC lifecycle tools (lifecycle.py)
    # - Template/tools (templates.py)
    # - Snapshot tools (snapshots.py)
    # - Backup tools (backups.py)
    # - Network tools (networking.py)
    # - Permission tools (permissions.py)
    # - Storage tools (storage.py)
    # - Discovery tools (discovery.py)

    mcp.run()


if __name__ == "__main__":
    main()
