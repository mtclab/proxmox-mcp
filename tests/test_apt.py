from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.apt import list_repositories, list_updates, list_versions, refresh_updates
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


class TestListUpdates:
    def test_list_updates_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {
                "Package": "pve-manager",
                "Version": "8.1.3",
                "OldVersion": "8.1.2",
                "Description": "PVE Manager",
            },
            {"Package": "qemu-server", "Version": "8.1.1", "OldVersion": "8.1.0"},
        ])
        result = list_updates(mock_client, node="pve")
        assert "pve-manager" in result
        assert "8.1.3" in result
        assert "APT Updates" in result

    def test_list_updates_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_updates(mock_client, node="pve")
        assert "No updates available" in result

    def test_list_updates_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_updates(mock_client, node="bad node!")


class TestRefreshUpdates:
    def test_refresh_updates_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            refresh_updates(mock_client, node="pve")

    def test_refresh_updates_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:00000001:apt:update"
        )
        result = refresh_updates(mock_client, node="pve", confirm=True)
        assert "APT update refresh initiated" in result
        assert "pve" in result


class TestListRepositories:
    def test_list_repositories_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": [
                {
                    "Path": "/etc/apt/sources.list",
                    "Suite": "bookworm",
                    "Components": "main contrib",
                    "Enabled": True,
                    "Comment": "",
                },
            ]
        })
        result = list_repositories(mock_client, node="pve")
        assert "APT Repositories" in result
        assert "bookworm" in result

    def test_list_repositories_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"Path": "/etc/apt/sources.list", "Suite": "bookworm", "Enabled": True},
        ])
        result = list_repositories(mock_client, node="pve")
        assert "bookworm" in result

    def test_list_repositories_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = list_repositories(mock_client, node="pve")
        assert "No repository information" in result


class TestListVersions:
    def test_list_versions_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {
                "Package": "pve-manager",
                "Version": "8.1.3",
                "Origin": "Proxmox",
                "OldVersion": "8.1.2",
            },
        ])
        result = list_versions(mock_client, node="pve")
        assert "pve-manager" in result
        assert "8.1.3" in result
        assert "APT Versions" in result

    def test_list_versions_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_versions(mock_client, node="pve")
        assert "No version information" in result

    def test_list_versions_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_versions(mock_client, node="bad!")
