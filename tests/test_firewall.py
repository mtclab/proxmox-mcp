from unittest.mock import MagicMock, patch

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
    def test_create_cluster_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_cluster_firewall_rule(mock_client, action="ACCEPT")

    def test_update_cluster_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_cluster_firewall_rule(mock_client, pos=0, action="DROP")

    def test_delete_cluster_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_cluster_firewall_rule(mock_client, pos=0)

    def test_set_cluster_firewall_options_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            set_cluster_firewall_options(mock_client, enable=1)

    def test_create_cluster_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_cluster_firewall_alias(mock_client, name="test", cidr="10.0.0.0/8")

    def test_delete_cluster_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_cluster_firewall_alias(mock_client, name="test")


class TestConfirmRequiredNode:
    def test_create_node_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_node_firewall_rule(mock_client, node="pve", action="ACCEPT")

    def test_delete_node_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_node_firewall_rule(mock_client, node="pve", pos=0)


class TestConfirmRequiredVM:
    def test_create_vm_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_vm_firewall_rule(mock_client, node="pve", vmid=100, action="ACCEPT")

    def test_delete_vm_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0)

    def test_create_vm_rule_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            create_vm_firewall_rule(mock_client, node="pve", vmid=100, vmtype="invalid", confirm=True)

    def test_delete_vm_rule_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            delete_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, vmtype="invalid", confirm=True)

    def test_list_vm_rules_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            list_vm_firewall_rules(mock_client, node="pve", vmid=100, vmtype="invalid")

    def test_get_vm_firewall_options_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            get_vm_firewall_options(mock_client, node="pve", vmid=100, vmtype="invalid")


class TestElevatedCheckCluster:
    def test_create_cluster_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_cluster_firewall_rule(client, action="ACCEPT", confirm=True)

    def test_update_cluster_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_cluster_firewall_rule(client, pos=0, action="DROP", confirm=True)

    def test_delete_cluster_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_cluster_firewall_rule(client, pos=0, confirm=True)

    def test_set_cluster_firewall_options_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            set_cluster_firewall_options(client, enable=1, confirm=True)

    def test_create_cluster_alias_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_cluster_firewall_alias(client, name="test", cidr="10.0.0.0/8", confirm=True)

    def test_delete_cluster_alias_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_cluster_firewall_alias(client, name="test", confirm=True)


class TestElevatedCheckNode:
    def test_create_node_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_node_firewall_rule(client, node="pve", action="ACCEPT", confirm=True)

    def test_delete_node_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_node_firewall_rule(client, node="pve", pos=0, confirm=True)


class TestElevatedCheckVM:
    def test_create_vm_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_vm_rule_requires_elevated_inner(client)

    def test_delete_vm_rule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_vm_firewall_rule(client, node="pve", vmid=100, pos=0, confirm=True)


def create_vm_rule_requires_elevated_inner(client):
    create_vm_firewall_rule(client, node="pve", vmid=100, action="ACCEPT", confirm=True)


class TestListClusterFirewallRules:
    def test_list_rules_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"pos": 0, "action": "ACCEPT", "type": "in", "dport": "22", "proto": "tcp", "comment": "SSH"},
            {"pos": 1, "action": "DROP", "source": "10.0.0.0/8"},
        ])
        result = list_cluster_firewall_rules(mock_client)
        assert "ACCEPT" in result
        assert "DROP" in result
        assert "SSH" in result

    def test_list_rules_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_cluster_firewall_rules(mock_client)
        assert "No rules found" in result

    def test_list_rules_dict_response(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = list_cluster_firewall_rules(mock_client)
        assert "ACCEPT" in result


class TestGetClusterFirewallRule:
    def test_get_rule_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "pos": 0, "action": "ACCEPT", "type": "in",
        })
        result = get_cluster_firewall_rule(mock_client, pos=0)
        assert "0" in result
        assert "ACCEPT" in result

    def test_get_rule_string_response(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="raw data")
        result = get_cluster_firewall_rule(mock_client, pos=0)
        assert "raw data" in result


class TestCreateClusterFirewallRule:
    def test_create_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "0"})
        result = create_cluster_firewall_rule(mock_client, action="ACCEPT", dport="22", proto="tcp", confirm=True)
        assert "ACCEPT" in result

    def test_create_rule_minimal(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="1")
        result = create_cluster_firewall_rule(mock_client, action="DROP", confirm=True)
        assert "DROP" in result


class TestUpdateClusterFirewallRule:
    def test_update_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_cluster_firewall_rule(mock_client, pos=0, action="DROP", confirm=True)
        assert "0" in result
        assert "updated" in result

    def test_update_rule_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_cluster_firewall_rule(mock_client, pos=0, confirm=True)


class TestDeleteClusterFirewallRule:
    def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_cluster_firewall_rule(mock_client, pos=0, confirm=True)
        assert "0" in result
        assert "deleted" in result


class TestClusterFirewallOptions:
    def test_get_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"enable": 1, "policy_in": "DROP"})
        result = get_cluster_firewall_options(mock_client)
        assert "enable" in result
        assert "policy_in" in result

    def test_get_options_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = get_cluster_firewall_options(mock_client)
        assert "No options found" in result

    def test_set_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = set_cluster_firewall_options(mock_client, enable=1, confirm=True)
        assert "updated" in result

    def test_set_options_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            set_cluster_firewall_options(mock_client, confirm=True)


class TestClusterFirewallAliases:
    def test_list_aliases(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "localnet", "cidr": "10.0.0.0/8", "comment": "RFC1918"},
        ])
        result = list_cluster_firewall_aliases(mock_client)
        assert "localnet" in result
        assert "10.0.0.0/8" in result

    def test_list_aliases_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_cluster_firewall_aliases(mock_client)
        assert "No aliases found" in result

    def test_create_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_cluster_firewall_alias(mock_client, name="test", cidr="10.0.0.0/8", confirm=True)
        assert "test" in result
        assert "created" in result

    def test_create_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            create_cluster_firewall_alias(mock_client, name="", cidr="10.0.0.0/8", confirm=True)

    def test_create_alias_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            create_cluster_firewall_alias(mock_client, name="test", cidr="", confirm=True)

    def test_delete_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_cluster_firewall_alias(mock_client, name="test", confirm=True)
        assert "test" in result
        assert "deleted" in result

    def test_delete_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            delete_cluster_firewall_alias(mock_client, name="", confirm=True)


class TestClusterFirewallIPSets:
    def test_list_ipsets(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "blacklist", "comment": "Blocked IPs"},
        ])
        result = list_cluster_firewall_ipsets(mock_client)
        assert "blacklist" in result

    def test_list_ipsets_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_cluster_firewall_ipsets(mock_client)
        assert "No IPSets found" in result


class TestClusterFirewallRefs:
    def test_list_refs(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"ref": "localnet", "type": "alias", "comment": "Local network"},
        ])
        result = list_cluster_firewall_refs(mock_client)
        assert "localnet" in result
        assert "alias" in result

    def test_list_refs_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_cluster_firewall_refs(mock_client)
        assert "No references found" in result


class TestListNodeFirewallRules:
    def test_list_rules(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"pos": 0, "action": "ACCEPT", "dport": "22", "proto": "tcp"},
        ])
        result = list_node_firewall_rules(mock_client, node="pve")
        assert "pve" in result
        assert "ACCEPT" in result

    def test_list_rules_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_firewall_rules(mock_client, node="pve")
        assert "No rules found" in result


class TestCreateNodeFirewallRule:
    def test_create_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "0"})
        result = create_node_firewall_rule(mock_client, node="pve", action="ACCEPT", dport="22", confirm=True)
        assert "pve" in result
        assert "ACCEPT" in result


class TestDeleteNodeFirewallRule:
    def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_node_firewall_rule(mock_client, node="pve", pos=0, confirm=True)
        assert "pve" in result
        assert "deleted" in result


class TestGetNodeFirewallOptions:
    def test_get_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"enable": 1})
        result = get_node_firewall_options(mock_client, node="pve")
        assert "pve" in result
        assert "enable" in result

    def test_get_options_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = get_node_firewall_options(mock_client, node="pve")
        assert "No options found" in result


class TestListVMFirewallRules:
    def test_list_rules_qemu(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"pos": 0, "action": "ACCEPT", "dport": "80", "proto": "tcp"},
        ])
        result = list_vm_firewall_rules(mock_client, node="pve", vmid=100, vmtype="qemu")
        assert "qemu" in result
        assert "100" in result
        assert "ACCEPT" in result

    def test_list_rules_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_vm_firewall_rules(mock_client, node="pve", vmid=101, vmtype="lxc")
        assert "lxc" in result
        assert "No rules found" in result


class TestCreateVMFirewallRule:
    def test_create_rule_qemu(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "0"})
        result = create_vm_firewall_rule(mock_client, node="pve", vmid=100, action="ACCEPT", dport="443", confirm=True)
        assert "qemu" in result
        assert "100" in result

    def test_create_rule_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="1")
        result = create_vm_firewall_rule(mock_client, node="pve", vmid=101, vmtype="lxc", action="DROP", confirm=True)
        assert "lxc" in result
        assert "101" in result


class TestDeleteVMFirewallRule:
    def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_vm_firewall_rule(mock_client, node="pve", vmid=100, pos=0, confirm=True)
        assert "0" in result
        assert "deleted" in result
        assert "qemu" in result

    def test_delete_rule_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_vm_firewall_rule(mock_client, node="pve", vmid=101, pos=1, vmtype="lxc", confirm=True)
        assert "lxc" in result
        assert "1" in result


class TestGetVMFirewallOptions:
    def test_get_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"enable": 1, "dhcp": 1})
        result = get_vm_firewall_options(mock_client, node="pve", vmid=100)
        assert "qemu" in result
        assert "100" in result
        assert "enable" in result

    def test_get_options_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = get_vm_firewall_options(mock_client, node="pve", vmid=100)
        assert "No options found" in result

    def test_get_options_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"enable": 0})
        result = get_vm_firewall_options(mock_client, node="pve", vmid=101, vmtype="lxc")
        assert "lxc" in result


class TestGetVMFirewallAlias:
    def test_get_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"name": "localnet", "cidr": "10.0.0.0/8"})
        result = get_vm_firewall_alias(mock_client, node="pve", vmid=100, name="localnet")
        assert "localnet" in result

    def test_get_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            get_vm_firewall_alias(mock_client, node="pve", vmid=100, name="")

    def test_get_alias_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            get_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", vmtype="invalid")


class TestCreateVMFirewallAlias:
    def test_create_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_vm_firewall_alias(
            mock_client, node="pve", vmid=100,
            name="test", cidr="10.0.0.0/8", confirm=True,
        )
        assert "test" in result
        assert "created" in result.lower()

    def test_create_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            create_vm_firewall_alias(mock_client, node="pve", vmid=100, name="", cidr="10.0.0.0/8", confirm=True)

    def test_create_alias_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            create_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", cidr="", confirm=True)

    def test_create_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", cidr="10.0.0.0/8")

    def test_create_alias_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_vm_firewall_alias(
            mock_client, node="pve", vmid=101,
            name="test", cidr="10.0.0.0/8", vmtype="lxc", confirm=True,
        )
        assert "lxc" in result


class TestDeleteVMFirewallAlias:
    def test_delete_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test", confirm=True)
        assert "test" in result
        assert "deleted" in result.lower()

    def test_delete_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            delete_vm_firewall_alias(mock_client, node="pve", vmid=100, name="", confirm=True)

    def test_delete_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_vm_firewall_alias(mock_client, node="pve", vmid=100, name="test")


class TestListVMFirewallIPSets:
    def test_list_ipsets(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "blacklist", "comment": "Blocked"},
        ])
        result = list_vm_firewall_ipsets(mock_client, node="pve", vmid=100)
        assert "blacklist" in result

    def test_list_ipsets_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_vm_firewall_ipsets(mock_client, node="pve", vmid=100)
        assert "No IPSets found" in result

    def test_list_ipsets_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_vm_firewall_ipsets(mock_client, node="pve", vmid=101, vmtype="lxc")
        assert "lxc" in result

    def test_list_ipsets_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            list_vm_firewall_ipsets(mock_client, node="pve", vmid=100, vmtype="invalid")


class TestClusterFirewallIPSetContent:
    def test_list_ipset_content(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"cidr": "10.0.0.1/32", "comment": "web server"},
        ])
        result = list_cluster_firewall_ipset_content(mock_client, name="blacklist")
        assert "blacklist" in result
        assert "10.0.0.1" in result

    def test_list_ipset_content_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_cluster_firewall_ipset_content(mock_client, name="blacklist")
        assert "No entries found" in result

    def test_list_ipset_content_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            list_cluster_firewall_ipset_content(mock_client, name="")


class TestCreateClusterFirewallIPSet:
    def test_create_ipset(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_cluster_firewall_ipset(mock_client, name="blacklist", confirm=True)
        assert "blacklist" in result
        assert "created" in result.lower()

    def test_create_ipset_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            create_cluster_firewall_ipset(mock_client, name="", confirm=True)

    def test_create_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_cluster_firewall_ipset(mock_client, name="blacklist")


class TestDeleteClusterFirewallIPSet:
    def test_delete_ipset(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_cluster_firewall_ipset(mock_client, name="blacklist", confirm=True)
        assert "blacklist" in result
        assert "deleted" in result.lower()

    def test_delete_ipset_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            delete_cluster_firewall_ipset(mock_client, name="", confirm=True)

    def test_delete_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_cluster_firewall_ipset(mock_client, name="blacklist")


class TestListNodeFirewallAliases:
    def test_list_aliases(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "localnet", "cidr": "10.0.0.0/8", "comment": "RFC1918"},
        ])
        result = list_node_firewall_aliases(mock_client, node="pve")
        assert "localnet" in result
        assert "10.0.0.0/8" in result

    def test_list_aliases_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_firewall_aliases(mock_client, node="pve")
        assert "No aliases found" in result


class TestNodeFirewallLog:
    def test_log(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"proto": "tcp", "action": "ACCEPT", "src": "10.0.0.1", "dst": "10.0.0.2", "dport": "22"},
        ])
        result = node_firewall_log(mock_client, node="pve")
        assert "pve" in result
        assert "tcp" in result

    def test_log_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = node_firewall_log(mock_client, node="pve")
        assert "No log entries found" in result


class TestGetClusterFirewallAlias:
    def test_get_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"name": "localnet", "cidr": "10.0.0.0/8"})
        result = get_cluster_firewall_alias(mock_client, name="localnet")
        assert "localnet" in result

    def test_get_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            get_cluster_firewall_alias(mock_client, name="")


class TestUpdateClusterFirewallAlias:
    def test_update_alias(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_cluster_firewall_alias(mock_client, name="localnet", cidr="10.0.0.0/8", confirm=True)
        assert "localnet" in result
        assert "updated" in result

    def test_update_alias_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            update_cluster_firewall_alias(mock_client, name="", cidr="10.0.0.0/8", confirm=True)

    def test_update_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_cluster_firewall_alias(mock_client, name="localnet", cidr="10.0.0.0/8")

    def test_update_alias_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_cluster_firewall_alias(mock_client, name="localnet", confirm=True)


class TestUpdateClusterFirewallIPSet:
    def test_update_ipset(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_cluster_firewall_ipset(mock_client, name="blacklist", comment="updated", confirm=True)
        assert "blacklist" in result
        assert "updated" in result

    def test_update_ipset_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            update_cluster_firewall_ipset(mock_client, name="", confirm=True)

    def test_update_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_cluster_firewall_ipset(mock_client, name="blacklist", comment="test")


class TestAddClusterFirewallIPSetEntry:
    def test_add_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = add_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32", confirm=True)
        assert "10.0.0.1/32" in result
        assert "blacklist" in result

    def test_add_entry_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            add_cluster_firewall_ipset_entry(mock_client, name="", cidr="10.0.0.1/32", confirm=True)

    def test_add_entry_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            add_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="", confirm=True)

    def test_add_entry_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            add_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32")


class TestGetClusterFirewallIPSetEntry:
    def test_get_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"cidr": "10.0.0.1/32", "comment": "web"})
        result = get_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32")
        assert "blacklist" in result
        assert "10.0.0.1/32" in result

    def test_get_entry_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            get_cluster_firewall_ipset_entry(mock_client, name="", cidr="10.0.0.1/32")

    def test_get_entry_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            get_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="")


class TestDeleteClusterFirewallIPSetEntry:
    def test_delete_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32", confirm=True)
        assert "10.0.0.1/32" in result
        assert "Removed" in result

    def test_delete_entry_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            delete_cluster_firewall_ipset_entry(mock_client, name="", cidr="10.0.0.1/32", confirm=True)

    def test_delete_entry_no_cidr_raises(self, mock_client):
        with pytest.raises(ValueError, match="cidr is required"):
            delete_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="", confirm=True)

    def test_delete_entry_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_cluster_firewall_ipset_entry(mock_client, name="blacklist", cidr="10.0.0.1/32")


class TestListClusterFirewallMacros:
    def test_list_macros(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"macro": "SSH", "description": "SSH (port 22)"},
        ])
        result = list_cluster_firewall_macros(mock_client)
        assert "SSH" in result

    def test_list_macros_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_cluster_firewall_macros(mock_client)
        assert "No macros found" in result


class TestGetNodeFirewallRule:
    def test_get_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = get_node_firewall_rule(mock_client, node="pve", pos=0)
        assert "pve" in result
        assert "ACCEPT" in result

    def test_get_rule_string_response(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="raw data")
        result = get_node_firewall_rule(mock_client, node="pve", pos=0)
        assert "raw data" in result


class TestUpdateNodeFirewallRule:
    def test_update_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_node_firewall_rule(mock_client, node="pve", pos=0, action="DROP", confirm=True)
        assert "pve" in result
        assert "updated" in result

    def test_update_rule_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_node_firewall_rule(mock_client, node="pve", pos=0, confirm=True)

    def test_update_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_node_firewall_rule(mock_client, node="pve", pos=0, action="DROP")


class TestSetNodeFirewallOptions:
    def test_set_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = set_node_firewall_options(mock_client, node="pve", enable=1, confirm=True)
        assert "pve" in result
        assert "updated" in result

    def test_set_options_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            set_node_firewall_options(mock_client, node="pve", confirm=True)

    def test_set_options_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            set_node_firewall_options(mock_client, node="pve", enable=1)


class TestListNodeFirewallIPSets:
    def test_list_ipsets(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "blacklist", "comment": "Blocked IPs"},
        ])
        result = list_node_firewall_ipsets(mock_client, node="pve")
        assert "blacklist" in result
        assert "pve" in result

    def test_list_ipsets_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_firewall_ipsets(mock_client, node="pve")
        assert "No IPSets found" in result
