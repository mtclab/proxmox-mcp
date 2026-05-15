from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import format_bytes, format_uptime


def list_nodes(client: Any) -> str:
    nodes = client.safe_api_call(client.monitor_client.nodes.get)
    if not isinstance(nodes, list):
        nodes = [nodes]
    lines = ["🖥️  **Proxmox Cluster Nodes**\n"]
    for n in nodes:
        status = "🟢" if n.get("status") in ("online",) or n.get("state") == "online" else "🔴"
        name = n.get("node", "unknown")
        cpu = n.get("cpu", 0) * 100
        mem = n.get("mem", 0)
        maxmem = n.get("maxmem", 0)
        uptime = n.get("uptime", 0)
        lines.append(f"{status} **{name}**")
        lines.append(f"   • CPU: {cpu:.1f}%")
        lines.append(f"   • Memory: {format_bytes(mem)} / {format_bytes(maxmem)}")
        lines.append(f"   • Uptime: {format_uptime(uptime)}")
        lines.append("")
    return "\n".join(lines)


def node_status(client: Any, node: Optional[str] = None) -> str:
    node = client.resolve_node(node)
    result = client.safe_api_call(client.monitor_client.nodes(node).status.get)
    lines = [f"📊 **Node Status: {node}**\n"]
    if isinstance(result, dict):
        lines.append(f"   • Kernel: {result.get('kversion', 'N/A')}")
        lines.append(f"   • Uptime: {format_uptime(result.get('uptime', 0))}")
        lines.append(f"   • CPU: {result.get('cpu', 0) * 100:.1f}%")
        mem = result.get('memory', {})
        if isinstance(mem, dict):
            lines.append(f"   • Memory: {format_bytes(mem.get('used', 0))} / {format_bytes(mem.get('total', 0))}")
        lines.append(f"   • PVE Version: {result.get('version', 'N/A')}")
    return "\n".join(lines)


def list_vms(client: Any, node: Optional[str] = None) -> str:
    result = client.safe_api_call(client.monitor_client.cluster.resources.get, type="vm")
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["💻 **Virtual Machines**\n"]
    for vm in result:
        status_icon = "🟢" if vm.get("status") == "running" else "🔴"
        vmtype = "📦" if vm.get("type") == "lxc" else "🖥️"
        name = vm.get("name", vm.get("vmid", "unknown"))
        vmid = vm.get("vmid", "?")
        n = vm.get("node", "?")
        lines.append(f"{status_icon} {vmtype} **{name}** (ID: {vmid})")
        lines.append(f"   • Node: {n}")
        lines.append(f"   • Status: {vm.get('status', 'unknown')}")
        if vm.get("cpu"):
            lines.append(f"   • CPU: {vm['cpu'] * 100:.1f}%")
        if vm.get("mem"):
            lines.append(f"   • Memory: {format_bytes(vm['mem'])}")
        lines.append("")
    return "\n".join(lines)


def vm_info(client: Any, node: Optional[str] = None, vmid: Optional[int] = None, name: Optional[str] = None) -> str:
    resolved_node, resolved_vmid = client.resolve_guest(name or str(vmid), node)
    status_data = client.safe_api_call(
        client.monitor_client.nodes(resolved_node).qemu(resolved_vmid).status.current.get
    )
    config_data = client.safe_api_call(
        client.monitor_client.nodes(resolved_node).qemu(resolved_vmid).config.get
    )
    lines = [f"🖥️ **VM {resolved_vmid} on {resolved_node}**\n"]
    if isinstance(status_data, dict):
        lines.append(f"   • Status: {status_data.get('status', 'unknown')}")
        lines.append(f"   • Uptime: {format_uptime(status_data.get('uptime', 0))}")
        lines.append(f"   • CPU: {status_data.get('cpu', 0) * 100:.1f}%")
        mem = status_data.get("mem", 0)
        maxmem = status_data.get("maxmem", 0)
        lines.append(f"   • Memory: {format_bytes(mem)} / {format_bytes(maxmem)}")
    if isinstance(config_data, dict):
        lines.append(f"   • Cores: {config_data.get('cores', 'N/A')}")
        lines.append(f"   • Name: {config_data.get('name', 'N/A')}")
        lines.append(f"   • OS: {config_data.get('ostype', 'N/A')}")
    return "\n".join(lines)


def list_lxc(client: Any, node: Optional[str] = None) -> str:
    result = client.safe_api_call(client.monitor_client.cluster.resources.get, type="lxc")
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["📦 **LXC Containers**\n"]
    for ct in result:
        status_icon = "🟢" if ct.get("status") == "running" else "🔴"
        name = ct.get("name", ct.get("vmid", "unknown"))
        vmid = ct.get("vmid", "?")
        n = ct.get("node", "?")
        lines.append(f"{status_icon} 📦 **{name}** (ID: {vmid})")
        lines.append(f"   • Node: {n}")
        lines.append(f"   • Status: {ct.get('status', 'unknown')}")
        if ct.get("cpu"):
            lines.append(f"   • CPU: {ct['cpu'] * 100:.1f}%")
        if ct.get("mem"):
            lines.append(f"   • Memory: {format_bytes(ct['mem'])}")
        lines.append("")
    return "\n".join(lines)


def lxc_info(client: Any, node: Optional[str] = None, vmid: Optional[int] = None, name: Optional[str] = None) -> str:
    resolved_node, resolved_vmid = client.resolve_guest(name or str(vmid), node)
    status_data = client.safe_api_call(client.monitor_client.nodes(resolved_node).lxc(resolved_vmid).status.current.get)
    config_data = client.safe_api_call(client.monitor_client.nodes(resolved_node).lxc(resolved_vmid).config.get)
    lines = [f"📦 **LXC {resolved_vmid} on {resolved_node}**\n"]
    if isinstance(status_data, dict):
        lines.append(f"   • Status: {status_data.get('status', 'unknown')}")
        lines.append(f"   • Uptime: {format_uptime(status_data.get('uptime', 0))}")
        lines.append(f"   • CPU: {status_data.get('cpu', 0) * 100:.1f}%")
        mem = status_data.get("mem", 0)
        maxmem = status_data.get("maxmem", 0)
        lines.append(f"   • Memory: {format_bytes(mem)} / {format_bytes(maxmem)}")
    if isinstance(config_data, dict):
        lines.append(f"   • Hostname: {config_data.get('hostname', 'N/A')}")
        lines.append(f"   • Cores: {config_data.get('cores', 'N/A')}")
    return "\n".join(lines)


def list_storage(client: Any, node: Optional[str] = None) -> str:
    result = client.safe_api_call(client.monitor_client.storage.get)
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["💾 **Storage Pools**\n"]
    for s in result:
        status_icon = "🟢" if s.get("active", 0) else "🔴"
        name = s.get("storage", "unknown")
        stype = s.get("type", "?")
        used = s.get("used", 0)
        total = s.get("total", 0) or 1
        content = s.get("content", "")
        lines.append(f"{status_icon} **{name}** ({stype})")
        lines.append(f"   • Content: {content}")
        if total > 1:
            lines.append(f"   • Usage: {format_bytes(used)} / {format_bytes(total)}")
        lines.append("")
    return "\n".join(lines)


def storage_content(client: Any, node: Optional[str] = None, storage: str = "local") -> str:
    node = client.resolve_node(node)
    result = client.safe_api_call(client.monitor_client.nodes(node).storage(storage).content.get)
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"📁 **Storage: {storage} on {node}**\n"]
    for item in result:
        volid = item.get("volid", "unknown")
        ctype = item.get("content", "?")
        size = item.get("size", 0)
        lines.append(f"   • {volid} ({ctype}) — {format_bytes(size) if size else 'N/A'}")
    return "\n".join(lines)


def list_tasks(client: Any, node: Optional[str] = None, limit: int = 50) -> str:
    result = client.safe_api_call(client.monitor_client.cluster.tasks.get)
    if not isinstance(result, list):
        result = [result] if result else []
    result = result[:limit]
    lines = [f"📋 **Recent Tasks** (showing {len(result)})\n"]
    for t in result:
        upid = t.get("upid", "?")
        status = t.get("status", "?")
        status_icon = "✅" if status == "OK" else "❌" if status else "⏳"
        lines.append(f"{status_icon} {upid}")
    return "\n".join(lines)


def task_status(client: Any, upid: str) -> str:
    parts = upid.split(":")
    node = parts[1] if len(parts) > 1 else client.resolve_node()
    result = client.safe_api_call(client.monitor_client.nodes(node).tasks(upid).status.get)
    lines = [f"📋 **Task: {upid}**\n"]
    if isinstance(result, dict):
        lines.append(f"   • Status: {result.get('status', 'unknown')}")
        exitstatus = result.get("exitstatus", "")
        if exitstatus:
            lines.append(f"   • Exit Status: {exitstatus}")
        lines.append(f"   • User: {result.get('user', 'N/A')}")
        lines.append(f"   • Node: {result.get('node', 'N/A')}")
    return "\n".join(lines)


def node_metrics(client: Any, node: Optional[str] = None, timeframe: str = "hour", cf: str = "AVERAGE") -> str:
    node = client.resolve_node(node)
    result = client.safe_api_call(client.monitor_client.nodes(node).rrddata.get, timeframe=timeframe, cf=cf)
    if not isinstance(result, list):
        return f"No metrics data available for node {node}"
    lines = [f"📈 **Node Metrics: {node}** ({timeframe})\n"]
    for entry in result[:5]:
        lines.append(f"   • {entry.get('time', '?')}")
    lines.append(f"   ... {len(result)} data points total")
    return "\n".join(lines)


def vm_metrics(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    name: Optional[str] = None,
    timeframe: str = "hour",
) -> str:
    resolved_node, resolved_vmid = client.resolve_guest(name or str(vmid), node)
    result = client.safe_api_call(
        client.monitor_client.nodes(resolved_node).qemu(resolved_vmid).rrddata.get, timeframe=timeframe
    )
    if not isinstance(result, list):
        return f"No metrics data available for VM {resolved_vmid}"
    lines = [f"📈 **VM {resolved_vmid} Metrics** ({timeframe})\n"]
    lines.append(f"   {len(result)} data points available")
    return "\n".join(lines)


def lxc_metrics(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    name: Optional[str] = None,
    timeframe: str = "hour",
) -> str:
    resolved_node, resolved_vmid = client.resolve_guest(name or str(vmid), node)
    result = client.safe_api_call(
        client.monitor_client.nodes(resolved_node).lxc(resolved_vmid).rrddata.get, timeframe=timeframe
    )
    if not isinstance(result, list):
        return f"No metrics data available for LXC {resolved_vmid}"
    lines = [f"📈 **LXC {resolved_vmid} Metrics** ({timeframe})\n"]
    lines.append(f"   {len(result)} data points available")
    return "\n".join(lines)


def list_bridges(client: Any, node: Optional[str] = None) -> str:
    node = client.resolve_node(node)
    result = client.safe_api_call(client.monitor_client.nodes(node).network.get)
    if not isinstance(result, list):
        result = [result] if result else []
    bridges = [iface for iface in result if iface.get("type") == "bridge" or iface.get("iface", "").startswith("vmbr")]
    lines = [f"🌐 **Network Bridges on {node}**\n"]
    for b in bridges:
        name = b.get("iface", "unknown")
        ports = b.get("bridge_ports", "none")
        lines.append(f"   • {name} — ports: {ports}")
    return "\n".join(lines)


def list_network(client: Any, node: Optional[str] = None) -> str:
    node = client.resolve_node(node)
    result = client.safe_api_call(client.monitor_client.nodes(node).network.get)
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **Network Interfaces on {node}**\n"]
    for iface in result:
        name = iface.get("iface", "unknown")
        itype = iface.get("type", "unknown")
        addr = iface.get("address", "")
        lines.append(f"   • {name} ({itype}) — {addr}")
    return "\n".join(lines)
