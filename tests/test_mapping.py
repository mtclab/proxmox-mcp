from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.mapping import (
    create_pci_mapping,
    create_usb_mapping,
    delete_pci_mapping,
    delete_usb_mapping,
    get_pci_mapping,
    get_usb_mapping,
    list_pci_mappings,
    list_usb_mappings,
    mapping_index,
    update_pci_mapping,
    update_usb_mapping,
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


class TestListPciMappings:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "gpu1", "type": "pci", "description": "GPU card"},
            ]
        )
        result = await list_pci_mappings(mock_client)
        assert "PCI Mappings" in result
        assert "gpu1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_pci_mappings(mock_client)
        assert "No PCI mappings found" in result


class TestCreatePciMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_pci_mapping(mock_client, id="gpu1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_pci_mapping(client, id="gpu1", confirm=True)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await create_pci_mapping(mock_client, id="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_pci_mapping(mock_client, id="gpu1", description="GPU card", confirm=True)
        assert "gpu1" in result
        assert "created" in result.lower()


class TestGetPciMapping:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"id": "gpu1", "type": "pci"})
        result = await get_pci_mapping(mock_client, id="gpu1")
        assert "gpu1" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_pci_mapping(mock_client, id="")


class TestUpdatePciMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_pci_mapping(mock_client, id="gpu1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await update_pci_mapping(mock_client, id="", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_pci_mapping(mock_client, id="gpu1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_pci_mapping(mock_client, id="gpu1", description="updated", confirm=True)
        assert "gpu1" in result
        assert "updated" in result.lower()


class TestDeletePciMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_pci_mapping(mock_client, id="gpu1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_pci_mapping(mock_client, id="", confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_pci_mapping(mock_client, id="gpu1", confirm=True)
        assert "gpu1" in result
        assert "deleted" in result.lower()


class TestListUsbMappings:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "usb1", "type": "usb", "description": "USB dongle"},
            ]
        )
        result = await list_usb_mappings(mock_client)
        assert "USB Mappings" in result
        assert "usb1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_usb_mappings(mock_client)
        assert "No USB mappings found" in result


class TestCreateUsbMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_usb_mapping(mock_client, id="usb1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_usb_mapping(client, id="usb1", confirm=True)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await create_usb_mapping(mock_client, id="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_usb_mapping(mock_client, id="usb1", description="USB dongle", confirm=True)
        assert "usb1" in result
        assert "created" in result.lower()


class TestGetUsbMapping:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"id": "usb1", "type": "usb"})
        result = await get_usb_mapping(mock_client, id="usb1")
        assert "usb1" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_usb_mapping(mock_client, id="")


class TestUpdateUsbMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_usb_mapping(mock_client, id="usb1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await update_usb_mapping(mock_client, id="", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_usb_mapping(mock_client, id="usb1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_usb_mapping(mock_client, id="usb1", description="updated", confirm=True)
        assert "usb1" in result
        assert "updated" in result.lower()


class TestDeleteUsbMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_usb_mapping(mock_client, id="usb1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_usb_mapping(mock_client, id="", confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_usb_mapping(mock_client, id="usb1", confirm=True)
        assert "usb1" in result
        assert "deleted" in result.lower()


class TestMappingIndex:
    async def test_dict_format(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "pci": [{"id": "gpu1"}],
                "usb": [{"id": "usb1"}],
                "dir": [{"id": "dir1"}],
            }
        )
        result = await mapping_index(mock_client)
        assert "Mapping Index" in result
        assert "gpu1" in result
        assert "PCI" in result
        assert "usb1" in result
        assert "USB" in result
        assert "dir1" in result
        assert "Directory" in result

    async def test_list_format(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "gpu1", "type": "pci"},
            ]
        )
        result = await mapping_index(mock_client)
        assert "gpu1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await mapping_index(mock_client)
        assert "No mappings found" in result
