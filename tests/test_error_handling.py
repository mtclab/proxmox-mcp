from __future__ import annotations

import ssl
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from proxmoxer.core import ResourceException

from proxmox_mcp.client import PVE_UPLOAD_FILE_FIELD, ProxmoxClient
from proxmox_mcp.config import Config
from proxmox_mcp.exceptions import (
    ProxmoxConnectionError,
    ProxmoxError,
    ProxmoxNodeError,
    ProxmoxNotFoundError,
    ProxmoxPermissionError,
    ProxmoxTaskError,
)


@pytest.fixture
def mock_config() -> Config:
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
def client(mock_config: Config) -> ProxmoxClient:
    with patch("proxmox_mcp.client.ProxmoxAPI"):
        c = ProxmoxClient(mock_config)
    c.monitor_client = MagicMock()
    c.admin_client = MagicMock()
    return c


def _make_595(msg: str = "connection refused") -> ResourceException:
    return ResourceException(595, "Errors during connection establishment", msg)


def _make_403(endpoint: str = "GET /nodes/pve/qemu") -> ResourceException:
    return ResourceException(403, "Forbidden", endpoint)


def _make_500_not_exists(vmid: int = 999, node: str = "pve", vmtype: str = "qemu") -> ResourceException:
    content = f"Configuration file 'nodes/{node}/{vmtype}-server/{vmid}.conf' does not exist"
    return ResourceException(500, "Internal Server Error", content)


class TestRetryWithBackoff595:
    async def test_retries_595_and_succeeds(self, client: ProxmoxClient) -> None:
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise _make_595()
            return "ok"

        with patch("proxmox_mcp.client.asyncio.sleep", new=AsyncMock()):
            result = await client.retry_with_backoff(flaky_func, max_retries=3, initial_delay=1.0)

        assert result == "ok"
        assert call_count == 3

    async def test_exhausts_retries_raises_connection_error(self, client: ProxmoxClient) -> None:
        def always_595():
            raise _make_595()

        with patch("proxmox_mcp.client.asyncio.sleep", new=AsyncMock()):
            with pytest.raises(ProxmoxConnectionError, match="595 error after 3 retries"):
                await client.retry_with_backoff(always_595, max_retries=3, initial_delay=1.0)

    async def test_exponential_backoff_timing(self, client: ProxmoxClient) -> None:
        call_count = 0

        def one_595_then_ok():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise _make_595()
            return "ok"

        with patch("proxmox_mcp.client.asyncio.sleep", new=AsyncMock()) as mock_sleep:
            await client.retry_with_backoff(one_595_then_ok, max_retries=3, initial_delay=1.0)
            assert mock_sleep.call_count == 1
            assert mock_sleep.call_args[0][0] == 1.0

    async def test_success_on_first_try(self, client: ProxmoxClient) -> None:
        def ok_func():
            return "done"

        result = await client.retry_with_backoff(ok_func, max_retries=3)
        assert result == "done"


class TestPermissionDenied403:
    async def test_403_raises_permission_error_with_elevated_hint(self, client: ProxmoxClient) -> None:
        def raise_403():
            raise _make_403("GET /nodes/pve/qemu/100/config")

        with pytest.raises(ProxmoxPermissionError, match="PROXMOX_ALLOW_ELEVATED=true"):
            await client.retry_with_backoff(raise_403)

    async def test_403_message_includes_endpoint(self, client: ProxmoxClient) -> None:
        def raise_403():
            raise _make_403("POST /nodes/pve/qemu/100/config")

        with pytest.raises(ProxmoxPermissionError, match="POST /nodes/pve/qemu/100/config"):
            await client.retry_with_backoff(raise_403)


class TestSSLError:
    async def test_ssl_error_suggests_verify_false(self, client: ProxmoxClient) -> None:
        def raise_ssl():
            raise ssl.SSLCertVerificationError("hostname '10.96.16.19' doesn't match")

        with pytest.raises(ProxmoxConnectionError, match="PROXMOX_VERIFY=false"):
            await client.retry_with_backoff(raise_ssl)

    async def test_ssl_error_suggests_ca_path(self, client: ProxmoxClient) -> None:
        def raise_ssl():
            raise ssl.SSLCertVerificationError("cert verify failed")

        with pytest.raises(ProxmoxConnectionError, match="PROXMOX_VERIFY=/path/to/ca.pem"):
            await client.retry_with_backoff(raise_ssl)


class TestWaitForTask:
    async def test_successful_task(self, client: ProxmoxClient) -> None:
        upid = "UPID:pve:00001234:abcdef:user@pve:task:1234567890"
        task_result = {"status": "stopped", "exitstatus": "OK"}
        client.monitor_client.nodes.return_value.tasks.return_value.status.get.return_value = task_result

        result = await client.wait_for_task(upid)
        assert result["exitstatus"] == "OK"

    async def test_failed_task_raises_task_error(self, client: ProxmoxClient) -> None:
        upid = "UPID:pve:00001234:abcdef:user@pve:task:1234567890"
        task_result = {"status": "stopped", "exitstatus": "command failed: some error"}
        client.monitor_client.nodes.return_value.tasks.return_value.status.get.return_value = task_result

        with pytest.raises(ProxmoxTaskError, match="command failed"):
            await client.wait_for_task(upid)

    async def test_task_error_includes_exitstatus(self, client: ProxmoxClient) -> None:
        upid = "UPID:pve:00001234:abcdef:user@pve:task:1234567890"
        task_result = {"status": "stopped", "exitstatus": "command failed: VM is locked"}
        client.monitor_client.nodes.return_value.tasks.return_value.status.get.return_value = task_result

        with pytest.raises(ProxmoxTaskError) as exc_info:
            await client.wait_for_task(upid)
        assert exc_info.value.exitstatus == "command failed: VM is locked"


class TestWrongNodeName:
    async def test_node_error_on_595_with_node_endpoint(self, client: ProxmoxClient) -> None:
        exc = _make_595()
        exc.content = "/nodes/wrong-node/qemu/100/status/current"

        def raise_595():
            raise exc

        with patch("proxmox_mcp.client.asyncio.sleep", new=AsyncMock()):
            with pytest.raises(ProxmoxNodeError, match="proxmox-list-nodes"):
                await client.safe_api_call(raise_595)

    async def test_node_error_includes_node_name(self, client: ProxmoxClient) -> None:
        exc = _make_595()
        exc.content = "/nodes/badhost/lxc/200/status/current"

        def raise_595():
            raise exc

        with patch("proxmox_mcp.client.asyncio.sleep", new=AsyncMock()):
            with pytest.raises(ProxmoxNodeError) as exc_info:
                await client.safe_api_call(raise_595)
            assert exc_info.value.node == "badhost"


class TestCustomExceptions:
    async def test_proxmox_error_is_base(self) -> None:
        assert issubclass(ProxmoxConnectionError, ProxmoxError)
        assert issubclass(ProxmoxPermissionError, ProxmoxError)
        assert issubclass(ProxmoxTaskError, ProxmoxError)
        assert issubclass(ProxmoxNodeError, ProxmoxError)
        assert issubclass(ProxmoxNotFoundError, ProxmoxError)

    async def test_proxmox_task_error_attributes(self) -> None:
        err = ProxmoxTaskError("command failed: exit 1", "output details")
        assert err.exitstatus == "command failed: exit 1"
        assert err.output == "output details"
        assert "command failed: exit 1" in str(err)

    async def test_proxmox_task_error_no_output(self) -> None:
        err = ProxmoxTaskError("UNKNOWN")
        assert err.output is None

    async def test_proxmox_node_error_attributes(self) -> None:
        err = ProxmoxNodeError("bad-node", "not found")
        assert err.node == "bad-node"
        assert "bad-node" in str(err)

    async def test_proxmox_connection_error_message(self) -> None:
        err = ProxmoxConnectionError("PVE 595: connection refused")
        assert "595" in str(err)

    async def test_proxmox_permission_error_message(self) -> None:
        err = ProxmoxPermissionError("Permission denied on /nodes/pve")
        assert "Permission denied" in str(err)

    async def test_proxmox_not_found_with_node(self) -> None:
        err = ProxmoxNotFoundError("Guest 999", "pve")
        assert err.resource == "Guest 999"
        assert err.node == "pve"
        assert "Guest 999 not found on node pve" in str(err)

    async def test_proxmox_not_found_without_node(self) -> None:
        err = ProxmoxNotFoundError("Resource xyz")
        assert err.node is None
        assert "Resource xyz not found" in str(err)


class TestUploadFieldConstant:
    async def test_upload_field_is_filename(self) -> None:
        assert PVE_UPLOAD_FILE_FIELD == "filename"


class TestNotFound500:
    async def test_500_not_exist_raises_not_found_error(self, client: ProxmoxClient) -> None:
        def raise_500_not_exist():
            raise _make_500_not_exists(vmid=999, node="pve")

        with pytest.raises(ProxmoxNotFoundError, match="Guest 999 not found on node pve"):
            await client.retry_with_backoff(raise_500_not_exist)

    async def test_500_not_exist_lxc(self, client: ProxmoxClient) -> None:
        def raise_500_lxc_not_exist():
            raise _make_500_not_exists(vmid=200, node="mynode", vmtype="lxc")

        with pytest.raises(ProxmoxNotFoundError, match="Guest 200 not found on node mynode"):
            await client.retry_with_backoff(raise_500_lxc_not_exist)

    async def test_500_other_error_reraises(self, client: ProxmoxClient) -> None:
        def raise_500_other():
            raise ResourceException(500, "Internal Server Error", "some other 500 error")

        with pytest.raises(ResourceException):
            await client.retry_with_backoff(raise_500_other)

    async def test_safe_api_call_propagates_not_found(self, client: ProxmoxClient) -> None:
        def raise_500_not_exist():
            raise _make_500_not_exists(vmid=42, node="pve")

        with pytest.raises(ProxmoxNotFoundError, match="Guest 42 not found on node pve"):
            await client.safe_api_call(raise_500_not_exist)
