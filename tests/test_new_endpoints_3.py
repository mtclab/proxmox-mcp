from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxmox_mcp import (
    acme as acme_mod,
)
from proxmox_mcp import (
    cluster as cluster_mod,
)
from proxmox_mcp import (
    mapping as mapping_mod,
)
from proxmox_mcp import (
    metrics as metrics_mod,
)
from proxmox_mcp import (
    notifications as notif_mod,
)
from proxmox_mcp.config import Config

notif_get_notification_target = notif_mod.get_notification_target
notif_test_notification_target = notif_mod.test_notification_target
notif_notification_index = notif_mod.notification_index
notif_notification_endpoints_index = notif_mod.notification_endpoints_index
notif_notification_matcher_fields = notif_mod.notification_matcher_fields
notif_notification_matcher_field_values = notif_mod.notification_matcher_field_values
notif_create_notification_matcher = notif_mod.create_notification_matcher
notif_update_notification_matcher = notif_mod.update_notification_matcher
notif_delete_notification_matcher = notif_mod.delete_notification_matcher
notif_get_sendmail_endpoint = notif_mod.get_sendmail_endpoint
notif_update_sendmail_endpoint = notif_mod.update_sendmail_endpoint
notif_get_smtp_endpoint = notif_mod.get_smtp_endpoint
notif_update_smtp_endpoint = notif_mod.update_smtp_endpoint
notif_get_gotify_endpoint = notif_mod.get_gotify_endpoint
notif_update_gotify_endpoint = notif_mod.update_gotify_endpoint
notif_get_webhook_endpoint = notif_mod.get_webhook_endpoint
notif_update_webhook_endpoint = notif_mod.update_webhook_endpoint
acme_get_acme_plugin = acme_mod.get_acme_plugin
acme_update_acme_plugin = acme_mod.update_acme_plugin
acme_acme_meta = acme_mod.acme_meta
mapping_mapping_index = mapping_mod.mapping_index
mapping_list_dir_mappings = mapping_mod.list_dir_mappings
mapping_get_dir_mapping = mapping_mod.get_dir_mapping
mapping_create_dir_mapping = mapping_mod.create_dir_mapping
mapping_update_dir_mapping = mapping_mod.update_dir_mapping
mapping_delete_dir_mapping = mapping_mod.delete_dir_mapping
metrics_metrics_index = metrics_mod.metrics_index
metrics_export_metrics = metrics_mod.export_metrics
cluster_cluster_config_totem = cluster_mod.cluster_config_totem
cluster_cluster_config_qdevice = cluster_mod.cluster_config_qdevice
cluster_backup_info_index = cluster_mod.backup_info_index
cluster_backup_job_included_volumes = cluster_mod.backup_job_included_volumes


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


class TestNotificationIndex:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"endpoints": 3, "matchers": 1})
        result = await notif_notification_index(mock_client)
        assert "Notification Index" in result

    async def test_non_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="some data")
        result = await notif_notification_index(mock_client)
        assert "some data" in result


class TestNotificationEndpointsIndex:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"sendmail": 1, "smtp": 1})
        result = await notif_notification_endpoints_index(mock_client)
        assert "Notification Endpoints Index" in result


class TestGetNotificationTarget:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "target1", "type": "sendmail"})
        result = await notif_get_notification_target(mock_client, name="target1")
        assert "target1" in result

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_get_notification_target(mock_client, name="")


class TestTestNotificationTarget:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_test_notification_target(mock_client, name="target1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await notif_test_notification_target(client, name="target1", confirm=True)

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_test_notification_target(mock_client, name="", confirm=True)

    async def test_test(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_test_notification_target(mock_client, name="target1", confirm=True)
        assert "target1" in result


class TestNotificationMatcherFields:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"name": "field1"}])
        result = await notif_notification_matcher_fields(mock_client)
        assert "Matcher Fields" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await notif_notification_matcher_fields(mock_client)
        assert "No matcher fields found" in result


class TestNotificationMatcherFieldValues:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"name": "value1"}])
        result = await notif_notification_matcher_field_values(mock_client)
        assert "Matcher Field Values" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await notif_notification_matcher_field_values(mock_client)
        assert "No matcher field values found" in result


class TestCreateNotificationMatcher:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_create_notification_matcher(mock_client, name="m1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await notif_create_notification_matcher(client, name="m1", confirm=True)

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_create_notification_matcher(mock_client, name="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_create_notification_matcher(mock_client, name="m1", confirm=True)
        assert "m1" in result
        assert "created" in result.lower()


class TestUpdateNotificationMatcher:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_update_notification_matcher(mock_client, name="m1")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_update_notification_matcher(mock_client, name="", comment="x", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await notif_update_notification_matcher(mock_client, name="m1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_update_notification_matcher(mock_client, name="m1", comment="updated", confirm=True)
        assert "m1" in result
        assert "updated" in result.lower()


class TestDeleteNotificationMatcher:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_delete_notification_matcher(mock_client, name="m1")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_delete_notification_matcher(mock_client, name="", confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_delete_notification_matcher(mock_client, name="m1", confirm=True)
        assert "m1" in result
        assert "deleted" in result.lower()


class TestGetSendmailEndpoint:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "sm1", "mailto": "a@b.com"})
        result = await notif_get_sendmail_endpoint(mock_client, name="sm1")
        assert "sm1" in result

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_get_sendmail_endpoint(mock_client, name="")


class TestUpdateSendmailEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_update_sendmail_endpoint(mock_client, name="sm1")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_update_sendmail_endpoint(mock_client, name="", comment="x", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await notif_update_sendmail_endpoint(mock_client, name="sm1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_update_sendmail_endpoint(mock_client, name="sm1", comment="updated", confirm=True)
        assert "sm1" in result


class TestGetSmtpEndpoint:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "smtp1", "server": "mail.com"})
        result = await notif_get_smtp_endpoint(mock_client, name="smtp1")
        assert "smtp1" in result

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_get_smtp_endpoint(mock_client, name="")


class TestUpdateSmtpEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_update_smtp_endpoint(mock_client, name="smtp1")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_update_smtp_endpoint(mock_client, name="", comment="x", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await notif_update_smtp_endpoint(mock_client, name="smtp1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_update_smtp_endpoint(mock_client, name="smtp1", comment="updated", confirm=True)
        assert "smtp1" in result


class TestGetGotifyEndpoint:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "got1", "server": "gotify.local"})
        result = await notif_get_gotify_endpoint(mock_client, name="got1")
        assert "got1" in result

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_get_gotify_endpoint(mock_client, name="")


class TestUpdateGotifyEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_update_gotify_endpoint(mock_client, name="got1")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_update_gotify_endpoint(mock_client, name="", comment="x", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await notif_update_gotify_endpoint(mock_client, name="got1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_update_gotify_endpoint(mock_client, name="got1", comment="updated", confirm=True)
        assert "got1" in result


class TestGetWebhookEndpoint:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"name": "wh1", "url": "https://hook.local"})
        result = await notif_get_webhook_endpoint(mock_client, name="wh1")
        assert "wh1" in result

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_get_webhook_endpoint(mock_client, name="")


class TestUpdateWebhookEndpoint:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await notif_update_webhook_endpoint(mock_client, name="wh1")

    async def test_no_name_raises(self, mock_client):
        with pytest.raises(ValueError, match="name is required"):
            await notif_update_webhook_endpoint(mock_client, name="", comment="x", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await notif_update_webhook_endpoint(mock_client, name="wh1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await notif_update_webhook_endpoint(mock_client, name="wh1", comment="updated", confirm=True)
        assert "wh1" in result


class TestGetAcmePlugin:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"plugin": "dns_ACME", "type": "dns"})
        result = await acme_get_acme_plugin(mock_client, id="dns_ACME")
        assert "dns_ACME" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await acme_get_acme_plugin(mock_client, id="")


class TestUpdateAcmePlugin:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await acme_update_acme_plugin(mock_client, id="p1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await acme_update_acme_plugin(mock_client, id="", api="new", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await acme_update_acme_plugin(mock_client, id="p1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await acme_update_acme_plugin(mock_client, id="p1", api="updated", confirm=True)
        assert "p1" in result


class TestAcmeMeta:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"termsOfService": "https://example.com/tos"})
        result = await acme_acme_meta(mock_client)
        assert "ACME Meta" in result


class TestMappingIndex:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"id": "pci-maps", "type": "pci"}])
        result = await mapping_mapping_index(mock_client)
        assert "Mapping Index" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await mapping_mapping_index(mock_client)
        assert "No mappings found" in result


class TestListDirMappings:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"id": "dir1", "description": "test"}])
        result = await mapping_list_dir_mappings(mock_client)
        assert "Directory Mappings" in result
        assert "dir1" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await mapping_list_dir_mappings(mock_client)
        assert "No directory mappings found" in result


class TestGetDirMapping:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"id": "dir1", "path": "/mnt/data"})
        result = await mapping_get_dir_mapping(mock_client, id="dir1")
        assert "dir1" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await mapping_get_dir_mapping(mock_client, id="")


class TestCreateDirMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await mapping_create_dir_mapping(mock_client, id="dir1")

    async def test_requires_elevated(self, mock_config):
        mock_config.allow_elevated = False
        with patch("proxmox_mcp.client.ProxmoxAPI"):
            from proxmox_mcp.client import ProxmoxClient

            client = ProxmoxClient(mock_config)
        with pytest.raises(ValueError, match="Elevated"):
            await mapping_create_dir_mapping(client, id="dir1", confirm=True)

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await mapping_create_dir_mapping(mock_client, id="", confirm=True)

    async def test_create(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await mapping_create_dir_mapping(mock_client, id="dir1", description="test", confirm=True)
        assert "dir1" in result
        assert "created" in result.lower()


class TestUpdateDirMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await mapping_update_dir_mapping(mock_client, id="dir1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await mapping_update_dir_mapping(mock_client, id="", description="x", confirm=True)

    async def test_no_params_raises(self, mock_client):
        with pytest.raises(ValueError, match="At least one"):
            await mapping_update_dir_mapping(mock_client, id="dir1", confirm=True)

    async def test_update(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await mapping_update_dir_mapping(mock_client, id="dir1", description="updated", confirm=True)
        assert "dir1" in result
        assert "updated" in result.lower()


class TestDeleteDirMapping:
    async def test_requires_confirm(self, mock_client):
        with pytest.raises(ValueError, match="confirm=true"):
            await mapping_delete_dir_mapping(mock_client, id="dir1")

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await mapping_delete_dir_mapping(mock_client, id="", confirm=True)

    async def test_delete(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=None)
        result = await mapping_delete_dir_mapping(mock_client, id="dir1", confirm=True)
        assert "dir1" in result
        assert "deleted" in result.lower()


class TestMetricsIndex:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"server": 1, "export": 1})
        result = await metrics_metrics_index(mock_client)
        assert "Metrics Index" in result


class TestExportMetrics:
    async def test_returns_formatted_list(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"id": "metric1", "value": 42},
            ]
        )
        result = await metrics_export_metrics(mock_client)
        assert "Cluster Metrics Export" in result
        assert "metric1" in result

    async def test_returns_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await metrics_export_metrics(mock_client)
        assert "No metrics data found" in result

    async def test_dict_result(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"key1": "val1"})
        result = await metrics_export_metrics(mock_client)
        assert "key1" in result


class TestClusterConfigTotem:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"token": "12345", "version": 2}})
        result = await cluster_cluster_config_totem(mock_client)
        assert "Totem" in result

    async def test_non_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="some data")
        result = await cluster_cluster_config_totem(mock_client)
        assert "some data" in result


class TestClusterConfigQdevice:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value={"data": {"state": "active"}})
        result = await cluster_cluster_config_qdevice(mock_client)
        assert "QDevice" in result

    async def test_non_dict(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value="some data")
        result = await cluster_cluster_config_qdevice(mock_client)
        assert "some data" in result


class TestBackupInfoIndex:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[{"id": "policy1"}])
        result = await cluster_backup_info_index(mock_client)
        assert "Backup Info Index" in result

    async def test_empty(self, mock_client):
        mock_client.safe_api_call = AsyncMock(return_value=[])
        result = await cluster_backup_info_index(mock_client)
        assert "No backup info entries found" in result


class TestBackupJobIncludedVolumes:
    async def test_returns_formatted(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value=[
                {"vmid": 100, "type": "qemu"},
            ]
        )
        result = await cluster_backup_job_included_volumes(mock_client, id="job1")
        assert "job1" in result
        assert "100" in result

    async def test_no_id_raises(self, mock_client):
        with pytest.raises(ValueError, match="id is required"):
            await cluster_backup_job_included_volumes(mock_client, id="")

    async def test_dict_data(self, mock_client):
        mock_client.safe_api_call = AsyncMock(
            return_value={
                "data": [{"vmid": 200, "type": "lxc"}],
            }
        )
        result = await cluster_backup_job_included_volumes(mock_client, id="job2")
        assert "job2" in result
