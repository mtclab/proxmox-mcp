from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.replication import (
    create_replication,
    delete_replication,
    get_replication,
    get_replication_log,
    get_replication_status,
    list_node_replication,
    list_replication,
    schedule_replication,
    update_replication,
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


class TestListReplication:
    def test_list_replication_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "100-local", "source": "pve", "target": "pve2", "schedule": "*/15", "state": "ok"},
        ])
        result = list_replication(mock_client)
        assert "100-local" in result
        assert "Replication Jobs" in result

    def test_list_replication_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_replication(mock_client)
        assert "No replication jobs" in result


class TestCreateReplication:
    def test_create_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_replication(mock_client, id="100-local")

    def test_create_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_replication(client, id="100-local", confirm=True)

    def test_create_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            create_replication(mock_client, id="", confirm=True)

    def test_create_replication(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_replication(
            mock_client, id="100-local", source="pve",
            target="pve2", schedule="*/15", confirm=True,
        )
        assert "100-local" in result
        assert "created" in result.lower()

    def test_create_with_optional_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_replication(
            mock_client, id="100-local", comment="test",
            disable=True, rate=50.0, confirm=True,
        )
        assert "100-local" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test"
        assert call_args[1]["disable"] == 1
        assert call_args[1]["rate"] == 50.0


class TestGetReplication:
    def test_get_replication(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "id": "100-local", "source": "pve", "target": "pve2",
        })
        result = get_replication(mock_client, id="100-local")
        assert "100-local" in result
        assert "pve" in result

    def test_get_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            get_replication(mock_client, id="")


class TestUpdateReplication:
    def test_update_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_replication(mock_client, id="100-local", schedule="*/30")

    def test_update_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_replication(client, id="100-local", confirm=True, schedule="*/30")

    def test_update_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            update_replication(mock_client, id="", confirm=True, schedule="*/30")

    def test_update_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_replication(mock_client, id="100-local", confirm=True)

    def test_update_replication(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_replication(
            mock_client, id="100-local", schedule="*/30", comment="updated", confirm=True,
        )
        assert "100-local" in result
        assert "updated" in result.lower()


class TestDeleteReplication:
    def test_delete_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_replication(mock_client, id="100-local")

    def test_delete_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_replication(client, id="100-local", confirm=True)

    def test_delete_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_replication(mock_client, id="", confirm=True)

    def test_delete_replication(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_replication(mock_client, id="100-local", confirm=True)
        assert "100-local" in result
        assert "deleted" in result.lower()


class TestListNodeReplication:
    def test_list_node_replication_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "100-local", "source": "pve", "target": "pve2", "state": "ok"},
        ])
        result = list_node_replication(mock_client, node="pve")
        assert "100-local" in result
        assert "pve" in result

    def test_list_node_replication_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_replication(mock_client, node="pve")
        assert "No replication jobs" in result

    def test_list_node_replication_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_node_replication(mock_client, node="bad!node")


class TestScheduleReplication:
    def test_schedule_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            schedule_replication(mock_client, id="100-local")

    def test_schedule_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            schedule_replication(client, id="100-local", confirm=True)

    def test_schedule_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            schedule_replication(mock_client, id="", confirm=True)

    def test_schedule_replication(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = schedule_replication(mock_client, id="100-local", node="pve", confirm=True)
        assert "100-local" in result
        assert "scheduled" in result.lower()

    def test_schedule_replication_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            schedule_replication(mock_client, id="100-local", node="bad!node", confirm=True)


class TestGetReplicationStatus:
    def test_get_replication_status(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"status": "ok", "guest": "100"},
        ])
        result = get_replication_status(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    def test_get_replication_status_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "status": "ok", "guest": "100",
        })
        result = get_replication_status(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    def test_get_replication_status_no_id(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            get_replication_status(mock_client, id="")

    def test_get_replication_status_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            get_replication_status(mock_client, node="bad!node", id="100-local")


class TestGetReplicationLog:
    def test_get_replication_log(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"n": 0, "t": "replication started"},
            {"n": 1, "t": "replication finished"},
        ])
        result = get_replication_log(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    def test_get_replication_log_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = get_replication_log(mock_client, node="pve", id="100-local")
        assert "100-local" in result

    def test_get_replication_log_no_id(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            get_replication_log(mock_client, id="")

    def test_get_replication_log_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            get_replication_log(mock_client, node="bad!node", id="100-local")
