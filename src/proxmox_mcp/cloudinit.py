from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.utils import confirm_required


@confirm_required
def set_cloudinit(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    ciuser: Optional[str] = None,
    cipassword: Optional[str] = None,
    ipconfig0: Optional[str] = None,
    sshkeys: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    params: dict[str, Any] = {}
    if ciuser:
        params["ciuser"] = ciuser
    if cipassword:
        params["cipassword"] = cipassword
    if ipconfig0:
        params["ipconfig0"] = ipconfig0
    if sshkeys:
        params["sshkeys"] = sshkeys

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).config.put, elevated=True, **params
    )
    upid = result if isinstance(result, str) else result.get("data", result)
    return f"Cloud-init configured for VM {vmid} on {resolved_node}. UPID: {upid}"


@confirm_required
def exec_vm(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    command: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    if not command:
        raise ValueError("command is required for guest execution")

    params: dict[str, Any] = {"command": command}

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).qemu(vmid).agent("exec").post, elevated=True, **params
    )
    pid = result if isinstance(result, str) else result.get("data", result)
    return f"Command executed in VM {vmid} on {resolved_node}. PID: {pid}"


@confirm_required
def exec_lxc(
    client: Any,
    node: Optional[str] = None,
    vmid: Optional[int] = None,
    command: Optional[str] = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)

    if not command:
        raise ValueError("command is required for guest execution")

    params: dict[str, Any] = {"command": command}

    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.nodes(resolved_node).lxc(vmid).exec.post, elevated=True, **params
    )
    pid = result if isinstance(result, str) else result.get("data", result)
    return f"Command executed in LXC {vmid} on {resolved_node}. PID: {pid}"
