from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.hardware import get_pci_device, list_pci, list_pci_mdev, list_usb


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
    client.monitor_client = MagicMock()
    return client


class TestListPci:
    async def test_list_pci_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {
                    "id": "0000:00:02.0",
                    "device_name": "VGA compatible controller",
                    "vendor_name": "Intel Corporation",
                    "subsystem_name": "HD Graphics 630",
                    "iommu_group": "1",
                },
            ]
        )
        result = await list_pci(mock_client, node="pve")
        assert "0000:00:02.0" in result
        assert "Intel" in result
        assert "PCI" in result

    async def test_list_pci_minimal(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "0000:01:00.0"},
            ]
        )
        result = await list_pci(mock_client, node="pve")
        assert "0000:01:00.0" in result

    async def test_list_pci_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_pci(mock_client, node="pve")
        assert "No PCI" in result

    async def test_list_pci_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_pci(mock_client, node="bad!node")


class TestListUsb:
    async def test_list_usb_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {
                    "id": "usb-1d6b-0001",
                    "product": "USB Keyboard",
                    "vendor": "Logitech",
                    "busnum": "1",
                    "devnum": "2",
                    "port": "1",
                },
            ]
        )
        result = await list_usb(mock_client, node="pve")
        assert "usb-1d6b-0001" in result
        assert "Logitech" in result
        assert "USB" in result

    async def test_list_usb_minimal(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "usb-1d6b-0002"},
            ]
        )
        result = await list_usb(mock_client, node="pve")
        assert "usb-1d6b-0002" in result

    async def test_list_usb_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_usb(mock_client, node="pve")
        assert "No USB" in result

    async def test_list_usb_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_usb(mock_client, node="bad!node")


class TestGetPciDevice:
    async def test_get_pci_device_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "device_name": "VGA compatible controller",
                "vendor_name": "Intel Corporation",
            }
        )
        result = await get_pci_device(mock_client, node="pve", pciid="0000:00:02.0")
        assert "0000:00:02.0" in result
        assert "pve" in result

    async def test_get_pci_device_no_pciid_raises(self, mock_client):
        with pytest.raises(ValueError, match="pciid is required"):
            await get_pci_device(mock_client, node="pve", pciid="")

    async def test_get_pci_device_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await get_pci_device(mock_client, node="bad!node", pciid="0000:00:02.0")


class TestListPciMdev:
    async def test_list_pci_mdev_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "nvidia-42", "description": "NVIDIA GPU", "available": "16"},
            ]
        )
        result = await list_pci_mdev(mock_client, node="pve", pciid="0000:01:00.0")
        assert "nvidia-42" in result
        assert "pve" in result

    async def test_list_pci_mdev_no_pciid_raises(self, mock_client):
        with pytest.raises(ValueError, match="pciid is required"):
            await list_pci_mdev(mock_client, node="pve", pciid="")

    async def test_list_pci_mdev_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_pci_mdev(mock_client, node="pve", pciid="0000:01:00.0")
        assert "No mediated device types found" in result
