from unittest.mock import MagicMock, mock_open, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.storage import list_isos, upload_iso


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


class TestConfirmRequired:
    def test_upload_iso_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            upload_iso(mock_client, node="pve", storage="local", filepath="/tmp/debian.iso")


class TestElevatedCheck:
    def test_upload_iso_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            upload_iso(client, node="pve", storage="local", filepath="/tmp/debian.iso", confirm=True)


class TestListIsos:
    def test_list_isos_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"volid": "local:iso/debian-12.iso", "size": 4000000000, "content": "iso"},
            {"volid": "local:iso/ubuntu-24.04.iso", "size": 5000000000, "content": "iso"},
        ])
        result = list_isos(mock_client, node="pve", storage="local")
        assert "debian-12" in result
        assert "ubuntu-24.04" in result
        mock_client.safe_api_call.assert_called_once()

    def test_list_isos_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_isos(mock_client, node="pve")
        assert "No ISOs found" in result

    def test_list_isos_passes_content_filter(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        list_isos(mock_client, node="pve", storage="local-lvm")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["content"] == "iso"


class TestUploadIso:
    def test_upload_iso_with_filepath(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0400:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_iso(
                mock_client, node="pve", storage="local",
                filepath="/tmp/debian-12.iso", confirm=True,
            )
        assert "UPID" in result
        assert "upload" in result.lower()
        mock_client.upload.assert_called_once()
        call_kwargs = mock_client.upload.call_args[1]
        assert call_kwargs["content_type"] == "iso"
        assert call_kwargs["node"] == "pve"
        assert call_kwargs["storage"] == "local"
        assert call_kwargs["filename"] == "debian-12.iso"

    def test_upload_iso_no_filepath_raises(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            upload_iso(mock_client, node="pve", storage="local", confirm=True)

    def test_upload_iso_resolves_node(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0401:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_iso(
                mock_client, storage="local",
                filepath="/tmp/debian.iso", confirm=True,
            )
        assert "pve" in result
