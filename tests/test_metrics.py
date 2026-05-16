from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.metrics import (
    create_metric_server,
    delete_metric_server,
    get_metric_server,
    list_metric_servers,
    update_metric_server,
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
    client.admin_client = MagicMock()
    client.monitor_client = MagicMock()
    return client


class TestListMetricServers:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "graphite1", "type": "graphite", "server": "10.0.0.1"},
                {"id": "influx1", "type": "influxdb", "server": "10.0.0.2"},
            ]
        )
        result = await list_metric_servers(mock_client)
        assert "Metric Servers" in result
        assert "graphite1" in result
        assert "influx1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_metric_servers(mock_client)
        assert "No metric servers found" in result


class TestGetMetricServer:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "id": "graphite1",
                "type": "graphite",
                "server": "10.0.0.1",
            }
        )
        result = await get_metric_server(mock_client, id="graphite1")
        assert "graphite1" in result
        assert "graphite" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_metric_server(mock_client, id="")


class TestCreateMetricServer:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_metric_server(mock_client, id="graphite1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_metric_server(client, id="graphite1", confirm=True)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await create_metric_server(mock_client, id="", confirm=True)

    async def test_invalid_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type must be one of"):
            await create_metric_server(mock_client, id="test", type="invalid", confirm=True)

    async def test_create_graphite(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_metric_server(
            mock_client, id="graphite1", type="graphite", server="10.0.0.1", confirm=True
        )
        assert "graphite1" in result
        assert "graphite" in result
        assert "created" in result.lower()

    async def test_create_influxdb(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_metric_server(mock_client, id="influx1", type="influxdb", confirm=True)
        assert "influx1" in result
        assert "influxdb" in result

    async def test_create_opentelemetry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_metric_server(mock_client, id="otel1", type="opentelemetry", confirm=True)
        assert "otel1" in result
        assert "opentelemetry" in result


class TestUpdateMetricServer:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_metric_server(mock_client, id="graphite1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await update_metric_server(mock_client, id="", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_metric_server(mock_client, id="graphite1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_metric_server(mock_client, id="graphite1", server="10.0.0.2", confirm=True)
        assert "graphite1" in result
        assert "updated" in result.lower()


class TestDeleteMetricServer:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_metric_server(mock_client, id="graphite1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_metric_server(client, id="graphite1", confirm=True)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_metric_server(mock_client, id="", confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_metric_server(mock_client, id="graphite1", confirm=True)
        assert "graphite1" in result
        assert "deleted" in result.lower()
