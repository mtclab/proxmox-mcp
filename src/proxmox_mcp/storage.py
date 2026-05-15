from __future__ import annotations

import os
from typing import Any, Optional

from proxmox_mcp.utils import confirm_required, format_bytes


def list_isos(
    client: Any,
    node: Optional[str] = None,
    storage: str = "local",
) -> str:
    resolved_node = client.resolve_node(node)
    result = client.safe_api_call(
        client.monitor_client.nodes(resolved_node).storage(storage).content.get,
        content="iso",
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"\U0001f4bf **ISOs on {storage} ({resolved_node})**\n"]
    for item in result:
        volid = item.get("volid", "unknown")
        size = item.get("size", 0)
        lines.append(f"   • {volid} — {format_bytes(size) if size else 'N/A'}")
    if not result:
        lines.append("   No ISOs found.")
    return "\n".join(lines)


@confirm_required
def upload_iso(
    client: Any,
    node: Optional[str] = None,
    storage: str = "local",
    filepath: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    if not filepath:
        raise ValueError("filepath is required for ISO upload")
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        result = client.upload(
            node=resolved_node,
            storage=storage,
            content_type="iso",
            file_obj=f,
            filename=filename,
            elevated=True,
        )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"ISO upload initiated to {resolved_node}/{storage}. UPID: {upid}"
