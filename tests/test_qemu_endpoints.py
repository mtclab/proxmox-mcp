from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.cloudinit import (
    agent_file_read,
    agent_file_write,
    agent_fsfreeze_status,
    agent_fstrim,
    agent_get_host_name,
    agent_get_memory_block_info,
    agent_get_memory_blocks,
    agent_get_time,
    agent_get_timezone,
    agent_get_users,
    agent_get_vcpus,
    agent_set_user_password,
    agent_shutdown,
    agent_suspend_disk,
    agent_suspend_hybrid,
    agent_suspend_ram,
)
from proxmox_mcp.config import Config
from proxmox_mcp.firewall import (
    add_vm_firewall_ipset_entry,
    delete_vm_firewall_ipset,
    delete_vm_firewall_ipset_entry,
    get_vm_firewall_ipset,
    get_vm_firewall_rule,
    list_vm_firewall_aliases,
    list_vm_firewall_ipset_content,
    set_vm_firewall_options,
    update_vm_firewall_alias,
    update_vm_firewall_ipset,
    update_vm_firewall_rule,
    vm_firewall_log,
    vm_firewall_refs,
)
from proxmox_mcp.lifecycle import (
    get_vm_config,
    remote_migrate_vm,
    update_vm_config,
    vm_rrddata,
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


class TestGetVmFirewallRule:
    async def test_get_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = await get_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0)
        assert "ACCEPT" in result
        assert "0" in result

    async def test_get_rule_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"pos": 1, "action": "DROP"})
        result = await get_vm_firewall_rule(mock_client, node="pve", vmid=200, pos=1, vmtype="lxc")
        assert "DROP" in result

    async def test_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await get_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, vmtype="bad")


class TestUpdateVmFirewallRule:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, action="DROP")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_vm_firewall_rule(client, node="pve", vmid=100, pos=0, action="DROP", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, confirm=True)

    async def test_update_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, action="DROP", confirm=True)
        assert "updated" in result


class TestSetVmFirewallOptions:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await set_vm_firewall_options(mock_client, node="pve", vmid=100, enable=1)

    async def test_no_kwargs_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            await set_vm_firewall_options(mock_client, node="pve", vmid=100, confirm=True)

    async def test_set_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await set_vm_firewall_options(mock_client, node="pve", vmid=100, enable=1, confirm=True)
        assert "updated" in result


class TestListVmFirewallAliases:
    async def test_list_aliases(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"name": "test", "cidr": "10.0.0.0/8"}])
        result = await list_vm_firewall_aliases(mock_client, node="pve", vmid=100)
        assert "test" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_vm_firewall_aliases(mock_client, node="pve", vmid=100)
        assert "No aliases found" in result


class TestUpdateVmFirewallAlias:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", cidr="10.0.0.0/8")

    async def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await update_vm_firewall_alias(mock_client, node="pve", vmid=100, confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", confirm=True)

    async def test_update_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_vm_firewall_alias(
            mock_client,
            node="pve",
            vmid=100,
            name="test",
            cidr="10.0.0.0/8",
            confirm=True,
        )
        assert "updated" in result


class TestListVmFirewallIpsetContent:
    async def test_list_content(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"cidr": "10.0.0.1/32"}])
        result = await list_vm_firewall_ipset_content(mock_client, node="pve", vmid=100, name="testset")
        assert "10.0.0.1" in result

    async def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await list_vm_firewall_ipset_content(mock_client, node="pve", vmid=100)


class TestGetVmFirewallIpset:
    async def test_get_ipset(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"cidr": "10.0.0.1/32", "comment": "test"})
        result = await get_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")
        assert "10.0.0.1" in result

    async def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await get_vm_firewall_ipset(mock_client, node="pve", vmid=100, cidr="10.0.0.1/32")

    async def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await get_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset")


class TestUpdateVmFirewallIpset:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")

    async def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await update_vm_firewall_ipset(mock_client, node="pve", vmid=100, confirm=True)

    async def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await update_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_vm_firewall_ipset(
            mock_client,
            node="pve",
            vmid=100,
            name="testset",
            cidr="10.0.0.1/32",
            comment="updated",
            confirm=True,
        )
        assert "updated" in result


class TestDeleteVmFirewallIpset:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset")

    async def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await delete_vm_firewall_ipset(mock_client, node="pve", vmid=100, confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", confirm=True)
        assert "deleted" in result


class TestAddVmFirewallIpsetEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await add_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")

    async def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await add_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, cidr="10.0.0.1/32", confirm=True)

    async def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await add_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", confirm=True)

    async def test_add(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await add_vm_firewall_ipset_entry(
            mock_client,
            node="pve",
            vmid=100,
            name="testset",
            cidr="10.0.0.1/32",
            confirm=True,
        )
        assert "added" in result


class TestDeleteVmFirewallIpsetEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")

    async def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await delete_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, cidr="10.0.0.1/32", confirm=True)

    async def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await delete_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_vm_firewall_ipset_entry(
            mock_client,
            node="pve",
            vmid=100,
            name="testset",
            cidr="10.0.0.1/32",
            confirm=True,
        )
        assert "deleted" in result


class TestVmFirewallLog:
    async def test_log(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"proto": "tcp", "action": "ACCEPT", "src": "10.0.0.1", "dst": "10.0.0.2", "dport": "80"},
            ],
        )
        result = await vm_firewall_log(mock_client, node="pve", vmid=100)
        assert "tcp" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await vm_firewall_log(mock_client, node="pve", vmid=100)
        assert "No log entries" in result


class TestVmFirewallRefs:
    async def test_refs(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"ref": "alias1", "type": "alias"}])
        result = await vm_firewall_refs(mock_client, node="pve", vmid=100)
        assert "alias1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await vm_firewall_refs(mock_client, node="pve", vmid=100)
        assert "No references" in result


class TestAgentFstrim:
    async def test_fstrim(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": 0})
        result = await agent_fstrim(mock_client, node="pve", vmid=100, confirm=True)
        assert "Fstrim" in result

    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await agent_fstrim(mock_client, node="pve", vmid=100, confirm=False)


class TestAgentFsfreezeStatus:
    async def test_status(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"frozen": False}})
        result = await agent_fsfreeze_status(mock_client, node="pve", vmid=100)
        assert "Fsfreeze status" in result


class TestAgentGetHostName:
    async def test_get_host_name(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"host-name": "testvm"}})
        result = await agent_get_host_name(mock_client, node="pve", vmid=100)
        assert "Host name" in result


class TestAgentGetMemoryBlockInfo:
    async def test_memory_block_info(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"size": 1048576}})
        result = await agent_get_memory_block_info(mock_client, node="pve", vmid=100)
        assert "Memory block info" in result


class TestAgentGetMemoryBlocks:
    async def test_memory_blocks(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"count": 512}})
        result = await agent_get_memory_blocks(mock_client, node="pve", vmid=100)
        assert "Memory blocks" in result


class TestAgentGetTime:
    async def test_get_time(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"time": 1700000000}})
        result = await agent_get_time(mock_client, node="pve", vmid=100)
        assert "Time" in result


class TestAgentGetTimezone:
    async def test_get_timezone(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"zone": "UTC"}})
        result = await agent_get_timezone(mock_client, node="pve", vmid=100)
        assert "Timezone" in result


class TestAgentGetUsers:
    async def test_get_users(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": [{"name": "root"}]})
        result = await agent_get_users(mock_client, node="pve", vmid=100)
        assert "root" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": []})
        result = await agent_get_users(mock_client, node="pve", vmid=100)
        assert "No users found" in result


class TestAgentGetVcpus:
    async def test_get_vcpus(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": [{"id": 0, "online": True}]})
        result = await agent_get_vcpus(mock_client, node="pve", vmid=100)
        assert "VCPUs" in result


class TestAgentSetUserPassword:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await agent_set_user_password(mock_client, node="pve", vmid=100, username="root", password="test")

    async def test_username_required(self, mock_client):
        with pytest.raises(ValueError, match="username is required"):
            await agent_set_user_password(mock_client, node="pve", vmid=100, password="test", confirm=True)

    async def test_password_required(self, mock_client):
        with pytest.raises(ValueError, match="password is required"):
            await agent_set_user_password(mock_client, node="pve", vmid=100, username="root", confirm=True)

    async def test_set_password(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await agent_set_user_password(
            mock_client,
            node="pve",
            vmid=100,
            username="root",
            password="secret",
            confirm=True,
        )
        assert "Password set" in result


class TestAgentFileRead:
    async def test_filepath_required(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            await agent_file_read(mock_client, node="pve", vmid=100)

    async def test_file_read(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"content": "hello"}})
        result = await agent_file_read(mock_client, node="pve", vmid=100, filepath="/etc/hostname")
        assert "File read" in result


class TestAgentFileWrite:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await agent_file_write(mock_client, node="pve", vmid=100, filepath="/tmp/test")

    async def test_filepath_required(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            await agent_file_write(mock_client, node="pve", vmid=100, confirm=True)

    async def test_file_write(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await agent_file_write(
            mock_client,
            node="pve",
            vmid=100,
            filepath="/tmp/test",
            content="hello",
            confirm=True,
        )
        assert "written" in result


class TestAgentShutdown:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await agent_shutdown(mock_client, node="pve", vmid=100, confirm=False)

    async def test_shutdown(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await agent_shutdown(mock_client, node="pve", vmid=100, confirm=True)
        assert "shutdown" in result.lower()


class TestAgentSuspendDisk:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await agent_suspend_disk(mock_client, node="pve", vmid=100, confirm=False)

    async def test_suspend_disk(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await agent_suspend_disk(mock_client, node="pve", vmid=100, confirm=True)
        assert "suspend-to-disk" in result.lower()


class TestAgentSuspendRam:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await agent_suspend_ram(mock_client, node="pve", vmid=100, confirm=False)

    async def test_suspend_ram(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await agent_suspend_ram(mock_client, node="pve", vmid=100, confirm=True)
        assert "suspend-to-ram" in result.lower()


class TestAgentSuspendHybrid:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await agent_suspend_hybrid(mock_client, node="pve", vmid=100, confirm=False)

    async def test_suspend_hybrid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await agent_suspend_hybrid(mock_client, node="pve", vmid=100, confirm=True)
        assert "hybrid suspend" in result.lower()


class TestGetVmConfig:
    async def test_get_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"cores": 2, "memory": 4096})
        result = await get_vm_config(mock_client, node="pve", vmid=100)
        assert "cores" in result
        assert "memory" in result

    async def test_get_current_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"cores": 2})
        result = await get_vm_config(mock_client, node="pve", vmid=100, current=True)
        assert "cores" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("current") == 1


class TestUpdateVmConfig:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_vm_config(mock_client, node="pve", vmid=100, cores=4)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_vm_config(mock_client, node="pve", vmid=100, confirm=True)

    async def test_update_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001:abc")
        result = await update_vm_config(mock_client, node="pve", vmid=100, cores=4, confirm=True)
        assert "updated" in result


class TestVmRrddata:
    async def test_rrddata(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"cpu": 0.5, "time": 1700000000}])
        result = await vm_rrddata(mock_client, node="pve", vmid=100)
        assert "RRD data" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await vm_rrddata(mock_client, node="pve", vmid=100)
        assert "No data" in result


class TestRemoteMigrateVm:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await remote_migrate_vm(mock_client, node="pve", vmid=100, target_address="10.0.0.1")

    async def test_target_address_required(self, mock_client):
        with pytest.raises(ValueError, match="target_address is required"):
            await remote_migrate_vm(mock_client, node="pve", vmid=100, confirm=True)

    async def test_migrate(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0001:abc")
        result = await remote_migrate_vm(mock_client, node="pve", vmid=100, target_address="10.0.0.1", confirm=True)
        assert "remote migration" in result.lower()
