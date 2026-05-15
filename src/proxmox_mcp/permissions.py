from __future__ import annotations

from typing import Any

from proxmox_mcp.utils import confirm_required


def _api(client: Any) -> Any:
    return client.get_client(elevated=client.config.allow_elevated)


def list_acl(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).access.acl.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["\U0001f510 **ACL Rules**\n"]
    for rule in result:
        path = rule.get("path", "?")
        users = rule.get("users", rule.get("ugid", "?"))
        roles = rule.get("roles", "?")
        propagate = rule.get("propagate", 1)
        lines.append(f"   • Path: {path}")
        lines.append(f"     Users: {users} | Roles: {roles} | Propagate: {propagate}")
    if not result:
        lines.append("   No ACL rules found.")
    return "\n".join(lines)


@confirm_required
def set_acl(
    client: Any,
    users: str = "",
    roles: str = "",
    path: str = "",
    propagate: bool = True,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not users:
        raise ValueError("users is required for ACL creation")
    if not roles:
        raise ValueError("roles is required for ACL creation")
    if not path:
        raise ValueError("path is required for ACL creation")
    params: dict[str, Any] = {
        "users": users,
        "roles": roles,
        "path": path,
    }
    if not propagate:
        params["propagate"] = 0
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.access.acl.put,
        elevated=True,
        **params,
    )
    return f"ACL set: users={users!r} roles={roles!r} path={path!r} propagate={propagate}"


@confirm_required
def delete_acl(
    client: Any,
    users: str = "",
    roles: str = "",
    path: str = "",
    propagate: bool = True,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not users:
        raise ValueError("users is required for ACL deletion")
    if not roles:
        raise ValueError("roles is required for ACL deletion")
    if not path:
        raise ValueError("path is required for ACL deletion")
    params: dict[str, Any] = {
        "users": users,
        "roles": roles,
        "path": path,
        "delete": 1,
    }
    if not propagate:
        params["propagate"] = 0
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.access.acl.put,
        elevated=True,
        **params,
    )
    return f"ACL deleted: users={users!r} roles={roles!r} path={path!r}"


def list_roles(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).access.roles.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["\U0001f511 **Roles**\n"]
    for role in result:
        roleid = role.get("roleid", "unknown")
        privs = role.get("privs", "")
        lines.append(f"   • **{roleid}** — {privs}")
    if not result:
        lines.append("   No roles found.")
    return "\n".join(lines)


def list_users(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).access.users.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["\U0001f464 **Users**\n"]
    for user in result:
        userid = user.get("userid", "unknown")
        enabled = user.get("enable", 1)
        status = "enabled" if enabled else "disabled"
        lines.append(f"   • **{userid}** [{status}]")
    if not result:
        lines.append("   No users found.")
    return "\n".join(lines)


def list_tokens(client: Any, userid: str = "") -> str:
    if not userid:
        raise ValueError("userid is required for token listing")
    result = client.safe_api_call(
        _api(client).access.users(userid).token.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = [f"\U0001f511 **API Tokens for {userid}**\n"]
    for token in result:
        tokenid = token.get("id", token.get("tokenid", "unknown"))
        privsep = token.get("privsep", 1)
        comment = token.get("comment", "")
        lines.append(f"   • **{tokenid}** (privsep: {privsep})")
        if comment:
            lines.append(f"     {comment}")
    if not result:
        lines.append("   No tokens found.")
    return "\n".join(lines)
