from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.tasks import stop_task, task_log


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


class TestTaskLog:
    async def test_task_log_basic(self, mock_client):
        entries = [{"n": 0, "t": "task started"}, {"n": 1, "t": "task completed"}]
        mock_client.safe_api_call = AsyncMock(return_value=entries)
        result = await task_log(mock_client, upid="UPID:pve:000:abc", node="pve")
        assert "UPID:pve:000:abc" in result
        assert "task started" in result

    async def test_task_log_extracts_node_from_upid(self, mock_client):
        entries = [{"t": "done"}]
        mock_client.safe_api_call = AsyncMock(return_value=entries)
        result = await task_log(mock_client, upid="UPID:pve:000:abc")
        assert "UPID:pve:000:abc" in result

    async def test_task_log_with_limit(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        await task_log(mock_client, upid="UPID:pve:000:abc", node="pve", limit=10)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("limit") == 10

    async def test_task_log_string_entries(self, mock_client):
        entries = ["line 1", "line 2"]
        mock_client.safe_api_call = AsyncMock(return_value=entries)
        result = await task_log(mock_client, upid="UPID:pve:000:abc", node="pve")
        assert "line 1" in result

    async def test_task_log_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await task_log(mock_client, upid="UPID:pve:000:abc", node="bad!node")

    async def test_task_log_empty_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await task_log(mock_client, upid="UPID:pve:000:abc", node="pve")
        assert "0 entries" in result

    async def test_task_log_truncation(self, mock_client):
        entries = [{"n": i, "t": f"line {i}"} for i in range(100)]
        mock_client.safe_api_call = AsyncMock(return_value=entries)
        result = await task_log(mock_client, upid="UPID:pve:000:abc", node="pve")
        assert "more entries" in result


class TestStopTask:
    async def test_stop_task_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await stop_task(mock_client, node="pve", upid="UPID:pve:000:abc")

    async def test_stop_task_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await stop_task(client, node="pve", upid="UPID:pve:000:abc", confirm=True)

    async def test_stop_task_requires_upid(self, mock_client):
        with pytest.raises(ValueError, match="upid is required"):
            await stop_task(mock_client, node="pve", upid="", confirm=True)

    async def test_stop_task_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await stop_task(mock_client, node="pve", upid="UPID:pve:000:abc", confirm=True)
        assert "UPID:pve:000:abc" in result
        assert "stopped" in result

    async def test_stop_task_string_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="OK")
        result = await stop_task(mock_client, node="pve", upid="UPID:pve:000:abc", confirm=True)
        assert "OK" in result

    async def test_stop_task_default_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="OK")
        result = await stop_task(mock_client, upid="UPID:pve:000:abc", confirm=True)
        assert "pve" in result

    async def test_stop_task_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await stop_task(mock_client, node="bad!node", upid="UPID:pve:000:abc", confirm=True)
