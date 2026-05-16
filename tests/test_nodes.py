from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.nodes import (
    extract_backup_config,
    get_network_interface,
    get_node_detailed_status,
    get_subscription,
    list_services,
    migrate_all,
    node_config,
    node_dns,
    node_execute,
    node_hosts,
    node_netstat,
    node_report,
    reboot_node,
    restart_service,
    scan_cifs,
    scan_iscsi,
    scan_lvm,
    scan_lvmthin,
    scan_nfs,
    scan_pbs,
    scan_zfs,
    service_state,
    shutdown_node,
    start_all,
    start_service,
    stop_all,
    stop_service,
    suspend_all,
    update_dns,
    update_hosts,
    update_node_config,
    update_subscription,
    update_time,
    vzdump_defaults,
)


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


class TestConfirmRequired:
    async def test_reboot_node_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await reboot_node(mock_client, node="pve")

    async def test_shutdown_node_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await shutdown_node(mock_client, node="pve")

    async def test_start_all_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await start_all(mock_client, node="pve")

    async def test_stop_all_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await stop_all(mock_client, node="pve")

    async def test_update_node_config_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_node_config(mock_client, node="pve", description="test")

    async def test_start_service_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await start_service(mock_client, node="pve", service="sshd")

    async def test_stop_service_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await stop_service(mock_client, node="pve", service="sshd")

    async def test_restart_service_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await restart_service(mock_client, node="pve", service="sshd")


class TestElevatedCheck:
    async def test_reboot_node_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await reboot_node(client, node="pve", confirm=True)

    async def test_shutdown_node_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await shutdown_node(client, node="pve", confirm=True)

    async def test_start_all_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await start_all(client, node="pve", confirm=True)

    async def test_stop_all_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await stop_all(client, node="pve", confirm=True)

    async def test_update_node_config_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_node_config(client, node="pve", description="test", confirm=True)

    async def test_start_service_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await start_service(client, node="pve", service="sshd", confirm=True)

    async def test_stop_service_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await stop_service(client, node="pve", service="sshd", confirm=True)

    async def test_restart_service_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await restart_service(client, node="pve", service="sshd", confirm=True)


class TestNodeConfig:
    async def test_node_config_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "keyboard": "en-us",
                "timezone": "UTC",
                "description": "Test node",
            }
        )
        result = await node_config(mock_client, node="pve")
        assert "pve" in result
        assert "keyboard" in result
        assert "timezone" in result

    async def test_node_config_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await node_config(mock_client, node="pve")
        assert "pve" in result


class TestUpdateNodeConfig:
    async def test_update_with_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0400:abc"})
        result = await update_node_config(
            mock_client,
            node="pve",
            description="updated",
            keyboard="en-us",
            time_zone="UTC",
            confirm=True,
        )
        assert "updated" in result
        assert "UPID" in result

    async def test_update_no_params(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0401:abc"})
        result = await update_node_config(mock_client, node="pve", confirm=True)
        assert "UPID" in result


class TestRebootNode:
    async def test_reboot_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0500:reboot")
        result = await reboot_node(mock_client, node="pve", confirm=True)
        assert "reboot" in result
        assert "UPID" in result


class TestShutdownNode:
    async def test_shutdown_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0501:shutdown")
        result = await shutdown_node(mock_client, node="pve", confirm=True)
        assert "shutdown" in result
        assert "UPID" in result


class TestStartAll:
    async def test_start_all_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0502:startall")
        result = await start_all(mock_client, node="pve", confirm=True)
        assert "Start all" in result
        assert "UPID" in result


class TestStopAll:
    async def test_stop_all_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0503:stopall")
        result = await stop_all(mock_client, node="pve", confirm=True)
        assert "Stop all" in result
        assert "UPID" in result


class TestListServices:
    async def test_list_services_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"service": "sshd", "state": "running", "description": "SSH daemon"},
                {"service": "pveproxy", "state": "running"},
            ]
        )
        result = await list_services(mock_client, node="pve")
        assert "sshd" in result
        assert "pveproxy" in result

    async def test_list_services_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_services(mock_client, node="pve")
        assert "No services found" in result


class TestServiceState:
    async def test_service_state_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "state": "running",
                "pid": 1234,
            }
        )
        result = await service_state(mock_client, node="pve", service="sshd")
        assert "sshd" in result
        assert "running" in result

    async def test_service_state_no_service_raises(self, mock_client):
        with pytest.raises(ValueError, match="service is required"):
            await service_state(mock_client, node="pve", service="")


class TestStartService:
    async def test_start_service_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0600:start")
        result = await start_service(mock_client, node="pve", service="sshd", confirm=True)
        assert "sshd" in result
        assert "UPID" in result

    async def test_start_service_no_service_raises(self, mock_client):
        with pytest.raises(ValueError, match="service is required"):
            await start_service(mock_client, node="pve", service="", confirm=True)


class TestStopService:
    async def test_stop_service_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0601:stop")
        result = await stop_service(mock_client, node="pve", service="sshd", confirm=True)
        assert "sshd" in result
        assert "UPID" in result

    async def test_stop_service_no_service_raises(self, mock_client):
        with pytest.raises(ValueError, match="service is required"):
            await stop_service(mock_client, node="pve", service="", confirm=True)


class TestRestartService:
    async def test_restart_service_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0602:restart")
        result = await restart_service(mock_client, node="pve", service="sshd", confirm=True)
        assert "sshd" in result
        assert "UPID" in result

    async def test_restart_service_no_service_raises(self, mock_client):
        with pytest.raises(ValueError, match="service is required"):
            await restart_service(mock_client, node="pve", service="", confirm=True)


class TestNodeDns:
    async def test_node_dns_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "dns1": "8.8.8.8",
                "dns2": "8.8.4.4",
                "search": "local",
            }
        )
        result = await node_dns(mock_client, node="pve")
        assert "pve" in result
        assert "8.8.8.8" in result

    async def test_node_dns_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await node_dns(mock_client, node="pve")
        assert "pve" in result


class TestNodeHosts:
    async def test_node_hosts_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": "127.0.0.1 localhost\n10.0.0.1 pve",
            }
        )
        result = await node_hosts(mock_client, node="pve")
        assert "pve" in result
        assert "localhost" in result

    async def test_node_hosts_dict_format(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "digest": "abc123",
            }
        )
        result = await node_hosts(mock_client, node="pve")
        assert "pve" in result


class TestNodeReport:
    async def test_node_report_dict_format(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": "line1\nline2\nline3",
            }
        )
        result = await node_report(mock_client, node="pve")
        assert "Report" in result
        assert "line1" in result

    async def test_node_report_string_format(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="line1\nline2\nline3")
        result = await node_report(mock_client, node="pve")
        assert "Report" in result
        assert "line1" in result

    async def test_node_report_dict_no_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"key1": "val1"})
        result = await node_report(mock_client, node="pve")
        assert "pve" in result


class TestNodeNetstat:
    async def test_node_netstat_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "eth0", "rx_bytes": 1000, "tx_bytes": 500},
                {"name": "eth1", "rx_bytes": 2000, "tx_bytes": 1000},
            ]
        )
        result = await node_netstat(mock_client, node="pve")
        assert "Netstat" in result
        assert "eth0" in result
        assert "eth1" in result

    async def test_node_netstat_dict_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": [{"name": "eth0", "rx_bytes": 1000}],
            }
        )
        result = await node_netstat(mock_client, node="pve")
        assert "Netstat" in result
        assert "eth0" in result

    async def test_node_netstat_dict_plain(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"key1": "val1"})
        result = await node_netstat(mock_client, node="pve")
        assert "Netstat" in result

    async def test_node_netstat_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await node_netstat(mock_client, node="pve")
        assert "No network stats available" in result


class TestUpdateDns:
    async def test_update_dns_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_dns(mock_client, node="pve", dns1="8.8.8.8")

    async def test_update_dns_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_dns(client, node="pve", dns1="8.8.8.8", confirm=True)

    async def test_update_dns_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await update_dns(mock_client, node="pve", confirm=True)

    async def test_update_dns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_dns(mock_client, node="pve", dns1="8.8.8.8", confirm=True)
        assert "pve" in result
        assert "updated" in result.lower()


class TestUpdateHosts:
    async def test_update_hosts_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_hosts(mock_client, node="pve", data="127.0.0.1 localhost")

    async def test_update_hosts_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_hosts(client, node="pve", data="127.0.0.1 localhost", confirm=True)

    async def test_update_hosts_no_data_raises(self, mock_client):
        with pytest.raises(ValueError, match="data is required"):
            await update_hosts(mock_client, node="pve", data="", confirm=True)

    async def test_update_hosts(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_hosts(mock_client, node="pve", data="127.0.0.1 localhost", confirm=True)
        assert "pve" in result
        assert "updated" in result.lower()


class TestUpdateTime:
    async def test_update_time_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_time(mock_client, node="pve", timezone="America/New_York")

    async def test_update_time_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_time(client, node="pve", timezone="America/New_York", confirm=True)

    async def test_update_time_no_timezone_raises(self, mock_client):
        with pytest.raises(ValueError, match="timezone is required"):
            await update_time(mock_client, node="pve", timezone="", confirm=True)

    async def test_update_time(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_time(mock_client, node="pve", timezone="America/New_York", confirm=True)
        assert "pve" in result
        assert "America/New_York" in result
        assert "updated" in result.lower()


class TestVzdumpDefaults:
    async def test_vzdump_defaults(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"storage": "local", "mode": "snapshot"},
            }
        )
        result = await vzdump_defaults(mock_client, node="pve")
        assert "pve" in result
        assert "VZDump" in result

    async def test_vzdump_defaults_with_storage(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"storage": "nfs-backup", "mode": "stop"},
            }
        )
        result = await vzdump_defaults(mock_client, node="pve", storage="nfs-backup")
        assert "pve" in result


class TestExtractBackupConfig:
    async def test_extract_backup_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"cores": 2, "memory": 4096},
            }
        )
        result = await extract_backup_config(mock_client, node="pve", archive="local:backup/vzdump-qemu-100.vma.zst")
        assert "pve" in result
        assert "Backup Config" in result

    async def test_extract_backup_config_no_archive_raises(self, mock_client):
        with pytest.raises(ValueError, match="archive is required"):
            await extract_backup_config(mock_client, node="pve", archive="")


class TestScanNfs:
    async def test_scan_nfs_returns_results(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"path": "/export/data", "type": "NFS"},
            ]
        )
        result = await scan_nfs(mock_client, node="pve", server="nas.local")
        assert "nas.local" in result
        assert "/export/data" in result

    async def test_scan_nfs_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await scan_nfs(mock_client, node="pve", server="nas.local")
        assert "No NFS exports" in result

    async def test_scan_nfs_no_server_raises(self, mock_client):
        with pytest.raises(ValueError, match="server is required"):
            await scan_nfs(mock_client, node="pve", server="")


class TestScanIscsi:
    async def test_scan_iscsi_returns_results(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"target": "iqn.2024.example:storage"},
            ]
        )
        result = await scan_iscsi(mock_client, node="pve", server="iscsi.local")
        assert "iscsi.local" in result
        assert "iqn.2024.example:storage" in result

    async def test_scan_iscsi_no_server_raises(self, mock_client):
        with pytest.raises(ValueError, match="server is required"):
            await scan_iscsi(mock_client, node="pve", server="")


class TestScanLvm:
    async def test_scan_lvm_returns_results(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"vg": "vg0"},
            ]
        )
        result = await scan_lvm(mock_client, node="pve")
        assert "vg0" in result

    async def test_scan_lvm_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await scan_lvm(mock_client, node="pve")
        assert "No LVM" in result


class TestScanLvmthin:
    async def test_scan_lvmthin_returns_results(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"vg": "vg0-thin"},
            ]
        )
        result = await scan_lvmthin(mock_client, node="pve")
        assert "vg0-thin" in result

    async def test_scan_lvmthin_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await scan_lvmthin(mock_client, node="pve")
        assert "No LVM thin" in result


class TestScanCifs:
    async def test_scan_cifs_returns_results(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"share": "backup", "description": "Backup share"},
            ]
        )
        result = await scan_cifs(mock_client, node="pve", server="smb.local")
        assert "smb.local" in result
        assert "backup" in result

    async def test_scan_cifs_no_server_raises(self, mock_client):
        with pytest.raises(ValueError, match="server is required"):
            await scan_cifs(mock_client, node="pve", server="")


class TestScanZfs:
    async def test_scan_zfs_returns_results(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"pool": "tank"},
            ]
        )
        result = await scan_zfs(mock_client, node="pve")
        assert "tank" in result

    async def test_scan_zfs_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await scan_zfs(mock_client, node="pve")
        assert "No ZFS" in result


class TestScanPbs:
    async def test_scan_pbs_returns_results(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"store": "backup-data"},
            ]
        )
        result = await scan_pbs(mock_client, node="pve", server="pbs.local")
        assert "pbs.local" in result
        assert "backup-data" in result

    async def test_scan_pbs_no_server_raises(self, mock_client):
        with pytest.raises(ValueError, match="server is required"):
            await scan_pbs(mock_client, node="pve", server="")


class TestGetSubscription:
    async def test_get_subscription_returns_info(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"status": "Active", "key": "pve123"},
            }
        )
        result = await get_subscription(mock_client, node="pve")
        assert "pve" in result
        assert "Active" in result

    async def test_get_subscription_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await get_subscription(mock_client, node="pve")
        assert "pve" in result


class TestUpdateSubscription:
    async def test_update_subscription_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_subscription(mock_client, node="pve", key="test-key")

    async def test_update_subscription_no_key_raises(self, mock_client):
        with pytest.raises(ValueError, match="key is required"):
            await update_subscription(mock_client, node="pve", key="", confirm=True)

    async def test_update_subscription_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:0700:sub"})
        result = await update_subscription(mock_client, node="pve", key="pve-key", confirm=True)
        assert "UPID" in result


class TestNodeExecute:
    async def test_execute_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await node_execute(mock_client, node="pve", commands="ls")

    async def test_execute_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await node_execute(client, node="pve", commands="ls", confirm=True)

    async def test_execute_no_commands_raises(self, mock_client):
        with pytest.raises(ValueError, match="commands is required"):
            await node_execute(mock_client, node="pve", commands=None, confirm=True)

    async def test_execute_returns_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"exitcode": 0}})
        result = await node_execute(mock_client, node="pve", commands="ls", confirm=True)
        assert "pve" in result


class TestGetNetworkInterface:
    async def test_get_network_interface_returns_info(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "iface": "vmbr0",
                "type": "bridge",
                "active": 1,
            }
        )
        result = await get_network_interface(mock_client, node="pve", iface="vmbr0")
        assert "vmbr0" in result

    async def test_get_network_interface_no_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="iface is required"):
            await get_network_interface(mock_client, node="pve", iface="")

    async def test_get_network_interface_invalid_iface_raises(self, mock_client):
        with pytest.raises(ValueError, match="Invalid interface"):
            await get_network_interface(mock_client, node="pve", iface="bad!iface")


class TestSuspendAll:
    async def test_suspend_all_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await suspend_all(mock_client, node="pve")

    async def test_suspend_all_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0603:suspendall")
        result = await suspend_all(mock_client, node="pve", confirm=True)
        assert "Suspend all" in result
        assert "UPID" in result

    async def test_suspend_all_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await suspend_all(client, node="pve", confirm=True)


class TestMigrateAll:
    async def test_migrate_all_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await migrate_all(mock_client, node="pve")

    async def test_migrate_all_returns_upid(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:0604:migrateall")
        result = await migrate_all(mock_client, node="pve", target="pve2", confirm=True)
        assert "Migrate all" in result
        assert "UPID" in result

    async def test_migrate_all_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await migrate_all(client, node="pve", confirm=True)


class TestGetNodeDetailedStatus:
    async def test_get_detailed_status(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "uptime": 123456,
                "cpu": 0.15,
                "memory": {"total": 32768, "used": 16384},
            }
        )
        result = await get_node_detailed_status(mock_client, node="pve")
        assert "pve" in result
        assert "uptime" in result

    async def test_get_detailed_status_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await get_node_detailed_status(mock_client, node="pve")
        assert "pve" in result
