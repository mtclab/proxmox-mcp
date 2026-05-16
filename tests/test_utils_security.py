from unittest.mock import patch

import pytest

from proxmox_mcp.exceptions import ProxmoxPermissionError
from proxmox_mcp.utils import validate_url


class TestValidateUrl:
    def test_https_public_domain_passes(self):
        with patch("proxmox_mcp.utils.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
            validate_url("https://example.com/template.tar.xz")

    def test_http_scheme_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="https scheme"):
            validate_url("http://example.com/template.tar.xz")

    def test_ftp_scheme_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="https scheme"):
            validate_url("ftp://example.com/template.tar.xz")

    def test_private_ip_10_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="private/internal"):
            validate_url("https://10.0.0.1/template.tar.xz")

    def test_private_ip_172_16_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="private/internal"):
            validate_url("https://172.16.0.1/template.tar.xz")

    def test_private_ip_192_168_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="private/internal"):
            validate_url("https://192.168.1.1/template.tar.xz")

    def test_private_ip_127_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="private/internal"):
            validate_url("https://127.0.0.1/template.tar.xz")

    def test_private_ip_169_254_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="private/internal"):
            validate_url("https://169.254.169.254/template.tar.xz")

    def test_ipv6_loopback_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="private/internal"):
            validate_url("https://[::1]/template.tar.xz")

    def test_hostname_resolving_to_private_ip_rejected(self):
        with patch("proxmox_mcp.utils.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (2, 1, 6, "", ("10.0.0.1", 0)),
            ]
            with pytest.raises(ProxmoxPermissionError, match="private/internal IP"):
                validate_url("https://internal.corp/template.tar.xz")

    def test_public_ip_passes(self):
        validate_url("https://93.184.216.34/template.tar.xz")

    def test_no_hostname_rejected(self):
        with pytest.raises(ProxmoxPermissionError, match="hostname"):
            validate_url("https:///template.tar.xz")
