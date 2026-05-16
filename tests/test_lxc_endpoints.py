from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.firewall import (
    add_vm_firewall_ipset_entry,
    create_vm_firewall_ipset,
    delete_vm_firewall_ipset,
    delete_vm_firewall_ipset_entry,
    get_vm_firewall_ipset_entry,
    get_vm_firewall_rule,
    list_vm_firewall_aliases,
    list_vm_firewall_ipset_content,
    list_vm_firewall_ipsets,
    set_vm_firewall_options,
    update_vm_firewall_alias,
    update_vm_firewall_ipset_entry,
    update_vm_firewall_rule,
    vm_firewall_log,
    vm_firewall_refs,
)
from proxmox_mcp.lifecycle import (
    get_lxc_config,
    get_lxc_status,
    lxc_rrddata,
    move_lxc_volume,
    remote_migrate_lxc,
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


class TestGetLxcConfig:
    async def test_get_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"cores": 2, "memory": 4096})
        result = await get_lxc_config(mock_client, node="pve", vmid=200)
        assert "200" in result
        assert "config" in result.lower()

    async def test_get_config_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await get_lxc_config(mock_client, node="pve", vmid=200)
        assert "200" in result


class TestGetLxcStatus:
    async def test_get_status(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"status": "running", "vmid": 200})
        result = await get_lxc_status(mock_client, node="pve", vmid=200)
        assert "200" in result
        assert "status" in result.lower()


class TestLxcRrddata:
    async def test_rrddata(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"time": 1, "cpu": 0.5}])
        result = await lxc_rrddata(mock_client, node="pve", vmid=200)
        assert "200" in result
        assert "RRDdata" in result

    async def test_rrddata_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await lxc_rrddata(mock_client, node="pve", vmid=200)
        assert "No data" in result


class TestRemoteMigrateLxc:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await remote_migrate_lxc(
                mock_client,
                node="pve",
                vmid=200,
                target="node2",
                target_endpoint="ep1",
            )

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await remote_migrate_lxc(
                client,
                node="pve",
                vmid=200,
                target="node2",
                target_endpoint="ep1",
                confirm=True,
            )

    async def test_requires_target(self, mock_client):
        with pytest.raises(ValueError, match="target is required"):
            await remote_migrate_lxc(
                mock_client,
                node="pve",
                vmid=200,
                target=None,
                target_endpoint="ep1",
                confirm=True,
            )

    async def test_requires_target_endpoint(self, mock_client):
        with pytest.raises(ValueError, match="target_endpoint is required"):
            await remote_migrate_lxc(
                mock_client,
                node="pve",
                vmid=200,
                target="node2",
                target_endpoint=None,
                confirm=True,
            )

    async def test_remote_migrate(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:100:abc")
        result = await remote_migrate_lxc(
            mock_client,
            node="pve",
            vmid=200,
            target="node2",
            target_endpoint="ep1",
            confirm=True,
        )
        assert "200" in result
        assert "remote migration" in result.lower()
        assert "UPID" in result


class TestMoveLxcVolume:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await move_lxc_volume(
                mock_client,
                node="pve",
                vmid=200,
                volume="rootfs",
            )

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await move_lxc_volume(
                client,
                node="pve",
                vmid=200,
                volume="rootfs",
                confirm=True,
            )

    async def test_move_volume(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:100:abc")
        result = await move_lxc_volume(
            mock_client,
            node="pve",
            vmid=200,
            volume="rootfs",
            storage="local-zfs",
            confirm=True,
        )
        assert "200" in result
        assert "move" in result.lower()
        assert "UPID" in result


class TestVmFirewallRuleOperations:
    async def test_get_rule_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = await get_vm_firewall_rule(
            mock_client,
            node="pve",
            vmid=200,
            pos=0,
            vmtype="lxc",
        )
        assert "200" in result
        assert "0" in result

    async def test_update_rule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_vm_firewall_rule(
                mock_client,
                node="pve",
                vmid=200,
                pos=0,
                action="DROP",
            )

    async def test_update_rule_no_params(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_vm_firewall_rule(
                mock_client,
                node="pve",
                vmid=200,
                pos=0,
                vmtype="lxc",
                confirm=True,
            )

    async def test_update_rule_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await update_vm_firewall_rule(
                mock_client,
                node="pve",
                vmid=200,
                pos=0,
                vmtype="invalid",
                action="DROP",
                confirm=True,
            )

    async def test_set_options_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await set_vm_firewall_options(
                mock_client,
                node="pve",
                vmid=200,
                vmtype="lxc",
                enable=1,
            )

    async def test_set_options_no_params(self, mock_client):
        with pytest.raises(ValueError, match="At least one option"):
            await set_vm_firewall_options(
                mock_client,
                node="pve",
                vmid=200,
                vmtype="lxc",
                confirm=True,
            )

    async def test_set_options_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await set_vm_firewall_options(
            mock_client,
            node="pve",
            vmid=200,
            vmtype="lxc",
            confirm=True,
            enable=1,
        )
        assert "lxc" in result
        assert "200" in result


class TestVmFirewallAliases:
    async def test_list_aliases_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"name": "test", "cidr": "10.0.0.0/8"}])
        result = await list_vm_firewall_aliases(
            mock_client,
            node="pve",
            vmid=200,
            vmtype="lxc",
        )
        assert "200" in result
        assert "test" in result

    async def test_update_alias_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_vm_firewall_alias(
                mock_client,
                node="pve",
                vmid=200,
                name="test",
                vmtype="lxc",
            )

    async def test_update_alias_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await update_vm_firewall_alias(
                mock_client,
                node="pve",
                vmid=200,
                name="",
                vmtype="lxc",
                confirm=True,
            )

    async def test_update_alias_no_params(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_vm_firewall_alias(
                mock_client,
                node="pve",
                vmid=200,
                name="test",
                vmtype="lxc",
                confirm=True,
            )


class TestVmFirewallLog:
    async def test_firewall_log_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {
                    "proto": "tcp",
                    "action": "ACCEPT",
                    "src": "10.0.0.1",
                    "dst": "10.0.0.2",
                    "dport": "80",
                }
            ]
        )
        result = await vm_firewall_log(
            mock_client,
            node="pve",
            vmid=200,
            vmtype="lxc",
        )
        assert "Log" in result
        assert "200" in result


class TestVmFirewallRefs:
    async def test_firewall_refs_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"ref": "test", "type": "alias"}])
        result = await vm_firewall_refs(
            mock_client,
            node="pve",
            vmid=200,
            vmtype="lxc",
        )
        assert "References" in result
        assert "test" in result


class TestVmFirewallIpsets:
    async def test_list_ipsets_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"name": "testset", "comment": "test"}])
        result = await list_vm_firewall_ipsets(
            mock_client,
            node="pve",
            vmid=200,
            vmtype="lxc",
        )
        assert "200" in result
        assert "testset" in result

    async def test_list_ipset_content_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"cidr": "10.0.0.1/32"}])
        result = await list_vm_firewall_ipset_content(
            mock_client,
            node="pve",
            vmid=200,
            name="testset",
            vmtype="lxc",
        )
        assert "10.0.0.1" in result

    async def test_create_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_vm_firewall_ipset(
                mock_client,
                node="pve",
                vmid=200,
                name="testset",
                vmtype="lxc",
            )

    async def test_create_ipset_name_required(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_vm_firewall_ipset(
                mock_client,
                node="pve",
                vmid=200,
                name="",
                vmtype="lxc",
                confirm=True,
            )

    async def test_delete_ipset_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_vm_firewall_ipset(
                mock_client,
                node="pve",
                vmid=200,
                name="testset",
                vmtype="lxc",
            )

    async def test_add_entry_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await add_vm_firewall_ipset_entry(
                mock_client,
                node="pve",
                vmid=200,
                name="testset",
                cidr="10.0.0.1/32",
                vmtype="lxc",
            )

    async def test_get_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"cidr": "10.0.0.1/32", "comment": "test"})
        result = await get_vm_firewall_ipset_entry(
            mock_client,
            node="pve",
            vmid=200,
            name="testset",
            cidr="10.0.0.1/32",
            vmtype="lxc",
        )
        assert "10.0.0.1" in result

    async def test_update_entry_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_vm_firewall_ipset_entry(
                mock_client,
                node="pve",
                vmid=200,
                name="testset",
                cidr="10.0.0.1/32",
                vmtype="lxc",
                comment="updated",
            )

    async def test_update_entry_no_params(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_vm_firewall_ipset_entry(
                mock_client,
                node="pve",
                vmid=200,
                name="testset",
                cidr="10.0.0.1/32",
                vmtype="lxc",
                confirm=True,
            )

    async def test_delete_entry_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_vm_firewall_ipset_entry(
                mock_client,
                node="pve",
                vmid=200,
                name="testset",
                cidr="10.0.0.1/32",
                vmtype="lxc",
            )

    async def test_invalid_vmtype(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await list_vm_firewall_ipsets(
                mock_client,
                node="pve",
                vmid=200,
                vmtype="invalid",
            )
