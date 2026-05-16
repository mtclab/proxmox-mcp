from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.console import (
    lxc_spice_proxy,
    lxc_termproxy,
    lxc_vnc_proxy,
    lxc_vnc_websocket,
    node_spiceshell,
    node_termproxy,
    node_vncshell,
    vm_spice_proxy,
    vm_termproxy,
    vm_vnc_proxy,
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


class TestVmVncProxy:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            vm_vnc_proxy(mock_client, node="pve", vmid=100)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            vm_vnc_proxy(client, node="pve", vmid=100, confirm=True)

    def test_invalid_vmid(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmid"):
            vm_vnc_proxy(mock_client, node="pve", vmid=-1, confirm=True)

    def test_vm_vnc_proxy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5900, "ticket": "abc123"})
        result = vm_vnc_proxy(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "5900" in result

    def test_vm_vnc_proxy_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5900, "ticket": "abc123"})
        result = vm_vnc_proxy(mock_client, vmid=100, confirm=True)
        assert "100" in result


class TestVmSpiceProxy:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            vm_spice_proxy(mock_client, node="pve", vmid=100)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            vm_spice_proxy(client, node="pve", vmid=100, confirm=True)

    def test_vm_spice_proxy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 3128, "ticket": "sp123"})
        result = vm_spice_proxy(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "3128" in result


class TestVmTermproxy:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            vm_termproxy(mock_client, node="pve", vmid=100)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            vm_termproxy(client, node="pve", vmid=100, confirm=True)

    def test_vm_termproxy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5100, "ticket": "term123"})
        result = vm_termproxy(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "5100" in result


class TestLxcVncProxy:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lxc_vnc_proxy(mock_client, node="pve", vmid=200)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            lxc_vnc_proxy(client, node="pve", vmid=200, confirm=True)

    def test_lxc_vnc_proxy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5901, "ticket": "lxc-vnc"})
        result = lxc_vnc_proxy(mock_client, node="pve", vmid=200, confirm=True)
        assert "200" in result
        assert "5901" in result


class TestLxcTermproxy:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lxc_termproxy(mock_client, node="pve", vmid=200)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            lxc_termproxy(client, node="pve", vmid=200, confirm=True)

    def test_lxc_termproxy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5101, "ticket": "lxc-term"})
        result = lxc_termproxy(mock_client, node="pve", vmid=200, confirm=True)
        assert "200" in result
        assert "5101" in result


class TestNodeVncshell:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            node_vncshell(mock_client, node="pve")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            node_vncshell(client, node="pve", confirm=True)

    def test_node_vncshell(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5902, "ticket": "vncshell"})
        result = node_vncshell(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "5902" in result


class TestNodeSpiceshell:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            node_spiceshell(mock_client, node="pve")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            node_spiceshell(client, node="pve", confirm=True)

    def test_node_spiceshell(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 3129, "ticket": "spiceshell"})
        result = node_spiceshell(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "3129" in result


class TestNodeTermproxy:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            node_termproxy(mock_client, node="pve")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            node_termproxy(client, node="pve", confirm=True)

    def test_node_termproxy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5102, "ticket": "nodeterm"})
        result = node_termproxy(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "5102" in result


class TestLxcSpiceProxy:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lxc_spice_proxy(mock_client, node="pve", vmid=200)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            lxc_spice_proxy(client, node="pve", vmid=200, confirm=True)

    def test_lxc_spice_proxy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 3130, "ticket": "lxc-spice"})
        result = lxc_spice_proxy(mock_client, node="pve", vmid=200, confirm=True)
        assert "200" in result
        assert "SPICE" in result

    def test_lxc_spice_proxy_invalid_vmid(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmid"):
            lxc_spice_proxy(mock_client, node="pve", vmid=-1, confirm=True)


class TestLxcVncWebsocket:
    def test_lxc_vnc_websocket(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"port": 5903, "path": "websockpath"})
        result = lxc_vnc_websocket(mock_client, node="pve", vmid=200)
        assert "200" in result
        assert "5903" in result

    def test_lxc_vnc_websocket_invalid_vmid(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmid"):
            lxc_vnc_websocket(mock_client, node="pve", vmid=-1)

    def test_lxc_vnc_websocket_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            lxc_vnc_websocket(mock_client, node="bad!node", vmid=200)
