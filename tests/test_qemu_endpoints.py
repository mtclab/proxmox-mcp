from unittest.mock import MagicMock, patch

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
    def test_get_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = get_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0)
        assert "ACCEPT" in result
        assert "0" in result

    def test_get_rule_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"pos": 1, "action": "DROP"})
        result = get_vm_firewall_rule(mock_client, node="pve", vmid=200, pos=1, vmtype="lxc")
        assert "DROP" in result

    def test_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            get_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, vmtype="bad")


class TestUpdateVmFirewallRule:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, action="DROP")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_vm_firewall_rule(client, node="pve", vmid=100, pos=0, action="DROP", confirm=True)

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, confirm=True)

    def test_update_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, action="DROP", confirm=True)
        assert "updated" in result


class TestSetVmFirewallOptions:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            set_vm_firewall_options(mock_client, node="pve", vmid=100, enable=1)

    def test_no_kwargs_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            set_vm_firewall_options(mock_client, node="pve", vmid=100, confirm=True)

    def test_set_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = set_vm_firewall_options(mock_client, node="pve", vmid=100, enable=1, confirm=True)
        assert "updated" in result


class TestListVmFirewallAliases:
    def test_list_aliases(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[{"name": "test", "cidr": "10.0.0.0/8"}])
        result = list_vm_firewall_aliases(mock_client, node="pve", vmid=100)
        assert "test" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_vm_firewall_aliases(mock_client, node="pve", vmid=100)
        assert "No aliases found" in result


class TestUpdateVmFirewallAlias:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", cidr="10.0.0.0/8")

    def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            update_vm_firewall_alias(mock_client, node="pve", vmid=100, confirm=True)

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", confirm=True)

    def test_update_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_vm_firewall_alias(
            mock_client, node="pve", vmid=100, name="test", cidr="10.0.0.0/8", confirm=True,
        )
        assert "updated" in result


class TestListVmFirewallIpsetContent:
    def test_list_content(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[{"cidr": "10.0.0.1/32"}])
        result = list_vm_firewall_ipset_content(mock_client, node="pve", vmid=100, name="testset")
        assert "10.0.0.1" in result

    def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            list_vm_firewall_ipset_content(mock_client, node="pve", vmid=100)


class TestGetVmFirewallIpset:
    def test_get_ipset(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"cidr": "10.0.0.1/32", "comment": "test"})
        result = get_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")
        assert "10.0.0.1" in result

    def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            get_vm_firewall_ipset(mock_client, node="pve", vmid=100, cidr="10.0.0.1/32")

    def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            get_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset")


class TestUpdateVmFirewallIpset:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")

    def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            update_vm_firewall_ipset(mock_client, node="pve", vmid=100, confirm=True)

    def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            update_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", confirm=True)

    def test_update(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_vm_firewall_ipset(
            mock_client, node="pve", vmid=100, name="testset",
            cidr="10.0.0.1/32", comment="updated", confirm=True,
        )
        assert "updated" in result


class TestDeleteVmFirewallIpset:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset")

    def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            delete_vm_firewall_ipset(mock_client, node="pve", vmid=100, confirm=True)

    def test_delete(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_vm_firewall_ipset(mock_client, node="pve", vmid=100, name="testset", confirm=True)
        assert "deleted" in result


class TestAddVmFirewallIpsetEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            add_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")

    def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            add_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, cidr="10.0.0.1/32", confirm=True)

    def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            add_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", confirm=True)

    def test_add(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = add_vm_firewall_ipset_entry(
            mock_client, node="pve", vmid=100, name="testset",
            cidr="10.0.0.1/32", confirm=True,
        )
        assert "added" in result


class TestDeleteVmFirewallIpsetEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", cidr="10.0.0.1/32")

    def test_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            delete_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, cidr="10.0.0.1/32", confirm=True)

    def test_cidr_required(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            delete_vm_firewall_ipset_entry(mock_client, node="pve", vmid=100, name="testset", confirm=True)

    def test_delete(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_vm_firewall_ipset_entry(
            mock_client, node="pve", vmid=100, name="testset",
            cidr="10.0.0.1/32", confirm=True,
        )
        assert "deleted" in result


class TestVmFirewallLog:
    def test_log(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value=[
                {"proto": "tcp", "action": "ACCEPT",
                 "src": "10.0.0.1", "dst": "10.0.0.2", "dport": "80"},
            ],
        )
        result = vm_firewall_log(mock_client, node="pve", vmid=100)
        assert "tcp" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = vm_firewall_log(mock_client, node="pve", vmid=100)
        assert "No log entries" in result


class TestVmFirewallRefs:
    def test_refs(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[{"ref": "alias1", "type": "alias"}])
        result = vm_firewall_refs(mock_client, node="pve", vmid=100)
        assert "alias1" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = vm_firewall_refs(mock_client, node="pve", vmid=100)
        assert "No references" in result


class TestAgentFstrim:
    def test_fstrim(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": 0})
        result = agent_fstrim(mock_client, node="pve", vmid=100, confirm=True)
        assert "Fstrim" in result

    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_fstrim(mock_client, node="pve", vmid=100, confirm=False)


class TestAgentFsfreezeStatus:
    def test_status(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"frozen": False}})
        result = agent_fsfreeze_status(mock_client, node="pve", vmid=100)
        assert "Fsfreeze status" in result


class TestAgentGetHostName:
    def test_get_host_name(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"host-name": "testvm"}})
        result = agent_get_host_name(mock_client, node="pve", vmid=100)
        assert "Host name" in result


class TestAgentGetMemoryBlockInfo:
    def test_memory_block_info(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"size": 1048576}})
        result = agent_get_memory_block_info(mock_client, node="pve", vmid=100)
        assert "Memory block info" in result


class TestAgentGetMemoryBlocks:
    def test_memory_blocks(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"count": 512}})
        result = agent_get_memory_blocks(mock_client, node="pve", vmid=100)
        assert "Memory blocks" in result


class TestAgentGetTime:
    def test_get_time(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"time": 1700000000}})
        result = agent_get_time(mock_client, node="pve", vmid=100)
        assert "Time" in result


class TestAgentGetTimezone:
    def test_get_timezone(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"zone": "UTC"}})
        result = agent_get_timezone(mock_client, node="pve", vmid=100)
        assert "Timezone" in result


class TestAgentGetUsers:
    def test_get_users(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": [{"name": "root"}]})
        result = agent_get_users(mock_client, node="pve", vmid=100)
        assert "root" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": []})
        result = agent_get_users(mock_client, node="pve", vmid=100)
        assert "No users found" in result


class TestAgentGetVcpus:
    def test_get_vcpus(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": [{"id": 0, "online": True}]})
        result = agent_get_vcpus(mock_client, node="pve", vmid=100)
        assert "VCPUs" in result


class TestAgentSetUserPassword:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_set_user_password(mock_client, node="pve", vmid=100, username="root", password="test")

    def test_username_required(self, mock_client):
        with pytest.raises(ValueError, match="username is required"):
            agent_set_user_password(mock_client, node="pve", vmid=100, password="test", confirm=True)

    def test_password_required(self, mock_client):
        with pytest.raises(ValueError, match="password is required"):
            agent_set_user_password(mock_client, node="pve", vmid=100, username="root", confirm=True)

    def test_set_password(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = agent_set_user_password(
            mock_client, node="pve", vmid=100, username="root",
            password="secret", confirm=True,
        )
        assert "Password set" in result


class TestAgentFileRead:
    def test_filepath_required(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            agent_file_read(mock_client, node="pve", vmid=100)

    def test_file_read(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"content": "hello"}})
        result = agent_file_read(mock_client, node="pve", vmid=100, filepath="/etc/hostname")
        assert "File read" in result


class TestAgentFileWrite:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_file_write(mock_client, node="pve", vmid=100, filepath="/tmp/test")

    def test_filepath_required(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            agent_file_write(mock_client, node="pve", vmid=100, confirm=True)

    def test_file_write(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = agent_file_write(
            mock_client, node="pve", vmid=100,
            filepath="/tmp/test", content="hello", confirm=True,
        )
        assert "written" in result


class TestAgentShutdown:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_shutdown(mock_client, node="pve", vmid=100, confirm=False)

    def test_shutdown(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = agent_shutdown(mock_client, node="pve", vmid=100, confirm=True)
        assert "shutdown" in result.lower()


class TestAgentSuspendDisk:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_suspend_disk(mock_client, node="pve", vmid=100, confirm=False)

    def test_suspend_disk(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = agent_suspend_disk(mock_client, node="pve", vmid=100, confirm=True)
        assert "suspend-to-disk" in result.lower()


class TestAgentSuspendRam:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_suspend_ram(mock_client, node="pve", vmid=100, confirm=False)

    def test_suspend_ram(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = agent_suspend_ram(mock_client, node="pve", vmid=100, confirm=True)
        assert "suspend-to-ram" in result.lower()


class TestAgentSuspendHybrid:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_suspend_hybrid(mock_client, node="pve", vmid=100, confirm=False)

    def test_suspend_hybrid(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = agent_suspend_hybrid(mock_client, node="pve", vmid=100, confirm=True)
        assert "hybrid suspend" in result.lower()


class TestGetVmConfig:
    def test_get_config(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"cores": 2, "memory": 4096})
        result = get_vm_config(mock_client, node="pve", vmid=100)
        assert "cores" in result
        assert "memory" in result

    def test_get_current_config(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"cores": 2})
        result = get_vm_config(mock_client, node="pve", vmid=100, current=True)
        assert "cores" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("current") == 1


class TestUpdateVmConfig:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_vm_config(mock_client, node="pve", vmid=100, cores=4)

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_vm_config(mock_client, node="pve", vmid=100, confirm=True)

    def test_update_config(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0001:abc")
        result = update_vm_config(mock_client, node="pve", vmid=100, cores=4, confirm=True)
        assert "updated" in result


class TestVmRrddata:
    def test_rrddata(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[{"cpu": 0.5, "time": 1700000000}])
        result = vm_rrddata(mock_client, node="pve", vmid=100)
        assert "RRD data" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = vm_rrddata(mock_client, node="pve", vmid=100)
        assert "No data" in result


class TestRemoteMigrateVm:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            remote_migrate_vm(mock_client, node="pve", vmid=100, target_address="10.0.0.1")

    def test_target_address_required(self, mock_client):
        with pytest.raises(ValueError, match="target_address is required"):
            remote_migrate_vm(mock_client, node="pve", vmid=100, confirm=True)

    def test_migrate(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0001:abc")
        result = remote_migrate_vm(mock_client, node="pve", vmid=100, target_address="10.0.0.1", confirm=True)
        assert "remote migration" in result.lower()
