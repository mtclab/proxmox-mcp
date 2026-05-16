from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.cluster import (
    cluster_config_apiversion,
    cluster_jobs_index,
    get_realm_sync_job,
    list_realm_sync_jobs,
)
from proxmox_mcp.config import Config
from proxmox_mcp.lifecycle import lxc_rrd, vm_rrd
from proxmox_mcp.nodes import query_url_metadata, wake_on_lan
from proxmox_mcp.storage import (
    copy_volume,
    file_restore_download,
    file_restore_list,
    get_storage_on_node,
    oci_registry_pull,
    storage_import_metadata,
    update_volume_attributes,
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


class TestQueryUrlMetadata:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"filename": "test.iso", "size": 1073741824, "mimetype": "application/x-iso9660-image"},
            }
        )
        result = await query_url_metadata(mock_client, node="pve", url="https://example.com/test.iso")
        assert "URL Metadata" in result
        assert "test.iso" in result

    async def test_requires_url(self, mock_client):
        with pytest.raises(ValueError, match="url is required"):
            await query_url_metadata(mock_client, node="pve", url="")


class TestWakeOnLan:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await wake_on_lan(mock_client, node="pve", macaddr="aa:bb:cc:dd:ee:ff")

    async def test_requires_macaddr(self, mock_client):
        with pytest.raises(ValueError, match="macaddr is required"):
            await wake_on_lan(mock_client, node="pve", macaddr="", confirm=True)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await wake_on_lan(client, node="pve", macaddr="aa:bb:cc:dd:ee:ff", confirm=True)

    async def test_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001:abc")
        result = await wake_on_lan(mock_client, node="pve", macaddr="aa:bb:cc:dd:ee:ff", confirm=True)
        assert "Wake-on-LAN" in result
        assert "aa:bb:cc:dd:ee:ff" in result


class TestGetStorageOnNode:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "storage": "local",
                "type": "dir",
                "content": "iso,vztmpl,backup",
            }
        )
        result = await get_storage_on_node(mock_client, node="pve", storage="local")
        assert "Storage Detail" in result
        assert "local" in result

    async def test_empty_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await get_storage_on_node(mock_client, node="pve", storage="local")
        assert "Storage Detail" in result


class TestCopyVolume:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await copy_volume(mock_client, node="pve", storage="local", volume="local:iso/test.iso", target="nfs")

    async def test_requires_volume(self, mock_client):
        with pytest.raises(ValueError, match="volume is required"):
            await copy_volume(mock_client, node="pve", storage="local", volume="", target="nfs", confirm=True)

    async def test_requires_target(self, mock_client):
        with pytest.raises(ValueError, match="target is required"):
            await copy_volume(mock_client, node="pve", storage="local", volume="vol1", target="", confirm=True)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await copy_volume(client, node="pve", storage="local", volume="vol1", target="nfs", confirm=True)

    async def test_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001:abc")
        result = await copy_volume(mock_client, node="pve", storage="local", volume="vol1", target="nfs", confirm=True)
        assert "copy" in result.lower()
        assert "UPID" in result


class TestUpdateVolumeAttributes:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_volume_attributes(mock_client, node="pve", storage="local", volume="vol1", comment="test")

    async def test_requires_volume(self, mock_client):
        with pytest.raises(ValueError, match="volume is required"):
            await update_volume_attributes(
                mock_client, node="pve", storage="local", volume="", confirm=True, comment="test"
            )

    async def test_requires_attributes(self, mock_client):
        with pytest.raises(ValueError, match="At least one attribute"):
            await update_volume_attributes(mock_client, node="pve", storage="local", volume="vol1", confirm=True)

    async def test_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_volume_attributes(
            mock_client,
            node="pve",
            storage="local",
            volume="vol1",
            confirm=True,
            comment="updated",
        )
        assert "updated" in result.lower()


class TestFileRestoreList:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"filename": "backup.vma.zst", "type": "file", "size": 1024},
            ]
        )
        result = await file_restore_list(mock_client, node="pve", storage="local")
        assert "File Restore List" in result
        assert "backup.vma.zst" in result

    async def test_empty_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await file_restore_list(mock_client, node="pve", storage="local")
        assert "No file restore entries" in result


class TestFileRestoreDownload:
    async def test_requires_filepath(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            await file_restore_download(mock_client, node="pve", storage="local", filepath="")

    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"filename": "test.txt", "size": 100},
            }
        )
        result = await file_restore_download(mock_client, node="pve", storage="local", filepath="/etc/hosts")
        assert "File Restore Download" in result


class TestStorageImportMetadata:
    async def test_returns_formatted_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"format": "raw", "type": "disk"},
            }
        )
        result = await storage_import_metadata(
            mock_client, node="pve", storage="local", volume="local:100/vm-100-disk-0.raw"
        )
        assert "Storage Import Metadata" in result

    async def test_returns_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"filename": "disk0.qcow2", "type": "disk"},
            ]
        )
        result = await storage_import_metadata(
            mock_client, node="pve", storage="local", volume="local:100/vm-100-disk-0.raw"
        )
        assert "Storage Import Metadata" in result

    async def test_empty_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await storage_import_metadata(
            mock_client, node="pve", storage="local", volume="local:100/vm-100-disk-0.raw"
        )
        assert "No import metadata" in result

    async def test_requires_volume(self, mock_client):
        with pytest.raises(ValueError, match="volume is required"):
            await storage_import_metadata(mock_client, node="pve", storage="local", volume="")


class TestOciRegistryPull:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await oci_registry_pull(mock_client, node="pve", storage="local", image="ubuntu:latest")

    async def test_requires_image(self, mock_client):
        with pytest.raises(ValueError, match="image is required"):
            await oci_registry_pull(mock_client, node="pve", storage="local", image="", confirm=True)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await oci_registry_pull(client, node="pve", storage="local", image="ubuntu:latest", confirm=True)

    async def test_success(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001:abc")
        result = await oci_registry_pull(mock_client, node="pve", storage="local", image="ubuntu:latest", confirm=True)
        assert "OCI registry pull" in result
        assert "ubuntu:latest" in result


class TestClusterConfigApiversion:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"version": "1.0", "release": "8.0"},
            }
        )
        result = await cluster_config_apiversion(mock_client)
        assert "Cluster API Version" in result
        assert "version" in result

    async def test_empty_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await cluster_config_apiversion(mock_client)
        assert "Cluster API Version" in result


class TestClusterJobsIndex:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "job1", "type": "realm-sync"},
                {"id": "job2", "type": "backup"},
            ]
        )
        result = await cluster_jobs_index(mock_client)
        assert "Cluster Jobs" in result
        assert "job1" in result

    async def test_empty_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await cluster_jobs_index(mock_client)
        assert "No cluster jobs" in result


class TestListRealmSyncJobs:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "sync1", "realm": "ldap", "schedule": "0 2 * * *"},
            ]
        )
        result = await list_realm_sync_jobs(mock_client)
        assert "Realm Sync Jobs" in result
        assert "sync1" in result

    async def test_empty_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_realm_sync_jobs(mock_client)
        assert "No realm sync jobs" in result


class TestGetRealmSyncJob:
    async def test_requires_id(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_realm_sync_job(mock_client, id="")

    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "id": "sync1",
                "realm": "ldap",
                "schedule": "0 2 * * *",
            }
        )
        result = await get_realm_sync_job(mock_client, id="sync1")
        assert "Realm Sync Job" in result
        assert "sync1" in result


class TestVmRrd:
    async def test_returns_formatted_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "cpu": 0.5,
                "maxcpu": 4,
            }
        )
        result = await vm_rrd(mock_client, node="pve", vmid=100)
        assert "VM 100 RRD" in result

    async def test_returns_binary(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=b"\x89PNG")
        result = await vm_rrd(mock_client, node="pve", vmid=100)
        assert "RRD" in result


class TestLxcRrd:
    async def test_returns_formatted_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "cpu": 0.3,
                "maxcpu": 2,
            }
        )
        result = await lxc_rrd(mock_client, node="pve", vmid=200)
        assert "LXC 200 RRD" in result

    async def test_returns_binary(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=b"\x89PNG")
        result = await lxc_rrd(mock_client, node="pve", vmid=200)
        assert "RRD" in result
