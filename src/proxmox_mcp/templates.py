from __future__ import annotations

import logging
import os
from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.exceptions import ProxmoxPermissionError
from proxmox_mcp.utils import confirm_required, format_bytes, validate_storage_name, validate_url


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


async def list_templates(client: ProxmoxClient, node: Optional[str] = None) -> str:
    node = await client.resolve_node(node)
    result = await client.safe_api_call(
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


async def list_storage_templates(client: ProxmoxClient, node: Optional[str] = None, storage: str = "local") -> str:
    node = await client.resolve_node(node)
    validate_storage_name(storage)
    result = await client.safe_api_call(
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
async def download_template(
    client: ProxmoxClient,
    node: Optional[str] = None,
    storage: str = "local",
    url: str = "",
    filename: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_storage_name(storage)
    if not url:
        raise ValueError("url is required for template download. Use list_templates to find available template URLs.")
    validate_url(url)
    params: dict[str, Any] = {
        "content": "vztmpl",
        "url": url,
    }
    if filename:
        params["filename"] = filename
    elevated = client.get_client(elevated=True)
    result = await client.safe_api_call(
        elevated.nodes(resolved_node).storage(storage).download_url.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Template download initiated on {resolved_node}/{storage}. UPID: {upid}"


@confirm_required
async def upload_template(
    client: ProxmoxClient,
    node: Optional[str] = None,
    storage: str = "local",
    filepath: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = await client.resolve_node(node)
    validate_storage_name(storage)
    if not filepath:
        raise ValueError("filepath is required for template upload")
    allowed_dir = client.config.upload_dir
    if allowed_dir is None:
        logging.warning("PROXMOX_UPLOAD_DIR not set; file path validation is disabled")
    else:
        os.makedirs(allowed_dir, exist_ok=True)
        real_path = os.path.realpath(filepath)
        real_dir = os.path.realpath(allowed_dir)
        if not real_path.startswith(real_dir + os.sep) and real_path != real_dir:
            raise ProxmoxPermissionError(f"filepath {filepath!r} is outside allowed upload directory {allowed_dir!r}")
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
