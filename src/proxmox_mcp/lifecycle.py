from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required


def _get_next_vmid(client: Any) -> int:
    result = client.monitor_client.cluster.nextid.get()
    return int(result)


def _validate_ostemplate(client: Any, node: str, ostemplate: str) -> None:
    storage_name = ostemplate.split(":")[0] if ":" in ostemplate else "local"
    try:
        content = client.safe_api_call(
            client.monitor_client.nodes(node).storage(storage_name).content.get
        )
        if isinstance(content, list):
            volids = [item.get("volid", "") for item in content]
            if ostemplate not in volids:
                raise ValueError(
                    f"OSTemplate {ostemplate!r} not found in storage {storage_name!r}. "
                    f"Available: {', '.join(v for v in volids if 'vztmpl' in v)}"
                )
    except ValueError:
        raise
    except Exception:
        pass


@confirm_required
def create_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    ostemplate: str = "",
    hostname: Optional[str] = None,
    memory: Optional[int] = None,
    cores: Optional[int] = None,
    rootfs: Optional[str] = None,
    password: Optional[str] = None,
    start: bool = False,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    if not vmid:
        vmid = _get_next_vmid(client)

    if ostemplate:
        _validate_ostemplate(client, resolved_node, ostemplate)

    params: dict[str, Any] = {
        "vmid": vmid,
        "ostemplate": ostemplate,
    }
    if hostname:
        params["hostname"] = hostname
    if memory is not None:
        params["memory"] = memory
    if cores is not None:
        params["cores"] = cores
    if rootfs:
        params["rootfs"] = rootfs
    if password:
        params["password"] = password
    if start:
        params["start"] = 1

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc.post, elevated=True, **params
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC container {vmid} created on {resolved_node}. UPID: {upid}"


@confirm_required
def start_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).status.start.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} start initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def stop_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).status.stop.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} stop initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def shutdown_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).status.shutdown.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} shutdown initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def reboot_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).status.reboot.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} reboot initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def delete_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).delete, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} deleted on {resolved_node}. UPID: {upid}"


@confirm_required
def configure_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    cores: Optional[int] = None,
    memory: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    params: dict[str, Any] = {}
    if cores is not None:
        params["cores"] = cores
    if memory is not None:
        params["memory"] = memory

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).config.put, elevated=True, **params
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} configured on {resolved_node}. UPID: {upid}"


@confirm_required
def create_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    name: Optional[str] = None,
    memory: Optional[int] = None,
    cores: Optional[int] = None,
    sockets: Optional[int] = None,
    disk_size: Optional[str] = None,
    storage: Optional[str] = None,
    iso: Optional[str] = None,
    ostype: Optional[str] = None,
    net0: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    if not vmid:
        vmid = _get_next_vmid(client)

    params: dict[str, Any] = {"vmid": vmid}
    if name:
        params["name"] = name
    if memory is not None:
        params["memory"] = memory
    if cores is not None:
        params["cores"] = cores
    if sockets is not None:
        params["sockets"] = sockets
    if disk_size:
        params["disk"] = disk_size
    if storage:
        params["storage"] = storage
    if iso:
        params["cdrom"] = f"{iso},media=cdrom"
    if ostype:
        params["ostype"] = ostype
    if net0:
        params["net0"] = net0

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu.post, elevated=True, **params
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} created on {resolved_node}. UPID: {upid}"


@confirm_required
def start_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).status.start.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} start initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def stop_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).status.stop.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} stop initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def shutdown_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).status.shutdown.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} shutdown initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def reboot_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).status.reboot.post, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} reboot initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def delete_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).delete, elevated=True
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} deleted on {resolved_node}. UPID: {upid}"


@confirm_required
def clone_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    newid: Optional[int] = None,
    name: Optional[str] = None,
    full: bool = True,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    if not newid:
        newid = _get_next_vmid(client)

    params: dict[str, Any] = {"newid": newid}
    if name:
        params["name"] = name
    params["full"] = 1 if full else 0

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).clone.post, elevated=True, **params
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} clone initiated → {newid} on {resolved_node}. UPID: {upid}"


@confirm_required
def migrate_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    target: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    params: dict[str, Any] = {"target": target}

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).migrate.post, elevated=True, **params
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} migration to {target} initiated. UPID: {upid}"


@confirm_required
def configure_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    cores: Optional[int] = None,
    memory: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    params: dict[str, Any] = {}
    if cores is not None:
        params["cores"] = cores
    if memory is not None:
        params["memory"] = memory

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).config.put, elevated=True, **params
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} configured on {resolved_node}. UPID: {upid}"
