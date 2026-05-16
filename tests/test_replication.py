from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.replication import (
    create_replication,
    delete_replication,
    get_replication,
    get_replication_log,
    get_replication_status,
    list_node_replication,
    list_replication,
    schedule_replication,
    update_replication,
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


class TestListReplication:
    async def test_list_replication_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "100-local", "source": "pve", "target": "pve2", "schedule": "*/15", "state": "ok"},
            ]
        )
        result = await list_replication(mock_client)
        assert "100-local" in result
        assert "Replication Jobs" in result

    async def test_list_replication_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_replication(mock_client)
        assert "No replication jobs" in result


class TestCreateReplication:
    async def test_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_replication(mock_client, id="100-local")

    async def test_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_replication(client, id="100-local", confirm=True)

    async def test_create_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await create_replication(mock_client, id="", confirm=True)

    async def test_create_replication(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_replication(
            mock_client,
            id="100-local",
            source="pve",
            target="pve2",
            schedule="*/15",
            confirm=True,
        )
        assert "100-local" in result
        assert "created" in result.lower()

    async def test_create_with_optional_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_replication(
            mock_client,
            id="100-local",
            comment="test",
            disable=True,
            rate=50.0,
            confirm=True,
        )
        assert "100-local" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test"
        assert call_args[1]["disable"] == 1
        assert call_args[1]["rate"] == 50.0


class TestGetReplication:
    async def test_get_replication(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "id": "100-local",
                "source": "pve",
                "target": "pve2",
            }
        )
        result = await get_replication(mock_client, id="100-local")
        assert "100-local" in result
        assert "pve" in result

    async def test_get_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_replication(mock_client, id="")


class TestUpdateReplication:
    async def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_replication(mock_client, id="100-local", schedule="*/30")

    async def test_update_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_replication(client, id="100-local", confirm=True, schedule="*/30")

    async def test_update_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await update_replication(mock_client, id="", confirm=True, schedule="*/30")

    async def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_replication(mock_client, id="100-local", confirm=True)

    async def test_update_replication(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_replication(
            mock_client,
            id="100-local",
            schedule="*/30",
            comment="updated",
            confirm=True,
        )
        assert "100-local" in result
        assert "updated" in result.lower()


class TestDeleteReplication:
    async def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_replication(mock_client, id="100-local")

    async def test_delete_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_replication(client, id="100-local", confirm=True)

    async def test_delete_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_replication(mock_client, id="", confirm=True)

    async def test_delete_replication(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_replication(mock_client, id="100-local", confirm=True)
        assert "100-local" in result
        assert "deleted" in result.lower()


class TestListNodeReplication:
    async def test_list_node_replication_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "100-local", "source": "pve", "target": "pve2", "state": "ok"},
            ]
        )
        result = await list_node_replication(mock_client, node="pve")
        assert "100-local" in result
        assert "pve" in result

    async def test_list_node_replication_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_node_replication(mock_client, node="pve")
        assert "No replication jobs" in result

    async def test_list_node_replication_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_node_replication(mock_client, node="bad!node")


class TestScheduleReplication:
    async def test_schedule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await schedule_replication(mock_client, id="100-local")

    async def test_schedule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await schedule_replication(client, id="100-local", confirm=True)

    async def test_schedule_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await schedule_replication(mock_client, id="", confirm=True)

    async def test_schedule_replication(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await schedule_replication(mock_client, id="100-local", node="pve", confirm=True)
        assert "100-local" in result
        assert "scheduled" in result.lower()

    async def test_schedule_replication_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await schedule_replication(mock_client, id="100-local", node="bad!node", confirm=True)


class TestGetReplicationStatus:
    async def test_get_replication_status(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"status": "ok", "guest": "100"},
            ]
        )
        result = await get_replication_status(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    async def test_get_replication_status_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "status": "ok",
                "guest": "100",
            }
        )
        result = await get_replication_status(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    async def test_get_replication_status_no_id(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_replication_status(mock_client, id="")

    async def test_get_replication_status_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await get_replication_status(mock_client, node="bad!node", id="100-local")


class TestGetReplicationLog:
    async def test_get_replication_log(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"n": 0, "t": "replication started"},
                {"n": 1, "t": "replication finished"},
            ]
        )
        result = await get_replication_log(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    async def test_get_replication_log_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await get_replication_log(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    async def test_get_replication_log_no_id(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_replication_log(mock_client, id="")

    async def test_get_replication_log_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await get_replication_log(mock_client, node="bad!node", id="100-local")
