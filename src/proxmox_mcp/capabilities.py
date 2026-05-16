from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.utils import validate_node_name


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


def list_cpu_models(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).capabilities.qemu.cpu.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🖥️ **QEMU CPU Models on {resolved_node}**\n"]
    for model in result:
        name = model.get("name", "unknown")
        model_type = model.get("type", "")
        lines.append(f"   • **{name}**")
        if model_type:
            lines.append(f"     Type: {model_type}")
    if not result:
        lines.append("   No CPU models found.")
    return "\n".join(lines)


def list_cpu_flags(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).capabilities.qemu("cpu-flags").get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🖥️ **QEMU CPU Flags on {resolved_node}**\n"]
    for flag in result:
        name = flag.get("name", "unknown")
        flag_type = flag.get("type", "")
        lines.append(f"   • **{name}**")
        if flag_type:
            lines.append(f"     Type: {flag_type}")
    if not result:
        lines.append("   No CPU flags found.")
    return "\n".join(lines)


def list_machine_types(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).capabilities.qemu.machines.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🖥️ **QEMU Machine Types on {resolved_node}**\n"]
    for machine in result:
        if isinstance(machine, str):
            lines.append(f"   • **{machine}**")
        else:
            name = machine.get("id", machine.get("name", "unknown"))
            mtype = machine.get("type", "")
            version = machine.get("version", "")
            lines.append(f"   • **{name}**")
            if mtype:
                lines.append(f"     Type: {mtype}")
            if version:
                lines.append(f"     Version: {version}")
    if not result:
        lines.append("   No machine types found.")
    return "\n".join(lines)


def list_capabilities(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).capabilities.get,
    )
    lines = [f"🖥️ **Node Capabilities: {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, list):
        for entry in result:
            lines.append(f"   • {entry}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def list_capabilities_qemu(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).capabilities.qemu.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🖥️ **QEMU Capabilities on {resolved_node}**\n"]
    for entry in result:
        name = entry.get("name", entry.get("id", "unknown"))
        lines.append(f"   • {name}")
    if not result:
        lines.append("   No QEMU capabilities found.")
    return "\n".join(lines)


def get_capability_qemu_migrations(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).capabilities.qemu.migration.get,
    )
    lines = [f"🖥️ **QEMU Migration Capabilities on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)
