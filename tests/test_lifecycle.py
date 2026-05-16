from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.lifecycle import (
    clone_lxc,
    clone_vm,
    configure_lxc,
    configure_vm,
    convert_lxc_to_template,
    convert_to_template,
    create_lxc,
    create_vm,
    delete_lxc,
    delete_vm,
    lxc_feature_check,
    lxc_interfaces,
    lxc_pending_config,
    migrate_lxc,
    migrate_vm,
    move_vm_disk,
    reboot_lxc,
    reboot_vm,
    reset_vm,
    resize_lxc,
    resize_vm,
    resume_lxc,
    resume_vm,
    send_vm_key,
    shutdown_lxc,
    shutdown_vm,
    start_lxc,
    start_vm,
    stop_lxc,
    stop_vm,
    suspend_lxc,
    suspend_vm,
    unlink_vm_disk,
    vm_dbus_vmstate,
    vm_feature_check,
    vm_monitor_command,
    vm_pending_config,
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
    async def test_create_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_lxc(mock_client, node="pve", vmid=200, ostemplate="local:vztmpl/debian.tar.xz")

    async def test_start_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await start_lxc(mock_client, node="pve", vmid=200)

    async def test_stop_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await stop_lxc(mock_client, node="pve", vmid=200)

    async def test_shutdown_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await shutdown_lxc(mock_client, node="pve", vmid=200)

    async def test_reboot_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await reboot_lxc(mock_client, node="pve", vmid=200)

    async def test_delete_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_lxc(mock_client, node="pve", vmid=200)

    async def test_configure_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await configure_lxc(mock_client, node="pve", vmid=200, cores=2)

    async def test_resize_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await resize_lxc(mock_client, node="pve", vmid=200, disk="rootfs", size="+10G")

    async def test_suspend_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await suspend_lxc(mock_client, node="pve", vmid=200)

    async def test_resume_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await resume_lxc(mock_client, node="pve", vmid=200)

    async def test_clone_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await clone_lxc(mock_client, node="pve", vmid=200, newid=201)

    async def test_migrate_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await migrate_lxc(mock_client, node="pve", vmid=200, target="pve2")

    async def test_create_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_vm(mock_client, node="pve", vmid=100, name="test")

    async def test_start_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await start_vm(mock_client, node="pve", vmid=100)

    async def test_stop_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await stop_vm(mock_client, node="pve", vmid=100)

    async def test_shutdown_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await shutdown_vm(mock_client, node="pve", vmid=100)

    async def test_reboot_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await reboot_vm(mock_client, node="pve", vmid=100)

    async def test_delete_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_vm(mock_client, node="pve", vmid=100)

    async def test_clone_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await clone_vm(mock_client, node="pve", vmid=100, newid=101)

    async def test_migrate_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await migrate_vm(mock_client, node="pve", vmid=100, target="pve2")

    async def test_configure_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await configure_vm(mock_client, node="pve", vmid=100, cores=2)

    async def test_resize_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await resize_vm(mock_client, node="pve", vmid=100, disk="scsi0", size="+10G")

    async def test_reset_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await reset_vm(mock_client, node="pve", vmid=100)

    async def test_suspend_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await suspend_vm(mock_client, node="pve", vmid=100)

    async def test_resume_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await resume_vm(mock_client, node="pve", vmid=100)


class TestElevatedCheck:
    async def test_create_lxc_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_lxc(client, node="pve", vmid=200, ostemplate="local:vztmpl/debian.tar.xz", confirm=True)

    async def test_create_vm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_vm(client, node="pve", vmid=100, name="test", confirm=True)

    async def test_resize_lxc_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await resize_lxc(client, node="pve", vmid=200, disk="rootfs", size="+10G", confirm=True)

    async def test_resize_vm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await resize_vm(client, node="pve", vmid=100, disk="scsi0", size="+10G", confirm=True)

    async def test_reset_vm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await reset_vm(client, node="pve", vmid=100, confirm=True)

    async def test_suspend_vm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await suspend_vm(client, node="pve", vmid=100, confirm=True)

    async def test_resume_vm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await resume_vm(client, node="pve", vmid=100, confirm=True)


class TestLxcLifecycle:
    async def test_create_lxc_with_vmid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001:abc")
        result = await create_lxc(
            mock_client, node="pve", vmid=200, ostemplate="local:vztmpl/debian.tar.xz", confirm=True
        )
        assert "200" in result
        assert "UPID" in result

    async def test_create_lxc_auto_vmid(self, mock_client):
        nextid_call = mock_client.monitor_client.cluster.nextid.get

        async def _side_effect(func, *args, **kwargs):
            if func is nextid_call:
                return 201
            return "UPID:pve:0001:abc"

        mock_client.safe_api_call = AsyncMock(side_effect=_side_effect)
        result = await create_lxc(mock_client, node="pve", ostemplate="local:vztmpl/debian.tar.xz", confirm=True)
        assert "UPID" in result
        assert "201" in result

    async def test_start_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0002:abc")
        result = await start_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "start" in result

    async def test_stop_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0003:abc")
        result = await stop_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "stop" in result

    async def test_shutdown_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0004:abc")
        result = await shutdown_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "shutdown" in result

    async def test_reboot_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0005:abc")
        result = await reboot_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "reboot" in result

    async def test_delete_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0006:abc")
        result = await delete_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "deleted" in result

    async def test_configure_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0007:abc")
        result = await configure_lxc(mock_client, node="pve", vmid=200, cores=4, memory=4096, confirm=True)
        assert "LXC 200" in result
        assert "configured" in result

    async def test_create_lxc_with_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0008:abc")
        result = await create_lxc(
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

    async def test_create_lxc_invalid_template(self, mock_client):
        content_result = [
            {
                "volid": "local:vztmpl/other.tar.xz",
                "content": "vztmpl",
            }
        ]
        mock_client.safe_api_call = AsyncMock(
            side_effect=[
                content_result,
                "UPID:pve:0009:abc",
            ]
        )
        with pytest.raises(ValueError, match="not found"):
            await create_lxc(
                mock_client,
                node="pve",
                vmid=200,
                ostemplate="local:vztmpl/nonexistent.tar.xz",
                confirm=True,
            )

    async def test_resize_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0030:abc")
        result = await resize_lxc(mock_client, node="pve", vmid=200, disk="rootfs", size="+10G", confirm=True)
        assert "LXC 200" in result
        assert "resize" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["disk"] == "rootfs"
        assert call_args[1]["size"] == "+10G"

    async def test_resize_lxc_mp0(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0031:abc")
        result = await resize_lxc(mock_client, node="pve", vmid=200, disk="mp0", size="+5G", confirm=True)
        assert "mp0" in result
        assert "+5G" in result

    async def test_suspend_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0032:abc")
        result = await suspend_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "suspend" in result

    async def test_resume_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0033:abc")
        result = await resume_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "LXC 200" in result
        assert "resume" in result

    async def test_clone_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0034:abc")
        result = await clone_lxc(mock_client, node="pve", vmid=200, newid=201, hostname="clone-ct", confirm=True)
        assert "clone" in result
        assert "201" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["newid"] == 201
        assert call_args[1]["hostname"] == "clone-ct"

    async def test_clone_lxc_auto_newid(self, mock_client):
        nextid_call = mock_client.monitor_client.cluster.nextid.get

        async def _side_effect(func, *args, **kwargs):
            if func is nextid_call:
                return 202
            return "UPID:pve:0035:abc"

        mock_client.safe_api_call = AsyncMock(side_effect=_side_effect)
        result = await clone_lxc(mock_client, node="pve", vmid=200, confirm=True)
        assert "202" in result

    async def test_clone_lxc_full_flag(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0036:abc")
        await clone_lxc(mock_client, node="pve", vmid=200, newid=201, full=True, confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["full"] == 1

    async def test_clone_lxc_linked(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0037:abc")
        await clone_lxc(mock_client, node="pve", vmid=200, newid=201, full=False, confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["full"] == 0

    async def test_clone_lxc_with_target(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0038:abc")
        await clone_lxc(mock_client, node="pve", vmid=200, newid=201, target="pve2", confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["target"] == "pve2"

    async def test_migrate_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0039:abc")
        result = await migrate_lxc(mock_client, node="pve", vmid=200, target="pve2", confirm=True)
        assert "migration" in result
        assert "pve2" in result

    async def test_lxc_interfaces(self, mock_client):
        iface_data = [
            {
                "name": "eth0",
                "hwaddr": "aa:bb:cc:dd:ee:ff",
                "ip-addresses": [
                    {"ip-address": "10.0.0.5", "ip-prefix-length": 24, "ip-address-type": "ipv4"},
                    {"ip-address": "::1", "ip-prefix-length": 128, "ip-address-type": "ipv6"},
                ],
            }
        ]
        mock_client.safe_api_call = AsyncMock(return_value=iface_data)
        result = await lxc_interfaces(mock_client, node="pve", vmid=200)
        assert "eth0" in result
        assert "10.0.0.5" in result

    async def test_lxc_interfaces_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await lxc_interfaces(mock_client, node="pve", vmid=200)
        assert "No interfaces" in result


class TestVmLifecycle:
    async def test_create_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0010:abc")
        result = await create_vm(mock_client, node="pve", vmid=100, name="test-vm", confirm=True)
        assert "VM 100" in result
        assert "created" in result

    async def test_create_vm_auto_vmid(self, mock_client):
        nextid_call = mock_client.monitor_client.cluster.nextid.get

        async def _side_effect(func, *args, **kwargs):
            if func is nextid_call:
                return 102
            return "UPID:pve:0011:abc"

        mock_client.safe_api_call = AsyncMock(side_effect=_side_effect)
        result = await create_vm(mock_client, node="pve", name="auto-vm", confirm=True)
        assert "UPID" in result
        assert "102" in result

    async def test_create_vm_with_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0012:abc")
        result = await create_vm(
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
        assert call_args[1]["scsi0"] == "local-lvm:32"

    async def test_create_vm_disk_size_string_G(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0012:abc")
        await create_vm(mock_client, node="pve", vmid=100, disk_size="1G", storage="local-lvm", confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["scsi0"] == "local-lvm:1"

    async def test_create_vm_disk_size_int(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0012:abc")
        await create_vm(mock_client, node="pve", vmid=100, disk_size=10, storage="local-lvm", confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["scsi0"] == "local-lvm:10"

    async def test_create_vm_disk_size_T(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0012:abc")
        await create_vm(mock_client, node="pve", vmid=100, disk_size="1T", storage="local-lvm", confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["scsi0"] == "local-lvm:1024"

    async def test_create_vm_disk_size_invalid_raises(self, mock_client):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            await create_vm(mock_client, node="pve", vmid=100, disk_size="abc", storage="local-lvm", confirm=True)

    async def test_start_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0013:abc")
        result = await start_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "start" in result

    async def test_stop_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0014:abc")
        result = await stop_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "stop" in result

    async def test_shutdown_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0015:abc")
        result = await shutdown_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "shutdown" in result

    async def test_reboot_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0016:abc")
        result = await reboot_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "reboot" in result

    async def test_delete_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0017:abc")
        result = await delete_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "VM 100" in result
        assert "deleted" in result

    async def test_clone_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0018:abc")
        result = await clone_vm(mock_client, node="pve", vmid=100, newid=101, name="clone-vm", confirm=True)
        assert "clone" in result
        assert "101" in result

    async def test_clone_vm_auto_newid(self, mock_client):
        nextid_call = mock_client.monitor_client.cluster.nextid.get

        async def _side_effect(func, *args, **kwargs):
            if func is nextid_call:
                return 102
            return "UPID:pve:0019:abc"

        mock_client.safe_api_call = AsyncMock(side_effect=_side_effect)
        result = await clone_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "102" in result

    async def test_migrate_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0020:abc")
        result = await migrate_vm(mock_client, node="pve", vmid=100, target="pve2", confirm=True)
        assert "migration" in result
        assert "pve2" in result

    async def test_configure_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0021:abc")
        result = await configure_vm(mock_client, node="pve", vmid=100, cores=4, memory=8192, confirm=True)
        assert "VM 100" in result
        assert "configured" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["cores"] == 4
        assert call_args[1]["memory"] == 8192

    async def test_resize_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0200:abc")
        result = await resize_vm(mock_client, node="pve", vmid=100, disk="scsi0", size="+10G", confirm=True)
        assert "100" in result
        assert "scsi0" in result
        assert "+10G" in result
        assert "UPID" in result

    async def test_resize_vm_custom_disk(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0201:abc")
        result = await resize_vm(mock_client, node="pve", vmid=100, disk="virtio1", size="+5G", confirm=True)
        assert "virtio1" in result
        assert "+5G" in result

    async def test_resize_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0202:abc"})
        result = await resize_vm(mock_client, node="pve", vmid=100, disk="scsi0", size="+10G", confirm=True)
        assert "UPID" in result

    async def test_resize_vm_passes_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0203:abc")
        await resize_vm(mock_client, node="pve", vmid=100, disk="scsi0", size="+10G", confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["disk"] == "scsi0"
        assert call_args[1]["size"] == "+10G"

    async def test_reset_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0210:abc")
        result = await reset_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "reset" in result
        assert "UPID" in result

    async def test_reset_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0211:abc"})
        result = await reset_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result

    async def test_suspend_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0220:abc")
        result = await suspend_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "suspend" in result
        assert "UPID" in result

    async def test_suspend_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0221:abc"})
        result = await suspend_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result

    async def test_resume_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0230:abc")
        result = await resume_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "resume" in result
        assert "UPID" in result

    async def test_resume_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0231:abc"})
        result = await resume_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result


class TestNodeResolution:
    async def test_lxc_defaults_to_config_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0100:abc")
        result = await start_lxc(mock_client, vmid=200, confirm=True)
        assert "pve" in result

    async def test_vm_defaults_to_config_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0101:abc")
        result = await start_vm(mock_client, vmid=100, confirm=True)
        assert "pve" in result

    async def test_lxc_explicit_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve2:0102:abc")
        result = await start_lxc(mock_client, node="pve2", vmid=200, confirm=True)
        assert "pve2" in result

    async def test_resize_vm_custom_disk(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0201:abc")
        result = await resize_vm(mock_client, node="pve", vmid=100, disk="virtio1", size="+5G", confirm=True)
        assert "virtio1" in result
        assert "+5G" in result

    async def test_resize_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0202:abc"})
        result = await resize_vm(mock_client, node="pve", vmid=100, disk="scsi0", size="+10G", confirm=True)
        assert "UPID" in result

    async def test_resize_vm_passes_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0203:abc")
        await resize_vm(mock_client, node="pve", vmid=100, disk="scsi0", size="+10G", confirm=True)
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["disk"] == "scsi0"
        assert call_args[1]["size"] == "+10G"

    async def test_resize_vm_node_resolution(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0204:abc")
        result = await resize_vm(mock_client, vmid=100, disk="scsi0", size="+10G", confirm=True)
        assert "pve" in result


class TestResetVm:
    async def test_reset_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0210:abc")
        result = await reset_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "reset" in result
        assert "UPID" in result

    async def test_reset_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0211:abc"})
        result = await reset_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result


class TestSuspendVm:
    async def test_suspend_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0220:abc")
        result = await suspend_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "suspend" in result
        assert "UPID" in result

    async def test_suspend_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0221:abc"})
        result = await suspend_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result


class TestResumeVm:
    async def test_resume_vm(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0230:abc")
        result = await resume_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "resume" in result
        assert "UPID" in result

    async def test_resume_vm_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0231:abc"})
        result = await resume_vm(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result


class TestMoveVmDisk:
    async def test_move_vm_disk_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await move_vm_disk(mock_client, node="pve", vmid=100, disk="scsi0", storage="local-lvm")

    async def test_move_vm_disk_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await move_vm_disk(client, node="pve", vmid=100, disk="scsi0", storage="local-lvm", confirm=True)

    async def test_move_vm_disk(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0300:abc")
        result = await move_vm_disk(mock_client, node="pve", vmid=100, disk="scsi0", storage="local-lvm", confirm=True)
        assert "100" in result
        assert "scsi0" in result
        assert "local-lvm" in result
        assert "UPID" in result

    async def test_move_vm_disk_with_format(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0301:abc")
        await move_vm_disk(
            mock_client, node="pve", vmid=100, disk="scsi0", storage="local-lvm", format="qcow2", confirm=True
        )
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["format"] == "qcow2"

    async def test_move_vm_disk_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0302:abc"})
        result = await move_vm_disk(mock_client, node="pve", vmid=100, disk="scsi0", storage="local-lvm", confirm=True)
        assert "UPID" in result


class TestConvertToTemplate:
    async def test_convert_to_template_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await convert_to_template(mock_client, node="pve", vmid=100)

    async def test_convert_to_template_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await convert_to_template(client, node="pve", vmid=100, confirm=True)

    async def test_convert_to_template(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0310:abc")
        result = await convert_to_template(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "template" in result
        assert "UPID" in result

    async def test_convert_to_template_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0311:abc"})
        result = await convert_to_template(mock_client, node="pve", vmid=100, confirm=True)
        assert "UPID" in result


class TestConvertLxcToTemplate:
    async def test_convert_lxc_to_template_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await convert_lxc_to_template(mock_client, node="pve", vmid=200)

    async def test_convert_lxc_to_template_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await convert_lxc_to_template(client, node="pve", vmid=200, confirm=True)

    async def test_convert_lxc_to_template(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0320:abc")
        result = await convert_lxc_to_template(mock_client, node="pve", vmid=200, confirm=True)
        assert "200" in result
        assert "template" in result
        assert "UPID" in result

    async def test_convert_lxc_to_template_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0321:abc"})
        result = await convert_lxc_to_template(mock_client, node="pve", vmid=200, confirm=True)
        assert "UPID" in result


class TestLxcFeatureCheck:
    async def test_lxc_feature_check(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"snapshot": True, "clone": True})
        result = await lxc_feature_check(mock_client, node="pve", vmid=200, feature="snapshot")
        assert "200" in result
        assert "snapshot" in result

    async def test_lxc_feature_check_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"snapshot": False})
        result = await lxc_feature_check(mock_client, node="pve", vmid=200, feature="snapshot")
        assert "200" in result
        assert "snapshot" in result


class TestVmFeatureCheck:
    async def test_vm_feature_check(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"snapshot": True, "clone": True})
        result = await vm_feature_check(mock_client, node="pve", vmid=100, feature="snapshot")
        assert "100" in result
        assert "snapshot" in result

    async def test_vm_feature_check_non_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="some result")
        result = await vm_feature_check(mock_client, node="pve", vmid=100, feature="clone")
        assert "some result" in result


class TestVmPendingConfig:
    async def test_vm_pending_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"key": "cores", "value": "4"},
                {"key": "memory", "pending": "8192"},
            ]
        )
        result = await vm_pending_config(mock_client, node="pve", vmid=100)
        assert "100" in result
        assert "cores" in result
        assert "memory" in result

    async def test_vm_pending_config_with_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"key": "unused0", "delete": 1},
            ]
        )
        result = await vm_pending_config(mock_client, node="pve", vmid=100)
        assert "DELETE" in result

    async def test_vm_pending_config_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await vm_pending_config(mock_client, node="pve", vmid=100)
        assert "No pending changes" in result


class TestLxcPendingConfig:
    async def test_lxc_pending_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"key": "cores", "value": "2"},
            ]
        )
        result = await lxc_pending_config(mock_client, node="pve", vmid=200)
        assert "200" in result
        assert "cores" in result

    async def test_lxc_pending_config_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await lxc_pending_config(mock_client, node="pve", vmid=200)
        assert "No pending changes" in result


class TestSendVmKey:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await send_vm_key(mock_client, node="pve", vmid=100, key="ctrl+alt+del")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await send_vm_key(client, node="pve", vmid=100, key="ctrl+alt+del", confirm=True)

    async def test_no_key_raises(self, mock_client):
        with pytest.raises(ValueError, match="key is required"):
            await send_vm_key(mock_client, node="pve", vmid=100, key="", confirm=True)

    async def test_send_key(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0400:abc")
        result = await send_vm_key(mock_client, node="pve", vmid=100, key="ctrl+alt+del", confirm=True)
        assert "100" in result
        assert "ctrl+alt+del" in result
        assert "UPID" in result


class TestVmMonitorCommand:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await vm_monitor_command(mock_client, node="pve", vmid=100, command="info")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await vm_monitor_command(client, node="pve", vmid=100, command="info", confirm=True)

    async def test_no_command_raises(self, mock_client):
        with pytest.raises(ValueError, match="command is required"):
            await vm_monitor_command(mock_client, node="pve", vmid=100, command="", confirm=True)

    async def test_monitor_command(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"result": "OK"})
        result = await vm_monitor_command(mock_client, node="pve", vmid=100, command="info", confirm=True)
        assert "100" in result
        assert "monitor" in result.lower()

    async def test_monitor_command_string_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="OK")
        result = await vm_monitor_command(mock_client, node="pve", vmid=100, command="info", confirm=True)
        assert "OK" in result


class TestUnlinkVmDisk:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await unlink_vm_disk(mock_client, node="pve", vmid=100, idlist="scsi0")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await unlink_vm_disk(client, node="pve", vmid=100, idlist="scsi0", confirm=True)

    async def test_no_idlist_raises(self, mock_client):
        with pytest.raises(ValueError, match="idlist is required"):
            await unlink_vm_disk(mock_client, node="pve", vmid=100, idlist="", confirm=True)

    async def test_unlink_disk(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0410:abc")
        result = await unlink_vm_disk(mock_client, node="pve", vmid=100, idlist="scsi0,scsi1", confirm=True)
        assert "100" in result
        assert "unlinked" in result.lower()
        assert "UPID" in result


class TestVmDbusVmstate:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await vm_dbus_vmstate(mock_client, node="pve", vmid=100)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await vm_dbus_vmstate(client, node="pve", vmid=100, confirm=True)

    async def test_dbus_vmstate(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await vm_dbus_vmstate(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "DBus VMstate" in result
