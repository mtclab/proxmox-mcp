from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.client import ProxmoxClient
from proxmox_mcp.config import Config


@pytest.fixture
def env_vars() -> dict[str, str]:
    return {
        "PROXMOX_URL": "https://10.96.16.19:8006",
        "PROXMOX_VERIFY": "false",
        "PROXMOX_MONITOR_TOKEN_ID": "zabbix@pve!zabbix",
        "PROXMOX_MONITOR_TOKEN_SECRET": "monitor-secret",
        "PROXMOX_ADMIN_TOKEN_ID": "homepilot@pve!homepilot",
        "PROXMOX_ADMIN_TOKEN_SECRET": "admin-secret",
        "PROXMOX_ALLOW_ELEVATED": "true",
        "PROXMOX_DEFAULT_NODE": "pve",
    }


@pytest.fixture
def mock_config(env_vars: dict[str, str]) -> Config:
    return Config(
        url=env_vars["PROXMOX_URL"],
        verify=False,
        monitor_token_id=env_vars["PROXMOX_MONITOR_TOKEN_ID"],
        monitor_token_secret=env_vars["PROXMOX_MONITOR_TOKEN_SECRET"],
        admin_token_id=env_vars["PROXMOX_ADMIN_TOKEN_ID"],
        admin_token_secret=env_vars["PROXMOX_ADMIN_TOKEN_SECRET"],
        allow_elevated=True,
        default_node="pve",
    )


@pytest.fixture
def mock_config_no_elevated(env_vars: dict[str, str]) -> Config:
    return Config(
        url=env_vars["PROXMOX_URL"],
        verify=False,
        monitor_token_id=env_vars["PROXMOX_MONITOR_TOKEN_ID"],
        monitor_token_secret=env_vars["PROXMOX_MONITOR_TOKEN_SECRET"],
        admin_token_id=env_vars["PROXMOX_ADMIN_TOKEN_ID"],
        admin_token_secret=env_vars["PROXMOX_ADMIN_TOKEN_SECRET"],
        allow_elevated=False,
        default_node="pve",
    )


@pytest.fixture
def mock_pve_nodes() -> list[dict[str, Any]]:
    return [
        {"node": "pve", "status": "online", "cpu": 0.1},
        {"node": "pve2", "status": "online", "cpu": 0.2},
    ]


@pytest.fixture
def mock_vm_list() -> list[dict[str, Any]]:
    return [
        {"vmid": 100, "name": "test-vm", "status": "running"},
        {"vmid": 101, "name": "test-vm2", "status": "stopped"},
    ]


@pytest.fixture
def mock_lxc_list() -> list[dict[str, Any]]:
    return [
        {"vmid": 200, "name": "test-ct", "status": "running"},
    ]


class _GuestAccessor:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self._data = data

    def get(self) -> list[dict[str, Any]]:
        return self._data


class _NodeAccessor:
    def __init__(
        self,
        vm_data: list[dict[str, Any]],
        lxc_data: list[dict[str, Any]],
    ) -> None:
        self._accessors: dict[str, _GuestAccessor] = {
            "qemu": _GuestAccessor(vm_data),
            "lxc": _GuestAccessor(lxc_data),
        }

    def __getattr__(self, name: str) -> Any:
        if name in self._accessors:
            return self._accessors[name]
        raise AttributeError(name)


@pytest.fixture
def mock_client(
    mock_config: Config,
    mock_pve_nodes: list[dict[str, Any]],
    mock_vm_list: list[dict[str, Any]],
    mock_lxc_list: list[dict[str, Any]],
) -> ProxmoxClient:
    with patch("proxmox_mcp.client.ProxmoxAPI"):
        client = ProxmoxClient(mock_config)
    client._nodes_cache = mock_pve_nodes

    mock_api = MagicMock()
    node_accessor = _NodeAccessor(mock_vm_list, mock_lxc_list)
    mock_api.nodes.return_value = node_accessor

    client.monitor_client = mock_api
    client.admin_client = MagicMock()

    async def _mock_safe_api_call(func, *args, **kwargs):
        if callable(func):
            return func()
        return func

    client.safe_api_call = AsyncMock(side_effect=_mock_safe_api_call)

    async def _mock_resolve_node(node=None):
        if node:
            return node
        return "pve"

    client.resolve_node = _mock_resolve_node

    return client
