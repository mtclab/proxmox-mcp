from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required, validate_node_name, validate_vmid


def _api(client: Any) -> Any:
    return client.get_client(elevated=False)


@confirm_required
def vm_vnc_proxy(
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
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).vncproxy.post, elevated=True,
    )
    lines = [f"\U0001f5a5 **VNC Proxy: VM {vmid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def vm_spice_proxy(
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
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).spiceproxy.post, elevated=True,
    )
    lines = [f"\U0001f5a5 **SPICE Proxy: VM {vmid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def vm_termproxy(
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
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).termproxy.post, elevated=True,
    )
    lines = [f"\U0001f4bb **Terminal Proxy: VM {vmid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def lxc_vnc_proxy(
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
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).vncproxy.post, elevated=True,
    )
    lines = [f"\U0001f5a5 **VNC Proxy: CT {vmid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def lxc_termproxy(
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
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).termproxy.post, elevated=True,
    )
    lines = [f"\U0001f4bb **Terminal Proxy: CT {vmid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def node_vncshell(
    client: Any,
    node: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).vncshell.post, elevated=True,
    )
    lines = [f"\U0001f5a5 **VNC Shell: {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def node_spiceshell(
    client: Any,
    node: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).spiceshell.post, elevated=True,
    )
    lines = [f"\U0001f5a5 **SPICE Shell: {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def node_termproxy(
    client: Any,
    node: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).termproxy.post, elevated=True,
    )
    lines = [f"\U0001f4bb **Terminal Proxy: {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


@confirm_required
def lxc_spice_proxy(
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
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).spiceproxy.post, elevated=True,
    )
    lines = [f"\U0001f5a5 **SPICE Proxy: CT {vmid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def lxc_vnc_websocket(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    validate_vmid(vmid)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).lxc(vmid).vncwebsocket.get,
    )
    lines = [f"\U0001f5a5 **VNC WebSocket: CT {vmid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in sorted(result.items()):
            lines.append(f"   • {key}: {val}")
    else:
        lines.append(str(result))
    return "\n".join(lines)
