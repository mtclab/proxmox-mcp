from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.apt import add_apt_repo, list_apt_changelog, update_apt_repo
from proxmox_mcp.capabilities import (
    get_capability_qemu_migrations,
    list_capabilities,
    list_capabilities_qemu,
)
from proxmox_mcp.certificates import list_acme_certs
from proxmox_mcp.config import Config
from proxmox_mcp.disks import (
    directory_create,
    directory_destroy,
    directory_list,
    lvm_create,
    lvm_destroy,
    lvm_detail,
    lvmthin_create,
    lvmthin_destroy,
    zfs_create,
    zfs_destroy,
    zfs_detail,
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


class TestZfsDetail:
    def test_zfs_detail(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"name": "tank", "size": "1T", "health": "ONLINE"})
        result = zfs_detail(mock_client, node="pve", name="tank")
        assert "tank" in result
        assert "ZFS Pool" in result

    def test_zfs_detail_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            zfs_detail(mock_client, node="pve", name="")

    def test_zfs_detail_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            zfs_detail(mock_client, node="bad!node", name="tank")


class TestZfsCreate:
    def test_zfs_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            zfs_create(mock_client, node="pve", name="tank", devices="/dev/sda")

    def test_zfs_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            zfs_create(client, node="pve", name="tank", devices="/dev/sda", confirm=True)

    def test_zfs_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            zfs_create(mock_client, node="pve", name="", confirm=True)

    def test_zfs_create(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0001")
        result = zfs_create(mock_client, node="pve", name="tank", devices="/dev/sda", confirm=True)
        assert "tank" in result
        assert "created" in result.lower()

    def test_zfs_create_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            zfs_create(mock_client, node="bad!node", name="tank", confirm=True)


class TestZfsDestroy:
    def test_zfs_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            zfs_destroy(mock_client, node="pve", name="tank")

    def test_zfs_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            zfs_destroy(mock_client, node="pve", name="", confirm=True)

    def test_zfs_destroy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0002")
        result = zfs_destroy(mock_client, node="pve", name="tank", confirm=True)
        assert "tank" in result
        assert "destroyed" in result.lower()


class TestLvmCreate:
    def test_lvm_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lvm_create(mock_client, node="pve", name="vg0", devices="/dev/sda")

    def test_lvm_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            lvm_create(mock_client, node="pve", name="", confirm=True)

    def test_lvm_create(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0003")
        result = lvm_create(mock_client, node="pve", name="vg0", devices="/dev/sda", confirm=True)
        assert "vg0" in result
        assert "created" in result.lower()


class TestLvmDetail:
    def test_lvm_detail(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"name": "pve", "size": "500G"})
        result = lvm_detail(mock_client, node="pve", name="pve")
        assert "pve" in result
        assert "LVM VG" in result

    def test_lvm_detail_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            lvm_detail(mock_client, node="pve", name="")


class TestLvmDestroy:
    def test_lvm_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lvm_destroy(mock_client, node="pve", name="vg0")

    def test_lvm_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            lvm_destroy(mock_client, node="pve", name="", confirm=True)

    def test_lvm_destroy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0004")
        result = lvm_destroy(mock_client, node="pve", name="vg0", confirm=True)
        assert "vg0" in result
        assert "destroyed" in result.lower()


class TestLvmthinCreate:
    def test_lvmthin_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lvmthin_create(mock_client, node="pve", name="data", devices="/dev/sda")

    def test_lvmthin_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            lvmthin_create(mock_client, node="pve", name="", confirm=True)

    def test_lvmthin_create(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0005")
        result = lvmthin_create(mock_client, node="pve", name="data", devices="/dev/sda", confirm=True)
        assert "data" in result
        assert "created" in result.lower()


class TestLvmthinDestroy:
    def test_lvmthin_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lvmthin_destroy(mock_client, node="pve", name="data")

    def test_lvmthin_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            lvmthin_destroy(mock_client, node="pve", name="", confirm=True)

    def test_lvmthin_destroy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0006")
        result = lvmthin_destroy(mock_client, node="pve", name="data", confirm=True)
        assert "data" in result
        assert "destroyed" in result.lower()


class TestDirectoryList:
    def test_directory_list_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "local", "path": "/var/lib/vz"},
            {"name": "nfs-storage", "path": "/mnt/pve/nfs-storage"},
        ])
        result = directory_list(mock_client, node="pve")
        assert "Directory Storages" in result
        assert "local" in result

    def test_directory_list_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = directory_list(mock_client, node="pve")
        assert "No directory storages" in result

    def test_directory_list_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            directory_list(mock_client, node="bad!node")


class TestDirectoryCreate:
    def test_directory_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            directory_create(mock_client, node="pve", name="mystore", devices="/dev/sda")

    def test_directory_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            directory_create(mock_client, node="pve", name="", confirm=True)

    def test_directory_create(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0007")
        result = directory_create(mock_client, node="pve", name="mystore", devices="/dev/sda", confirm=True)
        assert "mystore" in result
        assert "created" in result.lower()


class TestDirectoryDestroy:
    def test_directory_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            directory_destroy(mock_client, node="pve", name="mystore")

    def test_directory_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            directory_destroy(mock_client, node="pve", name="", confirm=True)

    def test_directory_destroy(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0008")
        result = directory_destroy(mock_client, node="pve", name="mystore", confirm=True)
        assert "mystore" in result
        assert "destroyed" in result.lower()


class TestAddAptRepo:
    def test_add_apt_repo_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            add_apt_repo(mock_client, node="pve")

    def test_add_apt_repo_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            add_apt_repo(client, node="pve", confirm=True)

    def test_add_apt_repo(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = add_apt_repo(mock_client, node="pve", path="/etc/apt/sources.list", confirm=True)
        assert "APT repository added" in result

    def test_add_apt_repo_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            add_apt_repo(mock_client, node="bad!node", confirm=True)


class TestUpdateAptRepo:
    def test_update_apt_repo_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_apt_repo(mock_client, node="pve")

    def test_update_apt_repo(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_apt_repo(mock_client, node="pve", index=0, enabled=True, confirm=True)
        assert "APT repository updated" in result


class TestListAptChangelog:
    def test_list_apt_changelog_string(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="version 8.1\nbugfix release\nsecurity fix")
        result = list_apt_changelog(mock_client, node="pve", name="pve-manager")
        assert "APT Changelog" in result

    def test_list_apt_changelog_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "changelog content here"})
        result = list_apt_changelog(mock_client, node="pve", name="pve-manager")
        assert "APT Changelog" in result

    def test_list_apt_changelog_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_apt_changelog(mock_client, node="bad node!")


class TestListCapabilities:
    def test_list_capabilities_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"qemu": True, "lxc": True})
        result = list_capabilities(mock_client, node="pve")
        assert "Capabilities" in result

    def test_list_capabilities_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_capabilities(mock_client, node="bad!")


class TestListCapabilitiesQemu:
    def test_list_capabilities_qemu(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "cpu"}, {"name": "machines"},
        ])
        result = list_capabilities_qemu(mock_client, node="pve")
        assert "QEMU Capabilities" in result

    def test_list_capabilities_qemu_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_capabilities_qemu(mock_client, node="pve")
        assert "No QEMU capabilities" in result


class TestGetCapabilityQemuMigration:
    def test_get_capability_qemu_migration(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"allowed": True, "local": {"name": "pve"}})
        result = get_capability_qemu_migrations(mock_client, node="pve")
        assert "Migration Capabilities" in result

    def test_get_capability_qemu_migration_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            get_capability_qemu_migrations(mock_client, node="bad!")


class TestListAcmeCerts:
    def test_list_acme_certs_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "pve-node", "status": "valid"},
        ])
        result = list_acme_certs(mock_client, node="pve")
        assert "ACME Certificates" in result
        assert "pve-node" in result

    def test_list_acme_certs_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_acme_certs(mock_client, node="pve")
        assert "No ACME" in result

    def test_list_acme_certs_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_acme_certs(mock_client, node="bad node!")
