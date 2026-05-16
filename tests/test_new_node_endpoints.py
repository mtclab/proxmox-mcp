from unittest.mock import AsyncMock, MagicMock, patch

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
    async def test_zfs_detail(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "tank", "size": "1T", "health": "ONLINE"})
        result = await zfs_detail(mock_client, node="pve", name="tank")
        assert "tank" in result
        assert "ZFS Pool" in result

    async def test_zfs_detail_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await zfs_detail(mock_client, node="pve", name="")

    async def test_zfs_detail_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await zfs_detail(mock_client, node="bad!node", name="tank")


class TestZfsCreate:
    async def test_zfs_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await zfs_create(mock_client, node="pve", name="tank", devices="/dev/sda")

    async def test_zfs_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await zfs_create(client, node="pve", name="tank", devices="/dev/sda", confirm=True)

    async def test_zfs_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await zfs_create(mock_client, node="pve", name="", confirm=True)

    async def test_zfs_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001")
        result = await zfs_create(mock_client, node="pve", name="tank", devices="/dev/sda", confirm=True)
        assert "tank" in result
        assert "created" in result.lower()

    async def test_zfs_create_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await zfs_create(mock_client, node="bad!node", name="tank", confirm=True)


class TestZfsDestroy:
    async def test_zfs_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await zfs_destroy(mock_client, node="pve", name="tank")

    async def test_zfs_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await zfs_destroy(mock_client, node="pve", name="", confirm=True)

    async def test_zfs_destroy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0002")
        result = await zfs_destroy(mock_client, node="pve", name="tank", confirm=True)
        assert "tank" in result
        assert "destroyed" in result.lower()


class TestLvmCreate:
    async def test_lvm_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lvm_create(mock_client, node="pve", name="vg0", devices="/dev/sda")

    async def test_lvm_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await lvm_create(mock_client, node="pve", name="", confirm=True)

    async def test_lvm_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0003")
        result = await lvm_create(mock_client, node="pve", name="vg0", devices="/dev/sda", confirm=True)
        assert "vg0" in result
        assert "created" in result.lower()


class TestLvmDetail:
    async def test_lvm_detail(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "pve", "size": "500G"})
        result = await lvm_detail(mock_client, node="pve", name="pve")
        assert "pve" in result
        assert "LVM VG" in result

    async def test_lvm_detail_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await lvm_detail(mock_client, node="pve", name="")


class TestLvmDestroy:
    async def test_lvm_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lvm_destroy(mock_client, node="pve", name="vg0")

    async def test_lvm_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await lvm_destroy(mock_client, node="pve", name="", confirm=True)

    async def test_lvm_destroy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0004")
        result = await lvm_destroy(mock_client, node="pve", name="vg0", confirm=True)
        assert "vg0" in result
        assert "destroyed" in result.lower()


class TestLvmthinCreate:
    async def test_lvmthin_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lvmthin_create(mock_client, node="pve", name="data", devices="/dev/sda")

    async def test_lvmthin_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await lvmthin_create(mock_client, node="pve", name="", confirm=True)

    async def test_lvmthin_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0005")
        result = await lvmthin_create(mock_client, node="pve", name="data", devices="/dev/sda", confirm=True)
        assert "data" in result
        assert "created" in result.lower()


class TestLvmthinDestroy:
    async def test_lvmthin_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lvmthin_destroy(mock_client, node="pve", name="data")

    async def test_lvmthin_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await lvmthin_destroy(mock_client, node="pve", name="", confirm=True)

    async def test_lvmthin_destroy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0006")
        result = await lvmthin_destroy(mock_client, node="pve", name="data", confirm=True)
        assert "data" in result
        assert "destroyed" in result.lower()


class TestDirectoryList:
    async def test_directory_list_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "local", "path": "/var/lib/vz"},
                {"name": "nfs-storage", "path": "/mnt/pve/nfs-storage"},
            ]
        )
        result = await directory_list(mock_client, node="pve")
        assert "Directory Storages" in result
        assert "local" in result

    async def test_directory_list_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await directory_list(mock_client, node="pve")
        assert "No directory storages" in result

    async def test_directory_list_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await directory_list(mock_client, node="bad!node")


class TestDirectoryCreate:
    async def test_directory_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await directory_create(mock_client, node="pve", name="mystore", devices="/dev/sda")

    async def test_directory_create_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await directory_create(mock_client, node="pve", name="", confirm=True)

    async def test_directory_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0007")
        result = await directory_create(mock_client, node="pve", name="mystore", devices="/dev/sda", confirm=True)
        assert "mystore" in result
        assert "created" in result.lower()


class TestDirectoryDestroy:
    async def test_directory_destroy_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await directory_destroy(mock_client, node="pve", name="mystore")

    async def test_directory_destroy_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await directory_destroy(mock_client, node="pve", name="", confirm=True)

    async def test_directory_destroy(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0008")
        result = await directory_destroy(mock_client, node="pve", name="mystore", confirm=True)
        assert "mystore" in result
        assert "destroyed" in result.lower()


class TestAddAptRepo:
    async def test_add_apt_repo_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await add_apt_repo(mock_client, node="pve")

    async def test_add_apt_repo_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await add_apt_repo(client, node="pve", confirm=True)

    async def test_add_apt_repo(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await add_apt_repo(mock_client, node="pve", path="/etc/apt/sources.list", confirm=True)
        assert "APT repository added" in result

    async def test_add_apt_repo_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await add_apt_repo(mock_client, node="bad!node", confirm=True)


class TestUpdateAptRepo:
    async def test_update_apt_repo_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_apt_repo(mock_client, node="pve")

    async def test_update_apt_repo(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_apt_repo(mock_client, node="pve", index=0, enabled=True, confirm=True)
        assert "APT repository updated" in result


class TestListAptChangelog:
    async def test_list_apt_changelog_string(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="version 8.1\nbugfix release\nsecurity fix")
        result = await list_apt_changelog(mock_client, node="pve", name="pve-manager")
        assert "APT Changelog" in result

    async def test_list_apt_changelog_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "changelog content here"})
        result = await list_apt_changelog(mock_client, node="pve", name="pve-manager")
        assert "APT Changelog" in result

    async def test_list_apt_changelog_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_apt_changelog(mock_client, node="bad node!")


class TestListCapabilities:
    async def test_list_capabilities_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"qemu": True, "lxc": True})
        result = await list_capabilities(mock_client, node="pve")
        assert "Capabilities" in result

    async def test_list_capabilities_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_capabilities(mock_client, node="bad!")


class TestListCapabilitiesQemu:
    async def test_list_capabilities_qemu(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "cpu"},
                {"name": "machines"},
            ]
        )
        result = await list_capabilities_qemu(mock_client, node="pve")
        assert "QEMU Capabilities" in result

    async def test_list_capabilities_qemu_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_capabilities_qemu(mock_client, node="pve")
        assert "No QEMU capabilities" in result


class TestGetCapabilityQemuMigration:
    async def test_get_capability_qemu_migration(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"allowed": True, "local": {"name": "pve"}})
        result = await get_capability_qemu_migrations(mock_client, node="pve")
        assert "Migration Capabilities" in result

    async def test_get_capability_qemu_migration_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await get_capability_qemu_migrations(mock_client, node="bad!")


class TestListAcmeCerts:
    async def test_list_acme_certs_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "pve-node", "status": "valid"},
            ]
        )
        result = await list_acme_certs(mock_client, node="pve")
        assert "ACME Certificates" in result
        assert "pve-node" in result

    async def test_list_acme_certs_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_acme_certs(mock_client, node="pve")
        assert "No ACME" in result

    async def test_list_acme_certs_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_acme_certs(mock_client, node="bad node!")
