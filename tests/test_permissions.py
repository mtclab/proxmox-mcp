from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.permissions import (
    delete_acl,
    list_acl,
    list_roles,
    list_tokens,
    list_users,
    set_acl,
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
            {"path": "/", "ugid": "admin@pve", "roles": "PVEAdmin", "propagate": 1},
            {"path": "/vms", "ugid": "user@pve", "roles": "PVEVMUser", "propagate": 1},
        ])
        result = list_acl(mock_client)
        assert "PVEAdmin" in result
        assert "PVEVMUser" in result

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
