from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.cloudinit import regenerate_cloudinit
from proxmox_mcp.config import Config
from proxmox_mcp.discovery import list_node_lxc, list_node_tasks, list_node_vms, node_index
from proxmox_mcp.lifecycle import lxc_migrate_preconditions, vm_migrate_preconditions
from proxmox_mcp.networking import revert_network
from proxmox_mcp.storage import allocate_disk, storage_identity, storage_metrics


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


class TestLxcMigratePreconditions:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"allowed": 1, "local_disks": 0})
        result = lxc_migrate_preconditions(mock_client, node="pve", vmid=200)
        assert "LXC 200" in result
        assert "pve" in result
        mock_client.safe_api_call.assert_called_once()

    def test_resolves_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = lxc_migrate_preconditions(mock_client, vmid=200)
        assert result is not None
        mock_client.safe_api_call.assert_called_once()


class TestVmMigratePreconditions:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"allowed": 1, "local_disks": 0})
        result = vm_migrate_preconditions(mock_client, node="pve", vmid=100)
        assert "VM 100" in result
        assert "pve" in result
        mock_client.safe_api_call.assert_called_once()


class TestStorageMetrics:
    def test_returns_data_points_count(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[{"time": 1}, {"time": 2}])
        result = storage_metrics(mock_client, node="pve", storage="local")
        assert "2 data points" in result
        assert "local" in result

    def test_returns_no_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = storage_metrics(mock_client, node="pve", storage="local")
        assert "No metrics data" in result


class TestStorageIdentity:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"storage": "local", "type": "dir"})
        result = storage_identity(mock_client, node="pve", storage="local")
        assert "local" in result
        assert "dir" in result

    def test_resolves_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = storage_identity(mock_client, storage="local")
        assert result is not None
        mock_client.safe_api_call.assert_called_once()


class TestAllocateDisk:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            allocate_disk(mock_client, node="pve", storage="local", size="1G")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            allocate_disk(client, node="pve", storage="local", size="1G", confirm=True)

    def test_allocates_disk(self, mock_client):
        mock_api = MagicMock()
        mock_api.nodes.return_value.storage.return_value.content.post.return_value = "UPID:pve:001:abc"
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:001:abc")
        result = allocate_disk(mock_client, node="pve", storage="local", size="1G", confirm=True)
        assert "UPID" in result

    def test_allocates_disk_with_vmid(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:002:abc")
        result = allocate_disk(mock_client, node="pve", storage="local", vmid=100, size="10G", confirm=True)
        assert "UPID" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["vmid"] == 100
        assert call_args[1]["size"] == "10G"

    def test_allocates_disk_with_filename_and_format(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:003:abc")
        result = allocate_disk(
            mock_client, node="pve", storage="local",
            filename="vm-100-disk-0", size="10G", format="qcow2",
            confirm=True,
        )
        assert "UPID" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["filename"] == "vm-100-disk-0"
        assert call_args[1]["format"] == "qcow2"


class TestListNodeLxc:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"vmid": 200, "name": "ct1", "status": "running", "cpu": 0.1, "mem": 500000000},
            {"vmid": 201, "name": "ct2", "status": "stopped"},
        ])
        result = list_node_lxc(mock_client, node="pve")
        assert "ct1" in result
        assert "ct2" in result
        mock_client.safe_api_call.assert_called_once()

    def test_empty_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_lxc(mock_client, node="pve")
        assert "No LXC containers" in result


class TestListNodeVms:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"vmid": 100, "name": "vm1", "status": "running", "cpu": 0.2, "mem": 1000000000},
        ])
        result = list_node_vms(mock_client, node="pve")
        assert "vm1" in result
        mock_client.safe_api_call.assert_called_once()

    def test_empty_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_vms(mock_client, node="pve")
        assert "No VMs" in result


class TestListNodeTasks:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"upid": "UPID:pve:001:abc", "status": "OK"},
            {"upid": "UPID:pve:002:def", "status": "stopped"},
        ])
        result = list_node_tasks(mock_client, node="pve")
        assert "UPID:pve:001" in result
        mock_client.safe_api_call.assert_called_once()

    def test_passes_limit(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        list_node_tasks(mock_client, node="pve", limit=10)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["limit"] == 10


class TestNodeIndex:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"node": "pve", "status": "online", "cpu": 0.5})
        result = node_index(mock_client, node="pve")
        assert "pve" in result
        mock_client.safe_api_call.assert_called_once()


class TestRegenerateCloudinit:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            regenerate_cloudinit(mock_client, node="pve", vmid=100)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            regenerate_cloudinit(client, node="pve", vmid=100, confirm=True)

    def test_regenerates(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:100:abc")
        result = regenerate_cloudinit(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result
        assert "100" in result


class TestRevertNetwork:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            revert_network(mock_client, node="pve")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            revert_network(client, node="pve", confirm=True)

    def test_reverts_network(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:network:revert")
        result = revert_network(mock_client, node="pve", confirm=True)
        assert "reverted" in result.lower()
        mock_client.safe_api_call.assert_called_once()
