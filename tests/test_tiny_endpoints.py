from unittest.mock import MagicMock, patch

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
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            create_domain(mock_client, realm="test", type="ldap")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            create_domain(client, realm="test", type="ldap", confirm=True)

    def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            create_domain(mock_client, realm="", type="ldap", confirm=True)

    def test_no_type_raises(self, mock_client):
        with pytest.raises(ValueError, match="type is required"):
            create_domain(mock_client, realm="test", type="", confirm=True)

    def test_create_domain(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = create_domain(mock_client, realm="ldap", type="ldap", confirm=True)
        assert "ldap" in result
        assert "created" in result

    def test_create_domain_with_kwargs(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = create_domain(
            mock_client, realm="ldap", type="ldap", comment="test", confirm=True
        )
        assert "ldap" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["comment"] == "test"


class TestUpdateDomain:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_domain(mock_client, realm="pve")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_domain(client, realm="pve", confirm=True)

    def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            update_domain(mock_client, realm="", confirm=True)

    def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            update_domain(mock_client, realm="pve", confirm=True)

    def test_update_domain(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_domain(mock_client, realm="pve", comment="updated", confirm=True)
        assert "pve" in result
        assert "updated" in result


class TestDeleteDomain:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_domain(mock_client, realm="test")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_domain(client, realm="test", confirm=True)

    def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            delete_domain(mock_client, realm="", confirm=True)

    def test_delete_domain(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_domain(mock_client, realm="ldap", confirm=True)
        assert "ldap" in result
        assert "deleted" in result


class TestGetUserTfaTypes:
    def test_no_userid_raises(self, mock_client):
        with pytest.raises(ValueError, match="userid is required"):
            get_user_tfa_types(mock_client, userid="")

    def test_get_user_tfa_types_list(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=[
            {"type": "totp"},
            {"type": "webauthn"},
        ])
        result = get_user_tfa_types(mock_client, userid="admin@pve")
        assert "admin@pve" in result

    def test_get_user_tfa_types_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"totp": "enabled"})
        result = get_user_tfa_types(mock_client, userid="admin@pve")
        assert "admin@pve" in result

    def test_get_user_tfa_types_empty(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value=None)
        result = get_user_tfa_types(mock_client, userid="admin@pve")
        assert "No TFA types found" in result


class TestOpenidAuthUrl:
    def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            openid_auth_url(mock_client, realm="")

    def test_openid_auth_url_with_url(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={
            "data": "https://idp.example.com/auth?state=abc",
        })
        result = openid_auth_url(mock_client, realm="ldap")
        assert "OpenID Auth URL" in result

    def test_openid_auth_url_dict_no_url_key(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"redirect": "https://idp.example.com"})
        result = openid_auth_url(mock_client, realm="ldap")
        assert "OpenID Auth URL" in result

    def test_openid_auth_url_string(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="https://idp.example.com/auth")
        result = openid_auth_url(mock_client, realm="ldap")
        assert "OpenID Auth URL" in result


class TestOpenidLogin:
    def test_no_realm_raises(self, mock_client):
        with pytest.raises(ValueError, match="realm is required"):
            openid_login(mock_client, realm="", code="abc")

    def test_no_code_raises(self, mock_client):
        with pytest.raises(ValueError, match="code is required"):
            openid_login(mock_client, realm="ldap", code="")

    def test_openid_login(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"ticket": "abc123"}})
        result = openid_login(mock_client, realm="ldap", code="auth-code")
        assert "OpenID Login" in result

    def test_openid_login_with_state(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": {"ticket": "abc"}})
        result = openid_login(mock_client, realm="ldap", code="code", state="state123")
        assert "OpenID Login" in result
        call_args = mock_client.safe_api_call.call_args
        assert call_args[1]["state"] == "state123"


class TestUpdateSnapshotConfig:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            update_snapshot_config(mock_client, node="pve", vmid=100, snapname="snap1")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            update_snapshot_config(client, node="pve", vmid=100, snapname="snap1", confirm=True)

    def test_invalid_vmtype_raises(self, mock_client):
        with pytest.raises(ValueError, match="Invalid vmtype"):
            update_snapshot_config(
                mock_client, node="pve", vmid=100, snapname="snap1", vmtype="evil", confirm=True
            )

    def test_update_snapshot_config(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_snapshot_config(
            mock_client, node="pve", vmid=100, snapname="snap1", description="updated", confirm=True
        )
        assert "snap1" in result
        assert "updated" in result

    def test_update_snapshot_config_lxc(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = update_snapshot_config(
            mock_client, node="pve", vmid=200, snapname="snap1", vmtype="lxc", confirm=True
        )
        assert "lxc" in result


class TestDeleteSubscription:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            delete_subscription(mock_client, node="pve")

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            delete_subscription(client, node="pve", confirm=True)

    def test_delete_subscription(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = delete_subscription(mock_client, node="pve", confirm=True)
        assert "pve" in result
        assert "deleted" in result.lower()


class TestAcquireSdnLock:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            acquire_sdn_lock(mock_client)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            acquire_sdn_lock(client, confirm=True)

    def test_acquire_sdn_lock(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value="UPID:pve:123:abc")
        result = acquire_sdn_lock(mock_client, confirm=True)
        assert "SDN lock acquired" in result

    def test_acquire_sdn_lock_dict(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "UPID:pve:456:def"})
        result = acquire_sdn_lock(mock_client, confirm=True)
        assert "UPID" in result


class TestReleaseSdnLock:
    def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            release_sdn_lock(mock_client)

    def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            release_sdn_lock(client, confirm=True)

    def test_release_sdn_lock(self, mock_client):
        mock_client.safe_api_call = MagicMock(return_value={"data": "OK"})
        result = release_sdn_lock(mock_client, confirm=True)
        assert "SDN lock released" in result
