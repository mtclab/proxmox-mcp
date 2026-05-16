from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.permissions import (
    check_permissions,
    create_group,
    create_role,
    create_token,
    create_user,
    delete_acl,
    delete_group,
    delete_role,
    delete_token,
    delete_user,
    get_group,
    get_role,
    get_token,
    get_user,
    list_acl,
    list_groups,
    list_roles,
    list_tokens,
    list_users,
    set_acl,
    update_group,
    update_role,
    update_token,
    update_user,
)


@pytest.fixture
def mock_config():
    return Config(
        url="https://10.96.16.19:8006",
        verify=False,
        monitor_token_id="zabbix@pve!zabbix",
        monitor_token_secret="monitor-secret",
        admin_token_id="homepilot@pve!homepilot",
        admin_token_secret="admin-secret",
        allow_elevated=True,
        default_node="pve",
    )


@pytest.fixture
def mock_client(mock_config):
    with patch("proxmox_mcp.client.ProxmoxAPI"):
        from proxmox_mcp.client import ProxmoxClient
        client = ProxmoxClient(mock_config)
    client._nodes_cache = [{"node": "pve", "status": "online"}]
    admin_mock = MagicMock()
    client.admin_client = admin_mock
    client.monitor_client = MagicMock()
    return client


class TestConfirmRequired:
    def test_set_acl_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            set_acl(mock_client, users="admin@pve", roles="PVEAdmin", path="/")

    def test_delete_acl_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_acl(mock_client, users="admin@pve", roles="PVEAdmin", path="/")


class TestElevatedCheck:
    def test_set_acl_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            set_acl(client, users="admin@pve", roles="PVEAdmin", path="/", confirm=True)

    def test_delete_acl_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_acl(client, users="admin@pve", roles="PVEAdmin", path="/", confirm=True)


class TestListAcl:
    def test_list_acl_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"path": "/", "userid": "admin@pve", "roleid": "PVEAdmin", "propagate": 1},
            {"path": "/vms", "userid": "user@pve", "roleid": "PVEVMUser", "propagate": 1},
        ])
        result = list_acl(mock_client)
        assert "PVEAdmin" in result
        assert "PVEVMUser" in result
        assert "admin@pve" in result

    def test_list_acl_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_acl(mock_client)
        assert "No ACL rules found" in result


class TestSetAcl:
    def test_set_acl(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = set_acl(
            mock_client, users="admin@pve", roles="PVEAdmin",
            path="/", confirm=True,
        )
        assert "admin@pve" in result
        assert "PVEAdmin" in result

    def test_set_acl_no_users_raises(self, mock_client):
        with pytest.raises(ValueError, match="users is required"):
            set_acl(mock_client, users="", roles="PVEAdmin", path="/", confirm=True)

    def test_set_acl_no_roles_raises(self, mock_client):
        with pytest.raises(ValueError, match="roles is required"):
            set_acl(mock_client, users="admin@pve", roles="", path="/", confirm=True)

    def test_set_acl_no_path_raises(self, mock_client):
        with pytest.raises(ValueError, match="path is required"):
            set_acl(mock_client, users="admin@pve", roles="PVEAdmin", path="", confirm=True)

    def test_set_acl_propagate_false(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        set_acl(
            mock_client, users="admin@pve", roles="PVEAdmin",
            path="/vms", propagate=False, confirm=True,
        )
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["propagate"] == 0


class TestDeleteAcl:
    def test_delete_acl(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_acl(
            mock_client, users="admin@pve", roles="PVEAdmin",
            path="/", confirm=True,
        )
        assert "admin@pve" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["delete"] == 1

    def test_delete_acl_no_users_raises(self, mock_client):
        with pytest.raises(ValueError, match="users is required"):
            delete_acl(mock_client, users="", roles="PVEAdmin", path="/", confirm=True)


class TestListRoles:
    def test_list_roles_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"roleid": "PVEAdmin", "privs": "VM.Monitor VM.PowerOff"},
            {"roleid": "PVEVMUser", "privs": "VM.Console VM.PowerOn"},
        ])
        result = list_roles(mock_client)
        assert "PVEAdmin" in result
        assert "PVEVMUser" in result

    def test_list_roles_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_roles(mock_client)
        assert "No roles found" in result


class TestListUsers:
    def test_list_users_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"userid": "admin@pve", "enable": 1},
            {"userid": "user@pve", "enable": 0},
        ])
        result = list_users(mock_client)
        assert "admin@pve" in result
        assert "user@pve" in result

    def test_list_users_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_users(mock_client)
        assert "No users found" in result


class TestListTokens:
    def test_list_tokens_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "zabbix@pve!zabbix", "privsep": 1, "comment": "monitoring"},
        ])
        result = list_tokens(mock_client, userid="zabbix@pve")
        assert "zabbix@pve!zabbix" in result
        mock_client.safe_api_call.assert_called_once()

    def test_list_tokens_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            list_tokens(mock_client, userid="")

    def test_list_tokens_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_tokens(mock_client, userid="admin@pve")
        assert "No tokens found" in result


class TestCreateUser:
    def test_create_user_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_user(mock_client, userid="test@pve", password="pass")

    def test_create_user_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_user(client, userid="test@pve", password="pass", confirm=True)

    def test_create_user_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            create_user(mock_client, userid="", password="pass", confirm=True)

    def test_create_user_no_password_raises(self, mock_client):
        with pytest.raises(ValueError, match="password is required"):
            create_user(mock_client, userid="test@pve", password="", confirm=True)

    def test_create_user(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = create_user(
            mock_client, userid="test@pve", password="pass123", confirm=True,
        )
        assert "test@pve" in result

    def test_create_user_with_optional(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        create_user(
            mock_client, userid="test@pve", password="pass123",
            comment="test user", email="t@t.com", firstname="Test",
            lastname="User", enable=True, expire=0, groups="group1",
            confirm=True,
        )
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test user"
        assert call_args[1]["enable"] == 1
        assert call_args[1]["expire"] == 0


class TestGetUser:
    def test_get_user_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            get_user(mock_client, userid="")

    def test_get_user(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"userid": "test@pve", "enable": 1})
        result = get_user(mock_client, userid="test@pve")
        assert "test@pve" in result


class TestUpdateUser:
    def test_update_user_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_user(mock_client, userid="test@pve")

    def test_update_user_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_user(client, userid="test@pve", confirm=True)

    def test_update_user_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            update_user(mock_client, userid="", confirm=True)

    def test_update_user(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_user(
            mock_client, userid="test@pve", email="new@t.com", confirm=True,
        )
        assert "test@pve" in result

    def test_update_user_enable_false(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        update_user(mock_client, userid="test@pve", enable=False, confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["enable"] == 0


class TestDeleteUser:
    def test_delete_user_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_user(mock_client, userid="test@pve")

    def test_delete_user_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_user(client, userid="test@pve", confirm=True)

    def test_delete_user_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            delete_user(mock_client, userid="", confirm=True)

    def test_delete_user(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_user(mock_client, userid="test@pve", confirm=True)
        assert "test@pve" in result


class TestCreateRole:
    def test_create_role_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_role(mock_client, roleid="MyRole", privs="VM.Monitor")

    def test_create_role_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_role(client, roleid="MyRole", privs="VM.Monitor", confirm=True)

    def test_create_role_no_roleid_raises(self, mock_client):
        with pytest.raises(ValueError, match="roleid is required"):
            create_role(mock_client, roleid="", privs="VM.Monitor", confirm=True)

    def test_create_role_no_privs_raises(self, mock_client):
        with pytest.raises(ValueError, match="privs is required"):
            create_role(mock_client, roleid="MyRole", privs="", confirm=True)

    def test_create_role(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = create_role(mock_client, roleid="MyRole", privs="VM.Monitor", confirm=True)
        assert "MyRole" in result
        assert "VM.Monitor" in result


class TestGetRole:
    def test_get_role_no_roleid_raises(self, mock_client):
        with pytest.raises(ValueError, match="roleid is required"):
            get_role(mock_client, roleid="")

    def test_get_role(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"roleid": "PVEAdmin", "privs": "VM.Monitor"})
        result = get_role(mock_client, roleid="PVEAdmin")
        assert "PVEAdmin" in result


class TestUpdateRole:
    def test_update_role_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_role(mock_client, roleid="MyRole", privs="VM.Monitor")

    def test_update_role_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_role(client, roleid="MyRole", privs="VM.Monitor", confirm=True)

    def test_update_role_no_roleid_raises(self, mock_client):
        with pytest.raises(ValueError, match="roleid is required"):
            update_role(mock_client, roleid="", privs="VM.Monitor", confirm=True)

    def test_update_role_no_privs_raises(self, mock_client):
        with pytest.raises(ValueError, match="privs is required"):
            update_role(mock_client, roleid="MyRole", privs="", confirm=True)

    def test_update_role(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_role(mock_client, roleid="MyRole", privs="VM.Monitor", confirm=True)
        assert "MyRole" in result


class TestDeleteRole:
    def test_delete_role_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_role(mock_client, roleid="MyRole")

    def test_delete_role_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_role(client, roleid="MyRole", confirm=True)

    def test_delete_role_no_roleid_raises(self, mock_client):
        with pytest.raises(ValueError, match="roleid is required"):
            delete_role(mock_client, roleid="", confirm=True)

    def test_delete_role(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_role(mock_client, roleid="MyRole", confirm=True)
        assert "MyRole" in result


class TestCreateToken:
    def test_create_token_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_token(mock_client, userid="test@pve", tokenid="mytoken")

    def test_create_token_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_token(client, userid="test@pve", tokenid="mytoken", confirm=True)

    def test_create_token_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            create_token(mock_client, userid="", tokenid="mytoken", confirm=True)

    def test_create_token_no_tokenid_raises(self, mock_client):
        with pytest.raises(ValueError, match="tokenid is required"):
            create_token(mock_client, userid="test@pve", tokenid="", confirm=True)

    def test_create_token(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"value": "secret123"})
        result = create_token(mock_client, userid="test@pve", tokenid="mytoken", confirm=True)
        assert "test@pve" in result
        assert "mytoken" in result


class TestGetToken:
    def test_get_token_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            get_token(mock_client, userid="", tokenid="mytoken")

    def test_get_token_no_tokenid_raises(self, mock_client):
        with pytest.raises(ValueError, match="tokenid is required"):
            get_token(mock_client, userid="test@pve", tokenid="")

    def test_get_token(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"privsep": 1, "comment": "test"})
        result = get_token(mock_client, userid="test@pve", tokenid="mytoken")
        assert "test@pve" in result
        assert "mytoken" in result


class TestUpdateToken:
    def test_update_token_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_token(mock_client, userid="test@pve", tokenid="mytoken")

    def test_update_token_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_token(client, userid="test@pve", tokenid="mytoken", confirm=True)

    def test_update_token_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            update_token(mock_client, userid="", tokenid="mytoken", confirm=True)

    def test_update_token_no_tokenid_raises(self, mock_client):
        with pytest.raises(ValueError, match="tokenid is required"):
            update_token(mock_client, userid="test@pve", tokenid="", confirm=True)

    def test_update_token(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_token(mock_client, userid="test@pve", tokenid="mytoken", confirm=True)
        assert "test@pve" in result
        assert "mytoken" in result


class TestDeleteToken:
    def test_delete_token_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_token(mock_client, userid="test@pve", tokenid="mytoken")

    def test_delete_token_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_token(client, userid="test@pve", tokenid="mytoken", confirm=True)

    def test_delete_token_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            delete_token(mock_client, userid="", tokenid="mytoken", confirm=True)

    def test_delete_token_no_tokenid_raises(self, mock_client):
        with pytest.raises(ValueError, match="tokenid is required"):
            delete_token(mock_client, userid="test@pve", tokenid="", confirm=True)

    def test_delete_token(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_token(mock_client, userid="test@pve", tokenid="mytoken", confirm=True)
        assert "test@pve" in result
        assert "mytoken" in result


class TestListGroups:
    def test_list_groups_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"groupid": "admin", "comment": "Administrators", "members": "root@pve"},
        ])
        result = list_groups(mock_client)
        assert "admin" in result

    def test_list_groups_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_groups(mock_client)
        assert "No groups found" in result


class TestCreateGroup:
    def test_create_group_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_group(mock_client, groupid="mygroup")

    def test_create_group_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_group(client, groupid="mygroup", confirm=True)

    def test_create_group_no_groupid_raises(self, mock_client):
        with pytest.raises(ValueError, match="groupid is required"):
            create_group(mock_client, groupid="", confirm=True)

    def test_create_group(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = create_group(mock_client, groupid="mygroup", confirm=True)
        assert "mygroup" in result


class TestGetGroup:
    def test_get_group_no_groupid_raises(self, mock_client):
        with pytest.raises(ValueError, match="groupid is required"):
            get_group(mock_client, groupid="")

    def test_get_group(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"groupid": "admin", "comment": "Administrators"})
        result = get_group(mock_client, groupid="admin")
        assert "admin" in result


class TestUpdateGroup:
    def test_update_group_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_group(mock_client, groupid="mygroup")

    def test_update_group_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_group(client, groupid="mygroup", confirm=True)

    def test_update_group_no_groupid_raises(self, mock_client):
        with pytest.raises(ValueError, match="groupid is required"):
            update_group(mock_client, groupid="", confirm=True)

    def test_update_group(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_group(mock_client, groupid="mygroup", comment="updated", confirm=True)
        assert "mygroup" in result


class TestDeleteGroup:
    def test_delete_group_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_group(mock_client, groupid="mygroup")

    def test_delete_group_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_group(client, groupid="mygroup", confirm=True)

    def test_delete_group_no_groupid_raises(self, mock_client):
        with pytest.raises(ValueError, match="groupid is required"):
            delete_group(mock_client, groupid="", confirm=True)

    def test_delete_group(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_group(mock_client, groupid="mygroup", confirm=True)
        assert "mygroup" in result


class TestCheckPermissions:
    def test_check_permissions(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "/": {"PVEAdmin": ["Sys.Modify", "Sys.Access"]},
            "/vms": {"PVEVMUser": ["VM.Console"]},
        })
        result = check_permissions(mock_client, userid="admin@pve")
        assert "PVEAdmin" in result

    def test_check_permissions_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = check_permissions(mock_client)
        assert "No permissions found" in result

    def test_check_permissions_with_path(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"/vms": {"PVEVMUser": ["VM.Console"]}})
        result = check_permissions(mock_client, userid="user@pve", path="/vms")
        assert "PVEVMUser" in result
