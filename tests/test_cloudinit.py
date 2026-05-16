from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.cloudinit import (
    agent_exec_status,
    agent_fsfreeze,
    agent_fsinfo,
    agent_fsthaw,
    agent_info,
    agent_network_interfaces,
    agent_osinfo,
    agent_ping,
    cloudinit_dump,
    exec_vm,
    set_cloudinit,
)
from proxmox_mcp.config import Config
from proxmox_mcp.exceptions import ProxmoxPermissionError


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

    def test_agent_fsfreeze_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_fsfreeze(mock_client, node="pve", vmid=100, confirm=False)

    def test_agent_fsthaw_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_fsthaw(mock_client, node="pve", vmid=100, confirm=False)


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

    def test_agent_ping_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_ping(client, node="pve", vmid=100, confirm=True)

    def test_agent_info_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_info(client, node="pve", vmid=100)

    def test_agent_network_interfaces_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_network_interfaces(client, node="pve", vmid=100)

    def test_agent_osinfo_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_osinfo(client, node="pve", vmid=100)

    def test_agent_fsinfo_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_fsinfo(client, node="pve", vmid=100)

    def test_agent_exec_status_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_exec_status(client, node="pve", vmid=100, pid=1234)

    def test_agent_fsfreeze_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_fsfreeze(client, node="pve", vmid=100, confirm=True)

    def test_agent_fsthaw_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            agent_fsthaw(client, node="pve", vmid=100, confirm=True)


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

    def test_exec_vm_allowed_command_passes(self, mock_client):
        mock_client.config.allowed_commands = ["ls", "whoami", "ping"]
        mock_client.safe_api_call = MagicMock(return_value={"data": 1234})
        result = exec_vm(mock_client, node="pve", vmid=100, command="whoami", confirm=True)
        assert "100" in result

    def test_exec_vm_blocked_command_raises(self, mock_client):
        mock_client.config.allowed_commands = ["ls", "whoami", "ping"]
        with pytest.raises(ProxmoxPermissionError, match="not in allowed list"):
            exec_vm(mock_client, node="pve", vmid=100, command="rm -rf /", confirm=True)

    def test_exec_vm_no_allowlist_allows_all(self, mock_client):
        mock_client.config.allowed_commands = None
        mock_client.safe_api_call = MagicMock(return_value={"data": 9999})
        result = exec_vm(mock_client, node="pve", vmid=100, command="rm -rf /", confirm=True)
        assert "9999" in result

    def test_exec_vm_explicit_allowed_commands_overrides_config(self, mock_client):
        mock_client.config.allowed_commands = ["ls"]
        mock_client.safe_api_call = MagicMock(return_value={"data": 5555})
        result = exec_vm(
            mock_client, node="pve", vmid=100, command="hostname",
            confirm=True, allowed_commands=["hostname"],
        )
        assert "5555" in result


class TestAgentPing:
    def test_agent_ping_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"result": True}})
        result = agent_ping(mock_client, node="pve", vmid=100, confirm=True)
        assert "100" in result
        assert "ping" in result.lower()

    def test_agent_ping_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"result": True}})
        result = agent_ping(mock_client, vmid=100, confirm=True)
        assert "pve" in result

    def test_agent_ping_string_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="pong")
        result = agent_ping(mock_client, node="pve", vmid=100, confirm=True)
        assert "pong" in result


class TestAgentInfo:
    def test_agent_info_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"version": "5.0.1"}})
        result = agent_info(mock_client, node="pve", vmid=100)
        assert "100" in result
        assert "version" in result

    def test_agent_info_no_confirm_needed(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"version": "5.0.1"}})
        result = agent_info(mock_client, node="pve", vmid=100)
        assert "info" in result.lower()


class TestAgentNetworkInterfaces:
    def test_agent_network_interfaces_success(self, mock_client):
        iface_data = [
            {
                "name": "eth0",
                "hardware-address": "52:54:00:12:34:56",
                "ip-addresses": [
                    {"ip-address": "192.168.1.10", "prefix": 24, "ip-address-type": "ipv4"}
                ],
            }
        ]
        mock_client.safe_api_call = MagicMock(return_value={"data": iface_data})
        result = agent_network_interfaces(mock_client, node="pve", vmid=100)
        assert "eth0" in result
        assert "192.168.1.10" in result
        assert "52:54:00:12:34:56" in result

    def test_agent_network_interfaces_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": []})
        result = agent_network_interfaces(mock_client, node="pve", vmid=100)
        assert "100" in result

    def test_agent_network_interfaces_string_response(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="no data")
        result = agent_network_interfaces(mock_client, node="pve", vmid=100)
        assert "100" in result


class TestAgentOsinfo:
    def test_agent_osinfo_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value={"data": {"kernel-release": "5.15.0", "os": "linux"}}
        )
        result = agent_osinfo(mock_client, node="pve", vmid=100)
        assert "100" in result
        assert "kernel-release" in result

    def test_agent_osinfo_string_response(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="raw")
        result = agent_osinfo(mock_client, node="pve", vmid=100)
        assert "100" in result


class TestAgentFsinfo:
    def test_agent_fsinfo_success(self, mock_client):
        fs_data = [
            {
                "name": "sda1",
                "type": "ext4",
                "mountpoint": "/",
                "total-bytes": 107374182400,
                "used-bytes": 53687091200,
                "free-bytes": 53687091200,
            }
        ]
        mock_client.safe_api_call = MagicMock(return_value={"data": fs_data})
        result = agent_fsinfo(mock_client, node="pve", vmid=100)
        assert "100" in result
        assert "/" in result
        assert "ext4" in result

    def test_agent_fsinfo_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": []})
        result = agent_fsinfo(mock_client, node="pve", vmid=100)
        assert "100" in result

    def test_agent_fsinfo_string_response(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="raw")
        result = agent_fsinfo(mock_client, node="pve", vmid=100)
        assert "100" in result


class TestAgentExecStatus:
    def test_agent_exec_status_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value={"data": {"exited": True, "exitcode": 0, "signal": 0}}
        )
        result = agent_exec_status(mock_client, node="pve", vmid=100, pid=1234)
        assert "1234" in result
        assert "exited" in result

    def test_agent_exec_status_requires_pid(self, mock_client):
        with pytest.raises(ValueError, match="pid is required"):
            agent_exec_status(mock_client, node="pve", vmid=100)

    def test_agent_exec_status_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(
            return_value={"data": {"exited": True}}
        )
        result = agent_exec_status(mock_client, vmid=100, pid=5678)
        assert "pve" in result


class TestAgentFsfreeze:
    def test_agent_fsfreeze_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": 3})
        result = agent_fsfreeze(mock_client, node="pve", vmid=100, confirm=True)
        assert "frozen" in result.lower()
        assert "100" in result

    def test_agent_fsfreeze_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_fsfreeze(mock_client, node="pve", vmid=100, confirm=False)

    def test_agent_fsfreeze_string_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="3")
        result = agent_fsfreeze(mock_client, node="pve", vmid=100, confirm=True)
        assert "3" in result


class TestAgentFsthaw:
    def test_agent_fsthaw_success(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": 3})
        result = agent_fsthaw(mock_client, node="pve", vmid=100, confirm=True)
        assert "thawed" in result.lower()
        assert "100" in result

    def test_agent_fsthaw_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            agent_fsthaw(mock_client, node="pve", vmid=100, confirm=False)

    def test_agent_fsthaw_string_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="3")
        result = agent_fsthaw(mock_client, node="pve", vmid=100, confirm=True)
        assert "3" in result


class TestCloudinitDump:
    def test_cloudinit_dump_basic(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "#cloud-config\nusers:\n  - name: admin"})
        result = cloudinit_dump(mock_client, node="pve", vmid=100)
        assert "cloud" in result.lower() or "admin" in result

    def test_cloudinit_dump_with_type(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "network config"})
        cloudinit_dump(mock_client, node="pve", vmid=100, type="network")
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1].get("type") == "network"

    def test_cloudinit_dump_string_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="plain text config")
        result = cloudinit_dump(mock_client, node="pve", vmid=100)
        assert "plain text config" in result

    def test_cloudinit_dump_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "config"})
        result = cloudinit_dump(mock_client, vmid=100)
        assert result is not None

    def test_cloudinit_dump_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            cloudinit_dump(mock_client, node="invalid!node", vmid=100)
