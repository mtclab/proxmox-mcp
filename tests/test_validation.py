import pytest

from proxmox_mcp.utils import (
    validate_disk_size,
    validate_iface_name,
    validate_node_name,
    validate_storage_name,
    validate_vmid,
)


class TestValidateNodeName:
    async def test_valid_simple(self):
        validate_node_name("pve")

    async def test_valid_with_dots(self):
        validate_node_name("node1.example.com")

    async def test_valid_with_hyphens(self):
        validate_node_name("my-node-1")

    async def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name("")

    async def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name("my node")

    async def test_rejects_special_chars(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name("node!@#")

    async def test_rejects_starts_with_dot(self):
        with pytest.raises(ValueError, match="Invalid node name"):
            validate_node_name(".hidden")


class TestValidateVmid:
    async def test_valid_positive_int(self):
        validate_vmid(100)

    async def test_none_passes(self):
        validate_vmid(None)

    async def test_rejects_zero(self):
        with pytest.raises(ValueError, match="Invalid vmid"):
            validate_vmid(0)

    async def test_rejects_negative(self):
        with pytest.raises(ValueError, match="Invalid vmid"):
            validate_vmid(-1)

    async def test_rejects_string(self):
        with pytest.raises(ValueError, match="Invalid vmid"):
            validate_vmid("100")


class TestValidateStorageName:
    async def test_valid_simple(self):
        validate_storage_name("local")

    async def test_valid_with_dots(self):
        validate_storage_name("local-lvm")

    async def test_valid_with_underscores(self):
        validate_storage_name("my_storage")

    async def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid storage name"):
            validate_storage_name("")

    async def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid storage name"):
            validate_storage_name("my storage")


class TestValidateIfaceName:
    async def test_valid_bridge(self):
        validate_iface_name("vmbr0")

    async def test_valid_eth(self):
        validate_iface_name("eno1")

    async def test_valid_with_colon(self):
        validate_iface_name("eth0:1")

    async def test_valid_with_dot(self):
        validate_iface_name("eth0.100")

    async def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid interface name"):
            validate_iface_name("")

    async def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid interface name"):
            validate_iface_name("bad iface")


class TestValidateDiskSize:
    async def test_integer_passthrough(self):
        assert validate_disk_size(32) == "32"

    async def test_string_integer(self):
        assert validate_disk_size("32") == "32"

    async def test_string_with_G(self):
        assert validate_disk_size("32G") == "32"

    async def test_string_with_GiB(self):
        assert validate_disk_size("10GiB") == "10"

    async def test_string_with_T(self):
        assert validate_disk_size("1T") == "1024"

    async def test_string_with_TiB(self):
        assert validate_disk_size("2TiB") == "2048"

    async def test_invalid_string_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("abc")

    async def test_invalid_unit_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("10MB")

    async def test_float_numeric_part_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size("1.5G")

    async def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid disk_size"):
            validate_disk_size([10])
