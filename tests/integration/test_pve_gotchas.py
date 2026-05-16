"""Integration tests verifying PVE API gotchas from live cluster testing.

These tests run against a real Proxmox VE cluster and validate known
gotchas/edge-cases discovered during integration testing.

Requires env vars: PROXMOX_URL, PROXMOX_MONITOR_TOKEN_ID,
PROXMOX_MONITOR_TOKEN_SECRET, PROXMOX_ADMIN_TOKEN_ID,
PROXMOX_ADMIN_TOKEN_SECRET, PROXMOX_ALLOW_ELEVATED=true

Run with: pytest tests/integration/test_pve_gotchas.py -m integration -v
"""

from __future__ import annotations

import os

import pytest

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.config import Config

PVE_NODE = os.environ.get("PROXMOX_DEFAULT_NODE", "pve")
NONEXISTENT_NODE = "no-such-node-xyz"
NONEXISTENT_VMID = 99999


def _make_config() -> Config:
    return Config(
        url=os.environ["PROXMOX_URL"],
        verify=False,
        monitor_token_id=os.environ["PROXMOX_MONITOR_TOKEN_ID"],
        monitor_token_secret=os.environ["PROXMOX_MONITOR_TOKEN_SECRET"],
        admin_token_id=os.environ["PROXMOX_ADMIN_TOKEN_ID"],
        admin_token_secret=os.environ["PROXMOX_ADMIN_TOKEN_SECRET"],
        allow_elevated=True,
        default_node=PVE_NODE,
    )


@pytest.fixture(scope="module")
def client() -> ProxmoxClient:
    cfg = _make_config()
    c = ProxmoxClient(cfg)
    c.discover_nodes()
    return c


@pytest.mark.integration
class TestNodeNameDiscovery:
    """Gotcha #1: GET /nodes returns 'pve' (PVE node name), not the hostname."""

    def test_list_nodes_returns_actual_pve_node_name(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.discovery import list_nodes

        result = list_nodes(client)
        assert "pve" in result, f"Expected node 'pve' in output, got: {result}"

    def test_discover_nodes_cache_has_pve(self, client: ProxmoxClient) -> None:
        nodes = client.discover_nodes()
        names = [n.get("node") for n in nodes]
        assert "pve" in names, f"Node 'pve' not in discovered nodes: {names}"


@pytest.mark.integration
class TestWrongNodeName:
    """Gotcha #2: Wrong node name returns friendly error, not raw 595."""

    def test_vm_config_wrong_node_raises_friendly(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.lifecycle import get_vm_config

        with pytest.raises(Exception) as exc_info:
            get_vm_config(client, node=NONEXISTENT_NODE, vmid=100)
        msg = str(exc_info.value).lower()
        assert "595" not in msg, f"Raw 595 error leaked: {exc_info.value}"
        assert "node" in msg or "not found" in msg or "error" in msg, (
            f"Error message not user-friendly: {exc_info.value}"
        )


@pytest.mark.integration
class TestTemplateDownload:
    """Gotcha #3: download_template requires confirm and elevated, validate params."""

    def test_download_template_requires_confirm(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.templates import download_template

        with pytest.raises(ValueError, match="confirm=true"):
            download_template(client, url="http://example.com/template.tar.gz")

    def test_download_template_requires_elevated(self) -> None:
        cfg = _make_config()
        cfg._allow_elevated = False
        cfg.allow_elevated = False
        from unittest.mock import patch

        with patch("proxmox_mcp.client.ProxmoxAPI"):
            c = ProxmoxClient(cfg)
        from proxmox_mcp.templates import download_template

        with pytest.raises(ValueError, match="Elevated"):
            download_template(
                c,
                url="http://example.com/template.tar.gz",
                storage="local",
                confirm=True,
            )

    def test_download_template_rejects_empty_url(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.templates import download_template

        with pytest.raises(ValueError, match="url is required"):
            download_template(client, url="", confirm=True)

    def test_list_templates_returns_data(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.templates import list_templates

        result = list_templates(client, node=PVE_NODE)
        assert "PVE Appliance Templates" in result or "No templates" in result


@pytest.mark.integration
class TestVM404Errors:
    """Gotcha #4: get_vm_config with non-existent VMID returns friendly message."""

    def test_vm_config_nonexistent_vmid(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.lifecycle import get_vm_config

        result = get_vm_config(client, node=PVE_NODE, vmid=NONEXISTENT_VMID)
        assert "not found" in result.lower(), f"Expected 'not found' message for VMID {NONEXISTENT_VMID}, got: {result}"

    def test_lxc_config_nonexistent_vmid(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.lifecycle import get_lxc_config

        result = get_lxc_config(client, node=PVE_NODE, vmid=NONEXISTENT_VMID)
        assert "not found" in result.lower(), f"Expected 'not found' message for VMID {NONEXISTENT_VMID}, got: {result}"


@pytest.mark.integration
class TestACLOperations:
    """Gotcha #5: ACL create/list operations work with admin token."""

    def test_list_acl_returns_data(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.permissions import list_acl

        result = list_acl(client)
        assert "ACL Rules" in result

    def test_list_roles_returns_data(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.permissions import list_roles

        result = list_roles(client)
        assert "Roles" in result or "roles" in result.lower()

    def test_list_users_returns_data(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.permissions import list_users

        result = list_users(client)
        assert "Users" in result or "users" in result.lower()


@pytest.mark.integration
class TestMachineTypes:
    """Gotcha #6: list_machine_types returns valid data for node 'pve'."""

    def test_list_machine_types_returns_data(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.capabilities import list_machine_types

        result = list_machine_types(client, node=PVE_NODE)
        assert "Machine Types" in result
        assert "q35" in result or "pc" in result or "Machine" in result, f"Expected common machine types, got: {result}"

    def test_list_cpu_models_returns_data(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.capabilities import list_cpu_models

        result = list_cpu_models(client, node=PVE_NODE)
        assert "CPU Models" in result or "cpu" in result.lower()


@pytest.mark.integration
class TestStorageListing:
    """Gotcha #7: list_storage returns storage pools with expected fields."""

    def test_list_storage_returns_pools(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.discovery import list_storage

        result = list_storage(client)
        assert "Storage Pools" in result
        assert "local" in result, f"Expected 'local' storage pool, got: {result}"

    def test_list_storage_has_expected_fields(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.discovery import list_storage

        result = list_storage(client)
        assert "type" in result.lower() or "(" in result, f"Expected storage type info in output, got: {result}"


@pytest.mark.integration
class TestUSBListing:
    """Gotcha #8: list_usb uses elevated token (requires Sys.Modify)."""

    def test_list_usb_returns_result(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.hardware import list_usb

        result = list_usb(client, node=PVE_NODE)
        assert "USB Devices" in result
        # On single-node cluster, may legitimately have no USB devices

    def test_list_pci_returns_result(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.hardware import list_pci

        result = list_pci(client, node=PVE_NODE)
        assert "PCI Devices" in result


@pytest.mark.integration
class TestNetworkListing:
    """Gotcha #9: list_network returns interfaces for node 'pve'."""

    def test_list_network_returns_interfaces(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.discovery import list_network

        result = list_network(client, node=PVE_NODE)
        assert "Network Interfaces" in result
        # Should always have at least lo or vmbr0
        assert "lo" in result or "vmbr0" in result or "eno" in result or "eth" in result or "enp" in result, (
            f"Expected at least one network interface, got: {result}"
        )

    def test_list_network_from_networking_module(self, client: ProxmoxClient) -> None:
        from proxmox_mcp.networking import list_network

        result = list_network(client, node=PVE_NODE)
        assert "Network Interfaces" in result


@pytest.mark.integration
class TestDiskSizeValidation:
    """Gotcha #10: validate_disk_size strips G/GiB/T/TiB suffixes correctly."""

    def test_strip_gib_suffix(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        assert validate_disk_size("32GiB") == "32"

    def test_strip_g_suffix(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        assert validate_disk_size("32G") == "32"

    def test_strip_tib_suffix(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        assert validate_disk_size("1TiB") == "1024"

    def test_strip_t_suffix(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        assert validate_disk_size("1T") == "1024"

    def test_plain_integer_passes(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        assert validate_disk_size("32") == "32"

    def test_int_input_passes(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        assert validate_disk_size(32) == "32"

    def test_invalid_suffix_raises(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("32MiB")

    def test_non_numeric_prefix_raises(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("abcG")

    def test_whitespace_stripped(self) -> None:
        from proxmox_mcp.utils import validate_disk_size

        assert validate_disk_size("  32G  ") == "32"
