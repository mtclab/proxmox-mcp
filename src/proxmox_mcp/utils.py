from __future__ import annotations

import functools
from typing import Any, Callable


def confirm_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        confirm = kwargs.get("confirm", False)
        if isinstance(confirm, str):
            confirm = confirm.lower() in ("true", "1", "yes")
        if not confirm:
            raise ValueError(
                f"Operation {func.__name__!r} requires confirm=true to execute. "
                "This is a destructive operation — pass confirm=true to proceed."
            )
        return func(*args, **kwargs)

    return wrapper


def resolve_node_for(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if "node" not in kwargs or kwargs["node"] is None:
            from proxmox_mcp.client import ProxmoxClient

            client = kwargs.get("client") or args[0] if args else None
            if isinstance(client, ProxmoxClient):
                kwargs["node"] = client.resolve_node()
        return func(*args, **kwargs)

    return wrapper


def format_bytes(value: int | float) -> str:
    if value < 0:
        return f"{value} B"
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if abs(value) < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} EiB"


def format_uptime(seconds: int) -> str:
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def format_error(exc: Exception) -> str:
    msg = str(exc)
    if hasattr(exc, "response") and hasattr(exc.response, "text"):
        msg = f"{msg}: {exc.response.text}"
    return msg
