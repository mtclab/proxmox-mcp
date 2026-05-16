from unittest.mock import AsyncMock, MagicMock, patch

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
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"zone": "zone1", "type": "evpn"},
                {"zone": "zone2", "type": "simple"},
            ]
        )
        result = await list_sdn_zones(mock_client)
        assert "zone1" in result
        assert "evpn" in result
        assert "SDN Zones" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_zones(mock_client)
        assert "No SDN zones" in result


class TestGetSdnZone:
    async def test_get_zone(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"zone": "zone1", "type": "evpn"})
        result = await get_sdn_zone(mock_client, zone="zone1")
        assert "zone1" in result
        assert "evpn" in result

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await get_sdn_zone(mock_client, zone="")


class TestCreateSdnZone:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_zone(mock_client, zone="z1", type="evpn")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_sdn_zone(client, zone="z1", type="evpn", confirm=True)

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await create_sdn_zone(mock_client, zone="", type="evpn", confirm=True)

    async def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            await create_sdn_zone(mock_client, zone="z1", type="", confirm=True)

    async def test_create_zone(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_zone(mock_client, zone="z1", type="evpn", confirm=True)
        assert "z1" in result
        assert "created" in result.lower()

    async def test_create_with_optional(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_zone(
            mock_client,
            zone="z1",
            type="evpn",
            comment="test",
            nodes="pve",
            confirm=True,
        )
        assert "z1" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test"
        assert call_args[1]["nodes"] == "pve"


class TestUpdateSdnZone:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_zone(mock_client, zone="z1", comment="x")

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await update_sdn_zone(mock_client, zone="", confirm=True, comment="x")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_zone(mock_client, zone="z1", confirm=True)

    async def test_update_zone(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_zone(mock_client, zone="z1", comment="new", confirm=True)
        assert "z1" in result
        assert "updated" in result.lower()


class TestDeleteSdnZone:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_zone(mock_client, zone="z1")

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await delete_sdn_zone(mock_client, zone="", confirm=True)

    async def test_delete_zone(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_zone(mock_client, zone="z1", confirm=True)
        assert "z1" in result
        assert "deleted" in result.lower()


class TestListSdnVnets:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"vnet": "vnet1", "zone": "zone1"},
            ]
        )
        result = await list_sdn_vnets(mock_client)
        assert "vnet1" in result
        assert "zone1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_vnets(mock_client)
        assert "No SDN VNets" in result


class TestGetSdnVnet:
    async def test_get_vnet(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"vnet": "vnet1", "zone": "zone1"})
        result = await get_sdn_vnet(mock_client, vnet="vnet1")
        assert "vnet1" in result

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await get_sdn_vnet(mock_client, vnet="")


class TestCreateSdnVnet:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_vnet(mock_client, vnet="v1", zone="z1")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await create_sdn_vnet(mock_client, vnet="", zone="z1", confirm=True)

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await create_sdn_vnet(mock_client, vnet="v1", zone="", confirm=True)

    async def test_create_vnet(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_vnet(mock_client, vnet="v1", zone="z1", confirm=True)
        assert "v1" in result
        assert "created" in result.lower()


class TestUpdateSdnVnet:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_vnet(mock_client, vnet="v1", comment="x")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await update_sdn_vnet(mock_client, vnet="", confirm=True, comment="x")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_vnet(mock_client, vnet="v1", confirm=True)

    async def test_update_vnet(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_vnet(mock_client, vnet="v1", comment="new", confirm=True)
        assert "v1" in result
        assert "updated" in result.lower()


class TestDeleteSdnVnet:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_vnet(mock_client, vnet="v1")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await delete_sdn_vnet(mock_client, vnet="", confirm=True)

    async def test_delete_vnet(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_vnet(mock_client, vnet="v1", confirm=True)
        assert "v1" in result
        assert "deleted" in result.lower()


class TestListSdnSubnets:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"subnet": "10.0.0.0/24"},
            ]
        )
        result = await list_sdn_subnets(mock_client, vnet="v1")
        assert "10.0.0.0/24" in result

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await list_sdn_subnets(mock_client, vnet="")


class TestCreateSdnSubnet:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await create_sdn_subnet(mock_client, vnet="", subnet="10.0.0.0/24", confirm=True)

    async def test_no_subnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="subnet is required"):
            await create_sdn_subnet(mock_client, vnet="v1", subnet="", confirm=True)

    async def test_create_subnet(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24", confirm=True)
        assert "10.0.0.0/24" in result
        assert "created" in result.lower()


class TestDeleteSdnSubnet:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await delete_sdn_subnet(mock_client, vnet="", subnet="10.0.0.0/24", confirm=True)

    async def test_no_subnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="subnet is required"):
            await delete_sdn_subnet(mock_client, vnet="v1", subnet="", confirm=True)

    async def test_delete_subnet(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_subnet(mock_client, vnet="v1", subnet="10.0.0.0/24", confirm=True)
        assert "10.0.0.0/24" in result
        assert "deleted" in result.lower()


class TestListSdnControllers:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"controller": "ctrl1", "type": "evpn"},
            ]
        )
        result = await list_sdn_controllers(mock_client)
        assert "ctrl1" in result
        assert "SDN Controllers" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_controllers(mock_client)
        assert "No SDN controllers" in result


class TestCreateSdnController:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_controller(mock_client, controller="c1", type="evpn")

    async def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            await create_sdn_controller(mock_client, controller="", type="evpn", confirm=True)

    async def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            await create_sdn_controller(mock_client, controller="c1", type="", confirm=True)

    async def test_create_controller(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_controller(mock_client, controller="c1", type="evpn", confirm=True)
        assert "c1" in result
        assert "created" in result.lower()


class TestDeleteSdnController:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_controller(mock_client, controller="c1")

    async def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            await delete_sdn_controller(mock_client, controller="", confirm=True)

    async def test_delete_controller(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_controller(mock_client, controller="c1", confirm=True)
        assert "c1" in result
        assert "deleted" in result.lower()


class TestListSdnDns:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"dns": "dns1", "type": "dns"},
            ]
        )
        result = await list_sdn_dns(mock_client)
        assert "dns1" in result
        assert "SDN DNS" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_dns(mock_client)
        assert "No SDN DNS" in result


class TestCreateSdnDns:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_dns(mock_client, dns="d1", type="dns")

    async def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            await create_sdn_dns(mock_client, dns="", type="dns", confirm=True)

    async def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            await create_sdn_dns(mock_client, dns="d1", type="", confirm=True)

    async def test_create_dns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_dns(mock_client, dns="d1", type="dns", confirm=True)
        assert "d1" in result
        assert "created" in result.lower()


class TestDeleteSdnDns:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_dns(mock_client, dns="d1")

    async def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            await delete_sdn_dns(mock_client, dns="", confirm=True)

    async def test_delete_dns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_dns(mock_client, dns="d1", confirm=True)
        assert "d1" in result
        assert "deleted" in result.lower()


class TestListSdnIpams:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"ipam": "ipam1", "type": "pve"},
            ]
        )
        result = await list_sdn_ipams(mock_client)
        assert "ipam1" in result
        assert "SDN IPAMs" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_ipams(mock_client)
        assert "No SDN IPAMs" in result


class TestCreateSdnIpam:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_ipam(mock_client, ipam="i1", type="pve")

    async def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            await create_sdn_ipam(mock_client, ipam="", type="pve", confirm=True)

    async def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            await create_sdn_ipam(mock_client, ipam="i1", type="", confirm=True)

    async def test_create_ipam(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_ipam(mock_client, ipam="i1", type="pve", confirm=True)
        assert "i1" in result
        assert "created" in result.lower()


class TestDeleteSdnIpam:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_ipam(mock_client, ipam="i1")

    async def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            await delete_sdn_ipam(mock_client, ipam="", confirm=True)

    async def test_delete_ipam(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_ipam(mock_client, ipam="i1", confirm=True)
        assert "i1" in result
        assert "deleted" in result.lower()


class TestApplySdn:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await apply_sdn(mock_client)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await apply_sdn(client, confirm=True)

    async def test_apply(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await apply_sdn(mock_client, confirm=True)
        assert "applied" in result.lower()


class TestListNodeSdnZones:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"zone": "zone1", "status": "ok"},
            ]
        )
        result = await list_node_sdn_zones(mock_client, node="pve")
        assert "zone1" in result
        assert "pve" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_node_sdn_zones(mock_client, node="pve")
        assert "No SDN zones" in result

    async def test_default_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_node_sdn_zones(mock_client)
        assert "pve" in result


class TestGetNodeSdnZoneStatus:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"zone": "zone1", "status": "ok"})
        result = await get_node_sdn_zone_status(mock_client, node="pve", zone="zone1")
        assert "zone1" in result
        assert "pve" in result

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await get_node_sdn_zone_status(mock_client, node="pve", zone="")

    async def test_list_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"bridge": "vmbr1", "ports": "vnet1"},
            ]
        )
        result = await get_node_sdn_zone_status(mock_client, node="pve", zone="zone1")
        assert "vmbr1" in result


class TestGetSdnIpamStatus:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"subnet": "10.0.0.0/24", "gateway": "10.0.0.1", "type": "ipv4"},
            ]
        )
        result = await get_sdn_ipam_status(mock_client, ipam="pve")
        assert "10.0.0.0/24" in result
        assert "pve" in result

    async def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            await get_sdn_ipam_status(mock_client, ipam="")

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await get_sdn_ipam_status(mock_client, ipam="pve")
        assert "No IPAM entries" in result


class TestListSdnFabrics:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"fabric": "fab1", "type": "evpn"},
            ]
        )
        result = await list_sdn_fabrics(mock_client)
        assert "fab1" in result
        assert "Fabrics" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_fabrics(mock_client)
        assert "No SDN fabrics" in result


class TestListSdnFabricDetail:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"fabric": "fab1", "type": "evpn"})
        result = await list_sdn_fabric_detail(mock_client, fabric="fab1")
        assert "fab1" in result

    async def test_no_fabric_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric is required"):
            await list_sdn_fabric_detail(mock_client, fabric="")


class TestCreateSdnFabric:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_fabric(mock_client, fabric="f1", type="evpn")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_sdn_fabric(client, fabric="f1", type="evpn", confirm=True)

    async def test_no_fabric_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric is required"):
            await create_sdn_fabric(mock_client, fabric="", type="evpn", confirm=True)

    async def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            await create_sdn_fabric(mock_client, fabric="f1", type="", confirm=True)

    async def test_create_fabric(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_fabric(mock_client, fabric="fab1", type="evpn", confirm=True)
        assert "fab1" in result
        assert "created" in result.lower()


class TestDeleteSdnFabric:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_fabric(mock_client, id="fab1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_sdn_fabric(mock_client, id="", confirm=True)

    async def test_delete_fabric(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_fabric(mock_client, id="fab1", confirm=True)
        assert "fab1" in result
        assert "deleted" in result.lower()


class TestUpdateSdnFabric:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_fabric(mock_client, id="fab1", comment="x")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await update_sdn_fabric(mock_client, id="", confirm=True, comment="x")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_fabric(mock_client, id="fab1", confirm=True)

    async def test_update_fabric(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_fabric(mock_client, id="fab1", comment="new", confirm=True)
        assert "fab1" in result
        assert "updated" in result.lower()


class TestListSdnPrefixLists:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "prefix1"},
            ]
        )
        result = await list_sdn_prefix_lists(mock_client)
        assert "prefix1" in result
        assert "Prefix Lists" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_prefix_lists(mock_client)
        assert "No SDN prefix lists" in result


class TestCreateSdnPrefixList:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_prefix_list(mock_client, id="pl1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_sdn_prefix_list(client, id="pl1", confirm=True)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await create_sdn_prefix_list(mock_client, id="", confirm=True)

    async def test_create_prefix_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_prefix_list(mock_client, id="pl1", confirm=True)
        assert "pl1" in result
        assert "created" in result.lower()


class TestDeleteSdnPrefixList:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_prefix_list(mock_client, id="pl1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_sdn_prefix_list(mock_client, id="", confirm=True)

    async def test_delete_prefix_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_prefix_list(mock_client, id="pl1", confirm=True)
        assert "pl1" in result
        assert "deleted" in result.lower()


class TestListSdnRouteMaps:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "rmap1"},
            ]
        )
        result = await list_sdn_route_maps(mock_client)
        assert "rmap1" in result
        assert "Route Maps" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_route_maps(mock_client)
        assert "No SDN route maps" in result


class TestSdnRollback:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await sdn_rollback(mock_client)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await sdn_rollback(client, confirm=True)

    async def test_rollback(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await sdn_rollback(mock_client, confirm=True)
        assert "rollback" in result.lower()


class TestGetSdnIpam:
    async def test_get_ipam(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"ipam": "pve", "type": "pve"})
        result = await get_sdn_ipam(mock_client, ipam="pve")
        assert "pve" in result

    async def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            await get_sdn_ipam(mock_client, ipam="")


class TestUpdateSdnIpam:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_ipam(mock_client, ipam="pve", comment="x")

    async def test_no_ipam_raises(self, mock_client):
        with pytest.raises(ValueError, match="ipam is required"):
            await update_sdn_ipam(mock_client, ipam="", confirm=True, comment="x")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_ipam(mock_client, ipam="pve", confirm=True)

    async def test_update_ipam(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_ipam(mock_client, ipam="pve", confirm=True, comment="new")
        assert "pve" in result
        assert "updated" in result.lower()


class TestGetSdnDns:
    async def test_get_dns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"dns": "dns1", "type": "dns"})
        result = await get_sdn_dns(mock_client, dns="dns1")
        assert "dns1" in result

    async def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            await get_sdn_dns(mock_client, dns="")


class TestUpdateSdnDns:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_dns(mock_client, dns="d1", comment="x")

    async def test_no_dns_raises(self, mock_client):
        with pytest.raises(ValueError, match="dns is required"):
            await update_sdn_dns(mock_client, dns="", confirm=True, comment="x")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_dns(mock_client, dns="d1", confirm=True)

    async def test_update_dns(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_dns(mock_client, dns="d1", confirm=True, comment="new")
        assert "d1" in result
        assert "updated" in result.lower()


class TestGetSdnController:
    async def test_get_controller(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"controller": "c1", "type": "evpn"})
        result = await get_sdn_controller(mock_client, controller="c1")
        assert "c1" in result

    async def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            await get_sdn_controller(mock_client, controller="")


class TestUpdateSdnController:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_controller(mock_client, controller="c1", comment="x")

    async def test_no_controller_raises(self, mock_client):
        with pytest.raises(ValueError, match="controller is required"):
            await update_sdn_controller(mock_client, controller="", confirm=True, comment="x")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_controller(mock_client, controller="c1", confirm=True)

    async def test_update_controller(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_controller(mock_client, controller="c1", confirm=True, comment="new")
        assert "c1" in result
        assert "updated" in result.lower()


class TestListSdnFabricNodes:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"node": "pve"},
                {"node": "pve2"},
            ]
        )
        result = await list_sdn_fabric_nodes(mock_client, fabric_id="fab1")
        assert "pve" in result
        assert "fab1" in result

    async def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            await list_sdn_fabric_nodes(mock_client, fabric_id="")


class TestAddSdnFabricNode:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await add_sdn_fabric_node(mock_client, fabric_id="f1", node="pve")

    async def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            await add_sdn_fabric_node(mock_client, fabric_id="", node="pve", confirm=True)

    async def test_no_node_raises(self, mock_client):
        with pytest.raises(ValueError, match="node is required"):
            await add_sdn_fabric_node(mock_client, fabric_id="f1", node="", confirm=True)

    async def test_add_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await add_sdn_fabric_node(mock_client, fabric_id="f1", node="pve", confirm=True)
        assert "pve" in result
        assert "f1" in result


class TestGetSdnFabricNode:
    async def test_get_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"node": "pve", "status": "ok"})
        result = await get_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve")
        assert "pve" in result

    async def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            await get_sdn_fabric_node(mock_client, fabric_id="", node_id="pve")

    async def test_no_node_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="node_id is required"):
            await get_sdn_fabric_node(mock_client, fabric_id="f1", node_id="")


class TestUpdateSdnFabricNode:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", comment="x")

    async def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            await update_sdn_fabric_node(mock_client, fabric_id="", node_id="pve", confirm=True, comment="x")

    async def test_no_node_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="node_id is required"):
            await update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="", confirm=True, comment="x")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", confirm=True)

    async def test_update_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", confirm=True, comment="new")
        assert "pve" in result
        assert "updated" in result.lower()


class TestRemoveSdnFabricNode:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await remove_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve")

    async def test_no_fabric_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="fabric_id is required"):
            await remove_sdn_fabric_node(mock_client, fabric_id="", node_id="pve", confirm=True)

    async def test_no_node_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="node_id is required"):
            await remove_sdn_fabric_node(mock_client, fabric_id="f1", node_id="", confirm=True)

    async def test_remove_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await remove_sdn_fabric_node(mock_client, fabric_id="f1", node_id="pve", confirm=True)
        assert "pve" in result
        assert "removed" in result.lower()


class TestCreateSdnVnetIp:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_vnet_ip(mock_client, vnet="v1")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await create_sdn_vnet_ip(mock_client, vnet="", confirm=True)

    async def test_create_ip(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_vnet_ip(mock_client, vnet="v1", confirm=True)
        assert "v1" in result
        assert "created" in result.lower()


class TestUpdateSdnVnetIp:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_vnet_ip(mock_client, vnet="v1", mac="aa:bb:cc")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await update_sdn_vnet_ip(mock_client, vnet="", confirm=True, mac="aa:bb:cc")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_vnet_ip(mock_client, vnet="v1", confirm=True)

    async def test_update_ip(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_vnet_ip(mock_client, vnet="v1", confirm=True, mac="aa:bb:cc")
        assert "v1" in result
        assert "updated" in result.lower()


class TestDeleteSdnVnetIp:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_vnet_ip(mock_client, vnet="v1")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await delete_sdn_vnet_ip(mock_client, vnet="", confirm=True)

    async def test_delete_ip(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_vnet_ip(mock_client, vnet="v1", confirm=True)
        assert "v1" in result
        assert "deleted" in result.lower()


class TestGetSdnVnetFirewallOptions:
    async def test_get_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"enable": 1, "policy_in": "ACCEPT"})
        result = await get_sdn_vnet_firewall_options(mock_client, vnet="v1")
        assert "v1" in result
        assert "enable" in result

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await get_sdn_vnet_firewall_options(mock_client, vnet="")


class TestSetSdnVnetFirewallOptions:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await set_sdn_vnet_firewall_options(mock_client, vnet="v1", enable=1)

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await set_sdn_vnet_firewall_options(mock_client, vnet="", confirm=True, enable=1)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await set_sdn_vnet_firewall_options(mock_client, vnet="v1", confirm=True)

    async def test_set_options(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await set_sdn_vnet_firewall_options(mock_client, vnet="v1", confirm=True, enable=1)
        assert "v1" in result
        assert "firewall options" in result.lower()


class TestListSdnVnetFirewallRules:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"pos": 0, "action": "ACCEPT"},
            ]
        )
        result = await list_sdn_vnet_firewall_rules(mock_client, vnet="v1")
        assert "v1" in result
        assert "ACCEPT" in result

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await list_sdn_vnet_firewall_rules(mock_client, vnet="")

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_sdn_vnet_firewall_rules(mock_client, vnet="v1")
        assert "No firewall rules" in result


class TestCreateSdnVnetFirewallRule:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sdn_vnet_firewall_rule(mock_client, vnet="v1")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await create_sdn_vnet_firewall_rule(mock_client, vnet="", confirm=True)

    async def test_create_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sdn_vnet_firewall_rule(mock_client, vnet="v1", confirm=True, action="ACCEPT")
        assert "v1" in result
        assert "created" in result.lower()


class TestDeleteSdnVnetFirewallRule:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0)

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await delete_sdn_vnet_firewall_rule(mock_client, vnet="", pos=0, confirm=True)

    async def test_delete_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, confirm=True)
        assert "v1" in result
        assert "deleted" in result.lower()


class TestGetSdnVnetFirewallRule:
    async def test_get_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"pos": 0, "action": "ACCEPT"})
        result = await get_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0)
        assert "v1" in result

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await get_sdn_vnet_firewall_rule(mock_client, vnet="", pos=0)


class TestUpdateSdnVnetFirewallRule:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, action="DROP")

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await update_sdn_vnet_firewall_rule(mock_client, vnet="", pos=0, confirm=True, action="DROP")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, confirm=True)

    async def test_update_rule(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_sdn_vnet_firewall_rule(mock_client, vnet="v1", pos=0, confirm=True, action="DROP")
        assert "v1" in result
        assert "updated" in result.lower()


class TestListPrefixListEntries:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"seq": 1, "prefix": "10.0.0.0/8"},
            ]
        )
        result = await list_prefix_list_entries(mock_client, id="pl1")
        assert "pl1" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await list_prefix_list_entries(mock_client, id="")

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_prefix_list_entries(mock_client, id="pl1")
        assert "No prefix list entries" in result


class TestCreatePrefixListEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_prefix_list_entry(mock_client, id="pl1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await create_prefix_list_entry(mock_client, id="", confirm=True)

    async def test_create_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_prefix_list_entry(mock_client, id="pl1", confirm=True)
        assert "pl1" in result
        assert "created" in result.lower()


class TestDeletePrefixListEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_prefix_list_entry(mock_client, id="pl1", url_seq=1)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await delete_prefix_list_entry(mock_client, id="", url_seq=1, confirm=True)

    async def test_delete_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_prefix_list_entry(mock_client, id="pl1", url_seq=1, confirm=True)
        assert "pl1" in result
        assert "deleted" in result.lower()


class TestGetPrefixListEntry:
    async def test_get_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"seq": 1, "prefix": "10.0.0.0/8"})
        result = await get_prefix_list_entry(mock_client, id="pl1", url_seq=1)
        assert "pl1" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await get_prefix_list_entry(mock_client, id="", url_seq=1)


class TestUpdatePrefixListEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_prefix_list_entry(mock_client, id="pl1", url_seq=1, prefix="10.0.0.0/8")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await update_prefix_list_entry(mock_client, id="", url_seq=1, confirm=True, prefix="10.0.0.0/8")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_prefix_list_entry(mock_client, id="pl1", url_seq=1, confirm=True)

    async def test_update_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_prefix_list_entry(mock_client, id="pl1", url_seq=1, confirm=True, prefix="10.0.0.0/8")
        assert "pl1" in result
        assert "updated" in result.lower()


class TestListRouteMapEntries:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "rm1"},
            ]
        )
        result = await list_route_map_entries(mock_client)
        assert "rm1" in result
        assert "Route Map Entries" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_route_map_entries(mock_client)
        assert "No route map entries" in result


class TestCreateRouteMapEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_route_map_entry(mock_client, route_map_id="rm1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            await create_route_map_entry(mock_client, route_map_id="", confirm=True)

    async def test_create_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_route_map_entry(mock_client, route_map_id="rm1", confirm=True)
        assert "rm1" in result
        assert "created" in result.lower()


class TestGetRouteMapEntry:
    async def test_get_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"order": 10},
            ]
        )
        result = await get_route_map_entry(mock_client, route_map_id="rm1")
        assert "rm1" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            await get_route_map_entry(mock_client, route_map_id="")

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await get_route_map_entry(mock_client, route_map_id="rm1")
        assert "No entries" in result


class TestDeleteRouteMapEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_route_map_entry(mock_client, route_map_id="rm1", order=10)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            await delete_route_map_entry(mock_client, route_map_id="", order=10, confirm=True)

    async def test_delete_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_route_map_entry(mock_client, route_map_id="rm1", order=10, confirm=True)
        assert "rm1" in result
        assert "deleted" in result.lower()


class TestUpdateRouteMapEntry:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_route_map_entry(mock_client, route_map_id="rm1", order=10, action="permit")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="route_map_id is required"):
            await update_route_map_entry(mock_client, route_map_id="", order=10, confirm=True, action="permit")

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one parameter"):
            await update_route_map_entry(mock_client, route_map_id="rm1", order=10, confirm=True)

    async def test_update_entry(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await update_route_map_entry(mock_client, route_map_id="rm1", order=10, confirm=True, action="permit")
        assert "rm1" in result
        assert "updated" in result.lower()


class TestSdnDryRun:
    async def test_dry_run_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"changes": "pending"})
        result = await sdn_dry_run(mock_client)
        assert "Dry-Run" in result

    async def test_dry_run_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"zone": "z1", "status": "changed"},
            ]
        )
        result = await sdn_dry_run(mock_client)
        assert "Dry-Run" in result

    async def test_dry_run_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await sdn_dry_run(mock_client)
        assert "Dry-Run" in result


class TestGetNodeSdnVnet:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"vnet": "v1", "zone": "z1"})
        result = await get_node_sdn_vnet(mock_client, node="pve", vnet="v1")
        assert "v1" in result
        assert "pve" in result

    async def test_no_vnet_raises(self, mock_client):
        with pytest.raises(ValueError, match="vnet is required"):
            await get_node_sdn_vnet(mock_client, node="pve", vnet="")

    async def test_default_node(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"vnet": "v1"})
        result = await get_node_sdn_vnet(mock_client, vnet="v1")
        assert "pve" in result


class TestListNodeSdnZoneBridges:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"bridge": "vmbr1"},
            ]
        )
        result = await list_node_sdn_zone_bridges(mock_client, node="pve", zone="z1")
        assert "vmbr1" in result
        assert "z1" in result

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await list_node_sdn_zone_bridges(mock_client, node="pve", zone="")

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_node_sdn_zone_bridges(mock_client, node="pve", zone="z1")
        assert "No bridges" in result


class TestGetNodeSdnZoneContent:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"zone": "z1", "content": "data"})
        result = await get_node_sdn_zone_content(mock_client, node="pve", zone="z1")
        assert "z1" in result

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await get_node_sdn_zone_content(mock_client, node="pve", zone="")


class TestGetNodeSdnZoneIpVrf:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"vrf": "vrf0"})
        result = await get_node_sdn_zone_ip_vrf(mock_client, node="pve", zone="z1")
        assert "z1" in result
        assert "IP-VRF" in result

    async def test_no_zone_raises(self, mock_client):
        with pytest.raises(ValueError, match="zone is required"):
            await get_node_sdn_zone_ip_vrf(mock_client, node="pve", zone="")
