from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.backups import create_backup, list_backups, restore_backup
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


class TestConfirmRequired:
    def test_create_backup_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_backup(mock_client, node="pve", vmid=100)

    def test_restore_backup_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            restore_backup(mock_client, vmid=100, archive="local:backup/vzdump.qemu")


class TestElevatedCheck:
    def test_create_backup_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_backup(client, node="pve", vmid=100, confirm=True)

    def test_restore_backup_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            restore_backup(client, vmid=100, archive="local:backup/vzdump.qemu", confirm=True)


class TestListBackups:
    def test_list_backups_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"volid": "local:backup/vzdump-qemu-100.vma.zst", "size": 1073741824, "content": "backup"},
            {"volid": "local:backup/vzdump-lxc-200.tar.zst", "size": 536870912, "content": "backup"},
        ])
        result = list_backups(mock_client, node="pve", storage="local")
        assert "vzdump-qemu-100" in result
        assert "vzdump-lxc-200" in result
        mock_client.safe_api_call.assert_called_once()

    def test_list_backups_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_backups(mock_client, node="pve")
        assert "No backups found" in result

    def test_list_backups_passes_content_filter(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        list_backups(mock_client, node="pve", storage="local-lvm")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["content"] == "backup"


class TestCreateBackup:
    def test_create_backup(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0200:abc")
        result = create_backup(
            mock_client, node="pve", vmid=100, confirm=True
        )
        assert "UPID" in result
        assert "qemu 100" in result

    def test_create_backup_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0201:abc")
        result = create_backup(
            mock_client, node="pve", vmid=200, vmtype="lxc", confirm=True
        )
        assert "lxc 200" in result

    def test_create_backup_with_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0202:abc")
        create_backup(
            mock_client, node="pve", vmid=100, storage="local",
            mode="stop", compress="gzip", confirm=True,
        )
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["storage"] == "local"
        assert call_args[1]["mode"] == "stop"
        assert call_args[1]["compress"] == "gzip"


class TestRestoreBackup:
    def test_restore_backup(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0203:abc")
        result = restore_backup(
            mock_client, vmid=100,
            archive="local:backup/vzdump-qemu-100.vma.zst",
            confirm=True,
        )
        assert "UPID" in result
        assert "100" in result

    def test_restore_backup_no_archive_raises(self, mock_client):
        with pytest.raises(ValueError, match="archive is required"):
            restore_backup(mock_client, vmid=100, confirm=True)
