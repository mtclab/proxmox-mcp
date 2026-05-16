from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.disks import (
    get_disk_smart,
    init_gpt,
    list_disks,
    list_lvm,
    list_lvmthin,
    list_zfs,
    wipe_disk,
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


class TestListDisks:
    async def test_list_disks_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"devpath": "/dev/sda", "size": "500G", "used": "N/A", "health": "OK", "model": "Samsung SSD"},
            ]
        )
        result = await list_disks(mock_client, node="pve")
        assert "/dev/sda" in result
        assert "Samsung SSD" in result

    async def test_list_disks_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_disks(mock_client, node="pve")
        assert "No disks" in result

    async def test_list_disks_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_disks(mock_client, node="bad!node")


class TestGetDiskSmart:
    async def test_get_disk_smart_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "overall_health": "PASSED",
                "temperature": "35C",
            }
        )
        result = await get_disk_smart(mock_client, node="pve", disk="/dev/sda")
        assert "/dev/sda" in result
        assert "PASSED" in result

    async def test_get_disk_smart_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "overall_health", "value": "PASSED"},
                {"name": "temperature", "value": "35C"},
            ]
        )
        result = await get_disk_smart(mock_client, node="pve", disk="/dev/sda")
        assert "/dev/sda" in result

    async def test_get_disk_smart_no_disk_raises(self, mock_client):
        with pytest.raises(ValueError, match="disk identifier is required"):
            await get_disk_smart(mock_client, node="pve", disk="")


class TestListLvm:
    async def test_list_lvm_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"vg": "pve", "size": "500G", "free": "50G"},
            ]
        )
        result = await list_lvm(mock_client, node="pve")
        assert "pve" in result
        assert "LVM" in result

    async def test_list_lvm_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_lvm(mock_client, node="pve")
        assert "No LVM" in result


class TestListLvmthin:
    async def test_list_lvmthin_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"lvname": "data", "size": "200G", "used": "100G"},
            ]
        )
        result = await list_lvmthin(mock_client, node="pve")
        assert "data" in result
        assert "LVM Thin" in result

    async def test_list_lvmthin_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_lvmthin(mock_client, node="pve")
        assert "No LVM thin" in result


class TestListZfs:
    async def test_list_zfs_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "tank", "size": "1T", "free": "500G", "health": "ONLINE"},
            ]
        )
        result = await list_zfs(mock_client, node="pve")
        assert "tank" in result
        assert "ZFS" in result

    async def test_list_zfs_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_zfs(mock_client, node="pve")
        assert "No ZFS" in result


class TestInitGpt:
    async def test_init_gpt_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await init_gpt(mock_client, node="pve", disk="/dev/sda")

    async def test_init_gpt_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await init_gpt(client, node="pve", disk="/dev/sda", confirm=True)

    async def test_init_gpt_no_disk_raises(self, mock_client):
        with pytest.raises(ValueError, match="disk identifier is required"):
            await init_gpt(mock_client, node="pve", disk="", confirm=True)

    async def test_init_gpt(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001")
        result = await init_gpt(mock_client, node="pve", disk="/dev/sda", confirm=True)
        assert "/dev/sda" in result
        assert "initialized" in result.lower()

    async def test_init_gpt_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await init_gpt(mock_client, node="bad!node", disk="/dev/sda", confirm=True)


class TestWipeDisk:
    async def test_wipe_disk_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await wipe_disk(mock_client, node="pve", disk="/dev/sda")

    async def test_wipe_disk_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await wipe_disk(client, node="pve", disk="/dev/sda", confirm=True)

    async def test_wipe_disk_no_disk_raises(self, mock_client):
        with pytest.raises(ValueError, match="disk identifier is required"):
            await wipe_disk(mock_client, node="pve", disk="", confirm=True)

    async def test_wipe_disk(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0002")
        result = await wipe_disk(mock_client, node="pve", disk="/dev/sdb", confirm=True)
        assert "/dev/sdb" in result
        assert "wiped" in result.lower()

    async def test_wipe_disk_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await wipe_disk(mock_client, node="bad!node", disk="/dev/sdb", confirm=True)
