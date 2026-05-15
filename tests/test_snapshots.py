from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.snapshots import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    rollback_snapshot,
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
    def test_create_snapshot_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_snapshot(mock_client, node="pve", vmid=100, snapname="snap1")

    def test_delete_snapshot_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_snapshot(mock_client, node="pve", vmid=100, snapname="snap1")

    def test_rollback_snapshot_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            rollback_snapshot(mock_client, node="pve", vmid=100, snapname="snap1")


class TestElevatedCheck:
    def test_create_snapshot_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_snapshot(client, node="pve", vmid=100, snapname="snap1", confirm=True)

    def test_delete_snapshot_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_snapshot(client, node="pve", vmid=100, snapname="snap1", confirm=True)

    def test_rollback_snapshot_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            rollback_snapshot(client, node="pve", vmid=100, snapname="snap1", confirm=True)


class TestListSnapshots:
    def test_list_snapshots_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "snap1", "description": "before update", "parent": "base"},
            {"name": "snap2", "description": "", "parent": "snap1"},
        ])
        result = list_snapshots(mock_client, node="pve", vmid=100)
        assert "snap1" in result
        assert "snap2" in result
        mock_client.safe_api_call.assert_called_once()

    def test_list_snapshots_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_snapshots(mock_client, node="pve", vmid=100)
        assert "No snapshots found" in result

    def test_list_snapshots_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "snap1", "parent": ""},
        ])
        result = list_snapshots(mock_client, node="pve", vmid=200, vmtype="lxc")
        assert "lxc" in result
        assert "snap1" in result


class TestCreateSnapshot:
    def test_create_snapshot(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0100:abc")
        result = create_snapshot(
            mock_client, node="pve", vmid=100, snapname="snap1", confirm=True
        )
        assert "snap1" in result
        assert "UPID" in result

    def test_create_snapshot_with_description(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0101:abc")
        result = create_snapshot(
            mock_client, node="pve", vmid=100, snapname="snap1",
            description="before upgrade", confirm=True,
        )
        assert "snap1" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["description"] == "before upgrade"

    def test_create_snapshot_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0102:abc")
        result = create_snapshot(
            mock_client, node="pve", vmid=200, snapname="snap1",
            vmtype="lxc", confirm=True,
        )
        assert "lxc" in result


class TestDeleteSnapshot:
    def test_delete_snapshot(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0103:abc")
        result = delete_snapshot(
            mock_client, node="pve", vmid=100, snapname="snap1", confirm=True
        )
        assert "snap1" in result
        assert "deletion" in result


class TestRollbackSnapshot:
    def test_rollback_snapshot(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0104:abc")
        result = rollback_snapshot(
            mock_client, node="pve", vmid=100, snapname="snap1", confirm=True
        )
        assert "snap1" in result
        assert "Rollback" in result
