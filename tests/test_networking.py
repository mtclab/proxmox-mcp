from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.networking import (
    create_network,
    delete_network,
    list_network,
    update_network,
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
    def test_create_network_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_network(mock_client, node="pve", iface="vmbr1")

    def test_update_network_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_network(mock_client, node="pve", iface="vmbr1")

    def test_delete_network_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_network(mock_client, node="pve", iface="vmbr1")


class TestElevatedCheck:
    def test_create_network_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_network(client, node="pve", iface="vmbr1", confirm=True)

    def test_update_network_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_network(client, node="pve", iface="vmbr1", confirm=True)

    def test_delete_network_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_network(client, node="pve", iface="vmbr1", confirm=True)


class TestListNetwork:
    def test_list_network_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"iface": "vmbr0", "type": "bridge", "address": "10.0.0.1", "netmask": "24", "active": 1},
            {"iface": "eno1", "type": "eth", "address": "", "active": 1},
        ])
        result = list_network(mock_client, node="pve")
        assert "vmbr0" in result
        assert "eno1" in result

    def test_list_network_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_network(mock_client, node="pve")
        assert "No interfaces found" in result

    def test_list_network_with_gateway(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {
                "iface": "vmbr0", "type": "bridge",
                "address": "10.0.0.1", "netmask": "24",
                "gateway": "10.0.0.254", "active": 1,
            },
        ])
        result = list_network(mock_client, node="pve")
        assert "10.0.0.254" in result


class TestCreateNetwork:
    def test_create_network(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0300:abc")
        result = create_network(
            mock_client, node="pve", iface="vmbr1",
            type="bridge", confirm=True,
        )
        assert "vmbr1" in result
        assert "UPID" in result

    def test_create_network_with_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0301:abc")
        create_network(
            mock_client, node="pve", iface="vmbr1",
            type="bridge", address="10.0.1.1",
            netmask="24", gateway="10.0.1.254",
            bridge_ports="eno1", confirm=True,
        )
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["address"] == "10.0.1.1"
        assert call_args[1]["netmask"] == "24"
        assert call_args[1]["gateway"] == "10.0.1.254"
        assert call_args[1]["bridge_ports"] == "eno1"

    def test_create_network_no_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="iface is required"):
            create_network(mock_client, node="pve", iface="", confirm=True)


class TestUpdateNetwork:
    def test_update_network(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0302:abc")
        result = update_network(
            mock_client, node="pve", iface="vmbr0",
            address="10.0.0.2", confirm=True,
        )
        assert "vmbr0" in result
        assert "UPID" in result

    def test_update_network_no_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="iface is required"):
            update_network(mock_client, node="pve", iface="", confirm=True)


class TestDeleteNetwork:
    def test_delete_network(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0303:abc")
        result = delete_network(
            mock_client, node="pve", iface="vmbr1", confirm=True,
        )
        assert "vmbr1" in result
        assert "UPID" in result

    def test_delete_network_no_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="iface is required"):
            delete_network(mock_client, node="pve", iface="", confirm=True)
