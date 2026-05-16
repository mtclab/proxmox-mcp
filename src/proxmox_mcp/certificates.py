from __future__ import annotations

from typing import Any, Optional

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.utils import confirm_required, validate_node_name


def _api(client: ProxmoxClient) -> Any:
    return client.get_client(elevated=False)


def list_certificates(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).certificates.info.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🔓 **Certificates on {resolved_node}**\n"]
    for cert in result:
        filename = cert.get("filename", "unknown")
        subject = cert.get("subject", cert.get("Subject", ""))
        issuer = cert.get("issuer", cert.get("Issuer", ""))
        not_before = cert.get("notbefore", cert.get("NotBefore", ""))
        not_after = cert.get("notafter", cert.get("NotAfter", ""))
        fingerprint = cert.get("fingerprint", "")
        lines.append(f"   • **{filename}**")
        if subject:
            lines.append(f"     Subject: {subject}")
        if issuer:
            lines.append(f"     Issuer: {issuer}")
        if not_before:
            lines.append(f"     Not Before: {not_before}")
        if not_after:
            lines.append(f"     Not After: {not_after}")
        if fingerprint:
            lines.append(f"     Fingerprint: {fingerprint}")
    if not result:
        lines.append("   No certificates found.")
    return "\n".join(lines)


@confirm_required
def order_acme_certificate(
    client: ProxmoxClient,
    node: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            params[k] = v
    result = client.safe_api_call(
        elevated.nodes(resolved_node).certificates.acme.certificate.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"ACME certificate order initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def renew_acme_certificate(
    client: ProxmoxClient,
    node: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            params[k] = v
    result = client.safe_api_call(
        elevated.nodes(resolved_node).certificates.acme.certificate.put,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"ACME certificate renewal initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def revoke_certificate(
    client: ProxmoxClient,
    node: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            params[k] = v
    result = client.safe_api_call(
        elevated.nodes(resolved_node).certificates.acme.certificate.delete,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Certificate revocation initiated on {resolved_node}. UPID: {upid}"


@confirm_required
def upload_custom_certificate(
    client: ProxmoxClient,
    node: Optional[str] = None,
    certificates: Optional[str] = None,
    key: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    if not certificates or not key:
        raise ValueError("Both 'certificates' and 'key' are required for custom certificate upload")
    elevated = client.get_client(elevated=True)
    params = {"certificates": certificates, "key": key}
    for k, v in kwargs.items():
        if v is not None:
            params[k] = v
    result = client.safe_api_call(
        elevated.nodes(resolved_node).certificates.custom.post,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Custom certificate uploaded on {resolved_node}. UPID: {upid}"


@confirm_required
def delete_custom_certificate(
    client: ProxmoxClient,
    node: Optional[str] = None,
    confirm: bool = False,
    **kwargs: Any,
) -> str:
    client.raise_if_not_elevated()
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    elevated = client.get_client(elevated=True)
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            params[k] = v
    result = client.safe_api_call(
        elevated.nodes(resolved_node).certificates.custom.delete,
        elevated=True,
        **params,
    )
    upid = result if isinstance(result, str) else result.get("data", result) if isinstance(result, dict) else result
    return f"Custom certificate deleted on {resolved_node}. UPID: {upid}"


def list_acme_certs(client: ProxmoxClient, node: Optional[str] = None) -> str:
    resolved_node = client.resolve_node(node)
    validate_node_name(resolved_node)
    result = client.safe_api_call(
        _api(client).nodes(resolved_node).certificates.acme.get,
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"🔓 **ACME Certificates on {resolved_node}**\n"]
    for entry in result:
        if isinstance(entry, dict):
            name = entry.get("name", entry.get("id", "unknown"))
            lines.append(f"   • {name}")
            for key, value in sorted(entry.items()):
                if key not in ("name", "id"):
                    lines.append(f"     {key}: {value}")
        else:
            lines.append(f"   • {entry}")
    if not result:
        lines.append("   No ACME certificate entries found.")
    return "\n".join(lines)
