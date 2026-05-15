from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.cloudinit import exec_lxc, exec_vm, set_cloudinit
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
    admin_mock = MagicMock()
    client.admin_client = admin_mock
    client.monitor_client = MagicMock()
    return client


class TestConfirmRequired:
    def test_set_cloudinit_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            set_cloudinit(mock_client, node="pve", vmid=100, ciuser="admin")

    def test_exec_vm_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            exec_vm(mock_client, node="pve", vmid=100, command="ls")

    def test_exec_lxc_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            exec_lxc(mock_client, node="pve", vmid=200, command="ls")


class TestElevatedCheck:
    def test_set_cloudinit_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            set_cloudinit(client, node="pve", vmid=100, ciuser="admin", confirm=True)

    def test_exec_vm_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            exec_vm(client, node="pve", vmid=100, command="ls", confirm=True)

    def test_exec_lxc_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            exec_lxc(client, node="pve", vmid=200, command="ls", confirm=True)


class TestSetCloudinit:
    def test_set_cloudinit_with_user(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0001:abc")
        result = set_cloudinit(mock_client, node="pve", vmid=100, ciuser="admin", confirm=True)
        assert "100" in result
        assert "Cloud-init" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["ciuser"] == "admin"

    def test_set_cloudinit_with_all_params(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0002:abc")
        result = set_cloudinit(
            mock_client, node="pve", vmid=100,
            ciuser="admin", cipassword="secret",
            ipconfig0="ip=192.168.1.10/24,gw=192.168.1.1",
            sshkeys="ssh-rsa AAA... user@host",
            confirm=True,
        )
        assert "100" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["ciuser"] == "admin"
        assert call_args[1]["cipassword"] == "secret"
        assert "ipconfig0" in call_args[1]
        assert "sshkeys" in call_args[1]

    def test_set_cloudinit_minimal(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0003:abc")
        result = set_cloudinit(mock_client, node="pve", vmid=100, ciuser="root", confirm=True)
        assert "Cloud-init" in result
        call_args = mock_client.safe_api_call.call_args
        assert "ciuser" in call_args[1]

    def test_set_cloudinit_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0004:abc")
        result = set_cloudinit(mock_client, vmid=100, ciuser="admin", confirm=True)
        assert "pve" in result


class TestExecVm:
    def test_exec_vm_basic(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": 1234})
        result = exec_vm(mock_client, node="pve", vmid=100, command="ls -la", confirm=True)
        assert "100" in result
        assert "PID" in result

    def test_exec_vm_requires_command(self, mock_client):
        with pytest.raises(ValueError, match="command is required"):
            exec_vm(mock_client, node="pve", vmid=100, confirm=True)

    def test_exec_vm_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0005:abc")
        result = exec_vm(mock_client, vmid=100, command="whoami", confirm=True)
        assert "pve" in result

    def test_exec_vm_string_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0006:abc")
        result = exec_vm(mock_client, node="pve", vmid=100, command="uptime", confirm=True)
        assert "100" in result


class TestExecLxc:
    def test_exec_lxc_basic(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": 5678})
        result = exec_lxc(mock_client, node="pve", vmid=200, command="ls -la", confirm=True)
        assert "200" in result
        assert "PID" in result

    def test_exec_lxc_requires_command(self, mock_client):
        with pytest.raises(ValueError, match="command is required"):
            exec_lxc(mock_client, node="pve", vmid=200, confirm=True)

    def test_exec_lxc_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0007:abc")
        result = exec_lxc(mock_client, vmid=200, command="whoami", confirm=True)
        assert "pve" in result

    def test_exec_lxc_string_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:0008:abc")
        result = exec_lxc(mock_client, node="pve", vmid=200, command="uptime", confirm=True)
        assert "200" in result
