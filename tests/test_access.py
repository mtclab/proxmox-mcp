from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.access import (
    add_tfa_entry,
    change_password,
    delete_tfa_entry,
    get_domain,
    get_tfa_entry,
    get_user_tfa,
    list_domains,
    list_tfa,
    sync_domain,
    unlock_tfa,
    update_tfa_entry,
)
from proxmox_mcp.config import Config


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


class TestListTfa:
    def test_list_tfa_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"userid": "admin@pve", "type": "totp"},
            {"userid": "user@pve", "type": "webauthn"},
        ])
        result = list_tfa(mock_client)
        assert "admin@pve" in result
        assert "user@pve" in result

    def test_list_tfa_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_tfa(mock_client)
        assert "No TFA entries found" in result


class TestGetUserTfa:
    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            get_user_tfa(mock_client, userid="")

    def test_get_user_tfa(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "totp-0", "type": "totp"},
        ])
        result = get_user_tfa(mock_client, userid="admin@pve")
        assert "admin@pve" in result

    def test_get_user_tfa_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"id": "totp-0", "type": "totp"})
        result = get_user_tfa(mock_client, userid="admin@pve")
        assert "admin@pve" in result

    def test_get_user_tfa_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = get_user_tfa(mock_client, userid="admin@pve")
        assert "No TFA entries found" in result


class TestAddTfaEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            add_tfa_entry(mock_client, userid="admin@pve", type="totp")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            add_tfa_entry(client, userid="admin@pve", type="totp", confirm=True)

    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            add_tfa_entry(mock_client, userid="", type="totp", confirm=True)

    def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            add_tfa_entry(mock_client, userid="admin@pve", type="", confirm=True)

    def test_add_tfa_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = add_tfa_entry(mock_client, userid="admin@pve", type="totp", confirm=True)
        assert "admin@pve" in result
        assert "totp" in result

    def test_add_tfa_entry_with_optional(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = add_tfa_entry(
            mock_client, userid="admin@pve", type="totp",
            description="my device", value="secret", confirm=True,
        )
        assert "admin@pve" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["description"] == "my device"
        assert call_args[1]["value"] == "secret"


class TestDeleteTfaEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_tfa_entry(mock_client, userid="admin@pve", id="totp-0")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_tfa_entry(client, userid="admin@pve", id="totp-0", confirm=True)

    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            delete_tfa_entry(mock_client, userid="", id="totp-0", confirm=True)

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_tfa_entry(mock_client, userid="admin@pve", id="", confirm=True)

    def test_delete_tfa_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_tfa_entry(mock_client, userid="admin@pve", id="totp-0", confirm=True)
        assert "admin@pve" in result
        assert "totp-0" in result


class TestGetTfaEntry:
    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            get_tfa_entry(mock_client, userid="", id="totp-0")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            get_tfa_entry(mock_client, userid="admin@pve", id="")

    def test_get_tfa_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"id": "totp-0", "type": "totp"})
        result = get_tfa_entry(mock_client, userid="admin@pve", id="totp-0")
        assert "admin@pve" in result
        assert "totp-0" in result

    def test_get_tfa_entry_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = get_tfa_entry(mock_client, userid="admin@pve", id="totp-0")
        assert "No data returned" in result


class TestUpdateTfaEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_tfa_entry(mock_client, userid="admin@pve", id="totp-0")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_tfa_entry(client, userid="admin@pve", id="totp-0", confirm=True)

    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            update_tfa_entry(mock_client, userid="", id="totp-0", confirm=True)

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            update_tfa_entry(mock_client, userid="admin@pve", id="", confirm=True)

    def test_update_tfa_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_tfa_entry(
            mock_client, userid="admin@pve", id="totp-0", description="updated", confirm=True,
        )
        assert "admin@pve" in result
        assert "totp-0" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["description"] == "updated"

    def test_update_tfa_enable_false(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        update_tfa_entry(mock_client, userid="admin@pve", id="totp-0", enable=False, confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["enable"] == 0


class TestUnlockTfa:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            unlock_tfa(mock_client, userid="admin@pve")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            unlock_tfa(client, userid="admin@pve", confirm=True)

    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            unlock_tfa(mock_client, userid="", confirm=True)

    def test_unlock_tfa(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = unlock_tfa(mock_client, userid="admin@pve", confirm=True)
        assert "admin@pve" in result
        assert "unlocked" in result.lower()


class TestListDomains:
    def test_list_domains_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"realm": "pve", "plugin": "pve"},
            {"realm": "ldap", "plugin": "ldap"},
        ])
        result = list_domains(mock_client)
        assert "pve" in result
        assert "ldap" in result

    def test_list_domains_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_domains(mock_client)
        assert "No auth domains found" in result


class TestGetDomain:
    def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            get_domain(mock_client, realm="")

    def test_get_domain(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"realm": "pve", "type": "pve"})
        result = get_domain(mock_client, realm="pve")
        assert "pve" in result

    def test_get_domain_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = get_domain(mock_client, realm="pve")
        assert "No data returned" in result


class TestSyncDomain:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            sync_domain(mock_client, realm="ldap")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            sync_domain(client, realm="ldap", confirm=True)

    def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            sync_domain(mock_client, realm="", confirm=True)

    def test_sync_domain(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "UPID:pve:123"})
        result = sync_domain(mock_client, realm="ldap", confirm=True)
        assert "ldap" in result


class TestChangePassword:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            change_password(mock_client, userid="admin@pve", password="newpass")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            change_password(client, userid="admin@pve", password="newpass", confirm=True)

    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            change_password(mock_client, userid="", password="newpass", confirm=True)

    def test_no_password_raises(self, mock_client):
        with pytest.raises(ValueError, match="password is required"):
            change_password(mock_client, userid="admin@pve", password="", confirm=True)

    def test_change_password(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = change_password(mock_client, userid="admin@pve", password="newpass", confirm=True)
        assert "admin@pve" in result
