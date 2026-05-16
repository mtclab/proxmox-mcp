from __future__ import annotations

import logging
from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.utils import confirm_required, validate_iface_name

logger = logging.getLogger(__name__)


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


async def _is_management_interface(client: ProxmoxClient, node: str, iface: str) -> bool:
    if iface == "vmbr0":
        return True
    try:
        host = client.config.host
        result = await client.safe_api_call(client.get_client(elevated=False).nodes(node).network.get)
        if isinstance(result, list):
            for ent in result:
                if ent.get("iface") == iface:
                    addr = ent.get("address", "")
                    if addr and host in addr:
                        return True
    except Exception:
        logger.warning("Could not check if %s is management interface", iface)
    return False


async def _apply_network(client: ProxmoxClient, node: str, iface: str = "") -> None:
    elevated = client.get_client(elevated=True)
    await client.safe_api_call(
        elevated.nodes(node).network.put,
        elevated=True,
    )


async def list_network(
    client: ProxmoxClient,
    node: Optional[str] = None,
) -> str:
    resolved_node = await client.resolve_node(node)
    result = await client.safe_api_call(_api(client).nodes(resolved_node).network.get)
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
async def create_network(
    client: ProxmoxClient,
    node: Optional[str] = None,
    iface: str = "",
    type: str = "bridge",
    address: Optional[str] = None,
    netmask: Optional[str] = None,
    gateway: Optional[str] = None,
    bridge_ports: Optional[str] = None,
    confirm: bool = False,
    apply: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    if not iface:
        raise ValueError("iface is required for network interface creation")
    validate_iface_name(iface)
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
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).network.post,
        elevated=True,
        **params,
    )
    if result is None:
        upid = "staged"
    elif isinstance(result, str):
        upid = result
    elif isinstance(result, dict):
        upid = result.get("data", result)
    else:
        upid = result
    staged_suffix = " (changes staged, not yet applied)" if upid == "staged" else ""
    msg = f"Network interface {iface!r} creation initiated on {resolved_node}. UPID: {upid}{staged_suffix}"
    if apply:
        warnings: list[str] = []
        if await _is_management_interface(client, resolved_node, iface):
            warnings.append(" WARNING: Applying changes to management interface may disconnect the agent.")
        await _apply_network(client, resolved_node, iface)
        msg += " Network changes applied."
        msg += "".join(warnings)
    return msg


@confirm_required
async def update_network(
    client: ProxmoxClient,
    node: Optional[str] = None,
    iface: str = "",
    address: Optional[str] = None,
    netmask: Optional[str] = None,
    gateway: Optional[str] = None,
    confirm: bool = False,
    apply: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    if not iface:
        raise ValueError("iface is required for network interface update")
    validate_iface_name(iface)
    params: dict[str, Any] = {}
    if address:
        params["address"] = address
    if netmask:
        params["netmask"] = netmask
    if gateway:
        params["gateway"] = gateway
    elevated = client.get_client(elevated=True)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).network(iface).put,
        elevated=True,
        **params,
    )
    if result is None:
        upid = "staged"
    elif isinstance(result, str):
        upid = result
    elif isinstance(result, dict):
        upid = result.get("data", result)
    else:
        upid = result
    staged_suffix = " (changes staged, not yet applied)" if upid == "staged" else ""
    msg = f"Network interface {iface!r} update initiated on {resolved_node}. UPID: {upid}{staged_suffix}"
    if apply:
        warnings: list[str] = []
        if await _is_management_interface(client, resolved_node, iface):
            warnings.append(" WARNING: Applying changes to management interface may disconnect the agent.")
        await _apply_network(client, resolved_node, iface)
        msg += " Network changes applied."
        msg += "".join(warnings)
    return msg


@confirm_required
async def delete_network(
    client: ProxmoxClient,
    node: Optional[str] = None,
    iface: str = "",
    confirm: bool = False,
    apply: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    if not iface:
        raise ValueError("iface is required for network interface deletion")
    validate_iface_name(iface)
    elevated = client.get_client(elevated=True)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).network(iface).delete,
        elevated=True,
    )
    if result is None:
        upid = "staged"
    elif isinstance(result, str):
        upid = result
    elif isinstance(result, dict):
        upid = result.get("data", result)
    else:
        upid = result
    staged_suffix = " (changes staged, not yet applied)" if upid == "staged" else ""
    msg = f"Network interface {iface!r} deletion initiated on {resolved_node}. UPID: {upid}{staged_suffix}"
    if apply:
        warnings: list[str] = []
        if await _is_management_interface(client, resolved_node, iface):
            warnings.append(" WARNING: Applying changes to management interface may disconnect the agent.")
        await _apply_network(client, resolved_node, iface)
        msg += " Network changes applied."
        msg += "".join(warnings)
    return msg


@confirm_required
async def revert_network(
    client: ProxmoxClient,
    node: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    elevated = client.get_client(elevated=True)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).network.delete,
        elevated=True,
    )
    if result is None:
        upid = "staged"
    elif isinstance(result, str):
        upid = result
    elif isinstance(result, dict):
        upid = result.get("data", result)
    else:
        upid = result
    staged_suffix = " (changes staged, not yet applied)" if upid == "staged" else ""
    return f"Network changes reverted on {resolved_node}. UPID: {upid}{staged_suffix}"
