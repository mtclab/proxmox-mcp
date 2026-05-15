from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.config import Config


class TestProxmoxClientInit:
    def test_creates_dual_clients(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            ProxmoxClient(mock_config)
            assert mock_api.call_count == 2

    def test_monitor_client_params(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            ProxmoxClient(mock_config)
            monitor_call = mock_api.call_args_list[0]
            assert monitor_call.kwargs["user"] == "zabbix@pve"
            assert monitor_call.kwargs["token_name"] == "zabbix"
            assert monitor_call.kwargs["token_value"] == "monitor-secret"
            assert monitor_call.kwargs["verify_ssl"] is False

    def test_admin_client_params(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            ProxmoxClient(mock_config)
            admin_call = mock_api.call_args_list[1]
            assert admin_call.kwargs["user"] == "homepilot@pve"
            assert admin_call.kwargs["token_name"] == "homepilot"
            assert admin_call.kwargs["token_value"] == "admin-secret"

    def test_ssl_verify_path(self) -> None:
        config = Config(
            url="https://myhost:8006",
            verify="/path/to/ca.pem",
            monitor_token_id="u@r!t",
            monitor_token_secret="s",
            admin_token_id="u@r!t2",
            admin_token_secret="s2",
        )
        with patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            ProxmoxClient(config)
            assert mock_api.call_args_list[0].kwargs["verify_ssl"] == "/path/to/ca.pem"


class TestGetClient:
    def test_returns_monitor_by_default(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            client = ProxmoxClient(mock_config)
            result = client.get_client()
            assert result is client.monitor_client

    def test_returns_admin_when_elevated(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            client = ProxmoxClient(mock_config)
            result = client.get_client(elevated=True)
            assert result is client.admin_client

    def test_raises_when_elevated_not_allowed(self, mock_config_no_elevated: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            client = ProxmoxClient(mock_config_no_elevated)
            with pytest.raises(ValueError, match="Elevated operations are not allowed"):
                client.get_client(elevated=True)


class TestRaiseIfNotElevated:
    def test_raises_when_not_allowed(self, mock_config_no_elevated: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            client = ProxmoxClient(mock_config_no_elevated)
            with pytest.raises(ValueError, match="PROXMOX_ALLOW_ELEVATED=true"):
                client.raise_if_not_elevated()

    def test_passes_when_allowed(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            client = ProxmoxClient(mock_config)
            client.raise_if_not_elevated()


class TestNodeDiscovery:
    def test_discover_nodes_caches(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.nodes.get.return_value = [
                {"node": "pve", "status": "online"},
            ]
            mock_api.return_value = mock_instance

            client = ProxmoxClient(mock_config)
            client.monitor_client = mock_instance

            result1 = client.discover_nodes()
            result2 = client.discover_nodes()
            assert result1 == result2
            assert mock_instance.nodes.get.call_count == 1

    def test_resolve_node_explicit(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            client = ProxmoxClient(mock_config)
            assert client.resolve_node("mynode") == "mynode"

    def test_resolve_node_default_config(self, mock_config: Config) -> None:
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            client = ProxmoxClient(mock_config)
            assert client.resolve_node() == "pve"

    def test_resolve_node_first_online(self) -> None:
        config = Config(
            url="https://myhost:8006",
            verify=True,
            monitor_token_id="u@r!t",
            monitor_token_secret="s",
            admin_token_id="u@r!t2",
            admin_token_secret="s2",
        )
        with patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.nodes.get.return_value = [
                {"node": "offline-node", "status": "offline"},
                {"node": "online-node", "status": "online"},
            ]
            mock_api.return_value = mock_instance
            client = ProxmoxClient(config)
            client.monitor_client = mock_instance
            assert client.resolve_node() == "online-node"

    def test_resolve_node_no_online_raises(self) -> None:
        config = Config(
            url="https://myhost:8006",
            verify=True,
            monitor_token_id="u@r!t",
            monitor_token_secret="s",
            admin_token_id="u@r!t2",
            admin_token_secret="s2",
        )
        with patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.nodes.get.return_value = []
            mock_api.return_value = mock_instance
            client = ProxmoxClient(config)
            client.monitor_client = mock_instance
            with pytest.raises(ValueError, match="No online node found"):
                client.resolve_node()


class TestResolveGuest:
    def test_resolve_by_vmid(self, mock_client: ProxmoxClient) -> None:
        node, vmid = mock_client.resolve_guest("100")
        assert vmid == 100

    def test_resolve_by_name(self, mock_client: ProxmoxClient) -> None:
        node, vmid = mock_client.resolve_guest("test-vm")
        assert vmid == 100

    def test_resolve_lxc_by_name(self, mock_client: ProxmoxClient) -> None:
        node, vmid = mock_client.resolve_guest("test-ct")
        assert vmid == 200

    def test_resolve_not_found_raises(self, mock_client: ProxmoxClient) -> None:
        with pytest.raises(ValueError, match="not found"):
            mock_client.resolve_guest("nonexistent")

    def test_resolve_with_explicit_node(self, mock_client: ProxmoxClient) -> None:
        node, vmid = mock_client.resolve_guest("100", node="explicit-node")
        assert node == "explicit-node"
        assert vmid == 100
