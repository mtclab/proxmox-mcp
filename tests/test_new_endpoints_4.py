from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.access import create_ticket, create_vnc_ticket
from proxmox_mcp.cluster import generate_cluster_config, remove_cluster_node
from proxmox_mcp.config import Config
from proxmox_mcp.discovery import get_next_vmid
from proxmox_mcp.disks import get_directory_detail, get_lvmthin_detail
from proxmox_mcp.ha import (
    arm_ha,
    create_ha_rule,
    delete_ha_group,
    delete_ha_rule,
    disarm_ha,
    get_ha_group,
    get_ha_rule,
    ha_manager_status,
    list_ha_rules,
    update_ha_group,
    update_ha_rule,
)
from proxmox_mcp.lifecycle import lxc_sendkey
from proxmox_mcp.nodes import check_subscription, reload_service


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


class TestListHARules:
    async def test_list_ha_rules(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "rule1", "type": "group"},
                {"id": "rule2", "type": "group"},
            ]
        )
        result = await list_ha_rules(mock_client)
        assert "HA Rules" in result
        assert "rule1" in result

    async def test_list_ha_rules_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_ha_rules(mock_client)
        assert "No HA rules" in result


class TestCreateHARule:
    async def test_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_ha_rule(mock_client, group="group1")

    async def test_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_ha_rule(client, group="group1", confirm=True)

    async def test_create_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            await create_ha_rule(mock_client, group="", confirm=True)

    async def test_create_ha_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_ha_rule(mock_client, group="group1", comment="test rule", confirm=True)
        assert "group1" in result


class TestGetHARule:
    async def test_get_ha_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"id": "rule1", "type": "group"})
        result = await get_ha_rule(mock_client, rule="rule1")
        assert "rule1" in result

    async def test_get_no_rule_raises(self, mock_client):
        with pytest.raises(ValueError, match="rule is required"):
            await get_ha_rule(mock_client, rule="")


class TestUpdateHARule:
    async def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_ha_rule(mock_client, rule="rule1", comment="updated")

    async def test_update_no_rule_raises(self, mock_client):
        with pytest.raises(ValueError, match="rule is required"):
            await update_ha_rule(mock_client, rule="", confirm=True, comment="x")

    async def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_ha_rule(mock_client, rule="rule1", confirm=True)

    async def test_update_ha_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_ha_rule(mock_client, rule="rule1", comment="updated", confirm=True)
        assert "rule1" in result
        assert "updated" in result.lower()


class TestDeleteHARule:
    async def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_ha_rule(mock_client, rule="rule1")

    async def test_delete_no_rule_raises(self, mock_client):
        with pytest.raises(ValueError, match="rule is required"):
            await delete_ha_rule(mock_client, rule="", confirm=True)

    async def test_delete_ha_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_ha_rule(mock_client, rule="rule1", confirm=True)
        assert "rule1" in result
        assert "deleted" in result.lower()


class TestGetHAGroup:
    async def test_get_ha_group(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"group": "grp1", "nodes": "pve"})
        result = await get_ha_group(mock_client, group="grp1")
        assert "grp1" in result

    async def test_get_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            await get_ha_group(mock_client, group="")


class TestUpdateHAGroup:
    async def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_ha_group(mock_client, group="grp1", nodes="pve pve2")

    async def test_update_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            await update_ha_group(mock_client, group="", confirm=True, nodes="pve")

    async def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_ha_group(mock_client, group="grp1", confirm=True)

    async def test_update_ha_group(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_ha_group(mock_client, group="grp1", nodes="pve pve2", confirm=True)
        assert "grp1" in result


class TestDeleteHAGroup:
    async def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_ha_group(mock_client, group="grp1")

    async def test_delete_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            await delete_ha_group(mock_client, group="", confirm=True)

    async def test_delete_ha_group(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_ha_group(mock_client, group="grp1", confirm=True)
        assert "grp1" in result
        assert "deleted" in result.lower()


class TestArmHA:
    async def test_arm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await arm_ha(mock_client)

    async def test_arm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await arm_ha(client, confirm=True)

    async def test_arm_ha(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await arm_ha(mock_client, confirm=True)
        assert "armed" in result.lower()


class TestDisarmHA:
    async def test_disarm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await disarm_ha(mock_client)

    async def test_disarm_ha(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await disarm_ha(mock_client, confirm=True)
        assert "disarmed" in result.lower()


class TestHAManagerStatus:
    async def test_ha_manager_status(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"master": "pve", "status": "running"})
        result = await ha_manager_status(mock_client)
        assert "HA Manager Status" in result
        assert "master" in result


class TestCreateTicket:
    async def test_create_ticket(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"ticket": "PVE:user@pam:abc123", "CSRFPreventionToken": "def456"},
            }
        )
        result = await create_ticket(mock_client, username="user@pam", password="pass123")
        assert "Authentication Ticket" in result

    async def test_create_ticket_no_username(self, mock_client):
        with pytest.raises(ValueError, match="username is required"):
            await create_ticket(mock_client, username="", password="pass")

    async def test_create_ticket_no_password(self, mock_client):
        with pytest.raises(ValueError, match="password is required"):
            await create_ticket(mock_client, username="user@pam", password="")


class TestCreateVNCTicket:
    async def test_create_vnc_ticket(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"ticket": "vnc-ticket"}})
        result = await create_vnc_ticket(mock_client, port=5900)
        assert "VNC Ticket" in result

    async def test_create_vnc_ticket_no_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"ticket": "vnc-ticket"})
        result = await create_vnc_ticket(mock_client)
        assert "VNC Ticket" in result


class TestLXCSendkey:
    async def test_sendkey_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await lxc_sendkey(mock_client, node="pve", vmid=100, key="ctrl+c")

    async def test_sendkey_no_key_raises(self, mock_client):
        with pytest.raises(ValueError, match="key is required"):
            await lxc_sendkey(mock_client, node="pve", vmid=100, key="", confirm=True)

    async def test_lxc_sendkey(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await lxc_sendkey(mock_client, node="pve", vmid=100, key="ctrl+c", confirm=True)
        assert "ctrl+c" in result
        assert "100" in result


class TestCheckSubscription:
    async def test_check_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await check_subscription(mock_client, node="pve")

    async def test_check_subscription(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await check_subscription(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "check" in result.lower()


class TestReloadService:
    async def test_reload_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await reload_service(mock_client, node="pve", service="nginx")

    async def test_reload_no_service_raises(self, mock_client):
        with pytest.raises(ValueError, match="service is required"):
            await reload_service(mock_client, node="pve", service="", confirm=True)

    async def test_reload_service(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await reload_service(mock_client, node="pve", service="nginx", confirm=True)
        assert "nginx" in result
        assert "reload" in result.lower()


class TestGetDirectoryDetail:
    async def test_get_directory_detail(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "local", "path": "/var/lib/vz"})
        result = await get_directory_detail(mock_client, node="pve", name="local")
        assert "local" in result
        assert "pve" in result

    async def test_get_directory_detail_no_name(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await get_directory_detail(mock_client, node="pve", name="")


class TestGetLVMThinDetail:
    async def test_get_lvmthin_detail(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"lvname": "thinpool", "vg": "pve"})
        result = await get_lvmthin_detail(mock_client, node="pve", name="thinpool")
        assert "thinpool" in result
        assert "pve" in result

    async def test_get_lvmthin_detail_no_name(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await get_lvmthin_detail(mock_client, node="pve", name="")


class TestGetNextVMID:
    async def test_get_next_vmid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=101)
        result = await get_next_vmid(mock_client)
        assert "101" in result

    async def test_get_next_vmid_zero(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=0)
        result = await get_next_vmid(mock_client)
        assert "0" in result


class TestGenerateClusterConfig:
    async def test_generate_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await generate_cluster_config(mock_client, node="pve")

    async def test_generate_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await generate_cluster_config(client, node="pve", confirm=True)

    async def test_generate_cluster_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await generate_cluster_config(mock_client, confirm=True)
        assert "Cluster config" in result


class TestRemoveClusterNode:
    async def test_remove_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await remove_cluster_node(mock_client, node="pve2")

    async def test_remove_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await remove_cluster_node(client, node="pve2", confirm=True)

    async def test_remove_no_node_raises(self, mock_client):
        with pytest.raises(ValueError, match="node is required"):
            await remove_cluster_node(mock_client, node="", confirm=True)

    async def test_remove_cluster_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await remove_cluster_node(mock_client, node="pve2", confirm=True)
        assert "pve2" in result
        assert "removed" in result.lower()
