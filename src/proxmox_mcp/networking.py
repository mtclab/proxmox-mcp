from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required


def list_network(
    client: Any,
    node: Optional[str] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    result = client.safe_api_call(
        client.monitor_client.nodes(resolved_node).network.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"\U0001f310 **Network Interfaces on {resolved_node}**\n"]
    for iface in result:
        name = iface.get("iface", "unknown")
        itype = iface.get("type", "unknown")
        addr = iface.get("address", "")
        netmask = iface.get("netmask", "")
        gateway = iface.get("gateway", "")
        active = iface.get("active", 0)
        status = "up" if active else "down"
        lines.append(f"   • **{name}** ({itype}) [{status}]")
        if addr:
            lines.append(f"     Address: {addr}/{netmask}" if netmask else f"     Address: {addr}")
        if gateway:
            lines.append(f"     Gateway: {gateway}")
    if not result:
        lines.append("   No interfaces found.")
    return "\n".join(lines)


@confirm_required
def create_network(
    client: Any,
    node: Optional[str] = None,
    iface: str = "",
    type: str = "bridge",
    address: Optional[str] = None,
    netmask: Optional[str] = None,
    gateway: Optional[str] = None,
    bridge_ports: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    if not iface:
        raise ValueError("iface is required for network interface creation")
    params: dict[str, Any] = {"iface": iface, "type": type}
    if address:
        params["address"] = address
    if netmask:
        params["netmask"] = netmask
    if gateway:
        params["gateway"] = gateway
    if bridge_ports:
        params["bridge_ports"] = bridge_ports
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).network.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Network interface {iface!r} creation initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def update_network(
    client: Any,
    node: Optional[str] = None,
    iface: str = "",
    address: Optional[str] = None,
    netmask: Optional[str] = None,
    gateway: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    if not iface:
        raise ValueError("iface is required for network interface update")
    params: dict[str, Any] = {}
    if address:
        params["address"] = address
    if netmask:
        params["netmask"] = netmask
    if gateway:
        params["gateway"] = gateway
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).network(iface).put,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Network interface {iface!r} update initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def delete_network(
    client: Any,
    node: Optional[str] = None,
    iface: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    if not iface:
        raise ValueError("iface is required for network interface deletion")
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).network(iface).delete,
        elevated=True,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Network interface {iface!r} deletion initiated on {resolved_node}. UPID: {upid}"
