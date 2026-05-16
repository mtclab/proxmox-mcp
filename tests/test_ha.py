from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.ha import (
    create_ha_resource,
    delete_ha_resource,
    get_ha_resource,
    ha_status,
    list_ha_groups,
    list_ha_resources,
    migrate_ha_resource,
    relocate_ha_resource,
    update_ha_resource,
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


class TestListHAResources:
    def test_list_ha_resources_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"sid": "vm:100", "type": "vm", "state": "started", "group": "group1"},
            {"sid": "ct:200", "type": "ct", "state": "stopped", "group": ""},
        ])
        result = list_ha_resources(mock_client)
        assert "vm:100" in result
        assert "ct:200" in result
        assert "HA Resources" in result

    def test_list_ha_resources_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ha_resources(mock_client)
        assert "No HA resources" in result


class TestCreateHAResource:
    def test_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_ha_resource(mock_client, sid="vm:100")

    def test_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_ha_resource(client, sid="vm:100", confirm=True)

    def test_create_no_sid_raises(self, mock_client):
        with pytest.raises(ValueError, match="sid is required"):
            create_ha_resource(mock_client, sid="", confirm=True)

    def test_create_ha_resource(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_ha_resource(
            mock_client, sid="vm:100", group="group1",
            state="started", type="vm", confirm=True,
        )
        assert "vm:100" in result
        assert "created" in result.lower()

    def test_create_with_optional_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_ha_resource(
            mock_client, sid="vm:100", comment="test HA",
            max_relocate=3, max_restart=2, confirm=True,
        )
        assert "vm:100" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test HA"
        assert call_args[1]["max_relocate"] == 3
        assert call_args[1]["max_restart"] == 2


class TestGetHAResource:
    def test_get_ha_resource(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "sid": "vm:100", "type": "vm", "state": "started",
        })
        result = get_ha_resource(mock_client, sid="vm:100")
        assert "vm:100" in result
        assert "started" in result

    def test_get_no_sid_raises(self, mock_client):
        with pytest.raises(ValueError, match="sid is required"):
            get_ha_resource(mock_client, sid="")


class TestUpdateHAResource:
    def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_ha_resource(mock_client, sid="vm:100", state="stopped")

    def test_update_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_ha_resource(client, sid="vm:100", confirm=True, state="stopped")

    def test_update_no_sid_raises(self, mock_client):
        with pytest.raises(ValueError, match="sid is required"):
            update_ha_resource(mock_client, sid="", confirm=True, state="stopped")

    def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_ha_resource(mock_client, sid="vm:100", confirm=True)

    def test_update_ha_resource(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_ha_resource(
            mock_client, sid="vm:100", state="stopped", group="group2", confirm=True,
        )
        assert "vm:100" in result
        assert "updated" in result.lower()


class TestDeleteHAResource:
    def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_ha_resource(mock_client, sid="vm:100")

    def test_delete_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_ha_resource(client, sid="vm:100", confirm=True)

    def test_delete_no_sid_raises(self, mock_client):
        with pytest.raises(ValueError, match="sid is required"):
            delete_ha_resource(mock_client, sid="", confirm=True)

    def test_delete_ha_resource(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_ha_resource(mock_client, sid="vm:100", confirm=True)
        assert "vm:100" in result
        assert "deleted" in result.lower()


class TestMigrateHAResource:
    def test_migrate_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            migrate_ha_resource(mock_client, sid="vm:100", node="pve2")

    def test_migrate_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            migrate_ha_resource(client, sid="vm:100", node="pve2", confirm=True)

    def test_migrate_no_sid_raises(self, mock_client):
        with pytest.raises(ValueError, match="sid is required"):
            migrate_ha_resource(mock_client, sid="", node="pve2", confirm=True)

    def test_migrate_no_node_raises(self, mock_client):
        with pytest.raises(ValueError, match="node is required"):
            migrate_ha_resource(mock_client, sid="vm:100", node="", confirm=True)

    def test_migrate_ha_resource(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = migrate_ha_resource(mock_client, sid="vm:100", node="pve2", confirm=True)
        assert "vm:100" in result
        assert "pve2" in result
        assert "migration" in result.lower()


class TestRelocateHAResource:
    def test_relocate_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            relocate_ha_resource(mock_client, sid="vm:100", node="pve2")

    def test_relocate_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            relocate_ha_resource(client, sid="vm:100", node="pve2", confirm=True)

    def test_relocate_no_sid_raises(self, mock_client):
        with pytest.raises(ValueError, match="sid is required"):
            relocate_ha_resource(mock_client, sid="", node="pve2", confirm=True)

    def test_relocate_no_node_raises(self, mock_client):
        with pytest.raises(ValueError, match="node is required"):
            relocate_ha_resource(mock_client, sid="vm:100", node="", confirm=True)

    def test_relocate_ha_resource(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = relocate_ha_resource(mock_client, sid="vm:100", node="pve2", confirm=True)
        assert "vm:100" in result
        assert "pve2" in result
        assert "relocation" in result.lower()


class TestListHAGroups:
    def test_list_ha_groups_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"group": "group1", "nodes": "pve pve2", "comment": "test group"},
        ])
        result = list_ha_groups(mock_client)
        assert "group1" in result
        assert "HA Groups" in result

    def test_list_ha_groups_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ha_groups(mock_client)
        assert "No HA groups" in result


class TestHAStatus:
    def test_ha_status_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"type": "service", "id": "pve", "status": "running"},
            {"type": "lrm", "sid": "vm:100", "state": "started"},
        ])
        result = ha_status(mock_client)
        assert "HA Status" in result
        assert "pve" in result

    def test_ha_status_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = ha_status(mock_client)
        assert "No HA status" in result
