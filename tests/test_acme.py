from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.acme import (
    create_acme_account,
    create_acme_plugin,
    delete_acme_account,
    delete_acme_plugin,
    get_acme_account,
    get_acme_challenge_schema,
    list_acme_accounts,
    list_acme_directories,
    list_acme_plugins,
    list_acme_tos,
    update_acme_account,
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
    client.admin_client = MagicMock()
    client.monitor_client = MagicMock()
    return client


class TestListAcmeAccounts:
    def test_list_acme_accounts(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "letsencrypt", "contact": "admin@example.com", "directory": "https://acme-v02.api.letsencrypt.org/directory"},
        ])
        result = list_acme_accounts(mock_client)
        assert "letsencrypt" in result
        assert "admin@example.com" in result

    def test_list_acme_accounts_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_acme_accounts(mock_client)
        assert "No ACME accounts" in result


class TestGetAcmeAccount:
    def test_get_acme_account(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "name": "letsencrypt",
            "contact": "admin@example.com",
        })
        result = get_acme_account(mock_client, name="letsencrypt")
        assert "letsencrypt" in result

    def test_get_acme_account_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            get_acme_account(mock_client, name="")


class TestCreateAcmeAccount:
    def test_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_acme_account(mock_client, name="test", contact="a@b.com")

    def test_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_acme_account(client, name="test", contact="a@b.com", confirm=True)

    def test_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            create_acme_account(mock_client, name="", contact="a@b.com", confirm=True)

    def test_create_no_contact_raises(self, mock_client):
        with pytest.raises(ValueError, match="contact is required"):
            create_acme_account(mock_client, name="test", contact="", confirm=True)

    def test_create_acme_account(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_acme_account(mock_client, name="letsencrypt", contact="admin@example.com", confirm=True)
        assert "letsencrypt" in result
        assert "created" in result.lower()


class TestDeleteAcmeAccount:
    def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_acme_account(mock_client, name="test")

    def test_delete_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_acme_account(client, name="test", confirm=True)

    def test_delete_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            delete_acme_account(mock_client, name="", confirm=True)

    def test_delete_acme_account(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_acme_account(mock_client, name="letsencrypt", confirm=True)
        assert "letsencrypt" in result
        assert "deleted" in result.lower()


class TestUpdateAcmeAccount:
    def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_acme_account(mock_client, name="test", contact="new@b.com")

    def test_update_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            update_acme_account(mock_client, name="", contact="new@b.com", confirm=True)

    def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            update_acme_account(mock_client, name="test", confirm=True)

    def test_update_acme_account(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_acme_account(mock_client, name="test", contact="new@b.com", confirm=True)
        assert "test" in result
        assert "updated" in result.lower()


class TestListAcmeDirectories:
    def test_list_acme_directories(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "Let's Encrypt", "url": "https://acme-v02.api.letsencrypt.org/directory"},
        ])
        result = list_acme_directories(mock_client)
        assert "Let's Encrypt" in result

    def test_list_acme_directories_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_acme_directories(mock_client)
        assert "No ACME directories" in result


class TestListAcmePlugins:
    def test_list_acme_plugins(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"plugin": "dns-example", "type": "dns"},
        ])
        result = list_acme_plugins(mock_client)
        assert "dns-example" in result

    def test_list_acme_plugins_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_acme_plugins(mock_client)
        assert "No ACME plugins" in result


class TestCreateAcmePlugin:
    def test_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_acme_plugin(mock_client, id="test", type="dns")

    def test_create_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            create_acme_plugin(mock_client, id="", type="dns", confirm=True)

    def test_create_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            create_acme_plugin(mock_client, id="test", type="", confirm=True)

    def test_create_acme_plugin(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_acme_plugin(mock_client, id="dns-example", type="dns", confirm=True)
        assert "dns-example" in result
        assert "created" in result.lower()


class TestDeleteAcmePlugin:
    def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_acme_plugin(mock_client, id="test")

    def test_delete_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_acme_plugin(mock_client, id="", confirm=True)

    def test_delete_acme_plugin(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_acme_plugin(mock_client, id="dns-example", confirm=True)
        assert "dns-example" in result
        assert "deleted" in result.lower()


class TestGetAcmeChallengeSchema:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"dns-01": {"type": "string"}}})
        result = get_acme_challenge_schema(mock_client)
        assert "Challenge Schema" in result

    def test_dict_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"http-01": "url"})
        result = get_acme_challenge_schema(mock_client)
        assert "http-01" in result


class TestListAcmeTos:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"url": "https://terms.example.com"}})
        result = list_acme_tos(mock_client)
        assert "Terms of Service" in result

    def test_list_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[{"url": "https://terms.example.com"}])
        result = list_acme_tos(mock_client)
        assert "terms.example.com" in result
