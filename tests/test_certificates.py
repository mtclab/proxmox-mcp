from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.certificates import (
    delete_custom_certificate,
    list_certificates,
    order_acme_certificate,
    renew_acme_certificate,
    revoke_certificate,
    upload_custom_certificate,
)
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


class TestListCertificates:
    def test_list_certificates_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {
                "filename": "pve-node.pem",
                "subject": "CN=pve.local",
                "issuer": "CN=Let's Encrypt Authority",
                "notbefore": "2024-01-01",
                "notafter": "2024-04-01",
                "fingerprint": "SHA256:abc123",
            },
        ])
        result = list_certificates(mock_client, node="pve")
        assert "pve-node.pem" in result
        assert "pve.local" in result
        assert "Certificates" in result

    def test_list_certificates_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_certificates(mock_client, node="pve")
        assert "No certificates" in result

    def test_list_certificates_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_certificates(mock_client, node="bad node!")


class TestOrderAcmeCertificate:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            order_acme_certificate(mock_client, node="pve")

    def test_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:00000001:acme:order"
        )
        result = order_acme_certificate(mock_client, node="pve", confirm=True)
        assert "ACME certificate order initiated" in result


class TestRenewAcmeCertificate:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            renew_acme_certificate(mock_client, node="pve")

    def test_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:00000002:acme:renew"
        )
        result = renew_acme_certificate(mock_client, node="pve", confirm=True)
        assert "ACME certificate renewal initiated" in result


class TestRevokeCertificate:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            revoke_certificate(mock_client, node="pve")

    def test_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:00000003:acme:revoke"
        )
        result = revoke_certificate(mock_client, node="pve", confirm=True)
        assert "Certificate revocation initiated" in result


class TestUploadCustomCertificate:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            upload_custom_certificate(
                mock_client, node="pve", certificates="cert", key="key"
            )

    def test_requires_cert_and_key(self, mock_client):
        with pytest.raises(ValueError, match="certificates.*key.*required"):
            upload_custom_certificate(mock_client, node="pve", confirm=True)

    def test_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:00000004:cert:upload"
        )
        result = upload_custom_certificate(
            mock_client,
            node="pve",
            certificates="cert-data",
            key="key-data",
            confirm=True,
        )
        assert "Custom certificate uploaded" in result


class TestDeleteCustomCertificate:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            delete_custom_certificate(mock_client, node="pve")

    def test_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value="UPID:pve:00000005:cert:delete"
        )
        result = delete_custom_certificate(mock_client, node="pve", confirm=True)
        assert "Custom certificate deleted" in result
