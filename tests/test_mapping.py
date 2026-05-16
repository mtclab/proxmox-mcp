from unittest.mock import MagicMock, patch

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
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "gpu1", "type": "pci", "description": "GPU card"},
        ])
        result = list_pci_mappings(mock_client)
        assert "PCI Mappings" in result
        assert "gpu1" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_pci_mappings(mock_client)
        assert "No PCI mappings found" in result


class TestCreatePciMapping:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_pci_mapping(mock_client, id="gpu1")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_pci_mapping(client, id="gpu1", confirm=True)

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            create_pci_mapping(mock_client, id="", confirm=True)

    def test_create(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_pci_mapping(mock_client, id="gpu1", description="GPU card", confirm=True)
        assert "gpu1" in result
        assert "created" in result.lower()


class TestGetPciMapping:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"id": "gpu1", "type": "pci"})
        result = get_pci_mapping(mock_client, id="gpu1")
        assert "gpu1" in result

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            get_pci_mapping(mock_client, id="")


class TestUpdatePciMapping:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_pci_mapping(mock_client, id="gpu1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            update_pci_mapping(mock_client, id="", confirm=True)

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_pci_mapping(mock_client, id="gpu1", confirm=True)

    def test_update(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_pci_mapping(mock_client, id="gpu1", description="updated", confirm=True)
        assert "gpu1" in result
        assert "updated" in result.lower()


class TestDeletePciMapping:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_pci_mapping(mock_client, id="gpu1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_pci_mapping(mock_client, id="", confirm=True)

    def test_delete(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_pci_mapping(mock_client, id="gpu1", confirm=True)
        assert "gpu1" in result
        assert "deleted" in result.lower()


class TestListUsbMappings:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "usb1", "type": "usb", "description": "USB dongle"},
        ])
        result = list_usb_mappings(mock_client)
        assert "USB Mappings" in result
        assert "usb1" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_usb_mappings(mock_client)
        assert "No USB mappings found" in result


class TestCreateUsbMapping:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_usb_mapping(mock_client, id="usb1")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_usb_mapping(client, id="usb1", confirm=True)

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            create_usb_mapping(mock_client, id="", confirm=True)

    def test_create(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_usb_mapping(mock_client, id="usb1", description="USB dongle", confirm=True)
        assert "usb1" in result
        assert "created" in result.lower()


class TestGetUsbMapping:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"id": "usb1", "type": "usb"})
        result = get_usb_mapping(mock_client, id="usb1")
        assert "usb1" in result

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            get_usb_mapping(mock_client, id="")


class TestUpdateUsbMapping:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_usb_mapping(mock_client, id="usb1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            update_usb_mapping(mock_client, id="", confirm=True)

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_usb_mapping(mock_client, id="usb1", confirm=True)

    def test_update(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_usb_mapping(mock_client, id="usb1", description="updated", confirm=True)
        assert "usb1" in result
        assert "updated" in result.lower()


class TestDeleteUsbMapping:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_usb_mapping(mock_client, id="usb1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_usb_mapping(mock_client, id="", confirm=True)

    def test_delete(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_usb_mapping(mock_client, id="usb1", confirm=True)
        assert "usb1" in result
        assert "deleted" in result.lower()


class TestMappingIndex:
    def test_dict_format(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "pci": [{"id": "gpu1"}],
            "usb": [{"id": "usb1"}],
            "dir": [{"id": "dir1"}],
        })
        result = mapping_index(mock_client)
        assert "Mapping Index" in result
        assert "gpu1" in result
        assert "PCI" in result
        assert "usb1" in result
        assert "USB" in result
        assert "dir1" in result
        assert "Directory" in result

    def test_list_format(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "gpu1", "type": "pci"},
        ])
        result = mapping_index(mock_client)
        assert "gpu1" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = mapping_index(mock_client)
        assert "No mappings found" in result
