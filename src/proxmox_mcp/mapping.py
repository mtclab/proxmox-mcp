from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required


def _api(client: Any) -> Any:
    return client.get_client(elevated=False)


def list_pci_mappings(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).cluster.mapping.pci.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🖥️ **PCI Mappings**\n"]
    for mapping in result:
        mid = mapping.get("id", "unknown")
        mtype = mapping.get("type", "unknown")
        lines.append(f"   • **{mid}** — type: {mtype}")
        description = mapping.get("description", mapping.get("comment", ""))
        if description:
            lines.append(f"     {description}")
    if not result:
        lines.append("   No PCI mappings found.")
    return "\n".join(lines)


@confirm_required
def create_pci_mapping(
    client: Any,
    id: str = "",
    description: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for PCI mapping creation")
    params: dict[str, Any] = {"id": id}
    if description is not None:
        params["description"] = description
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.pci.post,
        elevated=True,
        **params,
    )
    return f"PCI mapping {id!r} created"


def get_pci_mapping(client: Any, id: str = "") -> str:
    if not id:
        raise ValueError("id is required")
    result = client.safe_api_call(
        _api(client).cluster.mapping.pci(id).get,
    )
    lines = [f"🖥️ **PCI Mapping: {id}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_pci_mapping(
    client: Any,
    id: str = "",
    description: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for PCI mapping update")
    params: dict[str, Any] = {}
    if description is not None:
        params["description"] = description
    params.update(kwargs)
    if not params:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.pci(id).put,
        elevated=True,
        **params,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in params.items())
    return f"PCI mapping {id!r} updated: {opts}"


@confirm_required
def delete_pci_mapping(
    client: Any,
    id: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for PCI mapping deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.pci(id).delete,
        elevated=True,
    )
    return f"PCI mapping {id!r} deleted"


def list_usb_mappings(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).cluster.mapping.usb.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["🔌 **USB Mappings**\n"]
    for mapping in result:
        mid = mapping.get("id", "unknown")
        mtype = mapping.get("type", "unknown")
        lines.append(f"   • **{mid}** — type: {mtype}")
        description = mapping.get("description", mapping.get("comment", ""))
        if description:
            lines.append(f"     {description}")
    if not result:
        lines.append("   No USB mappings found.")
    return "\n".join(lines)


@confirm_required
def create_usb_mapping(
    client: Any,
    id: str = "",
    description: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for USB mapping creation")
    params: dict[str, Any] = {"id": id}
    if description is not None:
        params["description"] = description
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.usb.post,
        elevated=True,
        **params,
    )
    return f"USB mapping {id!r} created"


def get_usb_mapping(client: Any, id: str = "") -> str:
    if not id:
        raise ValueError("id is required")
    result = client.safe_api_call(
        _api(client).cluster.mapping.usb(id).get,
    )
    lines = [f"🔌 **USB Mapping: {id}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def update_usb_mapping(
    client: Any,
    id: str = "",
    description: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for USB mapping update")
    params: dict[str, Any] = {}
    if description is not None:
        params["description"] = description
    params.update(kwargs)
    if not params:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.usb(id).put,
        elevated=True,
        **params,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in params.items())
    return f"USB mapping {id!r} updated: {opts}"


@confirm_required
def delete_usb_mapping(
    client: Any,
    id: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for USB mapping deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.usb(id).delete,
        elevated=True,
    )
    return f"USB mapping {id!r} deleted"


def mapping_index(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).cluster.mapping.get,
    )
    type_labels = {"pci": "PCI", "usb": "USB", "dir": "Directory"}
    lines = ["\U0001f4bb **Mapping Index**\n"]
    if isinstance(result, dict):
        for key, entries in sorted(result.items()):
            label = type_labels.get(key, key)
            if isinstance(entries, list):
                for entry in entries:
                    mid = entry.get("id", "unknown") if isinstance(entry, dict) else str(entry)
                    lines.append(f"   • {mid} ({label})")
            else:
                lines.append(f"   • {entries} ({label})")
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                mid = entry.get("id", "unknown")
                mtype = type_labels.get(entry.get("type", ""), entry.get("type", "unknown"))
                lines.append(f"   • {mid} ({mtype})")
            else:
                lines.append(f"   • {entry}")
    if not result:
        lines.append("   No mappings found.")
    return "\n".join(lines)


def list_dir_mappings(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).cluster.mapping.dir.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["\U0001f4c1 **Directory Mappings**\n"]
    for mapping in result:
        mid = mapping.get("id", "unknown")
        description = mapping.get("description", mapping.get("comment", ""))
        lines.append(f"   • **{mid}**")
        if description:
            lines.append(f"     {description}")
    if not result:
        lines.append("   No directory mappings found.")
    return "\n".join(lines)


def get_dir_mapping(client: Any, id: str = "") -> str:
    if not id:
        raise ValueError("id is required")
    result = client.safe_api_call(
        _api(client).cluster.mapping.dir(id).get,
    )
    lines = [f"\U0001f4c1 **Directory Mapping: {id}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def create_dir_mapping(
    client: Any,
    id: str = "",
    description: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for directory mapping creation")
    params: dict[str, Any] = {"id": id}
    if description is not None:
        params["description"] = description
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.dir.post,
        elevated=True,
        **params,
    )
    return f"Directory mapping {id!r} created"


@confirm_required
def update_dir_mapping(
    client: Any,
    id: str = "",
    description: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for directory mapping update")
    params: dict[str, Any] = {}
    if description is not None:
        params["description"] = description
    params.update(kwargs)
    if not params:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.dir(id).put,
        elevated=True,
        **params,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in params.items())
    return f"Directory mapping {id!r} updated: {opts}"


@confirm_required
def delete_dir_mapping(
    client: Any,
    id: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for directory mapping deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.mapping.dir(id).delete,
        elevated=True,
    )
    return f"Directory mapping {id!r} deleted"
