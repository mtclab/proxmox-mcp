from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.exceptions import ProxmoxPermissionError
from proxmox_mcp.utils import confirm_required, validate_node_name


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


async def list_disks(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.list.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"💿 **Disks on {resolved_node}**\n"]
    for disk in result:
        devpath = disk.get("devpath", disk.get("device", "unknown"))
        size = disk.get("size", "N/A")
        used = disk.get("used", "N/A")
        health = disk.get("health", "N/A")
        model = disk.get("model", "")
        serial = disk.get("serial", "")
        lines.append(f"   • **{devpath}** — size: {size}, used: {used}, health: {health}")
        if model:
            lines.append(f"     Model: {model}")
        if serial:
            lines.append(f"     Serial: {serial}")
    if not result:
        lines.append("   No disks found.")
    return "\n".join(lines)


async def get_disk_smart(client: ProxmoxClient, node: Optional[str] = None, disk: str = "") -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not disk:
        raise ValueError("disk identifier is required")
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.smart.get,
        disk=disk,
    )
    lines = [f"💿 **SMART: {disk} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                name = entry.get("name", "unknown")
                value = entry.get("value", entry.get("raw", "N/A"))
                lines.append(f"   • {name}: {value}")
    if not result:
        lines.append("   No SMART data available.")
    return "\n".join(lines)


async def list_lvm(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.lvm.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"💿 **LVM Volume Groups on {resolved_node}**\n"]
    for vg in result:
        name = vg.get("vg", "unknown")
        size = vg.get("size", "N/A")
        free = vg.get("free", "N/A")
        lines.append(f"   • **{name}** — size: {size}, free: {free}")
    if not result:
        lines.append("   No LVM volume groups found.")
    return "\n".join(lines)


async def list_lvmthin(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.lvmthin.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"💿 **LVM Thin Pools on {resolved_node}**\n"]
    for pool in result:
        name = pool.get("lvname", pool.get("vg", "unknown"))
        size = pool.get("size", "N/A")
        used = pool.get("used", "N/A")
        lines.append(f"   • **{name}** — size: {size}, used: {used}")
    if not result:
        lines.append("   No LVM thin pools found.")
    return "\n".join(lines)


async def list_zfs(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.zfs.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"💿 **ZFS Pools on {resolved_node}**\n"]
    for pool in result:
        name = pool.get("name", "unknown")
        size = pool.get("size", "N/A")
        free = pool.get("free", "N/A")
        health = pool.get("health", "N/A")
        lines.append(f"   • **{name}** — size: {size}, free: {free}, health: {health}")
    if not result:
        lines.append("   No ZFS pools found.")
    return "\n".join(lines)


@confirm_required
async def init_gpt(
    client: ProxmoxClient,
    node: Optional[str] = None,
    disk: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not disk:
        raise ValueError("disk identifier is required")
    elevated = client.get_client(elevated=True)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.initgpt.post,
        elevated=True,
        disk=disk,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Disk {disk!r} initialized with GPT on {resolved_node}. UPID: {upid}"


@confirm_required
async def wipe_disk(
    client: ProxmoxClient,
    node: Optional[str] = None,
    disk: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not disk:
        raise ValueError("disk identifier is required")
    elevated = client.get_client(elevated=True)
    try:
        result = await client.safe_api_call(
            elevated.nodes(resolved_node).disks.wipedisk.put,
            elevated=True,
            disk=disk,
        )
    except ProxmoxPermissionError:
        return (
            f"⚠️ Disk wipe requires root@pam authentication. "
            f"API tokens (even with Administrator role) lack permission for this operation. "
            f"Use the PVE web UI or SSH with root@pam to wipe disk {disk!r} on {resolved_node}."
        )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Disk {disk!r} wiped on {resolved_node}. UPID: {upid}"


async def zfs_detail(client: ProxmoxClient, node: Optional[str] = None, name: str = "") -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.zfs(name).get,
    )
    lines = [f"💿 **ZFS Pool: {name} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
async def zfs_create(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    devices: str = "",
    raidlevel: str = "single",
    ashift: Optional[int] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    if not devices:
        raise ValueError("'devices' is required for ZFS pool creation (comma-separated disk paths)")
    elevated = client.get_client(elevated=True)
    params: dict[str, Any] = {"name": name, "devices": devices, "raidlevel": raidlevel}
    if ashift is not None:
        params["ashift"] = ashift
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.zfs.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"ZFS pool {name!r} created on {resolved_node}. UPID: {upid}"


@confirm_required
async def zfs_destroy(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    elevated = client.get_client(elevated=True)
    params: dict[str, Any] = {}
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.zfs(name).delete,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"ZFS pool {name!r} destroyed on {resolved_node}. UPID: {upid}"


@confirm_required
async def lvm_create(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    devices: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    elevated = client.get_client(elevated=True)
    params: dict[str, Any] = {"name": name}
    if devices:
        params["devices"] = devices
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.lvm.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"LVM VG {name!r} created on {resolved_node}. UPID: {upid}"


async def lvm_detail(client: ProxmoxClient, node: Optional[str] = None, name: str = "") -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.lvm(name).get,
    )
    lines = [f"💿 **LVM VG: {name} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
async def lvm_destroy(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    elevated = client.get_client(elevated=True)
    params: dict[str, Any] = {}
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.lvm(name).delete,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"LVM VG {name!r} destroyed on {resolved_node}. UPID: {upid}"


@confirm_required
async def lvmthin_create(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    devices: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    elevated = client.get_client(elevated=True)
    # Note: PVE auto-generates thinpool and vgname from the name parameter.
    # Pass thinpool/vgname via **kwargs only if custom names are needed.
    params: dict[str, Any] = {"name": name}
    if devices:
        params["devices"] = devices
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.lvmthin.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"LVM thin pool {name!r} created on {resolved_node}. UPID: {upid}"


@confirm_required
async def lvmthin_destroy(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    elevated = client.get_client(elevated=True)
    params: dict[str, Any] = {}
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.lvmthin(name).delete,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"LVM thin pool {name!r} destroyed on {resolved_node}. UPID: {upid}"


async def directory_list(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.directory.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"💿 **Directory Storages on {resolved_node}**\n"]
    for entry in result:
        name = entry.get("name", "unknown")
        path = entry.get("path", "N/A")
        lines.append(f"   • **{name}** — path: {path}")
    if not result:
        lines.append("   No directory storages found.")
    return "\n".join(lines)


@confirm_required
async def directory_create(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    devices: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    elevated = client.get_client(elevated=True)
    params: dict[str, Any] = {"name": name}
    if devices:
        params["devices"] = devices
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.directory.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Directory storage {name!r} created on {resolved_node}. UPID: {upid}"


@confirm_required
async def directory_destroy(
    client: ProxmoxClient,
    node: Optional[str] = None,
    name: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    elevated = client.get_client(elevated=True)
    params: dict[str, Any] = {}
    params.update(kwargs)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).disks.directory(name).delete,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Directory storage {name!r} destroyed on {resolved_node}. UPID: {upid}"


async def get_directory_detail(client: ProxmoxClient, node: Optional[str] = None, name: str = "") -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.directory(name).get,
    )
    lines = [f"💿 **Directory Storage: {name} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


async def get_lvmthin_detail(client: ProxmoxClient, node: Optional[str] = None, name: str = "") -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not name:
        raise ValueError("name is required")
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).disks.lvmthin(name).get,
    )
    lines = [f"💿 **LVM Thin Pool: {name} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)
