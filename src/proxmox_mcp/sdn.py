from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.utils import confirm_required, validate_node_name


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


def list_sdn_zones(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn.zones.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN Zones**\n"]
    for zone in result:
        name = zone.get("zone", "unknown")
        ztype = zone.get("type", "unknown")
        lines.append(f"   • **{name}** — type: {ztype}")
    if not result:
        lines.append("   No SDN zones found.")
    return "\n".join(lines)


def get_sdn_zone(client: ProxmoxClient, zone: str = "") -> str:
    if not zone:
        raise ValueError("zone is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.zones(zone).get,
    )
    lines = [f"🌐 **SDN Zone: {zone}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def create_sdn_zone(
    client: ProxmoxClient,
    zone: str = "",
    type: str = "",
    comment: Optional[str] = None,
    nodes: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not zone:
        raise ValueError("zone is required for SDN zone creation")
    if not type:
        raise ValueError("type is required for SDN zone creation")
    params: dict[str, Any] = {"zone": zone, "type": type}
    if comment is not None:
        params["comment"] = comment
    if nodes is not None:
        params["nodes"] = nodes
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.zones.post,
        elevated=True,
        **params,
    )
    return f"SDN zone {zone!r} created"


@confirm_required
def update_sdn_zone(
    client: ProxmoxClient,
    zone: str = "",
    comment: Optional[str] = None,
    nodes: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not zone:
        raise ValueError("zone is required for SDN zone update")
    params: dict[str, Any] = {}
    if comment is not None:
        params["comment"] = comment
    if nodes is not None:
        params["nodes"] = nodes
    params.update(kwargs)
    if not params:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.zones(zone).put,
        elevated=True,
        **params,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in params.items())
    return f"SDN zone {zone!r} updated: {opts}"


@confirm_required
def delete_sdn_zone(
    client: ProxmoxClient,
    zone: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not zone:
        raise ValueError("zone is required for SDN zone deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.zones(zone).delete,
        elevated=True,
    )
    return f"SDN zone {zone!r} deleted"


def list_sdn_vnets(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn.vnets.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN VNets**\n"]
    for vnet in result:
        name = vnet.get("vnet", "unknown")
        zone = vnet.get("zone", "")
        lines.append(f"   • **{name}** — zone: {zone}")
    if not result:
        lines.append("   No SDN VNets found.")
    return "\n".join(lines)


def get_sdn_vnet(client: ProxmoxClient, vnet: str = "") -> str:
    if not vnet:
        raise ValueError("vnet is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.vnets(vnet).get,
    )
    lines = [f"🌐 **SDN VNet: {vnet}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def create_sdn_vnet(
    client: ProxmoxClient,
    vnet: str = "",
    zone: str = "",
    comment: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet creation")
    if not zone:
        raise ValueError("zone is required for SDN VNet creation")
    params: dict[str, Any] = {"vnet": vnet, "zone": zone}
    if comment is not None:
        params["comment"] = comment
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets.post,
        elevated=True,
        **params,
    )
    return f"SDN VNet {vnet!r} created"


@confirm_required
def update_sdn_vnet(
    client: ProxmoxClient,
    vnet: str = "",
    comment: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet update")
    params: dict[str, Any] = {}
    if comment is not None:
        params["comment"] = comment
    params.update(kwargs)
    if not params:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).put,
        elevated=True,
        **params,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in params.items())
    return f"SDN VNet {vnet!r} updated: {opts}"


@confirm_required
def delete_sdn_vnet(
    client: ProxmoxClient,
    vnet: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).delete,
        elevated=True,
    )
    return f"SDN VNet {vnet!r} deleted"


def list_sdn_subnets(client: ProxmoxClient, vnet: str = "") -> str:
    if not vnet:
        raise ValueError("vnet is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.vnets(vnet).subnets.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN Subnets for VNet {vnet}**\n"]
    for subnet in result:
        name = subnet.get("subnet", "unknown")
        lines.append(f"   • **{name}**")
    if not result:
        lines.append("   No subnets found.")
    return "\n".join(lines)


@confirm_required
def create_sdn_subnet(
    client: ProxmoxClient,
    vnet: str = "",
    subnet: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN subnet creation")
    if not subnet:
        raise ValueError("subnet is required for SDN subnet creation")
    params: dict[str, Any] = {"subnet": subnet}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).subnets.post,
        elevated=True,
        **params,
    )
    return f"SDN subnet {subnet!r} created in VNet {vnet!r}"


@confirm_required
def delete_sdn_subnet(
    client: ProxmoxClient,
    vnet: str = "",
    subnet: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN subnet deletion")
    if not subnet:
        raise ValueError("subnet is required for SDN subnet deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).subnets(subnet).delete,
        elevated=True,
    )
    return f"SDN subnet {subnet!r} deleted from VNet {vnet!r}"


def list_sdn_controllers(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn.controllers.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN Controllers**\n"]
    for ctrl in result:
        name = ctrl.get("controller", "unknown")
        ctype = ctrl.get("type", "unknown")
        lines.append(f"   • **{name}** — type: {ctype}")
    if not result:
        lines.append("   No SDN controllers found.")
    return "\n".join(lines)


@confirm_required
def create_sdn_controller(
    client: ProxmoxClient,
    controller: str = "",
    type: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not controller:
        raise ValueError("controller is required for SDN controller creation")
    if not type:
        raise ValueError("type is required for SDN controller creation")
    params: dict[str, Any] = {"controller": controller, "type": type}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.controllers.post,
        elevated=True,
        **params,
    )
    return f"SDN controller {controller!r} created"


@confirm_required
def delete_sdn_controller(
    client: ProxmoxClient,
    controller: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not controller:
        raise ValueError("controller is required for SDN controller deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.controllers(controller).delete,
        elevated=True,
    )
    return f"SDN controller {controller!r} deleted"


def list_sdn_dns(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn.dns.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN DNS**\n"]
    for entry in result:
        name = entry.get("dns", "unknown")
        dtype = entry.get("type", "unknown")
        lines.append(f"   • **{name}** — type: {dtype}")
    if not result:
        lines.append("   No SDN DNS entries found.")
    return "\n".join(lines)


@confirm_required
def create_sdn_dns(
    client: ProxmoxClient,
    dns: str = "",
    type: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not dns:
        raise ValueError("dns is required for SDN DNS creation")
    if not type:
        raise ValueError("type is required for SDN DNS creation")
    params: dict[str, Any] = {"dns": dns, "type": type}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.dns.post,
        elevated=True,
        **params,
    )
    return f"SDN DNS {dns!r} created"


@confirm_required
def delete_sdn_dns(
    client: ProxmoxClient,
    dns: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not dns:
        raise ValueError("dns is required for SDN DNS deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.dns(dns).delete,
        elevated=True,
    )
    return f"SDN DNS {dns!r} deleted"


def list_sdn_ipams(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn.ipams.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN IPAMs**\n"]
    for entry in result:
        name = entry.get("ipam", entry.get("id", "unknown"))
        itype = entry.get("type", "unknown")
        lines.append(f"   • **{name}** — type: {itype}")
    if not result:
        lines.append("   No SDN IPAMs found.")
    return "\n".join(lines)


@confirm_required
def create_sdn_ipam(
    client: ProxmoxClient,
    ipam: str = "",
    type: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not ipam:
        raise ValueError("ipam is required for SDN IPAM creation")
    if not type:
        raise ValueError("type is required for SDN IPAM creation")
    params: dict[str, Any] = {"ipam": ipam, "type": type}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.ipams.post,
        elevated=True,
        **params,
    )
    return f"SDN IPAM {ipam!r} created"


@confirm_required
def delete_sdn_ipam(
    client: ProxmoxClient,
    ipam: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not ipam:
        raise ValueError("ipam is required for SDN IPAM deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.ipams(ipam).delete,
        elevated=True,
    )
    return f"SDN IPAM {ipam!r} deleted"


@confirm_required
def apply_sdn(
    client: ProxmoxClient,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.put,
        elevated=True,
    )
    return "SDN changes applied"


def list_node_sdn_zones(
    client: ProxmoxClient,
    node: Optional[str] = None,
) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).sdn.zones.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN Zones on {resolved_node}**\n"]
    for zone in result:
        name = zone.get("zone", "unknown")
        status = zone.get("status", "unknown")
        lines.append(f"   • **{name}** — status: {status}")
    if not result:
        lines.append("   No SDN zones found.")
    return "\n".join(lines)


def get_node_sdn_zone_status(
    client: ProxmoxClient,
    node: Optional[str] = None,
    zone: str = "",
) -> str:
    if not zone:
        raise ValueError("zone is required")
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).sdn.zones(zone).get,
    )
    lines = [f"🌐 **SDN Zone Status: {zone} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                for key, value in sorted(entry.items()):
                    lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


def get_sdn_ipam_status(client: ProxmoxClient, ipam: str = "") -> str:
    if not ipam:
        raise ValueError("ipam is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.ipams(ipam).status.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN IPAM Status: {ipam}**\n"]
    for entry in result:
        subnet = entry.get("subnet", entry.get("id", "unknown"))
        lines.append(f"   • **{subnet}**")
        for key in ("gateway", "mask", "type"):
            if key in entry:
                lines.append(f"     {key}: {entry[key]}")
    if not result:
        lines.append("   No IPAM entries found.")
    return "\n".join(lines)


def list_sdn_fabrics(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn.fabrics.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN Fabrics**\n"]
    for entry in result:
        fabric = entry.get("fabric", entry.get("id", "unknown"))
        ftype = entry.get("type", "unknown")
        lines.append(f"   • **{fabric}** — type: {ftype}")
    if not result:
        lines.append("   No SDN fabrics found.")
    return "\n".join(lines)


def list_sdn_fabric_detail(client: ProxmoxClient, fabric: str = "") -> str:
    if not fabric:
        raise ValueError("fabric is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.fabrics.fabric(fabric).get,
    )
    lines = [f"🌐 **SDN Fabric: {fabric}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def create_sdn_fabric(
    client: ProxmoxClient,
    fabric: str = "",
    type: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not fabric:
        raise ValueError("fabric is required for SDN fabric creation")
    if not type:
        raise ValueError("type is required for SDN fabric creation")
    params: dict[str, Any] = {"fabric": fabric, "type": type}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.fabrics.fabric.post,
        elevated=True,
        **params,
    )
    return f"SDN fabric {fabric!r} created"


@confirm_required
def delete_sdn_fabric(
    client: ProxmoxClient,
    id: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for SDN fabric deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.fabrics.fabric(id).delete,
        elevated=True,
    )
    return f"SDN fabric {id!r} deleted"


@confirm_required
def update_sdn_fabric(
    client: ProxmoxClient,
    id: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for SDN fabric update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.fabrics.fabric(id).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN fabric {id!r} updated: {opts}"


def list_sdn_prefix_lists(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn("prefix-lists").get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN Prefix Lists**\n"]
    for entry in result:
        name = entry.get("name", entry.get("id", "unknown"))
        lines.append(f"   • **{name}**")
    if not result:
        lines.append("   No SDN prefix lists found.")
    return "\n".join(lines)


@confirm_required
def create_sdn_prefix_list(
    client: ProxmoxClient,
    id: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for SDN prefix list creation")
    params: dict[str, Any] = {"id": id}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("prefix-lists").post,
        elevated=True,
        **params,
    )
    return f"SDN prefix list {id!r} created"


@confirm_required
def delete_sdn_prefix_list(
    client: ProxmoxClient,
    id: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for SDN prefix list deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("prefix-lists")(id).delete,
        elevated=True,
    )
    return f"SDN prefix list {id!r} deleted"


def list_sdn_route_maps(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn("route-maps").entries.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN Route Maps**\n"]
    for entry in result:
        name = entry.get("id", entry.get("route-map", "unknown"))
        lines.append(f"   • **{name}**")
    if not result:
        lines.append("   No SDN route maps found.")
    return "\n".join(lines)


@confirm_required
def acquire_sdn_lock(
    client: ProxmoxClient,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.cluster.sdn.lock.post,
        elevated=True,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"SDN lock acquired. UPID: {upid}"


@confirm_required
def release_sdn_lock(
    client: ProxmoxClient,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.lock.delete,
        elevated=True,
    )
    return "SDN lock released"


@confirm_required
def sdn_rollback(
    client: ProxmoxClient,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.rollback.post,
        elevated=True,
    )
    return "SDN rollback initiated"


def get_sdn_ipam(client: ProxmoxClient, ipam: str = "") -> str:
    if not ipam:
        raise ValueError("ipam is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.ipams(ipam).get,
    )
    lines = [f"🌐 **SDN IPAM: {ipam}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_sdn_ipam(
    client: ProxmoxClient,
    ipam: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not ipam:
        raise ValueError("ipam is required for SDN IPAM update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.ipams(ipam).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN IPAM {ipam!r} updated: {opts}"


def get_sdn_dns(client: ProxmoxClient, dns: str = "") -> str:
    if not dns:
        raise ValueError("dns is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.dns(dns).get,
    )
    lines = [f"🌐 **SDN DNS: {dns}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_sdn_dns(
    client: ProxmoxClient,
    dns: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not dns:
        raise ValueError("dns is required for SDN DNS update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.dns(dns).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN DNS {dns!r} updated: {opts}"


def get_sdn_controller(client: ProxmoxClient, controller: str = "") -> str:
    if not controller:
        raise ValueError("controller is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.controllers(controller).get,
    )
    lines = [f"🌐 **SDN Controller: {controller}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_sdn_controller(
    client: ProxmoxClient,
    controller: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not controller:
        raise ValueError("controller is required for SDN controller update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.controllers(controller).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN controller {controller!r} updated: {opts}"


def list_sdn_fabric_nodes(client: ProxmoxClient, fabric_id: str = "") -> str:
    if not fabric_id:
        raise ValueError("fabric_id is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.fabrics.node(fabric_id).get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN Fabric Nodes for {fabric_id}**\n"]
    for entry in result:
        nid = entry.get("node", entry.get("id", "unknown"))
        lines.append(f"   • **{nid}**")
    if not result:
        lines.append("   No fabric nodes found.")
    return "\n".join(lines)


@confirm_required
def add_sdn_fabric_node(
    client: ProxmoxClient,
    fabric_id: str = "",
    node: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not fabric_id:
        raise ValueError("fabric_id is required for SDN fabric node creation")
    if not node:
        raise ValueError("node is required for SDN fabric node creation")
    params: dict[str, Any] = {"node": node}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.fabrics.node(fabric_id).post,
        elevated=True,
        **params,
    )
    return f"SDN fabric node {node!r} added to fabric {fabric_id!r}"


def get_sdn_fabric_node(client: ProxmoxClient, fabric_id: str = "", node_id: str = "") -> str:
    if not fabric_id:
        raise ValueError("fabric_id is required")
    if not node_id:
        raise ValueError("node_id is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.fabrics.node(fabric_id)(node_id).get,
    )
    lines = [f"🌐 **SDN Fabric Node: {node_id} in {fabric_id}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_sdn_fabric_node(
    client: ProxmoxClient,
    fabric_id: str = "",
    node_id: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not fabric_id:
        raise ValueError("fabric_id is required for SDN fabric node update")
    if not node_id:
        raise ValueError("node_id is required for SDN fabric node update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.fabrics.node(fabric_id)(node_id).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN fabric node {node_id!r} in {fabric_id!r} updated: {opts}"


@confirm_required
def remove_sdn_fabric_node(
    client: ProxmoxClient,
    fabric_id: str = "",
    node_id: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not fabric_id:
        raise ValueError("fabric_id is required for SDN fabric node removal")
    if not node_id:
        raise ValueError("node_id is required for SDN fabric node removal")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.fabrics.node(fabric_id)(node_id).delete,
        elevated=True,
    )
    return f"SDN fabric node {node_id!r} removed from fabric {fabric_id!r}"


@confirm_required
def create_sdn_vnet_ip(
    client: ProxmoxClient,
    vnet: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet IP creation")
    params: dict[str, Any] = {}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).ips.post,
        elevated=True,
        **params,
    )
    return f"SDN VNet IP created in {vnet!r}"


@confirm_required
def update_sdn_vnet_ip(
    client: ProxmoxClient,
    vnet: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet IP update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).ips.put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN VNet IP updated in {vnet!r}: {opts}"


@confirm_required
def delete_sdn_vnet_ip(
    client: ProxmoxClient,
    vnet: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet IP deletion")
    params: dict[str, Any] = {}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).ips.delete,
        elevated=True,
        **params,
    )
    return f"SDN VNet IP deleted from {vnet!r}"


def get_sdn_vnet_firewall_options(client: ProxmoxClient, vnet: str = "") -> str:
    if not vnet:
        raise ValueError("vnet is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.vnets(vnet).firewall.options.get,
    )
    lines = [f"🌐 **SDN VNet Firewall Options: {vnet}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def set_sdn_vnet_firewall_options(
    client: ProxmoxClient,
    vnet: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet firewall options")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to set")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).firewall.options.put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN VNet {vnet!r} firewall options set: {opts}"


def list_sdn_vnet_firewall_rules(client: ProxmoxClient, vnet: str = "") -> str:
    if not vnet:
        raise ValueError("vnet is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.vnets(vnet).firewall.rules.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN VNet Firewall Rules: {vnet}**\n"]
    for rule in result:
        pos = rule.get("pos", "?")
        action = rule.get("action", "?")
        lines.append(f"   • pos {pos}: action={action}")
    if not result:
        lines.append("   No firewall rules found.")
    return "\n".join(lines)


@confirm_required
def create_sdn_vnet_firewall_rule(
    client: ProxmoxClient,
    vnet: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet firewall rule creation")
    params: dict[str, Any] = {}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).firewall.rules.post,
        elevated=True,
        **params,
    )
    return f"SDN VNet firewall rule created in {vnet!r}"


@confirm_required
def delete_sdn_vnet_firewall_rule(
    client: ProxmoxClient,
    vnet: str = "",
    pos: int = 0,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet firewall rule deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).firewall.rules(str(pos)).delete,
        elevated=True,
    )
    return f"SDN VNet firewall rule pos {pos} deleted from {vnet!r}"


def get_sdn_vnet_firewall_rule(client: ProxmoxClient, vnet: str = "", pos: int = 0) -> str:
    if not vnet:
        raise ValueError("vnet is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn.vnets(vnet).firewall.rules(str(pos)).get,
    )
    lines = [f"🌐 **SDN VNet Firewall Rule: {vnet} pos {pos}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_sdn_vnet_firewall_rule(
    client: ProxmoxClient,
    vnet: str = "",
    pos: int = 0,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not vnet:
        raise ValueError("vnet is required for SDN VNet firewall rule update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn.vnets(vnet).firewall.rules(str(pos)).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN VNet firewall rule pos {pos} in {vnet!r} updated: {opts}"


def list_prefix_list_entries(client: ProxmoxClient, id: str = "") -> str:
    if not id:
        raise ValueError("id is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn("prefix-lists")(id).entries.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN Prefix List Entries: {id}**\n"]
    for entry in result:
        seq = entry.get("seq", entry.get("url_seq", "?"))
        lines.append(f"   • seq {seq}")
    if not result:
        lines.append("   No prefix list entries found.")
    return "\n".join(lines)


@confirm_required
def create_prefix_list_entry(
    client: ProxmoxClient,
    id: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for prefix list entry creation")
    params: dict[str, Any] = {}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("prefix-lists")(id).entries.post,
        elevated=True,
        **params,
    )
    return f"SDN prefix list entry created in {id!r}"


@confirm_required
def delete_prefix_list_entry(
    client: ProxmoxClient,
    id: str = "",
    url_seq: int = 0,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for prefix list entry deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("prefix-lists")(id).entries(str(url_seq)).delete,
        elevated=True,
    )
    return f"SDN prefix list entry {url_seq} deleted from {id!r}"


def get_prefix_list_entry(client: ProxmoxClient, id: str = "", url_seq: int = 0) -> str:
    if not id:
        raise ValueError("id is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn("prefix-lists")(id).entries(str(url_seq)).get,
    )
    lines = [f"🌐 **SDN Prefix List Entry: {id} seq {url_seq}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_prefix_list_entry(
    client: ProxmoxClient,
    id: str = "",
    url_seq: int = 0,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for prefix list entry update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("prefix-lists")(id).entries(str(url_seq)).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN prefix list entry {url_seq} in {id!r} updated: {opts}"


def list_route_map_entries(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn("route-maps").entries.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🌐 **SDN Route Map Entries**\n"]
    for entry in result:
        rid = entry.get("id", entry.get("route-map", "unknown"))
        lines.append(f"   • **{rid}**")
    if not result:
        lines.append("   No route map entries found.")
    return "\n".join(lines)


@confirm_required
def create_route_map_entry(
    client: ProxmoxClient,
    route_map_id: str = "",
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not route_map_id:
        raise ValueError("route_map_id is required for route map entry creation")
    params: dict[str, Any] = {"id": route_map_id}
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("route-maps").entries.post,
        elevated=True,
        **params,
    )
    return f"SDN route map entry {route_map_id!r} created"


def get_route_map_entry(client: ProxmoxClient, route_map_id: str = "") -> str:
    if not route_map_id:
        raise ValueError("route_map_id is required")
    result = client.safe_api_call(
        _api(client).cluster.sdn("route-maps").entries(route_map_id).get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN Route Map Entry: {route_map_id}**\n"]
    for entry in result:
        order = entry.get("order", entry.get("id", "?"))
        lines.append(f"   • order {order}")
    if not result:
        lines.append("   No entries found.")
    return "\n".join(lines)


@confirm_required
def delete_route_map_entry(
    client: ProxmoxClient,
    route_map_id: str = "",
    order: int = 0,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not route_map_id:
        raise ValueError("route_map_id is required for route map entry deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("route-maps").entries(route_map_id)("entry")(str(order)).delete,
        elevated=True,
    )
    return f"SDN route map entry {route_map_id!r} order {order} deleted"


@confirm_required
def update_route_map_entry(
    client: ProxmoxClient,
    route_map_id: str = "",
    order: int = 0,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not route_map_id:
        raise ValueError("route_map_id is required for route map entry update")
    if not kwargs:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.sdn("route-maps").entries(route_map_id)("entry")(str(order)).put,
        elevated=True,
        **kwargs,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"SDN route map entry {route_map_id!r} order {order} updated: {opts}"


def sdn_dry_run(client: ProxmoxClient) -> str:
    result = client.safe_api_call(
        _api(client).cluster.sdn("dry-run").get,
    )
    lines = ["🌐 **SDN Dry-Run**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                for key, value in sorted(entry.items()):
                    lines.append(f"   • {key}: {value}")
            else:
                lines.append(f"   • {entry}")
    else:
        lines.append(f"   {result}")
    return "\n".join(lines)


def get_node_sdn_vnet(
    client: ProxmoxClient,
    node: Optional[str] = None,
    vnet: str = "",
) -> str:
    if not vnet:
        raise ValueError("vnet is required")
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).sdn.vnets(vnet).get,
    )
    lines = [f"🌐 **SDN VNet: {vnet} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                for key, value in sorted(entry.items()):
                    lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


def list_node_sdn_zone_bridges(
    client: ProxmoxClient,
    node: Optional[str] = None,
    zone: str = "",
) -> str:
    if not zone:
        raise ValueError("zone is required")
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).sdn.zones(zone).bridges.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🌐 **SDN Zone Bridges: {zone} on {resolved_node}**\n"]
    for bridge in result:
        name = bridge.get("bridge", bridge.get("id", "unknown"))
        lines.append(f"   • **{name}**")
    if not result:
        lines.append("   No bridges found.")
    return "\n".join(lines)


def get_node_sdn_zone_content(
    client: ProxmoxClient,
    node: Optional[str] = None,
    zone: str = "",
) -> str:
    if not zone:
        raise ValueError("zone is required")
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).sdn.zones(zone).content.get,
    )
    lines = [f"🌐 **SDN Zone Content: {zone} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                for key, value in sorted(entry.items()):
                    lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


def get_node_sdn_zone_ip_vrf(
    client: ProxmoxClient,
    node: Optional[str] = None,
    zone: str = "",
) -> str:
    if not zone:
        raise ValueError("zone is required")
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).sdn.zones(zone)("ip-vrf").get,
    )
    lines = [f"🌐 **SDN Zone IP-VRF: {zone} on {resolved_node}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                for key, value in sorted(entry.items()):
                    lines.append(f"   • {key}: {value}")
    return "\n".join(lines)
