from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.utils import validate_node_name


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


async def list_pci(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).hardware.pci.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🔌 **PCI Devices on {resolved_node}**\n"]
    for dev in result:
        pciid = dev.get("id", dev.get("pciid", "unknown"))
        device_name = dev.get("device_name", dev.get("class", ""))
        vendor = dev.get("vendor_name", dev.get("vendor", ""))
        subsystem = dev.get("subsystem_name", "")
        iommu = dev.get("iommu_group", "")
        lines.append(f"   • **{pciid}**")
        if device_name:
            lines.append(f"     Device: {device_name}")
        if vendor:
            lines.append(f"     Vendor: {vendor}")
        if subsystem:
            lines.append(f"     Subsystem: {subsystem}")
        if iommu:
            lines.append(f"     IOMMU Group: {iommu}")
    if not result:
        lines.append("   No PCI devices found.")
    return "\n".join(lines)


async def list_usb(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).hardware.usb.get,
        elevated=True,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🔌 **USB Devices on {resolved_node}**\n"]
    for dev in result:
        usbid = dev.get("id", dev.get("usbid", "unknown"))
        device_name = dev.get("product", dev.get("product_name", ""))
        vendor = dev.get("vendor", dev.get("vendor_name", ""))
        busnum = dev.get("busnum", "")
        devnum = dev.get("devnum", "")
        port = dev.get("port", "")
        lines.append(f"   • **{usbid}**")
        if device_name:
            lines.append(f"     Product: {device_name}")
        if vendor:
            lines.append(f"     Vendor: {vendor}")
        if port:
            lines.append(f"     Port: {port}")
        if busnum and devnum:
            lines.append(f"     Bus/Dev: {busnum}/{devnum}")
    if not result:
        lines.append("   No USB devices found.")
    return "\n".join(lines)


async def get_pci_device(client: ProxmoxClient, node: Optional[str] = None, pciid: str = "") -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not pciid:
        raise ValueError("pciid is required")
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).hardware.pci(pciid).get,
    )
    lines = [f"🔌 **PCI Device: {pciid} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, val in sorted(result.items()):
            lines.append(f"   • {key}: {val}")
    if not isinstance(result, dict) or not result:
        lines.append("   No data returned.")
    return "\n".join(lines)


async def list_pci_mdev(client: ProxmoxClient, node: Optional[str] = None, pciid: str = "") -> str:
    resolved_node = await client.resolve_node(node)
    validate_node_name(resolved_node)
    if not pciid:
        raise ValueError("pciid is required")
    result = await client.safe_api_call(
        _api(client).nodes(resolved_node).hardware.pci(pciid).mdev.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🔌 **MDEV Types for {pciid} on {resolved_node}**\n"]
    for mdev in result:
        mtype = mdev.get("type", "unknown")
        desc = mdev.get("description", "")
        available = mdev.get("available", "")
        lines.append(f"   • **{mtype}**")
        if desc:
            lines.append(f"     {desc}")
        if available:
            lines.append(f"     Available: {available}")
    if not result:
        lines.append("   No mediated device types found.")
    return "\n".join(lines)
