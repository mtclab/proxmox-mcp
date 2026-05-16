from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required, validate_node_name


def _api(client: Any) -> Any:
    return client.get_client(elevated=False)


def task_log(
    client: Any,
    upid: str,
    node: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    parts = upid.split(":")
    resolved_node = node if node else (parts[1] if len(parts) > 1 else client.resolve_node())
    validate_node_name(resolved_node)
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).tasks(upid).log.get, **params
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"📋 **Task Log: {upid}** ({len(result)} entries)\n"]
    for entry in result[:50]:
        if isinstance(entry, dict):
            t = entry.get("t", entry.get("msg", str(entry)))
            n = entry.get("n", entry.get("line", ""))
            lines.append(f"   {n}: {t}" if n else f"   {t}")
        else:
            lines.append(f"   {entry}")
    if len(result) > 50:
        lines.append(f"   ... {len(result) - 50} more entries")
    return "\n".join(lines)


@confirm_required
def stop_task(
    client: Any,
    node: Optional[str] = None,
    upid: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not upid:
        raise ValueError("upid is required")
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).tasks(upid).delete, elevated=True
    )
    data = result if isinstance(result, str) else result.get("data", result)
    return f"Task {upid} stopped on {resolved_node}: {data}"
