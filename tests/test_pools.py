from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.pools import (
    create_pool,
    delete_pool,
    get_pool,
    list_pools,
    update_pool,
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


class TestListPools:
    async def test_list_pools(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"poolid": "pool1", "comment": "Test pool"},
                {"poolid": "pool2"},
            ]
        )
        result = await list_pools(mock_client)
        assert "pool1" in result
        assert "pool2" in result

    async def test_list_pools_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_pools(mock_client)
        assert "No pools found" in result


class TestGetPool:
    async def test_get_pool(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "comment": "Production pool",
                "members": [
                    {"vmid": 100, "type": "qemu", "name": "vm1"},
                    {"vmid": 200, "type": "lxc", "name": "ct1"},
                ],
            }
        )
        result = await get_pool(mock_client, poolid="pool1")
        assert "pool1" in result
        assert "100" in result
        assert "200" in result

    async def test_get_pool_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "members": [],
            }
        )
        result = await get_pool(mock_client, poolid="empty-pool")
        assert "empty-pool" in result
        assert "No members" in result


class TestCreatePool:
    async def test_create_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_pool(mock_client, poolid="new-pool")

    async def test_create_pool_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_pool(client, poolid="new-pool", confirm=True)

    async def test_create_pool_no_poolid_raises(self, mock_client):
        with pytest.raises(ValueError, match="poolid is required"):
            await create_pool(mock_client, poolid="", confirm=True)

    async def test_create_pool(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_pool(mock_client, poolid="new-pool", comment="Test pool", confirm=True)
        assert "new-pool" in result
        assert "created" in result.lower()

    async def test_create_pool_without_comment(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_pool(mock_client, poolid="new-pool", confirm=True)
        assert "new-pool" in result
        call_args = mock_client.safe_api_call.call_args
        assert "comment" not in call_args[1]


class TestUpdatePool:
    async def test_update_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_pool(mock_client, poolid="pool1", comment="updated")

    async def test_update_pool_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_pool(client, poolid="pool1", comment="updated", confirm=True)

    async def test_update_pool_no_poolid_raises(self, mock_client):
        with pytest.raises(ValueError, match="poolid is required"):
            await update_pool(mock_client, poolid="", confirm=True)

    async def test_update_pool(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_pool(mock_client, poolid="pool1", comment="updated comment", confirm=True)
        assert "pool1" in result
        assert "updated" in result.lower()

    async def test_update_pool_with_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_pool(mock_client, poolid="pool1", delete="100", confirm=True)
        assert "pool1" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["delete"] == "100"


class TestDeletePool:
    async def test_delete_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_pool(mock_client, poolid="pool1")

    async def test_delete_pool_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_pool(client, poolid="pool1", confirm=True)

    async def test_delete_pool_no_poolid_raises(self, mock_client):
        with pytest.raises(ValueError, match="poolid is required"):
            await delete_pool(mock_client, poolid="", confirm=True)

    async def test_delete_pool(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_pool(mock_client, poolid="pool1", confirm=True)
        assert "pool1" in result
        assert "deleted" in result.lower()
