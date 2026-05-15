from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required


def list_snapshots(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    vmtype: str = "qemu",
) -> str:
    resolved_node = client.resolve_node(node)
    result = client.safe_api_call(
        getattr(client.monitor_client.nodes(resolved_node), vmtype)(vmid).snapshot.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"\U0001f4f8 **Snapshots for {vmtype} {vmid} on {resolved_node}**\n"]
    for snap in result:
        name = snap.get("name", "unknown")
        description = snap.get("description", "")
        parent = snap.get("parent", "")
        snaptime = snap.get("snaptime", "")
        lines.append(f"   • **{name}** (parent: {parent})")
        if description:
            lines.append(f"     {description}")
        if snaptime:
            lines.append(f"     Created: {snaptime}")
    if not result:
        lines.append("   No snapshots found.")
    return "\n".join(lines)


@confirm_required
def create_snapshot(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    snapname: str = "",
    vmtype: str = "qemu",
    description: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    params: dict[str, Any] = {"snapname": snapname}
    if description:
        params["description"] = description
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        getattr(elevated.nodes(resolved_node), vmtype)(vmid).snapshot.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Snapshot {snapname!r} creation initiated for {vmtype} {vmid} on {resolved_node}. UPID: {upid}"


@confirm_required
def delete_snapshot(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    snapname: str = "",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        getattr(elevated.nodes(resolved_node), vmtype)(vmid).snapshot(snapname).delete,
        elevated=True,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Snapshot {snapname!r} deletion initiated for {vmtype} {vmid} on {resolved_node}. UPID: {upid}"


@confirm_required
def rollback_snapshot(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    snapname: str = "",
    vmtype: str = "qemu",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        getattr(elevated.nodes(resolved_node), vmtype)(vmid).snapshot(snapname).rollback.post,
        elevated=True,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Rollback to snapshot {snapname!r} initiated for {vmtype} {vmid} on {resolved_node}. UPID: {upid}"
