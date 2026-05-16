from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.cluster import (
    api_version,
    backup_info_not_backed_up,
    bulk_migrate_guests,
    bulk_shutdown_guests,
    bulk_start_guests,
    bulk_suspend_guests,
    cluster_config,
    cluster_config_join,
    cluster_config_nodes,
    cluster_options,
    cluster_status,
    create_backup_job,
    delete_backup_job,
    get_backup_job,
    list_backup_jobs,
    update_backup_job,
    update_cluster_options,
)
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
    admin_mock = MagicMock()
    client.admin_client = admin_mock
    client.monitor_client = MagicMock()
    return client


class TestClusterStatus:
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


class TestClusterOptions:
    async def test_cluster_options_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "keyboard": "en-us",
                "http_proxy": "",
                "migration": {"type": "secure"},
            }
        )
        result = await cluster_options(mock_client)
        assert "keyboard" in result
        assert "en-us" in result

    async def test_cluster_options_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await cluster_options(mock_client)
        assert "No cluster options" in result


class TestUpdateClusterOptions:
    async def test_update_cluster_options_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_cluster_options(mock_client, keyboard="en-us")

    async def test_update_cluster_options_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_cluster_options(client, confirm=True, keyboard="en-us")

    async def test_update_cluster_options_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            await update_cluster_options(mock_client, confirm=True)

    async def test_update_cluster_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_cluster_options(mock_client, confirm=True, keyboard="de")
        assert "keyboard" in result
        assert "updated" in result.lower()


class TestListBackupJobs:
    async def test_list_backup_jobs_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "backup-vm100", "schedule": "0 2 * * *", "vmid": "100", "storage": "local", "mode": "snapshot"},
            ]
        )
        result = await list_backup_jobs(mock_client)
        assert "backup-vm100" in result
        assert "0 2 * * *" in result

    async def test_list_backup_jobs_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_backup_jobs(mock_client)
        assert "No backup jobs" in result


class TestCreateBackupJob:
    async def test_create_backup_job_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_backup_job(mock_client, id="backup-1")

    async def test_create_backup_job_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_backup_job(client, id="backup-1", confirm=True)

    async def test_create_backup_job_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await create_backup_job(mock_client, id="", confirm=True)

    async def test_create_backup_job(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_backup_job(
            mock_client,
            id="backup-1",
            schedule="0 2 * * *",
            storage="local",
            mode="snapshot",
            confirm=True,
        )
        assert "backup-1" in result
        assert "created" in result.lower()

    async def test_create_backup_job_with_compress(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_backup_job(
            mock_client,
            id="backup-2",
            schedule="0 3 * * *",
            vmid="100",
            storage="nfs-backup",
            mode="stop",
            compress="zstd",
            confirm=True,
        )
        assert "backup-2" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["compress"] == "zstd"
        assert call_args[1]["vmid"] == "100"


class TestDeleteBackupJob:
    async def test_delete_backup_job_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_backup_job(mock_client, id="backup-1")

    async def test_delete_backup_job_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_backup_job(client, id="backup-1", confirm=True)

    async def test_delete_backup_job_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_backup_job(mock_client, id="", confirm=True)

    async def test_delete_backup_job(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_backup_job(mock_client, id="backup-1", confirm=True)
        assert "backup-1" in result
        assert "deleted" in result.lower()


class TestGetBackupJob:
    async def test_get_backup_job(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "id": "backup-1",
                "schedule": "0 2 * * *",
                "vmid": "100",
            }
        )
        result = await get_backup_job(mock_client, id="backup-1")
        assert "backup-1" in result
        assert "schedule" in result

    async def test_get_backup_job_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_backup_job(mock_client, id="")


class TestUpdateBackupJob:
    async def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_backup_job(mock_client, id="backup-1", schedule="0 3 * * *")

    async def test_update_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_backup_job(client, id="backup-1", schedule="0 3 * * *", confirm=True)

    async def test_update_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await update_backup_job(mock_client, id="", schedule="0 3 * * *", confirm=True)

    async def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await update_backup_job(mock_client, id="backup-1", confirm=True)

    async def test_update_backup_job(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_backup_job(mock_client, id="backup-1", schedule="0 3 * * *", confirm=True)
        assert "backup-1" in result
        assert "updated" in result.lower()


class TestClusterConfig:
    async def test_cluster_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"version": "1", "nodes": {"pve": {"votes": 1}}},
            }
        )
        result = await cluster_config(mock_client)
        assert "Cluster Config" in result

    async def test_cluster_config_nodes(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "pve", "nodeid": 1, "votes": 1},
            ]
        )
        result = await cluster_config_nodes(mock_client)
        assert "pve" in result
        assert "Cluster Config Nodes" in result

    async def test_cluster_config_nodes_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await cluster_config_nodes(mock_client)
        assert "No cluster config nodes" in result

    async def test_cluster_config_join(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "nodelist": [{"name": "pve"}],
                "fingerprints": "abc123",
            }
        )
        result = await cluster_config_join(mock_client)
        assert "Cluster Join" in result


class TestBackupInfoNotBackedUp:
    async def test_backup_info_not_backed_up(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"vmid": 100, "name": "test-vm", "type": "qemu"},
            ]
        )
        result = await backup_info_not_backed_up(mock_client)
        assert "100" in result
        assert "Not Backed Up" in result

    async def test_backup_info_not_backed_up_all_backed(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await backup_info_not_backed_up(mock_client)
        assert "All guests have backups" in result


class TestApiVersion:
    async def test_api_version(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"version": "8.1.0", "release": "8.1"},
            }
        )
        result = await api_version(mock_client)
        assert "API Version" in result
        assert "8.1.0" in result


class TestBulkMigrateGuests:
    async def test_bulk_migrate_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await bulk_migrate_guests(mock_client, vmids="100,101", target="pve2")

    async def test_bulk_migrate_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await bulk_migrate_guests(client, vmids="100,101", target="pve2", confirm=True)

    async def test_bulk_migrate_no_vmids_raises(self, mock_client):
        with pytest.raises(ValueError, match="vmids is required"):
            await bulk_migrate_guests(mock_client, vmids="", target="pve2", confirm=True)

    async def test_bulk_migrate_no_target_raises(self, mock_client):
        with pytest.raises(ValueError, match="target node is required"):
            await bulk_migrate_guests(mock_client, vmids="100", target="", confirm=True)

    async def test_bulk_migrate_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0800:migrate"})
        result = await bulk_migrate_guests(mock_client, vmids="100,101", target="pve2", confirm=True)
        assert "UPID" in result
        assert "pve2" in result


class TestBulkShutdownGuests:
    async def test_bulk_shutdown_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await bulk_shutdown_guests(mock_client, vmids="100,101")

    async def test_bulk_shutdown_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await bulk_shutdown_guests(client, vmids="100,101", confirm=True)

    async def test_bulk_shutdown_no_vmids_raises(self, mock_client):
        with pytest.raises(ValueError, match="vmids is required"):
            await bulk_shutdown_guests(mock_client, vmids="", confirm=True)

    async def test_bulk_shutdown_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0801:shutdown"})
        result = await bulk_shutdown_guests(mock_client, vmids="100,101", confirm=True)
        assert "UPID" in result


class TestBulkStartGuests:
    async def test_bulk_start_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await bulk_start_guests(mock_client, vmids="100,101")

    async def test_bulk_start_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await bulk_start_guests(client, vmids="100,101", confirm=True)

    async def test_bulk_start_no_vmids_raises(self, mock_client):
        with pytest.raises(ValueError, match="vmids is required"):
            await bulk_start_guests(mock_client, vmids="", confirm=True)

    async def test_bulk_start_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0802:start"})
        result = await bulk_start_guests(mock_client, vmids="100,101", confirm=True)
        assert "UPID" in result


class TestBulkSuspendGuests:
    async def test_bulk_suspend_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await bulk_suspend_guests(mock_client, vmids="100,101")

    async def test_bulk_suspend_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await bulk_suspend_guests(client, vmids="100,101", confirm=True)

    async def test_bulk_suspend_no_vmids_raises(self, mock_client):
        with pytest.raises(ValueError, match="vmids is required"):
            await bulk_suspend_guests(mock_client, vmids="", confirm=True)

    async def test_bulk_suspend_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0803:suspend"})
        result = await bulk_suspend_guests(mock_client, vmids="100,101", confirm=True)
        assert "UPID" in result
