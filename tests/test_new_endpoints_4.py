from unittest.mock import MagicMock, patch

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
    def test_list_ha_rules(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "rule1", "type": "group"},
            {"id": "rule2", "type": "group"},
        ])
        result = list_ha_rules(mock_client)
        assert "HA Rules" in result
        assert "rule1" in result

    def test_list_ha_rules_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ha_rules(mock_client)
        assert "No HA rules" in result


class TestCreateHARule:
    def test_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_ha_rule(mock_client, group="group1")

    def test_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_ha_rule(client, group="group1", confirm=True)

    def test_create_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            create_ha_rule(mock_client, group="", confirm=True)

    def test_create_ha_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_ha_rule(mock_client, group="group1", comment="test rule", confirm=True)
        assert "group1" in result


class TestGetHARule:
    def test_get_ha_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"id": "rule1", "type": "group"})
        result = get_ha_rule(mock_client, rule="rule1")
        assert "rule1" in result

    def test_get_no_rule_raises(self, mock_client):
        with pytest.raises(ValueError, match="rule is required"):
            get_ha_rule(mock_client, rule="")


class TestUpdateHARule:
    def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_ha_rule(mock_client, rule="rule1", comment="updated")

    def test_update_no_rule_raises(self, mock_client):
        with pytest.raises(ValueError, match="rule is required"):
            update_ha_rule(mock_client, rule="", confirm=True, comment="x")

    def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_ha_rule(mock_client, rule="rule1", confirm=True)

    def test_update_ha_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_ha_rule(mock_client, rule="rule1", comment="updated", confirm=True)
        assert "rule1" in result
        assert "updated" in result.lower()


class TestDeleteHARule:
    def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_ha_rule(mock_client, rule="rule1")

    def test_delete_no_rule_raises(self, mock_client):
        with pytest.raises(ValueError, match="rule is required"):
            delete_ha_rule(mock_client, rule="", confirm=True)

    def test_delete_ha_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_ha_rule(mock_client, rule="rule1", confirm=True)
        assert "rule1" in result
        assert "deleted" in result.lower()


class TestGetHAGroup:
    def test_get_ha_group(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"group": "grp1", "nodes": "pve"})
        result = get_ha_group(mock_client, group="grp1")
        assert "grp1" in result

    def test_get_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            get_ha_group(mock_client, group="")


class TestUpdateHAGroup:
    def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_ha_group(mock_client, group="grp1", nodes="pve pve2")

    def test_update_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            update_ha_group(mock_client, group="", confirm=True, nodes="pve")

    def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_ha_group(mock_client, group="grp1", confirm=True)

    def test_update_ha_group(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_ha_group(mock_client, group="grp1", nodes="pve pve2", confirm=True)
        assert "grp1" in result


class TestDeleteHAGroup:
    def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_ha_group(mock_client, group="grp1")

    def test_delete_no_group_raises(self, mock_client):
        with pytest.raises(ValueError, match="group is required"):
            delete_ha_group(mock_client, group="", confirm=True)

    def test_delete_ha_group(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_ha_group(mock_client, group="grp1", confirm=True)
        assert "grp1" in result
        assert "deleted" in result.lower()


class TestArmHA:
    def test_arm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            arm_ha(mock_client)

    def test_arm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            arm_ha(client, confirm=True)

    def test_arm_ha(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = arm_ha(mock_client, confirm=True)
        assert "armed" in result.lower()


class TestDisarmHA:
    def test_disarm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            disarm_ha(mock_client)

    def test_disarm_ha(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = disarm_ha(mock_client, confirm=True)
        assert "disarmed" in result.lower()


class TestHAManagerStatus:
    def test_ha_manager_status(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"master": "pve", "status": "running"})
        result = ha_manager_status(mock_client)
        assert "HA Manager Status" in result
        assert "master" in result


class TestCreateTicket:
    def test_create_ticket(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"ticket": "PVE:user@pam:abc123", "CSRFPreventionToken": "def456"},
        })
        result = create_ticket(mock_client, username="user@pam", password="pass123")
        assert "Authentication Ticket" in result

    def test_create_ticket_no_username(self, mock_client):
        with pytest.raises(ValueError, match="username is required"):
            create_ticket(mock_client, username="", password="pass")

    def test_create_ticket_no_password(self, mock_client):
        with pytest.raises(ValueError, match="password is required"):
            create_ticket(mock_client, username="user@pam", password="")


class TestCreateVNCTicket:
    def test_create_vnc_ticket(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"ticket": "vnc-ticket"}})
        result = create_vnc_ticket(mock_client, port=5900)
        assert "VNC Ticket" in result

    def test_create_vnc_ticket_no_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"ticket": "vnc-ticket"})
        result = create_vnc_ticket(mock_client)
        assert "VNC Ticket" in result


class TestLXCSendkey:
    def test_sendkey_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            lxc_sendkey(mock_client, node="pve", vmid=100, key="ctrl+c")

    def test_sendkey_no_key_raises(self, mock_client):
        with pytest.raises(ValueError, match="key is required"):
            lxc_sendkey(mock_client, node="pve", vmid=100, key="", confirm=True)

    def test_lxc_sendkey(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = lxc_sendkey(mock_client, node="pve", vmid=100, key="ctrl+c", confirm=True)
        assert "ctrl+c" in result
        assert "100" in result


class TestCheckSubscription:
    def test_check_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            check_subscription(mock_client, node="pve")

    def test_check_subscription(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = check_subscription(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "check" in result.lower()


class TestReloadService:
    def test_reload_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            reload_service(mock_client, node="pve", service="nginx")

    def test_reload_no_service_raises(self, mock_client):
        with pytest.raises(ValueError, match="service is required"):
            reload_service(mock_client, node="pve", service="", confirm=True)

    def test_reload_service(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = reload_service(mock_client, node="pve", service="nginx", confirm=True)
        assert "nginx" in result
        assert "reload" in result.lower()


class TestGetDirectoryDetail:
    def test_get_directory_detail(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"name": "local", "path": "/var/lib/vz"})
        result = get_directory_detail(mock_client, node="pve", name="local")
        assert "local" in result
        assert "pve" in result

    def test_get_directory_detail_no_name(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            get_directory_detail(mock_client, node="pve", name="")


class TestGetLVMThinDetail:
    def test_get_lvmthin_detail(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"lvname": "thinpool", "vg": "pve"})
        result = get_lvmthin_detail(mock_client, node="pve", name="thinpool")
        assert "thinpool" in result
        assert "pve" in result

    def test_get_lvmthin_detail_no_name(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            get_lvmthin_detail(mock_client, node="pve", name="")


class TestGetNextVMID:
    def test_get_next_vmid(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=101)
        result = get_next_vmid(mock_client)
        assert "101" in result

    def test_get_next_vmid_zero(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=0)
        result = get_next_vmid(mock_client)
        assert "0" in result


class TestGenerateClusterConfig:
    def test_generate_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            generate_cluster_config(mock_client, node="pve")

    def test_generate_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            generate_cluster_config(client, node="pve", confirm=True)

    def test_generate_cluster_config(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = generate_cluster_config(mock_client, confirm=True)
        assert "Cluster config" in result


class TestRemoveClusterNode:
    def test_remove_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            remove_cluster_node(mock_client, node="pve2")

    def test_remove_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            remove_cluster_node(client, node="pve2", confirm=True)

    def test_remove_no_node_raises(self, mock_client):
        with pytest.raises(ValueError, match="node is required"):
            remove_cluster_node(mock_client, node="", confirm=True)

    def test_remove_cluster_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = remove_cluster_node(mock_client, node="pve2", confirm=True)
        assert "pve2" in result
        assert "removed" in result.lower()
