"""Integration tests for cluster and discovery modules against live PVE cluster.

Requires PVE_API_URL, PVE_MONITOR_TOKEN_ID, PVE_MONITOR_TOKEN_SECRET,
PVE_ADMIN_TOKEN_ID, PVE_ADMIN_TOKEN_SECRET env vars (or proxmox.json secrets file).

Run with: pytest tests/integration/ -m integration -v
Skip in CI without PVE access: pytest -m "not integration"
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.cluster import (
    api_version,
    cluster_config,
    cluster_config_nodes,
    cluster_log,
    cluster_options,
    cluster_status,
    get_next_vmid,
    list_backup_jobs,
)
from proxmox_mcp.discovery import (
    cluster_resources,
    list_lxc,
    list_network,
    list_nodes,
    list_storage,
    list_vms,
)
from proxmox_mcp.disks import list_disks
from proxmox_mcp.storage import list_isos
from proxmox_mcp.templates import list_templates

SECRETS_PATH = Path("/home/kasm-user/.config/opencode/secrets/proxmox.json")


def _load_secrets() -> dict[str, str]:
    if SECRETS_PATH.exists():
        with open(SECRETS_PATH) as f:
            return json.load(f)
    return {
        "PVE_URL": os.environ.get("PROXMOX_URL", "https://192.168.100.2:8006"),
        "PVE_MONITOR_TOKEN_ID": os.environ.get("PROXMOX_MONITOR_TOKEN_ID", "zabbix@pve!zabbix"),
        "PVE_MONITOR_TOKEN_SECRET": os.environ.get("PROXMOX_MONITOR_TOKEN_SECRET", ""),
        "PVE_ADMIN_TOKEN_ID": os.environ.get("PROXMOX_ADMIN_TOKEN_ID", "homepilot@pve!homepilot"),
        "PVE_ADMIN_TOKEN_SECRET": os.environ.get("PROXMOX_ADMIN_TOKEN_SECRET", ""),
        "PVE_NODE": os.environ.get("PROXMOX_DEFAULT_NODE", "pve"),
    }


def _make_client() -> ProxmoxClient:
    from proxmox_mcp.config import Config

    secrets = _load_secrets()
    url = secrets.get("PVE_URL", secrets.get("PROXMOX_URL", "https://192.168.100.2:8006"))
    url = url.replace("http://", "https://")
    if not url.startswith("https://"):
        url = f"https://{url}"
    if ":8006" not in url:
        url = f"{url}:8006"

    monitor_id = secrets.get("PVE_MONITOR_TOKEN_ID", secrets.get("PROXMOX_MONITOR_TOKEN_ID", ""))
    monitor_secret = secrets.get("PVE_MONITOR_TOKEN_SECRET", secrets.get("PROXMOX_MONITOR_TOKEN_SECRET", ""))
    admin_id = secrets.get("PVE_ADMIN_TOKEN_ID", secrets.get("PROXMOX_ADMIN_TOKEN_ID", ""))
    admin_secret = secrets.get("PVE_ADMIN_TOKEN_SECRET", secrets.get("PROXMOX_ADMIN_TOKEN_SECRET", ""))
    default_node = secrets.get("PVE_NODE", secrets.get("PROXMOX_DEFAULT_NODE", "pve"))

    config = Config(
        url=url,
        verify=False,
        monitor_token_id=monitor_id,
        monitor_token_secret=monitor_secret,
        admin_token_id=admin_id,
        admin_token_secret=admin_secret,
        allow_elevated=True,
        default_node=default_node,
    )
    return ProxmoxClient(config)


@pytest.fixture(scope="module")
def pve_client() -> ProxmoxClient:
    return _make_client()


# ── Cluster module ──────────────────────────────────────────────────


@pytest.mark.integration
class TestClusterStatusLive:
    def test_cluster_status_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = cluster_status(pve_client)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_cluster_status_contains_cluster_info(self, pve_client: ProxmoxClient) -> None:
        result = cluster_status(pve_client)
        assert "Cluster" in result or "cluster" in result.lower()

    def test_cluster_status_shows_node(self, pve_client: ProxmoxClient) -> None:
        result = cluster_status(pve_client)
        assert "pve" in result


@pytest.mark.integration
class TestClusterOptionsLive:
    def test_cluster_options_returns_dict(self, pve_client: ProxmoxClient) -> None:
        result = cluster_options(pve_client)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_cluster_options_has_content(self, pve_client: ProxmoxClient) -> None:
        result = cluster_options(pve_client)
        assert "keyboard" in result.lower() or "Cluster Options" in result or "option" in result.lower()


@pytest.mark.integration
class TestClusterConfigLive:
    def test_cluster_config_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = cluster_config(pve_client)
        assert isinstance(result, str)

    def test_cluster_config_nodes(self, pve_client: ProxmoxClient) -> None:
        result = cluster_config_nodes(pve_client)
        assert isinstance(result, str)
        assert "pve" in result


@pytest.mark.integration
class TestClusterLogLive:
    def test_cluster_log_returns_entries(self, pve_client: ProxmoxClient) -> None:
        result = cluster_log(pve_client, limit=5)
        assert isinstance(result, str)
        assert "Cluster Log" in result or "log" in result.lower()


@pytest.mark.integration
class TestApiVersionLive:
    def test_api_version(self, pve_client: ProxmoxClient) -> None:
        result = api_version(pve_client)
        assert isinstance(result, str)
        assert "version" in result.lower() or "Version" in result


@pytest.mark.integration
class TestGetNextVmidLive:
    def test_get_next_vmid(self, pve_client: ProxmoxClient) -> None:
        result = get_next_vmid(pve_client)
        assert isinstance(result, str)
        assert "Next VMID" in result or "vmid" in result.lower()
        lines = result.strip().split("\n")
        vmid_line = [l for l in lines if l.strip() and "•" in l]
        assert len(vmid_line) >= 1
        vmid_str = vmid_line[0].split("•")[-1].strip()
        assert vmid_str.isdigit()


@pytest.mark.integration
class TestListBackupJobsLive:
    def test_list_backup_jobs(self, pve_client: ProxmoxClient) -> None:
        result = list_backup_jobs(pve_client)
        assert isinstance(result, str)
        assert "Backup" in result or "backup" in result.lower()


# ── Discovery module ───────────────────────────────────────────────


@pytest.mark.integration
class TestListNodesLive:
    def test_list_nodes_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_nodes(pve_client)
        assert isinstance(result, str)

    def test_list_nodes_contains_pve(self, pve_client: ProxmoxClient) -> None:
        result = list_nodes(pve_client)
        assert "pve" in result

    def test_list_nodes_has_status(self, pve_client: ProxmoxClient) -> None:
        result = list_nodes(pve_client)
        assert "online" in result.lower() or "offline" in result.lower()


@pytest.mark.integration
class TestClusterResourcesLive:
    def test_cluster_resources_all(self, pve_client: ProxmoxClient) -> None:
        result = cluster_resources(pve_client)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_cluster_resources_by_type_vm(self, pve_client: ProxmoxClient) -> None:
        result = cluster_resources(pve_client, type="vm")
        assert isinstance(result, str)
        assert "vm" in result.lower() or "Resources" in result

    def test_cluster_resources_by_type_storage(self, pve_client: ProxmoxClient) -> None:
        result = cluster_resources(pve_client, type="storage")
        assert isinstance(result, str)
        assert "storage" in result.lower() or "local" in result.lower()

    def test_cluster_resources_invalid_type_raises(self, pve_client: ProxmoxClient) -> None:
        with pytest.raises(ValueError, match="Invalid type"):
            cluster_resources(pve_client, type="invalid")


@pytest.mark.integration
class TestListVmsLive:
    def test_list_vms_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_vms(pve_client)
        assert isinstance(result, str)

    def test_list_vms_has_vm_header(self, pve_client: ProxmoxClient) -> None:
        result = list_vms(pve_client)
        assert "Virtual Machines" in result or "VM" in result


@pytest.mark.integration
class TestListLxcLive:
    def test_list_lxc_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_lxc(pve_client)
        assert isinstance(result, str)

    def test_list_lxc_has_lxc_header(self, pve_client: ProxmoxClient) -> None:
        result = list_lxc(pve_client)
        assert "LXC" in result


@pytest.mark.integration
class TestListStorageLive:
    def test_list_storage_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_storage(pve_client)
        assert isinstance(result, str)

    def test_list_storage_has_local(self, pve_client: ProxmoxClient) -> None:
        result = list_storage(pve_client)
        assert "local" in result.lower()

    def test_list_storage_has_storage_type(self, pve_client: ProxmoxClient) -> None:
        result = list_storage(pve_client)
        assert "Storage" in result


@pytest.mark.integration
class TestListNetworkLive:
    def test_list_network_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_network(pve_client)
        assert isinstance(result, str)

    def test_list_network_has_interfaces(self, pve_client: ProxmoxClient) -> None:
        result = list_network(pve_client)
        assert "Network" in result or "network" in result.lower()
        lines = [l for l in result.split("\n") if "•" in l]
        assert len(lines) >= 1  # at least one interface on pve node


@pytest.mark.integration
class TestListDisksLive:
    def test_list_disks_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_disks(pve_client)
        assert isinstance(result, str)

    def test_list_disks_has_disk_header(self, pve_client: ProxmoxClient) -> None:
        result = list_disks(pve_client)
        assert "Disks" in result or "disk" in result.lower()


@pytest.mark.integration
class TestListIsosLive:
    def test_list_isos_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_isos(pve_client, storage="local")
        assert isinstance(result, str)

    def test_list_isos_has_iso_header(self, pve_client: ProxmoxClient) -> None:
        result = list_isos(pve_client, storage="local")
        assert "ISO" in result


@pytest.mark.integration
class TestListTemplatesLive:
    def test_list_templates_returns_string(self, pve_client: ProxmoxClient) -> None:
        result = list_templates(pve_client)
        assert isinstance(result, str)

    def test_list_templates_has_template_header(self, pve_client: ProxmoxClient) -> None:
        result = list_templates(pve_client)
        assert "Template" in result or "Appliance" in result
