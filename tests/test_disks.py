from unittest.mock import MagicMock, patch

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
    def test_list_disks_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"devpath": "/dev/sda", "size": "500G", "used": "N/A", "health": "OK", "model": "Samsung SSD"},
        ])
        result = list_disks(mock_client, node="pve")
        assert "/dev/sda" in result
        assert "Samsung SSD" in result

    def test_list_disks_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_disks(mock_client, node="pve")
        assert "No disks" in result

    def test_list_disks_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_disks(mock_client, node="bad!node")


class TestGetDiskSmart:
    def test_get_disk_smart_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "overall_health": "PASSED", "temperature": "35C",
        })
        result = get_disk_smart(mock_client, node="pve", disk="/dev/sda")
        assert "/dev/sda" in result
        assert "PASSED" in result

    def test_get_disk_smart_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "overall_health", "value": "PASSED"},
            {"name": "temperature", "value": "35C"},
        ])
        result = get_disk_smart(mock_client, node="pve", disk="/dev/sda")
        assert "/dev/sda" in result

    def test_get_disk_smart_no_disk_raises(self, mock_client):
        with pytest.raises(ValueError, match="disk identifier is required"):
            get_disk_smart(mock_client, node="pve", disk="")


class TestListLvm:
    def test_list_lvm_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"vg": "pve", "size": "500G", "free": "50G"},
        ])
        result = list_lvm(mock_client, node="pve")
        assert "pve" in result
        assert "LVM" in result

    def test_list_lvm_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_lvm(mock_client, node="pve")
        assert "No LVM" in result


class TestListLvmthin:
    def test_list_lvmthin_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"lvname": "data", "size": "200G", "used": "100G"},
        ])
        result = list_lvmthin(mock_client, node="pve")
        assert "data" in result
        assert "LVM Thin" in result

    def test_list_lvmthin_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_lvmthin(mock_client, node="pve")
        assert "No LVM thin" in result


class TestListZfs:
    def test_list_zfs_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "tank", "size": "1T", "free": "500G", "health": "ONLINE"},
        ])
        result = list_zfs(mock_client, node="pve")
        assert "tank" in result
        assert "ZFS" in result

    def test_list_zfs_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_zfs(mock_client, node="pve")
        assert "No ZFS" in result


class TestInitGpt:
    def test_init_gpt_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            init_gpt(mock_client, node="pve", disk="/dev/sda")

    def test_init_gpt_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            init_gpt(client, node="pve", disk="/dev/sda", confirm=True)

    def test_init_gpt_no_disk_raises(self, mock_client):
        with pytest.raises(ValueError, match="disk identifier is required"):
            init_gpt(mock_client, node="pve", disk="", confirm=True)

    def test_init_gpt(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0001")
        result = init_gpt(mock_client, node="pve", disk="/dev/sda", confirm=True)
        assert "/dev/sda" in result
        assert "initialized" in result.lower()

    def test_init_gpt_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            init_gpt(mock_client, node="bad!node", disk="/dev/sda", confirm=True)


class TestWipeDisk:
    def test_wipe_disk_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            wipe_disk(mock_client, node="pve", disk="/dev/sda")

    def test_wipe_disk_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            wipe_disk(client, node="pve", disk="/dev/sda", confirm=True)

    def test_wipe_disk_no_disk_raises(self, mock_client):
        with pytest.raises(ValueError, match="disk identifier is required"):
            wipe_disk(mock_client, node="pve", disk="", confirm=True)

    def test_wipe_disk(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0002")
        result = wipe_disk(mock_client, node="pve", disk="/dev/sdb", confirm=True)
        assert "/dev/sdb" in result
        assert "wiped" in result.lower()

    def test_wipe_disk_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            wipe_disk(mock_client, node="bad!node", disk="/dev/sdb", confirm=True)
