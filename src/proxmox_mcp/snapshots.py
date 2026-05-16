from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required, validate_node_name, validate_vmid

ALLOWED_VMTYPES = ("qemu", "lxc")


def _validate_vmtype(vmtype: str) -> None:
    if vmtype not in ALLOWED_VMTYPES:
        raise ValueError(
            f"Invalid vmtype {vmtype!r}. Must be one of {ALLOWED_VMTYPES}"
        )


def _api(client: Any) -> Any:
    return client.get_client(elevated=False)


def snapshot_config(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    snapname: str = "",
    vmtype: str = "qemu",
) -> str:
    _validate_vmtype(vmtype)
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(
        getattr(_api(client).nodes(resolved_node), vmtype)(vmid).snapshot(snapname).config.get
    )
    if not isinstance(result, dict):
        return f"Snapshot {snapname!r} config for {vmtype} {vmid} on {resolved_node}: {result}"
    lines = [f"**Snapshot {snapname!r} config for {vmtype} {vmid} on {resolved_node}**\n"]
    for key, val in sorted(result.items()):
        lines.append(f"  • **{key}**: {val}")
    return "\n".join(lines)


def list_snapshots(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    vmtype: str = "qemu",
) -> str:
    _validate_vmtype(vmtype)
    resolved_node = client.resolve_node(node)
    result = client.safe_api_call(
        getattr(_api(client).nodes(resolved_node), vmtype)(vmid).snapshot.get
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
    _validate_vmtype(vmtype)
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
    _validate_vmtype(vmtype)
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        getattr(elevated.nodes(resolved_node), vmtype)(vmid).snapshot(snapname).delete,
        elevated=True,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Snapshot {snapname!r} deletion initiated for {vmtype} {vmid} on {resolved_node}. UPID: {upid}"


@confirm_required
def update_snapshot_config(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    snapname: str = "",
    vmtype: str = "qemu",
    description: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    _validate_vmtype(vmtype)
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    params: dict[str, Any] = {}
    if description is not None:
        params["description"] = description
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        getattr(elevated.nodes(resolved_node), vmtype)(vmid).snapshot(snapname).config.put,
        elevated=True,
        **params,
    )
    return f"Snapshot {snapname!r} config updated for {vmtype} {vmid} on {resolved_node}"


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
    _validate_vmtype(vmtype)
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        getattr(elevated.nodes(resolved_node), vmtype)(vmid).snapshot(snapname).rollback.post,
        elevated=True,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Rollback to snapshot {snapname!r} initiated for {vmtype} {vmid} on {resolved_node}. UPID: {upid}"
