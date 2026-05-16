from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.exceptions import ProxmoxNotFoundError
from proxmox_mcp.utils import confirm_required, validate_disk_size, validate_node_name, validate_vmid


def _api(client: Any) -> Any:
    return client.get_client(elevated=False)


def _get_next_vmid(client: Any) -> int:
    result = _api(client).cluster.nextid.get()
    return int(result)


def _validate_ostemplate(client: Any, node: str, ostemplate: str) -> None:
    storage_name = ostemplate.split(":")[0] if ":" in ostemplate else "local"
    try:
        content = client.safe_api_call(_api(client).nodes(node).storage(storage_name).content.get)
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
    validate_node_name(resolved_node)

    if not vmid:
        vmid = _get_next_vmid(client)
    validate_vmid(vmid)

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
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc.post, elevated=True, **params)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).status.start.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).status.stop.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).status.shutdown.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).status.reboot.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).delete, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    params: dict[str, Any] = {}
    if cores is not None:
        params["cores"] = cores
    if memory is not None:
        params["memory"] = memory

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).config.put, elevated=True, **params)
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
    validate_node_name(resolved_node)

    if not vmid:
        vmid = _get_next_vmid(client)
    validate_vmid(vmid)

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
        validated_size = validate_disk_size(disk_size)
        if storage:
            params["scsi0"] = f"{storage}:{validated_size}"
        else:
            params["scsi0"] = validated_size
    if storage and not disk_size:
        params["storage"] = storage
    if iso:
        if ":" in iso:
            params["cdrom"] = f"{iso},media=cdrom"
        elif storage:
            params["cdrom"] = f"{storage}:iso/{iso},media=cdrom"
        else:
            params["cdrom"] = f"{iso},media=cdrom"
    if ostype:
        params["ostype"] = ostype
    if net0:
        params["net0"] = net0

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu.post, elevated=True, **params)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).status.start.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).status.stop.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).status.shutdown.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).status.reboot.post, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).delete, elevated=True)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    if not newid:
        newid = _get_next_vmid(client)
    validate_vmid(newid)

    params: dict[str, Any] = {"newid": newid}
    if name:
        params["name"] = name
    params["full"] = 1 if full else 0

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).clone.post, elevated=True, **params)
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
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    params: dict[str, Any] = {"target": target}

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).migrate.post, elevated=True, **params)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} migration to {target} initiated. UPID: {upid}"


@confirm_required
def resize_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    disk: str = "rootfs",
    size: str = "+10G",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).resize.put, elevated=True, disk=disk, size=size
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} disk {disk} resize to {size} initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def suspend_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).status.suspend.post, elevated=True)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} suspend initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def resume_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).status.resume.post, elevated=True)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} resume initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def clone_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    newid: Optional[int] = None,
    hostname: Optional[str] = None,
    full: bool = True,
    target: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    if not newid:
        newid = _get_next_vmid(client)
    validate_vmid(newid)

    params: dict[str, Any] = {"newid": newid}
    if hostname:
        params["hostname"] = hostname
    params["full"] = 1 if full else 0
    if target:
        params["target"] = target

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).clone.post, elevated=True, **params)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} clone initiated → {newid} on {resolved_node}. UPID: {upid}"


@confirm_required
def migrate_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    target: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    params: dict[str, Any] = {"target": target}

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).migrate.post, elevated=True, **params)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} migration to {target} initiated. UPID: {upid}"


def lxc_interfaces(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(_api(client).nodes(resolved_node).lxc(vmid).interfaces.get)
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"**Interfaces for LXC {vmid} on {resolved_node}**\n"]
    for iface in result:
        name = iface.get("name", "unknown")
        hwaddr = iface.get("hwaddr", "")
        lines.append(f"  • **{name}** (HW: {hwaddr})")
        for addr in iface.get("ip-addresses", []):
            ip = addr.get("ip-address", "")
            prefix = addr.get("ip-prefix-length", "")
            proto = addr.get("ip-address-type", "")
            lines.append(f"    - {proto}: {ip}/{prefix}")
    if not result:
        lines.append("  No interfaces found.")
    return "\n".join(lines)


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
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    params: dict[str, Any] = {}
    if cores is not None:
        params["cores"] = cores
    if memory is not None:
        params["memory"] = memory

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).config.put, elevated=True, **params)
    if result is None:
        return f"VM {vmid} configuration updated on {resolved_node} (no pending changes)"
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} configured on {resolved_node}. UPID: {upid}"


@confirm_required
def resize_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    disk: str = "scsi0",
    size: str = "+10G",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).resize.put, elevated=True, disk=disk, size=size
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} disk {disk} resize to {size} initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def reset_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).status.reset.post, elevated=True)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} reset initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def suspend_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).status.suspend.post, elevated=True)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} suspend initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def resume_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).status.resume.post, elevated=True)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} resume initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def move_vm_disk(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    disk: str = "scsi0",
    storage: Optional[str] = None,
    format: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)

    params: dict[str, Any] = {"disk": disk, "storage": storage}
    if format:
        params["format"] = format

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).move_disk.post, elevated=True, **params)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} disk {disk} move to {storage} initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def convert_to_template(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).template.post, elevated=True)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} convert to template initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def convert_lxc_to_template(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).template.post, elevated=True)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} convert to template initiated on {resolved_node}. UPID: {upid}"


def lxc_migrate_preconditions(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(_api(client).nodes(resolved_node).lxc(vmid).migrate.get)
    lines = [f"**LXC {vmid} migrate preconditions on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"  • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def vm_migrate_preconditions(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(_api(client).nodes(resolved_node).qemu(vmid).migrate.get)
    lines = [f"**VM {vmid} migrate preconditions on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"  • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def lxc_feature_check(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    feature: str = "",
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(_api(client).nodes(resolved_node).lxc(vmid).feature.get, feature=feature)
    lines = [f"**LXC {vmid} feature check on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in result.items():
            lines.append(f"  • {key}: {value}")
    else:
        lines.append(f"  {result}")
    return "\n".join(lines)


def vm_feature_check(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    feature: str = "",
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(_api(client).nodes(resolved_node).qemu(vmid).feature.get, feature=feature)
    lines = [f"**VM {vmid} feature check on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in result.items():
            lines.append(f"  • {key}: {value}")
    else:
        lines.append(f"  {result}")
    return "\n".join(lines)


def vm_pending_config(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(_api(client).nodes(resolved_node).qemu(vmid).pending.get)
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"**VM {vmid} pending config on {resolved_node}**\n"]
    for item in result:
        key = item.get("key", "?")
        value = item.get("value", item.get("pending", ""))
        delete = item.get("delete", 0)
        if delete:
            lines.append(f"  • {key}: [DELETE]")
        else:
            lines.append(f"  • {key}: {value}")
    if not result:
        lines.append("  No pending changes.")
    return "\n".join(lines)


def lxc_pending_config(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(_api(client).nodes(resolved_node).lxc(vmid).pending.get)
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"**LXC {vmid} pending config on {resolved_node}**\n"]
    for item in result:
        key = item.get("key", "?")
        value = item.get("value", item.get("pending", ""))
        delete = item.get("delete", 0)
        if delete:
            lines.append(f"  • {key}: [DELETE]")
        else:
            lines.append(f"  • {key}: {value}")
    if not result:
        lines.append("  No pending changes.")
    return "\n".join(lines)


@confirm_required
def send_vm_key(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    key: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    if not key:
        raise ValueError("key is required")
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).sendkey.put, elevated=True, key=key)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Key {key!r} sent to VM {vmid} on {resolved_node}. UPID: {upid}"


@confirm_required
def vm_monitor_command(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    command: str = "",
    confirm: bool = False,
) -> str:
    """WARNING: This sends a raw QEMU monitor command directly to the VM.
    Extremely powerful and dangerous — can crash or corrupt the guest.
    Use with extreme caution.

    SECURITY: If PROXMOX_ALLOWED_MONITOR_COMMANDS is set, only commands
    starting with entries in that allowlist are permitted. If not set,
    all commands are allowed (require elevated token + confirm)."""
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    if not command:
        raise ValueError("command is required")
    if client.config.allowed_monitor_commands is not None:
        allowed = False
        for prefix in client.config.allowed_monitor_commands:
            if command.strip().lower().startswith(prefix.lower()):
                allowed = True
                break
        if not allowed:
            raise ValueError(
                f"Monitor command {command!r} is not in PROXMOX_ALLOWED_MONITOR_COMMANDS allowlist. "
                f"Allowed prefixes: {client.config.allowed_monitor_commands}"
            )
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).monitor.post, elevated=True, command=command)
    lines = [f"**VM {vmid} monitor command on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"  • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def unlink_vm_disk(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    idlist: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    if not idlist:
        raise ValueError("idlist is required (comma-separated disk IDs)")
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).unlink.put, elevated=True, idlist=idlist)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} disks {idlist!r} unlinked on {resolved_node}. UPID: {upid}"


@confirm_required
def vm_dbus_vmstate(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).dbus_vmstate.post,
        elevated=True,
    )
    return f"DBus VMstate triggered for VM {vmid} on {resolved_node}"


def vm_rrd(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
    ds: str = "cpu,maxmem,maxnet",
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    params: dict[str, Any] = {"timeframe": timeframe, "cf": cf, "ds": ds}
    try:
        result = client.safe_api_call(
            _api(client).nodes(resolved_node).qemu(vmid).rrd.get,
            **params,
        )
    except Exception as exc:
        return f"VM {vmid} RRD unavailable on {resolved_node} (use vm_rrddata for structured data): {exc}"
    if isinstance(result, dict) and "image" in result:
        img_data = result.get("image", "")
        return f"VM {vmid} RRD image returned ({len(img_data)} bytes) on {resolved_node}"
    lines = [f"📈 **VM {vmid} RRD on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, str):
        lines.append(f"   Binary/image data ({len(result)} bytes)")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def get_lxc_config(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    try:
        result = client.safe_api_call(_api(client).nodes(resolved_node).lxc(vmid).config.get)
    except ProxmoxNotFoundError:
        return f"LXC {vmid} not found on node {resolved_node}"
    lines = [f"**LXC {vmid} config on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in sorted(result.items()):
            lines.append(f"  • {key}: {val}")
    else:
        lines.append(str(result))
    if not isinstance(result, dict) or not result:
        lines.append("  No config data returned.")
    return "\n".join(lines)


def get_lxc_status(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    try:
        result = client.safe_api_call(_api(client).nodes(resolved_node).lxc(vmid).status.current.get)
    except ProxmoxNotFoundError:
        return f"LXC {vmid} not found on node {resolved_node}"
    lines = [f"**LXC {vmid} status on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in sorted(result.items()):
            lines.append(f"  • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def remote_migrate_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    target: Optional[str] = None,
    target_endpoint: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    if not target:
        raise ValueError("target is required for remote migration")
    if not target_endpoint:
        raise ValueError("target_endpoint is required for remote migration")
    params: dict[str, Any] = {"target": target, "target-endpoint": target_endpoint}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).remote_migrate.post, elevated=True, **params)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} remote migration to {target} via {target_endpoint} initiated. UPID: {upid}"


@confirm_required
def move_lxc_volume(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    volume: str = "rootfs",
    storage: Optional[str] = None,
    target_vmid: Optional[int] = None,
    target_volume: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    params: dict[str, Any] = {"volume": volume}
    if storage is not None:
        params["storage"] = storage
    if target_vmid is not None:
        params["target_vmid"] = target_vmid
    if target_volume is not None:
        params["target-volume"] = target_volume
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).move_volume.post, elevated=True, **params)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"LXC {vmid} volume {volume} move initiated on {resolved_node}. UPID: {upid}"


def lxc_rrddata(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    params: dict[str, Any] = {"timeframe": timeframe, "cf": cf}
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).lxc(vmid).rrddata.get,
        **params,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"📈 **LXC {vmid} RRDdata on {resolved_node} ({timeframe}/{cf})**\n"]
    for entry in result:
        if isinstance(entry, dict):
            ts = entry.get("time", "?")
            parts = [f"t={ts}"]
            for k, v in sorted(entry.items()):
                if k != "time":
                    parts.append(f"{k}={v}")
            lines.append(f"  • {' | '.join(parts)}")
        else:
            lines.append(f"  • {entry}")
    if not result:
        lines.append("  No data returned.")
    return "\n".join(lines)


def lxc_rrd(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
    ds: str = "cpu,maxmem,maxnet",
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    params: dict[str, Any] = {"timeframe": timeframe, "cf": cf, "ds": ds}
    try:
        result = client.safe_api_call(
            _api(client).nodes(resolved_node).lxc(vmid).rrd.get,
            **params,
        )
    except Exception as exc:
        return f"LXC {vmid} RRD unavailable on {resolved_node} (use lxc_rrddata for structured data): {exc}"
    if isinstance(result, dict) and "image" in result:
        img_data = result.get("image", "")
        return f"LXC {vmid} RRD image returned ({len(img_data)} bytes) on {resolved_node}"
    lines = [f"📈 **LXC {vmid} RRD on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, str):
        lines.append(f"   Binary/image data ({len(result)} bytes)")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def get_vm_config(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    current: bool = False,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    params: dict[str, Any] = {}
    if current:
        params["current"] = 1
    try:
        result = client.safe_api_call(_api(client).nodes(resolved_node).qemu(vmid).config.get, **params)
    except ProxmoxNotFoundError:
        return f"VM {vmid} not found on node {resolved_node}"
    lines = [f"**VM {vmid} config on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in sorted(result.items()):
            lines.append(f"  • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def _parse_kwargs(kwargs: Any) -> dict[str, Any]:
    import json

    if isinstance(kwargs, dict):
        return kwargs
    if isinstance(kwargs, str):
        try:
            parsed = json.loads(kwargs)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        try:
            return {k: v for k, v in (pair.split("=", 1) for pair in kwargs.split() if "=" in pair)}
        except ValueError:
            return {}
    return {}


@confirm_required
def update_vm_config(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    parsed = _parse_kwargs(kwargs)
    if not parsed:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).config.post, elevated=True, **parsed)
    if result is None:
        return f"VM {vmid} config updated on {resolved_node} (no pending changes)"
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} config updated on {resolved_node}. UPID: {upid}"


def vm_rrddata(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    timeframe: str = "hour",
    cf: str = "AVERAGE",
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    params: dict[str, Any] = {"timeframe": timeframe, "cf": cf}
    result = client.safe_api_call(_api(client).nodes(resolved_node).qemu(vmid).rrddata.get, **params)
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"📈 **VM {vmid} RRD data on {resolved_node} (timeframe={timeframe}, cf={cf})**\n"]
    for entry in result:
        if isinstance(entry, dict):
            parts = [f"{k}={v}" for k, v in sorted(entry.items())]
            lines.append(f"   • {' | '.join(parts)}")
        else:
            lines.append(f"   • {entry}")
    if not result:
        lines.append("   No data found.")
    return "\n".join(lines)


@confirm_required
def remote_migrate_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    target_address: Optional[str] = None,
    target_node: Optional[str] = None,
    target_storage: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    if not target_address:
        raise ValueError("target_address is required for remote migration")
    params: dict[str, Any] = {"target-address": target_address}
    if target_node:
        params["target-node"] = target_node
    if target_storage:
        params["target-storage"] = target_storage
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).qemu(vmid).remote_migrate.post, elevated=True, **params)
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"VM {vmid} remote migration to {target_address} initiated. UPID: {upid}"


@confirm_required
def lxc_sendkey(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    key: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    if not key:
        raise ValueError("key is required")
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(elevated.nodes(resolved_node).lxc(vmid).sendkey.put, elevated=True, key=key)
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Key {key!r} sent to LXC {vmid} on {resolved_node}. UPID: {upid}"
