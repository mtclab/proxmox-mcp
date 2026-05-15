from __future__ import annotations

import os
from typing import Any, Optional

from proxmox_mcp.utils import confirm_required, format_bytes


def _api(client: Any) -> Any:
    return client.get_client(elevated=client.config.allow_elevated)


def list_templates(client: Any, node: Optional[str] = None) -> str:
    node = client.resolve_node(node)
    result = client.safe_api_call(
        _api(client).nodes(node).aplinfo.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"📋 **PVE Appliance Templates** (node: {node})\n"]
    for tmpl in result:
        name = tmpl.get("name", "unknown")
        version = tmpl.get("version", "")
        section = tmpl.get("section", "")
        location = tmpl.get("location", "")
        size = tmpl.get("size", 0)
        lines.append(f"   • **{name}** v{version} [{section}]")
        if size:
            lines.append(f"     Size: {format_bytes(size)} | {location}")
        elif location:
            lines.append(f"     {location}")
    if not result:
        lines.append("   No templates available.")
    return "\n".join(lines)


def list_storage_templates(client: Any, node: Optional[str] = None, storage: str = "local") -> str:
    node = client.resolve_node(node)
    result = client.safe_api_call(
        _api(client).nodes(node).storage(storage).content.get,
        content="vztmpl",
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"📦 **Downloaded Templates** ({storage} on {node})\n"]
    for item in result:
        volid = item.get("volid", "unknown")
        size = item.get("size", 0)
        lines.append(f"   • {volid} — {format_bytes(size) if size else 'N/A'}")
    if not result:
        lines.append("   No templates found in storage.")
    return "\n".join(lines)


@confirm_required
def download_template(
    client: Any,
    node: Optional[str] = None,
    storage: str = "local",
    url: str = "",
    filename: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    if not url:
        raise ValueError(
            "url is required for template download. "
            "Use list_templates to find available template URLs."
        )
    params: dict[str, Any] = {
        "content": "vztmpl",
        "url": url,
    }
    if filename:
        params["filename"] = filename
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).storage(storage).download_url.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Template download initiated on {resolved_node}/{storage}. UPID: {upid}"


@confirm_required
def upload_template(
    client: Any,
    node: Optional[str] = None,
    storage: str = "local",
    filepath: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    if not filepath:
        raise ValueError("filepath is required for template upload")
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        result = client.upload(
            node=resolved_node,
            storage=storage,
            content_type="vztmpl",
            file_obj=f,
            filename=filename,
            elevated=True,
        )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Template upload initiated to {resolved_node}/{storage}. UPID: {upid}"
