from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.access import (
    create_domain,
    delete_domain,
    get_user_tfa_types,
    openid_auth_url,
    openid_login,
    update_domain,
)
from proxmox_mcp.config import Config
from proxmox_mcp.nodes import delete_subscription
from proxmox_mcp.sdn import acquire_sdn_lock, release_sdn_lock
from proxmox_mcp.snapshots import update_snapshot_config


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


class TestCreateDomain:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_domain(mock_client, realm="test", type="ldap")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_domain(client, realm="test", type="ldap", confirm=True)

    async def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            await create_domain(mock_client, realm="", type="ldap", confirm=True)

    async def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            await create_domain(mock_client, realm="test", type="", confirm=True)

    async def test_create_domain(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await create_domain(mock_client, realm="ldap", type="ldap", confirm=True)
        assert "ldap" in result
        assert "created" in result

    async def test_create_domain_with_kwargs(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await create_domain(mock_client, realm="ldap", type="ldap", comment="test", confirm=True)
        assert "ldap" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test"


class TestUpdateDomain:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_domain(mock_client, realm="pve")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_domain(client, realm="pve", confirm=True)

    async def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            await update_domain(mock_client, realm="", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await update_domain(mock_client, realm="pve", confirm=True)

    async def test_update_domain(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await update_domain(mock_client, realm="pve", comment="updated", confirm=True)
        assert "pve" in result
        assert "updated" in result


class TestDeleteDomain:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_domain(mock_client, realm="test")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_domain(client, realm="test", confirm=True)

    async def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            await delete_domain(mock_client, realm="", confirm=True)

    async def test_delete_domain(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await delete_domain(mock_client, realm="ldap", confirm=True)
        assert "ldap" in result
        assert "deleted" in result


class TestGetUserTfaTypes:
    async def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            await get_user_tfa_types(mock_client, userid="")

    async def test_get_user_tfa_types_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"type": "totp"},
                {"type": "webauthn"},
            ]
        )
        result = await get_user_tfa_types(mock_client, userid="admin@pve")
        assert "admin@pve" in result

    async def test_get_user_tfa_types_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"totp": "enabled"})
        result = await get_user_tfa_types(mock_client, userid="admin@pve")
        assert "admin@pve" in result

    async def test_get_user_tfa_types_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await get_user_tfa_types(mock_client, userid="admin@pve")
        assert "No TFA types found" in result


class TestOpenidAuthUrl:
    async def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            await openid_auth_url(mock_client, realm="")

    async def test_openid_auth_url_with_url(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": "https://idp.example.com/auth?state=abc",
            }
        )
        result = await openid_auth_url(mock_client, realm="ldap")
        assert "OpenID Auth URL" in result

    async def test_openid_auth_url_dict_no_url_key(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"redirect": "https://idp.example.com"})
        result = await openid_auth_url(mock_client, realm="ldap")
        assert "OpenID Auth URL" in result

    async def test_openid_auth_url_string(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="https://idp.example.com/auth")
        result = await openid_auth_url(mock_client, realm="ldap")
        assert "OpenID Auth URL" in result


class TestOpenidLogin:
    async def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            await openid_login(mock_client, realm="", code="abc")

    async def test_no_code_raises(self, mock_client):
        with pytest.raises(ValueError, match="code is required"):
            await openid_login(mock_client, realm="ldap", code="")

    async def test_openid_login(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"ticket": "abc123"}})
        result = await openid_login(mock_client, realm="ldap", code="auth-code")
        assert "OpenID Login" in result

    async def test_openid_login_with_state(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"ticket": "abc"}})
        result = await openid_login(mock_client, realm="ldap", code="code", state="state123")
        assert "OpenID Login" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["state"] == "state123"


class TestUpdateSnapshotConfig:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await update_snapshot_config(mock_client, node="pve", vmid=100, snapname="snap1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await update_snapshot_config(client, node="pve", vmid=100, snapname="snap1", confirm=True)

    async def test_invalid_vmtype_raises(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            await update_snapshot_config(
                mock_client, node="pve", vmid=100, snapname="snap1", vmtype="evil", confirm=True
            )

    async def test_update_snapshot_config(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await update_snapshot_config(
            mock_client, node="pve", vmid=100, snapname="snap1", description="updated", confirm=True
        )
        assert "snap1" in result
        assert "updated" in result

    async def test_update_snapshot_config_lxc(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await update_snapshot_config(
            mock_client, node="pve", vmid=200, snapname="snap1", vmtype="lxc", confirm=True
        )
        assert "lxc" in result


class TestDeleteSubscription:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_subscription(mock_client, node="pve")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await delete_subscription(client, node="pve", confirm=True)

    async def test_delete_subscription(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await delete_subscription(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "deleted" in result.lower()


class TestAcquireSdnLock:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await acquire_sdn_lock(mock_client)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await acquire_sdn_lock(client, confirm=True)

    async def test_acquire_sdn_lock(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="UPID:pve:123:abc")
        result = await acquire_sdn_lock(mock_client, confirm=True)
        assert "SDN lock acquired" in result

    async def test_acquire_sdn_lock_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "UPID:pve:456:def"})
        result = await acquire_sdn_lock(mock_client, confirm=True)
        assert "UPID" in result


class TestReleaseSdnLock:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await release_sdn_lock(mock_client)

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await release_sdn_lock(client, confirm=True)

    async def test_release_sdn_lock(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": "OK"})
        result = await release_sdn_lock(mock_client, confirm=True)
        assert "SDN lock released" in result
