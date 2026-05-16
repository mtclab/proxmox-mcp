from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.capabilities import list_cpu_flags, list_cpu_models, list_machine_types
from proxmox_mcp.config import Config


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


class TestListCpuModels:
    async def test_list_cpu_models_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "qemu64", "type": "custom"},
                {"name": "host", "type": "default"},
            ]
        )
        result = await list_cpu_models(mock_client, node="pve")
        assert "qemu64" in result
        assert "host" in result
        assert "CPU Models" in result

    async def test_list_cpu_models_minimal(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "kvm64"},
            ]
        )
        result = await list_cpu_models(mock_client, node="pve")
        assert "kvm64" in result

    async def test_list_cpu_models_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cpu_models(mock_client, node="pve")
        assert "No CPU models" in result

    async def test_list_cpu_models_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_cpu_models(mock_client, node="bad node!")


class TestListCpuFlags:
    async def test_list_cpu_flags_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "aes", "type": "bool"},
                {"name": "avx", "type": "bool"},
            ]
        )
        result = await list_cpu_flags(mock_client, node="pve")
        assert "aes" in result
        assert "avx" in result
        assert "CPU Flags" in result

    async def test_list_cpu_flags_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_cpu_flags(mock_client, node="pve")
        assert "No CPU flags" in result

    async def test_list_cpu_flags_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_cpu_flags(mock_client, node="bad!")


class TestListMachineTypes:
    async def test_list_machine_types_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                "pc-i440fx-9.0",
                "pc-q35-9.0",
            ]
        )
        result = await list_machine_types(mock_client, node="pve")
        assert "pc-i440fx-9.0" in result
        assert "pc-q35-9.0" in result
        assert "Machine Types" in result

    async def test_list_machine_types_dict_format(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "pc", "type": "i440fx"},
                {"name": "q35", "type": "q35"},
            ]
        )
        result = await list_machine_types(mock_client, node="pve")
        assert "pc" in result
        assert "q35" in result

    async def test_list_machine_types_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_machine_types(mock_client, node="pve")
        assert "No machine types" in result

    async def test_list_machine_types_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_machine_types(mock_client, node="bad node")
