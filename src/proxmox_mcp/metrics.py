from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required


def _api(client: Any) -> Any:
    return client.get_client(elevated=False)


def list_metric_servers(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).cluster.metrics.server.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["📊 **Metric Servers**\n"]
    for server in result:
        sid = server.get("id", "unknown")
        stype = server.get("type", "unknown")
        server_addr = server.get("server", "N/A")
        lines.append(f"   • **{sid}** — type: {stype}, server: {server_addr}")
    if not result:
        lines.append("   No metric servers found.")
    return "\n".join(lines)


def get_metric_server(client: Any, id: str = "") -> str:
    if not id:
        raise ValueError("id is required")
    result = client.safe_api_call(
        _api(client).cluster.metrics.server(id).get,
    )
    lines = [f"📊 **Metric Server: {id}**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    return "\n".join(lines)


@confirm_required
def create_metric_server(
    client: Any,
    id: str = "",
    type: str = "graphite",
    server: Optional[str] = None,
    port: Optional[int] = None,
    comment: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for metric server creation")
    valid_types = {"graphite", "influxdb", "opentelemetry"}
    if type not in valid_types:
        raise ValueError(f"type must be one of {valid_types}, got {type!r}")
    params: dict[str, Any] = {"id": id, "type": type}
    if server is not None:
        params["server"] = server
    if port is not None:
        params["port"] = port
    if comment is not None:
        params["comment"] = comment
    params.update(kwargs)
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.metrics.server(id).post,
        elevated=True,
        **params,
    )
    return f"Metric server {id!r} ({type}) created"


@confirm_required
def update_metric_server(
    client: Any,
    id: str = "",
    server: Optional[str] = None,
    port: Optional[int] = None,
    comment: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for metric server update")
    params: dict[str, Any] = {}
    if server is not None:
        params["server"] = server
    if port is not None:
        params["port"] = port
    if comment is not None:
        params["comment"] = comment
    params.update(kwargs)
    if not params:
        raise ValueError("At least one parameter must be provided to update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.metrics.server(id).put,
        elevated=True,
        **params,
    )
    opts = ", ".join(f"{k}={v!r}" for k, v in params.items())
    return f"Metric server {id!r} updated: {opts}"


@confirm_required
def delete_metric_server(
    client: Any,
    id: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not id:
        raise ValueError("id is required for metric server deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.cluster.metrics.server(id).delete,
        elevated=True,
    )
    return f"Metric server {id!r} deleted"


def metrics_index(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).cluster.metrics.get,
    )
    lines = ["\U0001f4ca **Metrics Index**\n"]
    if isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)


def export_metrics(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).cluster.metrics.export.get,
    )
    lines = ["\U0001f4ca **Cluster Metrics Export**\n"]
    if isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                mid = entry.get("id", entry.get("metric", "unknown"))
                value = entry.get("value", "N/A")
                lines.append(f"   • {mid}: {value}")
            else:
                lines.append(f"   {entry}")
        if not result:
            lines.append("   No metrics data found.")
    elif isinstance(result, dict):
        for key, value in sorted(result.items()):
            lines.append(f"   • {key}: {value}")
    else:
        lines.append(str(result))
    return "\n".join(lines)
