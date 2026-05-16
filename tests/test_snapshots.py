from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.snapshots import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    rollback_snapshot,
    snapshot_config,
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
    async def test_create_snapshot_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_snapshot(mock_client, node="pve", vmid=100, snapname="snap1")

    async def test_delete_snapshot_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_snapshot(mock_client, node="pve", vmid=100, snapname="snap1")

    async def test_rollback_snapshot_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await rollback_snapshot(mock_client, node="pve", vmid=100, snapname="snap1")


class TestElevatedCheck:
    async def test_create_snapshot_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_snapshot(client, node="pve", vmid=100, snapname="snap1", confirm=True)

    async def test_delete_snapshot_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_snapshot(client, node="pve", vmid=100, snapname="snap1", confirm=True)

    async def test_rollback_snapshot_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await rollback_snapshot(client, node="pve", vmid=100, snapname="snap1", confirm=True)


class TestVmtypeValidation:
    async def test_list_snapshots_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await list_snapshots(mock_client, node="pve", vmid=100, vmtype="malicious")

    async def test_create_snapshot_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await create_snapshot(mock_client, node="pve", vmid=100, snapname="snap1", vmtype="evil", confirm=True)

    async def test_delete_snapshot_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await delete_snapshot(mock_client, node="pve", vmid=100, snapname="snap1", vmtype="evil", confirm=True)

    async def test_rollback_snapshot_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await rollback_snapshot(mock_client, node="pve", vmid=100, snapname="snap1", vmtype="evil", confirm=True)

    async def test_snapshot_config_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await snapshot_config(mock_client, node="pve", vmid=100, snapname="snap1", vmtype="evil")

    async def test_list_snapshots_valid_vmtype_qemu(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_snapshots(mock_client, node="pve", vmid=100, vmtype="qemu")
        assert "No snapshots found" in result

    async def test_list_snapshots_valid_vmtype_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_snapshots(mock_client, node="pve", vmid=100, vmtype="lxc")
        assert "No snapshots found" in result


class TestListSnapshots:
    async def test_list_snapshots_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "snap1", "description": "before update", "parent": "base"},
                {"name": "snap2", "description": "", "parent": "snap1"},
            ]
        )
        result = await list_snapshots(mock_client, node="pve", vmid=100)
        assert "snap1" in result
        assert "snap2" in result
        mock_client.safe_api_call.assert_called_once()

    async def test_list_snapshots_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_snapshots(mock_client, node="pve", vmid=100)
        assert "No snapshots found" in result

    async def test_list_snapshots_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "snap1", "parent": ""},
            ]
        )
        result = await list_snapshots(mock_client, node="pve", vmid=200, vmtype="lxc")
        assert "lxc" in result
        assert "snap1" in result


class TestCreateSnapshot:
    async def test_create_snapshot(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0100:abc")
        result = await create_snapshot(mock_client, node="pve", vmid=100, snapname="snap1", confirm=True)
        assert "snap1" in result
        assert "UPID" in result

    async def test_create_snapshot_with_description(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0101:abc")
        result = await create_snapshot(
            mock_client,
            node="pve",
            vmid=100,
            snapname="snap1",
            description="before upgrade",
            confirm=True,
        )
        assert "snap1" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["description"] == "before upgrade"

    async def test_create_snapshot_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0102:abc")
        result = await create_snapshot(
            mock_client,
            node="pve",
            vmid=200,
            snapname="snap1",
            vmtype="lxc",
            confirm=True,
        )
        assert "lxc" in result


class TestDeleteSnapshot:
    async def test_delete_snapshot(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0103:abc")
        result = await delete_snapshot(mock_client, node="pve", vmid=100, snapname="snap1", confirm=True)
        assert "snap1" in result
        assert "deletion" in result


class TestRollbackSnapshot:
    async def test_rollback_snapshot(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0104:abc")
        result = await rollback_snapshot(mock_client, node="pve", vmid=100, snapname="snap1", confirm=True)
        assert "snap1" in result
        assert "Rollback" in result


class TestSnapshotConfig:
    async def test_snapshot_config_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "snapname": "snap1",
                "description": "before upgrade",
                "parent": "base",
                "vmstate": 1,
            }
        )
        result = await snapshot_config(mock_client, node="pve", vmid=100, snapname="snap1")
        assert "snap1" in result
        assert "config" in result
        mock_client.safe_api_call.assert_called_once()

    async def test_snapshot_config_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"snapname": "snap1"})
        result = await snapshot_config(mock_client, node="pve", vmid=200, snapname="snap1", vmtype="lxc")
        assert "lxc" in result
        assert "snap1" in result

    async def test_snapshot_config_no_confirm_needed(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"snapname": "snap1"})
        result = await snapshot_config(mock_client, node="pve", vmid=100, snapname="snap1")
        assert "snap1" in result

    async def test_snapshot_config_uses_monitor_client(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"snapname": "snap1"})
        await snapshot_config(mock_client, node="pve", vmid=100, snapname="snap1")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("elevated") is None or call_args[0][0] is not None
