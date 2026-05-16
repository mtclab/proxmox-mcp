from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.firewall import (
    add_cluster_firewall_ipset_entry,
    create_cluster_firewall_alias,
    create_cluster_firewall_ipset,
    create_cluster_firewall_rule,
    create_node_firewall_rule,
    create_vm_firewall_alias,
    create_vm_firewall_rule,
    delete_cluster_firewall_alias,
    delete_cluster_firewall_ipset,
    delete_cluster_firewall_ipset_entry,
    delete_cluster_firewall_rule,
    delete_node_firewall_rule,
    delete_vm_firewall_alias,
    delete_vm_firewall_rule,
    get_cluster_firewall_alias,
    get_cluster_firewall_ipset_entry,
    get_cluster_firewall_options,
    get_cluster_firewall_rule,
    get_node_firewall_options,
    get_node_firewall_rule,
    get_vm_firewall_alias,
    get_vm_firewall_options,
    list_cluster_firewall_aliases,
    list_cluster_firewall_ipset_content,
    list_cluster_firewall_ipsets,
    list_cluster_firewall_macros,
    list_cluster_firewall_refs,
    list_cluster_firewall_rules,
    list_node_firewall_aliases,
    list_node_firewall_ipsets,
    list_node_firewall_rules,
    list_vm_firewall_ipsets,
    list_vm_firewall_rules,
    node_firewall_log,
    set_cluster_firewall_options,
    set_node_firewall_options,
    update_cluster_firewall_alias,
    update_cluster_firewall_ipset,
    update_cluster_firewall_rule,
    update_node_firewall_rule,
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


class TestConfirmRequiredCluster:
    async def test_create_cluster_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_cluster_firewall_rule(mock_client, action="ACCEPT")

    async def test_update_cluster_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_cluster_firewall_rule(mock_client, pos=0, action="DROP")

    async def test_delete_cluster_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_cluster_firewall_rule(mock_client, pos=0)

    async def test_set_cluster_firewall_options_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await set_cluster_firewall_options(mock_client, enable=1)

    async def test_create_cluster_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_cluster_firewall_alias(mock_client, name="test", cidr="10.0.0.0/8")

    async def test_delete_cluster_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_cluster_firewall_alias(mock_client, name="test")


class TestConfirmRequiredNode:
    async def test_create_node_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_node_firewall_rule(mock_client, node="pve", action="ACCEPT")

    async def test_delete_node_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_node_firewall_rule(mock_client, node="pve", pos=0)


class TestConfirmRequiredVM:
    async def test_create_vm_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_vm_firewall_rule(mock_client, node="pve", vmid=100, action="ACCEPT")

    async def test_delete_vm_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0)

    async def test_create_vm_rule_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await create_vm_firewall_rule(mock_client, node="pve", vmid=100, vmtype="invalid", confirm=True)

    async def test_delete_vm_rule_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await delete_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, vmtype="invalid", confirm=True)

    async def test_list_vm_rules_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await list_vm_firewall_rules(mock_client, node="pve", vmid=100, vmtype="invalid")

    async def test_get_vm_firewall_options_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await get_vm_firewall_options(mock_client, node="pve", vmid=100, vmtype="invalid")


class TestElevatedCheckCluster:
    async def test_create_cluster_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_cluster_firewall_rule(client, action="ACCEPT", confirm=True)

    async def test_update_cluster_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_cluster_firewall_rule(client, pos=0, action="DROP", confirm=True)

    async def test_delete_cluster_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_cluster_firewall_rule(client, pos=0, confirm=True)

    async def test_set_cluster_firewall_options_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await set_cluster_firewall_options(client, enable=1, confirm=True)

    async def test_create_cluster_alias_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_cluster_firewall_alias(client, name="test", cidr="10.0.0.0/8", confirm=True)

    async def test_delete_cluster_alias_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_cluster_firewall_alias(client, name="test", confirm=True)


class TestElevatedCheckNode:
    async def test_create_node_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_node_firewall_rule(client, node="pve", action="ACCEPT", confirm=True)

    async def test_delete_node_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_node_firewall_rule(client, node="pve", pos=0, confirm=True)


class TestElevatedCheckVM:
    async def test_create_vm_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_vm_rule_requires_elevated_inner(client)

    async def test_delete_vm_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_vm_firewall_rule(client, node="pve", vmid=100, pos=0, confirm=True)


async def create_vm_rule_requires_elevated_inner(client):
    await create_vm_firewall_rule(client, node="pve", vmid=100, action="ACCEPT", confirm=True)


class TestListClusterFirewallRules:
    async def test_list_rules_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"pos": 0, "action": "ACCEPT", "type": "in", "dport": "22", "proto": "tcp", "comment": "SSH"},
                {"pos": 1, "action": "DROP", "source": "10.0.0.0/8"},
            ]
        )
        result = await list_cluster_firewall_rules(mock_client)
        assert "ACCEPT" in result
        assert "DROP" in result
        assert "SSH" in result

    async def test_list_rules_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cluster_firewall_rules(mock_client)
        assert "No rules found" in result

    async def test_list_rules_dict_response(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = await list_cluster_firewall_rules(mock_client)
        assert "ACCEPT" in result


class TestGetClusterFirewallRule:
    async def test_get_rule_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "pos": 0,
                "action": "ACCEPT",
                "type": "in",
            }
        )
        result = await get_cluster_firewall_rule(mock_client, pos=0)
        assert "0" in result
        assert "ACCEPT" in result

    async def test_get_rule_string_response(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="raw data")
        result = await get_cluster_firewall_rule(mock_client, pos=0)
        assert "raw data" in result


class TestCreateClusterFirewallRule:
    async def test_create_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "0"})
        result = await create_cluster_firewall_rule(mock_client, action="ACCEPT", dport="22", proto="tcp", confirm=True)
        assert "ACCEPT" in result

    async def test_create_rule_minimal(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="1")
        result = await create_cluster_firewall_rule(mock_client, action="DROP", confirm=True)
        assert "DROP" in result


class TestUpdateClusterFirewallRule:
    async def test_update_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_cluster_firewall_rule(mock_client, pos=0, action="DROP", confirm=True)
        assert "0" in result
        assert "updated" in result

    async def test_update_rule_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_cluster_firewall_rule(mock_client, pos=0, confirm=True)


class TestDeleteClusterFirewallRule:
    async def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_cluster_firewall_rule(mock_client, pos=0, confirm=True)
        assert "0" in result
        assert "deleted" in result


class TestClusterFirewallOptions:
    async def test_get_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"enable": 1, "policy_in": "DROP"})
        result = await get_cluster_firewall_options(mock_client)
        assert "enable" in result
        assert "policy_in" in result

    async def test_get_options_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await get_cluster_firewall_options(mock_client)
        assert "No options found" in result

    async def test_set_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await set_cluster_firewall_options(mock_client, enable=1, confirm=True)
        assert "updated" in result

    async def test_set_options_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            await set_cluster_firewall_options(mock_client, confirm=True)


class TestClusterFirewallAliases:
    async def test_list_aliases(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "localnet", "cidr": "10.0.0.0/8", "comment": "RFC1918"},
            ]
        )
        result = await list_cluster_firewall_aliases(mock_client)
        assert "localnet" in result
        assert "10.0.0.0/8" in result

    async def test_list_aliases_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cluster_firewall_aliases(mock_client)
        assert "No aliases found" in result

    async def test_create_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_cluster_firewall_alias(mock_client, name="test", cidr="10.0.0.0/8", confirm=True)
        assert "test" in result
        assert "created" in result

    async def test_create_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_cluster_firewall_alias(mock_client, name="", cidr="10.0.0.0/8", confirm=True)

    async def test_create_alias_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await create_cluster_firewall_alias(mock_client, name="test", cidr="", confirm=True)

    async def test_delete_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_cluster_firewall_alias(mock_client, name="test", confirm=True)
        assert "test" in result
        assert "deleted" in result

    async def test_delete_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await delete_cluster_firewall_alias(mock_client, name="", confirm=True)


class TestClusterFirewallIPSets:
    async def test_list_ipsets(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "blacklist", "comment": "Blocked IPs"},
            ]
        )
        result = await list_cluster_firewall_ipsets(mock_client)
        assert "blacklist" in result

    async def test_list_ipsets_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cluster_firewall_ipsets(mock_client)
        assert "No IPSets found" in result


class TestClusterFirewallRefs:
    async def test_list_refs(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"ref": "localnet", "type": "alias", "comment": "Local network"},
            ]
        )
        result = await list_cluster_firewall_refs(mock_client)
        assert "localnet" in result
        assert "alias" in result

    async def test_list_refs_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cluster_firewall_refs(mock_client)
        assert "No references found" in result


class TestListNodeFirewallRules:
    async def test_list_rules(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"pos": 0, "action": "ACCEPT", "dport": "22", "proto": "tcp"},
            ]
        )
        result = await list_node_firewall_rules(mock_client, node="pve")
        assert "pve" in result
        assert "ACCEPT" in result

    async def test_list_rules_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_node_firewall_rules(mock_client, node="pve")
        assert "No rules found" in result


class TestCreateNodeFirewallRule:
    async def test_create_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "0"})
        result = await create_node_firewall_rule(mock_client, node="pve", action="ACCEPT", dport="22", confirm=True)
        assert "pve" in result
        assert "ACCEPT" in result


class TestDeleteNodeFirewallRule:
    async def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_node_firewall_rule(mock_client, node="pve", pos=0, confirm=True)
        assert "pve" in result
        assert "deleted" in result


class TestGetNodeFirewallOptions:
    async def test_get_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"enable": 1})
        result = await get_node_firewall_options(mock_client, node="pve")
        assert "pve" in result
        assert "enable" in result

    async def test_get_options_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await get_node_firewall_options(mock_client, node="pve")
        assert "No options found" in result


class TestListVMFirewallRules:
    async def test_list_rules_qemu(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"pos": 0, "action": "ACCEPT", "dport": "80", "proto": "tcp"},
            ]
        )
        result = await list_vm_firewall_rules(mock_client, node="pve", vmid=100, vmtype="qemu")
        assert "qemu" in result
        assert "100" in result
        assert "ACCEPT" in result

    async def test_list_rules_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_vm_firewall_rules(mock_client, node="pve", vmid=101, vmtype="lxc")
        assert "lxc" in result
        assert "No rules found" in result


class TestCreateVMFirewallRule:
    async def test_create_rule_qemu(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "0"})
        result = await create_vm_firewall_rule(
            mock_client, node="pve", vmid=100, action="ACCEPT", dport="443", confirm=True
        )
        assert "qemu" in result
        assert "100" in result

    async def test_create_rule_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="1")
        result = await create_vm_firewall_rule(
            mock_client, node="pve", vmid=101, vmtype="lxc", action="DROP", confirm=True
        )
        assert "lxc" in result
        assert "101" in result


class TestDeleteVMFirewallRule:
    async def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, confirm=True)
        assert "0" in result
        assert "deleted" in result
        assert "qemu" in result

    async def test_delete_rule_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_vm_firewall_rule(mock_client, node="pve", vmid=101, pos=1, vmtype="lxc", confirm=True)
        assert "lxc" in result
        assert "1" in result


class TestGetVMFirewallOptions:
    async def test_get_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"enable": 1, "dhcp": 1})
        result = await get_vm_firewall_options(mock_client, node="pve", vmid=100)
        assert "qemu" in result
        assert "100" in result
        assert "enable" in result

    async def test_get_options_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await get_vm_firewall_options(mock_client, node="pve", vmid=100)
        assert "No options found" in result

    async def test_get_options_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"enable": 0})
        result = await get_vm_firewall_options(mock_client, node="pve", vmid=101, vmtype="lxc")
        assert "lxc" in result


class TestGetVMFirewallAlias:
    async def test_get_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "localnet", "cidr": "10.0.0.0/8"})
        result = await get_vm_firewall_alias(mock_client, node="pve", vmid=100, name="localnet")
        assert "localnet" in result

    async def test_get_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await get_vm_firewall_alias(mock_client, node="pve", vmid=100, name="")

    async def test_get_alias_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await get_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", vmtype="invalid")


class TestCreateVMFirewallAlias:
    async def test_create_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_vm_firewall_alias(
            mock_client,
            node="pve",
            vmid=100,
            name="test",
            cidr="10.0.0.0/8",
            confirm=True,
        )
        assert "test" in result
        assert "created" in result.lower()

    async def test_create_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_vm_firewall_alias(mock_client, node="pve", vmid=100, name="", cidr="10.0.0.0/8", confirm=True)

    async def test_create_alias_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await create_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", cidr="", confirm=True)

    async def test_create_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", cidr="10.0.0.0/8")

    async def test_create_alias_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_vm_firewall_alias(
            mock_client,
            node="pve",
            vmid=101,
            name="test",
            cidr="10.0.0.0/8",
            vmtype="lxc",
            confirm=True,
        )
        assert "lxc" in result


class TestDeleteVMFirewallAlias:
    async def test_delete_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", confirm=True)
        assert "test" in result
        assert "deleted" in result.lower()

    async def test_delete_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await delete_vm_firewall_alias(mock_client, node="pve", vmid=100, name="", confirm=True)

    async def test_delete_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test")


class TestListVMFirewallIPSets:
    async def test_list_ipsets(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "blacklist", "comment": "Blocked"},
            ]
        )
        result = await list_vm_firewall_ipsets(mock_client, node="pve", vmid=100)
        assert "blacklist" in result

    async def test_list_ipsets_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_vm_firewall_ipsets(mock_client, node="pve", vmid=100)
        assert "No IPSets found" in result

    async def test_list_ipsets_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_vm_firewall_ipsets(mock_client, node="pve", vmid=101, vmtype="lxc")
        assert "lxc" in result

    async def test_list_ipsets_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await list_vm_firewall_ipsets(mock_client, node="pve", vmid=100, vmtype="invalid")


class TestClusterFirewallIPSetContent:
    async def test_list_ipset_content(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"cidr": "10.0.0.1/32", "comment": "web server"},
            ]
        )
        result = await list_cluster_firewall_ipset_content(mock_client, name="blacklist")
        assert "blacklist" in result
        assert "10.0.0.1" in result

    async def test_list_ipset_content_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cluster_firewall_ipset_content(mock_client, name="blacklist")
        assert "No entries found" in result

    async def test_list_ipset_content_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await list_cluster_firewall_ipset_content(mock_client, name="")


class TestCreateClusterFirewallIPSet:
    async def test_create_ipset(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_cluster_firewall_ipset(mock_client, name="blacklist", confirm=True)
        assert "blacklist" in result
        assert "created" in result.lower()

    async def test_create_ipset_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_cluster_firewall_ipset(mock_client, name="", confirm=True)

    async def test_create_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_cluster_firewall_ipset(mock_client, name="blacklist")


class TestDeleteClusterFirewallIPSet:
    async def test_delete_ipset(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_cluster_firewall_ipset(mock_client, name="blacklist", confirm=True)
        assert "blacklist" in result
        assert "deleted" in result.lower()

    async def test_delete_ipset_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await delete_cluster_firewall_ipset(mock_client, name="", confirm=True)

    async def test_delete_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_cluster_firewall_ipset(mock_client, name="blacklist")


class TestListNodeFirewallAliases:
    async def test_list_aliases(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "localnet", "cidr": "10.0.0.0/8", "comment": "RFC1918"},
            ]
        )
        result = await list_node_firewall_aliases(mock_client, node="pve")
        assert "localnet" in result
        assert "10.0.0.0/8" in result

    async def test_list_aliases_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_node_firewall_aliases(mock_client, node="pve")
        assert "No aliases found" in result


class TestNodeFirewallLog:
    async def test_log(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"proto": "tcp", "action": "ACCEPT", "src": "10.0.0.1", "dst": "10.0.0.2", "dport": "22"},
            ]
        )
        result = await node_firewall_log(mock_client, node="pve")
        assert "pve" in result
        assert "tcp" in result

    async def test_log_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await node_firewall_log(mock_client, node="pve")
        assert "No log entries found" in result


class TestGetClusterFirewallAlias:
    async def test_get_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "localnet", "cidr": "10.0.0.0/8"})
        result = await get_cluster_firewall_alias(mock_client, name="localnet")
        assert "localnet" in result

    async def test_get_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await get_cluster_firewall_alias(mock_client, name="")


class TestUpdateClusterFirewallAlias:
    async def test_update_alias(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_cluster_firewall_alias(mock_client, name="localnet", cidr="10.0.0.0/8", confirm=True)
        assert "localnet" in result
        assert "updated" in result

    async def test_update_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await update_cluster_firewall_alias(mock_client, name="", cidr="10.0.0.0/8", confirm=True)

    async def test_update_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_cluster_firewall_alias(mock_client, name="localnet", cidr="10.0.0.0/8")

    async def test_update_alias_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_cluster_firewall_alias(mock_client, name="localnet", confirm=True)


class TestUpdateClusterFirewallIPSet:
    async def test_update_ipset(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_cluster_firewall_ipset(mock_client, name="blacklist", comment="updated", confirm=True)
        assert "blacklist" in result
        assert "updated" in result

    async def test_update_ipset_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await update_cluster_firewall_ipset(mock_client, name="", confirm=True)

    async def test_update_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_cluster_firewall_ipset(mock_client, name="blacklist", comment="test")


class TestAddClusterFirewallIPSetEntry:
    async def test_add_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await add_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32", confirm=True)
        assert "10.0.0.1/32" in result
        assert "blacklist" in result

    async def test_add_entry_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await add_cluster_firewall_ipset_entry(mock_client, name="", cidr="10.0.0.1/32", confirm=True)

    async def test_add_entry_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await add_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="", confirm=True)

    async def test_add_entry_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await add_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32")


class TestGetClusterFirewallIPSetEntry:
    async def test_get_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"cidr": "10.0.0.1/32", "comment": "web"})
        result = await get_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32")
        assert "blacklist" in result
        assert "10.0.0.1/32" in result

    async def test_get_entry_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await get_cluster_firewall_ipset_entry(mock_client, name="", cidr="10.0.0.1/32")

    async def test_get_entry_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await get_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="")


class TestDeleteClusterFirewallIPSetEntry:
    async def test_delete_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_cluster_firewall_ipset_entry(
            mock_client, name="blacklist", cidr="10.0.0.1/32", confirm=True
        )
        assert "10.0.0.1/32" in result
        assert "Removed" in result

    async def test_delete_entry_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await delete_cluster_firewall_ipset_entry(mock_client, name="", cidr="10.0.0.1/32", confirm=True)

    async def test_delete_entry_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            await delete_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="", confirm=True)

    async def test_delete_entry_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32")


class TestListClusterFirewallMacros:
    async def test_list_macros(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"macro": "SSH", "description": "SSH (port 22)"},
            ]
        )
        result = await list_cluster_firewall_macros(mock_client)
        assert "SSH" in result

    async def test_list_macros_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cluster_firewall_macros(mock_client)
        assert "No macros found" in result


class TestGetNodeFirewallRule:
    async def test_get_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = await get_node_firewall_rule(mock_client, node="pve", pos=0)
        assert "pve" in result
        assert "ACCEPT" in result

    async def test_get_rule_string_response(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="raw data")
        result = await get_node_firewall_rule(mock_client, node="pve", pos=0)
        assert "raw data" in result


class TestUpdateNodeFirewallRule:
    async def test_update_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_node_firewall_rule(mock_client, node="pve", pos=0, action="DROP", confirm=True)
        assert "pve" in result
        assert "updated" in result

    async def test_update_rule_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_node_firewall_rule(mock_client, node="pve", pos=0, confirm=True)

    async def test_update_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_node_firewall_rule(mock_client, node="pve", pos=0, action="DROP")


class TestSetNodeFirewallOptions:
    async def test_set_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await set_node_firewall_options(mock_client, node="pve", enable=1, confirm=True)
        assert "pve" in result
        assert "updated" in result

    async def test_set_options_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            await set_node_firewall_options(mock_client, node="pve", confirm=True)

    async def test_set_options_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await set_node_firewall_options(mock_client, node="pve", enable=1)


class TestListNodeFirewallIPSets:
    async def test_list_ipsets(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "blacklist", "comment": "Blocked IPs"},
            ]
        )
        result = await list_node_firewall_ipsets(mock_client, node="pve")
        assert "blacklist" in result
        assert "pve" in result

    async def test_list_ipsets_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_node_firewall_ipsets(mock_client, node="pve")
        assert "No IPSets found" in result
