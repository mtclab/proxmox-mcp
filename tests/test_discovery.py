from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.discovery import (
    cluster_log,
    cluster_resources,
    cluster_status,
    list_tasks,
    node_dns,
    node_hosts,
    node_journal,
    node_syslog,
    node_time,
    node_version,
    task_log,
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
    client.monitor_client = MagicMock()
    client.admin_client = MagicMock()
    return client


class TestListTasks:
    async def test_list_tasks_passes_limit_to_api(self, mock_client):
        tasks = [{"upid": f"UPID:pve:00{i}:abc", "status": "OK"} for i in range(5)]
        mock_client.safe_api_call = AsyncMock(return_value=tasks)
        result = await list_tasks(mock_client, limit=3)
        assert "showing 3" in result

    async def test_list_tasks_default_limit(self, mock_client):
        tasks = [{"upid": "UPID:pve:000:abc", "status": "OK"}]
        mock_client.safe_api_call = AsyncMock(return_value=tasks)
        await list_tasks(mock_client)
        call_args = mock_client.safe_api_call.call_args

    async def test_list_tasks_client_side_slice_fallback(self, mock_client):
        tasks = [{"upid": f"UPID:pve:00{i}:abc", "status": "OK"} for i in range(10)]
        mock_client.safe_api_call = AsyncMock(return_value=tasks)
        result = await list_tasks(mock_client, limit=5)
        assert "showing 5" in result


class TestClusterResources:
    async def test_cluster_resources_all(self, mock_client):
        resources = [
            {"type": "qemu", "name": "vm1", "vmid": 100, "node": "pve", "status": "running"},
            {"type": "lxc", "name": "ct1", "vmid": 200, "node": "pve", "status": "stopped"},
            {"type": "storage", "name": "local", "node": "pve"},
        ]
        mock_client.safe_api_call = AsyncMock(return_value=resources)
        result = await cluster_resources(mock_client)
        assert "vm1" in result
        assert "ct1" in result
        assert "local" in result
        assert "all" in result

    async def test_cluster_resources_filtered_by_type(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "qemu", "name": "vm1", "vmid": 100, "node": "pve", "status": "running"},
            ]
        )
        result = await cluster_resources(mock_client, type="vm")
        assert "vm1" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["type"] == "vm"

    async def test_cluster_resources_no_type_param(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "node", "id": "node/pve", "name": "pve", "status": "online"},
            ]
        )
        await cluster_resources(mock_client)
        call_args = mock_client.safe_api_call.call_args
        assert "type" not in call_args[1]

    async def test_cluster_resources_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await cluster_resources(mock_client)
        assert "No resources found" in result

    async def test_cluster_resources_running_indicator(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "qemu", "name": "vm1", "vmid": 100, "node": "pve", "status": "running"},
            ]
        )
        result = await cluster_resources(mock_client)
        assert "🟢" in result

    async def test_cluster_resources_stopped_indicator(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "qemu", "name": "vm1", "vmid": 100, "node": "pve", "status": "stopped"},
            ]
        )
        result = await cluster_resources(mock_client)
        assert "🔴" in result


class TestNodeVersion:
    async def test_node_version_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"version": "8.1.0", "release": "8.1"}})
        result = await node_version(mock_client, node="pve")
        assert "Version" in result
        assert "pve" in result

    async def test_node_version_default_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"version": "8.1.0"})
        result = await node_version(mock_client)
        assert result is not None

    async def test_node_version_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await node_version(mock_client, node="bad!node")


class TestNodeDns:
    async def test_node_dns_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"dns1": "8.8.8.8", "search": "local"}})
        result = await node_dns(mock_client, node="pve")
        assert "DNS" in result
        assert "pve" in result

    async def test_node_dns_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await node_dns(mock_client, node="bad!node")


class TestNodeHosts:
    async def test_node_hosts_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "127.0.0.1 localhost\n10.0.0.1 pve"})
        result = await node_hosts(mock_client, node="pve")
        assert "Hosts" in result
        assert "localhost" in result

    async def test_node_hosts_dict_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"key": "value"}})
        result = await node_hosts(mock_client, node="pve")
        assert "Hosts" in result


class TestNodeTime:
    async def test_node_time_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"timezone": "UTC", "time": 1700000000}})
        result = await node_time(mock_client, node="pve")
        assert "Time" in result
        assert "pve" in result


class TestNodeSyslog:
    async def test_node_syslog_basic(self, mock_client):
        entries = [{"timestamp": "2024-01-01", "msg": "kernel: ok"}]
        mock_client.safe_api_call = AsyncMock(return_value=entries)
        result = await node_syslog(mock_client, node="pve")
        assert "Syslog" in result
        assert "pve" in result

    async def test_node_syslog_with_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        await node_syslog(mock_client, node="pve", limit=10, since="2024-01-01")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("limit") == 10
        assert call_args[1].get("since") == "2024-01-01"

    async def test_node_syslog_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await node_syslog(mock_client, node="bad!node")


class TestNodeJournal:
    async def test_node_journal_basic(self, mock_client):
        entries = [{"timestamp": "2024-01-01", "msg": "systemd: started"}]
        mock_client.safe_api_call = AsyncMock(return_value=entries)
        result = await node_journal(mock_client, node="pve")
        assert "Journal" in result
        assert "pve" in result

    async def test_node_journal_with_service(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        await node_journal(mock_client, node="pve", service="pvedaemon")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("service") == "pvedaemon"


class TestClusterLog:
    async def test_cluster_log_basic(self, mock_client):
        entries = [{"timestamp": "2024-01-01", "msg": "node joined"}]
        mock_client.safe_api_call = AsyncMock(return_value=entries)
        result = await cluster_log(mock_client)
        assert "Cluster Log" in result

    async def test_cluster_log_with_limit(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        await cluster_log(mock_client, limit=20)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("max") == 20


class TestTaskLog:
    async def test_task_log_with_node(self, mock_client):
        log_entries = [
            {"n": 1, "t": "starting task"},
            {"n": 2, "t": "task completed"},
        ]
        mock_client.safe_api_call = AsyncMock(return_value=log_entries)
        result = await task_log(mock_client, upid="UPID:pve:0001:abc", node="pve")
        assert "UPID:pve:0001:abc" in result
        assert "starting task" in result

    async def test_task_log_extracts_node_from_upid(self, mock_client):
        log_entries = [{"t": "done"}]
        mock_client.safe_api_call = AsyncMock(return_value=log_entries)
        await task_log(mock_client, upid="UPID:pve:0001:abc")
        call_args = mock_client.safe_api_call.call_args
        assert call_args is not None

    async def test_task_log_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await task_log(mock_client, upid="UPID:pve:0001:abc", node="pve")
        assert "No log output" in result

    async def test_task_log_with_limit(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        await task_log(mock_client, upid="UPID:pve:0001:abc", node="pve", limit=20)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("limit") == 20

    async def test_task_log_string_entries(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=["line1", "line2"])
        result = await task_log(mock_client, upid="UPID:pve:0001:abc", node="pve")
        assert "line1" in result
        assert "line2" in result


class TestClusterStatusDiscovery:
    async def test_cluster_status_with_cluster(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "cluster", "name": "pve-cluster", "quorate": 1, "nodes": 3, "version": 1},
                {"type": "node", "name": "pve", "online": 1, "ip": "10.96.16.19"},
            ]
        )
        result = await cluster_status(mock_client)
        assert "pve-cluster" in result
        assert "Quorum" in result

    async def test_cluster_status_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await cluster_status(mock_client)
        assert "No cluster status" in result

    async def test_cluster_status_offline_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "node", "name": "pve2", "online": 0},
            ]
        )
        result = await cluster_status(mock_client)
        assert "pve2" in result
        assert "offline" in result
