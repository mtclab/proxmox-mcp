from __future__ import annotations

from typing import Any

from proxmox_mcp.exceptions import ProxmoxNotFoundError
from proxmox_mcp.utils import confirm_required


def _api(client: Any) -> Any:
    return client.get_client(elevated=False)


def list_acl(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).access.acl.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["\U0001f510 **ACL Rules**\n"]
    for rule in result:
        path = rule.get("path", "?")
        users = rule.get("userid", rule.get("ugid", "unknown"))
        roles = rule.get("roleid", rule.get("roles", "unknown"))
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
    try:
        client.safe_api_call(
            elevated.access.acl.put,
            elevated=True,
            **params,
        )
    except ProxmoxNotFoundError:
        return (
            f"ACL entry not found (may have been auto-removed with role deletion): "
            f"path={path!r} roles={roles!r} users={users!r}"
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


@confirm_required
def create_user(
    client: Any,
    userid: str = "",
    password: str = "",
    comment: str | None = None,
    email: str | None = None,
    firstname: str | None = None,
    lastname: str | None = None,
    enable: bool | None = None,
    expire: int | None = None,
    groups: str | None = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not userid:
        raise ValueError("userid is required for user creation")
    if not password:
        raise ValueError("password is required for user creation")
    params: dict[str, Any] = {"userid": userid, "password": password}
    if comment is not None:
        params["comment"] = comment
    if email is not None:
        params["email"] = email
    if firstname is not None:
        params["firstname"] = firstname
    if lastname is not None:
        params["lastname"] = lastname
    if enable is not None:
        params["enable"] = 1 if enable else 0
    if expire is not None:
        params["expire"] = expire
    if groups is not None:
        params["groups"] = groups
    elevated = client.get_client(elevated=True)
    client.safe_api_call(elevated.access.users.post, elevated=True, **params)
    return f"User {userid!r} created"


def get_user(client: Any, userid: str = "") -> str:
    if not userid:
        raise ValueError("userid is required")
    result = client.safe_api_call(
        _api(client).access.users(userid).get
    )
    lines = [f"\U0001f464 **User {userid}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    if not result:
        lines.append("   No data returned.")
    return "\n".join(lines)


@confirm_required
def update_user(
    client: Any,
    userid: str = "",
    comment: str | None = None,
    email: str | None = None,
    firstname: str | None = None,
    lastname: str | None = None,
    enable: bool | None = None,
    expire: int | None = None,
    groups: str | None = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not userid:
        raise ValueError("userid is required for user update")
    params: dict[str, Any] = {}
    if comment is not None:
        params["comment"] = comment
    if email is not None:
        params["email"] = email
    if firstname is not None:
        params["firstname"] = firstname
    if lastname is not None:
        params["lastname"] = lastname
    if enable is not None:
        params["enable"] = 1 if enable else 0
    if expire is not None:
        params["expire"] = expire
    if groups is not None:
        params["groups"] = groups
    elevated = client.get_client(elevated=True)
    client.safe_api_call(elevated.access.users(userid).put, elevated=True, **params)
    return f"User {userid!r} updated"


@confirm_required
def delete_user(
    client: Any,
    userid: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not userid:
        raise ValueError("userid is required for user deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(elevated.access.users(userid).delete, elevated=True)
    return f"User {userid!r} deleted"


@confirm_required
def create_role(
    client: Any,
    roleid: str = "",
    privs: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not roleid:
        raise ValueError("roleid is required for role creation")
    if not privs:
        raise ValueError("privs is required for role creation")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.access.roles.post, elevated=True, roleid=roleid, privs=privs,
    )
    return f"Role {roleid!r} created with privileges: {privs}"


def get_role(client: Any, roleid: str = "") -> str:
    if not roleid:
        raise ValueError("roleid is required")
    result = client.safe_api_call(
        _api(client).access.roles(roleid).get
    )
    lines = [f"\U0001f511 **Role {roleid}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    if not result:
        lines.append("   No data returned.")
    return "\n".join(lines)


@confirm_required
def update_role(
    client: Any,
    roleid: str = "",
    privs: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not roleid:
        raise ValueError("roleid is required for role update")
    if not privs:
        raise ValueError("privs is required for role update")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.access.roles(roleid).put, elevated=True, privs=privs,
    )
    return f"Role {roleid!r} updated with privileges: {privs}"


@confirm_required
def delete_role(
    client: Any,
    roleid: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not roleid:
        raise ValueError("roleid is required for role deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(elevated.access.roles(roleid).delete, elevated=True)
    return f"Role {roleid!r} deleted"


@confirm_required
def create_token(
    client: Any,
    userid: str = "",
    tokenid: str = "",
    comment: str | None = None,
    privsep: bool | None = None,
    expire: int | None = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not userid:
        raise ValueError("userid is required for token creation")
    if not tokenid:
        raise ValueError("tokenid is required for token creation")
    params: dict[str, Any] = {}
    if comment is not None:
        params["comment"] = comment
    if privsep is not None:
        params["privsep"] = 1 if privsep else 0
    if expire is not None:
        params["expire"] = expire
    elevated = client.get_client(elevated=True)
    result = client.safe_api_call(
        elevated.access.users(userid).token(tokenid).post, elevated=True, **params,
    )
    lines = [f"\U0001f511 **Token {userid}!{tokenid} created**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    return "\n".join(lines)


def get_token(client: Any, userid: str = "", tokenid: str = "") -> str:
    if not userid:
        raise ValueError("userid is required")
    if not tokenid:
        raise ValueError("tokenid is required")
    result = client.safe_api_call(
        _api(client).access.users(userid).token(tokenid).get
    )
    lines = [f"\U0001f511 **Token {userid}!{tokenid}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    if not result:
        lines.append("   No data returned.")
    return "\n".join(lines)


@confirm_required
def update_token(
    client: Any,
    userid: str = "",
    tokenid: str = "",
    comment: str | None = None,
    privsep: bool | None = None,
    expire: int | None = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not userid:
        raise ValueError("userid is required for token update")
    if not tokenid:
        raise ValueError("tokenid is required for token update")
    params: dict[str, Any] = {}
    if comment is not None:
        params["comment"] = comment
    if privsep is not None:
        params["privsep"] = 1 if privsep else 0
    if expire is not None:
        params["expire"] = expire
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.access.users(userid).token(tokenid).put, elevated=True, **params,
    )
    return f"Token {userid}!{tokenid} updated"


@confirm_required
def delete_token(
    client: Any,
    userid: str = "",
    tokenid: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not userid:
        raise ValueError("userid is required for token deletion")
    if not tokenid:
        raise ValueError("tokenid is required for token deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(
        elevated.access.users(userid).token(tokenid).delete, elevated=True,
    )
    return f"Token {userid}!{tokenid} deleted"


def list_groups(client: Any) -> str:
    result = client.safe_api_call(
        _api(client).access.groups.get
    )
    if not isinstance(result, list):
        result = [result] if result else []
    lines = ["\U0001f465 **Groups**\n"]
    for group in result:
        groupid = group.get("groupid", "unknown")
        comment = group.get("comment", "")
        members = group.get("members", "")
        lines.append(f"   • **{groupid}**")
        if comment:
            lines.append(f"     {comment}")
        if members:
            lines.append(f"     Members: {members}")
    if not result:
        lines.append("   No groups found.")
    return "\n".join(lines)


@confirm_required
def create_group(
    client: Any,
    groupid: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not groupid:
        raise ValueError("groupid is required for group creation")
    params: dict[str, Any] = {"groupid": groupid}
    if comment is not None:
        params["comment"] = comment
    elevated = client.get_client(elevated=True)
    client.safe_api_call(elevated.access.groups.post, elevated=True, **params)
    return f"Group {groupid!r} created"


def get_group(client: Any, groupid: str = "") -> str:
    if not groupid:
        raise ValueError("groupid is required")
    result = client.safe_api_call(
        _api(client).access.groups(groupid).get
    )
    lines = [f"\U0001f465 **Group {groupid}**\n"]
    if isinstance(result, dict):
        for key, val in result.items():
            lines.append(f"   • {key}: {val}")
    if not result:
        lines.append("   No data returned.")
    return "\n".join(lines)


@confirm_required
def update_group(
    client: Any,
    groupid: str = "",
    comment: str | None = None,
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not groupid:
        raise ValueError("groupid is required for group update")
    params: dict[str, Any] = {}
    if comment is not None:
        params["comment"] = comment
    elevated = client.get_client(elevated=True)
    client.safe_api_call(elevated.access.groups(groupid).put, elevated=True, **params)
    return f"Group {groupid!r} updated"


@confirm_required
def delete_group(
    client: Any,
    groupid: str = "",
    confirm: bool = False,
) -> str:
    client.raise_if_not_elevated()
    if not groupid:
        raise ValueError("groupid is required for group deletion")
    elevated = client.get_client(elevated=True)
    client.safe_api_call(elevated.access.groups(groupid).delete, elevated=True)
    return f"Group {groupid!r} deleted"


def check_permissions(
    client: Any,
    userid: str | None = None,
    path: str | None = None,
) -> str:
    params: dict[str, Any] = {}
    if userid is not None:
        params["userid"] = userid
    if path is not None:
        params["path"] = path
    result = client.safe_api_call(
        _api(client).access.permissions.get, **params,
    )
    lines = ["\U0001f510 **Effective Permissions**\n"]
    if isinstance(result, dict):
        for perm_path, perm_data in result.items():
            lines.append(f"   • **{perm_path}**")
            if isinstance(perm_data, dict):
                for role, privs in perm_data.items():
                    lines.append(f"     {role}: {privs}")
    elif isinstance(result, list):
        for entry in result:
            lines.append(f"   • {entry}")
    if not result:
        lines.append("   No permissions found.")
    return "\n".join(lines)
