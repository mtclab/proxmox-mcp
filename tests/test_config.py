import os
from unittest.mock import patch

import pytest

from proxmox_mcp.config import Config


class TestConfigFromEnv:
    async def test_valid_config(self, env_vars: dict[str, str]) -> None:
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            assert config.url == "https://10.96.16.19:8006"
            assert config.verify is False
            assert config.monitor_token_id == "zabbix@pve!zabbix"
            assert config.admin_token_id == "homepilot@pve!homepilot"
            assert config.allow_elevated is True
            assert config.default_node == "pve"

    async def test_missing_url(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_URL"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="PROXMOX_URL is required"):
                Config.from_env()

    async def test_missing_monitor_token_id(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_MONITOR_TOKEN_ID"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="PROXMOX_MONITOR_TOKEN_ID is required"):
                Config.from_env()

    async def test_missing_monitor_token_secret(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_MONITOR_TOKEN_SECRET"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="PROXMOX_MONITOR_TOKEN_SECRET is required"):
                Config.from_env()

    async def test_missing_admin_token_id(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_ADMIN_TOKEN_ID"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="PROXMOX_ADMIN_TOKEN_ID is required"):
                Config.from_env()

    async def test_missing_admin_token_secret(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_ADMIN_TOKEN_SECRET"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="PROXMOX_ADMIN_TOKEN_SECRET is required"):
                Config.from_env()

    async def test_invalid_token_format(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_MONITOR_TOKEN_ID": "bad-token"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="user@realm!tokenid format"):
                Config.from_env()

    async def test_invalid_url_http(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_URL": "http://10.96.16.19:8006"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="must start with https://"):
                Config.from_env()

    async def test_invalid_url_no_protocol(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_URL": "10.96.16.19:8006"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="must start with https://"):
                Config.from_env()

    async def test_allow_elevated_false(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_ALLOW_ELEVATED": "false"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.allow_elevated is False

    async def test_allow_elevated_defaults_false(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_ALLOW_ELEVATED"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.allow_elevated is False

    async def test_verify_path(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_VERIFY": "/etc/ssl/certs/my-ca.pem"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.verify == "/etc/ssl/certs/my-ca.pem"

    async def test_verify_true(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_VERIFY": "true"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.verify is True

    async def test_default_node_none(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_DEFAULT_NODE"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.default_node is None

    async def test_host_property(self) -> None:
        config = Config(
            url="https://myhost:8006",
            verify=True,
            monitor_token_id="u@r!t",
            monitor_token_secret="s",
            admin_token_id="u@r!t2",
            admin_token_secret="s2",
        )
        assert config.host == "myhost"

    async def test_port_property(self) -> None:
        config = Config(
            url="https://myhost:8006",
            verify=True,
            monitor_token_id="u@r!t",
            monitor_token_secret="s",
            admin_token_id="u@r!t2",
            admin_token_secret="s2",
        )
        assert config.port == 8006

    async def test_port_default(self) -> None:
        config = Config(
            url="https://myhost",
            verify=True,
            monitor_token_id="u@r!t",
            monitor_token_secret="s",
            admin_token_id="u@r!t2",
            admin_token_secret="s2",
        )
        assert config.port == 8006

    async def test_allowed_commands_from_env(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_ALLOWED_COMMANDS": "ls,cat,ping,hostname"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.allowed_commands == ["ls", "cat", "ping", "hostname"]

    async def test_allowed_commands_empty_means_none(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_ALLOWED_COMMANDS": ""}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.allowed_commands is None

    async def test_allowed_commands_unset_means_none(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_ALLOWED_COMMANDS"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.allowed_commands is None

    async def test_upload_dir_from_env(self, env_vars: dict[str, str]) -> None:
        env = {**env_vars, "PROXMOX_UPLOAD_DIR": "/tmp/uploads"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.upload_dir == "/tmp/uploads"

    async def test_upload_dir_unset_means_none(self, env_vars: dict[str, str]) -> None:
        env = {k: v for k, v in env_vars.items() if k != "PROXMOX_UPLOAD_DIR"}
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()
            assert config.upload_dir is None
