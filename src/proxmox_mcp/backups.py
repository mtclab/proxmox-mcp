from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required, format_bytes


def list_backups(
    client: Any,
    node: Optional[str] = None,
    storage: str = "local",
) -> str:
    resolved_node = client.resolve_node(node)
    result = client.safe_api_call(
        client.monitor_client.nodes(resolved_node).storage(storage).content.get,
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
def create_backup(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    vmtype: str = "qemu",
    storage: str = "local",
    mode: str = "snapshot",
    compress: str = "zstd",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    params: dict[str, Any] = {
        "vmid": vmid,
        "storage": storage,
        "mode": mode,
        "compress": compress,
    }
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).vzdump.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Backup creation initiated for {vmtype} {vmid} on {resolved_node}. UPID: {upid}"


@confirm_required
def restore_backup(
    client: Any,
    vmid: Optional[int] = None,
    archive: str = "",
    storage: str = "local",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not archive:
        raise ValueError(
            "archive is required for backup restore. "
            "Use list_backups to find available backup archives."
        )
    params: dict[str, Any] = {
        "vmid": vmid,
        "archive": archive,
        "storage": storage,
    }
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes.vzdump_restore.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Backup restore initiated for VMID {vmid} from {archive!r}. UPID: {upid}"
