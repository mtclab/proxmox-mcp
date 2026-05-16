from unittest.mock import MagicMock, mock_open, patch

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
    def test_upload_iso_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            upload_iso(mock_client, node="pve", storage="local", filepath="/tmp/debian.iso")

    def test_create_storage_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_storage(mock_client, storage="mystorage", type="dir")

    def test_update_storage_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_storage(mock_client, storage="mystorage", content="images")

    def test_delete_storage_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_storage(mock_client, storage="mystorage")

    def test_delete_volume_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_volume(mock_client, node="pve", storage="local", volume="local:iso/test.iso")

    def test_prune_backups_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            prune_backups(mock_client, node="pve", storage="local")


class TestElevatedCheck:
    def test_upload_iso_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            upload_iso(client, node="pve", storage="local", filepath="/tmp/debian.iso", confirm=True)

    def test_create_storage_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_storage(client, storage="mystorage", type="dir", confirm=True)

    def test_update_storage_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_storage(client, storage="mystorage", content="images", confirm=True)

    def test_delete_storage_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_storage(client, storage="mystorage", confirm=True)

    def test_delete_volume_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_volume(client, node="pve", storage="local", volume="local:iso/test.iso", confirm=True)

    def test_prune_backups_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            prune_backups(client, node="pve", storage="local", confirm=True)


class TestListIsos:
    def test_list_isos_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"volid": "local:iso/debian-12.iso", "size": 4000000000, "content": "iso"},
            {"volid": "local:iso/ubuntu-24.04.iso", "size": 5000000000, "content": "iso"},
        ])
        result = list_isos(mock_client, node="pve", storage="local")
        assert "debian-12" in result
        assert "ubuntu-24.04" in result
        mock_client.safe_api_call.assert_called_once()

    def test_list_isos_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_isos(mock_client, node="pve")
        assert "No ISOs found" in result

    def test_list_isos_passes_content_filter(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        list_isos(mock_client, node="pve", storage="local-lvm")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["content"] == "iso"


class TestUploadIso:
    def test_upload_iso_with_filepath(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0400:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_iso(
                mock_client, node="pve", storage="local",
                filepath="/tmp/debian-12.iso", confirm=True,
            )
        assert "UPID" in result
        assert "upload" in result.lower()
        mock_client.upload.assert_called_once()
        call_kwargs = mock_client.upload.call_args[1]
        assert call_kwargs["content_type"] == "iso"
        assert call_kwargs["node"] == "pve"
        assert call_kwargs["storage"] == "local"
        assert call_kwargs["filename"] == "debian-12.iso"

    def test_upload_iso_no_filepath_raises(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            upload_iso(mock_client, node="pve", storage="local", confirm=True)

    def test_upload_iso_resolves_node(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0401:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_iso(
                mock_client, storage="local",
                filepath="/tmp/debian.iso", confirm=True,
            )
        assert "pve" in result


class TestUploadPathValidation:
    def test_upload_iso_blocks_traversal(self, mock_client):
        mock_client.config.upload_dir = "/tmp/proxmox-mcp-uploads"
        with pytest.raises(ProxmoxPermissionError, match="outside allowed upload directory"):
            upload_iso(
                mock_client, node="pve", storage="local",
                filepath="/etc/shadow", confirm=True,
            )

    def test_upload_iso_allows_file_in_upload_dir(self, mock_client):
        mock_client.config.upload_dir = "/tmp/proxmox-mcp-uploads"
        mock_client.upload = MagicMock(return_value="UPID:pve:0402:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_iso(
                mock_client, node="pve", storage="local",
                filepath="/tmp/proxmox-mcp-uploads/debian.iso", confirm=True,
            )
        assert "UPID" in result

    def test_upload_iso_no_upload_dir_warns_but_allows(self, mock_client):
        mock_client.config.upload_dir = None
        mock_client.upload = MagicMock(return_value="UPID:pve:0403:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_iso(
                mock_client, node="pve", storage="local",
                filepath="/tmp/debian.iso", confirm=True,
            )
        assert "UPID" in result


class TestGetStorage:
    def test_get_storage_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "storage": "local",
            "type": "dir",
            "content": "iso,vztmpl,backup",
            "path": "/var/lib/vz",
            "shared": 0,
            "active": 1,
            "nodes": "pve",
        })
        result = get_storage(mock_client, storage="local")
        assert "local" in result
        assert "dir" in result
        mock_client.safe_api_call.assert_called_once()

    def test_get_storage_with_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "storage": "local",
            "type": "dir",
            "content": "iso,vztmpl,backup",
            "path": "/var/lib/vz",
            "shared": 0,
            "active": 1,
        })
        result = get_storage(mock_client, storage="local", node="pve")
        assert "local" in result
        assert "pve" in result

    def test_get_storage_validates_name(self, mock_client):
        with pytest.raises(ValueError, match="Invalid storage name"):
            get_storage(mock_client, storage="")


class TestCreateStorage:
    def test_create_storage(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_storage(
            mock_client, storage="mystorage", type="dir",
            path="/mnt/data", content="iso,images", nodes="pve", confirm=True,
        )
        assert "mystorage" in result
        assert "created" in result.lower()
        mock_client.safe_api_call.assert_called_once()

    def test_create_storage_validates_name(self, mock_config):
        mock_config.allow_elevated = True
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Invalid storage name"):
            create_storage(client, storage="", type="dir", confirm=True)


class TestUpdateStorage:
    def test_update_storage(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_storage(
            mock_client, storage="local", content="iso,vztmpl", confirm=True,
        )
        assert "local" in result
        assert "updated" in result.lower()

    def test_update_storage_with_delete(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_storage(
            mock_client, storage="local", delete="nodes", confirm=True,
        )
        assert "updated" in result.lower()


class TestDeleteStorage:
    def test_delete_storage(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_storage(mock_client, storage="mystorage", confirm=True)
        assert "mystorage" in result
        assert "deleted" in result.lower()


class TestDeleteVolume:
    def test_delete_volume(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_volume(
            mock_client, node="pve", storage="local",
            volume="local:iso/test.iso", confirm=True,
        )
        assert "test.iso" in result
        assert "deleted" in result.lower()

    def test_delete_volume_requires_volume(self, mock_client):
        with pytest.raises(ValueError, match="volume is required"):
            delete_volume(mock_client, node="pve", storage="local", volume="", confirm=True)

    def test_delete_volume_resolves_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_volume(
            mock_client, storage="local",
            volume="local:iso/test.iso", confirm=True,
        )
        assert "pve" in result


class TestPruneBackups:
    def test_prune_backups(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0500:abc")
        result = prune_backups(mock_client, node="pve", storage="local", confirm=True)
        assert "pve" in result
        assert "prune" in result.lower()

    def test_prune_backups_with_type(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0501:abc")
        result = prune_backups(
            mock_client, node="pve", storage="local",
            prune_type="keep-last", confirm=True,
        )
        assert "prune" in result.lower()
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["prune_type"] == "keep-last"


class TestStorageStatus:
    def test_storage_status_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "total": 107374182400,
            "used": 53687091200,
            "avail": 53687091200,
            "content": "iso,vztmpl,backup",
            "active": 1,
        })
        result = storage_status(mock_client, node="pve", storage="local")
        assert "local" in result
        assert "pve" in result
        assert "Total" in result
        mock_client.safe_api_call.assert_called_once()

    def test_storage_status_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = storage_status(mock_client, node="pve", storage="local")
        assert "local" in result
