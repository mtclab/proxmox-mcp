from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.ceph import (
    ceph_cfg_db,
    ceph_cfg_value,
    ceph_config,
    ceph_crush,
    ceph_flags,
    ceph_log,
    ceph_metadata,
    ceph_osd_in,
    ceph_osd_metadata,
    ceph_osd_out,
    ceph_osd_scrub,
    ceph_pool_status,
    ceph_status,
    create_ceph_fs,
    create_ceph_mds,
    create_ceph_mgr,
    create_ceph_mon,
    create_ceph_osd,
    create_ceph_pool,
    destroy_ceph_mds,
    destroy_ceph_mgr,
    destroy_ceph_mon,
    destroy_ceph_osd,
    destroy_ceph_pool,
    get_ceph_flag,
    get_ceph_pool,
    init_ceph,
    list_ceph_mds_detail,
    list_ceph_mgr,
    list_ceph_mon,
    list_ceph_osd,
    list_ceph_osd_detail,
    list_ceph_pools,
    node_ceph_fs,
    node_ceph_status,
    restart_ceph,
    set_ceph_flag,
    set_ceph_flags,
    start_ceph,
    stop_ceph,
    update_ceph_pool,
)
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
    client.admin_client = MagicMock()
    client.monitor_client = MagicMock()
    return client


class TestCephStatus:
    async def test_ceph_status_full(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "health": {"status": "HEALTH_OK", "summary": "all is fine"},
                "fsid": "abc-123",
                "quorum": ["mon1", "mon2", "mon3"],
                "osdmap": {"osdmap": {"num_osds": 6, "num_up_osds": 6}},
                "pgmap": {"num_pgs": 192, "bytes_used": 1073741824, "bytes_total": 10737418240},
            }
        )
        result = await ceph_status(mock_client)
        assert "HEALTH_OK" in result
        assert "abc-123" in result
        assert "3" in result
        assert "6" in result

    async def test_ceph_status_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await ceph_status(mock_client)
        assert "Ceph Cluster Status" in result

    async def test_ceph_status_not_configured(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_status(mock_client)
        assert "No Ceph status" in result

    async def test_ceph_status_health_detail(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "health": {"status": "HEALTH_WARN"},
                "fsid": "def-456",
            }
        )
        result = await ceph_status(mock_client)
        assert "HEALTH_WARN" in result


class TestCephMetadata:
    async def test_ceph_metadata_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "version": "17.2.0",
                "release": "quincy",
            }
        )
        result = await ceph_metadata(mock_client)
        assert "version" in result
        assert "17.2.0" in result

    async def test_ceph_metadata_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "osd.0", "status": "up"},
                {"name": "osd.1", "status": "up"},
            ]
        )
        result = await ceph_metadata(mock_client)
        assert "osd.0" in result

    async def test_ceph_metadata_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await ceph_metadata(mock_client)
        assert "No Ceph metadata" in result


class TestNodeCephStatus:
    async def test_node_ceph_status(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "health": {"status": "HEALTH_OK"},
                "fsid": "abc-123",
                "quorum": ["mon1"],
                "osdmap": {"osdmap": {"num_osds": 3, "num_up_osds": 3}},
            }
        )
        result = await node_ceph_status(mock_client, node="pve")
        assert "pve" in result
        assert "HEALTH_OK" in result
        mock_client.safe_api_call.assert_called_once()

    async def test_node_ceph_status_resolves_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"health": {"status": "HEALTH_OK"}})
        result = await node_ceph_status(mock_client, node=None)
        assert "pve" in result

    async def test_node_ceph_status_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await node_ceph_status(mock_client, node="bad node!")

    async def test_node_ceph_status_empty_response(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={})
        result = await node_ceph_status(mock_client, node="pve")
        assert "Ceph Status" in result


class TestNodeCephFs:
    async def test_node_ceph_fs_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "cephfs", "metadata_pool": "2", "data_pool": "1"},
            ]
        )
        result = await node_ceph_fs(mock_client, node="pve")
        assert "cephfs" in result
        assert "Ceph Filesystems" in result

    async def test_node_ceph_fs_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await node_ceph_fs(mock_client, node="pve")
        assert "No Ceph filesystems" in result

    async def test_node_ceph_fs_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await node_ceph_fs(mock_client, node="bad!")


class TestCreateCephFs:
    async def test_create_ceph_fs_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await create_ceph_fs(mock_client, node="pve", name="myfs")

    async def test_create_ceph_fs_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_ceph_fs(mock_client, node="pve", name="", confirm=True)


class TestListCephOsd:
    async def test_list_ceph_osd_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": 0, "name": "osd.0", "status": "up", "host": "pve"},
            ]
        )
        result = await list_ceph_osd(mock_client, node="pve")
        assert "OSD 0" in result
        assert "up" in result

    async def test_list_ceph_osd_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_ceph_osd(mock_client, node="pve")
        assert "No Ceph OSDs" in result


class TestListCephMon:
    async def test_list_ceph_mon_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "pve", "addr": "10.0.0.1:6789", "rank": 0},
            ]
        )
        result = await list_ceph_mon(mock_client, node="pve")
        assert "pve" in result
        assert "10.0.0.1" in result

    async def test_list_ceph_mon_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_ceph_mon(mock_client, node="pve")
        assert "No Ceph monitors" in result


class TestListCephMgr:
    async def test_list_ceph_mgr_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "pve", "addr": "10.0.0.1:6800", "state": "active"},
            ]
        )
        result = await list_ceph_mgr(mock_client, node="pve")
        assert "pve" in result
        assert "active" in result

    async def test_list_ceph_mgr_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_ceph_mgr(mock_client, node="pve")
        assert "No Ceph managers" in result


class TestCephConfig:
    async def test_ceph_config_string(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "[global]\nmon_host = pve"})
        result = await ceph_config(mock_client, node="pve")
        assert "Ceph Configuration" in result

    async def test_ceph_config_none(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_config(mock_client, node="pve")
        assert "No Ceph configuration" in result


class TestCephFlags:
    async def test_ceph_flags_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "noout": True,
                "nobalance": False,
            }
        )
        result = await ceph_flags(mock_client)
        assert "Ceph Cluster Flags" in result
        assert "noout" in result

    async def test_ceph_flags_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_flags(mock_client)
        assert "No Ceph flags" in result

    async def test_ceph_flags_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "noout", "value": True},
            ]
        )
        result = await ceph_flags(mock_client)
        assert "noout" in result


class TestSetCephFlags:
    async def test_set_ceph_flags_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await set_ceph_flags(mock_client, flags="noout", confirm=False)

    async def test_set_ceph_flags_requires_flags(self, mock_client):
        with pytest.raises(ValueError, match="Flags string is required"):
            await set_ceph_flags(mock_client, flags="", confirm=True)


class TestGetCephFlag:
    async def test_get_ceph_flag_requires_flag(self, mock_client):
        with pytest.raises(ValueError, match="Flag name is required"):
            await get_ceph_flag(mock_client, flag="")

    async def test_get_ceph_flag_bool(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=True)
        result = await get_ceph_flag(mock_client, flag="noout")
        assert "noout" in result

    async def test_get_ceph_flag_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"value": True}})
        result = await get_ceph_flag(mock_client, flag="noout")
        assert "noout" in result


class TestSetCephFlag:
    async def test_set_ceph_flag_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await set_ceph_flag(mock_client, flag="noout", value="1", confirm=False)

    async def test_set_ceph_flag_requires_flag(self, mock_client):
        with pytest.raises(ValueError, match="Flag name is required"):
            await set_ceph_flag(mock_client, flag="", value="1", confirm=True)


class TestListCephOsdDetail:
    async def test_list_ceph_osd_detail(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"id": 0, "host": "pve", "state": "up"},
            }
        )
        result = await list_ceph_osd_detail(mock_client, node="pve", osdid=0)
        assert "OSD 0" in result

    async def test_list_ceph_osd_detail_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            await list_ceph_osd_detail(mock_client, node="bad!", osdid=0)


class TestCreateCephOsd:
    async def test_create_ceph_osd_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await create_ceph_osd(mock_client, node="pve", dev="/dev/sdb")

    async def test_create_ceph_osd_requires_dev(self, mock_client):
        with pytest.raises(ValueError, match="Device path is required"):
            await create_ceph_osd(mock_client, node="pve", dev="", confirm=True)


class TestDestroyCephOsd:
    async def test_destroy_ceph_osd_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await destroy_ceph_osd(mock_client, node="pve", osdid=0)


class TestCephOsdIn:
    async def test_ceph_osd_in_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await ceph_osd_in(mock_client, node="pve", osdid=0)


class TestCephOsdOut:
    async def test_ceph_osd_out_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await ceph_osd_out(mock_client, node="pve", osdid=0)


class TestCephOsdScrub:
    async def test_ceph_osd_scrub_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await ceph_osd_scrub(mock_client, node="pve", osdid=0)


class TestCephOsdMetadata:
    async def test_ceph_osd_metadata_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"id": 0, "host": "pve"},
            }
        )
        result = await ceph_osd_metadata(mock_client, node="pve", osdid=0)
        assert "OSD 0" in result

    async def test_ceph_osd_metadata_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_osd_metadata(mock_client, node="pve", osdid=0)
        assert "No OSD metadata" in result


class TestListCephPools:
    async def test_list_ceph_pools_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"pool_name": "rbd", "pg_num": 64, "size": 3},
            ]
        )
        result = await list_ceph_pools(mock_client, node="pve")
        assert "rbd" in result
        assert "Ceph Pools" in result

    async def test_list_ceph_pools_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_ceph_pools(mock_client, node="pve")
        assert "No Ceph pools" in result


class TestCreateCephPool:
    async def test_create_ceph_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await create_ceph_pool(mock_client, node="pve", name="test")

    async def test_create_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            await create_ceph_pool(mock_client, node="pve", name="", confirm=True)


class TestGetCephPool:
    async def test_get_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            await get_ceph_pool(mock_client, node="pve", name="")

    async def test_get_ceph_pool_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"pool_name": "rbd", "pg_num": 64},
            }
        )
        result = await get_ceph_pool(mock_client, node="pve", name="rbd")
        assert "rbd" in result


class TestUpdateCephPool:
    async def test_update_ceph_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await update_ceph_pool(mock_client, node="pve", name="rbd")

    async def test_update_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            await update_ceph_pool(mock_client, node="pve", name="", confirm=True)


class TestDestroyCephPool:
    async def test_destroy_ceph_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await destroy_ceph_pool(mock_client, node="pve", name="rbd")

    async def test_destroy_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            await destroy_ceph_pool(mock_client, node="pve", name="", confirm=True)


class TestCephPoolStatus:
    async def test_ceph_pool_status_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            await ceph_pool_status(mock_client, node="pve", name="")

    async def test_ceph_pool_status_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"bytes_used": 1000, "percent_used": 10.0},
            }
        )
        result = await ceph_pool_status(mock_client, node="pve", name="rbd")
        assert "rbd" in result


class TestListCephMdsDetail:
    async def test_list_ceph_mds_detail_with_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "pve", "state": "active", "rank": 0},
            ]
        )
        result = await list_ceph_mds_detail(mock_client, node="pve")
        assert "pve" in result
        assert "active" in result

    async def test_list_ceph_mds_detail_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_ceph_mds_detail(mock_client, node="pve")
        assert "No Ceph MDS" in result


class TestCreateCephMds:
    async def test_create_ceph_mds_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await create_ceph_mds(mock_client, node="pve", name="mds0")

    async def test_create_ceph_mds_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="MDS name is required"):
            await create_ceph_mds(mock_client, node="pve", name="", confirm=True)


class TestDestroyCephMds:
    async def test_destroy_ceph_mds_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await destroy_ceph_mds(mock_client, node="pve", name="mds0")

    async def test_destroy_ceph_mds_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="MDS name is required"):
            await destroy_ceph_mds(mock_client, node="pve", name="", confirm=True)


class TestCreateCephMgr:
    async def test_create_ceph_mgr_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await create_ceph_mgr(mock_client, node="pve", id="mgr0")

    async def test_create_ceph_mgr_requires_id(self, mock_client):
        with pytest.raises(ValueError, match="MGR id is required"):
            await create_ceph_mgr(mock_client, node="pve", id="", confirm=True)


class TestDestroyCephMgr:
    async def test_destroy_ceph_mgr_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await destroy_ceph_mgr(mock_client, node="pve", id="mgr0")

    async def test_destroy_ceph_mgr_requires_id(self, mock_client):
        with pytest.raises(ValueError, match="MGR id is required"):
            await destroy_ceph_mgr(mock_client, node="pve", id="", confirm=True)


class TestCreateCephMon:
    async def test_create_ceph_mon_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await create_ceph_mon(mock_client, node="pve", monid="mon0")

    async def test_create_ceph_mon_requires_monid(self, mock_client):
        with pytest.raises(ValueError, match="Monitor id is required"):
            await create_ceph_mon(mock_client, node="pve", monid="", confirm=True)


class TestDestroyCephMon:
    async def test_destroy_ceph_mon_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await destroy_ceph_mon(mock_client, node="pve", monid="mon0")

    async def test_destroy_ceph_mon_requires_monid(self, mock_client):
        with pytest.raises(ValueError, match="Monitor id is required"):
            await destroy_ceph_mon(mock_client, node="pve", monid="", confirm=True)


class TestStartCeph:
    async def test_start_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await start_ceph(mock_client, node="pve")


class TestStopCeph:
    async def test_stop_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await stop_ceph(mock_client, node="pve")


class TestRestartCeph:
    async def test_restart_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await restart_ceph(mock_client, node="pve")


class TestCephCfgDb:
    async def test_ceph_cfg_db_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": [{"key": "mon_host", "value": "10.0.0.1"}],
            }
        )
        result = await ceph_cfg_db(mock_client, node="pve")
        assert "Config DB" in result

    async def test_ceph_cfg_db_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"mon_host": "10.0.0.1"},
            }
        )
        result = await ceph_cfg_db(mock_client, node="pve")
        assert "Config DB" in result

    async def test_ceph_cfg_db_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_cfg_db(mock_client, node="pve")
        assert "No Ceph config DB" in result


class TestCephCfgValue:
    async def test_ceph_cfg_value_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"mon_host": "10.0.0.1"},
            }
        )
        result = await ceph_cfg_value(mock_client, node="pve")
        assert "Config Value" in result

    async def test_ceph_cfg_value_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_cfg_value(mock_client, node="pve")
        assert "No config value" in result


class TestCephCrush:
    async def test_ceph_crush_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": {"root": "default", "rules": 2},
            }
        )
        result = await ceph_crush(mock_client, node="pve")
        assert "CRUSH" in result

    async def test_ceph_crush_string(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="crush map data")
        result = await ceph_crush(mock_client, node="pve")
        assert "CRUSH" in result

    async def test_ceph_crush_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_crush(mock_client, node="pve")
        assert "No CRUSH map" in result


class TestCephLog:
    async def test_ceph_log_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"timestamp": "2024-01-01", "message": "osd.0 up"},
            ]
        )
        result = await ceph_log(mock_client, node="pve")
        assert "Ceph Log" in result
        assert "osd.0 up" in result

    async def test_ceph_log_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": [{"timestamp": "2024-01-01", "message": "osd.0 down"}],
            }
        )
        result = await ceph_log(mock_client, node="pve")
        assert "Ceph Log" in result

    async def test_ceph_log_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await ceph_log(mock_client, node="pve")
        assert "No Ceph log" in result


class TestInitCeph:
    async def test_init_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            await init_ceph(mock_client, node="pve")


class TestElevatedEnforcement:
    async def test_create_ceph_osd_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await create_ceph_osd(mock_client, node="pve", dev="/dev/sdb", confirm=True)

    async def test_destroy_ceph_osd_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await destroy_ceph_osd(mock_client, node="pve", osdid=0, confirm=True)

    async def test_ceph_osd_in_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await ceph_osd_in(mock_client, node="pve", osdid=0, confirm=True)

    async def test_ceph_osd_out_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await ceph_osd_out(mock_client, node="pve", osdid=0, confirm=True)

    async def test_ceph_osd_scrub_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await ceph_osd_scrub(mock_client, node="pve", osdid=0, confirm=True)

    async def test_create_ceph_pool_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await create_ceph_pool(mock_client, node="pve", name="test", confirm=True)

    async def test_update_ceph_pool_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await update_ceph_pool(mock_client, node="pve", name="test", confirm=True)

    async def test_destroy_ceph_pool_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await destroy_ceph_pool(mock_client, node="pve", name="test", confirm=True)

    async def test_create_ceph_mds_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await create_ceph_mds(mock_client, node="pve", name="test", confirm=True)

    async def test_destroy_ceph_mds_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await destroy_ceph_mds(mock_client, node="pve", name="test", confirm=True)

    async def test_create_ceph_mgr_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await create_ceph_mgr(mock_client, node="pve", id="test", confirm=True)

    async def test_destroy_ceph_mgr_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await destroy_ceph_mgr(mock_client, node="pve", id="test", confirm=True)

    async def test_create_ceph_mon_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await create_ceph_mon(mock_client, node="pve", monid="test", confirm=True)

    async def test_destroy_ceph_mon_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await destroy_ceph_mon(mock_client, node="pve", monid="test", confirm=True)

    async def test_start_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await start_ceph(mock_client, node="pve", confirm=True)

    async def test_stop_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await stop_ceph(mock_client, node="pve", confirm=True)

    async def test_restart_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await restart_ceph(mock_client, node="pve", confirm=True)

    async def test_set_ceph_flags_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await set_ceph_flags(mock_client, flags="noout", confirm=True)

    async def test_set_ceph_flag_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await set_ceph_flag(mock_client, flag="noout", value="1", confirm=True)

    async def test_init_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            await init_ceph(mock_client, node="pve", confirm=True)
