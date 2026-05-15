from __future__ import annotations

import ssl
from unittest.mock import MagicMock, patch

import pytest
from proxmoxer.core import ResourceException

from proxmox_mcp.client import PVE_UPLOAD_FILE_FIELD, ProxmoxClient
from proxmox_mcp.config import Config
from proxmox_mcp.exceptions import (
    ProxmoxConnectionError,
    ProxmoxError,
    ProxmoxNodeError,
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


class TestRetryWithBackoff595:
    def test_retries_595_and_succeeds(self, client: ProxmoxClient) -> None:
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise _make_595()
            return "ok"

        with patch("proxmox_mcp.client.time.sleep"):
            result = client.retry_with_backoff(flaky_func, max_retries=3, initial_delay=1.0)

        assert result == "ok"
        assert call_count == 3

    def test_exhausts_retries_raises_connection_error(self, client: ProxmoxClient) -> None:
        def always_595():
            raise _make_595()

        with patch("proxmox_mcp.client.time.sleep"):
            with pytest.raises(ProxmoxConnectionError, match="595 error after 3 retries"):
                client.retry_with_backoff(always_595, max_retries=3, initial_delay=1.0)

    def test_exponential_backoff_timing(self, client: ProxmoxClient) -> None:
        call_count = 0

        def one_595_then_ok():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise _make_595()
            return "ok"

        with patch("proxmox_mcp.client.time.sleep") as mock_sleep:
            client.retry_with_backoff(one_595_then_ok, max_retries=3, initial_delay=1.0)
            assert mock_sleep.call_count == 1
            assert mock_sleep.call_args[0][0] == 1.0

    def test_success_on_first_try(self, client: ProxmoxClient) -> None:
        def ok_func():
            return "done"

        result = client.retry_with_backoff(ok_func, max_retries=3)
        assert result == "done"


class TestPermissionDenied403:
    def test_403_raises_permission_error_with_elevated_hint(self, client: ProxmoxClient) -> None:
        def raise_403():
            raise _make_403("GET /nodes/pve/qemu/100/config")

        with pytest.raises(ProxmoxPermissionError, match="PROXMOX_ALLOW_ELEVATED=true"):
            client.retry_with_backoff(raise_403)

    def test_403_message_includes_endpoint(self, client: ProxmoxClient) -> None:
        def raise_403():
            raise _make_403("POST /nodes/pve/qemu/100/config")

        with pytest.raises(ProxmoxPermissionError, match="POST /nodes/pve/qemu/100/config"):
            client.retry_with_backoff(raise_403)


class TestSSLError:
    def test_ssl_error_suggests_verify_false(self, client: ProxmoxClient) -> None:
        def raise_ssl():
            raise ssl.SSLCertVerificationError(
                "hostname '10.96.16.19' doesn't match"
            )

        with pytest.raises(ProxmoxConnectionError, match="PROXMOX_VERIFY=false"):
            client.retry_with_backoff(raise_ssl)

    def test_ssl_error_suggests_ca_path(self, client: ProxmoxClient) -> None:
        def raise_ssl():
            raise ssl.SSLCertVerificationError("cert verify failed")

        with pytest.raises(ProxmoxConnectionError, match="PROXMOX_VERIFY=/path/to/ca.pem"):
            client.retry_with_backoff(raise_ssl)


class TestWaitForTask:
    def test_successful_task(self, client: ProxmoxClient) -> None:
        upid = "UPID:pve:00001234:abcdef:user@pve:task:1234567890"
        task_result = {"status": "stopped", "exitstatus": "OK"}
        client.monitor_client.nodes.return_value.tasks.return_value.status.get.return_value = task_result

        result = client.wait_for_task(upid)
        assert result["exitstatus"] == "OK"

    def test_failed_task_raises_task_error(self, client: ProxmoxClient) -> None:
        upid = "UPID:pve:00001234:abcdef:user@pve:task:1234567890"
        task_result = {"status": "stopped", "exitstatus": "command failed: some error"}
        client.monitor_client.nodes.return_value.tasks.return_value.status.get.return_value = task_result

        with pytest.raises(ProxmoxTaskError, match="command failed"):
            client.wait_for_task(upid)

    def test_task_error_includes_exitstatus(self, client: ProxmoxClient) -> None:
        upid = "UPID:pve:00001234:abcdef:user@pve:task:1234567890"
        task_result = {"status": "stopped", "exitstatus": "command failed: VM is locked"}
        client.monitor_client.nodes.return_value.tasks.return_value.status.get.return_value = task_result

        with pytest.raises(ProxmoxTaskError) as exc_info:
            client.wait_for_task(upid)
        assert exc_info.value.exitstatus == "command failed: VM is locked"


class TestWrongNodeName:
    def test_node_error_on_595_with_node_endpoint(self, client: ProxmoxClient) -> None:
        exc = _make_595()
        exc.content = "/nodes/wrong-node/qemu/100/status/current"

        def raise_595():
            raise exc

        with patch("proxmox_mcp.client.time.sleep"):
            with pytest.raises(ProxmoxNodeError, match="proxmox-list-nodes"):
                client.safe_api_call(raise_595)

    def test_node_error_includes_node_name(self, client: ProxmoxClient) -> None:
        exc = _make_595()
        exc.content = "/nodes/badhost/lxc/200/status/current"

        def raise_595():
            raise exc

        with patch("proxmox_mcp.client.time.sleep"):
            with pytest.raises(ProxmoxNodeError) as exc_info:
                client.safe_api_call(raise_595)
            assert exc_info.value.node == "badhost"


class TestCustomExceptions:
    def test_proxmox_error_is_base(self) -> None:
        assert issubclass(ProxmoxConnectionError, ProxmoxError)
        assert issubclass(ProxmoxPermissionError, ProxmoxError)
        assert issubclass(ProxmoxTaskError, ProxmoxError)
        assert issubclass(ProxmoxNodeError, ProxmoxError)

    def test_proxmox_task_error_attributes(self) -> None:
        err = ProxmoxTaskError("command failed: exit 1", "output details")
        assert err.exitstatus == "command failed: exit 1"
        assert err.output == "output details"
        assert "command failed: exit 1" in str(err)

    def test_proxmox_task_error_no_output(self) -> None:
        err = ProxmoxTaskError("UNKNOWN")
        assert err.output is None

    def test_proxmox_node_error_attributes(self) -> None:
        err = ProxmoxNodeError("bad-node", "not found")
        assert err.node == "bad-node"
        assert "bad-node" in str(err)

    def test_proxmox_connection_error_message(self) -> None:
        err = ProxmoxConnectionError("PVE 595: connection refused")
        assert "595" in str(err)

    def test_proxmox_permission_error_message(self) -> None:
        err = ProxmoxPermissionError("Permission denied on /nodes/pve")
        assert "Permission denied" in str(err)


class TestUploadFieldConstant:
    def test_upload_field_is_filename(self) -> None:
        assert PVE_UPLOAD_FILE_FIELD == "filename"
