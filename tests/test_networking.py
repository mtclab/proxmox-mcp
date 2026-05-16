from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.networking import (
    _apply_network,
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
    async def test_create_network_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_network(mock_client, node="pve", iface="vmbr1")

    async def test_update_network_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_network(mock_client, node="pve", iface="vmbr1")

    async def test_delete_network_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_network(mock_client, node="pve", iface="vmbr1")


class TestElevatedCheck:
    async def test_create_network_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_network(client, node="pve", iface="vmbr1", confirm=True)

    async def test_update_network_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_network(client, node="pve", iface="vmbr1", confirm=True)

    async def test_delete_network_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_network(client, node="pve", iface="vmbr1", confirm=True)


class TestListNetwork:
    async def test_list_network_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"iface": "vmbr0", "type": "bridge", "address": "10.0.0.1", "netmask": "24", "active": 1},
                {"iface": "eno1", "type": "eth", "address": "", "active": 1},
            ]
        )
        result = await list_network(mock_client, node="pve")
        assert "vmbr0" in result
        assert "eno1" in result

    async def test_list_network_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_network(mock_client, node="pve")
        assert "No interfaces found" in result

    async def test_list_network_with_gateway(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {
                    "iface": "vmbr0",
                    "type": "bridge",
                    "address": "10.0.0.1",
                    "netmask": "24",
                    "gateway": "10.0.0.254",
                    "active": 1,
                },
            ]
        )
        result = await list_network(mock_client, node="pve")
        assert "10.0.0.254" in result


class TestCreateNetwork:
    async def test_create_network_default_no_apply(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0300:abc")
        result = await create_network(
            mock_client,
            node="pve",
            iface="vmbr1",
            type="bridge",
            confirm=True,
        )
        assert "vmbr1" in result
        assert "UPID" in result
        assert "Network changes applied" not in result

    async def test_create_network_apply_true(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0300:abc")
        result = await create_network(
            mock_client,
            node="pve",
            iface="vmbr2",
            type="bridge",
            confirm=True,
            apply=True,
        )
        assert "vmbr2" in result
        assert "UPID" in result
        assert "Network changes applied" in result

    async def test_create_network_apply_false(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0300:abc")
        result = await create_network(
            mock_client,
            node="pve",
            iface="vmbr1",
            type="bridge",
            confirm=True,
            apply=False,
        )
        assert "vmbr1" in result
        assert "Network changes applied" not in result

    async def test_create_network_with_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0301:abc")
        await create_network(
            mock_client,
            node="pve",
            iface="vmbr1",
            type="bridge",
            address="10.0.1.1",
            netmask="24",
            gateway="10.0.1.254",
            bridge_ports="eno1",
            confirm=True,
        )
        first_call = mock_client.safe_api_call.call_args_list[0]
        assert first_call[1]["address"] == "10.0.1.1"
        assert first_call[1]["netmask"] == "24"
        assert first_call[1]["gateway"] == "10.0.1.254"
        assert first_call[1]["bridge_ports"] == "eno1"

    async def test_create_network_no_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="iface is required"):
            await create_network(mock_client, node="pve", iface="", confirm=True)

    async def test_create_network_invalid_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="Invalid interface name"):
            await create_network(mock_client, node="pve", iface="bad iface!", confirm=True)


class TestUpdateNetwork:
    async def test_update_network_default_no_apply(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0302:abc")
        result = await update_network(
            mock_client,
            node="pve",
            iface="vmbr0",
            address="10.0.0.2",
            confirm=True,
        )
        assert "vmbr0" in result
        assert "UPID" in result
        assert "Network changes applied" not in result

    async def test_update_network_apply_true(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0302:abc")
        result = await update_network(
            mock_client,
            node="pve",
            iface="vmbr0",
            address="10.0.0.2",
            confirm=True,
            apply=True,
        )
        assert "vmbr0" in result
        assert "UPID" in result
        assert "Network changes applied" in result

    async def test_update_network_apply_false(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0302:abc")
        result = await update_network(
            mock_client,
            node="pve",
            iface="vmbr0",
            address="10.0.0.2",
            confirm=True,
            apply=False,
        )
        assert "vmbr0" in result
        assert "Network changes applied" not in result

    async def test_update_network_no_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="iface is required"):
            await update_network(mock_client, node="pve", iface="", confirm=True)

    async def test_update_network_invalid_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="Invalid interface name"):
            await update_network(mock_client, node="pve", iface="bad!name", confirm=True)


class TestDeleteNetwork:
    async def test_delete_network_default_no_apply(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0303:abc")
        result = await delete_network(
            mock_client,
            node="pve",
            iface="vmbr1",
            confirm=True,
        )
        assert "vmbr1" in result
        assert "UPID" in result
        assert "Network changes applied" not in result

    async def test_delete_network_apply_true(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0303:abc")
        result = await delete_network(
            mock_client,
            node="pve",
            iface="vmbr1",
            confirm=True,
            apply=True,
        )
        assert "vmbr1" in result
        assert "UPID" in result
        assert "Network changes applied" in result

    async def test_delete_network_apply_false(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0303:abc")
        result = await delete_network(
            mock_client,
            node="pve",
            iface="vmbr1",
            confirm=True,
            apply=False,
        )
        assert "vmbr1" in result
        assert "Network changes applied" not in result

    async def test_delete_network_no_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="iface is required"):
            await delete_network(mock_client, node="pve", iface="", confirm=True)

    async def test_delete_network_invalid_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="Invalid interface name"):
            await delete_network(mock_client, node="pve", iface="bad!name", confirm=True)


class TestApplyNetwork:
    async def test_apply_network_calls_put(self, mock_client):
        mock_client.safe_api_call = AsyncMock()
        await _apply_network(mock_client, "pve", "vmbr1")
        mock_client.safe_api_call.assert_called_once()
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["elevated"] is True


class TestManagementInterfaceWarning:
    async def test_create_vmbr0_warns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0304:abc")
        result = await create_network(
            mock_client,
            node="pve",
            iface="vmbr0",
            type="bridge",
            confirm=True,
            apply=True,
        )
        assert "WARNING" in result
        assert "management interface" in result

    async def test_create_non_mgmt_no_warning(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0305:abc")
        result = await create_network(
            mock_client,
            node="pve",
            iface="vmbr99",
            type="bridge",
            confirm=True,
            apply=True,
        )
        assert "WARNING" not in result

    async def test_update_vmbr0_warns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0306:abc")
        result = await update_network(
            mock_client,
            node="pve",
            iface="vmbr0",
            address="10.0.0.2",
            confirm=True,
            apply=True,
        )
        assert "WARNING" in result

    async def test_delete_vmbr0_warns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0307:abc")
        result = await delete_network(
            mock_client,
            node="pve",
            iface="vmbr0",
            confirm=True,
            apply=True,
        )
        assert "WARNING" in result
