from unittest.mock import AsyncMock, MagicMock, patch

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
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await vm_vnc_proxy(mock_client, node="pve", vmid=100)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await vm_vnc_proxy(client, node="pve", vmid=100, confirm=True)

    async def test_invalid_vmid(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmid"):
            await vm_vnc_proxy(mock_client, node="pve", vmid=-1, confirm=True)

    async def test_vm_vnc_proxy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5900, "ticket": "abc123"})
        result = await vm_vnc_proxy(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "5900" in result

    async def test_vm_vnc_proxy_default_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5900, "ticket": "abc123"})
        result = await vm_vnc_proxy(mock_client, vmid=100, confirm=True)
        assert "100" in result


class TestVmSpiceProxy:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await vm_spice_proxy(mock_client, node="pve", vmid=100)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await vm_spice_proxy(client, node="pve", vmid=100, confirm=True)

    async def test_vm_spice_proxy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 3128, "ticket": "sp123"})
        result = await vm_spice_proxy(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "3128" in result


class TestVmTermproxy:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await vm_termproxy(mock_client, node="pve", vmid=100)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await vm_termproxy(client, node="pve", vmid=100, confirm=True)

    async def test_vm_termproxy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5100, "ticket": "term123"})
        result = await vm_termproxy(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "5100" in result


class TestLxcVncProxy:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lxc_vnc_proxy(mock_client, node="pve", vmid=200)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await lxc_vnc_proxy(client, node="pve", vmid=200, confirm=True)

    async def test_lxc_vnc_proxy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5901, "ticket": "lxc-vnc"})
        result = await lxc_vnc_proxy(mock_client, node="pve", vmid=200, confirm=True)
        assert "200" in result
        assert "5901" in result


class TestLxcTermproxy:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lxc_termproxy(mock_client, node="pve", vmid=200)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await lxc_termproxy(client, node="pve", vmid=200, confirm=True)

    async def test_lxc_termproxy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5101, "ticket": "lxc-term"})
        result = await lxc_termproxy(mock_client, node="pve", vmid=200, confirm=True)
        assert "200" in result
        assert "5101" in result


class TestNodeVncshell:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await node_vncshell(mock_client, node="pve")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await node_vncshell(client, node="pve", confirm=True)

    async def test_node_vncshell(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5902, "ticket": "vncshell"})
        result = await node_vncshell(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "5902" in result


class TestNodeSpiceshell:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await node_spiceshell(mock_client, node="pve")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await node_spiceshell(client, node="pve", confirm=True)

    async def test_node_spiceshell(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 3129, "ticket": "spiceshell"})
        result = await node_spiceshell(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "3129" in result


class TestNodeTermproxy:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await node_termproxy(mock_client, node="pve")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await node_termproxy(client, node="pve", confirm=True)

    async def test_node_termproxy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5102, "ticket": "nodeterm"})
        result = await node_termproxy(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "5102" in result


class TestLxcSpiceProxy:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lxc_spice_proxy(mock_client, node="pve", vmid=200)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await lxc_spice_proxy(client, node="pve", vmid=200, confirm=True)

    async def test_lxc_spice_proxy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 3130, "ticket": "lxc-spice"})
        result = await lxc_spice_proxy(mock_client, node="pve", vmid=200, confirm=True)
        assert "200" in result
        assert "SPICE" in result

    async def test_lxc_spice_proxy_invalid_vmid(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmid"):
            await lxc_spice_proxy(mock_client, node="pve", vmid=-1, confirm=True)


class TestLxcVncWebsocket:
    async def test_lxc_vnc_websocket(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"port": 5903, "path": "websockpath"})
        result = await lxc_vnc_websocket(mock_client, node="pve", vmid=200)
        assert "200" in result
        assert "5903" in result

    async def test_lxc_vnc_websocket_invalid_vmid(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmid"):
            await lxc_vnc_websocket(mock_client, node="pve", vmid=-1)

    async def test_lxc_vnc_websocket_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await lxc_vnc_websocket(mock_client, node="bad!node", vmid=200)
