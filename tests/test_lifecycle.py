from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.lifecycle import (
    clone_vm,
    configure_lxc,
    configure_vm,
    create_lxc,
    create_vm,
    delete_lxc,
    delete_vm,
    migrate_vm,
    reboot_lxc,
    reboot_vm,
    shutdown_lxc,
    shutdown_vm,
    start_lxc,
    start_vm,
    stop_lxc,
    stop_vm,
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
    def test_create_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_lxc(mock_client, node="pve", vmid=200, ostemplate="local:vztmpl/debian.tar.xz")

    def test_start_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            start_lxc(mock_client, node="pve", vmid=200)

    def test_stop_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            stop_lxc(mock_client, node="pve", vmid=200)

    def test_shutdown_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            shutdown_lxc(mock_client, node="pve", vmid=200)

    def test_reboot_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            reboot_lxc(mock_client, node="pve", vmid=200)

    def test_delete_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_lxc(mock_client, node="pve", vmid=200)

    def test_configure_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            configure_lxc(mock_client, node="pve", vmid=200, cores=2)

    def test_create_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_vm(mock_client, node="pve", vmid=100, name="test")

    def test_start_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            start_vm(mock_client, node="pve", vmid=100)

    def test_stop_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            stop_vm(mock_client, node="pve", vmid=100)

    def test_shutdown_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            shutdown_vm(mock_client, node="pve", vmid=100)

    def test_reboot_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            reboot_vm(mock_client, node="pve", vmid=100)

    def test_delete_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_vm(mock_client, node="pve", vmid=100)

    def test_clone_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            clone_vm(mock_client, node="pve", vmid=100, newid=101)

    def test_migrate_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            migrate_vm(mock_client, node="pve", vmid=100, target="pve2")

    def test_configure_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            configure_vm(mock_client, node="pve", vmid=100, cores=2)


class TestElevatedCheck:
    def test_create_lxc_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_lxc(client, node="pve", vmid=200, ostemplate="local:vztmpl/debian.tar.xz", confirm=True)

    def test_create_vm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_vm(client, node="pve", vmid=100, name="test", confirm=True)


class TestLxcLifecycle:
    def test_create_lxc_with_vmid(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0001:abc")
        result = create_lxc(
            mock_client, node="pve", vmid=200, ostemplate="local:vztmpl/debian.tar.xz", confirm=True
        )
        assert "200" in result
        assert "UPID" in result

    def test_create_lxc_auto_vmid(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0001:abc")
        mock_client.admin_client.cluster.nextid.get = MagicMock(return_value=201)
        result = create_lxc(
            mock_client, node="pve", ostemplate="local:vztmpl/debian.tar.xz", confirm=True
        )
        assert "UPID" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["vmid"] == 201

    def test_start_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0002:abc")
        result = start_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "start" in result

    def test_stop_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0003:abc")
        result = stop_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "stop" in result

    def test_shutdown_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0004:abc")
        result = shutdown_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "shutdown" in result

    def test_reboot_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0005:abc")
        result = reboot_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "reboot" in result

    def test_delete_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0006:abc")
        result = delete_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "deleted" in result

    def test_configure_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0007:abc")
        result = configure_lxc(mock_client, node="pve", vmid=200, cores=4, memory=4096, confirm=True)
        assert "LXC 200" in result
        assert "configured" in result

    def test_create_lxc_with_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0008:abc")
        result = create_lxc(
            mock_client,
            node="pve",
            vmid=200,
            ostemplate="local:vztmpl/debian.tar.xz",
            hostname="myct",
            memory=2048,
            cores=2,
            rootfs="local-lvm:10",
            password="secret",
            start=True,
            confirm=True,
        )
        assert "200" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["hostname"] == "myct"
        assert call_args[1]["memory"] == 2048
        assert call_args[1]["cores"] == 2
        assert call_args[1]["rootfs"] == "local-lvm:10"
        assert call_args[1]["start"] == 1

    def test_create_lxc_invalid_template(self, mock_client):
        content_result = [
            {
                "volid": "local:vztmpl/other.tar.xz",
                "content": "vztmpl",
            }
        ]
        mock_client.safe_api_call = MagicMock(side_effect=[
            content_result,
            "UPID:pve:0009:abc",
        ])
        with pytest.raises(ValueError, match="not found"):
            create_lxc(
                mock_client,
                node="pve",
                vmid=200,
                ostemplate="local:vztmpl/nonexistent.tar.xz",
                confirm=True,
            )


class TestVmLifecycle:
    def test_create_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0010:abc")
        result = create_vm(mock_client, node="pve", vmid=100, name="test-vm", confirm=True)
        assert "VM 100" in result
        assert "created" in result

    def test_create_vm_auto_vmid(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0011:abc")
        mock_client.admin_client.cluster.nextid.get = MagicMock(return_value=102)
        result = create_vm(mock_client, node="pve", name="auto-vm", confirm=True)
        assert "UPID" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["vmid"] == 102

    def test_create_vm_with_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0012:abc")
        result = create_vm(
            mock_client,
            node="pve",
            vmid=100,
            name="test-vm",
            memory=4096,
            cores=4,
            sockets=2,
            disk_size="32G",
            storage="local-lvm",
            iso="local:iso/debian.iso",
            ostype="l26",
            net0="virtio,bridge=vmbr0",
            confirm=True,
        )
        assert "VM 100" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["memory"] == 4096
        assert call_args[1]["cores"] == 4
        assert call_args[1]["sockets"] == 2
        assert call_args[1]["disk"] == "32G"
        assert call_args[1]["storage"] == "local-lvm"
        assert "cdrom" in call_args[1]

    def test_start_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0013:abc")
        result = start_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "start" in result

    def test_stop_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0014:abc")
        result = stop_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "stop" in result

    def test_shutdown_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0015:abc")
        result = shutdown_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "shutdown" in result

    def test_reboot_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0016:abc")
        result = reboot_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "reboot" in result

    def test_delete_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0017:abc")
        result = delete_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "deleted" in result

    def test_clone_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0018:abc")
        result = clone_vm(mock_client, node="pve", vmid=100, newid=101, name="clone-vm", confirm=True)
        assert "clone" in result
        assert "101" in result

    def test_clone_vm_auto_newid(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0019:abc")
        mock_client.admin_client.cluster.nextid.get = MagicMock(return_value=102)
        result = clone_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "102" in result

    def test_migrate_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0020:abc")
        result = migrate_vm(mock_client, node="pve", vmid=100, target="pve2", confirm=True)
        assert "migration" in result
        assert "pve2" in result

    def test_configure_vm(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0021:abc")
        result = configure_vm(mock_client, node="pve", vmid=100, cores=4, memory=8192, confirm=True)
        assert "VM 100" in result
        assert "configured" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["cores"] == 4
        assert call_args[1]["memory"] == 8192


class TestNodeResolution:
    def test_lxc_defaults_to_config_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0100:abc")
        result = start_lxc(mock_client, vmid=200, confirm=True)
        assert "pve" in result

    def test_vm_defaults_to_config_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0101:abc")
        result = start_vm(mock_client, vmid=100, confirm=True)
        assert "pve" in result

    def test_lxc_explicit_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve2:0102:abc")
        result = start_lxc(mock_client, node="pve2", vmid=200, confirm=True)
        assert "pve2" in result
