from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.exceptions import ProxmoxPermissionError
from proxmox_mcp.storage import (
    create_storage,
    delete_storage,
    delete_volume,
    get_storage,
    list_isos,
    prune_backups,
    storage_status,
    update_storage,
    upload_iso,
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
    async def test_upload_iso_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await upload_iso(mock_client, node="pve", storage="local", filepath="/tmp/debian.iso")

    async def test_create_storage_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_storage(mock_client, storage="mystorage", type="dir")

    async def test_update_storage_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_storage(mock_client, storage="mystorage", content="images")

    async def test_delete_storage_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_storage(mock_client, storage="mystorage")

    async def test_delete_volume_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_volume(mock_client, node="pve", storage="local", volume="local:iso/test.iso")

    async def test_prune_backups_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await prune_backups(mock_client, node="pve", storage="local")


class TestElevatedCheck:
    async def test_upload_iso_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await upload_iso(client, node="pve", storage="local", filepath="/tmp/debian.iso", confirm=True)

    async def test_create_storage_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_storage(client, storage="mystorage", type="dir", confirm=True)

    async def test_update_storage_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_storage(client, storage="mystorage", content="images", confirm=True)

    async def test_delete_storage_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_storage(client, storage="mystorage", confirm=True)

    async def test_delete_volume_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_volume(client, node="pve", storage="local", volume="local:iso/test.iso", confirm=True)

    async def test_prune_backups_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await prune_backups(client, node="pve", storage="local", confirm=True)


class TestListIsos:
    async def test_list_isos_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"volid": "local:iso/debian-12.iso", "size": 4000000000, "content": "iso"},
                {"volid": "local:iso/ubuntu-24.04.iso", "size": 5000000000, "content": "iso"},
            ]
        )
        result = await list_isos(mock_client, node="pve", storage="local")
        assert "debian-12" in result
        assert "ubuntu-24.04" in result
        mock_client.safe_api_call.assert_called_once()

    async def test_list_isos_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_isos(mock_client, node="pve")
        assert "No ISOs found" in result

    async def test_list_isos_passes_content_filter(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        await list_isos(mock_client, node="pve", storage="local-lvm")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["content"] == "iso"


class TestUploadIso:
    async def test_upload_iso_with_filepath(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0400:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = await upload_iso(
                mock_client,
                node="pve",
                storage="local",
                filepath="/tmp/debian-12.iso",
                confirm=True,
            )
        assert "UPID" in result
        assert "upload" in result.lower()
        mock_client.upload.assert_called_once()
        call_kwargs = mock_client.upload.call_args[1]
        assert call_kwargs["content_type"] == "iso"
        assert call_kwargs["node"] == "pve"
        assert call_kwargs["storage"] == "local"
        assert call_kwargs["filename"] == "debian-12.iso"

    async def test_upload_iso_no_filepath_raises(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            await upload_iso(mock_client, node="pve", storage="local", confirm=True)

    async def test_upload_iso_resolves_node(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0401:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = await upload_iso(
                mock_client,
                storage="local",
                filepath="/tmp/debian.iso",
                confirm=True,
            )
        assert "pve" in result


class TestUploadPathValidation:
    async def test_upload_iso_blocks_traversal(self, mock_client):
        mock_client.config.upload_dir = "/tmp/proxmox-mcp-uploads"
        with pytest.raises(ProxmoxPermissionError, match="outside allowed upload directory"):
            await upload_iso(
                mock_client,
                node="pve",
                storage="local",
                filepath="/etc/shadow",
                confirm=True,
            )

    async def test_upload_iso_allows_file_in_upload_dir(self, mock_client):
        mock_client.config.upload_dir = "/tmp/proxmox-mcp-uploads"
        mock_client.upload = MagicMock(return_value="UPID:pve:0402:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = await upload_iso(
                mock_client,
                node="pve",
                storage="local",
                filepath="/tmp/proxmox-mcp-uploads/debian.iso",
                confirm=True,
            )
        assert "UPID" in result

    async def test_upload_iso_no_upload_dir_warns_but_allows(self, mock_client):
        mock_client.config.upload_dir = None
        mock_client.upload = MagicMock(return_value="UPID:pve:0403:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = await upload_iso(
                mock_client,
                node="pve",
                storage="local",
                filepath="/tmp/debian.iso",
                confirm=True,
            )
        assert "UPID" in result


class TestGetStorage:
    async def test_get_storage_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "storage": "local",
                "type": "dir",
                "content": "iso,vztmpl,backup",
                "path": "/var/lib/vz",
                "shared": 0,
                "active": 1,
                "nodes": "pve",
            }
        )
        result = await get_storage(mock_client, storage="local")
        assert "local" in result
        assert "dir" in result
        mock_client.safe_api_call.assert_called_once()

    async def test_get_storage_with_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "storage": "local",
                "type": "dir",
                "content": "iso,vztmpl,backup",
                "path": "/var/lib/vz",
                "shared": 0,
                "active": 1,
            }
        )
        result = await get_storage(mock_client, storage="local", node="pve")
        assert "local" in result
        assert "pve" in result

    async def test_get_storage_validates_name(self, mock_client):
        with pytest.raises(ValueError, match="Invalid storage name"):
            await get_storage(mock_client, storage="")


class TestCreateStorage:
    async def test_create_storage(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_storage(
            mock_client,
            storage="mystorage",
            type="dir",
            path="/mnt/data",
            content="iso,images",
            nodes="pve",
            confirm=True,
        )
        assert "mystorage" in result
        assert "created" in result.lower()
        mock_client.safe_api_call.assert_called_once()

    async def test_create_storage_validates_name(self, mock_config):
        mock_config.allow_elevated = True
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Invalid storage name"):
            await create_storage(client, storage="", type="dir", confirm=True)


class TestUpdateStorage:
    async def test_update_storage(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_storage(
            mock_client,
            storage="local",
            content="iso,vztmpl",
            confirm=True,
        )
        assert "local" in result
        assert "updated" in result.lower()

    async def test_update_storage_with_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_storage(
            mock_client,
            storage="local",
            delete="nodes",
            confirm=True,
        )
        assert "updated" in result.lower()


class TestDeleteStorage:
    async def test_delete_storage(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_storage(mock_client, storage="mystorage", confirm=True)
        assert "mystorage" in result
        assert "deleted" in result.lower()


class TestDeleteVolume:
    async def test_delete_volume(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_volume(
            mock_client,
            node="pve",
            storage="local",
            volume="local:iso/test.iso",
            confirm=True,
        )
        assert "test.iso" in result
        assert "deleted" in result.lower()

    async def test_delete_volume_requires_volume(self, mock_client):
        with pytest.raises(ValueError, match="volume is required"):
            await delete_volume(mock_client, node="pve", storage="local", volume="", confirm=True)

    async def test_delete_volume_resolves_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_volume(
            mock_client,
            storage="local",
            volume="local:iso/test.iso",
            confirm=True,
        )
        assert "pve" in result


class TestPruneBackups:
    async def test_prune_backups(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0500:abc")
        result = await prune_backups(mock_client, node="pve", storage="local", confirm=True)
        assert "pve" in result
        assert "prune" in result.lower()

    async def test_prune_backups_with_type(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0501:abc")
        result = await prune_backups(
            mock_client,
            node="pve",
            storage="local",
            prune_type="keep-last",
            confirm=True,
        )
        assert "prune" in result.lower()
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["prune_type"] == "keep-last"


class TestStorageStatus:
    async def test_storage_status_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "total": 107374182400,
                "used": 53687091200,
                "avail": 53687091200,
                "content": "iso,vztmpl,backup",
                "active": 1,
            }
        )
        result = await storage_status(mock_client, node="pve", storage="local")
        assert "local" in result
        assert "pve" in result
        assert "Total" in result
        mock_client.safe_api_call.assert_called_once()

    async def test_storage_status_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await storage_status(mock_client, node="pve", storage="local")
        assert "local" in result
