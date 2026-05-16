from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.utils import confirm_required, format_bytes, validate_storage_name, validate_vmid


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


async def list_backups(
    client: ProxmoxClient,
    node: Optional[str] = None,
    storage: str = "local",
) -> str:
    resolved_node = await client.resolve_node(node)
    validate_storage_name(storage)
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).storage(storage).content.get,
        content="backup",
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"\U0001f4be **Backups on {storage} ({resolved_node})**\n"]
    for item in result:
        volid = item.get("volid", "unknown")
        size = item.get("size", 0)
        ctype = item.get("content", "?")
        lines.append(f"   • {volid} ({ctype}) — {format_bytes(size) if size else 'N/A'}")
    if not result:
        lines.append("   No backups found.")
    return "\n".join(lines)


@confirm_required
async def create_backup(
    client: ProxmoxClient,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    vmtype: str = "qemu",
    storage: str = "local",
    mode: str = "snapshot",
    compress: str = "zstd",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_vmid(vmid)
    validate_storage_name(storage)
    params: dict[str, Any] = {
        "vmid": vmid,
        "storage": storage,
        "mode": mode,
        "compress": compress,
        "type": vmtype,
    }
    elevated = client.get_client(elevated=True)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).vzdump.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Backup creation initiated for {vmtype} {vmid} on {resolved_node}. UPID: {upid}"


@confirm_required
async def restore_backup(
    client: ProxmoxClient,
    vmid: Optional[int] = None,
    archive: str = "",
    storage: str = "local",
    vmtype: str = "qemu",
    node: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not archive:
        raise ValueError("archive is required for backup restore. Use list_backups to find available backup archives.")
    if not vmid:
        raise ValueError("vmid is required for backup restore")
    validate_vmid(vmid)
    validate_storage_name(storage)
    resolved_node = await client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    if vmtype == "lxc":
        params: dict[str, Any] = {
            "vmid": vmid,
            "ostemplate": archive,
            "storage": storage,
            "restore": 1,
        }
        result = await client.safe_api_call(
            elevated.nodes(resolved_node).lxc.post,
            elevated=True,
            **params,
        )
    else:
        params: dict[str, Any] = {
            "vmid": vmid,
            "archive": archive,
            "storage": storage,
            "restore": 1,
        }
        result = await client.safe_api_call(
            elevated.nodes(resolved_node).qemu.post,
            elevated=True,
            **params,
        )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Backup restore initiated for {vmtype} {vmid} from {archive!r} on {resolved_node}. UPID: {upid}"
