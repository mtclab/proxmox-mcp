from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_TOKEN_RE = re.compile(r"^.+@.+\!.+$")


class Config:
    def __init__(
        self,
        url: str,
        verify: str | bool,
        monitor_token_id: str,
        monitor_token_secret: str,
        admin_token_id: str,
        admin_token_secret: str,
        allow_elevated: bool = False,
        default_node: Optional[str] = None,
        allowed_commands: Optional[list[str]] = None,
        upload_dir: Optional[str] = None,
    ) -> None:
        self.url = url
        self.verify = verify
        self.monitor_token_id = monitor_token_id
        self.monitor_token_secret = monitor_token_secret
        self.admin_token_id = admin_token_id
        self.admin_token_secret = admin_token_secret
        self.allow_elevated = allow_elevated
        self.default_node = default_node
        self.allowed_commands = allowed_commands
        self.upload_dir = upload_dir

        self._validate()

    def _validate(self) -> None:
        if not self.url.startswith("https://"):
            raise ValueError(f"PROXMOX_URL must start with https:// — got {self.url!r}")

        for label, tid in [
            ("PROXMOX_MONITOR_TOKEN_ID", self.monitor_token_id),
            ("PROXMOX_ADMIN_TOKEN_ID", self.admin_token_id),
        ]:
            if not _TOKEN_RE.match(tid):
                raise ValueError(
                    f"{label} must match user@realm!tokenid format — got {tid!r}"
                )

    @classmethod
    def from_env(cls, dotenv_path: Optional[str | Path] = None) -> Config:
        if dotenv_path is not None:
            load_dotenv(dotenv_path)
        else:
            load_dotenv()

        url = os.environ.get("PROXMOX_URL")
        if not url:
            raise ValueError("PROXMOX_URL is required")

        monitor_token_id = os.environ.get("PROXMOX_MONITOR_TOKEN_ID")
        if not monitor_token_id:
            raise ValueError("PROXMOX_MONITOR_TOKEN_ID is required")

        monitor_token_secret = os.environ.get("PROXMOX_MONITOR_TOKEN_SECRET")
        if not monitor_token_secret:
            raise ValueError("PROXMOX_MONITOR_TOKEN_SECRET is required")

        admin_token_id = os.environ.get("PROXMOX_ADMIN_TOKEN_ID")
        if not admin_token_id:
            raise ValueError("PROXMOX_ADMIN_TOKEN_ID is required")

        admin_token_secret = os.environ.get("PROXMOX_ADMIN_TOKEN_SECRET")
        if not admin_token_secret:
            raise ValueError("PROXMOX_ADMIN_TOKEN_SECRET is required")

        allow_elevated = os.environ.get("PROXMOX_ALLOW_ELEVATED", "false").strip().lower() in (
            "true",
            "1",
            "yes",
        )

        default_node = os.environ.get("PROXMOX_DEFAULT_NODE") or None

        allowed_commands_raw = os.environ.get("PROXMOX_ALLOWED_COMMANDS", "")
        allowed_commands = [c.strip() for c in allowed_commands_raw.split(",") if c.strip()] or None

        upload_dir = os.environ.get("PROXMOX_UPLOAD_DIR") or None

        verify_raw = os.environ.get("PROXMOX_VERIFY", "true").strip().lower()
        if verify_raw in ("false", "0", "no"):
            verify: str | bool = False
        elif verify_raw in ("true", "1", "yes"):
            verify = True
        else:
            verify = verify_raw

        return cls(
            url=url,
            verify=verify,
            monitor_token_id=monitor_token_id,
            monitor_token_secret=monitor_token_secret,
            admin_token_id=admin_token_id,
            admin_token_secret=admin_token_secret,
            allow_elevated=allow_elevated,
            default_node=default_node,
            allowed_commands=allowed_commands,
            upload_dir=upload_dir,
        )

    @property
    def host(self) -> str:
        return self.url.replace("https://", "").split(":")[0]

    @property
    def port(self) -> int:
        parts = self.url.replace("https://", "").split(":")
        if len(parts) > 1:
            try:
                return int(parts[1].rstrip("/"))
            except ValueError:
                pass
        return 8006
