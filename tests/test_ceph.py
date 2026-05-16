from unittest.mock import MagicMock, patch

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
    def test_ceph_status_full(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "health": {"status": "HEALTH_OK", "summary": "all is fine"},
            "fsid": "abc-123",
            "quorum": ["mon1", "mon2", "mon3"],
            "osdmap": {"osdmap": {"num_osds": 6, "num_up_osds": 6}},
            "pgmap": {"num_pgs": 192, "bytes_used": 1073741824, "bytes_total": 10737418240},
        })
        result = ceph_status(mock_client)
        assert "HEALTH_OK" in result
        assert "abc-123" in result
        assert "3" in result
        assert "6" in result

    def test_ceph_status_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = ceph_status(mock_client)
        assert "Ceph Cluster Status" in result

    def test_ceph_status_not_configured(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_status(mock_client)
        assert "No Ceph status" in result

    def test_ceph_status_health_detail(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "health": {"status": "HEALTH_WARN"},
            "fsid": "def-456",
        })
        result = ceph_status(mock_client)
        assert "HEALTH_WARN" in result


class TestCephMetadata:
    def test_ceph_metadata_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "version": "17.2.0",
            "release": "quincy",
        })
        result = ceph_metadata(mock_client)
        assert "version" in result
        assert "17.2.0" in result

    def test_ceph_metadata_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "osd.0", "status": "up"},
            {"name": "osd.1", "status": "up"},
        ])
        result = ceph_metadata(mock_client)
        assert "osd.0" in result

    def test_ceph_metadata_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = ceph_metadata(mock_client)
        assert "No Ceph metadata" in result


class TestNodeCephStatus:
    def test_node_ceph_status(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "health": {"status": "HEALTH_OK"},
            "fsid": "abc-123",
            "quorum": ["mon1"],
            "osdmap": {"osdmap": {"num_osds": 3, "num_up_osds": 3}},
        })
        result = node_ceph_status(mock_client, node="pve")
        assert "pve" in result
        assert "HEALTH_OK" in result
        mock_client.safe_api_call.assert_called_once()

    def test_node_ceph_status_resolves_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"health": {"status": "HEALTH_OK"}})
        result = node_ceph_status(mock_client, node=None)
        assert "pve" in result

    def test_node_ceph_status_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            node_ceph_status(mock_client, node="bad node!")

    def test_node_ceph_status_empty_response(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={})
        result = node_ceph_status(mock_client, node="pve")
        assert "Ceph Status" in result


class TestNodeCephFs:
    def test_node_ceph_fs_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "cephfs", "metadata_pool": "2", "data_pool": "1"},
        ])
        result = node_ceph_fs(mock_client, node="pve")
        assert "cephfs" in result
        assert "Ceph Filesystems" in result

    def test_node_ceph_fs_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = node_ceph_fs(mock_client, node="pve")
        assert "No Ceph filesystems" in result

    def test_node_ceph_fs_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            node_ceph_fs(mock_client, node="bad!")


class TestCreateCephFs:
    def test_create_ceph_fs_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            create_ceph_fs(mock_client, node="pve", name="myfs")

    def test_create_ceph_fs_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            create_ceph_fs(mock_client, node="pve", name="", confirm=True)


class TestListCephOsd:
    def test_list_ceph_osd_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": 0, "name": "osd.0", "status": "up", "host": "pve"},
        ])
        result = list_ceph_osd(mock_client, node="pve")
        assert "OSD 0" in result
        assert "up" in result

    def test_list_ceph_osd_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ceph_osd(mock_client, node="pve")
        assert "No Ceph OSDs" in result


class TestListCephMon:
    def test_list_ceph_mon_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "pve", "addr": "10.0.0.1:6789", "rank": 0},
        ])
        result = list_ceph_mon(mock_client, node="pve")
        assert "pve" in result
        assert "10.0.0.1" in result

    def test_list_ceph_mon_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ceph_mon(mock_client, node="pve")
        assert "No Ceph monitors" in result


class TestListCephMgr:
    def test_list_ceph_mgr_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "pve", "addr": "10.0.0.1:6800", "state": "active"},
        ])
        result = list_ceph_mgr(mock_client, node="pve")
        assert "pve" in result
        assert "active" in result

    def test_list_ceph_mgr_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ceph_mgr(mock_client, node="pve")
        assert "No Ceph managers" in result


class TestCephConfig:
    def test_ceph_config_string(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "[global]\nmon_host = pve"})
        result = ceph_config(mock_client, node="pve")
        assert "Ceph Configuration" in result

    def test_ceph_config_none(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_config(mock_client, node="pve")
        assert "No Ceph configuration" in result


class TestCephFlags:
    def test_ceph_flags_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "noout": True,
            "nobalance": False,
        })
        result = ceph_flags(mock_client)
        assert "Ceph Cluster Flags" in result
        assert "noout" in result

    def test_ceph_flags_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_flags(mock_client)
        assert "No Ceph flags" in result

    def test_ceph_flags_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "noout", "value": True},
        ])
        result = ceph_flags(mock_client)
        assert "noout" in result


class TestSetCephFlags:
    def test_set_ceph_flags_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            set_ceph_flags(mock_client, flags="noout", confirm=False)

    def test_set_ceph_flags_requires_flags(self, mock_client):
        with pytest.raises(ValueError, match="Flags string is required"):
            set_ceph_flags(mock_client, flags="", confirm=True)


class TestGetCephFlag:
    def test_get_ceph_flag_requires_flag(self, mock_client):
        with pytest.raises(ValueError, match="Flag name is required"):
            get_ceph_flag(mock_client, flag="")

    def test_get_ceph_flag_bool(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=True)
        result = get_ceph_flag(mock_client, flag="noout")
        assert "noout" in result

    def test_get_ceph_flag_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"value": True}})
        result = get_ceph_flag(mock_client, flag="noout")
        assert "noout" in result


class TestSetCephFlag:
    def test_set_ceph_flag_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            set_ceph_flag(mock_client, flag="noout", value="1", confirm=False)

    def test_set_ceph_flag_requires_flag(self, mock_client):
        with pytest.raises(ValueError, match="Flag name is required"):
            set_ceph_flag(mock_client, flag="", value="1", confirm=True)


class TestListCephOsdDetail:
    def test_list_ceph_osd_detail(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"id": 0, "host": "pve", "state": "up"},
        })
        result = list_ceph_osd_detail(mock_client, node="pve", osdid=0)
        assert "OSD 0" in result

    def test_list_ceph_osd_detail_invalid_node(self, mock_client):
        with pytest.raises(ValueError, match="Invalid node name"):
            list_ceph_osd_detail(mock_client, node="bad!", osdid=0)


class TestCreateCephOsd:
    def test_create_ceph_osd_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            create_ceph_osd(mock_client, node="pve", dev="/dev/sdb")

    def test_create_ceph_osd_requires_dev(self, mock_client):
        with pytest.raises(ValueError, match="Device path is required"):
            create_ceph_osd(mock_client, node="pve", dev="", confirm=True)


class TestDestroyCephOsd:
    def test_destroy_ceph_osd_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            destroy_ceph_osd(mock_client, node="pve", osdid=0)


class TestCephOsdIn:
    def test_ceph_osd_in_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            ceph_osd_in(mock_client, node="pve", osdid=0)


class TestCephOsdOut:
    def test_ceph_osd_out_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            ceph_osd_out(mock_client, node="pve", osdid=0)


class TestCephOsdScrub:
    def test_ceph_osd_scrub_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            ceph_osd_scrub(mock_client, node="pve", osdid=0)


class TestCephOsdMetadata:
    def test_ceph_osd_metadata_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"id": 0, "host": "pve"},
        })
        result = ceph_osd_metadata(mock_client, node="pve", osdid=0)
        assert "OSD 0" in result

    def test_ceph_osd_metadata_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_osd_metadata(mock_client, node="pve", osdid=0)
        assert "No OSD metadata" in result


class TestListCephPools:
    def test_list_ceph_pools_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"pool_name": "rbd", "pg_num": 64, "size": 3},
        ])
        result = list_ceph_pools(mock_client, node="pve")
        assert "rbd" in result
        assert "Ceph Pools" in result

    def test_list_ceph_pools_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ceph_pools(mock_client, node="pve")
        assert "No Ceph pools" in result


class TestCreateCephPool:
    def test_create_ceph_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            create_ceph_pool(mock_client, node="pve", name="test")

    def test_create_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            create_ceph_pool(mock_client, node="pve", name="", confirm=True)


class TestGetCephPool:
    def test_get_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            get_ceph_pool(mock_client, node="pve", name="")

    def test_get_ceph_pool_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"pool_name": "rbd", "pg_num": 64},
        })
        result = get_ceph_pool(mock_client, node="pve", name="rbd")
        assert "rbd" in result


class TestUpdateCephPool:
    def test_update_ceph_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            update_ceph_pool(mock_client, node="pve", name="rbd")

    def test_update_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            update_ceph_pool(mock_client, node="pve", name="", confirm=True)


class TestDestroyCephPool:
    def test_destroy_ceph_pool_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            destroy_ceph_pool(mock_client, node="pve", name="rbd")

    def test_destroy_ceph_pool_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            destroy_ceph_pool(mock_client, node="pve", name="", confirm=True)


class TestCephPoolStatus:
    def test_ceph_pool_status_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="Pool name is required"):
            ceph_pool_status(mock_client, node="pve", name="")

    def test_ceph_pool_status_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"bytes_used": 1000, "percent_used": 10.0},
        })
        result = ceph_pool_status(mock_client, node="pve", name="rbd")
        assert "rbd" in result


class TestListCephMdsDetail:
    def test_list_ceph_mds_detail_with_data(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "pve", "state": "active", "rank": 0},
        ])
        result = list_ceph_mds_detail(mock_client, node="pve")
        assert "pve" in result
        assert "active" in result

    def test_list_ceph_mds_detail_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_ceph_mds_detail(mock_client, node="pve")
        assert "No Ceph MDS" in result


class TestCreateCephMds:
    def test_create_ceph_mds_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            create_ceph_mds(mock_client, node="pve", name="mds0")

    def test_create_ceph_mds_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="MDS name is required"):
            create_ceph_mds(mock_client, node="pve", name="", confirm=True)


class TestDestroyCephMds:
    def test_destroy_ceph_mds_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            destroy_ceph_mds(mock_client, node="pve", name="mds0")

    def test_destroy_ceph_mds_requires_name(self, mock_client):
        with pytest.raises(ValueError, match="MDS name is required"):
            destroy_ceph_mds(mock_client, node="pve", name="", confirm=True)


class TestCreateCephMgr:
    def test_create_ceph_mgr_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            create_ceph_mgr(mock_client, node="pve", id="mgr0")

    def test_create_ceph_mgr_requires_id(self, mock_client):
        with pytest.raises(ValueError, match="MGR id is required"):
            create_ceph_mgr(mock_client, node="pve", id="", confirm=True)


class TestDestroyCephMgr:
    def test_destroy_ceph_mgr_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            destroy_ceph_mgr(mock_client, node="pve", id="mgr0")

    def test_destroy_ceph_mgr_requires_id(self, mock_client):
        with pytest.raises(ValueError, match="MGR id is required"):
            destroy_ceph_mgr(mock_client, node="pve", id="", confirm=True)


class TestCreateCephMon:
    def test_create_ceph_mon_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            create_ceph_mon(mock_client, node="pve", monid="mon0")

    def test_create_ceph_mon_requires_monid(self, mock_client):
        with pytest.raises(ValueError, match="Monitor id is required"):
            create_ceph_mon(mock_client, node="pve", monid="", confirm=True)


class TestDestroyCephMon:
    def test_destroy_ceph_mon_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            destroy_ceph_mon(mock_client, node="pve", monid="mon0")

    def test_destroy_ceph_mon_requires_monid(self, mock_client):
        with pytest.raises(ValueError, match="Monitor id is required"):
            destroy_ceph_mon(mock_client, node="pve", monid="", confirm=True)


class TestStartCeph:
    def test_start_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            start_ceph(mock_client, node="pve")


class TestStopCeph:
    def test_stop_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            stop_ceph(mock_client, node="pve")


class TestRestartCeph:
    def test_restart_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            restart_ceph(mock_client, node="pve")


class TestCephCfgDb:
    def test_ceph_cfg_db_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": [{"key": "mon_host", "value": "10.0.0.1"}],
        })
        result = ceph_cfg_db(mock_client, node="pve")
        assert "Config DB" in result

    def test_ceph_cfg_db_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"mon_host": "10.0.0.1"},
        })
        result = ceph_cfg_db(mock_client, node="pve")
        assert "Config DB" in result

    def test_ceph_cfg_db_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_cfg_db(mock_client, node="pve")
        assert "No Ceph config DB" in result


class TestCephCfgValue:
    def test_ceph_cfg_value_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"mon_host": "10.0.0.1"},
        })
        result = ceph_cfg_value(mock_client, node="pve")
        assert "Config Value" in result

    def test_ceph_cfg_value_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_cfg_value(mock_client, node="pve")
        assert "No config value" in result


class TestCephCrush:
    def test_ceph_crush_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": {"root": "default", "rules": 2},
        })
        result = ceph_crush(mock_client, node="pve")
        assert "CRUSH" in result

    def test_ceph_crush_string(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="crush map data")
        result = ceph_crush(mock_client, node="pve")
        assert "CRUSH" in result

    def test_ceph_crush_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_crush(mock_client, node="pve")
        assert "No CRUSH map" in result


class TestCephLog:
    def test_ceph_log_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"timestamp": "2024-01-01", "message": "osd.0 up"},
        ])
        result = ceph_log(mock_client, node="pve")
        assert "Ceph Log" in result
        assert "osd.0 up" in result

    def test_ceph_log_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": [{"timestamp": "2024-01-01", "message": "osd.0 down"}],
        })
        result = ceph_log(mock_client, node="pve")
        assert "Ceph Log" in result

    def test_ceph_log_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = ceph_log(mock_client, node="pve")
        assert "No Ceph log" in result


class TestInitCeph:
    def test_init_ceph_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="requires confirm=true"):
            init_ceph(mock_client, node="pve")


class TestElevatedEnforcement:
    def test_create_ceph_osd_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            create_ceph_osd(mock_client, node="pve", dev="/dev/sdb", confirm=True)

    def test_destroy_ceph_osd_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            destroy_ceph_osd(mock_client, node="pve", osdid=0, confirm=True)

    def test_ceph_osd_in_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            ceph_osd_in(mock_client, node="pve", osdid=0, confirm=True)

    def test_ceph_osd_out_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            ceph_osd_out(mock_client, node="pve", osdid=0, confirm=True)

    def test_ceph_osd_scrub_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            ceph_osd_scrub(mock_client, node="pve", osdid=0, confirm=True)

    def test_create_ceph_pool_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            create_ceph_pool(mock_client, node="pve", name="test", confirm=True)

    def test_update_ceph_pool_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            update_ceph_pool(mock_client, node="pve", name="test", confirm=True)

    def test_destroy_ceph_pool_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            destroy_ceph_pool(mock_client, node="pve", name="test", confirm=True)

    def test_create_ceph_mds_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            create_ceph_mds(mock_client, node="pve", name="test", confirm=True)

    def test_destroy_ceph_mds_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            destroy_ceph_mds(mock_client, node="pve", name="test", confirm=True)

    def test_create_ceph_mgr_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            create_ceph_mgr(mock_client, node="pve", id="test", confirm=True)

    def test_destroy_ceph_mgr_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            destroy_ceph_mgr(mock_client, node="pve", id="test", confirm=True)

    def test_create_ceph_mon_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            create_ceph_mon(mock_client, node="pve", monid="test", confirm=True)

    def test_destroy_ceph_mon_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            destroy_ceph_mon(mock_client, node="pve", monid="test", confirm=True)

    def test_start_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            start_ceph(mock_client, node="pve", confirm=True)

    def test_stop_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            stop_ceph(mock_client, node="pve", confirm=True)

    def test_restart_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            restart_ceph(mock_client, node="pve", confirm=True)

    def test_set_ceph_flags_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            set_ceph_flags(mock_client, flags="noout", confirm=True)

    def test_set_ceph_flag_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            set_ceph_flag(mock_client, flag="noout", value="1", confirm=True)

    def test_init_ceph_requires_elevated(self, mock_client):
        mock_client.config.allow_elevated = False
        with pytest.raises(ValueError, match="Elevated operations are not allowed"):
            init_ceph(mock_client, node="pve", confirm=True)
