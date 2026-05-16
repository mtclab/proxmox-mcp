from unittest.mock import MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.sdn import (
    add_sdn_fabric_node,
    apply_sdn,
    create_prefix_list_entry,
    create_route_map_entry,
    create_sdn_controller,
    create_sdn_dns,
    create_sdn_fabric,
    create_sdn_ipam,
    create_sdn_prefix_list,
    create_sdn_subnet,
    create_sdn_vnet,
    create_sdn_vnet_firewall_rule,
    create_sdn_vnet_ip,
    create_sdn_zone,
    delete_prefix_list_entry,
    delete_route_map_entry,
    delete_sdn_controller,
    delete_sdn_dns,
    delete_sdn_fabric,
    delete_sdn_ipam,
    delete_sdn_prefix_list,
    delete_sdn_subnet,
    delete_sdn_vnet,
    delete_sdn_vnet_firewall_rule,
    delete_sdn_vnet_ip,
    delete_sdn_zone,
    get_node_sdn_vnet,
    get_node_sdn_zone_content,
    get_node_sdn_zone_ip_vrf,
    get_node_sdn_zone_status,
    get_prefix_list_entry,
    get_route_map_entry,
    get_sdn_controller,
    get_sdn_dns,
    get_sdn_fabric_node,
    get_sdn_ipam,
    get_sdn_ipam_status,
    get_sdn_vnet,
    get_sdn_vnet_firewall_options,
    get_sdn_vnet_firewall_rule,
    get_sdn_zone,
    list_node_sdn_zone_bridges,
    list_node_sdn_zones,
    list_prefix_list_entries,
    list_route_map_entries,
    list_sdn_controllers,
    list_sdn_dns,
    list_sdn_fabric_detail,
    list_sdn_fabric_nodes,
    list_sdn_fabrics,
    list_sdn_ipams,
    list_sdn_prefix_lists,
    list_sdn_route_maps,
    list_sdn_subnets,
    list_sdn_vnet_firewall_rules,
    list_sdn_vnets,
    list_sdn_zones,
    remove_sdn_fabric_node,
    sdn_dry_run,
    sdn_rollback,
    set_sdn_vnet_firewall_options,
    update_prefix_list_entry,
    update_route_map_entry,
    update_sdn_controller,
    update_sdn_dns,
    update_sdn_fabric,
    update_sdn_fabric_node,
    update_sdn_ipam,
    update_sdn_vnet,
    update_sdn_vnet_firewall_rule,
    update_sdn_vnet_ip,
    update_sdn_zone,
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
    admin_mock = MagicMock()
    client.admin_client = admin_mock
    client.monitor_client = MagicMock()
    return client


class TestListSdnZones:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"zone": "zone1", "type": "evpn"},
            {"zone": "zone2", "type": "simple"},
        ])
        result = list_sdn_zones(mock_client)
        assert "zone1" in result
        assert "evpn" in result
        assert "SDN Zones" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_zones(mock_client)
        assert "No SDN zones" in result


class TestGetSdnZone:
    def test_get_zone(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"zone": "zone1", "type": "evpn"})
        result = get_sdn_zone(mock_client, zone="zone1")
        assert "zone1" in result
        assert "evpn" in result

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            get_sdn_zone(mock_client, zone="")


class TestCreateSdnZone:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_zone(mock_client, zone="z1", type="evpn")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_sdn_zone(client, zone="z1", type="evpn", confirm=True)

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            create_sdn_zone(mock_client, zone="", type="evpn", confirm=True)

    def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            create_sdn_zone(mock_client, zone="z1", type="", confirm=True)

    def test_create_zone(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_zone(mock_client, zone="z1", type="evpn", confirm=True)
        assert "z1" in result
        assert "created" in result.lower()

    def test_create_with_optional(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_zone(
            mock_client, zone="z1", type="evpn", comment="test", nodes="pve", confirm=True,
        )
        assert "z1" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test"
        assert call_args[1]["nodes"] == "pve"


class TestUpdateSdnZone:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_zone(mock_client, zone="z1", comment="x")

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            update_sdn_zone(mock_client, zone="", confirm=True, comment="x")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_zone(mock_client, zone="z1", confirm=True)

    def test_update_zone(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_zone(mock_client, zone="z1", comment="new", confirm=True)
        assert "z1" in result
        assert "updated" in result.lower()


class TestDeleteSdnZone:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_zone(mock_client, zone="z1")

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            delete_sdn_zone(mock_client, zone="", confirm=True)

    def test_delete_zone(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_zone(mock_client, zone="z1", confirm=True)
        assert "z1" in result
        assert "deleted" in result.lower()


class TestListSdnVnets:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"vnet": "vnet1", "zone": "zone1"},
        ])
        result = list_sdn_vnets(mock_client)
        assert "vnet1" in result
        assert "zone1" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_vnets(mock_client)
        assert "No SDN VNets" in result


class TestGetSdnVnet:
    def test_get_vnet(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"vnet": "vnet1", "zone": "zone1"})
        result = get_sdn_vnet(mock_client, vnet="vnet1")
        assert "vnet1" in result

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            get_sdn_vnet(mock_client, vnet="")


class TestCreateSdnVnet:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_vnet(mock_client, vnet="v1", zone="z1")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            create_sdn_vnet(mock_client, vnet="", zone="z1", confirm=True)

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            create_sdn_vnet(mock_client, vnet="v1", zone="", confirm=True)

    def test_create_vnet(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_vnet(mock_client, vnet="v1", zone="z1", confirm=True)
        assert "v1" in result
        assert "created" in result.lower()


class TestUpdateSdnVnet:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_vnet(mock_client, vnet="v1", comment="x")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            update_sdn_vnet(mock_client, vnet="", confirm=True, comment="x")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_vnet(mock_client, vnet="v1", confirm=True)

    def test_update_vnet(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_vnet(mock_client, vnet="v1", comment="new", confirm=True)
        assert "v1" in result
        assert "updated" in result.lower()


class TestDeleteSdnVnet:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_vnet(mock_client, vnet="v1")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            delete_sdn_vnet(mock_client, vnet="", confirm=True)

    def test_delete_vnet(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_vnet(mock_client, vnet="v1", confirm=True)
        assert "v1" in result
        assert "deleted" in result.lower()


class TestListSdnSubnets:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"subnet": "10.0.0.0/24"},
        ])
        result = list_sdn_subnets(mock_client, vnet="v1")
        assert "10.0.0.0/24" in result

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            list_sdn_subnets(mock_client, vnet="")


class TestCreateSdnSubnet:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            create_sdn_subnet(mock_client, vnet="", subnet="10.0.0.0/24", confirm=True)

    def test_no_subnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="subnet is required"):
            create_sdn_subnet(mock_client, vnet="v1", subnet="", confirm=True)

    def test_create_subnet(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24", confirm=True)
        assert "10.0.0.0/24" in result
        assert "created" in result.lower()


class TestDeleteSdnSubnet:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            delete_sdn_subnet(mock_client, vnet="", subnet="10.0.0.0/24", confirm=True)

    def test_no_subnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="subnet is required"):
            delete_sdn_subnet(mock_client, vnet="v1", subnet="", confirm=True)

    def test_delete_subnet(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24", confirm=True)
        assert "10.0.0.0/24" in result
        assert "deleted" in result.lower()


class TestListSdnControllers:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"controller": "ctrl1", "type": "evpn"},
        ])
        result = list_sdn_controllers(mock_client)
        assert "ctrl1" in result
        assert "SDN Controllers" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_controllers(mock_client)
        assert "No SDN controllers" in result


class TestCreateSdnController:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_controller(mock_client, controller="c1", type="evpn")

    def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            create_sdn_controller(mock_client, controller="", type="evpn", confirm=True)

    def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            create_sdn_controller(mock_client, controller="c1", type="", confirm=True)

    def test_create_controller(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_controller(mock_client, controller="c1", type="evpn", confirm=True)
        assert "c1" in result
        assert "created" in result.lower()


class TestDeleteSdnController:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_controller(mock_client, controller="c1")

    def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            delete_sdn_controller(mock_client, controller="", confirm=True)

    def test_delete_controller(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_controller(mock_client, controller="c1", confirm=True)
        assert "c1" in result
        assert "deleted" in result.lower()


class TestListSdnDns:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"dns": "dns1", "type": "dns"},
        ])
        result = list_sdn_dns(mock_client)
        assert "dns1" in result
        assert "SDN DNS" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_dns(mock_client)
        assert "No SDN DNS" in result


class TestCreateSdnDns:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_dns(mock_client, dns="d1", type="dns")

    def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            create_sdn_dns(mock_client, dns="", type="dns", confirm=True)

    def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            create_sdn_dns(mock_client, dns="d1", type="", confirm=True)

    def test_create_dns(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_dns(mock_client, dns="d1", type="dns", confirm=True)
        assert "d1" in result
        assert "created" in result.lower()


class TestDeleteSdnDns:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_dns(mock_client, dns="d1")

    def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            delete_sdn_dns(mock_client, dns="", confirm=True)

    def test_delete_dns(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_dns(mock_client, dns="d1", confirm=True)
        assert "d1" in result
        assert "deleted" in result.lower()


class TestListSdnIpams:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"ipam": "ipam1", "type": "pve"},
        ])
        result = list_sdn_ipams(mock_client)
        assert "ipam1" in result
        assert "SDN IPAMs" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_ipams(mock_client)
        assert "No SDN IPAMs" in result


class TestCreateSdnIpam:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_ipam(mock_client, ipam="i1", type="pve")

    def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            create_sdn_ipam(mock_client, ipam="", type="pve", confirm=True)

    def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            create_sdn_ipam(mock_client, ipam="i1", type="", confirm=True)

    def test_create_ipam(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_ipam(mock_client, ipam="i1", type="pve", confirm=True)
        assert "i1" in result
        assert "created" in result.lower()


class TestDeleteSdnIpam:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_ipam(mock_client, ipam="i1")

    def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            delete_sdn_ipam(mock_client, ipam="", confirm=True)

    def test_delete_ipam(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_ipam(mock_client, ipam="i1", confirm=True)
        assert "i1" in result
        assert "deleted" in result.lower()


class TestApplySdn:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            apply_sdn(mock_client)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            apply_sdn(client, confirm=True)

    def test_apply(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = apply_sdn(mock_client, confirm=True)
        assert "applied" in result.lower()


class TestListNodeSdnZones:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"zone": "zone1", "status": "ok"},
        ])
        result = list_node_sdn_zones(mock_client, node="pve")
        assert "zone1" in result
        assert "pve" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_sdn_zones(mock_client, node="pve")
        assert "No SDN zones" in result

    def test_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_sdn_zones(mock_client)
        assert "pve" in result


class TestGetNodeSdnZoneStatus:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"zone": "zone1", "status": "ok"})
        result = get_node_sdn_zone_status(mock_client, node="pve", zone="zone1")
        assert "zone1" in result
        assert "pve" in result

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            get_node_sdn_zone_status(mock_client, node="pve", zone="")

    def test_list_result(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"bridge": "vmbr1", "ports": "vnet1"},
        ])
        result = get_node_sdn_zone_status(mock_client, node="pve", zone="zone1")
        assert "vmbr1" in result


class TestGetSdnIpamStatus:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"subnet": "10.0.0.0/24", "gateway": "10.0.0.1", "type": "ipv4"},
        ])
        result = get_sdn_ipam_status(mock_client, ipam="pve")
        assert "10.0.0.0/24" in result
        assert "pve" in result

    def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            get_sdn_ipam_status(mock_client, ipam="")

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = get_sdn_ipam_status(mock_client, ipam="pve")
        assert "No IPAM entries" in result


class TestListSdnFabrics:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"fabric": "fab1", "type": "evpn"},
        ])
        result = list_sdn_fabrics(mock_client)
        assert "fab1" in result
        assert "Fabrics" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_fabrics(mock_client)
        assert "No SDN fabrics" in result


class TestListSdnFabricDetail:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"fabric": "fab1", "type": "evpn"})
        result = list_sdn_fabric_detail(mock_client, fabric="fab1")
        assert "fab1" in result

    def test_no_fabric_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric is required"):
            list_sdn_fabric_detail(mock_client, fabric="")


class TestCreateSdnFabric:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_fabric(mock_client, fabric="f1", type="evpn")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_sdn_fabric(client, fabric="f1", type="evpn", confirm=True)

    def test_no_fabric_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric is required"):
            create_sdn_fabric(mock_client, fabric="", type="evpn", confirm=True)

    def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            create_sdn_fabric(mock_client, fabric="f1", type="", confirm=True)

    def test_create_fabric(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_fabric(mock_client, fabric="fab1", type="evpn", confirm=True)
        assert "fab1" in result
        assert "created" in result.lower()


class TestDeleteSdnFabric:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_fabric(mock_client, id="fab1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_sdn_fabric(mock_client, id="", confirm=True)

    def test_delete_fabric(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_fabric(mock_client, id="fab1", confirm=True)
        assert "fab1" in result
        assert "deleted" in result.lower()


class TestUpdateSdnFabric:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_fabric(mock_client, id="fab1", comment="x")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            update_sdn_fabric(mock_client, id="", confirm=True, comment="x")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_fabric(mock_client, id="fab1", confirm=True)

    def test_update_fabric(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_fabric(mock_client, id="fab1", comment="new", confirm=True)
        assert "fab1" in result
        assert "updated" in result.lower()


class TestListSdnPrefixLists:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"name": "prefix1"},
        ])
        result = list_sdn_prefix_lists(mock_client)
        assert "prefix1" in result
        assert "Prefix Lists" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_prefix_lists(mock_client)
        assert "No SDN prefix lists" in result


class TestCreateSdnPrefixList:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_prefix_list(mock_client, id="pl1")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_sdn_prefix_list(client, id="pl1", confirm=True)

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            create_sdn_prefix_list(mock_client, id="", confirm=True)

    def test_create_prefix_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_prefix_list(mock_client, id="pl1", confirm=True)
        assert "pl1" in result
        assert "created" in result.lower()


class TestDeleteSdnPrefixList:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_prefix_list(mock_client, id="pl1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_sdn_prefix_list(mock_client, id="", confirm=True)

    def test_delete_prefix_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_prefix_list(mock_client, id="pl1", confirm=True)
        assert "pl1" in result
        assert "deleted" in result.lower()


class TestListSdnRouteMaps:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "rmap1"},
        ])
        result = list_sdn_route_maps(mock_client)
        assert "rmap1" in result
        assert "Route Maps" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_route_maps(mock_client)
        assert "No SDN route maps" in result


class TestSdnRollback:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            sdn_rollback(mock_client)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient
            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            sdn_rollback(client, confirm=True)

    def test_rollback(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = sdn_rollback(mock_client, confirm=True)
        assert "rollback" in result.lower()


class TestGetSdnIpam:
    def test_get_ipam(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"ipam": "pve", "type": "pve"})
        result = get_sdn_ipam(mock_client, ipam="pve")
        assert "pve" in result

    def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            get_sdn_ipam(mock_client, ipam="")


class TestUpdateSdnIpam:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_ipam(mock_client, ipam="pve", comment="x")

    def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            update_sdn_ipam(mock_client, ipam="", confirm=True, comment="x")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_ipam(mock_client, ipam="pve", confirm=True)

    def test_update_ipam(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_ipam(mock_client, ipam="pve", confirm=True, comment="new")
        assert "pve" in result
        assert "updated" in result.lower()


class TestGetSdnDns:
    def test_get_dns(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"dns": "dns1", "type": "dns"})
        result = get_sdn_dns(mock_client, dns="dns1")
        assert "dns1" in result

    def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            get_sdn_dns(mock_client, dns="")


class TestUpdateSdnDns:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_dns(mock_client, dns="d1", comment="x")

    def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            update_sdn_dns(mock_client, dns="", confirm=True, comment="x")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_dns(mock_client, dns="d1", confirm=True)

    def test_update_dns(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_dns(mock_client, dns="d1", confirm=True, comment="new")
        assert "d1" in result
        assert "updated" in result.lower()


class TestGetSdnController:
    def test_get_controller(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"controller": "c1", "type": "evpn"})
        result = get_sdn_controller(mock_client, controller="c1")
        assert "c1" in result

    def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            get_sdn_controller(mock_client, controller="")


class TestUpdateSdnController:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_controller(mock_client, controller="c1", comment="x")

    def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            update_sdn_controller(mock_client, controller="", confirm=True, comment="x")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_controller(mock_client, controller="c1", confirm=True)

    def test_update_controller(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_controller(mock_client, controller="c1", confirm=True, comment="new")
        assert "c1" in result
        assert "updated" in result.lower()


class TestListSdnFabricNodes:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"node": "pve"}, {"node": "pve2"},
        ])
        result = list_sdn_fabric_nodes(mock_client, fabric_id="fab1")
        assert "pve" in result
        assert "fab1" in result

    def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            list_sdn_fabric_nodes(mock_client, fabric_id="")


class TestAddSdnFabricNode:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            add_sdn_fabric_node(mock_client, fabric_id="f1", node="pve")

    def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            add_sdn_fabric_node(mock_client, fabric_id="", node="pve", confirm=True)

    def test_no_node_raises(self, mock_client):
        with pytest.raises(ValueError, match="node is required"):
            add_sdn_fabric_node(mock_client, fabric_id="f1", node="", confirm=True)

    def test_add_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = add_sdn_fabric_node(mock_client, fabric_id="f1", node="pve", confirm=True)
        assert "pve" in result
        assert "f1" in result


class TestGetSdnFabricNode:
    def test_get_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"node": "pve", "status": "ok"})
        result = get_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve")
        assert "pve" in result

    def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            get_sdn_fabric_node(mock_client, fabric_id="", node_id="pve")

    def test_no_node_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="node_id is required"):
            get_sdn_fabric_node(mock_client, fabric_id="f1", node_id="")


class TestUpdateSdnFabricNode:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", comment="x")

    def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            update_sdn_fabric_node(mock_client, fabric_id="", node_id="pve", confirm=True, comment="x")

    def test_no_node_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="node_id is required"):
            update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="", confirm=True, comment="x")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", confirm=True)

    def test_update_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", confirm=True, comment="new")
        assert "pve" in result
        assert "updated" in result.lower()


class TestRemoveSdnFabricNode:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            remove_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve")

    def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            remove_sdn_fabric_node(mock_client, fabric_id="", node_id="pve", confirm=True)

    def test_no_node_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="node_id is required"):
            remove_sdn_fabric_node(mock_client, fabric_id="f1", node_id="", confirm=True)

    def test_remove_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = remove_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", confirm=True)
        assert "pve" in result
        assert "removed" in result.lower()


class TestCreateSdnVnetIp:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_vnet_ip(mock_client, vnet="v1")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            create_sdn_vnet_ip(mock_client, vnet="", confirm=True)

    def test_create_ip(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_vnet_ip(mock_client, vnet="v1", confirm=True)
        assert "v1" in result
        assert "created" in result.lower()


class TestUpdateSdnVnetIp:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_vnet_ip(mock_client, vnet="v1", mac="aa:bb:cc")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            update_sdn_vnet_ip(mock_client, vnet="", confirm=True, mac="aa:bb:cc")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_vnet_ip(mock_client, vnet="v1", confirm=True)

    def test_update_ip(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_vnet_ip(mock_client, vnet="v1", confirm=True, mac="aa:bb:cc")
        assert "v1" in result
        assert "updated" in result.lower()


class TestDeleteSdnVnetIp:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_vnet_ip(mock_client, vnet="v1")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            delete_sdn_vnet_ip(mock_client, vnet="", confirm=True)

    def test_delete_ip(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_vnet_ip(mock_client, vnet="v1", confirm=True)
        assert "v1" in result
        assert "deleted" in result.lower()


class TestGetSdnVnetFirewallOptions:
    def test_get_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"enable": 1, "policy_in": "ACCEPT"})
        result = get_sdn_vnet_firewall_options(mock_client, vnet="v1")
        assert "v1" in result
        assert "enable" in result

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            get_sdn_vnet_firewall_options(mock_client, vnet="")


class TestSetSdnVnetFirewallOptions:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            set_sdn_vnet_firewall_options(mock_client, vnet="v1", enable=1)

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            set_sdn_vnet_firewall_options(mock_client, vnet="", confirm=True, enable=1)

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            set_sdn_vnet_firewall_options(mock_client, vnet="v1", confirm=True)

    def test_set_options(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = set_sdn_vnet_firewall_options(mock_client, vnet="v1", confirm=True, enable=1)
        assert "v1" in result
        assert "firewall options" in result.lower()


class TestListSdnVnetFirewallRules:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"pos": 0, "action": "ACCEPT"},
        ])
        result = list_sdn_vnet_firewall_rules(mock_client, vnet="v1")
        assert "v1" in result
        assert "ACCEPT" in result

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            list_sdn_vnet_firewall_rules(mock_client, vnet="")

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_sdn_vnet_firewall_rules(mock_client, vnet="v1")
        assert "No firewall rules" in result


class TestCreateSdnVnetFirewallRule:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_sdn_vnet_firewall_rule(mock_client, vnet="v1")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            create_sdn_vnet_firewall_rule(mock_client, vnet="", confirm=True)

    def test_create_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_sdn_vnet_firewall_rule(mock_client, vnet="v1", confirm=True, action="ACCEPT")
        assert "v1" in result
        assert "created" in result.lower()


class TestDeleteSdnVnetFirewallRule:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0)

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            delete_sdn_vnet_firewall_rule(mock_client, vnet="", pos=0, confirm=True)

    def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, confirm=True)
        assert "v1" in result
        assert "deleted" in result.lower()


class TestGetSdnVnetFirewallRule:
    def test_get_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = get_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0)
        assert "v1" in result

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            get_sdn_vnet_firewall_rule(mock_client, vnet="", pos=0)


class TestUpdateSdnVnetFirewallRule:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, action="DROP")

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            update_sdn_vnet_firewall_rule(mock_client, vnet="", pos=0, confirm=True, action="DROP")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, confirm=True)

    def test_update_rule(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, confirm=True, action="DROP")
        assert "v1" in result
        assert "updated" in result.lower()


class TestListPrefixListEntries:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"seq": 1, "prefix": "10.0.0.0/8"},
        ])
        result = list_prefix_list_entries(mock_client, id="pl1")
        assert "pl1" in result

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            list_prefix_list_entries(mock_client, id="")

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_prefix_list_entries(mock_client, id="pl1")
        assert "No prefix list entries" in result


class TestCreatePrefixListEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_prefix_list_entry(mock_client, id="pl1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            create_prefix_list_entry(mock_client, id="", confirm=True)

    def test_create_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_prefix_list_entry(mock_client, id="pl1", confirm=True)
        assert "pl1" in result
        assert "created" in result.lower()


class TestDeletePrefixListEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_prefix_list_entry(mock_client, id="pl1", url_seq=1)

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            delete_prefix_list_entry(mock_client, id="", url_seq=1, confirm=True)

    def test_delete_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_prefix_list_entry(mock_client, id="pl1", url_seq=1, confirm=True)
        assert "pl1" in result
        assert "deleted" in result.lower()


class TestGetPrefixListEntry:
    def test_get_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"seq": 1, "prefix": "10.0.0.0/8"})
        result = get_prefix_list_entry(mock_client, id="pl1", url_seq=1)
        assert "pl1" in result

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            get_prefix_list_entry(mock_client, id="", url_seq=1)


class TestUpdatePrefixListEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_prefix_list_entry(mock_client, id="pl1", url_seq=1, prefix="10.0.0.0/8")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            update_prefix_list_entry(mock_client, id="", url_seq=1, confirm=True, prefix="10.0.0.0/8")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_prefix_list_entry(mock_client, id="pl1", url_seq=1, confirm=True)

    def test_update_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_prefix_list_entry(mock_client, id="pl1", url_seq=1, confirm=True, prefix="10.0.0.0/8")
        assert "pl1" in result
        assert "updated" in result.lower()


class TestListRouteMapEntries:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"id": "rm1"},
        ])
        result = list_route_map_entries(mock_client)
        assert "rm1" in result
        assert "Route Map Entries" in result

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_route_map_entries(mock_client)
        assert "No route map entries" in result


class TestCreateRouteMapEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_route_map_entry(mock_client, route_map_id="rm1")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            create_route_map_entry(mock_client, route_map_id="", confirm=True)

    def test_create_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = create_route_map_entry(mock_client, route_map_id="rm1", confirm=True)
        assert "rm1" in result
        assert "created" in result.lower()


class TestGetRouteMapEntry:
    def test_get_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"order": 10},
        ])
        result = get_route_map_entry(mock_client, route_map_id="rm1")
        assert "rm1" in result

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            get_route_map_entry(mock_client, route_map_id="")

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = get_route_map_entry(mock_client, route_map_id="rm1")
        assert "No entries" in result


class TestDeleteRouteMapEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_route_map_entry(mock_client, route_map_id="rm1", order=10)

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            delete_route_map_entry(mock_client, route_map_id="", order=10, confirm=True)

    def test_delete_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = delete_route_map_entry(mock_client, route_map_id="rm1", order=10, confirm=True)
        assert "rm1" in result
        assert "deleted" in result.lower()


class TestUpdateRouteMapEntry:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_route_map_entry(mock_client, route_map_id="rm1", order=10, action="permit")

    def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            update_route_map_entry(mock_client, route_map_id="", order=10, confirm=True, action="permit")

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            update_route_map_entry(mock_client, route_map_id="rm1", order=10, confirm=True)

    def test_update_entry(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = update_route_map_entry(mock_client, route_map_id="rm1", order=10, confirm=True, action="permit")
        assert "rm1" in result
        assert "updated" in result.lower()


class TestSdnDryRun:
    def test_dry_run_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"changes": "pending"})
        result = sdn_dry_run(mock_client)
        assert "Dry-Run" in result

    def test_dry_run_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"zone": "z1", "status": "changed"},
        ])
        result = sdn_dry_run(mock_client)
        assert "Dry-Run" in result

    def test_dry_run_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = sdn_dry_run(mock_client)
        assert "Dry-Run" in result


class TestGetNodeSdnVnet:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"vnet": "v1", "zone": "z1"})
        result = get_node_sdn_vnet(mock_client, node="pve", vnet="v1")
        assert "v1" in result
        assert "pve" in result

    def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            get_node_sdn_vnet(mock_client, node="pve", vnet="")

    def test_default_node(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"vnet": "v1"})
        result = get_node_sdn_vnet(mock_client, vnet="v1")
        assert "pve" in result


class TestListNodeSdnZoneBridges:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"bridge": "vmbr1"},
        ])
        result = list_node_sdn_zone_bridges(mock_client, node="pve", zone="z1")
        assert "vmbr1" in result
        assert "z1" in result

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            list_node_sdn_zone_bridges(mock_client, node="pve", zone="")

    def test_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[])
        result = list_node_sdn_zone_bridges(mock_client, node="pve", zone="z1")
        assert "No bridges" in result


class TestGetNodeSdnZoneContent:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"zone": "z1", "content": "data"})
        result = get_node_sdn_zone_content(mock_client, node="pve", zone="z1")
        assert "z1" in result

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            get_node_sdn_zone_content(mock_client, node="pve", zone="")


class TestGetNodeSdnZoneIpVrf:
    def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"vrf": "vrf0"})
        result = get_node_sdn_zone_ip_vrf(mock_client, node="pve", zone="z1")
        assert "z1" in result
        assert "IP-VRF" in result

    def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            get_node_sdn_zone_ip_vrf(mock_client, node="pve", zone="")
