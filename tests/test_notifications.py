from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp.config import Config
from proxmox_mcp.notifications import (
    create_gotify_endpoint,
    create_sendmail_endpoint,
    create_smtp_endpoint,
    create_webhook_endpoint,
    delete_gotify_endpoint,
    delete_sendmail_endpoint,
    delete_smtp_endpoint,
    delete_webhook_endpoint,
    get_notification_matcher,
    list_gotify_endpoints,
    list_notification_matchers,
    list_notification_targets,
    list_sendmail_endpoints,
    list_smtp_endpoints,
    list_webhook_endpoints,
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


class TestListNotificationTargets:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "target1", "type": "sendmail"},
                {"name": "target2", "type": "gotify"},
            ]
        )
        result = await list_notification_targets(mock_client)
        assert "Notification Targets" in result
        assert "target1" in result
        assert "target2" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_notification_targets(mock_client)
        assert "No notification targets found" in result


class TestListNotificationMatchers:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "matcher1", "comment": "test"},
            ]
        )
        result = await list_notification_matchers(mock_client)
        assert "Notification Matchers" in result
        assert "matcher1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await list_notification_matchers(mock_client)
        assert "No notification matchers found" in result


class TestGetNotificationMatcher:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "matcher1"})
        result = await get_notification_matcher(mock_client, name="matcher1")
        assert "matcher1" in result

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await get_notification_matcher(mock_client, name="")


class TestListSendmailEndpoints:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "email1", "comment": "test"},
            ]
        )
        result = await list_sendmail_endpoints(mock_client)
        assert "Sendmail" in result
        assert "email1" in result


class TestCreateSendmailEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_sendmail_endpoint(mock_client, name="test")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await create_sendmail_endpoint(client, name="test", confirm=True)

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_sendmail_endpoint(mock_client, name="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_sendmail_endpoint(mock_client, name="test", confirm=True)
        assert "test" in result
        assert "created" in result.lower()


class TestDeleteSendmailEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_sendmail_endpoint(mock_client, name="test")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await delete_sendmail_endpoint(mock_client, name="", confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_sendmail_endpoint(mock_client, name="test", confirm=True)
        assert "test" in result
        assert "deleted" in result.lower()


class TestListSmtpEndpoints:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "smtp1", "server": "mail.example.com"},
            ]
        )
        result = await list_smtp_endpoints(mock_client)
        assert "SMTP" in result
        assert "smtp1" in result


class TestCreateSmtpEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_smtp_endpoint(mock_client, name="test")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_smtp_endpoint(mock_client, name="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_smtp_endpoint(mock_client, name="test", server="mail.example.com", confirm=True)
        assert "test" in result


class TestDeleteSmtpEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_smtp_endpoint(mock_client, name="test")

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_smtp_endpoint(mock_client, name="test", confirm=True)
        assert "deleted" in result.lower()


class TestListGotifyEndpoints:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "gotify1"},
            ]
        )
        result = await list_gotify_endpoints(mock_client)
        assert "Gotify" in result
        assert "gotify1" in result


class TestCreateGotifyEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_gotify_endpoint(mock_client, name="test")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_gotify_endpoint(mock_client, name="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_gotify_endpoint(mock_client, name="test", confirm=True)
        assert "test" in result
        assert "created" in result.lower()


class TestDeleteGotifyEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_gotify_endpoint(mock_client, name="test")

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_gotify_endpoint(mock_client, name="test", confirm=True)
        assert "deleted" in result.lower()


class TestListWebhookEndpoints:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"name": "hook1"},
            ]
        )
        result = await list_webhook_endpoints(mock_client)
        assert "Webhook" in result
        assert "hook1" in result


class TestCreateWebhookEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await create_webhook_endpoint(mock_client, name="test")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await create_webhook_endpoint(mock_client, name="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await create_webhook_endpoint(mock_client, name="test", confirm=True)
        assert "test" in result
        assert "created" in result.lower()


class TestDeleteWebhookEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await delete_webhook_endpoint(mock_client, name="test")

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await delete_webhook_endpoint(mock_client, name="test", confirm=True)
        assert "deleted" in result.lower()
