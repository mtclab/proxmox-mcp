from unittest.mock import MagicMock, mock_open, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.templates import (
    download_template,
    list_storage_templates,
    list_templates,
    upload_template,
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


class TestListTemplates:
    def test_list_templates_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {
                "name": "ubuntu-24.04-standard",
                "version": "24.04-2",
                "section": "system",
                "location": "http://repo/ubuntu-24.04.tar.xz",
                "size": 200000000,
            },
            {
                "name": "debian-12-standard",
                "version": "12.0-1",
                "section": "system",
                "location": "http://repo/debian-12.tar.xz",
                "size": 150000000,
            },
        ])
        result = list_templates(mock_client, node="pve")
        assert "ubuntu-24.04-standard" in result
        assert "24.04-2" in result
        assert "debian-12-standard" in result
        mock_client.safe_api_call.assert_called_once()

    def test_list_templates_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_templates(mock_client, node="pve")
        assert "No templates available" in result

    def test_list_templates_resolves_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        list_templates(mock_client)
        call_args = mock_client.safe_api_call.call_args
        assert call_args is not None


class TestListStorageTemplates:
    def test_list_storage_templates_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {
                "volid": "local:vztmpl/ubuntu-24.04.tar.xz",
                "size": 200000000,
                "content": "vztmpl",
            },
            {
                "volid": "local:vztmpl/debian-12.tar.xz",
                "size": 150000000,
                "content": "vztmpl",
            },
        ])
        result = list_storage_templates(
            mock_client, node="pve", storage="local"
        )
        assert "ubuntu-24.04" in result
        assert "debian-12" in result
        mock_client.safe_api_call.assert_called_once()

    def test_list_storage_templates_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_storage_templates(
            mock_client, node="pve", storage="local"
        )
        assert "No templates found" in result

    def test_list_storage_templates_passes_content_filter(
        self, mock_client
    ):
        mock_client.safe_api_call = MagicMock(return_value=[])
        list_storage_templates(
            mock_client, node="pve", storage="local-lvm"
        )
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["content"] == "vztmpl"


class TestConfirmRequired:
    def test_download_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            download_template(
                mock_client, node="pve", storage="local",
                url="http://example.com/template.tar.xz",
            )

    def test_upload_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            upload_template(
                mock_client, node="pve", storage="local",
                filepath="/tmp/template.tar.xz",
            )


class TestElevatedCheck:
    def test_download_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            download_template(
                client, node="pve", storage="local",
                url="http://example.com/template.tar.xz", confirm=True,
            )

    def test_upload_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            upload_template(
                client, node="pve", storage="local",
                filepath="/tmp/template.tar.xz", confirm=True,
            )


class TestDownloadTemplate:
    def test_download_template_with_url(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:0050:abc"
        )
        result = download_template(
            mock_client, node="pve", storage="local",
            url="http://repo/ubuntu-24.04-standard_24.04-2_amd64.tar.xz",
            confirm=True,
        )
        assert "UPID" in result
        assert "download" in result.lower()
        call_args = mock_client.safe_api_call.call_args
        url = "http://repo/ubuntu-24.04-standard_24.04-2_amd64.tar.xz"
        assert call_args[1]["url"] == url
        assert call_args[1]["content"] == "vztmpl"

    def test_download_template_with_filename(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:0051:abc"
        )
        result = download_template(
            mock_client, node="pve", storage="local",
            url="http://repo/template.tar.xz",
            filename="ubuntu-24.04-standard_24.04-2_amd64.tar.xz",
            confirm=True,
        )
        assert "UPID" in result
        call_args = mock_client.safe_api_call.call_args
        assert (
            call_args[1]["filename"]
            == "ubuntu-24.04-standard_24.04-2_amd64.tar.xz"
        )

    def test_download_template_no_url_raises(self, mock_client):
        with pytest.raises(ValueError, match="url is required"):
            download_template(
                mock_client, node="pve", storage="local", confirm=True
            )

    def test_download_template_resolves_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:0052:abc"
        )
        result = download_template(
            mock_client, storage="local",
            url="http://repo/template.tar.xz", confirm=True,
        )
        assert "pve" in result


class TestUploadTemplate:
    def test_upload_template_with_filepath(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0060:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_template(
                mock_client, node="pve", storage="local",
                filepath="/tmp/template.tar.xz", confirm=True,
            )
        assert "UPID" in result
        assert "upload" in result.lower()
        mock_client.upload.assert_called_once()
        call_kwargs = mock_client.upload.call_args[1]
        assert call_kwargs["content_type"] == "vztmpl"
        assert call_kwargs["node"] == "pve"
        assert call_kwargs["storage"] == "local"

    def test_upload_template_no_filepath_raises(self, mock_client):
        with pytest.raises(ValueError, match="filepath is required"):
            upload_template(
                mock_client, node="pve", storage="local", confirm=True
            )

    def test_upload_template_uses_correct_field(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0061:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            upload_template(
                mock_client, node="pve", storage="local",
                filepath="/tmp/ubuntu-24.04-standard_24.04-2_amd64.tar.xz",
                confirm=True,
            )
        call_kwargs = mock_client.upload.call_args[1]
        assert (
            call_kwargs["filename"]
            == "ubuntu-24.04-standard_24.04-2_amd64.tar.xz"
        )

    def test_upload_template_resolves_node(self, mock_client):
        mock_client.upload = MagicMock(return_value="UPID:pve:0062:abc")
        with patch("builtins.open", mock_open(read_data=b"fake")):
            result = upload_template(
                mock_client, storage="local",
                filepath="/tmp/template.tar.xz", confirm=True,
            )
        assert "pve" in result
